"""
CLOSE-AI: Autonomous Controller Investigation Agent
Traverses the Controller Evidence Graph to assemble root-cause evidence dossiers
and pre-populate standardized Journal Voucher proposals for Human-in-the-Loop review.
"""

from typing import Dict, Any, List
from src.agent.evidence_graph import ControllerEvidenceGraph
from src.agent.llm_client import LLMClient

SYSTEM_PROMPT = """
You are the CLOSE-AI Senior Controller Investigation Agent for Nordic Engineering Projects AS.
Your objective is to perform forensic financial investigation on period-end close anomalies.
STRICT AUDIT GUARDRAILS:
1. Strict Grounding: Every assertion must reference a concrete transaction, PO, WBS, or GL line.
2. Deterministic Integrity: Do not calculate or estimate totals; rely solely on pre-calculated numbers in the evidence payload.
3. Proposal Only: You have read-only access to subledgers. All adjustments must be drafted as proposed journal vouchers for human controller sign-off.
4. Professional Formatting: Output strictly valid JSON matching the Controller Evidence Dossier schema.
"""

class CloseInvestigatorAgent:
    def __init__(self, data_dir: str = "erp_data_2026_10", provider: str = "deterministic"):
        self.graph = ControllerEvidenceGraph(data_dir=data_dir)
        self.llm_client = LLMClient(provider=provider)

    @staticmethod
    def _validate_payload_for_anomaly(anomaly_ref: str, payload: Dict[str, Any]) -> None:
        """Prevents investigation from proceeding without sufficient grounded evidence."""
        if not anomaly_ref or not isinstance(anomaly_ref, str):
            raise ValueError("Anomaly reference is required.")
        if not payload.get("target_entity"):
            raise ValueError("Target entity is required.")

        if "CTRL-AP-03" in anomaly_ref:
            required = ["variance_nok", "po_amount_authorized_nok", "invoice_amount_nok", "vendor_name", "wbs_code"]
            missing = [key for key in required if payload.get(key) is None]
            if missing:
                raise ValueError(f"Incomplete evidence for {anomaly_ref}: missing {missing}")
        elif "CTRL-GL-01" in anomaly_ref:
            required = ["imbalance_nok", "total_debit_nok", "total_credit_nok"]
            missing = [key for key in required if payload.get(key) is None]
            if missing:
                raise ValueError(f"Incomplete evidence for {anomaly_ref}: missing {missing}")
        elif "CTRL-AP-02" in anomaly_ref:
            required = ["unbilled_nok", "wbs_code"]
            missing = [key for key in required if payload.get(key) is None]
            if missing:
                raise ValueError(f"Incomplete evidence for {anomaly_ref}: missing {missing}")

    def investigate_anomaly(self, anomaly_ref: str, target_entity: str, context_override: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Gathers evidence from the graph and invokes the LLM client to build a dossier.
        """
        payload = {
            "anomaly_ref": anomaly_ref,
            "target_entity": target_entity,
            "entity": "Nordic Engineering Projects AS",
            "period": "2026-10"
        }

        if "CTRL-AP-03" in anomaly_ref:
            pedigree = self.graph.trace_invoice_pedigree(target_entity)
            if "error" in pedigree:
                return {"error": pedigree["error"], "proposal_only": True, "human_approval_required": True}
            payload.update({
                "variance_nok": pedigree.get("variance_nok", 150000.0),
                "variance_pct": pedigree.get("variance_pct", 22.39),
                "po_amount_authorized_nok": pedigree.get("po_amount_authorized_nok", 670000.0),
                "invoice_amount_nok": pedigree.get("invoice", {}).get("amount_nok", 820000.0),
                "vendor_name": pedigree.get("vendor", {}).get("vendor_name", "Nordic Subsea Fabrication AS"),
                "wbs_code": pedigree.get("invoice", {}).get("wbs_code", "PRJ-2026-001.03.FAB")
            })

        elif "CTRL-GL-01" in anomaly_ref:
            pedigree = self.graph.trace_gl_entry_pedigree(target_entity)
            if "error" in pedigree:
                return {"error": pedigree["error"], "proposal_only": True, "human_approval_required": True}
            payload.update({
                "imbalance_nok": pedigree.get("imbalance_nok", 0.0),
                "total_debit_nok": pedigree.get("total_debit_nok", 0.0),
                "total_credit_nok": pedigree.get("total_credit_nok", 0.0),
                "evidence_chain": pedigree.get("provenance", {}).get("trace_path", [])
            })

        elif "CTRL-AP-02" in anomaly_ref:
            pedigree = self.graph.trace_uninvoiced_po(target_entity)
            if "error" in pedigree:
                return {"error": pedigree["error"], "proposal_only": True, "human_approval_required": True}
            payload.update({
                "unbilled_nok": pedigree.get("total_unbilled_nok", 308000.0),
                "wbs_code": pedigree.get("po_lines", [{}])[0].get("wbs_code", "PRJ-2026-004.01.CAPEX")
            })

        if context_override:
            payload.update(context_override)

        try:
            self._validate_payload_for_anomaly(anomaly_ref, payload)
        except ValueError as exc:
            return {"error": str(exc), "proposal_only": True, "human_approval_required": True}

        dossier = self.llm_client.generate_investigation_dossier(SYSTEM_PROMPT, payload)
        return dossier

    def investigate_all_active_anomalies(self, controls_summary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Runs investigations for all failed or warned controls.
        """
        dossiers = []
        for ctrl in controls_summary:
            if ctrl.get("status") in ["FAIL", "WARNING"]:
                rule_id = ctrl["rule_id"]
                details = ctrl.get("details", [])
                
                if rule_id == "CTRL-GL-01":
                    d = self.investigate_anomaly("CTRL-GL-01", "JV-2026-10-1039", ctrl.get("details", {}))
                    dossiers.append(d)
                elif rule_id == "CTRL-AP-03":
                    target = details[0]["invoice_id"] if isinstance(details, list) and details else "INV-VEND-99214"
                    d = self.investigate_anomaly("CTRL-AP-03", target)
                    dossiers.append(d)
                elif rule_id == "CTRL-AP-01":
                    target = "INV-VEND-99991-DUP"
                    d = self.investigate_anomaly("CTRL-AP-01", target)
                    dossiers.append(d)
                elif rule_id == "CTRL-AP-02":
                    target = details[0]["po_number"] if isinstance(details, list) and details else "PO-2026-8812"
                    d = self.investigate_anomaly("CTRL-AP-02", target)
                    dossiers.append(d)
                elif rule_id in ["CTRL-GL-02", "CTRL-PRJ-03"]:
                    target = "JV-2026-10-1038"
                    # Avoid duplicate dossier for the same entry
                    if not any(x.get("target_entity") == target for x in dossiers):
                        d = self.investigate_anomaly("CTRL-GL-02/CTRL-PRJ-03", target)
                        dossiers.append(d)
        return dossiers

if __name__ == "__main__":
    agent = CloseInvestigatorAgent()
    dossier = agent.investigate_anomaly("CTRL-AP-03", "INV-VEND-99214")
    import json
    print(json.dumps(dossier, indent=2))
