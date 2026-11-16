"""
CLOSE-AI & Financial Close Control Room - Nordea Bank & General Ledger Generator
Generates:
1. Nordea Driftskonto NOK (1925) multi-month transaction flows (Jan-Oct 2026).
2. Staging tables (staging_bank, staging_erp) in DuckDB.
3. Bank and ERP statement CSV extracts and JSON reconciliation balance summaries.
"""

import os
import json
import duckdb
import pandas as pd
from typing import Dict, Any


def generate_nordea_dataset(data_dir: str = "data") -> Dict[str, Any]:
    """Generates synthetic Nordea bank and ERP GL transactions for account 1925."""
    os.makedirs(data_dir, exist_ok=True)
    main_db = os.path.join(data_dir, 'reconciliation.duckdb')

    # Detailed transactions for October 2026
    okt_bank = [
        ("BNK-2026-1001", "1925", "2026-10-02", 1450000.00, "INNBET EQUINOR ASA KID 992019401", "REF-99201", "992019401", "NOK"),
        ("BNK-2026-1002", "1925", "2026-10-05", -840000.00, "REMITTERING AKER BP FAKT 48820", "REF-48820", "", "NOK"),
        ("BNK-2026-1003", "1925", "2026-10-12", 2150000.00, "INNBET VÅR ENERGI KID 883011402", "REF-88301", "883011402", "NOK"),
        ("BNK-2026-1004", "1925", "2026-10-15", -1220000.00, "REMITTERING SUBSEA 7 FAKT 51109", "REF-51109", "", "NOK"),
        ("BNK-2026-1005", "1925", "2026-10-22", 3450000.00, "NETS OPPGJØR SAMLEINNBETALING", "NETS-88401", "", "NOK"),
        ("BNK-2026-1006", "1925", "2026-10-25", -5560000.00, "REMITTERING KONGSBERG MARITIME", "REF-77201", "", "NOK"),
        ("BNK-2026-1007", "1925", "2026-10-28", 1070400.00, "INNBET MORELD FLOW TECH KID 773019", "REF-77301", "773019", "NOK"),
        ("BNK-2026-10-FEE", "1925", "2026-10-31", -2450.00, "NORDEA DEPOT- OG TRANSAKSJONSGEBYR OKT 2026", "NORDEA-FEE-10", "", "NOK"),
        ("BNK-2026-10-INT", "1925", "2026-10-31", -18750.00, "NORDEA RENTER KASSEKREDITT/LÅN PR 31.10.26", "NORDEA-INT-10", "", "NOK")
    ]
    
    okt_erp = [
        ("V-2026-1001", "1925", "2026-10-02", 1450000.00, "Kundeinnbetaling Equinor ASA", "F-99201", "992019401", "PRJ-401_SUBSEA"),
        ("V-2026-1002", "1925", "2026-10-05", -840000.00, "Leverandørremittering Aker BP", "F-48820", "", "PRJ-402_TOPSIDE"),
        ("V-2026-1003", "1925", "2026-10-12", 2150000.00, "Kundeinnbetaling Vår Energi", "F-88301", "883011402", "PRJ-401_SUBSEA"),
        ("V-2026-1004", "1925", "2026-10-15", -1220000.00, "Leverandørremittering Subsea 7", "F-51109", "", "PRJ-403_PIPELINE"),
        ("V-2026-1005", "1925", "2026-10-22", 3450000.00, "Nets oppgjør terminal batch", "NETS-88401", "", "PRJ-ADMIN"),
        ("V-2026-1006", "1925", "2026-10-25", -5560000.00, "Leverandørremittering Kongsberg", "F-77201", "", "PRJ-402_TOPSIDE"),
        ("V-2026-1007", "1925", "2026-10-28", 1070400.00, "Kundeinnbetaling Moreld Flow", "F-77301", "773019", "PRJ-401_SUBSEA")
    ]

    # Populate DuckDB staging tables
    if os.path.exists(main_db):
        with duckdb.connect(main_db) as con:
            con.execute("CREATE TABLE IF NOT EXISTS staging_bank (tx_id VARCHAR PRIMARY KEY, account_id VARCHAR, tx_date DATE, amount DOUBLE, text VARCHAR, ref_id VARCHAR, kid VARCHAR, currency VARCHAR);")
            con.execute("CREATE TABLE IF NOT EXISTS staging_erp (voucher_no VARCHAR PRIMARY KEY, account_id VARCHAR, post_date DATE, amount DOUBLE, text VARCHAR, invoice_no VARCHAR, kid_ocr VARCHAR, wbs VARCHAR);")
            con.execute("DELETE FROM staging_bank WHERE account_id = '1925';")
            con.execute("DELETE FROM staging_erp WHERE account_id = '1925';")
            
            for r in okt_bank:
                con.execute("INSERT OR REPLACE INTO staging_bank VALUES (?, ?, ?, ?, ?, ?, ?, ?)", list(r))
                
            for r in okt_erp:
                con.execute("INSERT OR REPLACE INTO staging_erp VALUES (?, ?, ?, ?, ?, ?, ?, ?)", list(r))

    # Export CSV files
    df_bank = pd.DataFrame(okt_bank, columns=["TransaksjonsId", "Konto", "Bokforingsdato", "Belop", "Tekst", "Arkivreferanse", "KID", "Valuta"])
    bank_csv_path = os.path.join(data_dir, "bank_nordea_2026_10.csv")
    df_bank.to_csv(bank_csv_path, sep=";", index=False, encoding="utf-8-sig")

    df_erp = pd.DataFrame(okt_erp, columns=["Bilagsnummer", "Konto", "Bokforingsdato", "Belop", "Tekst", "Fakturanummer", "KID_OCR", "WBS_Prosjekt"])
    erp_csv_path = os.path.join(data_dir, "erp_hovedbok_2026_10.csv")
    df_erp.to_csv(erp_csv_path, sep=";", index=False, encoding="utf-8-sig")

    # Export Balance Reports
    bank_report = {
        "rapport_navn": "Nordea Account Statement Summary",
        "konto": "1925 Nordea Driftskonto NOK (NO93 1503 1234 5678)",
        "periode": "2026-10-01 til 2026-10-31",
        "inngaende_balanse": 5842100.00,
        "totalt_godskrevet": 8120400.00,
        "totalt_belastet": -7641200.00,
        "utgaende_balanse": 6321300.00,
        "kontrollsum_formel": "IB + Innbetalinger + Utbetalinger == UB",
        "status": "VERIFISERT_OK"
    }
    
    erp_report = {
        "rapport_navn": "Hovedbok Kontosaldorapport (Konto 1925)",
        "selskap": "Nordic Engineering Projects AS",
        "periode": "Oktober 2026",
        "inngaende_balanse": 5842100.00,
        "sum_debet": 8120400.00,
        "sum_kredit_ordinar": -7620000.00,
        "ubokfort_bankgebyr_og_rente": -21200.00,
        "utgaende_balanse_etter_spinoff": 6321300.00,
        "status": "AVVENTER_SPINOFF_BILAG"
    }

    bank_json_path = os.path.join(data_dir, "bank_saldo_rapport_2026_10.json")
    erp_json_path = os.path.join(data_dir, "erp_saldo_rapport_2026_10.json")

    with open(bank_json_path, "w", encoding="utf-8") as f:
        json.dump(bank_report, f, indent=2, ensure_ascii=False)

    with open(erp_json_path, "w", encoding="utf-8") as f:
        json.dump(erp_report, f, indent=2, ensure_ascii=False)

    return {
        "bank_rows": len(okt_bank),
        "erp_rows": len(okt_erp),
        "bank_csv": bank_csv_path,
        "erp_csv": erp_csv_path,
        "bank_json": bank_json_path,
        "erp_json": erp_json_path
    }


if __name__ == "__main__":
    res = generate_nordea_dataset("data")
    print(f"Generated {res['bank_rows']} bank transactions and {res['erp_rows']} ERP records.")
