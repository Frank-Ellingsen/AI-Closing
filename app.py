"""
CLOSE-AI: Master Enterprise Financial Close, Adra Balancer & Audit Control Room Cockpit
Designed for Nordic Engineering Projects AS (Stavanger / Oslo, Norway)
Executive Controller: Frank Ellingsen (Lead Project Controller)
Adheres to Edward Tufte's Data-Ink ratio principles & statutory audit standards (ISA 240 / 315 / 500 & SAF-T).
Connects directly to DuckDB Analytical Lakehouse and SQLite/DuckDB transactional state.
"""

import os
import json
import datetime
import hashlib
import pandas as pd
import numpy as np
import duckdb
import streamlit as st

from src.engine.evaluate_controls import run_close_controls, get_duckdb_connection, RULE_WEIGHTS
from src.ml.anomaly_detector import run_anomaly_detection
from src.agent.investigator import CloseInvestigatorAgent
from src.audit.audit_manager import AuditManager
from src.data_generator.generate_erp_data import generate_erp_dataset
from src.data_generator.nordea_generator import generate_nordea_dataset
from setup_duckdb import setup_databases

# ---------------------------------------------------------
# Page Configuration & Styling (Tufte Data-Ink Principles)
# ---------------------------------------------------------
st.set_page_config(
    page_title="CLOSE-AI | Master Financial Close Control Room",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Density Financial Terminal CSS
st.markdown("""
<style>
    /* Remove unnecessary margins and shadows */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Clean metric cards without drop shadows */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Tufte table styling: clean, right-aligned numbers */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 0.9rem;
    }
    th {
        border-bottom: 2px solid #2b2d42;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
        color: #1a1a1a;
    }
    td {
        border-bottom: 1px solid #e5e5e5;
        padding: 6px 12px;
    }
    .num-cell {
        text-align: right;
        font-variant-numeric: tabular-nums;
    }
    
    /* Status pills */
    .status-pass {
        color: #2b9348;
        font-weight: 600;
    }
    .status-fail {
        color: #d90429;
        font-weight: 600;
    }
    .status-warn {
        color: #f77f00;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

ERP_DIR = "erp_data_2026_10"
DUCKDB_DIR = "data"
MAIN_DB = os.path.join(DUCKDB_DIR, "reconciliation.duckdb")
RECON_DB = os.path.join(DUCKDB_DIR, "reconciled_transactions.duckdb")
UNRECON_DB = os.path.join(DUCKDB_DIR, "unreconciled_transactions.duckdb")
WORKFLOW_STATE_FILE = "workflow_state_2026_10.json"

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
def load_workflow_state():
    if os.path.exists(WORKFLOW_STATE_FILE):
        try:
            with open(WORKFLOW_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "resolved_anomalies": [],
        "disputed_items": [],
        "posted_journals": [],
        "period_locked": False
    }

def persist_workflow_state():
    state = {
        "resolved_anomalies": list(st.session_state.resolved_anomalies),
        "disputed_items": list(st.session_state.disputed_items),
        "posted_journals": st.session_state.posted_journals,
        "period_locked": st.session_state.period_locked
    }
    with open(WORKFLOW_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

initial_state = load_workflow_state()

if "resolved_anomalies" not in st.session_state:
    st.session_state.resolved_anomalies = set(initial_state.get("resolved_anomalies", []))
if "disputed_items" not in st.session_state:
    st.session_state.disputed_items = set(initial_state.get("disputed_items", []))
if "posted_journals" not in st.session_state:
    st.session_state.posted_journals = initial_state.get("posted_journals", [])
if "period_locked" not in st.session_state:
    st.session_state.period_locked = initial_state.get("period_locked", False)
if "audit_mgr" not in st.session_state:
    st.session_state.audit_mgr = AuditManager(base_dir="data/audit_logs")

# Ensure base datasets exist
if not os.path.exists(ERP_DIR):
    generate_erp_dataset(ERP_DIR)
if not os.path.exists(MAIN_DB):
    setup_databases(DUCKDB_DIR)
    generate_nordea_dataset(DUCKDB_DIR)

# ---------------------------------------------------------
# Sidebar: Control Room Controls & Entity Metadata
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚖️ CLOSE-AI")
    st.caption("Autonomous Financial Close & Control Room Suite")
    st.markdown("---")
    
    st.markdown("**Entity:** Nordic Engineering Projects AS")
    st.markdown("**Org Nr:** `NO 984 521 890 MVA`")
    st.markdown("**Period:** `2026-10` (October 2026)")
    st.markdown("**Currency:** NOK (Norwegian Krone)")
    st.markdown("**Target Close:** Workday +4 *(Current: WD+2)*")
    
    st.markdown("---")
    st.subheader("🧭 Workspace Module")
    workspace_mode = st.radio(
        "Aktiv visning:",
        [
            "📊 Adra Balancer & Matcher (DuckDB Lakehouse)",
            "🔍 CLOSE-AI Financial Controls & Audit Dossier",
            "🌐 Unified Executive Control Room"
        ],
        index=0
    )

    st.markdown("---")
    st.subheader("👤 Controller Session")
    controller_name = st.text_input("Active Controller", value="Frank Ellingsen")
    controller_role = st.selectbox(
        "Authorization Tier",
        ["Tier 2 - Lead Project Controller", "Tier 1 - VP Finance / CFO"]
    )
    
    st.markdown("---")
    st.subheader("🤖 AI Engine Configuration")
    ai_engine = st.selectbox(
        "Inference Engine",
        ["Deterministic Audit Engine", "Gemini Flash (Cloud)", "Ollama (Local Llama 3.1)"]
    )
    if "Deterministic" in ai_engine:
        st.caption("🔒 Strict zero-hallucination code-governed calculations.")
    elif "Ollama" in ai_engine:
        st.caption("🛡️ Local air-gapped inference on internal network.")
    else:
        st.caption("⚡ Cloud inference with structured JSON output.")
        
    st.markdown("---")
    col_reset1, col_reset2 = st.columns(2)
    with col_reset1:
        if st.button("🔄 Re-Run Engine", use_container_width=True):
            st.cache_data.clear()
            st.toast("Controls & Lakehouse re-evaluated.")
            st.rerun()
    with col_reset2:
        if st.button("♻️ Reset Data", use_container_width=True):
            generate_erp_dataset(ERP_DIR)
            setup_databases(DUCKDB_DIR)
            generate_nordea_dataset(DUCKDB_DIR)
            st.session_state.resolved_anomalies = set()
            st.session_state.disputed_items = set()
            st.session_state.posted_journals = []
            st.session_state.period_locked = False
            persist_workflow_state()
            st.toast("Datasets & DuckDB reset to baseline.")
            st.rerun()

# ---------------------------------------------------------
# MODULE 1: Adra Balancer & Matcher (DuckDB Lakehouse)
# ---------------------------------------------------------
def render_adra_balancer_module():
    st.header("🏢 Adra Balancer, Matcher & DuckDB Control Room")
    st.caption("Automatisert bankavstemming, 4-veis balansekontroll, spin-off bilagsgenerering og toveis DuckDB-synkronisering.")

    # Fetch accounts from DuckDB
    try:
        with duckdb.connect(MAIN_DB) as con:
            accounts_df = con.execute("SELECT account_id, account_name, bank_iban, currency, ib_bank, ib_erp, rounding_tolerance FROM accounts").df()
    except Exception as e:
        setup_databases(DUCKDB_DIR)
        with duckdb.connect(MAIN_DB) as con:
            accounts_df = con.execute("SELECT account_id, account_name, bank_iban, currency, ib_bank, ib_erp, rounding_tolerance FROM accounts").df()

    acc_options = accounts_df['account_id'] + " - " + accounts_df['account_name']
    c_acc, c_per = st.columns([3, 1])
    with c_acc:
        selected_acc_str = st.selectbox("Velg aktiv avstemmingskonto:", acc_options, index=0)
        selected_acc_id = selected_acc_str.split(" - ")[0]
    with c_per:
        st.selectbox("Finansiell periode:", ["2026-10 (Oktober 2026)", "2026-09 (September 2026)", "2026-08 (August 2026)"], index=0)

    acc_info = accounts_df[accounts_df['account_id'] == selected_acc_id].iloc[0]

    # Calculate Balances & Open items
    with duckdb.connect(MAIN_DB) as con:
        bank_moves = con.execute("SELECT coalesce(sum(amount), 0) FROM staging_bank WHERE account_id = ?", [selected_acc_id]).fetchone()[0]
        erp_moves = con.execute("SELECT coalesce(sum(amount), 0) FROM staging_erp WHERE account_id = ?", [selected_acc_id]).fetchone()[0]

    ub_bank = acc_info['ib_bank'] + bank_moves
    ub_erp = acc_info['ib_erp'] + erp_moves

    with duckdb.connect(UNRECON_DB) as con:
        open_bank = con.execute("SELECT * FROM open_bank_items WHERE account_id = ?", [selected_acc_id]).df()
        open_erp = con.execute("SELECT * FROM open_erp_items WHERE account_id = ?", [selected_acc_id]).df()

    with duckdb.connect(RECON_DB) as con:
        reconciled_df = con.execute("SELECT * FROM reconciled WHERE account_id = ?", [selected_acc_id]).df()

    # Top KPI Metrics Ribbon
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("UB Bank (Kontoutskrift)", f"{ub_bank:,.2f} {acc_info['currency']}")
    kpi2.metric("UB Hovedbok ERP", f"{ub_erp:,.2f} {acc_info['currency']}")
    kpi3.metric("Avstemte poster (DuckDB)", len(reconciled_df), delta=f"{len(reconciled_df)} poster")
    kpi4.metric("Åpne bankposter", len(open_bank), delta=f"-{len(open_bank)}" if len(open_bank) > 0 else "0", delta_color="inverse")

    st.markdown("---")

    adra_tabs = st.tabs([
        "📊 4-Veis Balansekontroll (Adra Balancer)",
        "⚖️ Avstemmingsbenk (Adra Matcher)",
        "📝 Spin-Off Bilagsgenerator",
        "⚙️ Superbruker Regler (Regelstige)"
    ])

    # Tab 1: 4-Way Balance Control
    with adra_tabs[0]:
        st.subheader("Klassisk 4-delt Balansekontroll (Adra Balancer Bro)")
        st.caption("Matematisk bevis: Justert ERP = Justert Bank, hvor åpne timing-forskjeller og gebyrer isoleres med ørediff-toleranse.")

        box1 = open_bank[open_bank['amount'] > 0]['amount'].sum() if len(open_bank) > 0 else 0.0
        box2 = abs(open_bank[open_bank['amount'] < 0]['amount'].sum()) if len(open_bank) > 0 else 0.0
        box3 = open_erp[open_erp['amount'] > 0]['amount'].sum() if len(open_erp) > 0 else 0.0
        box4 = abs(open_erp[open_erp['amount'] < 0]['amount'].sum()) if len(open_erp) > 0 else 0.0

        adj_erp = ub_erp + box1 - box2
        adj_bank = ub_bank + box3 - box4
        delta = round(adj_erp - adj_bank, 2)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            **Boks 1: Kredittert Bank / Ikke debetert ERP:**  
            `{box1:,.2f} NOK` *(Uidentifiserte kundeinnbetalinger i transit)*
            
            **Boks 2: Debetert Bank / Ikke kreditert ERP:**  
            `{box2:,.2f} NOK` *(Autonome bankgebyrer og lånerenter som krever spin-off)*
            """)
        with c2:
            st.markdown(f"""
            **Boks 3: Debetert ERP / Ikke kreditert Bank:**  
            `{box3:,.2f} NOK` *(Bokførte innbetalinger som ennå ikke er godskrevet bank)*
            
            **Boks 4: Kredittert ERP / Ikke debetert Bank:**  
            `{box4:,.2f} NOK` *(Utestående remitteringer og leverandørutbetalinger i transit)*
            """)

        st.markdown("---")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Korrigert Hovedbok (Justert ERP)", f"{adj_erp:,.2f} NOK")
        res_col2.metric("Korrigert Bankbeholdning (Justert Bank)", f"{adj_bank:,.2f} NOK")
        res_col3.metric("Avstemmingsdifferanse (Delta)", f"{delta:,.2f} NOK", delta="0,00 kr" if abs(delta) <= acc_info['rounding_tolerance'] else f"{delta:,.2f} kr", delta_color="inverse")

        if abs(delta) <= acc_info['rounding_tolerance']:
            st.success(f"✓ I PERFEKT BALANSE: Justert ERP ({adj_erp:,.2f} NOK) == Justert Bank ({adj_bank:,.2f} NOK). Toleranse = ±{acc_info['rounding_tolerance']} NOK.")
        else:
            st.error(f"⚠ UBALANSE DETEKTERT: Differanse = {delta:,.2f} NOK. Behandle uavstemte poster eller godkjenn Spin-Off bilag under fane 3.")

    # Tab 2: Matcher Bench
    with adra_tabs[1]:
        st.subheader("Avstemmingsbenk — Åpne Bank- og ERP-poster")
        st.caption("Viser uavstemte transaksjoner lagret i DuckDB unreconciled_transactions.")
        col_b, col_e = st.columns(2)
        with col_b:
            st.markdown(f"**Åpne poster på Bankutskrift ({len(open_bank)}):**")
            st.dataframe(open_bank, use_container_width=True, hide_index=True)
        with col_e:
            st.markdown(f"**Åpne poster i ERP Hovedbok ({len(open_erp)}):**")
            st.dataframe(open_erp, use_container_width=True, hide_index=True)

        if len(reconciled_df) > 0:
            st.markdown(f"#### Avstemte poster i perioden ({len(reconciled_df)})")
            st.dataframe(reconciled_df, use_container_width=True, hide_index=True)

    # Tab 3: Spin-Off Vouchers
    with adra_tabs[2]:
        st.subheader("AI Spin-Off Bilagsgenerator (Bankgebyrer & Renter)")
        st.caption("Automatisk identifisering av poster belastet bank men ikke bokført i ERP (Boks 2).")

        fees_and_interest = open_bank[open_bank['text'].str.contains('gebyr|rente|fee|interest', case=False, na=False)]
        
        if len(fees_and_interest) > 0:
            for _, row in fees_and_interest.iterrows():
                is_fee = "gebyr" in row['text'].lower()
                debit_acc = "7770 Bank- og kortgebyrer" if is_fee else "8150 Annen rentekostnad"
                st.info(f"**{row['text']}** — Beløp: `{abs(row['amount']):,.2f} NOK` per `{row['tx_date']}`. Forslag: **Debet {debit_acc}** / **Kredit {selected_acc_id} {acc_info['account_name']}**")
                
                if st.button(f"⚡ Godkjenn og postér bilag for {row['tx_id']}", key=f"spinoff_{row['tx_id']}"):
                    with duckdb.connect(RECON_DB) as con:
                        con.execute("""
                            INSERT OR REPLACE INTO reconciled (match_id, account_id, bank_tx_id, erp_voucher_no, amount, rule_applied, difference, notes)
                            VALUES (?, ?, ?, ?, ?, 'R-SPINOFF', 0.0, ?)
                        """, [f"VOUCH-{row['tx_id']}", selected_acc_id, row['tx_id'], f"ERP-{row['tx_id']}", row['amount'], row['text']])
                    
                    with duckdb.connect(UNRECON_DB) as con:
                        con.execute("DELETE FROM open_bank_items WHERE tx_id = ?", [row['tx_id']])
                    
                    with duckdb.connect(MAIN_DB) as con:
                        con.execute("""
                            INSERT OR REPLACE INTO staging_erp (voucher_no, account_id, post_date, amount, text, invoice_no, kid_ocr, wbs)
                            VALUES (?, ?, CURRENT_DATE, ?, ?, 'AUTO-SPINOFF', '', 'PRJ-ADMIN')
                        """, [f"ERP-{row['tx_id']}", selected_acc_id, row['amount'], row['text']])
                    
                    st.success(f"Bilag for {row['tx_id']} er postert i DuckDB! Balansekontroll oppdatert.")
                    st.rerun()
        else:
            st.success("✓ Ingen ubehandlede bankgebyrer eller renteposter funnet. Alle kjente poster er godkjent og postert!")

    # Tab 4: Rules Ladder
    with adra_tabs[3]:
        st.subheader("Aktive Avstemmingsregler (Regelstige R-01 til R-AI)")
        with duckdb.connect(MAIN_DB) as con:
            rules_df = con.execute("SELECT * FROM match_rules ORDER BY priority ASC").df()
        st.dataframe(rules_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# MODULE 2: Financial Controls & Exception Dossier
# ---------------------------------------------------------
def render_financial_controls_module():
    st.header("Financial Close & Audit Control Room")
    st.caption("Nordic Engineering Projects AS • Period 2026-10 • Deterministic Verification • Isolation Forest ML • HITL Approval")

    # Evaluate controls
    raw_controls = run_close_controls(ERP_DIR)
    controls_list = []
    earned_weight = 0
    total_weight = sum(RULE_WEIGHTS.values())
    has_active_blocker = False

    for c in raw_controls["controls_summary"]:
        item = c.copy()
        rule_id = item["rule_id"]
        if rule_id in st.session_state.resolved_anomalies:
            item["status"] = "PASS"
            item["discrepancy_amount_nok"] = 0.0
            item["affected_count"] = 0
        
        if item["status"] == "PASS":
            earned_weight += item["weight"]
        elif item["severity"] == "BLOCKER":
            has_active_blocker = True
        controls_list.append(item)

    readiness_score = round((earned_weight / total_weight) * 100.0, 1)

    if st.session_state.period_locked:
        close_status = "PERIOD CLOSED & LOCKED"
    elif has_active_blocker:
        close_status = "CLOSE BLOCKED"
    elif readiness_score >= 95.0:
        close_status = "READY FOR CONTROLLER SIGN-OFF"
    else:
        close_status = "ACTION REQUIRED"

    # Metrics Ribbon
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns([1.6, 1, 1.2, 1])
    with col_stat1:
        if close_status == "CLOSE BLOCKED":
            st.error(f"### Status: 🔴 {close_status}")
        elif close_status == "READY FOR CONTROLLER SIGN-OFF":
            st.success(f"### Status: 🟢 {close_status}")
        elif close_status == "PERIOD CLOSED & LOCKED":
            st.info(f"### Status: 🔒 {close_status}")
        else:
            st.warning(f"### Status: 🟡 {close_status}")
    with col_stat2:
        st.metric("Composite Control Score", f"{readiness_score:.1f}%", delta=f"{readiness_score - 100:.1f}%")
    with col_stat3:
        failed_count = sum(1 for c in controls_list if c["status"] == "FAIL")
        st.metric("Deterministic Rule Failures", f"{failed_count} / {len(controls_list)}", delta="-1" if failed_count > 0 else "0", delta_color="inverse")
    with col_stat4:
        st.metric("Isolation Forest Outliers", "1 Anomaly", delta="Critical", delta_color="inverse")

    st.markdown("---")

    # Zone 1: Deterministic Controls Table
    st.subheader("1. Deterministic Financial Controls Matrix")
    controls_table_data = []
    for c in controls_list:
        status_symbol = "🟢 PASS" if c["status"] == "PASS" else ("🔴 FAIL" if c["severity"] == "BLOCKER" else "🟡 WARN")
        controls_table_data.append({
            "Rule ID": c["rule_id"],
            "Control Description": c["description"],
            "Severity": c["severity"],
            "Weight": f"{c['weight']} pts",
            "Status": status_symbol,
            "Discrepancy (NOK)": f"{c['discrepancy_amount_nok']:,.2f}",
            "Items": c["affected_count"]
        })
    df_controls = pd.DataFrame(controls_table_data)
    st.dataframe(df_controls, use_container_width=True, hide_index=True)

    # Zone 2: ML Anomaly Detector
    st.markdown("---")
    st.subheader("2. Multivariate Statistical Anomaly Detection (Isolation Forest)")
    ml_results = run_anomaly_detection(ERP_DIR)
    col_ml1, col_ml2 = st.columns([1, 2])
    with col_ml1:
        st.markdown(f"**Evaluated Postings:** `{ml_results['evaluated_postings']}`")
        st.markdown(f"**Contamination Rate:** `{ml_results['contamination_rate'] * 100:.1f}%`")
        st.markdown(f"**Outliers Flagged:** `{ml_results['outliers_flagged']}`")
    with col_ml2:
        if ml_results["top_anomalies"]:
            st.markdown("**Top Statistical Outlier Postings:**")
            st.dataframe(pd.DataFrame(ml_results["top_anomalies"]), use_container_width=True, hide_index=True)

    # Zone 3: Investigation Dossier & Tabs
    st.markdown("---")
    st.subheader("3. Investigation Workbench & Human-in-the-Loop Approval Gate")
    inv_agent = CloseInvestigatorAgent(data_dir=ERP_DIR, provider="deterministic")

    tab_inv, tab_staged, tab_audit, tab_tb = st.tabs([
        "🔍 Active Investigations & Proposals",
        "📋 Staged / Posted Adjustments",
        "📜 Verifiable Audit Evidence Pack",
        "📊 Pre vs. Post Close Trial Balance"
    ])

    with tab_inv:
        failing_rules = [c for c in controls_list if c["status"] == "FAIL"]
        if not failing_rules:
            st.success("All deterministic accounting controls are satisfied. No active investigations.")
        else:
            selected_rule = st.selectbox(
                "Select active exception to review dossier:",
                [f"{c['rule_id']}: {c['description']} ({c['discrepancy_amount_nok']:,.2f} NOK)" for c in failing_rules]
            )
            rule_id = selected_rule.split(":")[0]
            dossier = inv_agent.investigate_anomaly(rule_id, "SAMPLE_TARGET")

            col_dos1, col_dos2 = st.columns([2, 1])
            with col_dos1:
                st.markdown(f"#### Investigation Dossier: `{dossier['investigation_id']}`")
                st.markdown(f"**Observation:** {dossier['observation']}")
                st.markdown(f"**Likely Root Cause:** {dossier['likely_cause']}")
                st.markdown(f"**Recommended Action:** {dossier['recommended_action']}")
            with col_dos2:
                st.markdown("#### Financial Exposure")
                st.metric("Unauthorized Variance", f"{dossier['financial_impact']['unauthorized_variance_nok']:,.2f} NOK")
                st.metric("EBITDA Risk Assessment", dossier['financial_impact']['ebitda_risk'])

            # Proposed Journal Voucher
            jv = dossier.get("proposed_journal_voucher")
            if jv and jv.get("lines"):
                st.markdown("#### Proposed Corrective Journal Voucher")
                lines_df = pd.DataFrame(jv["lines"])
                lines_df["debit_nok"] = lines_df["debit_nok"].apply(lambda x: f"{x:,.2f}")
                lines_df["credit_nok"] = lines_df["credit_nok"].apply(lambda x: f"{x:,.2f}")
                st.dataframe(lines_df, use_container_width=True, hide_index=True)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"✅ Approve & Post Journal Voucher ({rule_id})", key=f"post_{rule_id}"):
                        st.session_state.resolved_anomalies.add(rule_id)
                        jv_entry = {
                            "journal_id": f"JV-POSTED-{len(st.session_state.posted_journals) + 1:04d}",
                            "rule_id": rule_id,
                            "entry_type": jv.get("entry_type", "ADJUSTMENT"),
                            "amount_nok": dossier['financial_impact']['unauthorized_variance_nok'],
                            "lines": jv["lines"],
                            "approver": controller_name,
                            "role": controller_role,
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "hash": hashlib.sha256(json.dumps(jv, sort_keys=True).encode()).hexdigest()[:16]
                        }
                        st.session_state.posted_journals.append(jv_entry)
                        st.session_state.audit_mgr.log_action(
                            event_type="JOURNAL_APPROVAL",
                            operator={"name": controller_name, "role": controller_role},
                            action_taken=f"Approved corrective journal {jv_entry['journal_id']} for {rule_id}",
                            entity_ref=rule_id,
                            evidence_payload=jv,
                            justification_memo=f"Controller approved proposed adjustment for {rule_id}"
                        )
                        persist_workflow_state()
                        st.success(f"Journal Voucher {jv_entry['journal_id']} successfully committed to ERP audit trail.")
                        st.rerun()

                with col_btn2:
                    if st.button(f"🚩 Route to Dispute / Vendor Query ({rule_id})", key=f"disp_{rule_id}"):
                        st.session_state.disputed_items.add(rule_id)
                        st.session_state.audit_mgr.log_action(
                            event_type="DISPUTE_RAISED",
                            operator={"name": controller_name, "role": controller_role},
                            action_taken=f"Routed {rule_id} to procurement inquiry",
                            entity_ref=rule_id,
                            evidence_payload=dossier,
                            justification_memo="Variance exceeds tolerance without valid subcontract change order."
                        )
                        persist_workflow_state()
                        st.warning(f"Exception {rule_id} marked as disputed. Formal query sent.")
                        st.rerun()

    with tab_staged:
        st.subheader("Committed Period-End Adjusting Entries")
        if not st.session_state.posted_journals:
            st.info("No adjusting journals posted yet.")
        else:
            for j in st.session_state.posted_journals:
                with st.expander(f"📌 {j['journal_id']} | Rule: {j.get('rule_id', 'N/A')} | Approver: {j['approver']} | Hash: {j['hash']}"):
                    st.json(j)

    with tab_audit:
        st.subheader("Statutory Audit Evidence Pack (ISA 240 / 315 / 500)")
        if st.session_state.audit_mgr.records:
            audit_display = []
            for r in st.session_state.audit_mgr.records:
                audit_display.append({
                    "Event ID": r["audit_event_id"],
                    "Timestamp (UTC)": r["timestamp_utc"][:19],
                    "Event Type": r["event_type"],
                    "Approver": r["operator"]["name"],
                    "Action": r["action_taken"],
                    "Memo": r["justification_memo"],
                    "SHA-256 Seal": r["current_record_hash"][:16] + "..."
                })
            st.dataframe(pd.DataFrame(audit_display), use_container_width=True, hide_index=True)

    with tab_tb:
        st.subheader("General Ledger Trial Balance Reconciliation")
        con_tb = get_duckdb_connection(ERP_DIR)
        tb_df = con_tb.execute("""
            SELECT 
                account_number,
                ROUND(SUM(debit_nok), 2) AS debit_nok,
                ROUND(SUM(credit_nok), 2) AS credit_nok,
                ROUND(SUM(debit_nok) - SUM(credit_nok), 2) AS net_balance_nok
            FROM gl_journal_lines
            GROUP BY account_number
            ORDER BY account_number
        """).df()
        st.dataframe(tb_df, use_container_width=True, hide_index=True)
        con_tb.close()

# ---------------------------------------------------------
# Main Workspace Router
# ---------------------------------------------------------
if workspace_mode == "📊 Adra Balancer & Matcher (DuckDB Lakehouse)":
    render_adra_balancer_module()
elif workspace_mode == "🔍 CLOSE-AI Financial Controls & Audit Dossier":
    render_financial_controls_module()
else:
    # Unified Executive Cockpit
    render_adra_balancer_module()
    st.markdown("---")
    render_financial_controls_module()
