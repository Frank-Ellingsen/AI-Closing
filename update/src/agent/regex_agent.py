import re
import json
from typing import Dict, Any, List, Optional

class RegexAgent:
    """
    Autonomous Regex Agent that tokenizes noisy financial strings,
    extracts ERP keys (PO, Invoices, KID, Batch IDs, Fees), and
    synthesizes new patterns when encountering unfamiliar formats.
    """

    BUILTIN_PATTERNS = {
        "invoice_num": r"(?i)(?:inv|invoice|faktura|fa)[\s#/:_-]*([A-Z0-9]{4,14})",
        "po_num": r"(?i)(?:po|ordre|ord|order)[\s#/:_-]*([A-Z0-9]{4,14})",
        "kid_num": r"(?:\bKID[:\s]*|\b)(\d{7,25})\b",
        "batch_id": r"(?i)(?:adyen|nets|stripe|vipps|klarna|batch)[\s#/:_-]*([A-Z0-9]{5,16})",
        "embedded_fee": r"(?i)(?:fee|gebyr|kortgebyr|deduct)[\s:]*([0-9.,]+)",
        "currency_code": r"\b(NOK|EUR|USD|GBP|SEK|DKK)\b",
        "wbs_element": r"(?i)\b([A-Z]{3}-\d{4}-\d{3}\.\d{2}\.[A-Z]{3})\b"
    }

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.learned_patterns: Dict[str, str] = {}

    def extract_all_tokens(self, memo: str) -> Dict[str, Any]:
        """Runs fast, deterministic regex extraction over raw string."""
        if not memo:
            return {"all_clean_identifiers": [], "raw_memo": ""}

        invoice_matches = re.findall(self.BUILTIN_PATTERNS["invoice_num"], memo)
        po_matches = re.findall(self.BUILTIN_PATTERNS["po_num"], memo)
        kid_matches = re.findall(self.BUILTIN_PATTERNS["kid_num"], memo)
        batch_matches = re.findall(self.BUILTIN_PATTERNS["batch_id"], memo)
        wbs_matches = re.findall(self.BUILTIN_PATTERNS["wbs_element"], memo)

        # Parse fees safely
        fee_strings = re.findall(self.BUILTIN_PATTERNS["embedded_fee"], memo)
        parsed_fees = []
        for f in fee_strings:
            try:
                parsed_fees.append(float(f.replace(",", ".")))
            except ValueError:
                pass

        # Standalone numeric sequences (common in bank remittance wires)
        standalone_nums = re.findall(r"\b\d{5,8}\b", memo)

        clean_identifiers = list(set(
            invoice_matches + po_matches + batch_matches + wbs_matches + standalone_nums
        ))

        return {
            "invoice_refs": invoice_matches,
            "po_refs": po_matches,
            "kid_refs": kid_matches,
            "batch_ids": batch_matches,
            "wbs_elements": wbs_matches,
            "embedded_fees": parsed_fees,
            "all_clean_identifiers": clean_identifiers,
            "raw_memo": memo
        }

    def synthesize_new_rule(self, failed_samples: List[str], expected_target_id: str) -> Dict[str, Any]:
        """
        Uses LLM (or mock inference) to induce a minimal, high-precision regex pattern
        when unfamiliar bank description formats fail built-in tokenization.
        """
        prompt = f"""
        You are an expert financial regular expression engineer.
        Analyze these raw transaction memos from bank/vendor feeds:
        {json.dumps(failed_samples, indent=2)}

        The target accounting identifier to reliably extract into Capture Group 1 is: '{expected_target_id}'.

        Generate:
        1. A strict, performant Python regular expression with capture group 1.
        2. A clear explanation of pattern mechanics.
        Return strictly JSON: {{"regex_pattern": "...", "explanation": "..."}}
        """

        if self.llm_client:
            try:
                response = self.llm_client.generate(prompt)
                parsed = json.loads(response)
                pattern = parsed.get("regex_pattern", "")
                explanation = parsed.get("explanation", "")
            except Exception as e:
                # Fallback to deterministic prefix-based synthesis
                escaped_target = re.escape(expected_target_id)
                pattern = rf"(?i)(?:ref|id|batch|num)[\s#/:_-]*({escaped_target})"
                explanation = f"Synthesized pattern fallback due to: {str(e)}"
        else:
            # Deterministic synthesis fallback
            escaped_target = re.escape(expected_target_id)
            pattern = rf"(?i)(?:ref|id|batch|wire)[\s#/:_-]*({escaped_target})"
            explanation = "Deterministic rule synthesized without active LLM provider."

        # Self-test the synthesized pattern against failed samples
        try:
            compiled = re.compile(pattern)
            matched_count = sum(1 for s in failed_samples if compiled.search(s))
            pass_rate = f"{matched_count}/{len(failed_samples)}"
            is_safe = matched_count > 0
        except re.error:
            pattern = re.escape(expected_target_id)
            pass_rate = "0/0"
            is_safe = False

        self.learned_patterns[expected_target_id] = pattern

        return {
            "pattern": pattern,
            "explanation": explanation,
            "test_pass_rate": pass_rate,
            "is_safe": is_safe
        }
