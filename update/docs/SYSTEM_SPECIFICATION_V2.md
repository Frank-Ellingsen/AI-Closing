# CLOSE-AI: Complete Autonomous Financial Close & Complex Reconciliation Engine (v2.0)

## 1. Executive Summary & Evolution (2006 vs. 2026)

In 2006, leading treasury and investment management teams (such as KLP Kapitalforvaltning with 350 bank accounts across 30 currencies) pioneered automated reconciliation by using **Adra Matcher** and scripted SQL spin-offs to reconcile SimCorp Dimension against SAP, reaching 99% automated matching.

Twenty years later, **CLOSE-AI (v2.0)** transforms this foundation from scheduled rule batches into an **autonomous, agentic, continuous close operating system**. It resolves the stubborn exceptions that break traditional spreadsheets:
* **Asymmetric Cardinalities:** 1:Many (batch payouts with net deductions), Many:1 (split payments), and Many:Many (intercompany netting with bank float).
* **Two-Stage Lifecycle:** Explicit separation between **Pre-Match (Staging & Heuristics)** and **Final Match (Hard Clearing & Cryptographic Freeze)**.
* **Autonomous Regex Agent:** Tokenizes messy bank descriptions and induces new extraction patterns when vendor formats change.
* **Spin-Offs & Paired Bilag:** Automatically balances variable fees, interest, and agio into ready-to-post journal vouchers (Bilag A: 31.10) with paired auto-reversals (Bilag B: 01.11).
* **Aging Analysis (Aldersfordelte Poster):** Categorizes open items into 0-30, 31-60, 61-90, and 90+ days, projecting loss provisions and raising audit risk alerts.

---

## 2. Architecture & Directory Layout

```
close_ai_v2/
├── src/
│   ├── agent/
│   │   └── regex_agent.py          # Tokenizer & autonomous pattern synthesis
│   ├── engine/
│   │   ├── models.py               # Dataclasses (Transactions, Vouchers, Aging)
│   │   ├── complex_matcher.py      # Pre-Match, Final Match & Subset-Sum solver
│   │   ├── voucher_generator.py    # Spin-offs, paired bilag, SAF-T XML & CSV export
│   │   └── aging_analyzer.py       # Aging analysis (0-30 to 90+ days) & provisions
│   └── governance/
│       └── audit_logger.py         # Append-only SHA-256 linear hash chain
├── scripts/
│   ├── run_close_pipeline.py       # End-to-end 5-stage pre-close CLI runner
│   └── benchmark_matching_speed.py # High-volume latency & throughput benchmark
├── tests/
│   └── test_complex_reconciliations.py # Comprehensive unit test suite
├── docs/
│   └── SYSTEM_SPECIFICATION_V2.md # Complete architectural reference
└── README.md
```

---

## 3. The 4 Complex Multi-Way Reconciliation Scenarios

1. **1:Many Merchant Batch Settlement with Hidden Interchange Fees:**
   * Target deposit: `89,512.50 NOK` matches 4 subledger invoices totaling `91,550.00 NOK`.
   * The `RegexAgent` extracts batch ID `88491`.
   * Combinatorial subset-sum isolates `2,037.50 NOK` as an authorized processing fee (`Konto 7770`), yielding `Delta = 0.00 NOK`.
2. **Multi-Way 4-Party Yard EPC Matching (PO vs. GRN vs. Invoice vs. CCO):**
   * Subsea manifold package (`PO-8809` on `PRJ-001.03.FAB`).
   * Delivers `670,000 NOK` approved leg, rejects `80,000 NOK` coating, and flags `145,000 NOK` unauthorized overtime.
3. **Many:Many Intercompany Netting with Spot FX & Bank Float:**
   * Oslo HQ bills Aberdeen in GBP over the month (`1,750,420 NOK` GL value).
   * Aberdeen settles `£125,000` wire arriving 4 days later (`1,724,110 NOK`).
   * Multi-currency window matches GBP balance and auto-generates `26,310 NOK` currency loss bilag (`Konto 8160`).
4. **Noisy Scanned Remittance Advice with Prompt Payment Discounts:**
   * OCR parses truncated invoice strings (`INV-90412`, `INV-90413`, `CR-11`).
   * Bipartite matching calculates the 2% discount (`Konto 8150`) and highlights unearned supplier deductions.

---

## 4. Spin-Off & Paired Bilag Contracts

### Spin-off Voucher (Bank Fee Auto-Post)
* **Debet:** `Konto 7770` (Bank- og transaksjonsgebyr)
* **Kredit:** `Konto 1920` (Bankinnskudd drift)
* **Validering:** `Debet == Kredit` (Delta = 0.00 NOK)

### Paired Accrual Bundle (Year/Month-End Adjusting Entry)
* **Bilag A (Periodejustering, 31.10.2026):**
  * Debet: `4100` (Fremmedytelse/Underentreprise)
  * Kredit: `2440` (Påløpt kostnad / Ikke mottatt faktura)
* **Bilag B (Autoreversering, 01.11.2026):**
  * Debet: `2440` (Påløpt kostnad)
  * Kredit: `4100` (Fremmedytelse)

---

## 5. Aging Analysis & Provisioning (IFRS 9 / ISA 500)

| Kategori | Dager | Avsetningssats | Revisjonsrisiko | Anbefalt Aksjon |
| :--- | :---: | :---: | :---: | :--- |
| **0–30 dager** | 0–30 | 0% | `LOW` | Ordinær oppfølging |
| **31–60 dager** | 31–60 | 2% | `MEDIUM` | Første purrerunde |
| **61–90 dager** | 61–90 | 10% | `HIGH` | Prosjektlederbekreftelse kreves |
| **90+ dager** | > 90 | 40% | `CRITICAL` | Vurderes for formell tapsavsetning |

---

## 6. Execution & Verification Commands

```bash
# 1. Run unit test suite
python3 -m unittest discover -s tests

# 2. Run automated pre-close pipeline CLI
python3 scripts/run_close_pipeline.py

# 3. Run high-volume throughput benchmark
python3 scripts/benchmark_matching_speed.py
```
