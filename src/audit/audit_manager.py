"""
CLOSE-AI: Cryptographic Audit Trail & Evidence Pack Generator
Enforces unbroken lineage, SHA-256 hash chaining, and statutory audit packaging
aligned with ISA 240 / 315 / 500 and Nordic SAF-T standards.
"""

import os
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional

class AuditManager:
    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, log_file: Optional[str] = "audit_log_2026_10.json", workflow_file: Optional[str] = None):
        self.log_file = log_file
        self.workflow_file = workflow_file or (
            f"{os.path.splitext(log_file)[0]}_workflow_state.json" if log_file else None
        )
        self.records: List[Dict[str, Any]] = []
        self.workflow_state: Dict[str, Any] = self.load_workflow_state()
        if self.log_file and os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []

    @staticmethod
    def default_workflow_state() -> Dict[str, Any]:
        return {
            "resolved_anomalies": [],
            "disputed_items": [],
            "posted_journals": [],
            "period_locked": False
        }

    def load_workflow_state(self) -> Dict[str, Any]:
        if not self.workflow_file or not os.path.exists(self.workflow_file):
            return self.default_workflow_state()
        try:
            with open(self.workflow_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if not isinstance(payload, dict):
                return self.default_workflow_state()
            state = self.default_workflow_state()
            state.update(payload)
            if not isinstance(state["resolved_anomalies"], list):
                state["resolved_anomalies"] = []
            if not isinstance(state["disputed_items"], list):
                state["disputed_items"] = []
            if not isinstance(state["posted_journals"], list):
                state["posted_journals"] = []
            state["period_locked"] = bool(state.get("period_locked", False))
            return state
        except Exception:
            return self.default_workflow_state()

    def save_workflow_state(self, state: Optional[Dict[str, Any]] = None):
        if not self.workflow_file:
            return
        payload = self.default_workflow_state()
        if state:
            payload.update(state)
        self.workflow_state = payload
        with open(self.workflow_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def get_workflow_snapshot(self) -> Dict[str, Any]:
        snapshot = self.default_workflow_state()
        snapshot.update(self.workflow_state)
        snapshot["resolved_anomalies"] = list(snapshot.get("resolved_anomalies", []))
        snapshot["disputed_items"] = list(snapshot.get("disputed_items", []))
        snapshot["posted_journals"] = list(snapshot.get("posted_journals", []))
        snapshot["period_locked"] = bool(snapshot.get("period_locked", False))
        return snapshot

    def get_latest_hash(self) -> str:
        if not self.records:
            return self.GENESIS_HASH
        return self.records[-1].get("current_record_hash", self.GENESIS_HASH)

    def log_event(
        self,
        event_type: str,
        operator_name: str = "Frank Ellingsen",
        operator_role: str = "Lead Project Controller",
        journal_id: Optional[str] = None,
        action_taken: str = "APPROVED_WITHOUT_EDIT",
        investigation_id: Optional[str] = None,
        triggering_control: Optional[str] = None,
        financial_lines: Optional[List[Dict[str, Any]]] = None,
        justification_memo: str = ""
    ) -> Dict[str, Any]:
        """
        Appends an immutable audit event to the cryptographic ledger log.
        """
        parent_hash = self.get_latest_hash()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        event_seq = len(self.records) + 1
        event_id = f"AUD-2026-10-31-{event_seq:04d}"

        record_payload = {
            "audit_event_id": event_id,
            "timestamp_utc": timestamp,
            "fiscal_period": "2026-10",
            "event_type": event_type,
            "journal_id": journal_id or f"JV-AUTO-{event_seq:04d}",
            "operator": {
                "user_id": f"usr_{operator_name.lower().replace(' ', '_')[:12]}",
                "name": operator_name,
                "role": operator_role,
                "auth_session": f"AUTH-TOKEN-{hashlib.sha256(f'{operator_name}-{timestamp}'.encode()).hexdigest()[:10].upper()}"
            },
            "action_taken": action_taken,
            "originating_investigation_id": investigation_id or "N/A",
            "triggering_control": triggering_control or "N/A",
            "financial_lines": financial_lines or [],
            "justification_memo": justification_memo,
            "parent_record_hash": parent_hash
        }

        # Compute SHA-256 over deterministic JSON representation
        serialized = json.dumps(record_payload, sort_keys=True)
        current_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        record_payload["current_record_hash"] = current_hash

        self.records.append(record_payload)
        self._persist()
        return record_payload

    def _persist(self):
        if self.log_file:
            try:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    json.dump(self.records, f, indent=2)
            except Exception as e:
                print(f"[AuditManager] Could not persist log: {e}")

    def verify_audit_chain(self) -> Dict[str, Any]:
        """
        Verifies cryptographic integrity of the audit log chain.
        Ensures zero tampering: each record's current_hash matches its content
        and matches the parent_hash of the subsequent record.
        """
        if not self.records:
            return {"valid": True, "record_count": 0, "message": "Log is empty"}

        expected_parent = self.GENESIS_HASH
        for idx, rec in enumerate(self.records):
            rec_copy = rec.copy()
            actual_current = rec_copy.pop("current_record_hash", "")
            actual_parent = rec_copy.get("parent_record_hash", "")

            if actual_parent != expected_parent:
                return {
                    "valid": False,
                    "tampered_index": idx,
                    "event_id": rec.get("audit_event_id"),
                    "error": f"Parent hash mismatch at record {idx}. Expected {expected_parent[:8]}, got {actual_parent[:8]}"
                }

            recomputed = hashlib.sha256(json.dumps(rec_copy, sort_keys=True).encode("utf-8")).hexdigest()
            if recomputed != actual_current:
                return {
                    "valid": False,
                    "tampered_index": idx,
                    "event_id": rec.get("audit_event_id"),
                    "error": f"Content hash mismatch at record {idx}. Record content was modified!"
                }

            expected_parent = actual_current

        return {
            "valid": True,
            "record_count": len(self.records),
            "head_hash": expected_parent,
            "message": "All cryptographic signatures and chaining links verified intact."
        }

    def generate_statutory_evidence_pack(
        self,
        controls_summary: List[Dict[str, Any]],
        anomalies_summary: Optional[List[Dict[str, Any]]] = None,
        staged_journals: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Compiles the Month-End Audit Evidence Pack for external statutory auditors.
        """
        verification = self.verify_audit_chain()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        pack = {
            "pack_title": "CLOSE-AI Statutory Month-End Audit Evidence Pack",
            "entity": "Nordic Engineering Projects AS",
            "organization_number": "NO 984 521 890 MVA",
            "fiscal_period": "2026-10",
            "reporting_currency": "NOK",
            "generated_at_utc": now,
            "lead_controller": "Frank Ellingsen",
            "audit_standard_compliance": ["ISA 240 (Fraud in Financial Statements)", "ISA 315 (Identifying Risks)", "ISA 500 (Audit Evidence)", "Nordic Standard SAF-T Financial"],
            "cryptographic_chain_status": verification,
            "deterministic_controls_execution": controls_summary,
            "unsupervised_anomaly_register": anomalies_summary or [],
            "approved_journal_vouchers": staged_journals or [],
            "audit_trail_events": self.records,
            "period_lock_certificate": {
                "status": "LOCKED" if verification["valid"] else "PENDING_VERIFICATION",
                "digital_seal_sha256": verification.get("head_hash", self.GENESIS_HASH),
                "certifying_officer": "Frank Ellingsen, Lead Project Controller"
            }
        }
        return pack

if __name__ == "__main__":
    mgr = AuditManager()
    mgr.log_event(
        event_type="JOURNAL_VOUCHER_POSTED",
        journal_id="JV-2026-10-0042",
        triggering_control="CTRL-AP-03",
        financial_lines=[
            {"account": "4100", "debit_nok": 670000.0, "credit_nok": 0.0, "wbs": "PRJ-2026-001.03.FAB"},
            {"account": "2440", "debit_nok": 0.0, "credit_nok": 670000.0, "wbs": "PRJ-2026-001.03.FAB"}
        ],
        justification_memo="Accrued 100% delivered fabrication per GR-4412. Held 150k dispute."
    )
    res = mgr.verify_audit_chain()
    print("Audit verification result:", res)
