"""
CLOSE-AI: Controller Evidence Graph
Traverses relational ERP entities deterministically to assemble the operational chain of custody:
Invoice -> PO -> PO Line -> WBS -> Project -> Customer / Contract -> Vendor
GL Journal Line -> GL Entry -> Account -> Cost Center -> Project / WBS
"""

import os
import duckdb
import pandas as pd
from typing import Dict, Any, Optional

class ControllerEvidenceGraph:
    def __init__(self, data_dir: str = "erp_data_2026_10"):
        self.data_dir = data_dir
        self.con = duckdb.connect(database=":memory:")
        self._load_tables()

    def _load_tables(self):
        tables = [
            "divisions", "cost_centers", "vendors", "projects", "wbs_elements",
            "purchase_orders", "po_lines", "vendor_invoices",
            "gl_journal_entries", "gl_journal_lines"
        ]
        for tbl in tables:
            pq_path = os.path.join(self.data_dir, f"{tbl}.parquet")
            csv_path = os.path.join(self.data_dir, f"{tbl}.csv")
            if os.path.exists(pq_path):
                self.con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_parquet('{pq_path.replace(chr(92), '/')}')")
            elif os.path.exists(csv_path):
                self.con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_path.replace(chr(92), '/')}')")

    def trace_invoice_pedigree(self, invoice_id: str) -> Dict[str, Any]:
        """
        Gathers complete upstream and downstream lineage for an invoice.
        """
        if not invoice_id or not isinstance(invoice_id, str):
            return {"error": "Invoice ID must be a non-empty string."}

        inv_df = self.con.execute("SELECT * FROM vendor_invoices WHERE invoice_id = ?", [invoice_id]).df()
        if inv_df.empty:
            return {"error": f"Invoice {invoice_id} not found."}
        
        inv = inv_df.iloc[0].to_dict()
        po_number = inv.get("po_number")

        po_info = {}
        po_lines = []
        if po_number:
            po_hdr = self.con.execute("SELECT * FROM purchase_orders WHERE po_number = ?", [po_number]).df()
            if not po_hdr.empty:
                po_info = po_hdr.iloc[0].to_dict()
            po_lines_df = self.con.execute("SELECT * FROM po_lines WHERE po_number = ?", [po_number]).df()
            po_lines = po_lines_df.to_dict(orient="records")

        wbs_code = inv.get("wbs_code")
        wbs_info = {}
        if wbs_code:
            wbs_df = self.con.execute("SELECT * FROM wbs_elements WHERE wbs_code = ?", [wbs_code]).df()
            if not wbs_df.empty:
                wbs_info = wbs_df.iloc[0].to_dict()

        prj_id = inv.get("project_id") or (wbs_info.get("project_id") if wbs_info else None)
        prj_info = {}
        if prj_id:
            prj_df = self.con.execute("SELECT * FROM projects WHERE project_id = ?", [prj_id]).df()
            if not prj_df.empty:
                prj_info = prj_df.iloc[0].to_dict()

        vendor_id = inv.get("vendor_id")
        vendor_info = {}
        if vendor_id:
            v_df = self.con.execute("SELECT * FROM vendors WHERE vendor_id = ?", [vendor_id]).df()
            if not v_df.empty:
                vendor_info = v_df.iloc[0].to_dict()

        po_amount_authorized = sum(float(l["total_amount_nok"]) for l in po_lines) if po_lines else 0.0
        invoice_amount = float(inv.get("amount_nok", 0.0))
        variance_nok = round(invoice_amount - po_amount_authorized, 2)
        variance_pct = round((variance_nok / po_amount_authorized * 100), 2) if po_amount_authorized > 0 else 0.0

        return {
            "target_type": "VENDOR_INVOICE",
            "invoice": inv,
            "po": po_info,
            "po_lines": po_lines,
            "po_amount_authorized_nok": po_amount_authorized,
            "variance_nok": variance_nok,
            "variance_pct": variance_pct,
            "wbs": wbs_info,
            "project": prj_info,
            "vendor": vendor_info,
            "provenance": {
                "source_table": "vendor_invoices",
                "record_id": invoice_id,
                "related_tables": ["purchase_orders", "po_lines", "wbs_elements", "projects", "vendors"],
                "trace_path": ["invoice", "po", "po_lines", "wbs", "project", "vendor"]
            }
        }

    def trace_gl_entry_pedigree(self, entry_id: str) -> Dict[str, Any]:
        """
        Traverses a GL journal entry and its lines.
        """
        if not entry_id or not isinstance(entry_id, str):
            return {"error": "Entry ID must be a non-empty string."}

        entry_df = self.con.execute("SELECT * FROM gl_journal_entries WHERE entry_id = ?", [entry_id]).df()
        if entry_df.empty:
            return {"error": f"GL Entry {entry_id} not found."}
        
        entry = entry_df.iloc[0].to_dict()
        lines_df = self.con.execute("SELECT * FROM gl_journal_lines WHERE entry_id = ?", [entry_id]).df()
        lines = lines_df.to_dict(orient="records")

        total_debit = sum(float(l["debit_nok"]) for l in lines)
        total_credit = sum(float(l["credit_nok"]) for l in lines)
        imbalance = round(abs(total_debit - total_credit), 2)

        return {
            "target_type": "GL_JOURNAL_ENTRY",
            "entry": entry,
            "lines": lines,
            "total_debit_nok": total_debit,
            "total_credit_nok": total_credit,
            "imbalance_nok": imbalance,
            "provenance": {
                "source_table": "gl_journal_entries",
                "record_id": entry_id,
                "related_tables": ["gl_journal_lines"],
                "trace_path": ["entry", "lines"]
            }
        }

    def trace_uninvoiced_po(self, po_number: str) -> Dict[str, Any]:
        """
        Traverses delivered PO lines lacking invoices.
        """
        if not po_number or not isinstance(po_number, str):
            return {"error": "PO number must be a non-empty string."}

        po_hdr = self.con.execute("SELECT * FROM purchase_orders WHERE po_number = ?", [po_number]).df()
        po_info = po_hdr.iloc[0].to_dict() if not po_hdr.empty else {}
        po_lines = self.con.execute("SELECT * FROM po_lines WHERE po_number = ?", [po_number]).df().to_dict(orient="records")
        total_unbilled = sum(float(l["total_amount_nok"]) for l in po_lines)

        prj_id = po_info.get("project_id")
        prj_info = {}
        if prj_id:
            prj_df = self.con.execute("SELECT * FROM projects WHERE project_id = ?", [prj_id]).df()
            if not prj_df.empty:
                prj_info = prj_df.iloc[0].to_dict()

        vendor_id = po_info.get("vendor_id")
        v_info = {}
        if vendor_id:
            v_df = self.con.execute("SELECT * FROM vendors WHERE vendor_id = ?", [vendor_id]).df()
            if not v_df.empty:
                v_info = v_df.iloc[0].to_dict()

        return {
            "target_type": "UNINVOICED_PURCHASE_ORDER",
            "po": po_info,
            "po_lines": po_lines,
            "total_unbilled_nok": total_unbilled,
            "project": prj_info,
            "vendor": v_info,
            "provenance": {
                "source_table": "purchase_orders",
                "record_id": po_number,
                "related_tables": ["po_lines", "projects", "vendors"],
                "trace_path": ["po", "po_lines", "project", "vendor"]
            }
        }

if __name__ == "__main__":
    graph = ControllerEvidenceGraph()
    pedigree = graph.trace_invoice_pedigree("INV-VEND-99214")
    print(f"Traced invoice {pedigree['invoice']['invoice_id']}: Variance {pedigree['variance_nok']} NOK ({pedigree['variance_pct']}%)")
