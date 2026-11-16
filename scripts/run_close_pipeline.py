import os
import sys
import argparse
import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.complex_matcher import ComplexReconciliationEngine
from src.engine.voucher_generator import VoucherGenerator
from src.engine.aging_analyzer import AgingAnalyzer
from src.governance.audit_logger import AuditLogger
from src.lakehouse.reconciliation_duckdb import ReconciliationDuckDBManager

console = Console()

def run_pipeline():
    console.print(Panel.fit(
        "[bold cyan]CLOSE-AI Financial Close Pipeline Runner v2.0[/bold cyan]\n"
        "[italic]Nordic Engineering Projects AS • Autonomous Pre-Match, Spin-offs & Aging Analysis[/italic]"
    ))

    audit_logger = AuditLogger(log_path="data/audit_logs/audit_trail.jsonl")

    # ---------------------------------------------------------
    # 1. Synthetic ERP & Bank Feed
    # ---------------------------------------------------------
    console.print("\n[bold]1. Ingesting Subledger & Bank Statement Lines...[/bold]")
    bank_lines = [
        {"tx_id": "BANK-2026-10-01", "amount_nok": 89512.50, "raw_memo": "CR-SETTL-ADYEN-88491-OCT26 INCL 2% DEDUCT", "posting_date": "2026-10-31"},
        {"tx_id": "BANK-2026-10-02", "amount_nok": 1724110.00, "raw_memo": "NETTING WIRE ABERDEEN HQ PO-PRJ-001 £125,000", "posting_date": "2026-10-31"},
        {"tx_id": "BANK-2026-10-03", "amount_nok": 670000.00, "raw_memo": "WIRE PO-8809 MANIFOLD DELIVERY PRJ-001.03", "posting_date": "2026-10-31"}
    ]

    open_invoices = [
        {"id": "INV-101", "po_number": "PO-88491-A", "amount_nok": 42000.00, "vendor": "Statoil Equinor", "invoice_date": "2026-10-15"},
        {"id": "INV-102", "po_number": "PO-88491-B", "amount_nok": 28500.00, "vendor": "Aker Solutions", "invoice_date": "2026-10-18"},
        {"id": "INV-103", "po_number": "PO-88491-C", "amount_nok": 11200.00, "vendor": "Subsea 7", "invoice_date": "2026-10-20"},
        {"id": "INV-104", "po_number": "PO-88491-D", "amount_nok": 9850.00, "vendor": "Vår Energi", "invoice_date": "2026-10-22"},
        {"id": "INV-OLD-01", "po_number": "PO-7712", "amount_nok": 85000.00, "vendor": "Kongsberg Yard", "invoice_date": "2026-08-10"},
        {"id": "INV-OLD-02", "po_number": "PO-6411", "amount_nok": 145000.00, "vendor": "Nordic Coatings AS", "invoice_date": "2026-07-04"}
    ]

    console.print(f" [green]✓[/green] Ingested {len(bank_lines)} bank statements and {len(open_invoices)} open subledger items.")

    # ---------------------------------------------------------
    # 2. Pre-Match & Complex 1:M Matching
    # ---------------------------------------------------------
    console.print("\n[bold]2. Executing Stage 1: Pre-Match (AI Close-Style Regex & Combinatorial Solver)...[/bold]")
    matcher = ComplexReconciliationEngine(fee_tolerance_pct=0.03, max_date_delta_days=5)
    proposals = matcher.run_pre_match(bank_transactions=bank_lines, subledger_items=open_invoices)

    rec_table = Table(title="Pre-Match Candidate Clusters", header_style="bold blue")
    rec_table.add_column("Proposal ID", width=18)
    rec_table.add_column("Bank Tx ID", width=14)
    rec_table.add_column("Type", width=10)
    rec_table.add_column("Subledger Lines", width=22)
    rec_table.add_column("Isolated Fee (NOK)", justify="right", width=18)
    rec_table.add_column("Confidence", justify="center", width=12)

    for p in proposals:
        matched_ids = [m["id"] for m in p["matched_subledger_lines"]]
        rec_table.add_row(
            p["proposal_id"],
            p["bank_transaction"]["tx_id"],
            p["match_type"],
            ", ".join(matched_ids),
            f"{p['isolated_fee_nok']:,.2f}",
            f"{p['confidence_score']*100:.0f}%"
        )
    console.print(rec_table)

    # ---------------------------------------------------------
    # 3. Spin-Off Bilag & ERP Export Generation
    # ---------------------------------------------------------
    console.print("\n[bold]3. Generating Spin-Off Vouchers (Bank Fees, Interest, Agio)...[/bold]")
    vouchers = []
    for p in proposals:
        if p["isolated_fee_nok"] > 0:
            spin_off = VoucherGenerator.create_spin_off_voucher(
                voucher_number=f"JV-FEE-{p['bank_transaction']['tx_id']}",
                posting_date="2026-10-31",
                transaction_type="BANK_FEE",
                amount_nok=p["isolated_fee_nok"],
                bank_account="1920",
                contra_account="7770",
                reference_text=f"Autopostert gebyr for {p['proposal_id']}",
                project_id="PRJ-001"
            )
            vouchers.append(spin_off)
            console.print(f" [green]✓[/green] Created balanced Bilag [bold]{spin_off.voucher_number}[/bold] (Debet 7770: {spin_off.lines[0].debet_nok:,.2f} NOK, Kredit 1920: {spin_off.lines[1].kredit_nok:,.2f} NOK).")

    # ---------------------------------------------------------
    # 4. Aging Analysis & Provisioning Report
    # ---------------------------------------------------------
    console.print("\n[bold]4. Running Aging Analysis (Aldersfordelte Åpne Poster)...[/bold]")
    aging_analyzer = AgingAnalyzer(reference_date="2026-10-31")
    aging_buckets = aging_analyzer.calculate_aging_buckets(open_invoices)
    aging_report_md = aging_analyzer.generate_aging_report_markdown(aging_buckets)

    aging_table = Table(title="Aldersfordeling & Tapsavsetning Summary", header_style="bold magenta")
    aging_table.add_column("Kategori", width=14)
    aging_table.add_column("Poster", justify="center", width=8)
    aging_table.add_column("Åpent Beløp (NOK)", justify="right", width=18)
    aging_table.add_column("Avsetningssats", justify="center", width=14)
    aging_table.add_column("Beregnet Avsetning", justify="right", width=18)
    aging_table.add_column("Risiko", width=10)

    for label, b in aging_buckets.items():
        r_color = "green" if b.audit_risk == "LOW" else ("yellow" if b.audit_risk == "MEDIUM" else "red")
        aging_table.add_row(
            label,
            str(b.item_count),
            f"{b.total_amount_nok:,.2f}",
            f"{b.provision_percentage:.0f}%",
            f"{b.estimated_loss_nok:,.2f}",
            f"[{r_color}]{b.audit_risk}[/{r_color}]"
        )
    console.print(aging_table)

    # ---------------------------------------------------------
    # 5. Cryptographic Audit Chain Verification
    # ---------------------------------------------------------
    console.print("\n[bold]5. Appending to Cryptographic Audit Chain & Verifying...[/bold]")
    audit_logger.log_event("PRE_MATCH_BATCH_EVALUATED", "SystemAutomator", {"proposals_count": len(proposals)})
    audit_logger.log_event("SPIN_OFF_VOUCHERS_GENERATED", "VoucherGenerator", {"voucher_count": len(vouchers)})
    audit_logger.log_event("AGING_ANALYSIS_EXECUTED", "AgingAnalyzer", {"total_open_items": len(open_invoices)})

    audit_status = audit_logger.verify_audit_integrity()
    if audit_status["is_valid"]:
        console.print(f" [green]✓[/green] Cryptographic audit chain verified: {audit_status['verified_records']} records intact.")
    else:
        console.print(f" [red]✗[/red] Integrity failure: {audit_status.get('error')}")

    # ---------------------------------------------------------
    # 6. DuckDB Real-Time Reconciliation Store Sync
    # ---------------------------------------------------------
    console.print("\n[bold]6. Syncing DuckDB Analytical Store (reconciled & unreconciled)...[/bold]")
    duckdb_mgr = ReconciliationDuckDBManager()
    duckdb_mgr.populate_from_pipeline_feed(
        bank_lines=bank_lines,
        open_invoices=open_invoices,
        proposals=proposals
    )
    metrics = duckdb_mgr.get_metrics()
    console.print(f" [green]✓[/green] DuckDB updated: [cyan]{metrics['reconciled_count']}[/cyan] reconciled items ({metrics['reconciled_gross_nok']:,.2f} NOK) | [yellow]{metrics['unreconciled_count']}[/yellow] unreconciled open items ({metrics['unreconciled_open_nok']:,.2f} NOK).")
    console.print(f"   • RAG distribution in DuckDB: [red]● {metrics['rag_distribution']['red']} Red[/red] | [yellow]● {metrics['rag_distribution']['amber']} Amber[/yellow] | [green]● {metrics['rag_distribution']['green']} Green[/green]")
    duckdb_mgr.close()

    console.print("\n[bold green]Pipeline executed successfully.[/bold green]\n")

if __name__ == "__main__":
    run_pipeline()
