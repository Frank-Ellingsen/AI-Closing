import datetime
from typing import List, Dict, Any, Optional
from src.engine.models import AgingBucketSummary

class AgingAnalyzer:
    """
    Analyzes un-reconciled and open subledger items, categorizing them
    into standard aging buckets (0-30, 31-60, 61-90, 90+ days),
    estimating default provisions, and flagging audit risks.
    """

    PROVISION_RATES = {
        "0-30 dager": 0.00,
        "31-60 dager": 0.02,
        "61-90 dager": 0.10,
        "90+ dager": 0.40
    }

    RISK_LEVELS = {
        "0-30 dager": "LOW",
        "31-60 dager": "MEDIUM",
        "61-90 dager": "HIGH",
        "90+ dager": "CRITICAL"
    }

    def __init__(self, reference_date: Optional[str] = None):
        if reference_date:
            self.ref_date = datetime.datetime.strptime(reference_date, "%Y-%m-%d").date()
        else:
            self.ref_date = datetime.date(2026, 10, 31)

    def calculate_aging_buckets(self, open_items: List[Dict[str, Any]]) -> Dict[str, AgingBucketSummary]:
        """
        Sorts items into aging buckets based on invoice_date or posting_date.
        """
        buckets = {
            "0-30 dager": [],
            "31-60 dager": [],
            "61-90 dager": [],
            "90+ dager": []
        }

        for item in open_items:
            date_str = item.get("invoice_date") or item.get("posting_date") or "2026-10-31"
            item_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            age_days = (self.ref_date - item_date).days

            item_copy = dict(item)
            item_copy["age_days"] = age_days

            if age_days <= 30:
                buckets["0-30 dager"].append(item_copy)
            elif age_days <= 60:
                buckets["31-60 dager"].append(item_copy)
            elif age_days <= 90:
                buckets["61-90 dager"].append(item_copy)
            else:
                buckets["90+ dager"].append(item_copy)

        summaries = {}
        for b_label, items in buckets.items():
            tot_amt = sum(float(it.get("amount_nok", 0.0)) for it in items)
            rate = self.PROVISION_RATES[b_label]
            prov_amt = round(tot_amt * rate, 2)
            summaries[b_label] = AgingBucketSummary(
                bucket_label=b_label,
                total_amount_nok=tot_amt,
                item_count=len(items),
                items=items,
                provision_percentage=rate * 100,
                estimated_loss_nok=prov_amt,
                audit_risk=self.RISK_LEVELS[b_label]
            )

        return summaries

    def generate_aging_report_markdown(self, summaries: Dict[str, AgingBucketSummary]) -> str:
        """Generates an executive aging report in Markdown."""
        total_open = sum(s.total_amount_nok for s in summaries.values())
        total_items = sum(s.item_count for s in summaries.values())
        total_provision = sum(s.estimated_loss_nok for s in summaries.values())

        lines = [
            "# Rapport: Aldersfordelte Åpne Poster & Tapsavsetning",
            f"**Referansedato (Periodeslutt):** {self.ref_date.isoformat()}  ",
            f"**Totalt Uavstemt / Åpent:** {total_open:,.2f} NOK across {total_items} poster  ",
            f"**Estimert Behov for Tapsavsetning (IFRS 9):** {total_provision:,.2f} NOK  ",
            "",
            "| Alderskategori | Antall Poster | Åpent Beløp (NOK) | Andel (%) | Avsetningssats | Beregnet Avsetning (NOK) | Revisjonsrisiko |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
        ]

        for label, s in summaries.items():
            pct = (s.total_amount_nok / total_open * 100) if total_open > 0 else 0.0
            lines.append(
                f"| **{label}** | {s.item_count} | {s.total_amount_nok:,.2f} NOK | {pct:.1f}% | {s.provision_percentage:.0f}% | {s.estimated_loss_nok:,.2f} NOK | `{s.audit_risk}` |"
            )

        lines.extend([
            "",
            "### Kritiske Poster (> 60 dager / Revisjonsvarsel)",
            "Poster eldre enn 60 dager krever skriftlig bekreftelse fra prosjektleder eller revisjonssanksjonert tapsnedskriving."
        ])

        critical_items = summaries["61-90 dager"].items + summaries["90+ dager"].items
        if critical_items:
            lines.append("")
            lines.append("| ID | Motpart / Prosjekt | Beløp (NOK) | Alder | Status / Anbefalt Tiltak |")
            lines.append("| :--- | :--- | :---: | :---: | :--- |")
            for it in critical_items:
                lines.append(
                    f"| `{it.get('id', 'N/A')}` | {it.get('vendor') or it.get('customer') or 'Ukjent'} | {float(it.get('amount_nok', 0.0)):,.2f} NOK | {it.get('age_days')} dager | Purring sendt / Vurderes for tapsføring |"
                )
        else:
            lines.append("\n*Ingen poster overskrider 60 dager per dags dato.*")

        return "\n".join(lines)
