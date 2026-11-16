"""
Unit tests for DuckDB Reconciliation Engine (Reconciled & Unreconciled Databases)
"""

import os
import shutil
import unittest
import duckdb
from src.lakehouse.reconciliation_duckdb import ReconciliationDuckDBManager

class TestReconciliationDuckDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = "data/test_duckdb"
        os.makedirs(self.test_dir, exist_ok=True)
        self.db_path = os.path.join(self.test_dir, "test_reconciliation.duckdb")
        self.rec_sat_path = os.path.join(self.test_dir, "test_reconciled.duckdb")
        self.unrec_sat_path = os.path.join(self.test_dir, "test_unreconciled.duckdb")
        
        self.manager = ReconciliationDuckDBManager(
            db_path=self.db_path,
            reconciled_db_path=self.rec_sat_path,
            unreconciled_db_path=self.unrec_sat_path
        )

    def tearDown(self):
        self.manager.close()
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    def test_schema_initialization(self):
        """Verifies tables and views exist in DuckDB."""
        tables = [t[0] for t in self.manager.con.execute("SHOW TABLES").fetchall()]
        self.assertIn("reconciled_transactions", tables)
        self.assertIn("unreconciled_transactions", tables)
        self.assertIn("v_reconciliation_summary", tables)
        self.assertIn("v_unreconciled_aging", tables)
        self.assertIn("v_wbs_open_exposure", tables)

    def test_upsert_unreconciled_items_and_rag(self):
        """Verifies open items are ingested with correct aging and RAG status."""
        item1 = {
            "item_id": "INV-TEST-01",
            "source_system": "ERP_SUBLEDGER",
            "account_number": "1920",
            "transaction_date": "2026-10-25",
            "amount_nok": 45000.0,
            "variance_type": "TIMING_TRANSIT",
            "project_id": "PRJ-UM-2026",
            "wbs_code": "WBS-014.2"
        }
        item2 = {
            "item_id": "INV-TEST-02",
            "source_system": "ERP_SUBLEDGER",
            "account_number": "1920",
            "transaction_date": "2026-07-01",
            "amount_nok": 185000.0,
            "variance_type": "DISPUTED_ITEM",
            "project_id": "PRJ-UM-2026",
            "wbs_code": "WBS-014.5"
        }

        self.manager.upsert_unreconciled_item(item1)
        self.manager.upsert_unreconciled_item(item2)

        df_unrec = self.manager.get_unreconciled_df()
        self.assertEqual(len(df_unrec), 2)
        
        row1 = df_unrec[df_unrec["item_id"] == "INV-TEST-01"].iloc[0]
        self.assertEqual(row1["aging_bucket"], "0-30")
        self.assertEqual(row1["rag_status"], "GREEN")
        self.assertEqual(row1["provision_nok"], 0.0)

        row2 = df_unrec[df_unrec["item_id"] == "INV-TEST-02"].iloc[0]
        self.assertEqual(row2["aging_bucket"], "90+")
        self.assertEqual(row2["rag_status"], "RED")
        self.assertEqual(row2["provision_nok"], 74000.0)  # 40% of 185,000

    def test_atomic_reconcile_match_transition(self):
        """Verifies atomic transition from unreconciled to reconciled."""
        # 1. Ingest items
        bank_tx = {
            "tx_id": "BANK-TX-99",
            "amount_nok": 89512.50,
            "posting_date": "2026-10-31",
            "raw_memo": "CR-ADYEN-88491",
            "account_number": "1920"
        }
        subledger_item = {
            "id": "INV-101",
            "amount_nok": 91550.00,
            "invoice_date": "2026-10-20",
            "vendor": "Equinor",
            "account_number": "1920",
            "project_id": "PRJ-001"
        }
        
        self.manager.upsert_unreconciled_item({
            "item_id": bank_tx["tx_id"],
            "amount_nok": bank_tx["amount_nok"],
            "transaction_date": bank_tx["posting_date"],
            "variance_type": "TIMING_TRANSIT"
        })
        self.manager.upsert_unreconciled_item({
            "item_id": subledger_item["id"],
            "amount_nok": subledger_item["amount_nok"],
            "transaction_date": subledger_item["invoice_date"],
            "variance_type": "UNIDENTIFIED_DISCREPANCY"
        })

        metrics_before = self.manager.get_metrics()
        self.assertEqual(metrics_before["unreconciled_count"], 2)
        self.assertEqual(metrics_before["reconciled_count"], 0)

        # 2. Execute Match
        rec_ids = self.manager.reconcile_match(
            match_group_id="PROP-MATCH-01",
            match_type="1:1",
            match_rule_code="R-NETS-1TOM",
            bank_tx=bank_tx,
            matched_items=[subledger_item],
            fee_deduction_nok=2037.50,
            matched_by="FRANK_ELLINGSEN"
        )
        self.assertEqual(len(rec_ids), 2)

        # 3. Verify that items moved to reconciled and are no longer in open unreconciled
        metrics_after = self.manager.get_metrics()
        self.assertEqual(metrics_after["reconciled_count"], 2)
        self.assertEqual(metrics_after["unreconciled_count"], 0)
        self.assertEqual(metrics_after["reconciled_fees_nok"], 2037.50)

        # 4. Verify unreconcile (rollback/omgjøring)
        reopened_count = self.manager.unreconcile_group("PROP-MATCH-01")
        self.assertEqual(reopened_count, 2)
        metrics_reopened = self.manager.get_metrics()
        self.assertEqual(metrics_reopened["reconciled_count"], 0)
        self.assertEqual(metrics_reopened["unreconciled_count"], 2)

    def test_wbs_exposure_view(self):
        """Verifies WBS Project Controlling rollup in DuckDB view."""
        self.manager.upsert_unreconciled_item({
            "item_id": "WBS-ITEM-1",
            "amount_nok": 50000.0,
            "project_id": "PRJ-UMOE-MANDAL",
            "wbs_code": "WBS-HULL-01",
            "transaction_date": "2026-10-15"
        })
        self.manager.upsert_unreconciled_item({
            "item_id": "WBS-ITEM-2",
            "amount_nok": 30000.0,
            "project_id": "PRJ-UMOE-MANDAL",
            "wbs_code": "WBS-HULL-01",
            "transaction_date": "2026-10-20"
        })

        res = self.manager.con.execute("""
            SELECT project_id, wbs_code, net_exposure_nok 
            FROM v_wbs_open_exposure 
            WHERE project_id = 'PRJ-UMOE-MANDAL';
        """).fetchall()

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "PRJ-UMOE-MANDAL")
        self.assertEqual(res[0][1], "WBS-HULL-01")
        self.assertEqual(res[0][2], 80000.0)

if __name__ == "__main__":
    unittest.main()
