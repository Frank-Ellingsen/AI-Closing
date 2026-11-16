"""
CLOSE-AI: High-Performance DuckDB Reconciliation Engine
Manages persistent Reconciled Transactions and Unreconciled Transactions tables/databases
with continuous updates, atomic ACID match transactions, IFRS 9 aging, and WBS project controlling rollups.

Designed for Lead Project Controller Frank Ellingsen (Nordic Engineering Projects AS / Umoe Mandal).
"""

import os
import hashlib
import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import duckdb
import pandas as pd


class ReconciliationDuckDBManager:
    """
    Manages DuckDB persistent analytical databases for:
    1. reconciled_transactions (settled matches, audit hashes, 1:1, 1:M, fee deductions, auto-tolerances)
    2. unreconciled_transactions (open items, transit items, RAG status, aging buckets, WBS tracking)
    
    Supports transactional ACID state transitions ('fortløpende oppdatering').
    """

    def __init__(
        self,
        db_path: str = "data/reconciliation.duckdb",
        reconciled_db_path: Optional[str] = "data/reconciled_transactions.duckdb",
        unreconciled_db_path: Optional[str] = "data/unreconciled_transactions.duckdb"
    ):
        self.db_path = db_path
        self.reconciled_db_path = reconciled_db_path
        self.unreconciled_db_path = unreconciled_db_path
        
        # Ensure target data directory exists
        for p in [self.db_path, self.reconciled_db_path, self.unreconciled_db_path]:
            if p:
                os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
                
        self.con = duckdb.connect(database=self.db_path)
        self._init_schemas()

    def _init_schemas(self):
        """Initializes tables, indexes, and analytical views in DuckDB."""
        # 1. Reconciled Transactions Table
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS reconciled_transactions (
                reconciliation_id VARCHAR PRIMARY KEY,
                match_group_id VARCHAR NOT NULL,
                match_type VARCHAR NOT NULL,             -- '1:1', '1:M', 'M:1', 'M:M', 'TOLERANCE_AUTO'
                match_rule_code VARCHAR NOT NULL,        -- 'R-EXACT-1TO1', 'R-NETS-1TOM', 'R-TOLERANCE-AUTO'
                account_number VARCHAR NOT NULL,         -- '1920', '1950', etc.
                source_system VARCHAR NOT NULL,          -- 'BANK_DNB', 'ERP_SUBLEDGER', 'ERP_GL'
                transaction_id VARCHAR NOT NULL,
                posting_date DATE NOT NULL,
                value_date DATE,
                gross_amount_nok DECIMAL(18,2) NOT NULL,
                fee_deduction_nok DECIMAL(18,2) DEFAULT 0.00,
                net_matched_nok DECIMAL(18,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'NOK',
                reference_memo VARCHAR,
                counterparty VARCHAR,
                project_id VARCHAR,
                wbs_code VARCHAR,
                matched_by VARCHAR NOT NULL,            -- 'AUTOPILOT', 'FRANK_ELLINGSEN', etc.
                matched_at TIMESTAMP NOT NULL,
                audit_hash VARCHAR(64) NOT NULL,
                status VARCHAR DEFAULT 'RECONCILED'     -- 'RECONCILED', 'CANCELLED'
            );
        """)

        # 2. Unreconciled Transactions Table
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS unreconciled_transactions (
                item_id VARCHAR PRIMARY KEY,
                source_system VARCHAR NOT NULL,         -- 'BANK_FEED', 'ERP_KUNDE_RESKONTRO', 'ERP_LEVERANDOR_RESKONTRO', 'ERP_GL'
                account_number VARCHAR NOT NULL,        -- '1920', '1950', etc.
                transaction_date DATE NOT NULL,
                due_date DATE,
                amount_nok DECIMAL(18,2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'NOK',
                reference_memo VARCHAR,
                counterparty VARCHAR,
                project_id VARCHAR,
                wbs_code VARCHAR,
                variance_type VARCHAR NOT NULL,         -- 'TIMING_TRANSIT', 'SPINOFF_PENDING', 'UNIDENTIFIED_DISCREPANCY', 'DISPUTED_ITEM'
                rag_status VARCHAR NOT NULL,            -- 'GREEN', 'AMBER', 'RED'
                age_days INTEGER NOT NULL,
                aging_bucket VARCHAR NOT NULL,          -- '0-30', '31-60', '61-90', '90+'
                provision_pct DECIMAL(5,2) DEFAULT 0.00,
                provision_nok DECIMAL(18,2) DEFAULT 0.00,
                audit_flags VARCHAR,
                status VARCHAR DEFAULT 'OPEN',          -- 'OPEN', 'PENDING_MATCH', 'RECONCILED', 'WRITTEN_OFF'
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            );
        """)

        # 3. Create Analytical Views for Instant Controlling
        self.con.execute("""
            CREATE OR REPLACE VIEW v_reconciliation_summary AS
            SELECT 
                match_type,
                match_rule_code,
                COUNT(*) AS total_items,
                SUM(gross_amount_nok) AS total_gross_nok,
                SUM(fee_deduction_nok) AS total_fees_nok,
                SUM(net_matched_nok) AS total_net_nok,
                MIN(posting_date) AS earliest_date,
                MAX(posting_date) AS latest_date
            FROM reconciled_transactions
            WHERE status = 'RECONCILED'
            GROUP BY match_type, match_rule_code;
        """)

        self.con.execute("""
            CREATE OR REPLACE VIEW v_unreconciled_aging AS
            SELECT 
                aging_bucket,
                rag_status,
                COUNT(*) AS open_count,
                SUM(amount_nok) AS total_open_amount_nok,
                SUM(provision_nok) AS total_provision_nok,
                ROUND(AVG(age_days), 1) AS avg_age_days
            FROM unreconciled_transactions
            WHERE status = 'OPEN'
            GROUP BY aging_bucket, rag_status
            ORDER BY 
                CASE aging_bucket 
                    WHEN '0-30' THEN 1 
                    WHEN '31-60' THEN 2 
                    WHEN '61-90' THEN 3 
                    WHEN '90+' THEN 4 
                    ELSE 5 
                END;
        """)

        self.con.execute("""
            CREATE OR REPLACE VIEW v_wbs_open_exposure AS
            SELECT 
                COALESCE(project_id, 'NO_PROJECT') AS project_id,
                COALESCE(wbs_code, 'UNASSIGNED') AS wbs_code,
                COUNT(*) AS open_items_count,
                SUM(CASE WHEN amount_nok > 0 THEN amount_nok ELSE 0 END) AS debit_exposure_nok,
                SUM(CASE WHEN amount_nok < 0 THEN amount_nok ELSE 0 END) AS credit_exposure_nok,
                SUM(amount_nok) AS net_exposure_nok,
                SUM(provision_nok) AS total_provision_nok
            FROM unreconciled_transactions
            WHERE status = 'OPEN'
            GROUP BY project_id, wbs_code
            ORDER BY ABS(SUM(amount_nok)) DESC;
        """)

    def compute_rag_status(self, age_days: int, amount_nok: float, variance_type: str) -> str:
        """Adheres to standard financial controlling RAG definitions."""
        if variance_type == "TIMING_TRANSIT" and age_days <= 7:
            return "GREEN"
        if age_days > 60 or abs(amount_nok) >= 100000.0 or variance_type == "DISPUTED_ITEM":
            return "RED"
        if age_days > 30 or abs(amount_nok) >= 20000.0 or variance_type == "SPINOFF_PENDING":
            return "AMBER"
        return "GREEN"

    def compute_aging_bucket_and_provision(self, age_days: int, amount_nok: float) -> Tuple[str, float, float]:
        """Calculates IFRS 9 stage provision metrics."""
        amt = abs(float(amount_nok))
        if age_days <= 30:
            return "0-30", 0.00, 0.00
        elif age_days <= 60:
            return "31-60", 0.02, round(amt * 0.02, 2)
        elif age_days <= 90:
            return "61-90", 0.10, round(amt * 0.10, 2)
        else:
            return "90+", 0.40, round(amt * 0.40, 2)

    def upsert_unreconciled_item(self, item: Dict[str, Any]) -> str:
        """
        Inserts or updates an open item into unreconciled_transactions on the fly.
        """
        item_id = item["item_id"]
        source_system = item.get("source_system", "ERP_SUBLEDGER")
        account_number = str(item.get("account_number", "1920"))
        tx_date = item.get("transaction_date", datetime.date.today().isoformat())
        due_date = item.get("due_date", tx_date)
        amount_nok = float(item["amount_nok"])
        currency = item.get("currency", "NOK")
        ref_memo = item.get("reference_memo", "")
        counterparty = item.get("counterparty", "")
        project_id = item.get("project_id", "PRJ-001")
        wbs_code = item.get("wbs_code", "WBS-001.01")
        variance_type = item.get("variance_type", "UNIDENTIFIED_DISCREPANCY")
        
        # Calculate dynamic age based on tx_date
        tx_d = datetime.date.fromisoformat(tx_date) if isinstance(tx_date, str) else tx_date
        ref_date = datetime.date(2026, 10, 31)  # Fiscal Close reference
        age_days = item.get("age_days", max(0, (ref_date - tx_d).days))
        
        rag_status = item.get("rag_status", self.compute_rag_status(age_days, amount_nok, variance_type))
        bucket, prov_pct, prov_nok = self.compute_aging_bucket_and_provision(age_days, amount_nok)
        audit_flags = item.get("audit_flags", "")
        status = item.get("status", "OPEN")
        now_ts = datetime.datetime.now()

        self.con.execute("""
            INSERT OR REPLACE INTO unreconciled_transactions (
                item_id, source_system, account_number, transaction_date, due_date,
                amount_nok, currency, reference_memo, counterparty, project_id, wbs_code,
                variance_type, rag_status, age_days, aging_bucket, provision_pct, provision_nok,
                audit_flags, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            item_id, source_system, account_number, tx_date, due_date,
            amount_nok, currency, ref_memo, counterparty, project_id, wbs_code,
            variance_type, rag_status, age_days, bucket, prov_pct, prov_nok,
            audit_flags, status, now_ts, now_ts
        ])
        return item_id

    def reconcile_match(
        self,
        match_group_id: str,
        match_type: str,
        match_rule_code: str,
        bank_tx: Dict[str, Any],
        matched_items: List[Dict[str, Any]],
        fee_deduction_nok: float = 0.0,
        matched_by: str = "AUTOPILOT"
    ) -> List[str]:
        """
        Executes an atomic ACID reconciliation match:
        1. Inserts records into reconciled_transactions.
        2. Sets matched items status to 'RECONCILED' in unreconciled_transactions.
        3. Generates cryptographic SHA-256 audit hash.
        """
        reconciliation_ids = []
        now_ts = datetime.datetime.now()
        
        self.con.execute("BEGIN TRANSACTION;")
        try:
            # 1. Process Bank Transaction line
            bank_id = f"REC-B-{bank_tx['tx_id']}"
            raw_hash_data = f"{match_group_id}_{bank_tx['tx_id']}_{bank_tx['amount_nok']}_{now_ts.isoformat()}"
            audit_hash = hashlib.sha256(raw_hash_data.encode("utf-8")).hexdigest()
            
            self.con.execute("""
                INSERT OR REPLACE INTO reconciled_transactions (
                    reconciliation_id, match_group_id, match_type, match_rule_code,
                    account_number, source_system, transaction_id, posting_date, value_date,
                    gross_amount_nok, fee_deduction_nok, net_matched_nok, currency,
                    reference_memo, counterparty, project_id, wbs_code,
                    matched_by, matched_at, audit_hash, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'RECONCILED');
            """, [
                bank_id, match_group_id, match_type, match_rule_code,
                str(bank_tx.get("account_number", "1920")), "BANK_FEED",
                bank_tx["tx_id"], bank_tx.get("posting_date", "2026-10-31"),
                bank_tx.get("posting_date", "2026-10-31"),
                float(bank_tx["amount_nok"]), float(fee_deduction_nok),
                float(bank_tx["amount_nok"]), bank_tx.get("currency", "NOK"),
                bank_tx.get("raw_memo", ""), bank_tx.get("counterparty", ""),
                bank_tx.get("project_id", "PRJ-001"), bank_tx.get("wbs_code", "WBS-001.01"),
                matched_by, now_ts, audit_hash
            ])
            reconciliation_ids.append(bank_id)

            # Mark bank tx as reconciled in unreconciled_transactions if it exists there
            self.con.execute("""
                UPDATE unreconciled_transactions 
                SET status = 'RECONCILED', updated_at = ? 
                WHERE item_id = ?;
            """, [now_ts, bank_tx["tx_id"]])

            # 2. Process Matched Subledger Items
            for item in matched_items:
                rec_item_id = f"REC-S-{item['id']}"
                item_hash_data = f"{match_group_id}_{item['id']}_{item['amount_nok']}_{now_ts.isoformat()}"
                item_hash = hashlib.sha256(item_hash_data.encode("utf-8")).hexdigest()

                self.con.execute("""
                    INSERT OR REPLACE INTO reconciled_transactions (
                        reconciliation_id, match_group_id, match_type, match_rule_code,
                        account_number, source_system, transaction_id, posting_date, value_date,
                        gross_amount_nok, fee_deduction_nok, net_matched_nok, currency,
                        reference_memo, counterparty, project_id, wbs_code,
                        matched_by, matched_at, audit_hash, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'RECONCILED');
                """, [
                    rec_item_id, match_group_id, match_type, match_rule_code,
                    str(item.get("account_number", "1920")), "ERP_SUBLEDGER",
                    item["id"], item.get("invoice_date", "2026-10-31"),
                    item.get("invoice_date", "2026-10-31"),
                    float(item["amount_nok"]), 0.00,
                    float(item["amount_nok"]), item.get("currency", "NOK"),
                    item.get("po_number", ""), item.get("vendor", ""),
                    item.get("project_id", "PRJ-001"), item.get("wbs_code", "WBS-001.01"),
                    matched_by, now_ts, item_hash
                ])
                reconciliation_ids.append(rec_item_id)

                # Update unreconciled table
                self.con.execute("""
                    UPDATE unreconciled_transactions 
                    SET status = 'RECONCILED', updated_at = ? 
                    WHERE item_id = ?;
                """, [now_ts, item["id"]])

            self.con.execute("COMMIT;")
            self._sync_satellite_databases()
            return reconciliation_ids
        except Exception as e:
            self.con.execute("ROLLBACK;")
            raise e

    def unreconcile_group(self, match_group_id: str) -> int:
        """
        Reverses a reconciliation group, reopening the items in unreconciled_transactions.
        """
        now_ts = datetime.datetime.now()
        self.con.execute("BEGIN TRANSACTION;")
        try:
            # Get list of transaction IDs in this group
            rows = self.con.execute("""
                SELECT transaction_id FROM reconciled_transactions 
                WHERE match_group_id = ? AND status = 'RECONCILED';
            """, [match_group_id]).fetchall()
            
            tx_ids = [r[0] for r in rows]
            
            # Cancel reconciled records
            self.con.execute("""
                UPDATE reconciled_transactions 
                SET status = 'CANCELLED' 
                WHERE match_group_id = ?;
            """, [match_group_id])

            # Re-open in unreconciled_transactions
            for tx_id in tx_ids:
                self.con.execute("""
                    UPDATE unreconciled_transactions 
                    SET status = 'OPEN', updated_at = ? 
                    WHERE item_id = ?;
                """, [now_ts, tx_id])

            self.con.execute("COMMIT;")
            self._sync_satellite_databases()
            return len(tx_ids)
        except Exception as e:
            self.con.execute("ROLLBACK;")
            raise e

    def _sync_satellite_databases(self):
        """
        Optionally synchronizes dedicated satellite duckdb files:
        data/reconciled_transactions.duckdb & data/unreconciled_transactions.duckdb
        """
        try:
            if self.reconciled_db_path:
                sat_rec = duckdb.connect(database=self.reconciled_db_path)
                df_rec = self.con.execute("SELECT * FROM reconciled_transactions").df()
                sat_rec.execute("CREATE OR REPLACE TABLE reconciled_transactions AS SELECT * FROM df_rec")
                sat_rec.close()

            if self.unreconciled_db_path:
                sat_unrec = duckdb.connect(database=self.unreconciled_db_path)
                df_unrec = self.con.execute("SELECT * FROM unreconciled_transactions").df()
                sat_unrec.execute("CREATE OR REPLACE TABLE unreconciled_transactions AS SELECT * FROM df_unrec")
                sat_unrec.close()
        except Exception as e:
            # Non-blocking satellite sync
            pass

    def get_reconciled_df(self, active_only: bool = True) -> pd.DataFrame:
        query = "SELECT * FROM reconciled_transactions"
        if active_only:
            query += " WHERE status = 'RECONCILED'"
        query += " ORDER BY posting_date DESC"
        return self.con.execute(query).df()

    def get_unreconciled_df(self, open_only: bool = True) -> pd.DataFrame:
        query = "SELECT * FROM unreconciled_transactions"
        if open_only:
            query += " WHERE status = 'OPEN'"
        query += " ORDER BY age_days DESC, ABS(amount_nok) DESC"
        return self.con.execute(query).df()

    def get_metrics(self) -> Dict[str, Any]:
        """Calculates live KPI metrics directly with DuckDB SQL."""
        rec_stats = self.con.execute("""
            SELECT 
                COUNT(*) AS count,
                COALESCE(SUM(gross_amount_nok), 0.0) AS total_gross,
                COALESCE(SUM(fee_deduction_nok), 0.0) AS total_fees,
                COALESCE(SUM(net_matched_nok), 0.0) AS total_net
            FROM reconciled_transactions
            WHERE status = 'RECONCILED';
        """).fetchone()

        unrec_stats = self.con.execute("""
            SELECT 
                COUNT(*) AS count,
                COALESCE(SUM(amount_nok), 0.0) AS total_open,
                COALESCE(SUM(provision_nok), 0.0) AS total_provision,
                COALESCE(SUM(CASE WHEN rag_status = 'RED' THEN 1 ELSE 0 END), 0) AS red_count,
                COALESCE(SUM(CASE WHEN rag_status = 'AMBER' THEN 1 ELSE 0 END), 0) AS amber_count,
                COALESCE(SUM(CASE WHEN rag_status = 'GREEN' THEN 1 ELSE 0 END), 0) AS green_count
            FROM unreconciled_transactions
            WHERE status = 'OPEN';
        """).fetchone()

        return {
            "reconciled_count": rec_stats[0],
            "reconciled_gross_nok": float(rec_stats[1]),
            "reconciled_fees_nok": float(rec_stats[2]),
            "reconciled_net_nok": float(rec_stats[3]),
            "unreconciled_count": unrec_stats[0],
            "unreconciled_open_nok": float(unrec_stats[1]),
            "unreconciled_provision_nok": float(unrec_stats[2]),
            "rag_distribution": {
                "red": unrec_stats[3],
                "amber": unrec_stats[4],
                "green": unrec_stats[5]
            }
        }

    def populate_from_pipeline_feed(
        self,
        bank_lines: List[Dict[str, Any]],
        open_invoices: List[Dict[str, Any]],
        proposals: List[Dict[str, Any]]
    ):
        """
        Populates both tables from raw close pipeline feed and marks matched proposals.
        """
        # 1. Ingest Bank lines into unreconciled table first
        for b in bank_lines:
            self.upsert_unreconciled_item({
                "item_id": b["tx_id"],
                "source_system": "BANK_FEED",
                "account_number": "1920",
                "transaction_date": b.get("posting_date", "2026-10-31"),
                "due_date": b.get("posting_date", "2026-10-31"),
                "amount_nok": b["amount_nok"],
                "reference_memo": b.get("raw_memo", ""),
                "counterparty": "DNB Bank ASA",
                "project_id": "PRJ-001",
                "wbs_code": "WBS-001.01",
                "variance_type": "TIMING_TRANSIT" if "BERGEN" in b.get("raw_memo", "") else "UNIDENTIFIED_DISCREPANCY"
            })

        # 2. Ingest Subledger items into unreconciled table
        for inv in open_invoices:
            self.upsert_unreconciled_item({
                "item_id": inv["id"],
                "source_system": "ERP_LEVERANDOR_RESKONTRO",
                "account_number": "1920",
                "transaction_date": inv["invoice_date"],
                "due_date": inv.get("due_date", inv["invoice_date"]),
                "amount_nok": inv["amount_nok"],
                "reference_memo": inv.get("po_number", ""),
                "counterparty": inv.get("vendor", ""),
                "project_id": inv.get("project_id", "PRJ-001"),
                "wbs_code": inv.get("wbs_code", "WBS-001.02"),
                "variance_type": "TIMING_TRANSIT" if "BERGEN" in inv.get("vendor", "").upper() else "UNIDENTIFIED_DISCREPANCY"
            })

        # 3. Apply Reconciled Matches from Proposals
        for p in proposals:
            match_group_id = p["proposal_id"]
            match_type = p.get("match_type", "1:1")
            match_rule = "R-NETS-1TOM" if "1:" in match_type else "R-EXACT-1TO1"
            bank_tx = p["bank_transaction"]
            subledger_items = p.get("matched_subledger_lines", [])
            fee_deduction = p.get("isolated_fee_nok", 0.0)

            self.reconcile_match(
                match_group_id=match_group_id,
                match_type=match_type,
                match_rule_code=match_rule,
                bank_tx=bank_tx,
                matched_items=subledger_items,
                fee_deduction_nok=fee_deduction,
                matched_by="CLOSE_AI_AUTOPILOT"
            )

    def close(self):
        """Closes DuckDB connection cleanly."""
        if self.con:
            self.con.close()
