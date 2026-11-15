import unittest
from unittest.mock import MagicMock
from src.engine.complex_matcher import ComplexReconciliationEngine
from src.agent.regex_agent import RegexAgent
from src.engine.voucher_generator import VoucherGenerator
from src.engine.aging_analyzer import AgingAnalyzer

class TestComplexReconciliations(unittest.TestCase):

    def setUp(self):
        self.complex_matcher = ComplexReconciliationEngine(fee_tolerance_pct=0.04, max_date_delta_days=5)

    def test_token_directed_one_to_many_matching(self):
        raw_memo = "CR-SETTL-ADYEN-88491-OCT26 INCL 2% DEDUCT"
        target_bank_payout = 89512.50

        candidate_invoices = [
            {"id": "INV-101", "po_number": "PO-88491-A", "amount_nok": 42000.00},
            {"id": "INV-102", "po_number": "PO-88491-B", "amount_nok": 28500.00},
            {"id": "INV-103", "po_number": "PO-88491-C", "amount_nok": 11200.00},
            {"id": "INV-104", "po_number": "PO-88491-D", "amount_nok": 9850.00},
            {"id": "INV-DISTRACT", "po_number": "PO-99999", "amount_nok": 89512.50}
        ]

        result = self.complex_matcher.solve_one_to_many_subset(
            target_amount_nok=target_bank_payout,
            raw_memo=raw_memo,
            candidate_items=candidate_invoices,
            max_fee_deduction_nok=2500.00
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["match_type"], "1:4")
        self.assertIn("88491", result["extracted_tokens"])
        matched_ids = [item["id"] for item in result["matched_lines"]]
        self.assertEqual(matched_ids, ["INV-101", "INV-102", "INV-103", "INV-104"])
        self.assertNotIn("INV-DISTRACT", matched_ids)
        self.assertEqual(result["gross_subledger_nok"], 91550.00)
        self.assertEqual(result["fee_deduction_nok"], 2037.50)

    def test_fee_must_fit_absolute_and_percentage_tolerances(self):
        strict_matcher = ComplexReconciliationEngine(fee_tolerance_pct=0.02)
        result = strict_matcher.solve_one_to_many_subset(
            target_amount_nok=9700.00,
            raw_memo="INV-200",
            candidate_items=[{"id": "INV-200", "amount_nok": 10000.00}],
            max_fee_deduction_nok=3500.00
        )

        self.assertIsNone(result)

    def test_finalized_items_cannot_be_allocated_twice(self):
        item = {"id": "INV-200", "amount_nok": 10000.00}
        bank_transactions = [
            {"tx_id": "TX-1", "amount_nok": 10000.00, "raw_memo": "INV-200"},
            {"tx_id": "TX-2", "amount_nok": 10000.00, "raw_memo": "INV-200"}
        ]
        proposals = self.complex_matcher.run_pre_match(bank_transactions, [item])
        self.assertEqual(len(proposals), 2)

        self.complex_matcher.execute_final_match(proposals[0]["proposal_id"])
        with self.assertRaisesRegex(ValueError, "already-finalized"):
            self.complex_matcher.execute_final_match(proposals[1]["proposal_id"])
        with self.assertRaisesRegex(ValueError, "already been finalized"):
            self.complex_matcher.execute_final_match(proposals[0]["proposal_id"])

        new_proposals = self.complex_matcher.run_pre_match(
            [{"tx_id": "TX-3", "amount_nok": 10000.00, "raw_memo": "INV-200"}],
            [item]
        )
        self.assertEqual(new_proposals, [])

    def test_final_match_rejects_unbalanced_proposal(self):
        proposal = self.complex_matcher.run_pre_match(
            [{"tx_id": "TX-4", "amount_nok": 10000.00, "raw_memo": "INV-201"}],
            [{"id": "INV-201", "amount_nok": 10000.00}]
        )[0]
        proposal["isolated_fee_nok"] = 25.00

        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            self.complex_matcher.execute_final_match(proposal["proposal_id"])

    def test_regex_agent_token_extraction(self):
        agent = RegexAgent()
        memo = "WIRE PO-8809 INV-4412 BATCH-88491 FEE: 2037.50 PRJ-2026-001.03.FAB"
        tokens = agent.extract_all_tokens(memo)

        self.assertIn("8809", tokens["po_refs"])
        self.assertIn("4412", tokens["invoice_refs"])
        self.assertIn("88491", tokens["batch_ids"])
        self.assertIn(2037.50, tokens["embedded_fees"])

    def test_spin_off_voucher_balancing(self):
        spin_off = VoucherGenerator.create_spin_off_voucher(
            voucher_number="JV-TEST-01",
            posting_date="2026-10-31",
            transaction_type="BANK_FEE",
            amount_nok=2037.50,
            bank_account="1920",
            contra_account="7770"
        )

        self.assertTrue(spin_off.is_balanced)
        self.assertEqual(spin_off.net_delta_nok, 0.0)
        self.assertEqual(spin_off.lines[0].account, "7770")
        self.assertEqual(spin_off.lines[0].debet_nok, 2037.50)
        self.assertEqual(spin_off.lines[1].account, "1920")
        self.assertEqual(spin_off.lines[1].kredit_nok, 2037.50)

    def test_aging_analysis_bucketing(self):
        analyzer = AgingAnalyzer(reference_date="2026-10-31")
        items = [
            {"id": "I-1", "amount_nok": 10000.0, "invoice_date": "2026-10-20"},  # 11 days (0-30)
            {"id": "I-2", "amount_nok": 20000.0, "invoice_date": "2026-09-15"},  # 46 days (31-60)
            {"id": "I-3", "amount_nok": 30000.0, "invoice_date": "2026-08-10"},  # 82 days (61-90)
            {"id": "I-4", "amount_nok": 40000.0, "invoice_date": "2026-06-01"}   # 152 days (90+)
        ]

        buckets = analyzer.calculate_aging_buckets(items)
        self.assertEqual(buckets["0-30 dager"].total_amount_nok, 10000.0)
        self.assertEqual(buckets["31-60 dager"].total_amount_nok, 20000.0)
        self.assertEqual(buckets["61-90 dager"].total_amount_nok, 30000.0)
        self.assertEqual(buckets["90+ dager"].total_amount_nok, 40000.0)
        self.assertEqual(buckets["90+ dager"].estimated_loss_nok, 16000.0)

if __name__ == "__main__":
    unittest.main()
