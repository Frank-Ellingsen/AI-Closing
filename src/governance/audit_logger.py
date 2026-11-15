import hashlib
import json
import datetime
import os
from typing import Dict, Any, List

class AuditLogger:
    """
    Append-only SHA-256 cryptographic audit logger.
    Guarantees an unbroken chain of custody for all reconciliations,
    pre-match approvals, spin-off exports, and journal vouchers.
    """

    def __init__(self, log_path: str = "data/audit_logs/audit_trail.jsonl"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                pass

    def _get_last_hash(self) -> str:
        """Retrieves the cryptographic hash of the most recent entry."""
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return "0" * 64

        last_line = ""
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()

        if not last_line:
            return "0" * 64

        try:
            record = json.loads(last_line)
            return record.get("current_hash", "0" * 64)
        except Exception:
            return "0" * 64

    def log_event(
        self,
        event_type: str,
        actor: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates SHA-256 hash linking previous hash + timestamp + actor + payload.
        Appends the verified entry to the audit log.
        """
        prev_hash = self._get_last_hash()
        timestamp = datetime.datetime.now().isoformat()

        body_str = json.dumps(payload, sort_keys=True)
        raw_to_hash = f"{prev_hash}|{timestamp}|{actor}|{event_type}|{body_str}"
        current_hash = hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()

        entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "actor": actor,
            "payload": payload,
            "prev_hash": prev_hash,
            "current_hash": current_hash
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Validates that no records in the audit chain have been modified."""
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return {"is_valid": True, "verified_records": 0, "message": "Log is empty"}

        records_count = 0
        expected_prev_hash = "0" * 64

        with open(self.log_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                record = json.loads(line.strip())
                if record["prev_hash"] != expected_prev_hash:
                    return {
                        "is_valid": False,
                        "broken_at_line": idx,
                        "error": f"Hash mismatch! Expected {expected_prev_hash}, got {record['prev_hash']}"
                    }

                body_str = json.dumps(record["payload"], sort_keys=True)
                raw_to_hash = f"{record['prev_hash']}|{record['timestamp']}|{record['actor']}|{record['event_type']}|{body_str}"
                recomputed_hash = hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()

                if recomputed_hash != record["current_hash"]:
                    return {
                        "is_valid": False,
                        "broken_at_line": idx,
                        "error": "Tampering detected: Payload or metadata altered."
                    }

                expected_prev_hash = record["current_hash"]
                records_count += 1

        return {"is_valid": True, "verified_records": records_count}
