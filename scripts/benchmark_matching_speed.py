import time
import random
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.complex_matcher import ComplexReconciliationEngine

console = Console()

def generate_synthetic_benchmark_dataset(num_batches: int = 150, invoices_per_batch: int = 4):
    bank_lines = []
    all_invoices = []
    vendor_names = ["Equinor", "Aker Solutions", "Subsea7", "Vår Energi", "Kongsberg Maritime", "Norsk Hydro"]

    for b in range(1, num_batches + 1):
        batch_id = f"BATCH-{10000 + b}"
        gross_total = 0.0

        for i in range(1, invoices_per_batch + 1):
            inv_id = f"INV-{b:04d}-{i}"
            amount = round(random.uniform(5000.0, 45000.0), 2)
            gross_total += amount
            inv_line = {
                "id": inv_id,
                "po_number": f"PO-{batch_id}-{i}",
                "vendor": random.choice(vendor_names),
                "amount_nok": amount
            }
            all_invoices.append(inv_line)

        fee_deduction = round(gross_total * random.uniform(0.01, 0.025), 2)
        net_bank_settlement = round(gross_total - fee_deduction, 2)

        bank_lines.append({
            "tx_id": f"BANK-TX-{b:05d}",
            "amount_nok": net_bank_settlement,
            "raw_memo": f"NETS*SETTLEMENT REF:{batch_id} INCL PROCESSING FEE",
            "expected_batch": batch_id
        })

    random.shuffle(all_invoices)
    return bank_lines, all_invoices

def run_benchmark():
    console.print(Panel.fit(
        "[bold cyan]CLOSE-AI Throughput & Latency Benchmark[/bold cyan]\n"
        "[italic]Testing Regex Tokenization + Bounded Subset-Sum Combinatorial Solver[/italic]"
    ))

    matcher = ComplexReconciliationEngine(fee_tolerance_pct=0.03, max_date_delta_days=5)

    scales = [
        {"name": "Mid-Market Close", "batches": 30, "items_per_batch": 3},
        {"name": "High-Volume Month-End", "batches": 100, "items_per_batch": 4}
    ]

    summary_table = Table(title="Benchmark Results", header_style="bold blue")
    summary_table.add_column("Scenario", width=22)
    summary_table.add_column("Bank Lines", justify="right", width=12)
    summary_table.add_column("Subledger Pool", justify="right", width=16)
    summary_table.add_column("Matched", justify="right", width=12)
    summary_table.add_column("Total Time", justify="right", width=12)
    summary_table.add_column("Throughput (tx/s)", justify="right", width=18)
    summary_table.add_column("Latency (ms)", justify="right", width=14)

    for test in scales:
        bank_lines, subledger_pool = generate_synthetic_benchmark_dataset(
            num_batches=test["batches"],
            invoices_per_batch=test["items_per_batch"]
        )

        total_tx = len(bank_lines)
        total_subledger = len(subledger_pool)
        matched_count = 0

        start_time = time.perf_counter()
        for bank_tx in bank_lines:
            res = matcher.solve_one_to_many_subset(
                target_amount_nok=bank_tx["amount_nok"],
                raw_memo=bank_tx["raw_memo"],
                candidate_items=subledger_pool,
                max_fee_deduction_nok=3500.00
            )
            if res:
                matched_count += 1

        elapsed = time.perf_counter() - start_time
        throughput = total_tx / elapsed if elapsed > 0 else 0
        latency_ms = (elapsed / total_tx) * 1000 if total_tx > 0 else 0

        summary_table.add_row(
            test["name"],
            f"{total_tx:,}",
            f"{total_subledger:,}",
            f"{matched_count}/{total_tx}",
            f"{elapsed:.2f} s",
            f"{throughput:,.1f}",
            f"{latency_ms:.2f} ms"
        )

    console.print(summary_table)

if __name__ == "__main__":
    run_benchmark()
