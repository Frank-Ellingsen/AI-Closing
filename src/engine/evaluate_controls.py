"""
CLOSE-AI: Deterministic Financial Controls Engine (DuckDB SQL)
Evaluates 6 core double-entry accounting controls and computes the Close Readiness Index.
Adheres strictly to Section 4 of the system specification.
"""

import os
import json
import duckdb
import pandas as pd

RULE_WEIGHTS = {
    "CTRL-GL-01": 25,  # Trial Balance (Blocker)
    "CTRL-GL-02": 15,  # Weekend/Manual entries
    "CTRL-AP-01": 15,  # Duplicate invoices
    "CTRL-AP-02": 15,  # Uninvoiced Goods Received
    "CTRL-AP-03": 15,  # PO Tolerance Overrun
    "CTRL-PRJ-03": 15  # Missing WBS/Project tags
}

def get_duckdb_connection(data_dir: str = "erp_data_2026_10") -> duckdb.DuckDBPyConnection:
    """
    Initializes an in-memory DuckDB database and registers ERP tables.
    Supports parquet first, falling back to CSV.
    """
    con = duckdb.connect(database=":memory:")
    tables = [
        "divisions", "cost_centers", "vendors", "projects", "wbs_elements",
        "purchase_orders", "po_lines", "vendor_invoices",
        "gl_journal_entries", "gl_journal_lines"
    ]
    for tbl in tables:
        pq_path = os.path.join(data_dir, f"{tbl}.parquet")
        csv_path = os.path.join(data_dir, f"{tbl}.csv")
        if os.path.exists(pq_path):
            con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_parquet('{pq_path.replace(chr(92), '/')}')")
        elif os.path.exists(csv_path):
            con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_path.replace(chr(92), '/')}')")
    return con

def run_close_controls(data_dir: str = "erp_data_2026_10", con: duckdb.DuckDBPyConnection = None) -> dict:
    """
    Runs all deterministic SQL control queries and computes the Close Readiness Index.
    """
    should_close_con = False
    if con is None:
        con = get_duckdb_connection(data_dir)
        should_close_con = True

    queries = {
        "CTRL-GL-01": """
            WITH tb AS (
                SELECT 
                    ROUND(SUM(debit_nok), 2) AS total_debit,
                    ROUND(SUM(credit_nok), 2) AS total_credit,
                    ROUND(ABS(SUM(debit_nok) - SUM(credit_nok)), 2) AS imbalance
                FROM gl_journal_lines
            )
            SELECT 
                'CTRL-GL-01' AS rule_id, 
                'Trial Balance Imbalance' AS rule_name,
                CASE WHEN imbalance = 0.00 THEN 'PASS' ELSE 'FAIL' END AS status,
                'BLOCKER' AS severity, 
                imbalance AS discrepancy_amount_nok,
                CASE WHEN imbalance = 0.00 THEN 0 ELSE 1 END AS affected_count,
                json_object('total_debit', total_debit, 'total_credit', total_credit, 'imbalance', imbalance) AS details_json
            FROM tb;
        """,
        "CTRL-GL-02": """
            WITH flg AS (
                SELECT 
                    e.entry_id, 
                    e.posting_date,
                    e.created_by,
                    ROUND(SUM(l.debit_nok), 2) AS total_nok
                FROM gl_journal_entries e
                JOIN gl_journal_lines l ON e.entry_id = l.entry_id
                WHERE e.source_module = 'MANUAL_GL' 
                  AND EXTRACT(DOW FROM CAST(e.posting_date AS DATE)) IN (0, 6)
                GROUP BY e.entry_id, e.posting_date, e.created_by
            )
            SELECT 
                'CTRL-GL-02' AS rule_id, 
                'Weekend Manual Postings' AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                'HIGH' AS severity, 
                COALESCE(SUM(total_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count,
                json_group_array(json_object('entry_id', entry_id, 'date', CAST(posting_date AS VARCHAR), 'user', created_by, 'amount_nok', total_nok)) AS details_json
            FROM flg;
        """,
        "CTRL-AP-01": """
            WITH dups AS (
                SELECT 
                    a.invoice_id AS invoice_a,
                    b.invoice_id AS invoice_b,
                    a.vendor_name,
                    a.amount_nok,
                    ABS(DATEDIFF('day', CAST(a.invoice_date AS DATE), CAST(b.invoice_date AS DATE))) AS day_difference
                FROM vendor_invoices a
                JOIN vendor_invoices b ON a.vendor_id = b.vendor_id
                 AND a.invoice_id < b.invoice_id
                 AND ABS(a.amount_nok - b.amount_nok) <= 0.01
                 AND ABS(DATEDIFF('day', CAST(a.invoice_date AS DATE), CAST(b.invoice_date AS DATE))) <= 14
            )
            SELECT 
                'CTRL-AP-01' AS rule_id, 
                'Duplicate Vendor Invoices' AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                'HIGH' AS severity, 
                COALESCE(SUM(amount_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count,
                json_group_array(json_object('invoice_pair', invoice_a || ' / ' || invoice_b, 'vendor', vendor_name, 'amount_nok', amount_nok, 'day_gap', day_difference)) AS details_json
            FROM dups;
        """,
        "CTRL-AP-02": """
            WITH uninvoiced AS (
                SELECT 
                    l.po_line_id,
                    l.po_number,
                    l.wbs_code,
                    l.total_amount_nok
                FROM po_lines l
                LEFT JOIN vendor_invoices i ON l.po_number = i.po_number
                WHERE l.delivery_status = 'DELIVERED' 
                  AND l.received_qty > 0
                  AND i.invoice_id IS NULL
            )
            SELECT 
                'CTRL-AP-02' AS rule_id, 
                'Uninvoiced Goods Received' AS rule_name,
                CASE 
                    WHEN COUNT(*) = 0 THEN 'PASS' 
                    WHEN SUM(total_amount_nok) <= 25000 THEN 'PASS'
                    WHEN SUM(total_amount_nok) <= 250000 THEN 'WARNING'
                    ELSE 'FAIL'
                END AS status,
                'HIGH' AS severity, 
                COALESCE(SUM(total_amount_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count,
                json_group_array(json_object('po_line_id', po_line_id, 'po_number', po_number, 'wbs_code', wbs_code, 'unbilled_nok', total_amount_nok)) AS details_json
            FROM uninvoiced;
        """,
        "CTRL-AP-03": """
            WITH po_totals AS (
                SELECT po_number, wbs_code, SUM(total_amount_nok) AS po_amount
                FROM po_lines
                GROUP BY po_number, wbs_code
            ),
            inv_totals AS (
                SELECT invoice_id, po_number, wbs_code, vendor_name, amount_nok AS invoice_amount
                FROM vendor_invoices
                WHERE po_number IS NOT NULL
            ),
            overruns AS (
                SELECT 
                    i.invoice_id,
                    i.po_number,
                    i.vendor_name,
                    i.invoice_amount,
                    p.po_amount,
                    ROUND((i.invoice_amount - p.po_amount), 2) AS variance_nok,
                    ROUND(((i.invoice_amount - p.po_amount) / p.po_amount) * 100, 2) AS variance_pct
                FROM inv_totals i
                JOIN po_totals p ON i.po_number = p.po_number AND i.wbs_code = p.wbs_code
                WHERE i.invoice_amount > p.po_amount
                  AND ((i.invoice_amount - p.po_amount) / p.po_amount) > 0.10
            )
            SELECT 
                'CTRL-AP-03' AS rule_id, 
                'PO Tolerance Overrun (>10%)' AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                'HIGH' AS severity, 
                COALESCE(SUM(variance_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count,
                json_group_array(json_object('invoice_id', invoice_id, 'po_number', po_number, 'vendor', vendor_name, 'variance_nok', variance_nok, 'variance_pct', variance_pct)) AS details_json
            FROM overruns;
        """,
        "CTRL-PRJ-03": """
            WITH untagged AS (
                SELECT 
                    line_id,
                    account_number,
                    debit_nok,
                    cost_center,
                    line_description
                FROM gl_journal_lines
                WHERE account_number BETWEEN '4000' AND '4999'
                  AND (project_id IS NULL OR wbs_code IS NULL)
            )
            SELECT 
                'CTRL-PRJ-03' AS rule_id, 
                'Untagged Project Direct Costs' AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                'HIGH' AS severity, 
                COALESCE(SUM(debit_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count,
                json_group_array(json_object('line_id', line_id, 'account', account_number, 'amount_nok', debit_nok, 'description', line_description)) AS details_json
            FROM untagged;
        """
    }

    results = []
    earned_weight = 0
    total_weight = sum(RULE_WEIGHTS.values())
    has_blocker = False

    for rule_id, sql in queries.items():
        res = con.execute(sql).df().iloc[0].to_dict()
        weight = RULE_WEIGHTS.get(rule_id, 0)
        res["weight"] = weight
        res["discrepancy_amount_nok"] = float(res["discrepancy_amount_nok"])
        res["affected_count"] = int(res["affected_count"])
        
        # Parse details_json safely
        try:
            if isinstance(res.get("details_json"), str):
                res["details"] = json.loads(res["details_json"])
            else:
                res["details"] = res.get("details_json", {})
        except Exception:
            res["details"] = {}

        results.append(res)

        if res["status"] == "PASS":
            earned_weight += weight
        elif res["severity"] == "BLOCKER" and res["status"] == "FAIL":
            has_blocker = True

    readiness_score = round((earned_weight / total_weight) * 100, 1)

    if has_blocker:
        overall_status = "CLOSE BLOCKED"
    elif readiness_score >= 95.0:
        overall_status = "READY FOR SIGN-OFF"
    else:
        overall_status = "ACTION REQUIRED"

    output = {
        "period": "2026-10",
        "entity": "Nordic Engineering Projects AS",
        "readiness_score_pct": readiness_score,
        "overall_status": overall_status,
        "controls_summary": results
    }

    if should_close_con:
        con.close()

    return output

if __name__ == "__main__":
    summary = run_close_controls("erp_data_2026_10")
    print(json.dumps(summary, indent=2))
