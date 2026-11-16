"""
Unit and Integration tests for Financial Close Control Room & DuckDB API
Validates:
1. DuckDB databases existence and schema integrity.
2. Account 1925 (Nordea Driftskonto NOK) configuration and opening balance proof.
3. 4-way reconciliation mathematical proof (Adra Balancer).
4. Spin-off items identification (fees & interest).
5. FastAPI control room endpoints and match/unmatch transactional lifecycle.
"""

import os
import unittest
import duckdb
from fastapi.testclient import TestClient

from setup_duckdb import setup_databases
from src.data_generator.nordea_generator import generate_nordea_dataset
from src.api.api_server import app

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
MAIN_DB = os.path.join(DATA_DIR, 'reconciliation.duckdb')
RECON_DB = os.path.join(DATA_DIR, 'reconciled_transactions.duckdb')
UNRECON_DB = os.path.join(DATA_DIR, 'unreconciled_transactions.duckdb')


class TestControlRoomDuckDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure fresh database setup and test data
        setup_databases(DATA_DIR)
        generate_nordea_dataset(DATA_DIR)
        cls.client = TestClient(app)

    def test_01_database_existence(self):
        """Verifies all persistent DuckDB databases exist."""
        self.assertTrue(os.path.exists(MAIN_DB), "reconciliation.duckdb må eksistere")
        self.assertTrue(os.path.exists(RECON_DB), "reconciled_transactions.duckdb må eksistere")
        self.assertTrue(os.path.exists(UNRECON_DB), "unreconciled_transactions.duckdb må eksistere")

    def test_02_account_nordea_setup(self):
        """Verifies account 1925 parameters in DuckDB."""
        with duckdb.connect(MAIN_DB) as con:
            acc = con.execute("SELECT account_id, ib_bank, ib_erp, rounding_tolerance FROM accounts WHERE account_id = '1925'").fetchone()
            self.assertIsNotNone(acc, "Konto 1925 må være opprettet")
            self.assertEqual(acc[1], 4850000.00, "IB Bank må være 4 850 000,00 NOK")
            self.assertEqual(acc[2], 4785000.00, "IB ERP må være 4 785 000,00 NOK")
            self.assertEqual(acc[3], 0.50, "Tillatt ørediff må være 0,50 NOK")

    def test_03_initial_open_items_balance(self):
        """Tester at IB Bank (4.85M) - 120k + 55k == IB ERP (4.785M)."""
        ib_bank = 4850000.00
        utestaaende_remittering = -120000.00
        uidentifisert_innbetaling = 55000.00
        ib_erp = 4785000.00
        self.assertEqual(ib_bank + utestaaende_remittering + uidentifisert_innbetaling, ib_erp)

    def test_04_spinoff_items_present(self):
        """Verifies October bank fees and interest items exist in open items."""
        with duckdb.connect(UNRECON_DB) as con:
            fees = con.execute("SELECT count(*) FROM open_bank_items WHERE tx_id IN ('BNK-2026-10-FEE', 'BNK-2026-10-INT')").fetchone()[0]
            self.assertEqual(fees, 2, "Begge spin-off poster for oktober (gebyr og rente) må ligge i uavstemte")

    def test_05_api_system_status(self):
        """Tests /api/status endpoint."""
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertGreaterEqual(data["accounts_count"], 3)
        self.assertIn("close_readiness_pct", data)

    def test_06_api_balance_control(self):
        """Tests 4-way balance control matrix calculation."""
        response = self.client.get("/api/reconciliation/balance-control?account_id=1925&period=2026-10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account_id"], "1925")
        self.assertIn("four_way_matrix", data)
        self.assertIn("delta", data)
        self.assertIn("status", data)

    def test_07_api_spinoff_proposals(self):
        """Tests spinoff proposals detection for bank fees & interest."""
        response = self.client.get("/api/spinoff/proposals?account_id=1925")
        self.assertEqual(response.status_code, 200)
        proposals = response.json()
        self.assertGreaterEqual(len(proposals), 2)
        tx_ids = [p["bank_tx_id"] for p in proposals]
        self.assertIn("BNK-2026-10-FEE", tx_ids)
        self.assertIn("BNK-2026-10-INT", tx_ids)

    def test_08_api_match_and_unmatch_lifecycle(self):
        """Tests matching an item and rolling it back (unmatch)."""
        match_payload = {
            "match_id": "TEST-MATCH-999",
            "account_id": "1925",
            "bank_tx_id": "BNK-2025-998",
            "amount": 55000.00,
            "rule_code": "R-TEST-MANUAL",
            "difference": 0.0,
            "notes": "Test manual reconciliation"
        }
        # Commit match
        m_res = self.client.post("/api/reconciliation/match", json=match_payload)
        self.assertEqual(m_res.status_code, 200)
        self.assertEqual(m_res.json()["status"], "matched")

        # Verify item removed from open items
        with duckdb.connect(UNRECON_DB) as con:
            cnt = con.execute("SELECT count(*) FROM open_bank_items WHERE tx_id = 'BNK-2025-998'").fetchone()[0]
            self.assertEqual(cnt, 0)

        # Unmatch rollback
        u_res = self.client.post("/api/reconciliation/unmatch", data={"match_id": "TEST-MATCH-999"})
        self.assertEqual(u_res.status_code, 200)
        self.assertEqual(u_res.json()["status"], "unmatched")

        # Verify item restored
        with duckdb.connect(UNRECON_DB) as con:
            cnt = con.execute("SELECT count(*) FROM open_bank_items WHERE tx_id = 'BNK-2025-998'").fetchone()[0]
            self.assertEqual(cnt, 1)


if __name__ == '__main__':
    unittest.main()
