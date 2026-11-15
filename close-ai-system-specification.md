# CLOSE-AI: Dynamic, Auditable Financial Close & Exception Governance Architecture

The modern financial month-end close is frequently characterized by operational friction, manual detective work, and fragmented subledger reconciliations. Traditional enterprise reporting and business intelligence architectures operate retrospectively: they present metrics and performance dashboards only after records have been manually reconciled, adjusted, and closed. This architectural design leaves corporate controllers unassisted during the critical window preceding the dashboard, where the essential operational questions are not *"What were the historical numbers?"*, but rather *"What balances are exposed to error?"* and *"Can the fiscal period be safely closed?"*.

The CLOSE-AI architecture establishes an autonomous, controlled financial operations framework engineered for project-driven enterprises. By enforcing strict separation between deterministic accounting calculations, statistical anomaly detection, agentic reasoning, and human authorization, the platform accelerates period closing while establishing an unbroken, tamper-evident audit lineage.

---

## 1. System Vision & The Pre-Dashboard Finance Operating Model

Corporate accounting mandates uncompromising precision, deterministic math, and compliance with statutory standards. Applying artificial intelligence within core finance has historically faltered because standard machine learning and generative models operate probabilistically. An unconstrained language model cannot be entrusted with accounting calculations, nor can autonomous software be permitted write access to general ledger tables without violating international auditing standards.

The CLOSE-AI operating model addresses this challenge by shifting artificial intelligence from an unconstrained calculator to an evidentiary investigator operating within a transparent glass-box architecture.

* **Raw ERP Subledgers & Bank Feeds:** Continuously captured into an immutable data lakehouse.
* **Dynamic Data Lakehouse (Raw → Silver → Gold):** In-memory analytical processing via DuckDB.
* **Dual Inspection Engines:**
  * **Deterministic Controls Engine:** Executes parameterized SQL rules enforcing hard double-entry invariants.
  * **Statistical Machine Learning Engine:** Unsupervised Isolation Forest detecting multivariate outliers.
* **Exception Candidate Stream:** Aggregates all flagged rule violations and statistical anomalies.
* **AI Investigation Agent:** Explores the Controller Evidence Graph to assemble root-cause evidence dossiers.
* **Staged Journal Proposals:** Generates pre-populated adjusting entries for human evaluation.
* **Human-in-the-Loop Gate:** Authorized controllers approve, edit, dispute, or reject proposals.
* **General Ledger Commit & Cryptographic Audit Pack:** Direct ledger posting with unbroken lineage hashing.

The system establishes an absolute separation of functional responsibilities across four distinct architectural tiers:

* **Deterministic Truth (Python & DuckDB SQL):** Executes core double-entry bookkeeping reconciliations, three-way matching, trial balance verification, and statutory tax clearing. Mathematical operations remain strictly code-governed; the language model never computes ledger totals.
* **Statistical Anomaly Detection (Scikit-Learn Isolation Forest):** Identifies multivariate behavioral outliers, unusual categorical pairings, and threshold-avoidance patterns across multi-dimensional transaction volumes without assuming static rules.
* **Investigative Reasoning (Agentic Language Model):** Synthesizes contextual data across the operational evidence graph, diagnoses operational root causes, evaluates financial exposure, and drafts standardized journal voucher proposals.
* **Executive Authorization (Human Controller):** Retains sole authority to approve, amend, or reject staged transactions. The system prevents autonomous write operations to production ledgers.

---

## 2. Organizational Entity Blueprint: Nordic Engineering Projects AS

To ensure the control architecture reflects enterprise realities, the reference data structure models Nordic Engineering Projects AS, a mid-sized Norwegian engineering, procurement, construction, installation, and commissioning contractor operating in the North Sea energy and Nordic civil infrastructure sectors.

### 2.1. Structural Complexity & Operating Divisions

Engineering contractors combine fixed-price lump-sum deliverables with reimbursable time-and-materials services and internal capital expenditure programs. This multi-contract environment creates structural accounting friction between physical project progress and the general ledger.

The operational structure spans four divisions and specialized cost centers:

* **DIV-OFF: Offshore Energy & Renewables**
  * `CC-1100`: Subsea Engineering & Design
  * `CC-1200`: Heavy Fabrication Yard & Mobilization
* **DIV-INF: Civil Infrastructure & Marine**
  * `CC-2100`: Tunnels & Structural Engineering
  * `CC-2200`: Site Operations & Assembly
* **DIV-SER: Specialized Engineering Consultancy**
  * `CC-3100`: FEA Simulation & Technical Advisory
* **DIV-CORP: Shared Services & Corporate Governance**
  * `CC-9000`: Finance & Close Operations
  * `CC-9100`: Executive & Administration

### 2.2. The Relational Backbone

The enterprise schema enforces relational integrity from upstream commercial contracts down to the financial ledger lines:

$$\text{Customer} \longrightarrow \text{Project} \longrightarrow \text{WBS Element} \longrightarrow \text{Purchase Order} \longrightarrow \text{PO Line} \longrightarrow \text{Vendor Invoice} \longrightarrow \text{GL Journal Line} \longrightarrow \text{Cost Center}$$

This lineage ensures that every recorded cost or accrual can be traced backward to a physical deliverable and purchase commitment, and forward to management EBITDA and statutory financial statements.

---

## 3. Dynamic Lakehouse Architecture: Raw to Semantic Layer

A key engineering requirement is the elimination of hard-coded paths, static schemas, and fixed thresholds. The platform organizes ingestion through a metadata-driven lakehouse pipeline utilizing DuckDB and Apache Parquet.

### 3.1. Medallion Storage Progression

The data pipeline transitions operational ERP exports through three distinct analytical tiers:

1. **Bronze Layer (Raw Ingestion):** Stores immutable snapshots of source ERP tables (General Ledger, Accounts Payable, Accounts Receivable, Purchase Commitments, Goods Receipts, Timesheets, and Master Entities) in append-only Parquet partitions. Every ingested record includes source system timestamps, batch IDs, and ingestion hashes.
2. **Silver Layer (Normalized & Cleaned):** Enforces data contracts, harmonizes multi-currency transactions into the functional reporting currency (NOK), standardizes date formats, cleans accounting dimension keys, and casts values into high-precision numeric types ($DECIMAL(18,4)$) to prevent floating-point rounding errors.
3. **Gold Layer (Finance Semantic Layer):** Assembles denormalized analytical models optimized for control queries and anomaly detection. Key structures include `fact_gl_postings`, `fact_ap_invoices`, `fact_po_commitments`, and dimensional hierarchies for accounts, projects, WBS elements, vendors, and cost centers.

### 3.2. Configuration-Driven Pipeline Specification

To avoid hard-coded logic, ingestion parameters and data contract definitions are externalized into declarative configuration manifests:

```yaml
# pipeline_config.yaml
pipeline_version: "2.1.0"
fiscal_entity: "Nordic Engineering Projects AS"
functional_currency: "NOK"
lakehouse_root: "data/lakehouse"

data_contracts:
  gl_journal_lines:
    required_keys: ["entry_id", "line_id", "account_number", "debit_nok", "credit_nok"]
    numeric_precision: 4
    allow_null_dimensions:
      direct_cost_accounts: false
      balance_sheet_accounts: true

currency_normalization:
  fx_rates_source: "silver/dim_fx_rates.parquet"
  supported_currencies: ["NOK", "EUR", "USD", "GBP"]
```

---

## 4. Deterministic Financial Controls Engine & Rules Matrix

Before statistical models or generative agents inspect the ledger, the deterministic control engine executes a battery of automated accounting proofs. These controls enforce mathematical certainty and statutory accounting standards.

### 4.1. Rules-as-Data Architecture

Control definitions are decoupled from execution logic. Each control is declared as a structured configuration record containing its identification code, target domain, validation query, threshold parameters, execution weight, and severity rating.

```json
{
  "control_id": "CTRL-GL-01",
  "control_name": "Zero Trial Balance Imbalance",
  "domain": "GENERAL_LEDGER",
  "severity": "BLOCKER",
  "weight": 25,
  "parameterized_sql": "SELECT ROUND(ABS(SUM(debit_nok) - SUM(credit_nok)), 2) AS delta FROM gl_journal_lines WHERE period_id = :period",
  "pass_condition": "delta == 0.00",
  "fail_action": "ENFORCE_PERIOD_FREEZE"
}
```

### 4.2. Core Accounting Control Matrix

The suite evaluates operational integrity across six primary functional dimensions:

| Control Identifier | Functional Scope | Primary Audit Risk | Deterministic Logic & Threshold | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **CTRL-GL-01** | General Ledger | Unbalanced Ledger Entries | $\left\|\sum \text{Debits} - \sum \text{Credits}\right\| = 0.00 \text{ NOK}$. Delta $\neq 0$ blocks ledger closing. | **BLOCKER** |
| **CTRL-GL-02** | General Ledger | Unauthorized Off-Hours Postings | Manual journal entries logged during weekends (Saturday/Sunday) or outside standard operating hours. | **HIGH** |
| **CTRL-AP-01** | Accounts Payable | Duplicate Vendor Disbursements | Invoices sharing identical vendor ID, matching amount ($\pm 0.01$), and posting dates within 14 calendar days. | **HIGH** |
| **CTRL-AP-02** | Procurement / AP | Uninvoiced Goods Received (GR/IR) | PO lines marked delivered with positive received quantity lacking corresponding invoice after 30 days. | **HIGH** |
| **CTRL-AP-03** | Procurement / AP | Three-Way Match Tolerance Breach | Invoiced line amount exceeding authorized purchase order commitment by more than 10.0%. | **HIGH** |
| **CTRL-PRJ-03**| Project Control | Missing Cost Allocation Dimensions | Direct project expenses (Accounts 4000–4999) posted without mandatory Project ID or WBS tags. | **HIGH** |

### 4.3. The Close Readiness Index Formulation

The platform synthesizes control outcomes into an aggregate readiness score:

$$\text{Readiness Index (\%)} = \left( \frac{\sum_{i \in \text{Passed Controls}} \text{Weight}_i}{\sum_{j \in \text{All Controls}} \text{Weight}_j} \right) \times 100$$

The governance engine applies a strict override hierarchy: if **any control classified as a BLOCKER** evaluates to `FAIL`, the system status is locked to **`CLOSE BLOCKED`**, regardless of whether the calculated index exceeds 95%. Formal sign-off is programmatically disabled until blockers are resolved.

---

## 5. Multivariate Statistical Anomaly Detection (Isolation Forest)

While deterministic rules effectively capture known violation patterns, they remain blind to subtle structural anomalies—such as fragmented invoices designed to circumvent authorization limits, novel vendor-to-cost-center pairings, or atypical posting timings.

An unsupervised machine learning layer complements the rule engine by scoring multidimensional outliers across the transaction population.

### 5.1. Model Design & Feature Matrix

The pipeline utilizes an Isolation Forest algorithm (`sklearn.ensemble.IsolationForest`). Isolation forests are mathematically suited for financial tabular data because they recursively isolate anomalies through orthogonal feature splits without relying on labeled training data or assuming normal distribution shapes.

The feature engineering layer dynamically transforms raw ledger lines into an eleven-dimensional normalized vector:

* **Amount Transformations:** Logarithmic scaling $\ln(\text{amount\_nok} + 1)$ to manage positive skewness.
* **Account Relative Variance:** Account Z-score $(x - \mu_{\text{acct}}) / \sigma_{\text{acct}}$ identifying uncharacteristic balances.
* **Cost Center Exposure:** Cost center Z-score $(x - \mu_{\text{cc}}) / \sigma_{\text{cc}}$ detecting abnormal departmental charges.
* **Cyclical Temporal Context:** Sine and cosine mappings of posting hours $\sin(2\pi h / 24)$ and $\cos(2\pi h / 24)$.
* **Operational Timing:** Weekend indicators and countdown of days remaining until the month-end closing window.
* **Relational Co-Occurrence:** Historical vendor frequency score per cost center, detecting novel vendor routing.
* **Forensic Number Tests:** Benford's Law first-digit log-likelihood deviation and round-thousand transaction flags.

### 5.2. Anomaly Scoring Calibration

The raw isolation tree depth is converted into an explainable anomaly score ranging from 0 to 100:

* **Score 0–64 (Inlier Band):** Normal operational transaction; passes directly to reporting tables.
* **Score 65–84 (Monitoring Band):** Atypical transaction characteristics; routed to the controller's secondary review queue.
* **Score 85–100 (Outlier Band):** Critical multivariate anomaly; automatically dispatched to the agentic investigation layer with high execution priority.

---

## 6. The Autonomous Controller Investigation Agent & Evidence Graph

When an exception is flagged, corporate controllers spend substantial administrative time compiling supporting documentation across disparate systems. The CLOSE-AI investigation agent acts as an automated forensic assistant, gathering evidence and assembling structured dossiers.

### 6.1. The Controller Evidence Graph

Rather than executing unconstrained text queries, the agent navigates a formal operational graph linking accounting records to physical documentation:

* Upstream: Links vendor invoices back through purchase orders, delivery receipts, and contract terms.
* Cross-Dimensional: Connects general ledger lines with work breakdown structures (WBS) and project milestones.
* Downstream: Traces proposed adjustments to trial balance impacts and management EBITDA variances.

By querying this graph deterministically, the agent retrieves the complete transactional pedigree: purchase authorizations, delivery sign-offs, previous vendor billing baselines, and project budget variances.

### 6.2. Structured Dossier Format

To maintain transparency and eliminate conversational ambiguity, every agent evaluation emits a standardized dossier:

```
INVESTIGATION DOSSIER: INV-2026-10-0042
Target Entity: Invoice INV-VEND-99214 | Vendor: Nordic Subsea Fabrication AS

1. OBSERVATION
   Vendor invoiced 820,000.00 NOK on WBS PRJ-2026-001.03.FAB. 
   Represents a 150,000.00 NOK (+22.4%) cost overrun against authorized commitment.

2. EVIDENCE CHAIN
   • PO Commitment: PO-8801 authorized for 670,000.00 NOK (Subsea manifold frame).
   • Physical Delivery: Yard receipt GR-4412 confirms delivery on 2026-10-24.
   • Invoicing: INV-99214 received 2026-10-29 citing 'Unscheduled yard overtime'.
   • Change Order Verification: Project register contains no approved Client Change Order (CCO).

3. ROOT CAUSE
   Subcontractor billed overtime hours without a formal PO variation order or approved client recharge.

4. FINANCIAL EXPOSURE
   • Gross margin erosion: 150,000.00 NOK unbudgeted direct project cost.
   • Cash impact: Immediate liquidity outflow if approved via standard payment run.

5. RECOMMENDED ACTION & PROPOSED JOURNAL VOUCHER
   • Action: Hold disputed variance; accrue authorized delivery to protect period close.
   • Staged Journal Voucher:
       Debit:  Account 4100 (Direct Yard Labor)       670,000.00 NOK [WBS: PRJ-2026-001.03.FAB]
       Credit: Account 2440 (Accrued Liabilities)     670,000.00 NOK [WBS: PRJ-2026-001.03.FAB]
   • Dispute Routing: Flag 150,000.00 NOK to Project Manager for vendor negotiation.
```

---

## 7. Ethical Governance, Safety Guardrails & Human-in-the-Loop State Machine

Financial accounting requires verifiable human accountability. Entrusting automated software with unilateral ledger write permissions violates international corporate governance standards and statutory requirements.

### 7.1. Ethical & Safety Guardrails

The platform adheres to four mandatory ethical principles:

1. **Principle of Non-Autonomous Posting:** The AI agent possesses read-only access to subledgers and write access strictly to a staging table (`staged_journal_vouchers`). It cannot execute SQL `INSERT` or `UPDATE` operations against active financial tables.
2. **Principle of Explainable Attribution:** The system prohibits opaque assertions. Every finding must explicitly reference concrete source records, contract clauses, or control definitions.
3. **Principle of Deterministic Integrity:** The language model is forbidden from computing balances, multiplying exchange rates, or calculating tax amounts. All figures presented in proposals derive from verified code execution.
4. **Principle of Role-Based Separation:** Personnel reviewing exceptions cannot approve entries beyond their statutory authorization limits. Period-end closure requires two-person authorization.

### 7.2. State Machine Lifecycle

Every identified exception and adjustment progresses through an audited state sequence:

1. **Exception Detected:** Control breach or ML outlier triggers event ingestion.
2. **Dossier & Voucher Staged:** Investigation agent compiles evidence and stages journal entry as `PROPOSED`.
3. **Controller Review & Gate:**
   * **Approve:** Advances state to `APPROVED`, committing entry to ledger.
   * **Edit:** Controller adjusts accounts or figures, advancing state to `EDITED` with mandatory justification notes.
   * **Hold / Dispute:** Temporarily freezes entry, advancing state to `ON_HOLD` and generating an operational ticket.
   * **Reject:** Advances state to `REJECTED`, logging the formal dismissal rationale.
4. **Committed to Ledger:** Approved transactions post to the general ledger, updating real-time trial balances.
5. **Cryptographic Sealing:** An immutable audit event is appended to the system ledger log.

---

## 8. Unbroken Lineage, Cryptographic Logging & Audit Evidence Packs

Auditing standards (ISA 240, ISA 315, ISA 500, and Nordic SAF-T regulations) demand that financial adjustments be verifiable by third-party auditors. CLOSE-AI guarantees complete traceability by recording an immutable audit log.

### 8.1. Cryptographic Record Structure

Each controller action generates a signed audit record sealed with a secure hash algorithm ($SHA\text{-}256$):

```json
{
  "audit_event_id": "AUD-2026-10-31-0982",
  "timestamp_utc": "2026-10-31T18:42:15Z",
  "fiscal_period": "2026-10",
  "event_type": "JOURNAL_VOUCHER_POSTED",
  "journal_id": "JV-2026-10-0042",
  "operator": {
    "user_id": "ctrl_frank_e",
    "name": "Frank Ellingsen",
    "role": "Lead Project Controller",
    "auth_session": "AUTH-TOKEN-99824-SEC"
  },
  "action_taken": "APPROVED_WITHOUT_EDIT",
  "originating_investigation_id": "INV-2026-10-0042",
  "triggering_control": "CTRL-AP-03",
  "financial_lines": [
    {"account": "4100", "debit_nok": 670000.00, "credit_nok": 0.00, "wbs": "PRJ-2026-001.03.FAB"},
    {"account": "2440", "debit_nok": 0.00, "credit_nok": 670000.00, "wbs": "PRJ-2026-001.03.FAB"}
  ],
  "justification_memo": "Accrued 100% of delivered fabrication per GR-4412. Disputed overrun held pending change order.",
  "parent_record_hash": "b2f4c...91a2",
  "current_record_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

### 8.2. The Month-End Audit Evidence Pack

Upon formal closure of the fiscal period, the system compiles the definitive Audit Evidence Pack:

* **Pre-Close & Post-Close Trial Balance:** Side-by-side reconciliation confirming net zero ledger balance and complete mathematical alignment.
* **Deterministic Verification Log:** Complete execution history of all six controls, including timestamps and evaluated SQL queries.
* **Anomaly Risk Register:** Comprehensive distribution of Isolation Forest scores across all posted subledger lines.
* **Approved Adjustments Dossier:** Detailed compilation of every staged journal voucher, including source POs, delivery receipts, agent observations, and electronic controller signatures.
* **Period Lock Attestation:** Digital certificate freezing the Gold ledger layer for the closed period.

---

## 9. Technical Implementation & Deployment Roadmap

The platform deployment roadmap balances rapid operational delivery with enterprise reliability. The system matures through five sequential iterations:

* **V0.1: Synthetic ERP Generator:** Data contracts, master entities, transaction synthesis, and injected ground-truth anomalies.
* **V0.2: Lakehouse & Semantic Layer:** Raw to Silver to Gold Parquet transformations with in-memory DuckDB query execution.
* **V0.3: Deterministic & ML Control Engines:** Rules-as-data SQL evaluation, Isolation Forest feature pipeline, and Close Readiness Index calculation.
* **V0.4: Agentic Investigation & HITL Cockpit:** Controller Evidence Graph traversal, automated dossier assembly, and Streamlit approval gate.
* **V1.0: Cryptographic Audit Trail & Statutory Packaging:** SHA-256 lineage logging, SAF-T export formatting, and executive management reporting.

By adhering to this phased implementation, the organization transitions from retrospective reporting to proactive, controlled, and verifiable financial close operations.
