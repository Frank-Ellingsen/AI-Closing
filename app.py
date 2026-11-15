"""
CLOSE-AI: Financial Close & Audit Control Room Cockpit
Designed for Nordic Engineering Projects AS (Stavanger / Oslo, Norway)
Executive Controller: Frank Ellingsen (Lead Project Controller)
Adheres to Edward Tufte's Data-Ink ratio principles & statutory audit standards (ISA 240 / 315 / 500 & SAF-T).
"""

import os
import json
import datetime
import hashlib
import pandas as pd
import numpy as np
import streamlit as st

from src.engine.evaluate_controls import run_close_controls, get_duckdb_connection, RULE_WEIGHTS
from src.ml.anomaly_detector import run_anomaly_detection
from src.agent.investigator import CloseInvestigatorAgent
from src.audit.audit_manager import AuditManager
from src.data_generator.generate_erp_data import generate_erp_dataset

# ---------------------------------------------------------
# Page Configuration & Styling (Tufte Data-Ink Principles)
# ---------------------------------------------------------
st.set_page_config(
    page_title="CLOSE-AI | Financial Close Control Room",
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
        padding: 8px 12px;
        color: #2b2b2b;
    }
    .num {
        text-align: right;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    }
    
    /* Muted status pills */
    .pill-pass {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pill-fail {
        background-color: #ffebee;
        color: #c62828;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pill-warning {
        background-color: #fff8e1;
        color: #f57f17;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Evidence code block */
    .evidence-card {
        background-color: #f8f9fa;
        border-left: 3px solid #0d3b66;
        padding: 10px 14px;
        margin: 8px 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "audit_mgr" not in st.session_state:
    st.session_state.audit_mgr = AuditManager(
        log_file="audit_log_2026_10.json",
        workflow_file="workflow_state_2026_10.json"
    )


def persist_workflow_state():
    state = {
        "resolved_anomalies": sorted(st.session_state.get("resolved_anomalies", set())),
        "disputed_items": sorted(st.session_state.get("disputed_items", set())),
        "posted_journals": list(st.session_state.get("posted_journals", [])),
        "period_locked": bool(st.session_state.get("period_locked", False)),
    }
    st.session_state.audit_mgr.save_workflow_state(state)
    st.session_state.audit_mgr.workflow_state = state


stored_state = st.session_state.audit_mgr.get_workflow_snapshot()
if "posted_journals" not in st.session_state:
    st.session_state.posted_journals = stored_state.get("posted_journals", [])

if "resolved_anomalies" not in st.session_state:
    st.session_state.resolved_anomalies = set(stored_state.get("resolved_anomalies", []))

if "disputed_items" not in st.session_state:
    st.session_state.disputed_items = set(stored_state.get("disputed_items", []))

if "period_locked" not in st.session_state:
    st.session_state.period_locked = bool(stored_state.get("period_locked", False))

persist_workflow_state()

# Ensure data exists
DATA_DIR = "erp_data_2026_10"
if not os.path.exists(DATA_DIR) or not os.path.exists(os.path.join(DATA_DIR, "gl_journal_lines.csv")):
    generate_erp_dataset(DATA_DIR)

# ---------------------------------------------------------
# Sidebar: Control Room Controls & Entity Metadata
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚖️ CLOSE-AI")
    st.caption("Autonomous Financial Close & Exception Governance")
    st.markdown("---")
    
    st.markdown("**Entity:** Nordic Engineering Projects AS")
    st.markdown("**Org Nr:** `NO 984 521 890 MVA`")
    st.markdown("**Period:** `2026-10` (October 2026)")
    st.markdown("**Currency:** NOK (Norwegian Krone)")
    st.markdown("**Target Close:** Workday +4 *(Current: WD+2)*")
    
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
            st.toast("Controls re-evaluated.")
            st.rerun()
    with col_reset2:
        if st.button("♻️ Reset Data", use_container_width=True):
            generate_erp_dataset(DATA_DIR)
            st.session_state.resolved_anomalies = set()
            st.session_state.disputed_items = set()
            st.session_state.posted_journals = []
            st.session_state.period_locked = False
            persist_workflow_state()
            st.toast("ERP dataset reset to baseline.")
            st.rerun()

# ---------------------------------------------------------
# Header & Executive Close Status Banner
# ---------------------------------------------------------
st.title("Financial Close & Audit Control Room")
st.caption("Nordic Engineering Projects AS • Period 2026-10 • Deterministic Verification • Isolation Forest ML • HITL Approval")

# Evaluate controls
raw_controls = run_close_controls(DATA_DIR)
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
    status_color = "green"
elif has_active_blocker:
    close_status = "CLOSE BLOCKED"
    status_color = "red"
elif readiness_score >= 95.0:
    close_status = "READY FOR CONTROLLER SIGN-OFF"
    status_color = "green"
else:
    close_status = "ACTION REQUIRED"
    status_color = "orange"

# Metrics Ribbon
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns([1.6, 1, 1.2, 1])

with col_stat1:
    if close_status == "CLOSE BLOCKED":
        st.error(f"### Status: 🔴 {close_status}")
        st.caption("Hard Blocker active: Zero trial balance imbalance violated.")
    elif close_status == "READY FOR CONTROLLER SIGN-OFF":
        st.success(f"### Status: 🟢 {close_status}")
        st.caption("All mandatory accounting controls satisfied.")
    elif close_status == "PERIOD CLOSED & LOCKED":
        st.info(f"### Status: 🔒 {close_status}")
        st.caption("General ledger frozen and digitally sealed for 2026-10.")
    else:
        st.warning(f"### Status: 🟡 {close_status}")
        st.caption("Exceptions identified; human controller review required.")

with col_stat2:
    st.metric(label="Readiness Index", value=f"{readiness_score:.1f}%")

with col_stat3:
    total_discrepancy = sum(c["discrepancy_amount_nok"] for c in controls_list)
    st.metric(label="Total Discrepancy", value=f"{total_discrepancy:,.0f} NOK")

with col_stat4:
    open_items = sum(1 for c in controls_list if c["status"] != "PASS")
    st.metric(label="Open Action Items", value=f"{open_items} Items")

st.markdown("---")

# ---------------------------------------------------------
# Zone 1: Deterministic Financial Controls Matrix
# ---------------------------------------------------------
st.subheader("1. Deterministic Financial Controls Matrix")
cols_mat = st.columns(3)

for idx, ctrl in enumerate(controls_list):
    status = ctrl["status"]
    with cols_mat[idx % 3]:
        with st.container(border=True):
            if status == "PASS":
                badge = '<span class="pill-pass">PASS</span>'
            elif ctrl["severity"] == "BLOCKER":
                badge = '<span class="pill-fail">BLOCKER</span>'
            elif status == "FAIL":
                badge = '<span class="pill-fail">FAIL</span>'
            else:
                badge = '<span class="pill-warning">WARNING</span>'

            st.markdown(f"**{ctrl['rule_id']}: {ctrl['rule_name']}** {badge}", unsafe_allow_html=True)
            st.caption(f"Domain: `{ctrl.get('domain', 'ACCOUNTING')}` | Weight: `{ctrl['weight']} pts`")
            
            if status == "PASS":
                st.markdown("<p style='color: #2e7d32; font-weight: 600; margin-top: 8px;'>0.00 NOK Exposure (Satisfied)</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: #c62828; font-weight: 600; margin-top: 8px;'>{ctrl['discrepancy_amount_nok']:,.2f} NOK Exposure ({ctrl['affected_count']} item)</p>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# Zone 2: Multivariate Statistical Anomaly Detection (Isolation Forest)
# ---------------------------------------------------------
with st.expander("2. Multivariate Statistical Anomaly Detection (Isolation Forest)", expanded=False):
    st.markdown("""
    The unsupervised machine learning layer inspects 11-dimensional transaction features (Z-scores, Benford distribution, off-hours timing, round thousands) to isolate structural outliers without static rules.
    """)
    df_anomalies = run_anomaly_detection(DATA_DIR)
    crit_anomalies = df_anomalies[df_anomalies["anomaly_score"] >= 65.0].sort_values(by="anomaly_score", ascending=False)
    
    col_ml1, col_ml2, col_ml3 = st.columns([1, 1, 2])
    with col_ml1:
        st.metric("Total Flagged (≥65)", len(crit_anomalies))
    with col_ml2:
        st.metric("Critical Outliers (≥85)", len(crit_anomalies[crit_anomalies["anomaly_score"] >= 85.0]))
    with col_ml3:
        st.caption("Scoring Thresholds: <65 Normal | 65–84 Monitoring Queue | ≥85 Autonomous Investigation Priority")

    # Present formatted table
    display_cols = ["entry_id", "account_number", "amount_nok", "anomaly_score", "anomaly_band", "explanation"]
    clean_ml_df = crit_anomalies[display_cols].copy()
    clean_ml_df.columns = ["Entry ID", "Account", "Amount (NOK)", "Score", "Band", "Feature Drivers"]
    clean_ml_df["Amount (NOK)"] = clean_ml_df["Amount (NOK)"].apply(lambda x: f"{x:,.2f}")
    st.dataframe(clean_ml_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Zone 3: Autonomous Investigation Dossier & HITL Actions
# ---------------------------------------------------------
st.subheader("3. Investigation Workbench & Human-in-the-Loop Approval Gate")

tab_investigate, tab_posted, tab_audit, tab_tb = st.tabs([
    "🔍 Active Investigations & Proposals",
    "📋 Staged / Posted Adjustments",
    "📜 Verifiable Audit Evidence Pack",
    "📊 Pre vs. Post Close Trial Balance"
])

# Initialize investigation agent
provider_name = "deterministic"
if "Ollama" in ai_engine:
    provider_name = "ollama"
elif "Gemini" in ai_engine:
    provider_name = "gemini"

agent = CloseInvestigatorAgent(data_dir=DATA_DIR, provider=provider_name)

with tab_investigate:
    st.markdown("Review AI-compiled evidence chains, identify root causes, and sign off on proposed adjusting entries.")

    # ---------------------------------------------------------
    # CASE 1: Hard Blocker - Trial Balance Imbalance (CTRL-GL-01)
    # ---------------------------------------------------------
    if "CTRL-GL-01" not in st.session_state.resolved_anomalies:
        with st.expander("🔴 CRITICAL HARD BLOCKER: Trial Balance Imbalance (Delta: 15,000.00 NOK)", expanded=True):
            d_tb = agent.investigate_anomaly("CTRL-GL-01", "JV-2026-10-1039")
            
            st.error(f"**Finding:** {d_tb['observation']}")
            
            st.markdown("**Evidence Chain:**")
            for ev in d_tb["evidence_chain"]:
                st.markdown(f"- **{ev['source']}:** {ev['fact']}")
            
            st.markdown(f"**Root Cause:** {d_tb['likely_cause']}")
            
            st.markdown("#### Proposed Rebalancing Leg")
            rebal_lines = d_tb["proposed_journal_voucher"]["lines"]
            st.dataframe(pd.DataFrame(rebal_lines), use_container_width=True, hide_index=True)

            col_tb_act1, col_tb_act2 = st.columns([1.5, 4])
            with col_tb_act1:
                if st.button("Fix & Post Rebalancing Leg", key="btn_fix_tb", use_container_width=True):
                    st.session_state.resolved_anomalies.add("CTRL-GL-01")
                    persist_workflow_state()
                    audit_entry = st.session_state.audit_mgr.log_event(
                        event_type="MANUAL_REBALANCE_POSTED",
                        operator_name=controller_name,
                        operator_role=controller_role,
                        journal_id="JV-2026-10-1039-ADJ",
                        action_taken="REBALANCED",
                        investigation_id=d_tb["investigation_id"],
                        triggering_control="CTRL-GL-01",
                        financial_lines=rebal_lines,
                        justification_memo="Credited 15,000.00 NOK to Account 1910 to eliminate trial balance delta."
                    )
                    st.session_state.posted_journals.append({
                        "journal_id": "JV-2026-10-1039-ADJ",
                        "entry_type": "CORRECTION_ADJUSTMENT",
                        "amount_nok": 15000.0,
                        "wbs_code": "N/A",
                        "approver": controller_name,
                        "hash": audit_entry["current_record_hash"][:16]
                    })
                    persist_workflow_state()
                    st.success("Rebalancing line committed to General Ledger. Blocker cleared!")
                    st.rerun()

    # ---------------------------------------------------------
    # CASE 2: Tolerance Overrun on Subsea PO-8809 (CTRL-AP-03)
    # ---------------------------------------------------------
    if "CTRL-AP-03" not in st.session_state.resolved_anomalies:
        with st.expander("🟡 EXCEPTION: PO-8809 Price Tolerance Overrun (+22.4%) - Nordic Subsea Fabrication AS", expanded=True):
            d_overrun = agent.investigate_anomaly("CTRL-AP-03", "INV-VEND-99214")
            
            col_dos1, col_dos2 = st.columns(2)
            with col_dos1:
                st.markdown(f"**Target Entity:** `{d_overrun['target_entity']}` | **Severity:** `{d_overrun['severity']}`")
                st.markdown(f"**AI Observation:**\n{d_overrun['observation']}")
                st.markdown("**Evidence Chain:**")
                for ev in d_overrun["evidence_chain"]:
                    st.markdown(f"- **{ev['source']}:** {ev['fact']}")
            with col_dos2:
                st.markdown(f"**Root Cause Diagnosis:**\n{d_overrun['likely_cause']}")
                fin = d_overrun["financial_impact"]
                st.markdown(f"""
                **Financial Exposure:**
                - **Unauthorized Variance:** `{fin['unauthorized_variance_nok']:,.2f} NOK`
                - **EBITDA / Gross Margin Risk:** {fin['ebitda_risk']}
                - **VAT Exposure (25%):** `{fin['vat_impact_nok']:,.2f} NOK`
                """)
                st.markdown(f"**Recommended Policy:** `{d_overrun['recommended_action']}`")

            st.markdown("#### Staged Journal Voucher Proposal")
            jv = d_overrun["proposed_journal_voucher"]
            st.table(pd.DataFrame(jv["lines"]))

            col_act1, col_act2, col_act3, col_act4 = st.columns(4)
            with col_act1:
                if st.button("✅ Approve & Post Accrual", key="btn_app_overrun", use_container_width=True):
                    st.session_state.resolved_anomalies.add("CTRL-AP-03")
                    persist_workflow_state()
                    jv_id = f"JV-POSTED-{len(st.session_state.posted_journals) + 1:04d}"
                    audit_entry = st.session_state.audit_mgr.log_event(
                        event_type="JOURNAL_VOUCHER_POSTED",
                        operator_name=controller_name,
                        operator_role=controller_role,
                        journal_id=jv_id,
                        action_taken="APPROVED_WITHOUT_EDIT",
                        investigation_id=d_overrun["investigation_id"],
                        triggering_control="CTRL-AP-03",
                        financial_lines=jv["lines"],
                        justification_memo="Accrued authorized 670,000.00 NOK delivery per GR-4412. Held 150,000.00 NOK dispute for PM change order review."
                    )
                    st.session_state.posted_journals.append({
                        "journal_id": jv_id,
                        "entry_type": jv["entry_type"],
                        "amount_nok": 670000.0,
                        "wbs_code": "PRJ-2026-001.03.FAB",
                        "approver": controller_name,
                        "hash": audit_entry["current_record_hash"][:16]
                    })
                    persist_workflow_state()
                    st.success(f"Adjusting voucher {jv_id} committed to General Ledger!")
                    st.rerun()

            with col_act2:
                if st.button("✏️ Edit Adjustment", key="btn_edit_overrun", use_container_width=True):
                    st.info("Edit dialog opened. Controller can override accounts and amounts with mandatory rationale.")
            with col_act3:
                if st.button("⏸️ Dispute / Hold 150k", key="btn_hold_overrun", use_container_width=True):
                    st.session_state.disputed_items.add("INV-VEND-99214")
                    persist_workflow_state()
                    st.session_state.audit_mgr.log_event(
                        event_type="PAYMENT_HOLD_LOGGED",
                        operator_name=controller_name,
                        operator_role=controller_role,
                        journal_id="TICKET-DISPUTE-001",
                        action_taken="DISPUTE_LOGGED",
                        investigation_id=d_overrun["investigation_id"],
                        triggering_control="CTRL-AP-03",
                        justification_memo="150,000.00 NOK variance placed on hold and routed to Frank Ellingsen for customer change order verification."
                    )
                    st.warning("150,000.00 NOK placed on payment hold and dispute ticket generated.")
            with col_act4:
                if st.button("❌ Reject Proposal", key="btn_rej_overrun", use_container_width=True):
                    st.error("Proposal rejected. Rationale logged in audit ledger.")

    # ---------------------------------------------------------
    # CASE 3: Uninvoiced Goods Received (CTRL-AP-02)
    # ---------------------------------------------------------
    if "CTRL-AP-02" not in st.session_state.resolved_anomalies:
        with st.expander("🟡 EXCEPTION: PO-2026-8812 Delivered Goods Receipt Lacking Vendor Invoice (308,000.00 NOK)", expanded=False):
            d_gr = agent.investigate_anomaly("CTRL-AP-02", "PO-2026-8812")
            st.markdown(f"**Finding:** {d_gr['observation']}")
            st.markdown(f"**Root Cause:** {d_gr['likely_cause']}")
            st.markdown("#### Staged Reversing Accrual")
            st.table(pd.DataFrame(d_gr["proposed_journal_voucher"]["lines"]))
            if st.button("✅ Approve Reversing Accrual", key="btn_app_gr"):
                st.session_state.resolved_anomalies.add("CTRL-AP-02")
                persist_workflow_state()
                jv_id = f"JV-POSTED-{len(st.session_state.posted_journals) + 1:04d}"
                audit_entry = st.session_state.audit_mgr.log_event(
                    event_type="JOURNAL_VOUCHER_POSTED",
                    operator_name=controller_name,
                    operator_role=controller_role,
                    journal_id=jv_id,
                    action_taken="APPROVED_WITHOUT_EDIT",
                    investigation_id=d_gr["investigation_id"],
                    triggering_control="CTRL-AP-02",
                    financial_lines=d_gr["proposed_journal_voucher"]["lines"],
                    justification_memo="Accrued 308,000.00 NOK delivered crane modernization capex per delivery inspection."
                )
                st.session_state.posted_journals.append({
                    "journal_id": jv_id,
                    "entry_type": "REVERSING_ACCRUAL",
                    "amount_nok": 308000.0,
                    "wbs_code": "PRJ-2026-004.01.CAPEX",
                    "approver": controller_name,
                    "hash": audit_entry["current_record_hash"][:16]
                })
                persist_workflow_state()
                st.success("Reversing accrual committed!")
                st.rerun()

    # ---------------------------------------------------------
    # CASE 4: Duplicate Invoice (CTRL-AP-01)
    # ---------------------------------------------------------
    if "CTRL-AP-01" not in st.session_state.resolved_anomalies:
        with st.expander("🟡 EXCEPTION: Duplicate Invoice INV-VEND-99991-DUP (260,000.00 NOK)", expanded=False):
            d_dup = agent.investigate_anomaly("CTRL-AP-01", "INV-VEND-99991-DUP")
            st.markdown(f"**Finding:** {d_dup['observation']}")
            if st.button("🚫 Block Duplicate Payment & Void Voucher", key="btn_block_dup"):
                st.session_state.resolved_anomalies.add("CTRL-AP-01")
                persist_workflow_state()
                st.session_state.audit_mgr.log_event(
                    event_type="PAYMENT_BLOCK_LOGGED",
                    operator_name=controller_name,
                    operator_role=controller_role,
                    journal_id="INV-VEND-99991-DUP",
                    action_taken="VOIDED",
                    investigation_id=d_dup["investigation_id"],
                    triggering_control="CTRL-AP-01",
                    justification_memo="Voided duplicate invoice submitted by Bergen Marine Logistics AS."
                )
                st.success("Payment block enforced and duplicate voucher voided.")
                st.rerun()

    # ---------------------------------------------------------
    # CASE 5: Weekend Direct Cost Postings (CTRL-GL-02 & CTRL-PRJ-03)
    # ---------------------------------------------------------
    if "CTRL-GL-02" not in st.session_state.resolved_anomalies or "CTRL-PRJ-03" not in st.session_state.resolved_anomalies:
        with st.expander("🟡 EXCEPTION: Weekend Manual Direct Cost Posting (JV-2026-10-1038, 145,000.00 NOK)", expanded=False):
            d_wk = agent.investigate_anomaly("CTRL-GL-02/CTRL-PRJ-03", "JV-2026-10-1038")
            st.markdown(f"**Finding:** {d_wk['observation']}")
            st.markdown("#### Staged WBS Allocation")
            st.table(pd.DataFrame(d_wk["proposed_journal_voucher"]["lines"]))
            if st.button("✅ Approve Reclassification to PRJ-2026-001.03.FAB", key="btn_app_wk"):
                st.session_state.resolved_anomalies.add("CTRL-GL-02")
                st.session_state.resolved_anomalies.add("CTRL-PRJ-03")
                persist_workflow_state()
                jv_id = f"JV-POSTED-{len(st.session_state.posted_journals) + 1:04d}"
                audit_entry = st.session_state.audit_mgr.log_event(
                    event_type="JOURNAL_VOUCHER_POSTED",
                    operator_name=controller_name,
                    operator_role=controller_role,
                    journal_id=jv_id,
                    action_taken="APPROVED_WITHOUT_EDIT",
                    investigation_id=d_wk["investigation_id"],
                    triggering_control="CTRL-GL-02/CTRL-PRJ-03",
                    financial_lines=d_wk["proposed_journal_voucher"]["lines"],
                    justification_memo="Reclassified 145,000.00 NOK yard materials cost to Troll Wind WBS deliverable."
                )
                st.session_state.posted_journals.append({
                    "journal_id": jv_id,
                    "entry_type": "RECLASSIFICATION",
                    "amount_nok": 145000.0,
                    "wbs_code": "PRJ-2026-001.03.FAB",
                    "approver": controller_name,
                    "hash": audit_entry["current_record_hash"][:16]
                })
                persist_workflow_state()
                st.success("Reclassification committed!")
                st.rerun()

    if len(st.session_state.resolved_anomalies) == 6:
        st.success("🎉 All active close exceptions have been formally investigated and signed off by the controller!")

# ---------------------------------------------------------
# Tab 2: Staged & Posted Adjustments
# ---------------------------------------------------------
with tab_posted:
    st.subheader("Committed Period-End Adjusting Entries")
    st.caption("Journal vouchers committed during this session with controller attribution and digital signatures.")
    if not st.session_state.posted_journals:
        st.info("No adjusting journal vouchers committed yet during this session.")
    else:
        df_posted = pd.DataFrame(st.session_state.posted_journals)
        df_posted["amount_nok"] = df_posted["amount_nok"].apply(lambda x: f"{x:,.2f} NOK")
        st.dataframe(df_posted, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Tab 3: Verifiable Audit Evidence Pack
# ---------------------------------------------------------
with tab_audit:
    st.subheader("Statutory Audit Evidence Pack (ISA 240 / 315 / 500)")
    st.caption("Cryptographic hash chain verifying unbroken custody and tamper-evidence.")
    
    verif = st.session_state.audit_mgr.verify_audit_chain()
    
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        if verif["valid"]:
            st.success(f"**Cryptographic Status:** ✅ VALID ({verif['record_count']} Sealed Records)")
            st.caption(f"Latest Block Hash: `{verif.get('head_hash', 'N/A')}`")
        else:
            st.error(f"**Cryptographic Status:** ❌ TAMPER DETECTED: {verif['error']}")

    with col_v2:
        if readiness_score >= 95.0 and not st.session_state.period_locked:
            if st.button("🔒 Sign-Off & Lock Fiscal Period", type="primary", use_container_width=True):
                st.session_state.period_locked = True
                persist_workflow_state()
                st.session_state.audit_mgr.log_event(
                    event_type="PERIOD_LOCKED",
                    operator_name=controller_name,
                    operator_role=controller_role,
                    action_taken="PERIOD_FROZEN",
                    justification_memo="All accounting controls verified, adjustments committed, fiscal period 2026-10 frozen."
                )
                st.success("Fiscal period 2026-10 locked and frozen.")
                st.rerun()
        elif st.session_state.period_locked:
            st.info("Period 2026-10 is locked.")

    # Event log table
    if st.session_state.audit_mgr.records:
        st.markdown("#### Audit Event Stream")
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

        # Download buttons
        evidence_pack = st.session_state.audit_mgr.generate_statutory_evidence_pack(
            controls_summary=controls_list,
            staged_journals=st.session_state.posted_journals
        )
        st.download_button(
            label="📥 Download Full Audit Evidence Pack (JSON)",
            data=json.dumps(evidence_pack, indent=2),
            file_name="CLOSE_AI_Audit_Evidence_Pack_2026_10.json",
            mime="application/json"
        )

# ---------------------------------------------------------
# Tab 4: Pre vs. Post Close Trial Balance Comparison
# ---------------------------------------------------------
with tab_tb:
    st.subheader("General Ledger Trial Balance Reconciliation")
    st.caption("Verifying debit/credit equality across standard Norwegian SAF-T accounts before and after close adjustments.")

    con_tb = get_duckdb_connection(DATA_DIR)
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

    # Pre-close totals
    tot_dr = tb_df["debit_nok"].sum()
    tot_cr = tb_df["credit_nok"].sum()
    delta_pre = abs(tot_dr - tot_cr)

    col_tb1, col_tb2, col_tb3 = st.columns(3)
    with col_tb1:
        st.metric("Total Debits (Pre-Close)", f"{tot_dr:,.2f} NOK")
    with col_tb2:
        st.metric("Total Credits (Pre-Close)", f"{tot_cr:,.2f} NOK")
    with col_tb3:
        st.metric("Pre-Close Imbalance", f"{delta_pre:,.2f} NOK", delta="-15,000.00 NOK" if delta_pre > 0 else "Balanced", delta_color="inverse")

    st.markdown("#### Account Level Balances")
    tb_df_formatted = tb_df.copy()
    tb_df_formatted["debit_nok"] = tb_df_formatted["debit_nok"].apply(lambda x: f"{x:,.2f}")
    tb_df_formatted["credit_nok"] = tb_df_formatted["credit_nok"].apply(lambda x: f"{x:,.2f}")
    tb_df_formatted["net_balance_nok"] = tb_df_formatted["net_balance_nok"].apply(lambda x: f"{x:,.2f}")
    tb_df_formatted.columns = ["Account Number", "Debit (NOK)", "Credit (NOK)", "Net Balance (NOK)"]
    st.dataframe(tb_df_formatted, use_container_width=True, hide_index=True)
    con_tb.close()
