"""
CLOSE-AI: Comprehensive End-to-End Test Suite
Validates the entire pipeline:
1. Synthetic ERP Data Generation
2. Medallion Lakehouse (Bronze -> Silver -> Gold)
3. Deterministic Financial Controls Engine (DuckDB)
4. Multivariate Isolation Forest Anomaly Detection
5. Controller Evidence Graph & Investigation Agent
6. Cryptographic Audit Trail & Tamper Verification
"""

import os
import json
import unittest
import pandas as pd
import duckdb

from src.data_generator.generate_erp_data import generate_erp_dataset
from src.lakehouse.pipeline import LakehousePipeline
from src.engine.evaluate_controls import run_close_controls
from src.ml.anomaly_detector import run_anomaly_detection
from src.agent.evidence_graph import ControllerEvidenceGraph
from src.agent.investigator import CloseInvestigatorAgent
from src.audit.audit_manager import AuditManager

class TestCloseAISystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_dir = "erp_data_2026_10"
        generate_erp_dataset(cls.test_dir)

    def test_01_synthetic_data_generation(self):
        """Verifies all master and transactional tables are exported."""
        expected_tables = [
            "divisions", "cost_centers", "vendors", "projects", "wbs_elements",
            "purchase_orders", "po_lines", "vendor_invoices",
            "gl_journal_entries", "gl_journal_lines"
        ]
        for tbl in expected_tables:
            csv_path = os.path.join(self.test_dir, f"{tbl}.csv")
            pq_path = os.path.join(self.test_dir, f"{tbl}.parquet")
            self.assertTrue(os.path.exists(csv_path), f"Missing CSV for {tbl}")
            self.assertTrue(os.path.exists(pq_path), f"Missing Parquet for {tbl}")

    def test_02_medallion_lakehouse_pipeline(self):
        """Verifies Bronze, Silver, and Gold transformations."""
        lakehouse = LakehousePipeline(base_dir="data/lakehouse")
        res = lakehouse.run_full_pipeline(self.test_dir)
        self.assertEqual(res["status"], "LAKEHOUSE_READY")
        
        # Verify Gold facts exist
        fact_gl_path = "data/lakehouse/gold/fact_gl_postings.parquet"
        fact_ap_path = "data/lakehouse/gold/fact_ap_invoices.parquet"
        self.assertTrue(os.path.exists(fact_gl_path))
        self.assertTrue(os.path.exists(fact_ap_path))

    def test_03_deterministic_controls(self):
        """Verifies deterministic controls catch the 5 injected accounting anomalies."""
        controls_output = run_close_controls(self.test_dir)
        self.assertEqual(controls_output["overall_status"], "CLOSE BLOCKED")
        self.assertEqual(controls_output["period"], "2026-10")

        rules_dict = {c["rule_id"]: c for c in controls_output["controls_summary"]}
        
        # 1. Trial Balance Blocker
        self.assertEqual(rules_dict["CTRL-GL-01"]["status"], "FAIL")
        self.assertEqual(rules_dict["CTRL-GL-01"]["discrepancy_amount_nok"], 15000.0)

        # 2. Weekend Manual Posting
        self.assertEqual(rules_dict["CTRL-GL-02"]["status"], "FAIL")

        # 3. Duplicate Invoices
        self.assertEqual(rules_dict["CTRL-AP-01"]["status"], "FAIL")

        # 4. Uninvoiced Goods Received
        self.assertIn(rules_dict["CTRL-AP-02"]["status"], ["WARNING", "FAIL"])

        # 5. PO Tolerance Overrun (+22.4%)
        self.assertEqual(rules_dict["CTRL-AP-03"]["status"], "FAIL")
        self.assertEqual(rules_dict["CTRL-AP-03"]["discrepancy_amount_nok"], 150000.0)

        # 6. Untagged direct cost
        self.assertEqual(rules_dict["CTRL-PRJ-03"]["status"], "FAIL")

    def test_04_isolation_forest_anomaly_detection(self):
        """Verifies unsupervised anomaly scoring flags out-of-distribution transactions."""
        df_anomalies = run_anomaly_detection(self.test_dir)
        self.assertIn("anomaly_score", df_anomalies.columns)
        self.assertIn("anomaly_band", df_anomalies.columns)
        self.assertIn("explanation", df_anomalies.columns)

        # The Sunday night manual posting without project code should be in the top anomalies
        critical = df_anomalies[df_anomalies["anomaly_score"] >= 85.0]
        self.assertGreater(len(critical), 0)
        self.assertTrue(any("Weekend posting" in exp for exp in critical["explanation"]))

    def test_05_investigation_agent_and_graph(self):
        """Verifies Controller Evidence Graph traversal and structured dossier generation."""
        agent = CloseInvestigatorAgent(data_dir=self.test_dir, provider="deterministic")
        dossier = agent.investigate_anomaly("CTRL-AP-03", "INV-VEND-99214")

        self.assertIn("investigation_id", dossier)
        self.assertIn("evidence_chain", dossier)
        self.assertIn("financial_impact", dossier)
        self.assertIn("proposed_journal_voucher", dossier)
        self.assertEqual(dossier["financial_impact"]["unauthorized_variance_nok"], 150000.0)

    def test_06_cryptographic_audit_trail_and_tamper_detection(self):
        """Verifies SHA-256 chain verification and intentional tamper detection."""
        log_file = "test_audit_log.json"
        if os.path.exists(log_file):
            os.remove(log_file)

        mgr = AuditManager(log_file=log_file)
        
        # Log 2 events
        r1 = mgr.log_event(
            event_type="JOURNAL_VOUCHER_POSTED",
            operator_name="Frank Ellingsen",
            journal_id="JV-2026-10-0001",
            justification_memo="Initial test journal entry"
        )
        r2 = mgr.log_event(
            event_type="JOURNAL_VOUCHER_POSTED",
            operator_name="Frank Ellingsen",
            journal_id="JV-2026-10-0002",
            justification_memo="Second test journal entry"
        )

        # 1. Verify chain is intact
        check = mgr.verify_audit_chain()
        self.assertTrue(check["valid"])
        self.assertEqual(check["record_count"], 2)

        # 2. Tamper test: modify record 0's memo and verify tamper detection
        mgr.records[0]["justification_memo"] = "TAMPERED_BY_MALICIOUS_ACTOR"
        tamper_check = mgr.verify_audit_chain()
        self.assertFalse(tamper_check["valid"])
        self.assertIn("Content hash mismatch", tamper_check["error"])

        # Clean up
        if os.path.exists(log_file):
            os.remove(log_file)

    def test_07_workflow_state_persistence(self):
        """Verifies workflow state persists across manager reloads."""
        log_file = "test_workflow_audit_log.json"
        workflow_file = "test_workflow_state.json"
        for path in [log_file, workflow_file]:
            if os.path.exists(path):
                os.remove(path)

        mgr = AuditManager(log_file=log_file, workflow_file=workflow_file)
        state = {
            "resolved_anomalies": ["CTRL-GL-01", "CTRL-AP-03"],
            "disputed_items": ["INV-VEND-99214"],
            "posted_journals": [{"journal_id": "JV-TEST-1", "amount_nok": 15000.0}],
            "period_locked": True,
        }
        mgr.save_workflow_state(state)

        reloaded = AuditManager(log_file=log_file, workflow_file=workflow_file)
        self.assertEqual(reloaded.workflow_state["resolved_anomalies"], ["CTRL-GL-01", "CTRL-AP-03"])
        self.assertTrue(reloaded.get_workflow_snapshot()["period_locked"])

        for path in [log_file, workflow_file]:
            if os.path.exists(path):
                os.remove(path)

    def test_08_safe_identifier_handling_in_evidence_graph(self):
        """Verifies evidence graph rejects malformed identifiers safely."""
        graph = ControllerEvidenceGraph(self.test_dir)

        missing_invoice = graph.trace_invoice_pedigree("DOES-NOT-EXIST")
        self.assertIn("error", missing_invoice)

        missing_journal = graph.trace_gl_entry_pedigree("DOES-NOT-EXIST")
        self.assertIn("error", missing_journal)

        invalid_po = graph.trace_uninvoiced_po("")
        self.assertIn("error", invalid_po)

    def test_09_ai_guardrails_reject_incomplete_evidence(self):
        """Verifies the investigation layer blocks incomplete evidence and the LLM validator rejects invalid dossiers."""
        agent = CloseInvestigatorAgent(data_dir=self.test_dir, provider="deterministic")
        blocked = agent.investigate_anomaly("CTRL-AP-03", "DOES-NOT-EXIST")
        self.assertIn("error", blocked)
        self.assertTrue(blocked["proposal_only"])
        self.assertTrue(blocked["human_approval_required"])

        invalid_dossier = {
            "investigation_id": "INV-TEST",
            "anomaly_ref": "CTRL-AP-03",
            "target_entity": "INV-1",
            "timestamp": "2026-10-31T00:00:00Z",
            "severity": "HIGH",
            "observation": "No evidence",
            "evidence_chain": [],
            "likely_cause": "Unknown",
            "financial_impact": {"unauthorized_variance_nok": 0.0, "ebitda_risk": "Low", "vat_impact_nok": 0.0},
            "recommended_action": "REVIEW",
            "proposed_journal_voucher": {"entry_type": "REVIEW", "lines": []},
            "proposal_only": False,
            "human_approval_required": False
        }
        self.assertFalse(agent.llm_client._validate_investigation_dossier(invalid_dossier))

if __name__ == "__main__":
    unittest.main()
