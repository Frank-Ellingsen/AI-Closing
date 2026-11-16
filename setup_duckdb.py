"""
CLOSE-AI & Financial Close Control Room - DuckDB Database Initialization
Configures and populates:
1. data/reconciliation.duckdb (accounts, staging_bank, staging_erp, match_rules, analytical views)
2. data/reconciled_transactions.duckdb (reconciled matches, audit trail)
3. data/unreconciled_transactions.duckdb (open bank items, open ERP items)
"""

import os
import duckdb
from datetime import date, datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

MAIN_DB = os.path.join(DATA_DIR, 'reconciliation.duckdb')
RECON_DB = os.path.join(DATA_DIR, 'reconciled_transactions.duckdb')
UNRECON_DB = os.path.join(DATA_DIR, 'unreconciled_transactions.duckdb')


def setup_databases(data_dir: str = DATA_DIR):
    """Initializes and seeds all DuckDB databases with enterprise test fixtures."""
    main_db = os.path.join(data_dir, 'reconciliation.duckdb')
    recon_db = os.path.join(data_dir, 'reconciled_transactions.duckdb')
    unrecon_db = os.path.join(data_dir, 'unreconciled_transactions.duckdb')

    print(f"Initialiserer DuckDB databaser i '{data_dir}'...")

    # 1. reconciliation.duckdb
    with duckdb.connect(main_db) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id VARCHAR PRIMARY KEY,
                account_name VARCHAR,
                bank_iban VARCHAR,
                swift_bic VARCHAR,
                currency VARCHAR,
                ib_bank DOUBLE,
                ib_erp DOUBLE,
                rounding_tolerance DOUBLE
            );
            
            INSERT OR REPLACE INTO accounts VALUES 
            ('1925', 'Nordea Driftskonto NOK', 'NO93 1503 1234 5678', 'NDEADKKK', 'NOK', 4850000.00, 4785000.00, 0.50),
            ('1920', 'DNB Hovedkonto NOK', 'NO93 1202 3456 7890', 'DNBANOKK', 'NOK', 12500000.00, 12500000.00, 0.50),
            ('1940', 'Nordea Valutakonto EUR', 'NO93 1503 9876 5432', 'NDEADKKK', 'EUR', 320000.00, 320000.00, 0.05);

            CREATE TABLE IF NOT EXISTS staging_bank (
                tx_id VARCHAR PRIMARY KEY,
                account_id VARCHAR,
                tx_date DATE,
                amount DOUBLE,
                text VARCHAR,
                ref_id VARCHAR,
                kid VARCHAR,
                currency VARCHAR
            );

            CREATE TABLE IF NOT EXISTS staging_erp (
                voucher_no VARCHAR PRIMARY KEY,
                account_id VARCHAR,
                post_date DATE,
                amount DOUBLE,
                text VARCHAR,
                invoice_no VARCHAR,
                kid_ocr VARCHAR,
                wbs VARCHAR
            );

            CREATE TABLE IF NOT EXISTS match_rules (
                rule_id VARCHAR PRIMARY KEY,
                rule_name VARCHAR,
                priority INT,
                cardinality VARCHAR,
                criteria VARCHAR,
                date_tolerance_days INT,
                amount_tolerance DOUBLE,
                is_active BOOLEAN
            );

            INSERT OR REPLACE INTO match_rules VALUES
            ('R-01', 'Eksakt KID/OCR (Same Day)', 1, '1:1', 'Bank.KID == ERP.KID_OCR AND Bank.Belop == ERP.Belop', 0, 0.0, true),
            ('R-02', 'Fakturanr m/ Dato-Float', 2, '1:1', 'Bank.Tekst CONTAINS ERP.Fakturanr AND Bank.Belop == ERP.Belop', 3, 0.50, true),
            ('R-03', 'Nets Samleoppgjør (1:Mange)', 3, '1:M', 'Bank.Tekst CONTAINS NETS AND SUM(ERP.Belop) == Bank.Belop', 2, 0.0, true),
            ('R-SPINOFF', 'Autonome Bankgebyr & Renter', 4, '1:0', 'Bank.Tekst MATCHES (GEBYR|RENTE)', 0, 0.0, true);
        ''')

    # 2. reconciled_transactions.duckdb
    with duckdb.connect(recon_db) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS reconciled (
                match_id VARCHAR PRIMARY KEY,
                account_id VARCHAR,
                bank_tx_id VARCHAR,
                erp_voucher_no VARCHAR,
                amount DOUBLE,
                rule_applied VARCHAR,
                difference DOUBLE DEFAULT 0.0,
                matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes VARCHAR
            );
        ''')

    # 3. unreconciled_transactions.duckdb
    with duckdb.connect(unrecon_db) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS open_bank_items (
                tx_id VARCHAR PRIMARY KEY,
                account_id VARCHAR,
                tx_date DATE,
                amount DOUBLE,
                text VARCHAR,
                ref_id VARCHAR,
                category VARCHAR
            );

            CREATE TABLE IF NOT EXISTS open_erp_items (
                voucher_no VARCHAR PRIMARY KEY,
                account_id VARCHAR,
                post_date DATE,
                amount DOUBLE,
                text VARCHAR,
                invoice_no VARCHAR,
                wbs VARCHAR,
                category VARCHAR
            );

            INSERT OR REPLACE INTO open_bank_items VALUES
            ('BNK-2025-998', '1925', '2025-12-31', 55000.00, 'Kundeinnbetaling uidentifisert ref 8821', 'REF-8821', 'Kredittert Bank / Ikke debetert ERP'),
            ('BNK-2026-10-FEE', '1925', '2026-10-31', -2450.00, 'NORDEA DEPOT- OG TRANSAKSJONSGEBYR OKT 2026', 'NORDEA-FEE-10', 'Debetert Bank / Ikke kreditert ERP'),
            ('BNK-2026-10-INT', '1925', '2026-10-31', -18750.00, 'NORDEA RENTER KASSEKREDITT/LÅN PR 31.10.26', 'NORDEA-INT-10', 'Debetert Bank / Ikke kreditert ERP');

            INSERT OR REPLACE INTO open_erp_items VALUES
            ('V-2025-10492', '1925', '2025-12-30', -120000.00, 'Aker Solutions AS remittering levfakt 40019', 'FAKT-40019', 'PRJ-401_SUBSEA', 'Kredittert ERP / Ikke debetert Bank');
        ''')

    print("DuckDB tabeller opprettet og populert med suksess!")


if __name__ == '__main__':
    setup_databases()
