"""
CLOSE-AI: Synthetic ERP Data Generator
Generates realistic, relational ERP subledgers and General Ledger transactions
for Nordic Engineering Projects AS (Stavanger, Norway) for fiscal period 2026-10.
Includes 5 ground-truth injected anomalies for financial close and audit control testing.
"""

import os
import random
import datetime
import json
import numpy as np
import pandas as pd

def generate_erp_dataset(output_dir: str = "erp_data_2026_10", seed: int = 42) -> dict:
    np.random.seed(seed)
    random.seed(seed)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # 1. Master Data: Divisions & Cost Centers
    # ---------------------------------------------------------
    divisions_data = [
        {"division_code": "DIV-OFF", "division_name": "Offshore Energy & Renewables", "lead": "Håkon Viken"},
        {"division_code": "DIV-INF", "division_name": "Civil Infrastructure & Marine", "lead": "Ingrid Berg"},
        {"division_code": "DIV-SER", "division_name": "Specialized Engineering Consultancy", "lead": "Solveig Lind"},
        {"division_code": "DIV-CORP", "division_name": "Shared Services & Corporate Governance", "lead": "Trond Aas"},
    ]
    df_divisions = pd.DataFrame(divisions_data)

    cost_centers_data = [
        {"cost_center": "CC-1100", "cost_center_name": "Subsea Engineering & Design", "division_code": "DIV-OFF"},
        {"cost_center": "CC-1200", "cost_center_name": "Fabrication Yard & Mobilization", "division_code": "DIV-OFF"},
        {"cost_center": "CC-2100", "cost_center_name": "Civil & Structural Engineering", "division_code": "DIV-INF"},
        {"cost_center": "CC-2200", "cost_center_name": "Site Operations & Assembly", "division_code": "DIV-INF"},
        {"cost_center": "CC-3100", "cost_center_name": "Specialist Consultants & Simulation", "division_code": "DIV-SER"},
        {"cost_center": "CC-9000", "cost_center_name": "Finance & Close Operations", "division_code": "DIV-CORP"},
        {"cost_center": "CC-9100", "cost_center_name": "HQ Admin & Executive Management", "division_code": "DIV-CORP"},
    ]
    df_cost_centers = pd.DataFrame(cost_centers_data)

    # ---------------------------------------------------------
    # 2. Master Data: Vendors
    # ---------------------------------------------------------
    vendors_data = [
        {"vendor_id": "VEND-101", "vendor_name": "Nordic Subsea Fabrication AS", "category": "Fabrication & Yard Services", "currency": "NOK"},
        {"vendor_id": "VEND-102", "vendor_name": "Bergen Marine Logistics AS", "category": "Mobilization & Marine Vessels", "currency": "NOK"},
        {"vendor_id": "VEND-103", "vendor_name": "Stavanger Inspection & NDT AS", "category": "Technical Testing & QA", "currency": "NOK"},
        {"vendor_id": "VEND-104", "vendor_name": "Fjord Steel & Piping Supplies BV", "category": "Raw Materials", "currency": "EUR"},
        {"vendor_id": "VEND-105", "vendor_name": "Equinor Engineering Advisory", "category": "Consulting & Feasibility", "currency": "NOK"},
        {"vendor_id": "VEND-106", "vendor_name": "Aker Yard Support DA", "category": "Subcontractor Labor", "currency": "NOK"},
        {"vendor_id": "VEND-107", "vendor_name": "Global CAD & Simulation Systems Inc", "category": "Software & Cloud Services", "currency": "USD"},
    ]
    df_vendors = pd.DataFrame(vendors_data)

    # ---------------------------------------------------------
    # 3. Master Data: Projects & WBS Elements
    # ---------------------------------------------------------
    projects_data = [
        {
            "project_id": "PRJ-2026-001",
            "project_name": "Troll Wind Substation Modular Frame",
            "customer_id": "CUST-EQN",
            "division_code": "DIV-OFF",
            "project_manager": "Frank Ellingsen",
            "contract_type": "FIXED_PRICE",
            "total_contract_value_nok": 18500000.0,
            "start_date": "2026-01-15",
            "planned_end_date": "2026-12-20",
            "status": "ACTIVE"
        },
        {
            "project_id": "PRJ-2026-002",
            "project_name": "Sognefjord Crossing Ventilation Shafts",
            "customer_id": "CUST-STAT",
            "division_code": "DIV-INF",
            "project_manager": "Kari Nordmann",
            "contract_type": "FIXED_PRICE",
            "total_contract_value_nok": 9200000.0,
            "start_date": "2026-03-01",
            "planned_end_date": "2026-11-30",
            "status": "ACTIVE"
        },
        {
            "project_id": "PRJ-2026-003",
            "project_name": "Hydrogen Pipeline FEA Simulation",
            "customer_id": "CUST-HYD",
            "division_code": "DIV-SER",
            "project_manager": "Erik Sørli",
            "contract_type": "TIME_AND_MATERIALS",
            "total_contract_value_nok": 3400000.0,
            "start_date": "2026-06-01",
            "planned_end_date": "2027-02-28",
            "status": "ACTIVE"
        },
        {
            "project_id": "PRJ-2026-004",
            "project_name": "Modular Yard Crane Electrification",
            "customer_id": "INTERNAL",
            "division_code": "DIV-OFF",
            "project_manager": "Lars Hovland",
            "contract_type": "INTERNAL_CAPEX",
            "total_contract_value_nok": 2100000.0,
            "start_date": "2026-08-01",
            "planned_end_date": "2026-12-31",
            "status": "ACTIVE"
        },
    ]
    df_projects = pd.DataFrame(projects_data)

    wbs_data = [
        {"wbs_code": "PRJ-2026-001.01.ENG", "project_id": "PRJ-2026-001", "phase_name": "Engineering & Design", "cost_center": "CC-1100", "allocated_budget_nok": 3500000.0, "forecast_cost_nok": 3400000.0, "actual_progress_pct": 95.0},
        {"wbs_code": "PRJ-2026-001.02.PROC", "project_id": "PRJ-2026-001", "phase_name": "Procurement & Steel", "cost_center": "CC-1100", "allocated_budget_nok": 5000000.0, "forecast_cost_nok": 5100000.0, "actual_progress_pct": 100.0},
        {"wbs_code": "PRJ-2026-001.03.FAB", "project_id": "PRJ-2026-001", "phase_name": "Yard Fabrication", "cost_center": "CC-1200", "allocated_budget_nok": 6500000.0, "forecast_cost_nok": 6800000.0, "actual_progress_pct": 80.0},
        {"wbs_code": "PRJ-2026-001.04.INST", "project_id": "PRJ-2026-001", "phase_name": "Offshore Mobilization", "cost_center": "CC-1200", "allocated_budget_nok": 3500000.0, "forecast_cost_nok": 3600000.0, "actual_progress_pct": 30.0},
        {"wbs_code": "PRJ-2026-002.01.CIVIL", "project_id": "PRJ-2026-002", "phase_name": "Civil Excavation", "cost_center": "CC-2100", "allocated_budget_nok": 4200000.0, "forecast_cost_nok": 4100000.0, "actual_progress_pct": 85.0},
        {"wbs_code": "PRJ-2026-002.02.VENT", "project_id": "PRJ-2026-002", "phase_name": "Ventilation Ducts", "cost_center": "CC-2200", "allocated_budget_nok": 5000000.0, "forecast_cost_nok": 5300000.0, "actual_progress_pct": 60.0},
        {"wbs_code": "PRJ-2026-003.01.FEA", "project_id": "PRJ-2026-003", "phase_name": "Finite Element Analysis", "cost_center": "CC-3100", "allocated_budget_nok": 3400000.0, "forecast_cost_nok": 3200000.0, "actual_progress_pct": 70.0},
        {"wbs_code": "PRJ-2026-004.01.CAPEX", "project_id": "PRJ-2026-004", "phase_name": "Crane Modernization", "cost_center": "CC-1200", "allocated_budget_nok": 2100000.0, "forecast_cost_nok": 2050000.0, "actual_progress_pct": 75.0},
    ]
    df_wbs = pd.DataFrame(wbs_data)

    # ---------------------------------------------------------
    # 4. Purchase Orders & PO Lines (Procurement Subledger)
    # ---------------------------------------------------------
    po_headers = []
    po_lines = []

    # Dedicated PO-2026-8809 specifically assigned to PRJ-2026-001.03.FAB and VEND-101 for the tolerance overrun scenario
    fixed_po_target = "PO-2026-8809"
    
    for i in range(1, 26):
        po_num = f"PO-2026-{8800 + i}"
        if po_num == fixed_po_target:
            vendor = next(v for v in vendors_data if v["vendor_id"] == "VEND-101")
            prj = next(p for p in projects_data if p["project_id"] == "PRJ-2026-001")
            selected_wbs = next(w for w in wbs_data if w["wbs_code"] == "PRJ-2026-001.03.FAB")
            currency = "NOK"
            order_date = datetime.date(2026, 9, 28)
        else:
            vendor = random.choice(vendors_data)
            prj = random.choice(projects_data)
            matching_wbs = [w for w in wbs_data if w["project_id"] == prj["project_id"]]
            selected_wbs = random.choice(matching_wbs) if matching_wbs else wbs_data[0]
            order_date = datetime.date(2026, 9, 15) + datetime.timedelta(days=random.randint(1, 25))
            currency = vendor["currency"]

        po_headers.append({
            "po_number": po_num,
            "vendor_id": vendor["vendor_id"],
            "project_id": prj["project_id"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "status": "PARTIALLY_RECEIVED",
            "currency": currency
        })

        if po_num == fixed_po_target:
            # Authorized commitment: 670,000 NOK exactly
            po_lines.append({
                "po_line_id": f"{po_num}-1",
                "po_number": po_num,
                "wbs_code": selected_wbs["wbs_code"],
                "line_description": "Fabrication of subsea manifold frame & structural supports",
                "ordered_qty": 1.0,
                "received_qty": 1.0,
                "unit_price": 670000.0,
                "total_amount_nok": 670000.0,
                "delivery_status": "DELIVERED"
            })
        else:
            # 1 to 2 lines per PO
            for line_idx in range(1, random.randint(2, 3)):
                line_id = f"{po_num}-{line_idx}"
                qty = float(random.randint(1, 15))
                unit_price = float(random.choice([8000.0, 15000.0, 28000.0, 65000.0, 110000.0]))
                total_nok = qty * unit_price
                po_lines.append({
                    "po_line_id": line_id,
                    "po_number": po_num,
                    "wbs_code": selected_wbs["wbs_code"],
                    "line_description": f"Deliverable services/materials for {selected_wbs['phase_name']}",
                    "ordered_qty": qty,
                    "received_qty": qty,
                    "unit_price": unit_price,
                    "total_amount_nok": total_nok,
                    "delivery_status": "DELIVERED"
                })

    df_pos = pd.DataFrame(po_headers)
    df_po_lines = pd.DataFrame(po_lines)

    # ---------------------------------------------------------
    # 5. Vendor Invoices (AP Subledger)
    # ---------------------------------------------------------
    invoices = []
    inv_counter = 99100

    # Build invoices corresponding to PO lines
    for idx, line in df_po_lines.iterrows():
        inv_counter += 1
        inv_id = f"INV-VEND-{inv_counter}"
        po_num = line["po_number"]
        po_hdr = df_pos[df_pos["po_number"] == po_num].iloc[0]
        
        o_date = datetime.date.fromisoformat(po_hdr["order_date"])
        inv_date = o_date + datetime.timedelta(days=random.randint(10, 20))
        # Ensure October 2026
        if inv_date > datetime.date(2026, 10, 31):
            inv_date = datetime.date(2026, 10, 28)
        due_date = inv_date + datetime.timedelta(days=30)
        
        vendor_info = next(v for v in vendors_data if v["vendor_id"] == po_hdr["vendor_id"])
        
        invoices.append({
            "invoice_id": inv_id,
            "vendor_id": po_hdr["vendor_id"],
            "vendor_name": vendor_info["vendor_name"],
            "po_number": po_num,
            "project_id": po_hdr["project_id"],
            "wbs_code": line["wbs_code"],
            "invoice_date": inv_date.strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "currency": po_hdr["currency"],
            "amount_nok": float(line["total_amount_nok"]),
            "approval_status": "APPROVED",
            "matched_to_po": True,
            "gr_ir_cleared": True
        })

    df_invoices = pd.DataFrame(invoices)

    # ---------------------------------------------------------
    # INJECT GROUND-TRUTH ANOMALIES
    # ---------------------------------------------------------
    
    # ANOMALY 1: Duplicate Vendor Invoice (CTRL-AP-01)
    # Pick invoice at index 3, duplicate with same vendor, amount, within 2 days gap
    dup_source = df_invoices.iloc[3].to_dict()
    dup_inv = dup_source.copy()
    dup_inv["invoice_id"] = "INV-VEND-99991-DUP"
    d_date = datetime.date.fromisoformat(dup_source["invoice_date"]) + datetime.timedelta(days=2)
    dup_inv["invoice_date"] = d_date.strftime("%Y-%m-%d")
    df_invoices = pd.concat([df_invoices, pd.DataFrame([dup_inv])], ignore_index=True)

    # ANOMALY 2: Tolerance Overrun (+22.4%) on Subsea PO-2026-8809 (CTRL-AP-03)
    # Vendor invoiced 820,000 NOK against authorized 670,000 NOK (+150k NOK overrun = +22.39%)
    overrun_idx = df_invoices[df_invoices["po_number"] == fixed_po_target].index
    if len(overrun_idx) > 0:
        o_idx = overrun_idx[0]
        df_invoices.loc[o_idx, "invoice_id"] = "INV-VEND-99214"
        df_invoices.loc[o_idx, "amount_nok"] = 820000.0  # 670,000 * 1.22388
        df_invoices.loc[o_idx, "approval_status"] = "PENDING_PM_APPROVAL"
        df_invoices.loc[o_idx, "matched_to_po"] = False
        df_invoices.loc[o_idx, "gr_ir_cleared"] = False

    # ANOMALY 3: Uninvoiced Delivery (CTRL-AP-02)
    # PO shows received_qty > 0 on WBS PRJ-2026-001.03.FAB, but vendor invoice is withheld
    # Find a po_line to omit from invoices
    uninvoiced_po_num = "PO-2026-8812"
    df_invoices = df_invoices[df_invoices["po_number"] != uninvoiced_po_num].reset_index(drop=True)

    # ---------------------------------------------------------
    # 6. General Ledger (gl_journal_entries & gl_journal_lines)
    # ---------------------------------------------------------
    gl_entries = []
    gl_lines = []
    entry_counter = 1000

    def add_journal_entry(date_str, period, module, user, lines_data):
        nonlocal entry_counter
        entry_counter += 1
        entry_id = f"JV-2026-10-{entry_counter}"

        gl_entries.append({
            "entry_id": entry_id,
            "posting_date": date_str,
            "period_id": period,
            "source_module": module,
            "created_by": user,
            "approval_status": "POSTED"
        })

        for l_idx, (acct, dr, cr, cc, prj, wbs, desc) in enumerate(lines_data, 1):
            gl_lines.append({
                "line_id": f"{entry_id}-{l_idx}",
                "entry_id": entry_id,
                "account_number": str(acct),
                "debit_nok": float(dr),
                "credit_nok": float(cr),
                "cost_center": cc,
                "project_id": prj,
                "wbs_code": wbs,
                "line_description": desc
            })

    # Normal AP postings for approved invoices
    for _, inv in df_invoices.iterrows():
        # Do not post unapproved or disputed invoice directly to AP GL lines
        if inv["approval_status"] == "APPROVED":
            amt = inv["amount_nok"]
            inv_date = inv["invoice_date"]
            add_journal_entry(
                inv_date, "2026-10", "AP", "sys_ap_batch",
                [
                    ("4100", amt, 0.0, "CC-1200", inv["project_id"], inv["wbs_code"], f"Subcontractor cost: {inv['invoice_id']}"),
                    ("2400", 0.0, amt, "CC-9000", None, None, f"Trade liability: {inv['invoice_id']}")
                ]
            )

    # Standard Monthly Payroll Entry (Engineering salaries & 14.1% AGA tax)
    add_journal_entry(
        "2026-10-25", "2026-10", "PAYROLL", "sys_payroll_auto",
        [
            ("5000", 1850000.0, 0.0, "CC-1100", None, None, "Engineering monthly salaries"),
            ("5400", 260850.0, 0.0, "CC-9000", None, None, "Employer AGA tax (14.1%)"),
            ("2600", 0.0, 1850000.0, "CC-9000", None, None, "Net salaries payable"),
            ("2770", 0.0, 260850.0, "CC-9000", None, None, "Statutory tax clearing")
        ]
    )

    # Standard Revenue Milestones
    add_journal_entry(
        "2026-10-28", "2026-10", "AR", "sys_billing",
        [
            ("1510", 3500000.0, 0.0, "CC-9000", "PRJ-2026-001", None, "Milestone 3 Billing - Troll Wind"),
            ("3010", 0.0, 3500000.0, "CC-1100", "PRJ-2026-001", "PRJ-2026-001.03.FAB", "Earned milestone revenue")
        ]
    )

    # ANOMALY 4: Off-Hours Manual Entry without WBS/Project Tagging (CTRL-GL-02 & CTRL-PRJ-03)
    # Sunday night manual posting to direct project cost account 4100
    sunday_date = "2026-10-25"  # 2026-10-25 was a Sunday
    add_journal_entry(
        sunday_date, "2026-10", "MANUAL_GL", "usr_external_temp",
        [
            ("4100", 145000.0, 0.0, "CC-1200", None, None, "Urgent weekend adjustment yard materials"),
            ("2440", 0.0, 145000.0, "CC-9000", None, None, "Accrued yard expenses")
        ]
    )

    # ANOMALY 5: Unbalanced Trial Balance Entry (CTRL-GL-01 Blocker)
    # 15,000 NOK discrepancy in JV-2026-10-1028
    add_journal_entry(
        "2026-10-30", "2026-10", "MANUAL_GL", "usr_junior_acct",
        [
            ("6800", 35000.0, 0.0, "CC-9100", None, None, "Travel and client site mobilization"),
            ("1910", 0.0, 20000.0, "CC-9000", None, None, "Direct bank withdrawal")  # 15k delta!
        ]
    )

    df_gl_entries = pd.DataFrame(gl_entries)
    df_gl_lines = pd.DataFrame(gl_lines)

    # ---------------------------------------------------------
    # 7. Export Tables to CSV and Parquet
    # ---------------------------------------------------------
    tables = {
        "divisions": df_divisions,
        "cost_centers": df_cost_centers,
        "vendors": df_vendors,
        "projects": df_projects,
        "wbs_elements": df_wbs,
        "purchase_orders": df_pos,
        "po_lines": df_po_lines,
        "vendor_invoices": df_invoices,
        "gl_journal_entries": df_gl_entries,
        "gl_journal_lines": df_gl_lines
    }

    for name, df in tables.items():
        csv_file = os.path.join(output_dir, f"{name}.csv")
        pq_file = os.path.join(output_dir, f"{name}.parquet")
        df.to_csv(csv_file, index=False)
        try:
            df.to_parquet(pq_file, index=False)
        except Exception as e:
            print(f"Warning: could not write parquet for {name}: {e}")

    summary = {
        "output_dir": output_dir,
        "gl_entries_count": len(df_gl_entries),
        "gl_lines_count": len(df_gl_lines),
        "invoices_count": len(df_invoices),
        "po_count": len(df_pos),
        "po_lines_count": len(df_po_lines),
        "projects_count": len(df_projects)
    }
    return summary

if __name__ == "__main__":
    res = generate_erp_dataset("erp_data_2026_10")
    print(f"Generated ERP dataset in '{res['output_dir']}': {res['gl_lines_count']} GL lines across {res['gl_entries_count']} entries.")
