# CLOSE-AI: Autonomous Financial Close & Audit Governance Control Room

[![Python 3.12]([suspicious link removed])]([suspicious link removed])
[![DuckDB]([suspicious link removed])]([suspicious link removed])
[![Streamlit]([suspicious link removed])]([suspicious link removed])
[![License: MIT]([suspicious link removed])](LICENSE)
[![Audit Compliance]([suspicious link removed])](#governance--audit-integrity)

> **CLOSE-AI** bridges the gap between operational ERP subledgers and statutory general ledger reporting. Designed specifically for mid-sized engineering and project-delivery enterprises (**Nordic Engineering Projects AS**), it combines **deterministic SQL accounting rules**, **unsupervised anomaly detection (Isolation Forest)**, and an **evidence-grounded LLM investigation agent** behind a strict **Human-in-the-Loop (HITL)** governance gate.

---

## 📌 Executive Summary & The Problem

Standard BI dashboards answer _"What were our numbers last month?"_—but only **after** books are closed and reconciliations are manually patched. They offer zero operational support for the intensive, error-prone close window that precedes the dashboard: answering **"Show me everything that might be wrong"** and **"Can we close the period?"**.

### Key Friction Points Solved:

1. **Disconnected Project Controlling & Subledgers:** Subcontractor claims, missing PO change orders, and unbilled milestone progress distort gross margin and EBITDA if not accrued prior to ledger locking.
2. **The "Black-Box" AI Hazard:** Large language models hallucinate arithmetic and cannot be trusted with write access to general ledgers.
3. **Statutory Audit Lineage:** External auditors require an unbroken chain of custody: every adjustment must trace directly from `Source Transaction` → `Rule/Model Detection` → `Investigation Evidence` → `Controller Approval`.

---

## 🏛️ Architectural Separation of Concerns

CLOSE-AI enforces four strict, non-negotiable architectural boundaries:

| Layer                             | Responsibility                                                                           | Technology / Mechanism                      |
| :-------------------------------- | :--------------------------------------------------------------------------------------- | :------------------------------------------ |
| **Deterministic Truth**           | Hard mathematical controls (Trial Balance, 3-Way Match, GR/IR aging, WIP checks).        | Python, DuckDB SQL, Parquet                 |
| **Statistical Outlier Detection** | Multi-dimensional behavioral anomaly detection (novel CC-vendor pairs, weekend packing). | Scikit-Learn (Isolation Forest)             |
| **Contextual Investigation**      | Gathers evidence chains across POs, WBS elements, and contracts; drafts proposed JVs.    | LLM Agent (Gemini Flash or local Llama 3.1) |
| **Authorization Gate (HITL)**     | Final human controller review, override, dispute routing, and ledger posting.            | Streamlit Cockpit, SHA-256 Hash Chaining    |

[Raw ERP Subledgers & GL Postings] │ ▼ ┌──────────────────────────────┐ ┌──────────────────────────────┐ │ Deterministic Controls │ │ Unsupervised ML │ │ (DuckDB SQL Engine) │ │ (Isolation Forest) │ │ • Zero Trial Balance delta │ │ • Multi-factor outliers │ │ • 3-Way PO tolerance check │ │ • Unusual posting hours │ │ • Duplicate invoice scan │ │ • Novel vendor-CC pairs │ └──────────────┬───────────────┘ └──────────────┬───────────────┘ │ │ └─────────────────┬──────────────────┘ ▼ [Exception & Anomaly Queue] │ ▼ ┌──────────────────────────────────┐ │ Scoped Investigation Agent │ │ (Gemini Flash / Ollama Llama 3.1)│ │ • Traverses Evidence Graph │ │ • Deduce Root Cause │ │ • Drafts Balanced Journal Entry │ └─────────────────┬────────────────┘ │ ▼ ┌──────────────────────────────────┐ │ Human-in-the-Loop Cockpit │ │ [Approve] [Edit] [Dispute] [Reject] │ • Cryptographic SHA-256 Chain │ └──────────────────────────────────┘

---

## ⚙️ Core Financial Controls (Deterministic Rules)

All controls are parameterized via `config/controls_config.yaml` with **zero hard-coded values in code**:

- **`CTRL-GL-01` [BLOCKER]: Zero Trial Balance Imbalance.** Enforces debits equal credits (\\(\Delta = 0.00\\) NOK). Any variance halts the close immediately.
- **`CTRL-GL-02` [HIGH]: Off-Hours & Weekend Manual Postings.** Scans manual entries posted on weekends or outside authorized operating windows.
- **`CTRL-AP-01` [HIGH]: Duplicate Vendor Invoices.** Identifies matching amounts, vendor IDs, and normalized invoice strings within a configurable lookback window.
- **`CTRL-AP-02` [HIGH]: Uninvoiced Goods Received (GR/IR).** Flags deliveries accepted at yard/site without corresponding vendor invoices or close accruals.
- **`CTRL-AP-03` [HIGH]: PO Price Tolerance Overrun.** Enforces 3-way match tolerances (flags variances \\(>10\%\\) without an approved change order).
- **`CTRL-PRJ-03` [HIGH]: Untagged Project Direct Costs.** Enforces strict WBS and project dimension tagging across direct cost accounts (`4000–4999`).

---

## 🔒 Governance & Audit Integrity

- **Zero Direct Write Access:** The AI agent can only write to a `staged_journal_proposals` table.
- **Cryptographic Hash Chaining:** Every controller approval, rejection, or edit is appended to a tamper-evident audit ledger using **SHA-256 linear hash chaining** (similar to a private blockchain).
- **Automated Audit Evidence Pack:** Generates complete audit dossiers including pre/post trial balances, rule execution metrics, and digital controller sign-off certificates conforming to **ISA 240 / 315 / 500** standards.

---

## 🚀 Quickstart & Installation

### Option A: Local Installation (Virtualenv)

```bash
# 1. Clone repository
git clone [suspicious link removed]
cd close-ai

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Set GEMINI_API_KEY if using cloud inference; Ollama works out of the box locally.

# 4. Generate synthetic ERP dataset with injected anomalies
python scripts/generate_synthetic_data.py

# 5. Run the CLI pipeline check
python scripts/run_close_pipeline.py --provider ollama --model llama3.1

# 6. Launch the Controller Control Room UI
streamlit run ui/app.py
Option B: Docker Compose (Full Stack with Local Ollama)
# Spin up both Streamlit Control Room and Ollama service
docker compose up -d --build

# Pull Llama 3.1 into the local Ollama container
docker exec -it close_ai_ollama ollama pull llama3.1

# Access the Cockpit UI in your browser:
# http://localhost:8501
🧪 Testing & Verification
Run the test suite to verify the deterministic financial controls and cryptographic audit integrity:
pytest tests/ -v
tests/test_deterministic_rules.py: Asserts zero-tolerance blockers, duplicate matching, and tolerance thresholds.
tests/test_audit_integrity.py: Simulates file tampering and asserts cryptographic detection.
📁 Repository Structure
close-ai/
├── config/
│   ├── controls_config.yaml         # Parameterized thresholds, tolerances & weights
│   ├── chart_of_accounts.yaml       # Dynamic account ranges & mapping rules
│   └── governance_policy.yaml       # Role RBAC, dual sign-off limits & audit rules
├── data/
│   ├── raw/                         # Ingested ERP extracts (Parquet / CSV)
│   ├── lakehouse/                   # DuckDB storage / Parquet partitions
│   └── audit_logs/                  # Cryptographically chained JSON-L audit trails
├── src/
│   ├── engine/
│   │   ├── control_evaluator.py     # Parameterized SQL rule runner
│   │   └── readiness_index.py       # Dynamic close readiness score calculator
│   ├── ml/
│   │   └── anomaly_detector.py      # Isolation Forest model & scoring engine
│   ├── agent/
│   │   ├── tools.py                 # Deterministic relational tools
│   │   ├── llm_client.py            # Dual client (Gemini Flash & Ollama Llama 3.1)
│   │   └── investigator.py          # Structured dossier generator
│   └── governance/
│       ├── hitl_gate.py             # Controller approval state machine
│       └── audit_logger.py          # SHA-256 hash-chained ledger logging
├── ui/
│   └── app.py                       # Streamlit Control Room Executive Cockpit
├── tests/
│   ├── test_deterministic_rules.py  # Unit tests for the 6 core financial controls
│   └── test_audit_integrity.py      # Tests for hash-chaining and immutability
├── scripts/
│   ├── generate_synthetic_data.py   # Synthetic ERP generator with injected anomalies
│   └── run_close_pipeline.py        # CLI orchestration runner
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
# AI-Closing
