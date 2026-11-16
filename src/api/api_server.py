"""
CLOSE-AI & Financial Close Control Room - FastAPI & DuckDB Backend Server
Kobler web-grensesnittene (index.html, index_carbon.html, index_nordea_simulation.html)
direkte til de lokale DuckDB-databasene og Lakehouse-motoren.
"""

import os
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from pydantic import BaseModel
import duckdb
import pandas as pd
from contextlib import contextmanager

@contextmanager
def get_db(db_path: str, read_only: bool = False):
    con = duckdb.connect(db_path, read_only=read_only)
    try:
        yield con
    finally:
        try:
            con.close()
        except Exception:
            pass


app = FastAPI(
    title="CLOSE-AI & Financial Close Control Room API",
    description="Backend for automatisert avstemming, DuckDB-persistens, spin-off bilagsgenerering og 4-veis balansekontroll.",
    version="3.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MAIN_DB = os.path.join(DATA_DIR, "reconciliation.duckdb")
RECONCILED_DB = os.path.join(DATA_DIR, "reconciled_transactions.duckdb")
UNRECONCILED_DB = os.path.join(DATA_DIR, "unreconciled_transactions.duckdb")
AUDIT_DIR = os.path.join(DATA_DIR, "audit_logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)


class AccountCreate(BaseModel):
    account_id: str
    account_name: str
    bank_iban: str
    swift_bic: Optional[str] = "NDEADKKK"
    currency: Optional[str] = "NOK"
    ib_bank: float = 0.0
    ib_erp: float = 0.0
    rounding_tolerance: float = 0.50


class MatchCommit(BaseModel):
    match_id: str
    account_id: str
    bank_tx_id: Optional[str] = None
    erp_voucher_no: Optional[str] = None
    amount: float
    rule_code: str
    difference: float = 0.0
    notes: Optional[str] = None


class SpinoffVoucher(BaseModel):
    voucher_id: str
    account_id: str
    voucher_type: str
    debit_account: str
    credit_account: str
    amount: float
    description: str
    period: str


@app.get("/")
def read_root():
    return {
        "system": "CLOSE-AI Control Room API",
        "status": "operational",
        "documentation": "/docs",
        "ui_endpoints": {
            "control_room_aurora": "/ui/aurora",
            "control_room_carbon": "/ui/carbon",
            "nordea_simulation": "/ui/nordea"
        }
    }


@app.get("/ui/aurora")
def serve_aurora_ui():
    p = os.path.join(PROJECT_ROOT, "index.html")
    if os.path.exists(p):
        return FileResponse(p, media_type="text/html")
    raise HTTPException(status_code=404, detail="index.html not found")


@app.get("/ui/carbon")
def serve_carbon_ui():
    p = os.path.join(PROJECT_ROOT, "index_carbon.html")
    if os.path.exists(p):
        return FileResponse(p, media_type="text/html")
    raise HTTPException(status_code=404, detail="index_carbon.html not found")


@app.get("/ui/nordea")
def serve_nordea_ui():
    p = os.path.join(PROJECT_ROOT, "index_nordea_simulation.html")
    if os.path.exists(p):
        return FileResponse(p, media_type="text/html")
    raise HTTPException(status_code=404, detail="index_nordea_simulation.html not found")


@app.get("/api/status")
def get_system_status():
    """Henter nøkkeltall og status på tvers av databasene"""
    try:
        with get_db(MAIN_DB) as con:
            acc_count = con.execute("SELECT count(*) FROM accounts").fetchone()[0]
        with get_db(RECONCILED_DB) as con:
            rec_count = con.execute("SELECT count(*) FROM reconciled").fetchone()[0]
            rec_sum = con.execute("SELECT coalesce(sum(amount), 0) FROM reconciled").fetchone()[0]
        with get_db(UNRECONCILED_DB) as con:
            open_bank_count = con.execute("SELECT count(*) FROM open_bank_items").fetchone()[0]
            open_erp_count = con.execute("SELECT count(*) FROM open_erp_items").fetchone()[0]
    except Exception as e:
        return {"status": "initializing", "error": str(e)}

    total_items = rec_count + open_bank_count + open_erp_count
    return {
        "status": "online",
        "accounts_count": acc_count,
        "reconciled_matches": rec_count,
        "reconciled_volume_nok": rec_sum,
        "open_bank_items": open_bank_count,
        "open_erp_items": open_erp_count,
        "close_readiness_pct": round((rec_count / (total_items or 1)) * 100, 1)
    }


@app.get("/api/accounts")
def list_accounts():
    """Henter alle konfigurerte avstemmingskonti"""
    with get_db(MAIN_DB) as con:
        df = con.execute("SELECT * FROM accounts").df()
    return df.to_dict(orient="records")


@app.post("/api/accounts")
def create_account(account: AccountCreate):
    with get_db(MAIN_DB) as con:
        con.execute("""
            INSERT OR REPLACE INTO accounts 
            (account_id, account_name, bank_iban, swift_bic, currency, ib_bank, ib_erp, rounding_tolerance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [account.account_id, account.account_name, account.bank_iban, account.swift_bic,
              account.currency, account.ib_bank, account.ib_erp, account.rounding_tolerance])
    return {"status": "created", "account": account.account_id}


@app.get("/api/reconciliation/balance-control")
def get_balance_control(account_id: str = "1925", period: str = "2026-10"):
    """Klassisk 4-delt AI Close Balancer revisjonsmatrise med matematisk bro"""
    with get_db(MAIN_DB) as con:
        acc = con.execute("SELECT * FROM accounts WHERE account_id = ?", [account_id]).fetchone()
    
    if not acc:
        raise HTTPException(status_code=404, detail=f"Konto {account_id} ikke funnet")

    ib_bank = acc[5]
    ib_erp = acc[6]

    with get_db(UNRECONCILED_DB) as con:
        box1_sum = con.execute("""
            SELECT coalesce(sum(amount), 0) FROM open_bank_items 
            WHERE account_id = ? AND amount > 0
        """, [account_id]).fetchone()[0]

        box2_sum = con.execute("""
            SELECT coalesce(sum(abs(amount)), 0) FROM open_bank_items 
            WHERE account_id = ? AND amount < 0
        """, [account_id]).fetchone()[0]

        box3_sum = con.execute("""
            SELECT coalesce(sum(amount), 0) FROM open_erp_items 
            WHERE account_id = ? AND amount > 0
        """, [account_id]).fetchone()[0]

        box4_sum = con.execute("""
            SELECT coalesce(sum(abs(amount)), 0) FROM open_erp_items 
            WHERE account_id = ? AND amount < 0
        """, [account_id]).fetchone()[0]

    with get_db(MAIN_DB) as con:
        bank_moves = con.execute("SELECT coalesce(sum(amount), 0) FROM staging_bank WHERE account_id = ?", [account_id]).fetchone()[0]
        erp_moves = con.execute("SELECT coalesce(sum(amount), 0) FROM staging_erp WHERE account_id = ?", [account_id]).fetchone()[0]

    ub_bank = ib_bank + bank_moves
    ub_erp = ib_erp + erp_moves

    adjusted_erp = ub_erp + box1_sum - box2_sum
    adjusted_bank = ub_bank + box3_sum - box4_sum
    delta = round(adjusted_erp - adjusted_bank, 2)

    return {
        "account_id": account_id,
        "period": period,
        "bank_balance": {"ib": ib_bank, "period_movement": bank_moves, "ub": ub_bank},
        "erp_balance": {"ib": ib_erp, "period_movement": erp_moves, "ub": ub_erp},
        "four_way_matrix": {
            "box1_credit_bank_not_debit_erp": round(box1_sum, 2),
            "box2_debit_bank_not_credit_erp": round(box2_sum, 2),
            "box3_debit_erp_not_credit_bank": round(box3_sum, 2),
            "box4_credit_erp_not_debit_bank": round(box4_sum, 2)
        },
        "adjusted_erp": round(adjusted_erp, 2),
        "adjusted_bank": round(adjusted_bank, 2),
        "delta": delta,
        "status": "I BALANSE" if abs(delta) <= 0.01 else f"UBALANSE ({delta} NOK)"
    }


@app.get("/api/reconciliation/open-items")
def get_open_items(account_id: str = "1925"):
    with get_db(UNRECONCILED_DB) as con:
        bank_items = con.execute("SELECT * FROM open_bank_items WHERE account_id = ?", [account_id]).df()
        erp_items = con.execute("SELECT * FROM open_erp_items WHERE account_id = ?", [account_id]).df()
    
    return {
        "bank_items": bank_items.to_dict(orient="records"),
        "erp_items": erp_items.to_dict(orient="records")
    }


@app.post("/api/reconciliation/match")
def commit_match(match: MatchCommit):
    with get_db(RECONCILED_DB) as con:
        con.execute("""
            INSERT OR REPLACE INTO reconciled (match_id, account_id, bank_tx_id, erp_voucher_no, amount, rule_applied, difference, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [match.match_id, match.account_id, match.bank_tx_id, match.erp_voucher_no,
              match.amount, match.rule_code, match.difference, match.notes])
    
    with get_db(UNRECONCILED_DB) as con:
        if match.bank_tx_id:
            con.execute("DELETE FROM open_bank_items WHERE tx_id = ?", [match.bank_tx_id])
        if match.erp_voucher_no:
            con.execute("DELETE FROM open_erp_items WHERE voucher_no = ?", [match.erp_voucher_no])

    return {"status": "matched", "match_id": match.match_id}


@app.post("/api/reconciliation/unmatch")
def unmatch(match_id: str = Form(...)):
    with get_db(RECONCILED_DB) as con:
        row = con.execute("SELECT * FROM reconciled WHERE match_id = ?", [match_id]).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Match ID ikke funnet")
        con.execute("DELETE FROM reconciled WHERE match_id = ?", [match_id])

    bank_tx_id = row[2]
    erp_voucher = row[3]
    amt = row[4]
    acc_id = row[1]

    with get_db(UNRECONCILED_DB) as con:
        if bank_tx_id:
            con.execute("""
                INSERT OR IGNORE INTO open_bank_items (tx_id, account_id, tx_date, amount, text)
                VALUES (?, ?, CURRENT_DATE, ?, 'Gjenopprettet etter unmatch')
            """, [bank_tx_id, acc_id, amt])
        if erp_voucher:
            con.execute("""
                INSERT OR IGNORE INTO open_erp_items (voucher_no, account_id, post_date, amount, text)
                VALUES (?, ?, CURRENT_DATE, ?, 'Gjenopprettet etter unmatch')
            """, [erp_voucher, acc_id, amt])

    return {"status": "unmatched", "match_id": match_id}


@app.get("/api/spinoff/proposals")
def get_spinoff_proposals(account_id: str = "1925"):
    with get_db(UNRECONCILED_DB) as con:
        df = con.execute("""
            SELECT tx_id, tx_date, amount, text FROM open_bank_items
            WHERE account_id = ? AND (
                lower(text) LIKE '%gebyr%' OR 
                lower(text) LIKE '%rente%' OR 
                lower(text) LIKE '%fee%' OR 
                lower(text) LIKE '%interest%'
            )
        """, [account_id]).df()

    proposals = []
    for _, row in df.iterrows():
        is_fee = "gebyr" in row['text'].lower() or "fee" in row['text'].lower()
        is_int = "rente" in row['text'].lower() or "interest" in row['text'].lower()
        debit_acc = "7770" if is_fee else ("8150" if is_int else "7790")
        desc = "Nordea bank- og transaksjonsgebyr" if is_fee else "Nordea renter lån/kassekreditt"

        proposals.append({
            "voucher_id": f"VOUCH-{row['tx_id']}",
            "bank_tx_id": row['tx_id'],
            "account_id": account_id,
            "amount": abs(row['amount']),
            "debit_account": debit_acc,
            "debit_name": "Bank- og kortgebyrer" if is_fee else "Annen rentekostnad",
            "credit_account": account_id,
            "credit_name": "Nordea Driftskonto",
            "description": f"{desc} ({row['tx_date']})",
            "confidence": 0.99
        })

    return proposals


@app.post("/api/spinoff/commit")
def commit_spinoff(voucher: SpinoffVoucher, bank_tx_id: str = Query(...)):
    with get_db(RECONCILED_DB) as con:
        con.execute("""
            INSERT OR REPLACE INTO reconciled (match_id, account_id, bank_tx_id, erp_voucher_no, amount, rule_applied, notes)
            VALUES (?, ?, ?, ?, ?, 'R-SPINOFF', ?)
        """, [voucher.voucher_id, voucher.account_id, bank_tx_id, voucher.voucher_id, -voucher.amount, voucher.description])

    with get_db(UNRECONCILED_DB) as con:
        con.execute("DELETE FROM open_bank_items WHERE tx_id = ?", [bank_tx_id])

    with get_db(MAIN_DB) as con:
        con.execute("""
            INSERT OR REPLACE INTO staging_erp (voucher_no, account_id, post_date, amount, text, invoice_no)
            VALUES (?, ?, CURRENT_DATE, ?, ?, 'AUTO-SPINOFF')
        """, [voucher.voucher_id, voucher.account_id, -voucher.amount, voucher.description])

    return {"status": "posted", "voucher_id": voucher.voucher_id}


@app.get("/api/export/erp-journal")
def export_erp_journal(account_id: str = "1925"):
    with get_db(RECONCILED_DB) as con:
        df = con.execute("""
            SELECT match_id AS Bilagsnr, CURRENT_DATE AS Dato, 
                   '7770' AS DebetKonto, account_id AS KreditKonto, 
                   abs(amount) AS Belop, notes AS Tekst
            FROM reconciled
            WHERE rule_applied = 'R-SPINOFF' AND account_id = ?
        """, [account_id]).df()
    
    csv_str = df.to_csv(index=False, sep=";")
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=erp_bilag_{account_id}.csv"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.api_server:app", host="127.0.0.1", port=8000, reload=True)
