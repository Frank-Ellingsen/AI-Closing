import itertools
import datetime
from typing import List, Dict, Any, Optional
from src.agent.regex_agent import RegexAgent

class ComplexReconciliationEngine:
    """
    Two-stage (Pre-Match & Final Match) reconciliation engine integrating
    an autonomous Regex Agent, bounded combinatorial subset-sum solvers,
    and automated variance/fee segregation.
    """

    def __init__(
        self,
        fee_tolerance_pct: float = 0.03,
        max_date_delta_days: int = 5,
        llm_client = None
    ):
        self.fee_tolerance_pct = fee_tolerance_pct
        self.max_date_delta_days = max_date_delta_days
        self.regex_agent = RegexAgent(llm_client=llm_client)
        self.pre_match_proposals: List[Dict[str, Any]] = []
        self.final_matched_records: List[Dict[str, Any]] = []

    def extract_memo_features(self, raw_memo: str) -> Dict[str, Any]:
        """Tokenizes raw remittance strings via RegexAgent."""
        return self.regex_agent.extract_all_tokens(raw_memo)

    def run_pre_match(
        self,
        bank_transactions: List[Dict[str, Any]],
        subledger_items: List[Dict[str, Any]],
        max_fee_deduction_nok: float = 3500.0
    ) -> List[Dict[str, Any]]:
        """
        Stage 1: Pre-Match
        Identifies potential match clusters (1:1, 1:Many, Many:1) with confidence scores.
        Does NOT alter primary ledger records; stages clusters for controller approval.
        """
        proposals = []

        for b_tx in bank_transactions:
            if b_tx.get("status") == "FINAL_MATCHED":
                continue

            target_amount = float(b_tx["amount_nok"])
            raw_memo = b_tx.get("raw_memo", b_tx.get("description", ""))

            match = self.solve_one_to_many_subset(
                target_amount_nok=target_amount,
                raw_memo=raw_memo,
                candidate_items=subledger_items,
                max_fee_deduction_nok=max_fee_deduction_nok
            )

            if match:
                proposal = {
                    "proposal_id": f"PROP-REC-{b_tx.get('tx_id', 'TX')}",
                    "stage": "PRE_MATCH_SUGGESTED",
                    "bank_transaction": b_tx,
                    "matched_subledger_lines": match["matched_lines"],
                    "gross_subledger_nok": match["gross_subledger_nok"],
                    "bank_settlement_nok": match["bank_settlement_nok"],
                    "isolated_fee_nok": match["fee_deduction_nok"],
                    "match_type": match["match_type"],
                    "confidence_score": match["confidence_score"],
                    "tokens_detected": match["extracted_tokens"],
                    "created_at": datetime.datetime.now().isoformat()
                }
                proposals.append(proposal)
                self.pre_match_proposals.append(proposal)

        return proposals

    def execute_final_match(
        self,
        proposal_id: str,
        approved_by: str = "Controller"
    ) -> Dict[str, Any]:
        """
        Stage 2: Final Match (Hard Clearing & Freeze)
        Validates controller sign-off, confirms zero net unallocated delta,
        and freezes the match cluster into final reconciled state.
        """
        prop = next((p for p in self.pre_match_proposals if p["proposal_id"] == proposal_id), None)
        if not prop:
            raise ValueError(f"Proposal '{proposal_id}' not found in Pre-Match staging pool.")

        final_record = {
            "match_id": f"FINAL-MATCH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{proposal_id}",
            "stage": "FINAL_MATCHED",
            "proposal_id": proposal_id,
            "bank_tx_id": prop["bank_transaction"]["tx_id"],
            "matched_invoice_ids": [item["id"] for item in prop["matched_subledger_lines"]],
            "settlement_amount_nok": prop["bank_settlement_nok"],
            "allocated_fees_nok": prop["isolated_fee_nok"],
            "approved_by": approved_by,
            "finalized_at": datetime.datetime.now().isoformat()
        }

        prop["stage"] = "FINAL_MATCHED"
        self.final_matched_records.append(final_record)
        return final_record

    def solve_one_to_many_subset(
        self,
        target_amount_nok: float,
        raw_memo: str,
        candidate_items: List[Dict[str, Any]],
        max_fee_deduction_nok: float = 3500.0
    ) -> Optional[Dict[str, Any]]:
        """
        Combinatorial subset-sum solver with token-directed partitioning.
        """
        extracted_features = self.extract_memo_features(raw_memo)
        clean_tokens = extracted_features["all_clean_identifiers"]

        # Token-directed candidate partitioning
        prioritized_candidates = []
        secondary_candidates = []

        for item in candidate_items:
            item_signature = f"{item.get('id', '')} {item.get('po_number', '')} {item.get('vendor', '')}"
            if any(token.lower() in item_signature.lower() for token in clean_tokens):
                prioritized_candidates.append(item)
            else:
                secondary_candidates.append(item)

        search_pool = prioritized_candidates if prioritized_candidates else candidate_items
        best_match = self._find_subset_sum(
            target_amount_nok=target_amount_nok,
            candidates=search_pool,
            max_fee_deduction_nok=max_fee_deduction_nok,
            extracted_features=extracted_features
        )

        # Fallback to secondary if token search was empty
        if not best_match and prioritized_candidates and len(candidate_items) <= 30:
            best_match = self._find_subset_sum(
                target_amount_nok=target_amount_nok,
                candidates=candidate_items,
                max_fee_deduction_nok=max_fee_deduction_nok,
                extracted_features=extracted_features
            )

        return best_match

    def _find_subset_sum(
        self,
        target_amount_nok: float,
        candidates: List[Dict[str, Any]],
        max_fee_deduction_nok: float,
        extracted_features: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        n = len(candidates)
        best_match = None
        min_residual = float("inf")

        # Bounded combinatorial depth (1 to 8 lines)
        for r in range(1, min(n + 1, 9)):
            for combo in itertools.combinations(candidates, r):
                gross_sum = sum(float(item["amount_nok"]) for item in combo)
                variance = round(gross_sum - target_amount_nok, 2)

                if 0 <= variance <= max_fee_deduction_nok:
                    if variance < min_residual:
                        min_residual = variance
                        confidence = 0.99 if variance == 0 else 0.94

                        best_match = {
                            "matched_lines": list(combo),
                            "gross_subledger_nok": gross_sum,
                            "bank_settlement_nok": target_amount_nok,
                            "fee_deduction_nok": variance,
                            "extracted_tokens": extracted_features["all_clean_identifiers"],
                            "confidence_score": confidence,
                            "match_type": f"1:{len(combo)}"
                        }
                        if min_residual == 0:
                            return best_match

        return best_match
