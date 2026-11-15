# CLOSE-AI: Autonomous Financial Close, Complex Reconciliation & Balance Control Architecture (v3.0)

A production-grade financial close and audit control room engineered for engineering, maritime, and project-heavy organizations (exemplified by **Nordic Engineering Projects AS**). The solution combines deterministic accounting checks, combinatorial subset-sum matching, autonomous regex investigation, two-way interactive reconciliation lifecycle, Adra Balancer formulation, and a cryptographic SHA-256 audit chain.

## Core Capabilities (v3.0 Architecture)

- **Multi-Period Ingestion Engine**: Native switching between fiscal periods (**August 2026** historical baseline, **September 2026** prior period cut-off, and **Oktober 2026** active close window) with CAMT.053 XML and SAFT CSV file upload simulation.
- **Balansekontroll & Avstemmingsbro (Adra Balancer)**: Mathematical proof of $\mathbf{IB} + \sum \text{Periodens bevegelser} = \mathbf{UB}$ across general ledger and bank statement, isolating timing differences, unbooked items, and posting errors down to $\Delta = 0.00\text{ NOK}$.
- **Reconciliation Rule Ladder (R-01 to R-AI)**: Prioritized execution hierarchy from 1:1 exact KID/OCR matching to combinatorial 1:M merchant batch settlement, multi-currency netting (agio/disagio), and fuzzy vendor recognition.
- **Two-Way Interactive Lifecycle**: Full bidirectional workflow supporting manual multi-line matching (**"Avstem Valgte"**) and instant audit rollback (**"Opphev Avstemming / Unmatch"**) returning lines to open items.
- **Autonomous AI Copilot (`AIMatchSuggester`)**: Natural language forensic reasoning, root-cause diagnosis, and zero-delta balanced journal voucher proposals for complex exceptions (e.g. unapproved shipyard overtime under ISA 240/315).
- **Aging Analysis & IFRS 9 ECL Provisions**: Stratification of open balances into regulatory aging bands (0–30, 31–60, 61–90, 90+ days) with scenario toggles (*Standard*, *Konservativ*, *Stresstest*) and ISA 500 audit risk ratings.
- **Spin-Offs & Paired Accrual Vouchers**: Automated generation of balancing entries (fees, interest, currency diffs) and paired accruals (*Bilag A* period adjustment + *Bilag B* auto-reversal) with zero-delta validation and export in Norwegian SAF-T Financial XML, Dynamics 365 Business Central CSV, and Visma.net.
- **Cryptographic Governance (ISA 240 / 315)**: Immutable SHA-256 linear hash chain sealing every automated match, manual override, and voucher posting with on-click cryptographic chain verification.

---

## Repository Structure

```
AI Financial Close Room/
├── app/
│   └── index.html               # Production Single-Page Web Cockpit (v3.0)
├── config/
│   ├── pipeline_config.yaml     # Ingestion & system parameters
│   └── rules_config.json        # Externalized SQL control rules
├── data/
│   └── audit_logs/              # SHA-256 linear audit trail (JSONL)
├── erp_data_2026_10/            # Relational ERP datasets (Bronze/Silver/Gold)
├── scripts/
│   ├── benchmark_matching_speed.py  # Latency & throughput benchmark
│   └── run_close_pipeline.py    # 5-stage close pipeline runner
├── src/
│   ├── agent/                   # Regex agent, evidence graph, investigator
│   ├── audit/                   # SHA-256 audit chaining & statutory evidence
│   ├── data_generator/          # Multi-table ERP data synthesis
│   ├── engine/                  # Complex matcher, voucher generator, aging
│   ├── governance/              # Audit logger & compliance
│   ├── lakehouse/               # DuckDB medallion lakehouse pipeline
│   └── ml/                      # Scikit-learn Isolation Forest anomaly detector
├── tests/
│   └── test_complex_reconciliations.py # Multi-way matching unit tests
├── app.py                       # Streamlit interactive control room
├── close-ai-v3-system-specification.md # Complete architectural specification
├── evaluate_controls.py         # DuckDB SQL deterministic rule evaluator
├── generate_erp_data.py         # ERP dataset generator
├── index.html                   # Synchronized web entrypoint
├── project_outline.md           # Business problem statement & deep dive
├── requirements.txt             # Python dependencies
└── test_close_system.py         # End-to-end integration test suite
```

---

## Verification & Execution

### 1. Web Application Cockpit
Open [app/index.html](file:///c:/Users/frank/Desktop/AI%20Financial%20Close%20Room/app/index.html) or [index.html](file:///c:/Users/frank/Desktop/AI%20Financial%20Close%20Room/index.html) in any modern browser to launch the full CLOSE-AI Control Room.

### 2. Run Test Suites
```bash
# Unit & Multi-Way Reconciliation Tests
python -m unittest discover -s tests

# End-to-End System Integration Tests
python test_close_system.py
```

### 3. Run Close Pipeline & Performance Benchmarks
```bash
# Full 5-stage close execution (Adra pre-match, spin-offs, aging, SHA-256 chain)
python scripts/run_close_pipeline.py

# High-volume throughput & latency benchmark
python scripts/benchmark_matching_speed.py
```

### 4. Run Streamlit Cockpit
```bash
streamlit run app.py
```
