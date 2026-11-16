# CLOSE-AI: Autonomous Financial Close, Complex Reconciliation & Control Room Suite (v3.0)

A production-grade financial close, Adra reconciliation matcher, and audit control room engineered for engineering, maritime, and project-heavy organizations (exemplified by **Nordic Engineering Projects AS**). The solution combines deterministic accounting checks, combinatorial subset-sum matching, autonomous regex investigation, two-way interactive reconciliation lifecycle, Adra Balancer 4-way balance control formulation, and a cryptographic SHA-256 audit chain.

---

## Core Capabilities

- **4-Way Balance Control & Avstemmingsbro (Adra Balancer)**: Mathematical proof of $\mathbf{IB} + \sum \text{Periodens bevegelser} = \mathbf{UB}$ across general ledger and bank statements, isolating timing differences (Boks 1, 3, 4) and autonomous spin-off items (Boks 2) down to $\Delta = 0.00\text{ NOK}$.
- **FastAPI & DuckDB REST Backend (`api_server.py`)**: High-performance local backend exposing transactional REST endpoints for live DuckDB state queries, balance control calculations, multi-way matching, rollback unmatching, and SAF-T journal exports.
- **Unified Multi-Module Streamlit Cockpit (`app.py`)**: Seamless switching between the **Adra Balancer & Matcher Control Room**, the **Financial Controls & AI Audit Dossier**, or the **Unified Master Executive View**.
- **Multi-Period Ingestion Engine**: Native switching between fiscal periods (**August 2026** historical baseline, **September 2026** prior period cut-off, and **Oktober 2026** active close window) with CAMT.053 XML and SAFT CSV file upload simulation.
- **Reconciliation Rule Ladder (R-01 to R-AI)**: Prioritized execution hierarchy from 1:1 exact KID/OCR matching to combinatorial 1:M merchant batch settlement, multi-currency netting (agio/disagio), fuzzy vendor recognition, and R-SPINOFF autonomous voucher proposal.
- **Two-Way Interactive Lifecycle**: Full bidirectional workflow supporting manual multi-line matching (**"Avstem Valgte"**) and instant audit rollback (**"Opphev Avstemming / Unmatch"**) returning lines to open items in DuckDB.
- **Autonomous AI Copilot (`AIMatchSuggester`)**: Natural language forensic reasoning, root-cause diagnosis, and zero-delta balanced journal voucher proposals for complex exceptions (e.g. unapproved shipyard overtime under ISA 240/315).
- **Aging Analysis & IFRS 9 ECL Provisions**: Stratification of open balances into regulatory aging bands (0–30, 31–60, 61–90, 90+ days) with scenario toggles (*Standard*, *Konservativ*, *Stresstest*) and ISA 500 audit risk ratings.
- **Spin-Offs & Paired Accrual Vouchers**: Automated generation of balancing entries (fees, interest, currency diffs) and paired accruals (*Bilag A* period adjustment + *Bilag B* auto-reversal) with zero-delta validation and export in Norwegian SAF-T Financial XML, Dynamics 365 Business Central CSV, and Visma.net.
- **Cryptographic Governance (ISA 240 / 315)**: Immutable SHA-256 linear hash chain sealing every automated match, manual override, and voucher posting with on-click cryptographic chain verification.

---

## Repository Structure

```
AI Financial Close Room/
├── app/
│   ├── index.html                   # Aurora-styled Production Web Cockpit (v3.0)
│   ├── index_carbon.html            # Carbon-styled Enterprise Suite Web Cockpit
│   └── index_nordea_simulation.html # Nordea 10-Month Simulation Cockpit
├── config/
│   ├── pipeline_config.yaml         # Ingestion & system parameters
│   └── rules_config.json            # Externalized SQL control rules
├── data/
│   ├── audit_logs/                  # SHA-256 linear audit trail (JSONL)
│   ├── lakehouse/                   # Medallion Lakehouse Parquet files (Bronze/Silver/Gold)
│   ├── bank_nordea_2026_10.csv      # Nordea October 2026 statement extract
│   ├── bank_saldo_rapport_2026_10.json # Bank reconciliation report
│   ├── erp_hovedbok_2026_10.csv     # ERP Account 1925 GL extract
│   ├── erp_saldo_rapport_2026_10.json  # ERP GL balance report
│   ├── reconciliation.duckdb        # Main DuckDB analytical database (accounts, staging, views)
│   ├── reconciled_transactions.duckdb # Reconciled transactions database
│   └── unreconciled_transactions.duckdb # Open bank and ERP items database
├── erp_data_2026_10/                # Relational ERP datasets (10 Master & Transactional tables)
├── scripts/
│   ├── benchmark_matching_speed.py  # Latency & throughput benchmark
│   ├── generate_nordea_data.py      # Nordea bank & GL data generator script
│   ├── run_close_pipeline.py        # 5-stage close pipeline runner
│   └── setup_duckdb.py              # DuckDB database setup script
├── src/
│   ├── agent/                       # Regex agent, evidence graph, investigator
│   ├── api/                         # FastAPI backend implementation
│   ├── audit/                       # SHA-256 audit chaining & statutory evidence
│   ├── data_generator/              # Multi-table ERP & Nordea data synthesis
│   ├── engine/                      # Complex matcher, voucher generator, aging
│   ├── governance/                  # Audit logger & compliance
│   ├── lakehouse/                   # DuckDB medallion lakehouse & reconciliation manager
│   └── ml/                          # Scikit-learn Isolation Forest anomaly detector
├── tests/
│   ├── __init__.py                  # Test package marker
│   ├── test_complex_reconciliations.py # Multi-way matching unit tests
│   ├── test_control_room_duckdb.py  # DuckDB schemas, balance control & API tests
│   └── test_reconciliation_duckdb.py # DuckDB analytical views & RAG status tests
├── api_server.py                    # Root FastAPI entrypoint
├── app.py                           # Master Streamlit interactive control room
├── close-ai-v3-system-specification.md # Complete architectural specification
├── evaluate_controls.py             # DuckDB SQL deterministic rule evaluator
├── generate_erp_data.py             # ERP dataset generator convenience entrypoint
├── index.html                       # Aurora-styled single-page web cockpit
├── index_carbon.html                # Carbon-styled enterprise suite web cockpit
├── index_nordea_simulation.html     # Nordea simulation web cockpit
├── project_outline.md               # Business problem statement & deep dive
├── requirements.txt                 # Unified Python dependencies
├── run_server.bat                   # Batch launcher for FastAPI server
├── run_server.ps1                   # PowerShell launcher for FastAPI server
├── run_streamlit.bat                # Batch launcher for Streamlit application
├── setup_duckdb.py                  # Root DuckDB initialization script
└── test_close_system.py             # Master end-to-end integration test runner
```

---

## Verification & Execution

### 1. Run Complete Test Suite
```bash
# Discover and run all unit & integration test suites (19 tests)
python -m unittest discover -s tests

# Master end-to-end system integration test runner (17 tests)
python test_close_system.py
```

### 2. Launch FastAPI & DuckDB Backend Server
```bash
# Via Python directly
python api_server.py

# Or via Windows scripts
.\run_server.bat
# or in PowerShell:
.\run_server.ps1
```
The API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Launch Master Streamlit Control Room
```bash
# Via Python
streamlit run app.py

# Or via Windows batch
.\run_streamlit.bat
```
Navigate in the sidebar between:
- **📊 Adra Balancer & Matcher (DuckDB Lakehouse)**: 4-veis balansekontroll, åpne poster, og spin-off bilagsføring.
- **🔍 CLOSE-AI Financial Controls & Audit Dossier**: 10 deterministiske regler, Isolation Forest ML og revisjonsdossier.
- **🌐 Unified Executive Control Room**: Samlet oversikt med alle moduler aktive samtidig.

### 4. Web Application Cockpits
Open any of the single-page web cockpits directly in your browser:
- [index.html](file:///G:/My%20Drive/AI%20Financial%20Close%20Room/index.html) — Aurora Design System Master Cockpit
- [index_carbon.html](file:///G:/My%20Drive/AI%20Financial%20Close%20Room/index_carbon.html) — Carbon Design System Enterprise Suite
- [index_nordea_simulation.html](file:///G:/My%20Drive/AI%20Financial%20Close%20Room/index_nordea_simulation.html) — Nordea 10-Måneders Avstemmingssimulering
- Or via FastAPI: `http://127.0.0.1:8000/ui/aurora`, `http://127.0.0.1:8000/ui/carbon`, `http://127.0.0.1:8000/ui/nordea`

### 5. Run Close Pipeline & Performance Benchmarks
```bash
# Full 5-stage close execution (pre-match, spin-offs, aging, SHA-256 chain)
python scripts/run_close_pipeline.py

# High-volume throughput & latency benchmark
python scripts/benchmark_matching_speed.py
```
