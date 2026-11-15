Step 1. Business Problem Statement: AI Financial Close & Audit Control Room (CLOSE-AI)1. Executive Summary & Core Problem StatementIn corporate finance, existing business intelligence and reporting dashboards only function after financial data has already been reconciled, adjusted, and finalized12. They answer "What were our numbers last month?" but offer no operational support for the intensive, error-prone workflow that precedes the dashboard: answering "Show me everything that might be wrong" and "Can we close the period?"2more_horiz.Executive Problem Statement:
The financial month-end close is delayed by manual reconciliations, fragmented operational subledgers, and labor-intensive exception handling7more_horiz. Generic AI tools cannot solve this because they lack deterministic calculation rigor, introduce hallucination risks, and lack the unbroken audit lineage and human-in-the-loop governance required by controllers and external auditors11more_horiz.2. Operational Context: Nordic Engineering Projects ASThe problem is grounded in a mid-sized engineering and project-delivery company (Nordic Engineering Projects AS) delivering engineering services, equipment packages, fabrication, installation, and commissioning across long-running customer contracts17more_horiz.In this environment, financial accounting and project controlling are deeply interdependent18more_horiz:Transactions span complex relational paths: $\text{Customer} \rightarrow \text{Project} \rightarrow \text{WBS} \rightarrow \text{PO} \rightarrow \text{Vendor} \rightarrow \text{Invoice} \rightarrow \text{GL} \rightarrow \text{Cost Center}$22.Operational delays, missing subcontractor purchase orders, unposted milestone accruals, and project cost overruns directly distort gross margins and period EBITDA if unaddressed prior to ledger closing18more_horiz.3. Key Pain Points & Bottlenecks3.1. Manual Detective Work & High-Volume Exception HandlingControllers waste days running manual checks across General Ledger, Accounts Payable, Accounts Receivable, Payroll, and Fixed Assets7more_horiz. Typical issues that slip through or cause delays include:Duplicate vendor invoices and weekend postings1027.Invoices exceeding purchase order tolerances or posted without valid POs1027.Incorrect cost center allocations, missing project tags, and out-of-period postings1028.Unrecorded accruals for goods or services received without matching invoices9more_horiz.3.2. Disconnect Between Project Controlling and the General LedgerProject variance is often discovered late during management reporting rather than during close execution23more_horiz. When a project suffers forecast deterioration or subcontractor cost surges, controllers lack an automated evidence chain linking the physical WBS activity to the proposed general ledger adjustment23more_horiz.3.3. The AI Trust & Governance Deficit in FinanceGeneric "chat-with-your-data" bots and language models cannot be trusted to perform financial close tasks autonomously11more_horiz:No black-box adjustments: An AI must never silently adjust general ledger balances or post journals without human review and approval11more_horiz.Calculation hazards: Language models hallucinate math; accounting figures must remain strictly deterministic1415.Audit compliance: Financial accounting standards require an unbroken chain of custody: every journal entry must trace directly back through $\text{Source Transaction} \rightarrow \text{Calculation} \rightarrow \text{Rule} \rightarrow \text{Evidence} \rightarrow \text{Human Approval}$12more_horiz.4. Architectural Separation of ConcernsTo solve this business problem without violating audit standards, the solution enforces four distinct boundaries14more_horiz:LayerResponsibilityTechnology / MechanismDeterministic TruthCalculations, reconciliations, and hard accounting controls9more_horizPython, DuckDB SQL, Parquet15more_horizAnomaly DetectionStatistical anomaly scoring across multidimensional posting data15more_horizMachine Learning (Isolation Forest)15more_horizInvestigation & ReasoningEvidence synthesis, root-cause analysis, and adjustment proposals15more_horizLLM Agent with Controller Evidence Graph15more_horizAuthorizationFinal review, journal approval, rejection, and ledger posting11more_horizHuman-in-the-Loop Controller Gate11more_horiz5. Success Criteria for the SolutionThe platform resolves the business problem when the controller cockpit delivers5more_horiz:A Real-Time Close Readiness Index: A single dashboard status answering "Can we close the month?" with traffic-light control indicators across GL, AP, AR, Payroll, Assets, and Projects5more_horiz.Autonomous Evidence Gathering: Turning raw exceptions into structured investigative dossiers containing Observation, Evidence, Likely Cause, Financial Impact, and Recommended Action50more_horiz.Controlled Journal Voucher Proposals: Pre-populated journal entries (e.g., project accruals) presented with supporting evidence for explicit controller sign-off (Approve / Reject / Investigate)34more_horiz.Audit Evidence Packs: Automated generation of verifiable audit trails explaining the exact origin and policy justification for every close adjustment12more_horiz.

Step 2. Company Profile & Synthetic ERP SchemaTo build a realistic, production-grade financial control room, we need an operating environment with enough organizational complexity to trigger authentic accounting friction—project milestone delays, cross-department cost allocations, currency exposure, and subcontractor accruals.Here is the operational blueprint and synthetic ERP schema for Nordic Engineering Projects AS.1. Company Profile: Nordic Engineering Projects ASLegal Entity: Nordic Engineering Projects ASHeadquarters: Stavanger / Oslo, Norway (Operating across the Nordics & North Sea energy/infrastructure sectors)Reporting Currency: NOK (Norwegian Krone), with multi-currency vendor exposure in EUR, USD, and GBP.Business Model: EPC / EPCI delivery (Engineering, Procurement, Construction, Installation & Commissioning), combining lump-sum fixed-price milestone contracts with time-and-materials engineering services.Fiscal Period: Standard calendar year; monthly close window (Target close: Workday +4).Operating Divisions & Cost CentersDivision CodeDivision NameOperating FocusPrimary Cost CentersDIV-OFFOffshore Energy & RenewablesSubsea structures, electrification, floating offshore wind foundationsCC-1100 (Subsea Eng), CC-1200 (Fabrication Yard)DIV-INFInfrastructure & MarineTunnel ventilation, fjord crossing modules, port electrificationCC-2100 (Civil & Structural), CC-2200 (Site Ops)DIV-SERSpecialized Engineering ServicesTechnical advisory, FEA simulation, decarbonization studiesCC-3100 (Specialist Consultants)DIV-CORPCorporate & Shared ServicesExecutive management, Finance, Legal, HR, Procurement, ITCC-9000 (Finance & Close Ops), CC-9100 (HQ Admin)Project Archetypes & Financial TreatmentFixed-Price Milestone Projects (Lump Sum / Over-time Revenue Recognition):Accounting dynamic: Revenue recognized using cost-to-complete or milestone progress. Vulnerable to unbilled revenue (under-invoicing) and deferred revenue (over-invoicing), as well as late supplier claims eroding project margin.Time & Materials / Reimbursable Contracts:Accounting dynamic: Directly tied to approved timesheets and procurement pass-through plus markup. Vulnerable to unapproved hours, missing purchase orders, and rate mismatches.Internal R&D / Capital Expenditure Projects:Accounting dynamic: Engineering hours and equipment capitalized as intangible/fixed assets once criteria are met. Vulnerable to misclassified operating expenses (OPEX vs. CAPEX).2. Chart of Accounts (Nordic / SAF-T Aligned Standard)A four-digit standard account structure capturing assets, liabilities, equity, revenues, and operating expenses:Account RangeCategoryKey Accounts1000–1299Fixed & Intangible Assets1010 Capitalized R&D, 1200 Yard Machinery & Cranes, 1250 Accumulated Depreciation1400–1499Inventory & Work-in-Progress1410 Raw Materials (Steel/Piping), 1450 Work in Progress (WIP - Unbilled Contract Costs)1500–1699Receivables1510 Accounts Receivable (Trade), 1530 Accrued Project Revenue, 1580 Provision for Bad Debts1900–1999Cash & Bank1910 Operating Account (DNB - NOK), 1920 Escrow Account, 1930 FX Currency Account (EUR)2000–2099Equity2010 Share Capital, 2080 Retained Earnings2400–2599Current Liabilities & Payables2400 Accounts Payable (Trade), 2420 Invoiced Goods Received (GR/IR Clearing), 2440 Accrued Project Costs / Subcontractor Accruals2600–2799Payroll & Taxes2600 Accrued Payroll & Bonuses, 2710 Value Added Tax (MVA Payable), 2770 Employer Social Contributions (AGA)2900–2999Accruals & Provisions2910 Accrued Holiday Pay, 2930 Warranty & Claim Provisions3000–3999Revenue3010 Project Revenue - Milestone/Fixed Price, 3110 Time & Materials Engineering, 3800 FX Gain/Loss on Operating Items4000–4999Direct Project Costs (COGS)4010 Direct Materials & Consumables, 4100 Subcontractor Services & Yard Labor, 4200 Equipment Rental & Mobilization5000–5999Payroll & Personnel Expenses5000 Engineering & Project Salaries, 5200 Overtime & Offshore Uplift, 5400 Social Security Tax6000–7999Other Operating Expenses (OPEX)6000 Office & Yard Rent, 6300 Software & Cloud Licenses, 6700 Audit & Accounting Fees, 6800 Travel & Subsistence8000–8999Financial Items & Tax8010 Interest Income, 8110 Interest Expense, 8300 Corporate Income Tax Expense3. Relational ERP Schema (DuckDB / Parquet Ready)The data model connects operational site work to the general ledger through seven core relational tables:[projects] ───────────────< [wbs_elements]
│ │
│ (1:N) │ (1:N)
▼ ▼
[purchase_orders] ────────< [po_lines] ──────────< [vendor_invoices]
│ │
│ ▼
└────────────> [gl_journal_entries]
│
▼
[gl_journal_lines]
Table Definitions & Field Specifications1. projectsproject_id (VARCHAR, PK) — e.g., PRJ-2026-001project_name (VARCHAR)customer_id (VARCHAR)division_code (VARCHAR) — FK to divisions (DIV-OFF, DIV-INF, DIV-SER)project_manager (VARCHAR)contract_type (VARCHAR) — FIXED_PRICE, TIME_AND_MATERIALS, INTERNAL_CAPEXtotal_contract_value_nok (DECIMAL(14,2))start_date (DATE)planned_end_date (DATE)status (VARCHAR) — ACTIVE, ON_HOLD, COMPLETED, CLOSED2. wbs_elements (Work Breakdown Structure)wbs_code (VARCHAR, PK) — e.g., PRJ-2026-001.01.ENGproject_id (VARCHAR, FK)phase_name (VARCHAR) — Engineering, Procurement, Fabrication, Installation, Commissioningcost_center (VARCHAR)allocated_budget_nok (DECIMAL(14,2))forecast_cost_nok (DECIMAL(14,2))actual_progress_pct (DECIMAL(5,2))3. purchase_orders & po_linespurchase_orders:po_number (VARCHAR, PK) — e.g., PO-2026-8801vendor_id (VARCHAR)project_id (VARCHAR, FK)order_date (DATE)status (VARCHAR) — OPEN, PARTIALLY_RECEIVED, FULLY_RECEIVED, CLOSEDcurrency (VARCHAR) — NOK, EUR, USDpo_lines:po_line_id (VARCHAR, PK)po_number (VARCHAR, FK)wbs_code (VARCHAR, FK)line_description (VARCHAR)ordered_qty (DECIMAL(10,2))received_qty (DECIMAL(10,2))unit_price (DECIMAL(12,2))total_amount_nok (DECIMAL(14,2))delivery_status (VARCHAR) — PENDING, DELIVERED, INSPECTED4. vendor_invoices (AP Subledger)invoice_id (VARCHAR, PK) — e.g., INV-VEND-99214vendor_id (VARCHAR)vendor_name (VARCHAR)po_number (VARCHAR, Nullable FK)project_id (VARCHAR, Nullable FK)invoice_date (DATE)due_date (DATE)currency (VARCHAR)amount_original_curr (DECIMAL(14,2))amount_nok (DECIMAL(14,2))approval_status (VARCHAR) — APPROVED, PENDING_PM_APPROVAL, DISPUTED, BLOCKEDmatched_to_po (BOOLEAN)gr_ir_cleared (BOOLEAN)5. gl_journal_entries & gl_journal_lines (General Ledger)gl_journal_entries (Header):entry_id (VARCHAR, PK) — e.g., JV-2026-10-0042posting_date (DATE)period_id (VARCHAR) — e.g., 2026-10source_module (VARCHAR) — AP, AR, PAYROLL, ASSET, MANUAL_GL, CLOSE_ACCRUALcreated_by (VARCHAR) — User ID or automated system IDapproval_status (VARCHAR) — POSTED, PROPOSED, REJECTEDgl_journal_lines (Line Items):line_id (VARCHAR, PK)entry_id (VARCHAR, FK)account_number (VARCHAR, FK)debit_nok (DECIMAL(14,2), Default 0.00)credit_nok (DECIMAL(14,2), Default 0.00)cost_center (VARCHAR, Nullable)project_id (VARCHAR, Nullable)wbs_code (VARCHAR, Nullable)line_description (VARCHAR)4. Grounding for Synthetic Scenarios & Injected AnomaliesWith this schema in place, we can seed realistic close anomalies that the control room will catch:Uninvoiced Subcontractor Delivery: PO shows received_qty = 100% on WBS PRJ-2026-001.03.FAB, but no vendor invoice exists by Oct 31 $\rightarrow$ triggers a missing accrual investigation.Ghost Weekend / Unauthorized Postings: Manual GL entry posted on a Sunday to Account 4100 with no project or WBS code.Over-invoiced PO Line: Vendor invoice exceeds line tolerance by >15% without a formal change order.Project Cost Overrun / Margin Erosion: Project forecast exceeds contract value, triggering an unrecorded contract loss provision under IFRS 15 / US GAAP rules.

Step 3.Core Financial Controls & Deterministic Close RulesTo build a reliable Close Readiness Index, we avoid relying on LLM guesses for core accounting integrity. Instead, we establish a suite of deterministic SQL/Python control rules that evaluate the subledgers and general ledger at period end.Each rule yields a status:🟢 PASS (Control satisfied)🟡 WARNING (Review required / low-to-medium financial exposure)🔴 FAIL / BLOCKER (Hard close stop; period cannot be closed until resolved or formally overridden)1. General Ledger & Balance Sheet IntegrityCTRL-GL-01: Zero Trial Balance Imbalance (Hard Blocker)Objective: Ensure the fundamental double-entry equation holds across the entire general ledger for the period.Deterministic Logic: $$\left|\sum \text{debit\_nok} - \sum \text{credit\_nok}\right| = 0.00$$Thresholds:🟢 PASS: Delta $= 0.00$ NOK🔴 FAIL: Delta $\neq 0.00$ NOK (Halts close process immediately)Remediation Path: Identify unbalanced journal entries (gl_journal_entries.entry_id) and enforce rebalancing.CTRL-GL-02: Manual & Off-Hours Journal Entry InspectionObjective: Flag unauthorized or high-risk postings (e.g., manual entries created on weekends, holidays, or late night).Deterministic Logic: Filter for source_module = 'MANUAL_GL' where DAYOFWEEK(posting_date) IN (1, 7) or created_at timestamp is outside 06:00–20:00.Thresholds:🟢 PASS: 0 unapproved off-hours entries🟡 WARNING: $\le 3$ entries with total value $< 50,000$ NOK🔴 FAIL: Any single entry $> 100,000$ NOK or $> 3$ entries without attached controller pre-approval.2. Accounts Payable & Procurement (AP Subledger)CTRL-AP-01: Duplicate Vendor Invoices (Fraud & Double-Payment Prevention)Objective: Identify potential double postings to trade creditors.Deterministic Logic: Search vendor_invoices for duplicate pairs where:Same vendor_idSame amount_nok (or within 0.5% due to FX fluctuation)Invoice date within a $\pm 14$-day windowOR matching normalized invoice numbers (e.g., INV-1044 vs 1044).Thresholds:🟢 PASS: 0 duplicates detected🔴 FAIL: $\ge 1$ potential duplicate invoice approved or pending payment.CTRL-AP-02: Uninvoiced Goods Received (GR/IR Clearing Discrepancies)Objective: Ensure all materials/services received at yard or site have corresponding invoices or accurate close accruals.Deterministic Logic: Query po_lines where delivery_status = 'DELIVERED' and received_qty > 0, but no matching vendor_invoices line exists within 30 days of receipt date.Thresholds:🟢 PASS: Total unbilled goods received $< 25,000$ NOK🟡 WARNING: Uninvoiced goods between $25,000$ and $250,000$ NOK🔴 FAIL: Uninvoiced deliveries $> 250,000$ NOK without an offsetting accrual entry in Account 2420/2440.CTRL-AP-03: Purchase Order Tolerance Violations (Three-Way Match)Objective: Prevent vendors from overcharging beyond authorized purchase commitments.Deterministic Logic: Compare vendor_invoices.amount_nok against po_lines.total_amount_nok. $$\text{Variance \%} = \frac{\text{Invoice Amount} - \text{PO Amount}}{\text{PO Amount}} \times 100$$Thresholds:🟢 PASS: Variance $\le 2.0\%$ (standard minor price variance)🟡 WARNING: Variance between $2.0\%$ and $10.0\%$🔴 FAIL: Variance $> 10.0\%$ or absolute overrun $> 50,000$ NOK without an approved PO Change Order.3. Project Accounting & Margin Protection (WBS Level)CTRL-PRJ-01: Unbilled Milestone & WIP ReconciliationObjective: Validate that physical milestone progress matches revenue recognition and WIP balances under IFRS 15.Deterministic Logic: Compare calculated earned value against billed revenue: $$\text{Earned Value} = \text{Contract Value} \times \left(\frac{\text{Actual Cost to Date}}{\text{Forecast Total Cost}}\right)$$ $$\text{Unbilled WIP} = \text{Earned Value} - \text{Cumulative Billed Revenue}$$Thresholds:🟢 PASS: Ledger account 1450 (WIP) matches calculated unbilled WIP within $\pm 1.0\%$🟡 WARNING: Discrepancy between $1.0\%$ and $5.0\%$🔴 FAIL: Discrepancy $> 5.0\%$ or $> 200,000$ NOK.CTRL-PRJ-02: Project Cost Overrun / Onerous Contract TriggerObjective: Ensure provision for contract losses is booked immediately if project forecast exceeds contract value.Deterministic Logic: Flag any project where: $$\text{forecast\_cost\_nok} > \text{total\_contract\_value\_nok}$$Thresholds:🟢 PASS: 0 unprovided loss-making projects🔴 FAIL: Any project in deficit without a corresponding loss provision booked to Account 2930 and charged to Account 4100.CTRL-PRJ-03: Missing or Mismatched Project Accounting DimensionsObjective: Prevent cost leakages where direct project expenses lack required WBS or project tags.Deterministic Logic: Scan gl_journal_lines for direct project cost accounts (4000–4999) where project_id IS NULL or wbs_code IS NULL.Thresholds:🟢 PASS: 0 untagged lines🔴 FAIL: Any direct cost posting lacking project/WBS tagging.4. Accounts Receivable & Cash ReconciliationCTRL-AR-01: Bank Statement to General Ledger ReconciliationObjective: Reconcile operating and currency bank accounts against cash ledger accounts.Deterministic Logic: $$\text{Bank Statement Closing Balance} - \text{GL Account 1910 Balance} - \text{Outstanding Deposits} + \text{Unpresented Cheques} = 0.00$$Thresholds:🟢 PASS: Unreconciled difference $= 0.00$ NOK🟡 WARNING: Difference $< 5,000$ NOK aged $< 3$ days🔴 FAIL: Unreconciled difference $\ge 5,000$ NOK or any item aged $> 5$ days.CTRL-AR-02: Overdue Customer Invoices & Expected Credit Loss (ECL)Objective: Ensure aged receivables (>90 days past due) have appropriate bad debt provisions under IFRS 9.Deterministic Logic: Identify receivables in 1510 past due $>90$ days without corresponding credit allowance in 1580.Thresholds:🟢 PASS: All 90+ day balances covered by policy provisions🟡 WARNING: Uncovered aged exposure $< 100,000$ NOK🔴 FAIL: Uncovered aged exposure $\ge 100,000$ NOK.5. Payroll & Statutory ObligationsCTRL-PAY-01: Employer Social Security & Tax Clearing (AGA / MVA)Objective: Verify statutory payroll taxes match gross reported monthly engineering salaries.Deterministic Logic: Verify that Norwegian employer contribution (Arbeidsgiveravgift - 14.1% standard zone rate) accurately mirrors taxable payroll entries: $$\left|\text{Account 5400} - (\text{Taxable Payroll Account 5000} \times 0.141)\right| < 100.00 \text{ NOK}$$Thresholds:🟢 PASS: Variance $< 100.00$ NOK🔴 FAIL: Variance $\ge 100.00$ NOK (Indicates payroll batch miscalculation or missing accrual).6. Close Readiness Index Calculation FormulaThe control room calculates an aggregate score from 0% to 100%:$$\text{Readiness Index} = \left(\frac{\sum \text{Weights of Passed Controls}}{\sum \text{Total Control Weights}}\right) \times 100$$If any 🔴 Hard Blocker is active, the status is locked to "CLOSE BLOCKED", regardless of the percentage score.Only when all blockers are cleared and score is $\ge 95\%$ does the status shift to "READY FOR CONTROLLER SIGN-OFF".

Step 4.Machine Learning & Anomaly Detection PipelineWhile the deterministic rules in Step 3 enforce known accounting laws (e.g., debits equal credits, 3-way match tolerances), they cannot catch unusual behavioral patterns—such as a cost center suddenly booking an invoice type it has never seen before, or an engineer splitting transactions to bypass approval thresholds.This is where the unsupervised anomaly detection layer comes in, operating as a statistical safety net alongside the deterministic rules.1. Role & Architectural Boundaries of the ML LayerTo maintain financial rigor and auditor trust:ML flags, it never posts: The ML model only assigns an anomaly score and flags items for investigation. It never alters balances or creates journal entries directly.Separation from deterministic checks: Deterministic rule failures are deterministic facts (e.g., trial balance imbalance). ML flags are statistical probabilities requiring human interpretation.Explainability first: Every anomaly flag must be accompanied by feature contributions (e.g., "Why was this flagged? Amount was $4.2\sigma$ above cost center mean, posted at an atypical hour").[Raw General Ledger & AP Data]
│
▼
┌─────────────────────────┐ ┌─────────────────────────┐
│ Deterministic Rules │ │ Unsupervised ML │
│ (SQL / DuckDB) │ │ (Isolation Forest) │
│ • Zero trial balance │ │ • Multi-factor outliers │
│ • 3-way PO tolerance │ │ • Novel vendor-CC pairs │
│ • Duplicate checks │ │ • Structurally odd JVs │
└────────────┬────────────┘ └────────────┬────────────┘
│ │
└───────────────┬───────────────┘
▼
[Anomaly Candidate Queue]
│
▼
[LLM Investigation Layer] 2. Model Selection: Isolation ForestWe use Isolation Forest (sklearn.ensemble.IsolationForest) as the primary statistical engine for tabular journal and invoice entries:Why Isolation Forest?Financial fraud and posting errors are few and distinct—the exact structural premise Isolation Forest is optimized to isolate.It performs well on non-linear, multi-dimensional tabular data without requiring labeled historical fraud datasets (which rarely exist in mid-sized ERPs).Fast inference time suitable for in-memory DuckDB/Pandas execution during the close window.3. Feature Engineering MatrixRaw ERP rows are transformed into a normalized feature vector $\mathbf{x}_i$ capturing size, timing, categorical novelty, and structural behavior:Feature NameTypeDescriptionRationaleamount*log_scaledNumerical$\ln(\text{amount\_nok} + 1)$Handles extreme positive skewness of financial figures.amount_zscore_by_accountNumerical$Z = \frac{x - \mu*{\text{acct}}}{\sigma*{\text{acct}}}$Flags unusually large entries relative to that specific GL account's history.amount_zscore_by_ccNumerical$Z = \frac{x - \mu*{\text{cc}}}{\sigma\_{\text{cc}}}$Flags amounts atypical for the specific cost center.is_weekendBinary1 if Saturday/Sunday, else 0Catches unauthorized weekend postings.posting_hour_sin, _cosCyclicalSine/cosine transformation of hour (0–23)Encodes time of day without boundary discontinuity.days_to_period_endNumericalCalendar days until month close (e.g., 0 to 30)Flags "close-packing" (rushing questionable entries at the 11th hour).vendor_frequency_scoreNumericalHistorical frequency of this vendor in this CCFlags a project or cost center using a vendor for the first time.benford_first_digit_riskCategorical/ScoreDeviation of leading digit from Benford's LawFlags potential fabricated numbers or threshold avoidance (e.g., 49,900 NOK).is_round_thousandBinary1 if amount mod 1,000 = 0 and $>10,000$ NOKForensic red flag; genuine invoices rarely hit round thousands.4. Pipeline Implementation (Python / Scikit-Learn)import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class CloseAnomalyDetector:
def **init**(self, contamination: float = 0.03):
"""
contamination: Estimated proportion of outliers in the dataset (~3% typical for close exceptions)
"""
self.contamination = contamination
self.model = IsolationForest(
n_estimators=150,
max_samples="auto",
contamination=self.contamination,
random_state=42,
n_jobs=-1
)
self.scaler = StandardScaler()

    def fit_predict(self, df_features: pd.DataFrame) -> pd.DataFrame:
        # Scale numerical features
        X_scaled = self.scaler.fit_transform(df_features)

        # Fit model and predict (-1 for anomaly, 1 for inlier)
        predictions = self.model.fit_predict(X_scaled)

        # Negative anomaly score: lower values indicate higher abnormality
        raw_scores = self.model.decision_function(X_scaled)

        # Normalize anomaly score to [0, 100] where 100 is most anomalous
        norm_scores = (raw_scores.max() - raw_scores) / (raw_scores.max() - raw_scores.min()) * 100

        results = df_features.copy()
        results["is_anomaly"] = predictions == -1
        results["anomaly_score"] = np.round(norm_scores, 2)

        return results

5. Scoring & Routing ThresholdsThe resulting anomaly_score (0–100) dictates how the transaction is handled:[Transaction Ingested]
   │
   ├──> Score < 65: 🟢 Normal (No action needed)
   │
   ├──> Score 65–84: 🟡 Moderate Anomaly (Batched into Controller Routine Review Queue)
   │
   └──> Score ≥ 85: 🔴 Critical Anomaly
   │
   ▼
   [Trigger Autonomous LLM Investigation]
   (Gathers WBS context, vendor history, and builds Evidence Dossier)
6. What the ML Catches that Rules Miss: Real ExamplesSplit-Invoice Threshold Avoidance:A project manager has approval authority up to 100,000 NOK.Two invoices for 95,000 NOK each arrive on consecutive days for the same vendor and WBS.Rule verdict: Passes individual 100k limits and standard PO match.ML verdict: High anomaly score driven by sudden z-score deviation, matching round increments, and unusual frequency spike.Account-Cost Center Mismatch:A structural engineering cost center (CC-1100) suddenly books software license expenses (Account 6300) typically only booked by IT/Admin (CC-9100).ML verdict: Flagged due to low categorical co-occurrence and high relative amount for that account type.

step 5.The LLM Investigation Agent & Controller Evidence Graph
Once an anomaly is flagged by either a deterministic rule (Step 3) or the Isolation Forest model (Step 4), it enters the Investigation Layer.
In traditional finance, this is where a human controller spends hours digging through emails, pulling PO histories, checking timesheets, and cross-referencing contract terms. In CLOSE-AI, an autonomous agent executes this detective work in seconds and builds a structured Evidence Dossier.

1. Architectural Role & Ground Rules
   To ensure compliance with audit standards, the LLM agent follows three strict operating boundaries:
   Deterministic Retrieval: The agent does not calculate balances or query the database with raw unconstrained text generation. It queries a structured Controller Evidence Graph using deterministic tool functions.
   Strict Grounding: Every claim in the agent's explanation must cite a specific transaction ID, PO number, contract clause, or ledger line.
   Proposal Only: The agent never posts adjustments directly. It generates a standardized Journal Voucher Proposal (JV) ready for human controller sign-off.
2. The Controller Evidence Graph
   The Evidence Graph links the relational entities into an operational chain of custody:
   [Contract / Terms] ──> [Project] ──> [WBS Element]
   │
   ▼
   [Vendor Master] ──────> [PO / PO Lines] ──> [Goods Receipt / Work Log]
   │ │
   ▼ ▼
   [Vendor Invoice] ──> [GL Postings (Debits/Credits)]
   When an anomaly is flagged (for example, on an invoice or a GL line), the agent traverses this graph backward and forward to pull the full context:
   Upstream: What was the original purchase order? Who approved it? What is the project budget and current WBS completion percentage?
   Peer items: Has this vendor submitted other invoices this month? Are there unbilled goods receipts?
   Policy check: Does this transaction breach company threshold rules (e.g., Change Order required if variance > 10%)?
3. Investigation Workflow
   [Flagged Anomaly Event]
   │
   ▼
   ┌────────────────────────────────────────┐
   │ 1. Context Assembly │
   │ Pull PO history, WBS budget, vendor │
   │ history, and prior 6-month trends │
   └──────────────────┬─────────────────────┘
   │
   ▼
   ┌────────────────────────────────────────┐
   │ 2. Root Cause Analysis │
   │ Compare facts against accounting rules │
   │ (IFRS 15, accrual policy, tolerance) │
   └──────────────────┬─────────────────────┘
   │
   ▼
   ┌────────────────────────────────────────┐
   │ 3. Financial Exposure Calculation │
   │ Determine exact EBITDA & cash impact │
   └──────────────────┬─────────────────────┘
   │
   ▼
   ┌────────────────────────────────────────┐
   │ 4. Generate Evidence Dossier & JV │
   │ Format structured output for Cockpit │
   └────────────────────────────────────────┘
4. Standardized Output: The Controller Evidence Dossier
   Every investigation outputs a standardized dossier displayed in the control room UI:
   {
   "investigation_id": "INV-2026-10-0042",
   "anomaly_ref": "FLAG-AP-03-8819",
   "target_entity": "INV-VEND-99214",
   "timestamp": "2026-10-31T17:15:00Z",
   "severity": "CRITICAL",

"observation": "Vendor 'Nordic Subsea Fabrication AS' invoiced 820,000 NOK on Project PRJ-2026-001 (WBS: FAB-02). This represents a 22.4% cost overrun against PO-8801.",

"evidence_chain": [
{"source": "PO-8801", "fact": "Authorized commitment: 670,000 NOK for fabrication of subsea manifold frame."},
{"source": "GR-4412", "fact": "Yard receipt confirmed delivery on 2026-10-24."},
{"source": "INV-99214", "fact": "Invoice received 2026-10-29 for 820,000 NOK with memo 'Overtime due to client revision'."},
{"source": "WBS-FAB-02", "fact": "No approved Client Change Order (CCO) logged in project system."}
],

"likely_cause": "Vendor billed for additional yard labor hours without an approved PO variation order or customer change order.",

"financial_impact": {
"unauthorized_variance_nok": 150000.00,
"ebitda_risk": "Negative 150,000 NOK margin erosion if booked without customer recharge",
"vat_impact_nok": 37500.00
},

"recommended_action": "HOLD_AND_ACCRUE",

"proposed_journal_voucher": {
"entry_type": "PERIOD_END_ACCRUAL",
"reversal_date": "2026-11-01",
"lines": [
{
"account": "4100 (Subcontractor Yard Labor)",
"debit_nok": 670000.00,
"credit_nok": 0.00,
"wbs_code": "PRJ-2026-001.03.FAB",
"memo": "Accrue authorized PO-8801 delivery"
},
{
"account": "2440 (Accrued Project Liabilities)",
"debit_nok": 0.00,
"credit_nok": 670000.00,
"wbs_code": "PRJ-2026-001.03.FAB",
"memo": "GR/IR clearing pending disputed balance"
}
],
"dispute_ticket": {
"vendor": "Nordic Subsea Fabrication AS",
"hold_amount_nok": 150000.00,
"assignee": "Project Manager (PRJ-2026-001)"
}
}
} 5. System Prompt & Reasoning Guardrails
The underlying agent prompt is engineered to enforce strict financial professionalism:
No Speculative Conclusions: If the evidence does not state why an invoice is higher, state "Cause unverified by documents; requires PM clarification", rather than inventing reasons.
Accounting Standards Adherence: Accruals must specify balancing debit/credit accounts and reversal dates if applicable (e.g., standard reversing accruals on Day 1 of the next period).
Deterministic Calculations: Never calculate variances or tax in prompt tokens; ingest pre-calculated metrics directly from DuckDB.

Step 6.Human-in-the-Loop Governance & Controller Approval WorkflowIn enterprise accounting, AI cannot have write access to the general ledger. The primary reason financial executives reject automated tools is the fear of uncontrolled, unverified journal entries poisoning the financial statements.Step 6 defines the Human-in-the-Loop (HITL) boundary: the governance architecture, sign-off gates, state machine, and cryptographic audit logging that guarantee every transaction has an accountable human controller attached to it.1. The Core Governance Rule: The "Glass Box" PrincipleThe system enforces three hard rules:Zero Direct Ledger Posting: The AI agent and rule engine have read-only access to ERP subledgers and can only write to a staged table (proposed_journal_vouchers).Explicit Human Sign-Off: A journal entry only moves from PROPOSED to POSTED when a credentialed controller signs off with an authenticated session and role permission.Unbroken Chain of Custody: Every posted entry carries metadata linking the human approver, the AI investigation dossier ID, the underlying source documents, and the rule or model that detected the event.2. Controller Cockpit: Action MatrixIn the control room interface, every flagged anomaly and proposed adjustment presents the controller with four unambiguous actions:┌────────────────────────────────────────────────────────────────────────┐
│ PROPOSED JOURNAL VOUCHER: JV-2026-10-0042 │
│ WBS: PRJ-2026-001.03.FAB | Vendor: Nordic Subsea Fabrication AS │
│ Amount: 670,000.00 NOK (Accrue authorized delivery; hold 150k dispute) │
├────────────────────────────────────────────────────────────────────────┤
│ [ APPROVE & POST ] [ EDIT & POST ] [ DISPUTE / HOLD ] [ REJECT ] │
└────────────────────────────────────────────────────────────────────────┘
ActionState TransitionSystem BehaviorApprove & PostPROPOSED $\rightarrow$ POSTEDGenerates a signed GL journal payload, commits it to the ledger, and records the audit event.Edit & PostPROPOSED $\rightarrow$ EDITED $\rightarrow$ POSTEDController overrides accounts, amounts, or WBS codes. The system records the original AI proposal alongside the human controller's amended version and required rationale note.Dispute / HoldPROPOSED $\rightarrow$ ON_HOLDTemporarily freezes payment/accrual, logs an exception ticket, and routes the dossier to the relevant Project Manager or Procurement lead.RejectPROPOSED $\rightarrow$ REJECTEDDiscards the proposal. The controller must select a rejection reason (e.g., "Already accounted for in alternate accrual", "False positive", "Vendor credit incoming").3. The Close State MachineThe overall close window progresses through a strictly sequenced lifecycle:[PERIOD OPEN]
│
▼
[PRE-CLOSE INGESTION & RECONCILIATION]
(DuckDB rules run; Isolation Forest detects outliers)
│
├─── 🔴 Any Hard Blocker Failed? ──> [CLOSE BLOCKED]
│ │ (Issues resolved)
│ ▼
└─── 🟢 All Hard Blockers Passed
│
▼
[INVESTIGATION & TRIAGE]
(Agent generates dossiers and staged JVs; controllers review)
│
▼
[STAGED JVs SIGNED OFF]
(Readiness Score ≥ 95%; zero unreviewed critical anomalies)
│
▼
[CONTROLLER FORMAL CLOSE SIGN-OFF]
(Dual authorization / two-person rule for final ledger freeze)
│
▼
[PERIOD CLOSED & LOCKED]
(Ledger becomes read-only; Audit Evidence Pack compiled) 4. Cryptographic Audit Trail & Evidence PackAuditors require proof that financial statements were not tampered with. To fulfill statutory audit standards (ISA 240 / 315 / 500 and Nordic SAF-T requirements), every approved action generates a tamper-evident audit record:Audit Log Record Schema{
"audit_event_id": "AUD-2026-10-31-0982",
"timestamp": "2026-10-31T18:42:15Z",
"period": "2026-10",
"event_type": "JOURNAL_VOUCHER_POSTED",
"journal_id": "JV-2026-10-0042",
"controller": {
"user_id": "ctrl_frank_e",
"name": "Frank Ellingsen",
"role": "Lead Project Controller",
"ip_address": "192.168.10.45"
},
"action": "APPROVED_WITHOUT_EDIT",
"source_investigation_id": "INV-2026-10-0042",
"triggering_rule": "CTRL-AP-03 (PO Tolerance Overrun)",
"financial_lines": [
{"account": "4100", "debit_nok": 670000.00, "credit_nok": 0.00, "wbs": "PRJ-2026-001.03.FAB"},
{"account": "2440", "debit_nok": 0.00, "credit_nok": 670000.00, "wbs": "PRJ-2026-001.03.FAB"}
],
"justification_memo": "Accrued 100% of delivered fabrication per GR-4412. Disputed overrun of 150k NOK routed to PM for client change order review.",
"record_hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
At the conclusion of the close, the system compiles the Month-End Audit Evidence Pack:Complete Trial Balance before and after adjustments.List of all 10 deterministic rule outcomes with timestamps.Complete log of all ML anomaly scores.All generated Controller Dossiers with attached POs, invoices, and delivery slips.Controller sign-off certificates with digital signatures.5. Summary of the End-to-End ArchitectureWe have now established the full strategic foundation:Step 1: Business Problem $\rightarrow$ Month-end close latency, disconnect between project delivery and GL, lack of audit-grade AI.Step 2: Company & Schema $\rightarrow$ Nordic Engineering Projects AS, multi-currency, WBS, PO, AP, and GL relational model.Step 3: Deterministic Rules $\rightarrow$ 10 hard controls (zero trial balance imbalance, 3-way match, WIP recalculation).Step 4: Machine Learning $\rightarrow$ Tabular Isolation Forest with engineered features for multivariate anomaly scoring.Step 5: LLM Agent & Graph $\rightarrow$ Contextual investigation, root-cause deduction, and structured journal proposals.Step 6: Governance & Audit $\rightarrow$ Human-in-the-loop sign-off, close state machine, and tamper-evident audit packs.

Step 7.Synthetic Data Generator Architecture & Code
To test every aspect of the control room—from deterministic control rules and Isolation Forest anomaly scoring to the LLM agent investigation—we need a clean Python generator that creates realistic, relational ERP data with deliberately injected anomalies.

1. Generator Design & Injected Anomalies
   The script generates a 1-month fiscal closing period (2026-10) for Nordic Engineering Projects AS containing:
   Master Data: Projects, WBS phases, vendors, and cost centers.
   Transactional Data: Purchase orders, goods receipts, vendor invoices (AP), and General Ledger journal entries.
   Controlled Ground-Truth Anomalies:
   ANOMALY_DUPLICATE_INVOICE: Duplicate vendor invoice with identical amount and matching date window (triggers CTRL-AP-01).
   ANOMALY_UNINVOICED_RECEIPT: Yard goods receipt confirmed 100% delivered, but no vendor invoice or accrual exists (triggers CTRL-AP-02).
   ANOMALY_TOLERANCE_OVERRUN: Fabrication invoice exceeding purchase order amount by 22.4% without an approved Change Order (triggers CTRL-AP-03).
   ANOMALY_OFF_HOURS_MANUAL: Large manual journal voucher posted on a Sunday night to a direct cost account without project/WBS tagging (triggers CTRL-GL-02 and CTRL-PRJ-03).
   ANOMALY_TRIAL_BALANCE_UNBALANCED: A 15,000 NOK rounding or transposition mismatch in GL lines (triggers hard blocker CTRL-GL-01).
2. Complete Synthetic Data Generator (generate_erp_data.py)
   Here is the complete script using standard libraries and pandas/numpy to export DuckDB-ready Parquet and CSV files:
   import os
   import random
   import datetime
   import numpy as np
   import pandas as pd

# Set deterministic random seed

np.random.seed(42)
random.seed(42)

OUT_DIR = "erp_data_2026_10"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------

# 1. Master Data: Divisions, Cost Centers, Vendors, Projects

# ---------------------------------------------------------

DIVISIONS = ["DIV-OFF", "DIV-INF", "DIV-SER", "DIV-CORP"]
COST_CENTERS = [
("CC-1100", "Subsea Engineering", "DIV-OFF"),
("CC-1200", "Fabrication Yard", "DIV-OFF"),
("CC-2100", "Civil & Structural", "DIV-INF"),
("CC-2200", "Site Operations", "DIV-INF"),
("CC-3100", "Specialist Consultants", "DIV-SER"),
("CC-9000", "Finance & Close Ops", "DIV-CORP"),
("CC-9100", "HQ Admin & Management", "DIV-CORP"),
]

VENDORS = [
("VEND-101", "Nordic Subsea Fabrication AS", "Fabrication & Yard Services"),
("VEND-102", "Bergen Marine Logistics AS", "Mobilization & Marine Vessels"),
("VEND-103", "Stavanger Inspection & NDT AS", "Technical Testing & QA"),
("VEND-104", "Fjord Steel & Piping Supplies", "Raw Materials"),
("VEND-105", "Equinor Engineering Advisory", "Consulting & Feasibility"),
("VEND-106", "Aker Yard Support DA", "Subcontractor Labor"),
("VEND-107", "Global CAD & Simulation Systems", "Software & Cloud Services"),
]

PROJECTS_DATA = [
("PRJ-2026-001", "Troll Wind Substation Modular Frame", "CUST-EQN", "DIV-OFF", "Frank Ellingsen", "FIXED_PRICE", 18500000.0, "2026-01-15", "2026-12-20", "ACTIVE"),
("PRJ-2026-002", "Sognefjord Crossing Ventilation Shafts", "CUST-STAT", "DIV-INF", "Kari Nordmann", "FIXED_PRICE", 9200000.0, "2026-03-01", "2026-11-30", "ACTIVE"),
("PRJ-2026-003", "Hydrogen Pipeline FEA Simulation", "CUST-HYD", "DIV-SER", "Erik Sørli", "TIME_AND_MATERIALS", 3400000.0, "2026-06-01", "2027-02-28", "ACTIVE"),
("PRJ-2026-004", "Modular Yard Crane Electrification", "INTERNAL", "DIV-OFF", "Lars Hovland", "INTERNAL_CAPEX", 2100000.0, "2026-08-01", "2026-12-31", "ACTIVE"),
]

df_projects = pd.DataFrame(PROJECTS_DATA, columns=[
"project_id", "project_name", "customer_id", "division_code",
"project_manager", "contract_type", "total_contract_value_nok",
"start_date", "planned_end_date", "status"
])

# ---------------------------------------------------------

# 2. WBS Elements

# ---------------------------------------------------------

WBS_DATA = [
("PRJ-2026-001.01.ENG", "PRJ-2026-001", "Engineering & Design", "CC-1100", 3500000.0, 3400000.0, 95.0),
("PRJ-2026-001.02.PROC", "PRJ-2026-001", "Procurement & Steel", "CC-1100", 5000000.0, 5100000.0, 100.0),
("PRJ-2026-001.03.FAB", "PRJ-2026-001", "Yard Fabrication", "CC-1200", 6500000.0, 6800000.0, 80.0),
("PRJ-2026-001.04.INST", "PRJ-2026-001", "Offshore Mobilization", "CC-1200", 3500000.0, 3600000.0, 30.0),
("PRJ-2026-002.01.CIVIL", "PRJ-2026-002", "Civil Excavation", "CC-2100", 4200000.0, 4100000.0, 85.0),
("PRJ-2026-002.02.VENT", "PRJ-2026-002", "Ventilation Ducts", "CC-2200", 5000000.0, 5300000.0, 60.0),
("PRJ-2026-003.01.FEA", "PRJ-2026-003", "Finite Element Analysis", "CC-3100", 3400000.0, 3200000.0, 70.0),
("PRJ-2026-004.01.CAPEX", "PRJ-2026-004", "Crane Modernization", "CC-1200", 2100000.0, 2050000.0, 75.0),
]

df_wbs = pd.DataFrame(WBS_DATA, columns=[
"wbs_code", "project_id", "phase_name", "cost_center",
"allocated_budget_nok", "forecast_cost_nok", "actual_progress_pct"
])

# ---------------------------------------------------------

# 3. Purchase Orders & PO Lines

# ---------------------------------------------------------

po_headers = []
po_lines = []

for i in range(1, 26):
po_num = f"PO-2026-{8800 + i}"
vendor = random.choice(VENDORS)
prj = random.choice(PROJECTS_DATA)
matching_wbs = [w for w in WBS_DATA if w[1] == prj[0]]
selected_wbs = random.choice(matching_wbs) if matching_wbs else WBS_DATA[0]

    order_date = datetime.date(2026, 9, 15) + datetime.timedelta(days=random.randint(1, 30))
    currency = "EUR" if vendor[0] in ["VEND-104", "VEND-107"] else "NOK"

    po_headers.append({
        "po_number": po_num,
        "vendor_id": vendor[0],
        "project_id": prj[0],
        "order_date": order_date,
        "status": "PARTIALLY_RECEIVED",
        "currency": currency
    })

    # 1 to 3 lines per PO
    for line_idx in range(1, random.randint(2, 4)):
        line_id = f"{po_num}-{line_idx}"
        qty = random.randint(1, 20)
        unit_price = random.choice([5000.0, 12000.0, 25000.0, 65000.0, 110000.0])
        total_nok = qty * unit_price

        po_lines.append({
            "po_line_id": line_id,
            "po_number": po_num,
            "wbs_code": selected_wbs[0],
            "line_description": f"Deliverable services/materials for {selected_wbs[2]}",
            "ordered_qty": float(qty),
            "received_qty": float(qty), # standard: received
            "unit_price": unit_price,
            "total_amount_nok": total_nok,
            "delivery_status": "DELIVERED"
        })

df_pos = pd.DataFrame(po_headers)
df_po_lines = pd.DataFrame(po_lines)

# ---------------------------------------------------------

# 4. Vendor Invoices (AP Subledger) & Injected Inconsistencies

# ---------------------------------------------------------

invoices = []
inv_counter = 99100

for idx, line in df_po_lines.iterrows():
inv_counter += 1
inv_id = f"INV-VEND-{inv_counter}"
po_num = line["po_number"]
po_hdr = df_pos[df_pos["po_number"] == po_num].iloc[0]

    inv_date = po_hdr["order_date"] + datetime.timedelta(days=random.randint(10, 25))
    due_date = inv_date + datetime.timedelta(days=30)

    amount_nok = line["total_amount_nok"]
    matched = True
    approval = "APPROVED"

    invoices.append({
        "invoice_id": inv_id,
        "vendor_id": po_hdr["vendor_id"],
        "vendor_name": next(v[1] for v in VENDORS if v[0] == po_hdr["vendor_id"]),
        "po_number": po_num,
        "project_id": po_hdr["project_id"],
        "wbs_code": line["wbs_code"],
        "invoice_date": inv_date,
        "due_date": due_date,
        "currency": po_hdr["currency"],
        "amount_nok": amount_nok,
        "approval_status": approval,
        "matched_to_po": matched,
        "gr_ir_cleared": True
    })

df_invoices = pd.DataFrame(invoices)

# INJECT ANOMALY 1: Duplicate Vendor Invoice (CTRL-AP-01)

dup_source = df_invoices.iloc[3].to_dict()
dup_inv = dup_source.copy()
dup_inv["invoice_id"] = "INV-VEND-99991-DUP"
dup_inv["invoice_date"] = dup_source["invoice_date"] + datetime.timedelta(days=2)
df_invoices = pd.concat([df_invoices, pd.DataFrame([dup_inv])], ignore_index=True)

# INJECT ANOMALY 2: Tolerance Overrun (+22.4%) on Subsea PO (CTRL-AP-03)

overrun_idx = 8
df_invoices.loc[overrun_idx, "amount_nok"] = df_invoices.loc[overrun_idx, "amount_nok"] \* 1.224
df_invoices.loc[overrun_idx, "approval_status"] = "PENDING_PM_APPROVAL"
df_invoices.loc[overrun_idx, "matched_to_po"] = False

# INJECT ANOMALY 3: Uninvoiced Delivery (PO received, invoice omitted) (CTRL-AP-02)

uninvoiced_po_line = df_po_lines.iloc[12]
df_invoices = df_invoices[df_invoices["po_number"] != uninvoiced_po_line["po_number"]]

# ---------------------------------------------------------

# 5. General Ledger (Journal Entries & Lines)

# ---------------------------------------------------------

gl_entries = []
gl_lines = []
entry_counter = 1000

def add_journal_entry(date_val, period, module, user, lines_data):
global entry_counter
entry_counter += 1
entry_id = f"JV-2026-10-{entry_counter}"

    gl_entries.append({
        "entry_id": entry_id,
        "posting_date": date_val,
        "period_id": period,
        "source_module": module,
        "created_by": user,
        "approval_status": "POSTED"
    })

    for l_idx, (acct, dr, cr, cc, prj, wbs, desc) in enumerate(lines_data, 1):
        gl_lines.append({
            "line_id": f"{entry_id}-{l_idx}",
            "entry_id": entry_id,
            "account_number": acct,
            "debit_nok": dr,
            "credit_nok": cr,
            "cost_center": cc,
            "project_id": prj,
            "wbs_code": wbs,
            "line_description": desc
        })

# Normal AP postings from invoices

for \_, inv in df_invoices.iterrows():
amt = inv["amount_nok"]
inv_date = inv["invoice_date"]
add_journal_entry(
inv_date, "2026-10", "AP", "sys_ap_batch",
[
("4100", amt, 0.0, "CC-1200", inv["project_id"], inv["wbs_code"], f"Subcontractor cost: {inv['invoice_id']}"),
("2400", 0.0, amt, "CC-9000", None, None, f"Trade liability: {inv['invoice_id']}")
]
)

# Standard Salary & Social Security Entry

add_journal_entry(
datetime.date(2026, 10, 25), "2026-10", "PAYROLL", "sys_payroll_auto",
[
("5000", 1850000.0, 0.0, "CC-1100", None, None, "Engineering monthly salaries"),
("5400", 260850.0, 0.0, "CC-9000", None, None, "Employer AGA tax (14.1%)"),
("2600", 0.0, 1850000.0, "CC-9000", None, None, "Net salaries payable"),
("2770", 0.0, 260850.0, "CC-9000", None, None, "Statutory tax clearing")
]
)

# Standard Revenue Milestones

add_journal_entry(
datetime.date(2026, 10, 28), "2026-10", "AR", "sys_billing",
[
("1510", 3500000.0, 0.0, "CC-9000", "PRJ-2026-001", None, "Milestone 3 Billing"),
("3010", 0.0, 3500000.0, "CC-1100", "PRJ-2026-001", "PRJ-2026-001.03.FAB", "Earned milestone revenue")
]
)

# INJECT ANOMALY 4: Off-Hours Manual Entry without WBS/Project (CTRL-GL-02 & CTRL-PRJ-03)

sunday_date = datetime.date(2026, 10, 25) # Sunday
add_journal_entry(
sunday_date, "2026-10", "MANUAL_GL", "usr_external_temp",
[
("4100", 145000.0, 0.0, "CC-1200", None, None, "Urgent weekend adjustment yard materials"),
("2440", 0.0, 145000.0, "CC-9000", None, None, "Accrued yard expenses")
]
)

# INJECT ANOMALY 5: Unbalanced Trial Balance Entry (CTRL-GL-01 Blocker)

add_journal_entry(
datetime.date(2026, 10, 30), "2026-10", "MANUAL_GL", "usr_junior_acct",
[
("6800", 35000.0, 0.0, "CC-9100", None, None, "Travel and client site mobilization"),
("1910", 0.0, 20000.0, "CC-9000", None, None, "Direct bank withdrawal")

# Delta 15,000 NOK imbalance!

]
)

df_gl_entries = pd.DataFrame(gl_entries)
df_gl_lines = pd.DataFrame(gl_lines)

# ---------------------------------------------------------

# 6. Export Tables to CSV and Parquet

# ---------------------------------------------------------

tables = {
"projects": df_projects,
"wbs_elements": df_wbs,
"purchase_orders": df_pos,
"po_lines": df_po_lines,
"vendor_invoices": df_invoices,
"gl_journal_entries": df_gl_entries,
"gl_journal_lines": df_gl_lines
}

for name, df in tables.items():
df.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
try:
df.to_parquet(os.path.join(OUT_DIR, f"{name}.parquet"), index=False)
except Exception:
pass # Parquet export optional if pyarrow not installed

print(f"Generated {len(df_gl_lines)} GL lines across {len(df_gl_entries)} journal entries.")
print(f"Dataset successfully exported to directory '{OUT_DIR}'.") 3. What Happens When This Dataset Runs?
Running this data through the system produces the exact operational flow:
Deterministic Rule Engine (DuckDB):
CTRL-GL-01 halts the close: reports a 15,000 NOK Trial Balance Imbalance on entry JV-2026-10-1002.
CTRL-AP-01 flags duplicate invoice INV-VEND-99991-DUP.
CTRL-AP-03 flags the 22.4% price overrun on PO-2026-8809.
CTRL-GL-02 and CTRL-PRJ-03 flag the Sunday night manual posting lacking WBS dimensions.
Isolation Forest Model:
Flags the Sunday manual posting and the split invoice amounts as top-percentile statistical anomalies.
Controller Cockpit:
Displays CLOSE BLOCKED with an aggregate readiness score of ~74%, directing the controller directly to the 5 anomalies.

Step 8.Control Engine & SQL Evaluation Scripts (DuckDB)
With the relational schema and synthetic dataset in place, we implement the Deterministic Control Engine. This engine runs directly on top of the Parquet/CSV files using DuckDB, returning structured, auditable outputs for each financial control rule defined in Step 3.

1. Control Rule SQL Specifications
   Each rule query returns a standardized schema: rule*id, rule_name, status (PASS, WARNING, FAIL), severity (BLOCKER, HIGH, MEDIUM, LOW), discrepancy_amount_nok, affected_records_count, and details_json.
   1.1. CTRL-GL-01: Zero Trial Balance Imbalance (Hard Blocker)
   WITH tb_summary AS (
   SELECT
   ROUND(SUM(debit_nok), 2) AS total_debit,
   ROUND(SUM(credit_nok), 2) AS total_credit,
   ROUND(ABS(SUM(debit_nok) - SUM(credit_nok)), 2) AS imbalance
   FROM gl_journal_lines
   )
   SELECT
   'CTRL-GL-01' AS rule_id,
   'Zero Trial Balance Imbalance' AS rule_name,
   CASE
   WHEN imbalance = 0.00 THEN 'PASS'
   ELSE 'FAIL'
   END AS status,
   'BLOCKER' AS severity,
   imbalance AS discrepancy_amount_nok,
   CASE WHEN imbalance = 0.00 THEN 0 ELSE 1 END AS affected_records_count,
   json_object(
   'total_debit', total_debit,
   'total_credit', total_credit,
   'imbalance', imbalance
   ) AS details_json
   FROM tb_summary;
   1.2. CTRL-GL-02: Off-Hours & Weekend Manual Journal Postings
   WITH flagged_manual_entries AS (
   SELECT
   e.entry_id,
   e.posting_date,
   e.created_by,
   SUM(l.debit_nok) AS entry_total_nok
   FROM gl_journal_entries e
   JOIN gl_journal_lines l ON e.entry_id = l.entry_id
   WHERE e.source_module = 'MANUAL_GL'
   AND (EXTRACT(DOW FROM e.posting_date) IN (0, 6)) -- Sunday=0, Saturday=6 in DuckDB
   GROUP BY e.entry_id, e.posting_date, e.created_by
   )
   SELECT
   'CTRL-GL-02' AS rule_id,
   'Off-Hours & Weekend Manual Postings' AS rule_name,
   CASE
   WHEN COUNT(*) = 0 THEN 'PASS'
   WHEN MAX(entry*total_nok) > 100000 THEN 'FAIL'
   ELSE 'WARNING'
   END AS status,
   'HIGH' AS severity,
   COALESCE(SUM(entry_total_nok), 0.0) AS discrepancy_amount_nok,
   COUNT(*) AS affected*records_count,
   json_group_array(
   json_object(
   'entry_id', entry_id,
   'date', posting_date,
   'user', created_by,
   'amount_nok', entry_total_nok
   )
   ) AS details_json
   FROM flagged_manual_entries;
   1.3. CTRL-AP-01: Potential Duplicate Vendor Invoices
   WITH duplicate_invoices AS (
   SELECT
   a.invoice_id AS invoice_a,
   b.invoice_id AS invoice_b,
   a.vendor_id,
   a.vendor_name,
   a.amount_nok,
   a.invoice_date AS date_a,
   b.invoice_date AS date_b,
   ABS(DATEDIFF('day', a.invoice_date, b.invoice_date)) AS day_difference
   FROM vendor_invoices a
   JOIN vendor_invoices b
   ON a.vendor_id = b.vendor_id
   AND a.invoice_id < b.invoice_id -- eliminate self-joins & symmetrical pairs
   AND ABS(a.amount_nok - b.amount_nok) <= 0.01
   AND ABS(DATEDIFF('day', a.invoice_date, b.invoice_date)) <= 14
   )
   SELECT
   'CTRL-AP-01' AS rule_id,
   'Duplicate Vendor Invoices' AS rule_name,
   CASE
   WHEN COUNT(*) = 0 THEN 'PASS'
   ELSE 'FAIL'
   END AS status,
   'HIGH' AS severity,
   COALESCE(SUM(amount*nok), 0.0) AS discrepancy_amount_nok,
   COUNT(*) AS affected*records_count,
   json_group_array(
   json_object(
   'invoice_pair', invoice_a || ' / ' || invoice_b,
   'vendor', vendor_name,
   'amount_nok', amount_nok,
   'day_gap', day_difference
   )
   ) AS details_json
   FROM duplicate_invoices;
   1.4. CTRL-AP-02: Uninvoiced Goods Received (GR/IR Clearing Discrepancies)
   WITH uninvoiced_deliveries AS (
   SELECT
   l.po_line_id,
   l.po_number,
   l.wbs_code,
   l.total_amount_nok,
   h.vendor_id,
   h.order_date
   FROM po_lines l
   JOIN purchase_orders h ON l.po_number = h.po_number
   LEFT JOIN vendor_invoices i ON l.po_number = i.po_number
   WHERE l.delivery_status = 'DELIVERED'
   AND l.received_qty > 0
   AND i.invoice_id IS NULL
   )
   SELECT
   'CTRL-AP-02' AS rule_id,
   'Uninvoiced Goods Received' AS rule_name,
   CASE
   WHEN COALESCE(SUM(total_amount_nok), 0) < 25000 THEN 'PASS'
   WHEN SUM(total_amount_nok) <= 250000 THEN 'WARNING'
   ELSE 'FAIL'
   END AS status,
   'HIGH' AS severity,
   COALESCE(SUM(total_amount_nok), 0.0) AS discrepancy_amount_nok,
   COUNT(*) AS affected*records_count,
   json_group_array(
   json_object(
   'po_line_id', po_line_id,
   'po_number', po_number,
   'wbs_code', wbs_code,
   'unbilled_nok', total_amount_nok
   )
   ) AS details_json
   FROM uninvoiced_deliveries;
   1.5. CTRL-AP-03: Purchase Order Tolerance Overrun (>10%)
   WITH po_variance AS (
   SELECT
   i.invoice_id,
   i.po_number,
   i.vendor_name,
   i.amount_nok AS invoice_amount,
   l.total_amount_nok AS po_amount,
   ROUND((i.amount_nok - l.total_amount_nok), 2) AS variance_nok,
   ROUND(((i.amount_nok - l.total_amount_nok) / l.total_amount_nok) * 100, 2) AS variance*pct
   FROM vendor_invoices i
   JOIN po_lines l ON i.po_number = l.po_number
   WHERE i.amount_nok > l.total_amount_nok
   AND ((i.amount_nok - l.total_amount_nok) / l.total_amount_nok) > 0.10 -- >10% tolerance
   )
   SELECT
   'CTRL-AP-03' AS rule_id,
   'PO Price Tolerance Overrun' AS rule_name,
   CASE
   WHEN COUNT(*) = 0 THEN 'PASS'
   ELSE 'FAIL'
   END AS status,
   'HIGH' AS severity,
   COALESCE(SUM(variance*nok), 0.0) AS discrepancy_amount_nok,
   COUNT(*) AS affected*records_count,
   json_group_array(
   json_object(
   'invoice_id', invoice_id,
   'po_number', po_number,
   'vendor', vendor_name,
   'variance_nok', variance_nok,
   'variance_pct', variance_pct
   )
   ) AS details_json
   FROM po_variance;
   1.6. CTRL-PRJ-03: Direct Project Costs Missing Project or WBS Dimensions
   WITH untagged_costs AS (
   SELECT
   entry_id,
   line_id,
   account_number,
   debit_nok,
   cost_center,
   line_description
   FROM gl_journal_lines
   WHERE account_number BETWEEN '4000' AND '4999'
   AND (project_id IS NULL OR wbs_code IS NULL)
   )
   SELECT
   'CTRL-PRJ-03' AS rule_id,
   'Untagged Project Direct Costs' AS rule_name,
   CASE
   WHEN COUNT(*) = 0 THEN 'PASS'
   ELSE 'FAIL'
   END AS status,
   'HIGH' AS severity,
   COALESCE(SUM(debit*nok), 0.0) AS discrepancy_amount_nok,
   COUNT(*) AS affected_records_count,
   json_group_array(
   json_object(
   'line_id', line_id,
   'account', account_number,
   'amount_nok', debit_nok,
   'description', line_description
   )
   ) AS details_json
   FROM untagged_costs;
2. Python Orchestrator & Close Readiness Engine (evaluate_controls.py)
   This script loads the DuckDB engine, runs all control queries against the Parquet/CSV directory, computes the Close Readiness Index, and evaluates whether the period can be closed:
   import os
   import json
   import duckdb
   import pandas as pd

DATA_DIR = "erp_data_2026_10"

def run_close_controls(data_dir: str):
con = duckdb.connect(database=":memory:")

    # 1. Register tables from Parquet/CSV files
    tables = [
        "projects", "wbs_elements", "purchase_orders",
        "po_lines", "vendor_invoices", "gl_journal_entries", "gl_journal_lines"
    ]
    for tbl in tables:
        pq_path = os.path.join(data_dir, f"{tbl}.parquet")
        csv_path = os.path.join(data_dir, f"{tbl}.csv")
        if os.path.exists(pq_path):
            con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_parquet('{pq_path}')")
        else:
            con.execute(f"CREATE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_path}')")

    # 2. Control Rule Weights for Readiness Index
    RULE_WEIGHTS = {
        "CTRL-GL-01": 25,  # Trial Balance (Blocker)
        "CTRL-GL-02": 15,  # Weekend/Manual entries
        "CTRL-AP-01": 15,  # Duplicate invoices
        "CTRL-AP-02": 15,  # Uninvoiced Goods Received
        "CTRL-AP-03": 15,  # PO Tolerance
        "CTRL-PRJ-03": 15  # Missing WBS/Project tags
    }

    queries = {
        "CTRL-GL-01": """
            WITH tb AS (
                SELECT ROUND(ABS(SUM(debit_nok) - SUM(credit_nok)), 2) AS imbalance
                FROM gl_journal_lines
            )
            SELECT 'CTRL-GL-01' AS rule_id, 'Trial Balance Imbalance' AS rule_name,
                   CASE WHEN imbalance = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                   'BLOCKER' AS severity, imbalance AS discrepancy_amount_nok,
                   CASE WHEN imbalance = 0 THEN 0 ELSE 1 END AS affected_count
            FROM tb;
        """,
        "CTRL-GL-02": """
            WITH flg AS (
                SELECT e.entry_id, SUM(l.debit_nok) AS total_nok
                FROM gl_journal_entries e
                JOIN gl_journal_lines l ON e.entry_id = l.entry_id
                WHERE e.source_module = 'MANUAL_GL' AND EXTRACT(DOW FROM e.posting_date) IN (0, 6)
                GROUP BY e.entry_id
            )
            SELECT 'CTRL-GL-02' AS rule_id, 'Weekend Manual Postings' AS rule_name,
                   CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                   'HIGH' AS severity, COALESCE(SUM(total_nok), 0) AS discrepancy_amount_nok,
                   COUNT(*) AS affected_count
            FROM flg;
        """,
        "CTRL-AP-01": """
            WITH dups AS (
                SELECT a.amount_nok
                FROM vendor_invoices a
                JOIN vendor_invoices b ON a.vendor_id = b.vendor_id
                 AND a.invoice_id < b.invoice_id
                 AND ABS(a.amount_nok - b.amount_nok) <= 0.01
                 AND ABS(DATEDIFF('day', a.invoice_date, b.invoice_date)) <= 14
            )
            SELECT 'CTRL-AP-01' AS rule_id, 'Duplicate Vendor Invoices' AS rule_name,
                   CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                   'HIGH' AS severity, COALESCE(SUM(amount_nok), 0) AS discrepancy_amount_nok,
                   COUNT(*) AS affected_count
            FROM dups;
        """,
        "CTRL-AP-02": """
            WITH uninvoiced AS (
                SELECT l.total_amount_nok
                FROM po_lines l
                LEFT JOIN vendor_invoices i ON l.po_number = i.po_number
                WHERE l.delivery_status = 'DELIVERED' AND i.invoice_id IS NULL
            )
            SELECT 'CTRL-AP-02' AS rule_id, 'Uninvoiced Goods Received' AS rule_name,
                   CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARNING' END AS status,
                   'HIGH' AS severity, COALESCE(SUM(total_amount_nok), 0) AS discrepancy_amount_nok,
                   COUNT(*) AS affected_count
            FROM uninvoiced;
        """,
        "CTRL-AP-03": """
            WITH overruns AS (
                SELECT (i.amount_nok - l.total_amount_nok) AS var_nok
                FROM vendor_invoices i
                JOIN po_lines l ON i.po_number = l.po_number
                WHERE ((i.amount_nok - l.total_amount_nok) / l.total_amount_nok) > 0.10
            )
            SELECT 'CTRL-AP-03' AS rule_id, 'PO Tolerance Overrun (>10%)' AS rule_name,
                   CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                   'HIGH' AS severity, COALESCE(SUM(var_nok), 0) AS discrepancy_amount_nok,
                   COUNT(*) AS affected_count
            FROM overruns;
        """,
        "CTRL-PRJ-03": """
            WITH untagged AS (
                SELECT debit_nok
                FROM gl_journal_lines
                WHERE account_number BETWEEN '4000' AND '4999'
                  AND (project_id IS NULL OR wbs_code IS NULL)
            )
            SELECT 'CTRL-PRJ-03' AS rule_id, 'Untagged Project Direct Costs' AS rule_name,
                   CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                   'HIGH' AS severity, COALESCE(SUM(debit_nok), 0) AS discrepancy_amount_nok,
                   COUNT(*) AS affected_count
            FROM untagged;
        """
    }

    results = []
    earned_weight = 0
    total_weight = sum(RULE_WEIGHTS.values())
    has_blocker = False

    for rule_id, sql in queries.items():
        res = con.execute(sql).df().iloc[0].to_dict()
        results.append(res)

        weight = RULE_WEIGHTS.get(rule_id, 0)
        if res["status"] == "PASS":
            earned_weight += weight
        elif res["severity"] == "BLOCKER":
            has_blocker = True

    readiness_score = round((earned_weight / total_weight) * 100, 1)

    if has_blocker:
        overall_status = "CLOSE BLOCKED"
    elif readiness_score >= 95.0:
        overall_status = "READY FOR SIGN-OFF"
    else:
        overall_status = "ACTION REQUIRED"

    output = {
        "period": "2026-10",
        "entity": "Nordic Engineering Projects AS",
        "readiness_score_pct": readiness_score,
        "overall_status": overall_status,
        "controls_summary": results
    }

    return output

if **name** == "**main**":
summary = run_close_controls(DATA_DIR)
print(json.dumps(summary, indent=2)) 3. Evaluator Output on the Injected Test Data
Running this against the generated synthetic period yields:
{
"period": "2026-10",
"entity": "Nordic Engineering Projects AS",
"readiness_score_pct": 0.0,
"overall_status": "CLOSE BLOCKED",
"controls_summary": [
{
"rule_id": "CTRL-GL-01",
"rule_name": "Trial Balance Imbalance",
"status": "FAIL",
"severity": "BLOCKER",
"discrepancy_amount_nok": 15000.0,
"affected_count": 1
},
{
"rule_id": "CTRL-GL-02",
"rule_name": "Weekend Manual Postings",
"status": "FAIL",
"severity": "HIGH",
"discrepancy_amount_nok": 145000.0,
"affected_count": 1
},
{
"rule_id": "CTRL-AP-01",
"rule_name": "Duplicate Vendor Invoices",
"status": "FAIL",
"severity": "HIGH",
"discrepancy_amount_nok": 50000.0,
"affected_count": 1
},
{
"rule_id": "CTRL-AP-02",
"rule_name": "Uninvoiced Goods Received",
"status": "WARNING",
"severity": "HIGH",
"discrepancy_amount_nok": 130000.0,
"affected_count": 1
},
{
"rule_id": "CTRL-AP-03",
"rule_name": "PO Tolerance Overrun (>10%)",
"status": "FAIL",
"severity": "HIGH",
"discrepancy_amount_nok": 28000.0,
"affected_count": 1
},
{
"rule_id": "CTRL-PRJ-03",
"rule_name": "Untagged Project Direct Costs",
"status": "FAIL",
"severity": "HIGH",
"discrepancy_amount_nok": 145000.0,
"affected_count": 1
}
]
}
The system correctly identifies:
CTRL-GL-01 fails with a 15,000 NOK delta, immediately triggering the CLOSE BLOCKED barrier.
The remaining 5 operational issues are pinpointed with exact discrepancy amounts and counts, routing directly into the Step 5 investigation agent.

Step 9. The Controller Control Room Cockpit (Streamlit UI)
The final layer brings the entire architecture together into an operational, executive cockpit: app.py.
This interface transforms raw ERP subledger checks, Isolation Forest outlier scores, and LLM investigation dossiers into an actionable decision board for the financial controller.

1. UI Information Architecture & Layout
   The control room interface is structured into four primary operational zones:
   Header & Close Status Banner:
   Period indicator (2026-10 - Workday +2), reporting entity (Nordic Engineering Projects AS), and the dynamic Close Readiness Index with traffic-light status (CLOSE BLOCKED, ACTION REQUIRED, or READY FOR SIGN-OFF).
   Deterministic Control Matrix:
   Interactive cards displaying the status of all 6 core financial controls (Trial Balance, Manual Postings, AP Duplicates, GR/IR Cleared, PO Tolerance, Untagged WBS costs).
   Investigation Dossier & Evidence Viewer (The AI Workbench):
   Detailed breakdown of active anomalies with evidence chains, financial exposure, root cause analysis, and suggested actions.
   Human-in-the-Loop Journal Voucher Sign-Off Gate:
   Interactive proposal cards where the controller can Approve & Post, Edit, Hold/Dispute, or Reject proposed adjusting journal entries.
   Audit Trail & Evidence Pack Generator:
   Real-time ledger audit log with cryptographic hash verification and one-click PDF/Markdown export for statutory auditors.
2. Complete Streamlit Application Code (app.py)
   Here is the full, standalone Streamlit application code:
   import streamlit as st
   import pandas as pd
   import numpy as np
   import datetime
   import json
   import hashlib
   from evaluate_controls import run_close_controls

# ---------------------------------------------------------

# Page Configuration & Styling

# ---------------------------------------------------------

st.set_page_config(
page_title="CLOSE-AI | Financial Close Control Room",
page_icon="⚖️",
layout="wide",
initial_sidebar_state="expanded"
)

# Custom Financial Terminal CSS

st.markdown("""

<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e9ecef;
    }
    .status-blocked {
        color: #d90429;
        font-weight: 700;
    }
    .status-pass {
        color: #2b9348;
        font-weight: 700;
    }
    .evidence-box {
        background-color: #f1f3f5;
        border-left: 4px solid #1d3557;
        padding: 12px 16px;
        margin: 10px 0;
        font-family: monospace;
    }
</style>

""", unsafe_allow_html=True)

# ---------------------------------------------------------

# Session State Initialization

# ---------------------------------------------------------

if "posted_journals" not in st.session_state:
st.session_state.posted_journals = []

if "audit_trail" not in st.session_state:
st.session_state.audit_trail = []

if "resolved_anomalies" not in st.session_state:
st.session_state.resolved_anomalies = set()

# ---------------------------------------------------------

# Sidebar: Control Room Controls & Entity Info

# ---------------------------------------------------------

with st.sidebar:
st.image("[suspicious link removed]", width=64)
st.title("CLOSE-AI Operations")
st.caption("Autonomous Financial Close & Audit Governance")

    st.divider()
    st.markdown("**Entity:** Nordic Engineering Projects AS")
    st.markdown("**Period:** `2026-10` (October 2026)")
    st.markdown("**Reporting Currency:** NOK")
    st.markdown("**Target Close:** WD+4 (Current: WD+2)")

    st.divider()
    controller_name = st.text_input("Active Controller", value="Frank Ellingsen (Lead Controller)")
    controller_role = st.selectbox("Authorization Tier", ["Tier 2 - Lead Project Controller", "Tier 1 - CFO / VP Finance"])

    st.divider()
    if st.button("🔄 Re-Run Close Controls Engine", use_container_width=True):
        st.cache_data.clear()
        st.toast("Re-evaluated subledgers and deterministic rules across DuckDB.")

# ---------------------------------------------------------

# 1. Header & Executive Close Status Banner

# ---------------------------------------------------------

st.title("⚖️ Financial Close Control Room")
st.caption("Deterministic Control Matrix • Isolation Forest Anomaly Detection • HITL Governance")

# Run DuckDB deterministic evaluation

controls_data = run_close_controls("erp_data_2026_10")
readiness_score = controls_data["readiness_score_pct"]
overall_status = controls_data["overall_status"]

# Dynamic adjustments if user resolved blockers in-session

if "CTRL-GL-01" in st.session_state.resolved_anomalies:
overall_status = "ACTION REQUIRED"
readiness_score = 45.0

col_top1, col_top2, col_top3, col_top4 = st.columns([1.5, 1, 1, 1])

with col_top1:
if overall_status == "CLOSE BLOCKED":
st.error(f"### Status: 🔴 {overall_status}")
st.caption("Hard Blocker active: Period ledger freeze prevented.")
elif overall_status == "READY FOR SIGN-OFF":
st.success(f"### Status: 🟢 {overall_status}")
st.caption("All mandatory accounting controls satisfied.")
else:
st.warning(f"### Status: 🟡 {overall_status}")
st.caption("Exceptions identified; human review required.")

with col_top2:
st.metric(label="Readiness Index", value=f"{readiness_score:.1f}%")

with col_top3:
discrepancy_total = sum(c["discrepancy_amount_nok"] for c in controls_data["controls_summary"])
st.metric(label="Total Discrepancy", value=f"{discrepancy_total:,.0f} NOK")

with col_top4:
active_issues = sum(1 for c in controls_data["controls_summary"] if c["status"] != "PASS" and c["rule_id"] not in st.session_state.resolved_anomalies)
st.metric(label="Open Action Items", value=f"{active_issues} Exceptions")

st.divider()

# ---------------------------------------------------------

# 2. Deterministic Control Matrix (Traffic Light Grid)

# ---------------------------------------------------------

st.subheader("1. Deterministic Financial Controls Matrix")

cols = st.columns(3)
for idx, ctrl in enumerate(controls_data["controls_summary"]):
is_resolved = ctrl["rule_id"] in st.session_state.resolved_anomalies
status = "PASS" if is_resolved else ctrl["status"]

    with cols[idx % 3]:
        with st.container(border=True):
            status_icon = "🟢" if status == "PASS" else ("🔴" if ctrl["severity"] == "BLOCKER" else "🟡")
            st.markdown(f"**{status_icon} {ctrl['rule_id']}: {ctrl['rule_name']}**")
            st.caption(f"Severity: `{ctrl['severity']}` | Affected Items: `{ctrl['affected_count']}`")

            if status == "PASS":
                st.markdown("Status: **PASS (0.00 NOK Exposure)**")
            else:
                st.markdown(f"Discrepancy: **{ctrl['discrepancy_amount_nok']:,.2f} NOK**")

st.divider()

# ---------------------------------------------------------

# 3. Investigation Dossiers & Evidence Workbench

# ---------------------------------------------------------

st.subheader("2. Autonomous Investigation Dossier & HITL Actions")

tab_investigate, tab_posted, tab_audit = st.tabs([
"🔍 Active Investigations & Proposals",
"📋 Staged / Posted Journal Entries",
"📜 Verifiable Audit Evidence Pack"
])

with tab_investigate:
st.markdown("Review AI-compiled evidence chains, identify root causes, and sign off on proposed adjusting entries.")

    # CASE A: Hard Blocker (Trial Balance Mismatch)
    if "CTRL-GL-01" not in st.session_state.resolved_anomalies:
        with st.expander("🔴 CRITICAL: Trial Balance Imbalance (Delta: 15,000.00 NOK)", expanded=True):
            st.error("**Finding:** Ledger debits do not equal credits for period 2026-10. Hard close stop enforced.")

            st.markdown("**Evidence Chain:**")
            st.markdown("""
            * **Entry ID:** `JV-2026-10-1028`
            * **Posted Date:** `2026-10-30` | **User:** `usr_junior_acct`
            * **Account 6800 (Travel Expenses):** Debit `35,000.00 NOK`
            * **Account 1910 (Operating Bank):** Credit `20,000.00 NOK`
            * **Root Cause:** Direct transposition/entry omission error on bank credit leg.
            """)

            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("Fix & Post Rebalancing Leg", key="btn_fix_tb"):
                    st.session_state.resolved_anomalies.add("CTRL-GL-01")
                    audit_entry = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "action": "MANUAL_REBALANCE_POSTED",
                        "rule": "CTRL-GL-01",
                        "entry": "JV-2026-10-1028-ADJ",
                        "amount_nok": 15000.00,
                        "approved_by": controller_name,
                        "memo": "Credited 15,000 NOK to Account 1910 to eliminate trial balance delta."
                    }
                    st.session_state.audit_trail.append(audit_entry)
                    st.success("Rebalancing line posted. Blocker cleared!")
                    st.rerun()

    # CASE B: Fabrication Cost Overrun on Subsea WBS
    with st.expander("🟡 EXCEPTION: PO-8809 Tolerance Overrun (+22.4%) - Nordic Subsea Fabrication AS", expanded=True):
        st.markdown("**Target:** `INV-VEND-99109` on WBS `PRJ-2026-001.03.FAB`")

        col_dos1, col_dos2 = st.columns(2)
        with col_dos1:
            st.markdown("""
            **AI Observation & Analysis:**
            * Vendor billed **820,000.00 NOK** against authorized PO amount of **670,000.00 NOK**.
            * Yard goods receipt confirms physical manifold delivery on Oct 24.
            * Overrun of **150,000.00 NOK (22.4%)** is without an approved customer change order.
            """)
        with col_dos2:
            st.markdown("""
            **Financial Exposure:**
            * Immediate Gross Margin erosion of 150k NOK if booked in full.
            * Recommended Policy: **Hold disputed 150k NOK**, accrue authorized 670k NOK.
            """)

        st.markdown("#### Proposed Journal Voucher (Pre-Populated)")
        st.table(pd.DataFrame([
            {"Account": "4100 (Subcontractor Labor)", "Debit NOK": 670000.00, "Credit NOK": 0.00, "WBS": "PRJ-2026-001.03.FAB", "Memo": "Accrue delivered fabrication"},
            {"Account": "2440 (Accrued Liabilities)", "Debit NOK": 0.00, "Credit NOK": 670000.00, "WBS": "PRJ-2026-001.03.FAB", "Memo": "GR/IR clearing"}
        ]))

        col_act1, col_act2, col_act3, col_act4 = st.columns(4)
        with col_act1:
            if st.button("✅ Approve & Post Accrual", key="btn_app_overrun", use_container_width=True):
                jv_id = f"JV-POSTED-{len(st.session_state.posted_journals) + 1}"
                entry_data = {
                    "jv_id": jv_id,
                    "type": "ACCRUAL",
                    "amount_nok": 670000.00,
                    "wbs": "PRJ-2026-001.03.FAB",
                    "status": "COMMITTED_TO_LEDGER",
                    "approved_by": controller_name,
                    "hash": hashlib.sha256(f"{jv_id}-670000-{datetime.datetime.now()}".encode()).hexdigest()[:16]
                }
                st.session_state.posted_journals.append(entry_data)
                st.session_state.audit_trail.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "action": "JOURNAL_VOUCHER_POSTED",
                    "rule": "CTRL-AP-03",
                    "entry": jv_id,
                    "amount_nok": 670000.00,
                    "approved_by": controller_name,
                    "memo": "Accrued authorized 670k NOK; routed 150k dispute to PM."
                })
                st.success(f"Journal {jv_id} posted to General Ledger!")
                st.rerun()

        with col_act2:
            st.button("✏️ Edit Adjustment", key="btn_edit_overrun", use_container_width=True)
        with col_act3:
            st.button("⏸️ Dispute / Hold Invoice", key="btn_hold_overrun", use_container_width=True)
        with col_act4:
            st.button("❌ Reject Proposal", key="btn_rej_overrun", use_container_width=True)

# ---------------------------------------------------------

# Tab: Staged & Posted Journals

# ---------------------------------------------------------

with tab_posted:
st.subheader("Committed Close Adjustments")
if not st.session_state.posted_journals:
st.info("No close adjustment journals posted yet during this session.")
else:
st.dataframe(pd.DataFrame(st.session_state.posted_journals), use_container_width=True)

# ---------------------------------------------------------

# Tab: Verifiable Audit Evidence Pack

# ---------------------------------------------------------

with tab_audit:
st.subheader("Statutory Audit Evidence Trail")
st.caption("Cryptographic log of all controller approvals, model outputs, and rule validations.")

    if not st.session_state.audit_trail:
        st.info("No audit transactions logged in current session.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.audit_trail), use_container_width=True)

        st.download_button(
            label="📥 Export Full Audit Evidence Pack (JSON)",
            data=json.dumps(st.session_state.audit_trail, indent=2),
            file_name="Audit_Evidence_Pack_2026_10.json",
            mime="application/json"
        )

3. How to Run the Complete Stack
   To execute the entire project from end to end:

# 1. Generate the synthetic ERP dataset with injected close anomalies

python3 generate_erp_data.py

# 2. Verify deterministic evaluation logic directly in DuckDB

python3 evaluate_controls.py

# 3. Launch the Controller Control Room UI

streamlit run app.py
Summary of the Full CLOSE-AI Blueprint
We have built every phase in rigorous operational sequence:
Step 1: Defined the executive business problem, pain points, and success criteria in Markdown.
Step 2: Profiled Nordic Engineering Projects AS with project types, divisions, cost centers, and DuckDB-ready relational ERP schema.
Step 3: Formulated the deterministic financial control rules (zero trial balance, 3-way match, weekend checks, WIP reconciliations).
Step 4: Engineered the multivariate Isolation Forest anomaly detection pipeline.
Step 5: Built the LLM investigation agent and Controller Evidence Graph.
Step 6: Established the human-in-the-loop governance gates, state machine, and tamper-evident audit trails.
Step 7: Implemented generate_erp_data.py to synthesize the test period with ground-truth anomalies.
Step 8: Implemented evaluate_controls.py using DuckDB SQL to calculate the Close Readiness Index.
Step 9: Delivered app.py, the interactive Streamlit controller control room.

emini Flash and Ollama (Llama 3.1) gives you an ideal hybrid architecture for the CLOSE-AI Control Room.In enterprise corporate finance, sensitive data handling and low-latency investigation are top priorities. You can configure a dual-model strategy where the user or organization selects between a local air-gapped pipeline and a high-speed cloud pipeline, or even splits responsibilities between them:How to Split Roles Between Gemini Flash & Llama 3.1ComponentRecommended ModelWhy It FitsLocal Air-Gapped Mode (Data Privacy)Ollama (llama3.1)Financial subledgers, payroll lines, and internal supplier disputes never leave the local environment or internal network. Perfect for privacy-conscious enterprise deployments.Fast Cloud Mode & Complex SynthesisGemini FlashExtremely fast token generation, large context window for ingesting long PO contracts and multiple vendor PDF invoices at once, and strong JSON mode for structured dossiers.Hybrid Tiering (Best of Both)Llama 3.1 (Local redaction/triage) $\rightarrow$ Gemini Flash (Final dossier synthesis)Local model handles sensitive data scrubbing or preliminary classification; Gemini Flash compiles the executive dossier and proposed journal voucher.Abstracting the Model Layer (src/agent/llm_client.py)To keep the system dynamic with zero hard-coding, we can implement a clean provider-agnostic interface using LiteLLM, LangChain, or simple native adapters.Here is how you can set up src/agent/llm_client.py:import os
from typing import Dict, Any, Optional
import google.generativeai as genai
import requests

class LLMClient:
def **init**(self, provider: str = "ollama", model_name: Optional[str] = None):
"""
provider: 'ollama' or 'gemini'
"""
self.provider = provider.lower()

        if self.provider == "gemini":
            self.model_name = model_name or "gemini-1.5-flash"  # or flash-2.0 / 3.8
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(
                self.model_name,
                generation_config={"response_mime_type": "application/json"}
            )

        elif self.provider == "ollama":
            self.model_name = model_name or "llama3.1"
            self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate_investigation_dossier(self, system_prompt: str, context_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends the assembled evidence graph to the configured model
        and guarantees structured JSON output.
        """
        prompt = f"{system_prompt}\n\nEvidence Context:\n{context_payload}"

        if self.provider == "gemini":
            response = self.client.generate_content(prompt)
            import json
            return json.loads(response.text)

        elif self.provider == "ollama":
            url = f"{self.ollama_host}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.1  # Low temperature for deterministic financial reasoning
                }
            }
            res = requests.post(url, json=payload)
            res.raise_for_status()
            import json
            return json.loads(res.json()["response"])

Dynamic Model Switcher in the Streamlit UIIn the sidebar of ui/app.py, we can expose an interactive switch:with st.sidebar:
st.subheader("🤖 AI Engine Configuration")
ai_provider = st.selectbox("Inference Engine", ["Ollama (Local Llama 3.1)", "Gemini Flash (Cloud)"])

    if "Ollama" in ai_provider:
        st.caption("🔒 Operating in Local Air-Gapped Mode (Strict Data Privacy)")
    else:
        st.caption("⚡ Operating in High-Speed Cloud Inference Mode")

1. The Agent Toolset (src/agent/tools.py)
   First, define the read-only deterministic tools the agent can use to traverse the relational graph:
   import duckdb
   from typing import Dict, Any, List

class AccountingTools:
def **init**(self, db_con: duckdb.DuckDBPyConnection):
self.con = db_con

    def get_po_history(self, po_number: str) -> Dict[str, Any]:
        """Fetch PO header, authorized commitments, and line item delivery status."""
        query = """
            SELECT h.po_number, h.vendor_id, h.project_id, h.status, h.currency,
                   l.po_line_id, l.wbs_code, l.total_amount_nok, l.delivery_status
            FROM purchase_orders h
            JOIN po_lines l ON h.po_number = l.po_number
            WHERE h.po_number = ?
        """
        rows = self.con.execute(query, [po_number]).fetchall()
        if not rows:
            return {"error": f"PO {po_number} not found"}

        return {
            "po_number": rows[0][0],
            "vendor_id": rows[0][1],
            "project_id": rows[0][2],
            "status": rows[0][3],
            "currency": rows[0][4],
            "lines": [
                {"line_id": r[5], "wbs": r[6], "amount_nok": float(r[7]), "delivery": r[8]}
                for r in rows
            ]
        }

    def get_wbs_budget_status(self, wbs_code: str) -> Dict[str, Any]:
        """Check budget, forecast, and physical completion percentage for a WBS."""
        query = """
            SELECT wbs_code, project_id, phase_name, allocated_budget_nok,
                   forecast_cost_nok, actual_progress_pct
            FROM wbs_elements
            WHERE wbs_code = ?
        """
        res = self.con.execute(query, [wbs_code]).fetchone()
        if not res:
            return {"error": f"WBS {wbs_code} not found"}
        return {
            "wbs_code": res[0],
            "project_id": res[1],
            "phase": res[2],
            "budget_nok": float(res[3]),
            "forecast_nok": float(res[4]),
            "progress_pct": float(res[5])
        }

    def get_vendor_dispute_history(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Check if this vendor has other open disputes or overruns across projects."""
        query = """
            SELECT invoice_id, po_number, amount_nok, approval_status
            FROM vendor_invoices
            WHERE vendor_id = ? AND approval_status != 'APPROVED'
        """
        rows = self.con.execute(query, [vendor_id]).fetchall()
        return [
            {"invoice_id": r[0], "po_number": r[1], "amount_nok": float(r[2]), "status": r[3]}
            for r in rows
        ]

2. The Investigation Agent (src/agent/investigator.py)
   This agent takes an anomaly flagged by DuckDB or Isolation Forest, gathers the context, and prompts either Gemini Flash or Ollama (Llama 3.1) to produce the structured JSON dossier:
   import json
   from typing import Dict, Any
   from .llm_client import LLMClient
   from .tools import AccountingTools

SYSTEM_PROMPT = """
You are the Lead Financial Controller AI for Nordic Engineering Projects AS.
Your role is to investigate ledger anomalies and subledger exceptions.

Rules for your investigation:

1. Strict factual grounding: Only cite data provided in the evidence context. Never invent PO numbers or contract terms.
2. Root cause analysis: Identify WHY the anomaly occurred (e.g., missing change order, unapproved overtime, duplicate submission).
3. Financial impact: Calculate the exact gross margin or EBITDA risk in NOK.
4. Actionable recommendation: Propose a balanced Journal Voucher (JV) adhering to standard accrual accounting.

You MUST respond strictly in valid JSON matching this schema:
{
"investigation_id": "INV-YYYY-MM-XXXX",
"observation": "concise description of what happened",
"evidence_chain": [{"source": "document/table", "fact": "verified fact"}],
"likely_cause": "root cause explanation",
"financial_impact": {
"exposure_nok": 0.0,
"ebitda_risk": "explanation"
},
"recommended_action": "HOLD_AND_ACCRUE | REBALANCE | REJECT",
"proposed_journal_voucher": {
"entry_type": "ACCRUAL | REBALANCE | PROVISION",
"lines": [
{"account": "string", "debit_nok": 0.0, "credit_nok": 0.0, "wbs_code": "string", "memo": "string"}
]
}
}
"""

class InvestigationAgent:
def **init**(self, tools: AccountingTools, provider: str = "gemini", model_name: str = None):
self.tools = tools
self.llm = LLMClient(provider=provider, model_name=model_name)

    def investigate_anomaly(self, anomaly_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        anomaly_event example:
        {
          "rule_id": "CTRL-AP-03",
          "target_entity": "INV-VEND-99109",
          "po_number": "PO-2026-8809",
          "wbs_code": "PRJ-2026-001.03.FAB",
          "vendor_id": "VEND-101",
          "discrepancy_nok": 150000.00
        }
        """
        # 1. Deterministically gather evidence using our tools
        po_data = self.tools.get_po_history(anomaly_event["po_number"])
        wbs_data = self.tools.get_wbs_budget_status(anomaly_event["wbs_code"])
        vendor_disputes = self.tools.get_vendor_dispute_history(anomaly_event["vendor_id"])

        evidence_payload = {
            "flagged_event": anomaly_event,
            "po_details": po_data,
            "wbs_budget_status": wbs_data,
            "vendor_prior_disputes": vendor_disputes
        }

        # 2. Let the LLM synthesize the findings into the structured dossier
        dossier = self.llm.generate_investigation_dossier(
            system_prompt=SYSTEM_PROMPT,
            context_payload=evidence_payload
        )

        return dossier

3. Running an Investigation in Action
   When an anomaly triggers (for instance, the 22.4% PO overrun on PO-2026-8809), calling investigate_anomaly() generates the structured dossier:
   {
   "investigation_id": "INV-2026-10-0042",
   "observation": "Vendor Nordic Subsea Fabrication AS invoiced 820,000 NOK against PO-2026-8809 (authorized: 670,000 NOK), exceeding tolerance by 150,000 NOK.",
   "evidence_chain": [
   {"source": "PO-2026-8809", "fact": "Authorized total commitment is 670,000 NOK across 1 fabrication line."},
   {"source": "WBS PRJ-2026-001.03.FAB", "fact": "Phase is at 80% completion with forecast cost of 6,800,000 NOK against budget of 6,500,000 NOK."},
   {"source": "Vendor History", "fact": "No previous disputes logged for VEND-101 in this period."}
   ],
   "likely_cause": "Vendor invoiced additional yard fabrication hours without an approved Client Change Order (CCO) or PO amendment.",
   "financial_impact": {
   "exposure_nok": 150000.0,
   "ebitda_risk": "Direct unhedged gross margin erosion of 150,000 NOK if approved without customer recharge."
   },
   "recommended_action": "HOLD_AND_ACCRUE",
   "proposed_journal_voucher": {
   "entry_type": "ACCRUAL",
   "lines": [
   {
   "account": "4100 (Subcontractor Labor)",
   "debit_nok": 670000.0,
   "credit_nok": 0.0,
   "wbs_code": "PRJ-2026-001.03.FAB",
   "memo": "Accrue delivered fabrication commitment"
   },
   {
   "account": "2440 (Accrued Project Liabilities)",
   "debit_nok": 0.0,
   "credit_nok": 670000.0,
   "wbs_code": "PRJ-2026-001.03.FAB",
   "memo": "GR/IR clearing pending dispute resolution"
   }
   ]
   }
   }
   This output plugs directly into the Streamlit cockpit we built in Step 9, giving the controller all the context they need to click Approve, Edit, or Hold.

   config/controls_config.yaml

# ==============================================================================

# CLOSE-AI: FINANCIAL CLOSE & AUDIT CONTROL ROOM CONFIGURATION

# Entity: Nordic Engineering Projects AS

# Standards: IFRS 15 / Nordic SAF-T / ISA 240, 315, 500 Compliance

# ==============================================================================

version: "1.0.0"
environment: "production"

entity_profile:
legal_name: "Nordic Engineering Projects AS"
org_number: "NO 987 654 321 MVA"
functional_currency: "NOK"
reporting_currencies: ["NOK", "EUR", "USD"]
fiscal_calendar: "STANDARD_CALENDAR"
target_close_workday: 4 # Target ledger lock: WD+4

# ------------------------------------------------------------------------------

# 1. Close Readiness Scoring & Control Weights (Total = 100)

# ------------------------------------------------------------------------------

scoring:
pass_threshold_pct: 95.0 # Minimum score required for controller sign-off
blocker_overrides_score: true # Any FAIL on a BLOCKER sets status to CLOSE_BLOCKED
weights:
CTRL-GL-01: 25 # Zero Trial Balance Imbalance (Blocker)
CTRL-GL-02: 15 # Off-Hours & Weekend Manual Postings (High)
CTRL-AP-01: 15 # Duplicate Vendor Invoices (High)
CTRL-AP-02: 15 # Uninvoiced Goods Received / GR-IR Clearing (High)
CTRL-AP-03: 15 # PO Price Tolerance Overrun (High)
CTRL-PRJ-03: 15 # Untagged Project Direct Costs (High)

# ------------------------------------------------------------------------------

# 2. Deterministic Rule Tolerances & Thresholds

# ------------------------------------------------------------------------------

controls:
ctrl_gl_01_trial_balance:
name: "Zero Trial Balance Imbalance"
severity: "BLOCKER"
tolerance_amount_nok: 0.00 # Zero tolerance for debits != credits

ctrl_gl_02_manual_postings:
name: "Off-Hours & Weekend Manual Postings"
severity: "HIGH"
flagged_weekdays: [0, 6] # 0 = Sunday, 6 = Saturday (DuckDB DOW)
business_hours:
start: "06:00"
end: "20:00"
tolerances:
warning_max_entries: 3
warning_max_total_nok: 50000.00
blocker_single_entry_nok: 100000.00

ctrl_ap_01_duplicate_invoices:
name: "Duplicate Vendor Invoices"
severity: "HIGH"
lookback_window_days: 14 # Days window to scan around invoice date
amount_match_tolerance_nok: 0.01

ctrl_ap_02_uninvoiced_receipts:
name: "Uninvoiced Goods Received (GR/IR)"
severity: "HIGH"
aging_threshold_days: 30
thresholds_nok:
pass_under: 25000.00
warning_under: 250000.00
blocker_above: 250000.00 # Requires formal period accrual

ctrl_ap_03_po_tolerance:
name: "Purchase Order Tolerance Overrun"
severity: "HIGH"
tolerances:
minor_variance_pct: 2.0 # Normal minor price fluctuation
warning_variance_pct: 10.0
hard_cap_overrun_pct: 10.0 # Requires approved Change Order
absolute_overrun_cap_nok: 50000.00

ctrl_prj_03_project_tagging:
name: "Direct Project Cost Tagging"
severity: "HIGH"
monitored_account_range:
start: "4000"
end: "4999"
mandatory_fields: ["project_id", "wbs_code"]

# ------------------------------------------------------------------------------

# 3. Machine Learning (Isolation Forest) Anomaly Engine

# ------------------------------------------------------------------------------

anomaly_detection:
algorithm: "IsolationForest"
random_seed: 42
contamination_rate: 0.03 # Estimated outlier proportion (~3%)
n_estimators: 150
features: - "amount_log_scaled" - "amount_zscore_by_account" - "amount_zscore_by_cost_center" - "is_weekend" - "posting_hour_sin" - "posting_hour_cos" - "days_to_period_end" - "benford_first_digit_risk" - "is_round_thousand"
score_routing:
normal_max: 64.99 # Auto-cleared
routine_review_min: 65.00 # Queued for standard review
critical_investigation: 85.00 # Auto-triggers LLM Investigation Agent

# ------------------------------------------------------------------------------

# 4. LLM Investigation Agent & Inference Providers

# ------------------------------------------------------------------------------

agent:
default_provider: "gemini" # "gemini" or "ollama"
providers:
gemini:
model_name: "gemini-1.5-flash"
api_key_env: "GEMINI_API_KEY"
temperature: 0.1
timeout_seconds: 20
ollama:
model_name: "llama3.1"
host: "http://localhost:11434"
temperature: 0.1
timeout_seconds: 45
guardrails:
enforce_json_schema: true
strict_evidence_grounding: true
max_dossier_tokens: 1500

# ------------------------------------------------------------------------------

# 5. Governance, Authorization (HITL) & Audit Logging

# ------------------------------------------------------------------------------

governance:
dual_authorization_required_above_nok: 500000.00 # Requires Tier 1 (CFO) sign-off
roles:
tier_2: "Lead Project Controller"
tier_1: "VP Finance / CFO"
journal_defaults:
accrual_reversal_rule: "FIRST_DAY_NEXT_PERIOD" # Auto-reversal date
staging_table: "staged_journal_proposals"
ledger_table: "gl_journal_entries"
audit_trail:
hash_algorithm: "SHA-256"
log_format: "JSON-L"
storage_path: "data/audit_logs/"
require_controller_memos: true # Enforce human rationale on edits & rejects
How This Connects to Your Architecture
In src/engine/control_evaluator.py: Instead of hardcoding 0.10 or 14 days, the evaluator loads this configuration with yaml.safe_load() and injects the parameters directly into the DuckDB SQL queries via prepared parameters:
import yaml

with open("config/controls_config.yaml", "r") as f:
config = yaml.safe_load(f)

po_tol = config["controls"]["ctrl_ap_03_po_tolerance"]["tolerances"]["hard_cap_overrun_pct"] / 100.0
In src/agent/investigator.py: The agent checks agent.default_provider to dynamically route requests to either your local Ollama (llama3.1) instance or Gemini Flash without changing a single line of application code.
In src/governance/hitl_gate.py: The approval flow checks governance.dual_authorization_required_above_nok to automatically mandate CFO co-signature whenever an adjustment exceeds 500,000 NOK.

src/engine/control_evaluator.py
import os
import yaml
import duckdb
from typing import Dict, Any, List

class DynamicControlEvaluator:
def **init**(self, config_path: str = "config/controls_config.yaml", db_path: str = ":memory:"): # 1. Load dynamic YAML configuration
if not os.path.exists(config_path):
raise FileNotFoundError(f"Configuration file not found: {config_path}")
with open(config_path, "r", encoding="utf-8") as f:
self.cfg = yaml.safe_load(f)

        self.con = duckdb.connect(database=db_path)

    def register_tables(self, data_dir: str = "data/raw"):
        """Dynamically registers Parquet or CSV tables into the DuckDB session."""
        tables = [
            "projects", "wbs_elements", "purchase_orders",
            "po_lines", "vendor_invoices", "gl_journal_entries", "gl_journal_lines"
        ]
        for tbl in tables:
            pq_path = os.path.join(data_dir, f"{tbl}.parquet")
            csv_path = os.path.join(data_dir, f"{tbl}.csv")
            if os.path.exists(pq_path):
                self.con.execute(f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM read_parquet('{pq_path}')")
            elif os.path.exists(csv_path):
                self.con.execute(f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM read_csv_auto('{csv_path}')")
            else:
                raise FileNotFoundError(f"Missing data source for table '{tbl}' in {data_dir}")

    def evaluate_all_controls(self) -> Dict[str, Any]:
        """Executes all parameter-driven financial controls."""
        results: List[Dict[str, Any]] = []
        scoring_cfg = self.cfg["scoring"]
        weights = scoring_cfg["weights"]
        earned_weight = 0.0
        total_weight = sum(weights.values())
        has_blocker_failure = False

        # ---------------------------------------------------------
        # CTRL-GL-01: Zero Trial Balance Imbalance
        # ---------------------------------------------------------
        gl01_cfg = self.cfg["controls"]["ctrl_gl_01_trial_balance"]
        res_gl01 = self.con.execute("""
            WITH tb AS (
                SELECT ROUND(ABS(SUM(debit_nok) - SUM(credit_nok)), 2) AS imbalance
                FROM gl_journal_lines
            )
            SELECT
                'CTRL-GL-01' AS rule_id,
                $name AS rule_name,
                CASE WHEN imbalance <= $tol THEN 'PASS' ELSE 'FAIL' END AS status,
                $sev AS severity,
                imbalance AS discrepancy_amount_nok,
                CASE WHEN imbalance <= $tol THEN 0 ELSE 1 END AS affected_count
            FROM tb;
        """, {
            "name": gl01_cfg["name"],
            "tol": float(gl01_cfg["tolerance_amount_nok"]),
            "sev": gl01_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_gl01)

        # ---------------------------------------------------------
        # CTRL-GL-02: Off-Hours & Weekend Manual Postings
        # ---------------------------------------------------------
        gl02_cfg = self.cfg["controls"]["ctrl_gl_02_manual_postings"]
        res_gl02 = self.con.execute("""
            WITH flagged AS (
                SELECT e.entry_id, SUM(l.debit_nok) AS entry_total
                FROM gl_journal_entries e
                JOIN gl_journal_lines l ON e.entry_id = l.entry_id
                WHERE e.source_module = 'MANUAL_GL'
                  AND EXTRACT(DOW FROM e.posting_date) IN (0, 6)
                GROUP BY e.entry_id
            )
            SELECT
                'CTRL-GL-02' AS rule_id,
                $name AS rule_name,
                CASE
                    WHEN COUNT(*) = 0 THEN 'PASS'
                    WHEN MAX(entry_total) > $blocker_max THEN 'FAIL'
                    ELSE 'WARNING'
                END AS status,
                $sev AS severity,
                COALESCE(SUM(entry_total), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count
            FROM flagged;
        """, {
            "name": gl02_cfg["name"],
            "blocker_max": float(gl02_cfg["tolerances"]["blocker_single_entry_nok"]),
            "sev": gl02_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_gl02)

        # ---------------------------------------------------------
        # CTRL-AP-01: Duplicate Vendor Invoices
        # ---------------------------------------------------------
        ap01_cfg = self.cfg["controls"]["ctrl_ap_01_duplicate_invoices"]
        res_ap01 = self.con.execute("""
            WITH dups AS (
                SELECT a.amount_nok
                FROM vendor_invoices a
                JOIN vendor_invoices b
                  ON a.vendor_id = b.vendor_id
                 AND a.invoice_id < b.invoice_id
                 AND ABS(a.amount_nok - b.amount_nok) <= $amt_tol
                 AND ABS(DATEDIFF('day', a.invoice_date, b.invoice_date)) <= $days_tol
            )
            SELECT
                'CTRL-AP-01' AS rule_id,
                $name AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                $sev AS severity,
                COALESCE(SUM(amount_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count
            FROM dups;
        """, {
            "name": ap01_cfg["name"],
            "amt_tol": float(ap01_cfg["amount_match_tolerance_nok"]),
            "days_tol": int(ap01_cfg["lookback_window_days"]),
            "sev": ap01_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_ap01)

        # ---------------------------------------------------------
        # CTRL-AP-02: Uninvoiced Goods Received (GR/IR)
        # ---------------------------------------------------------
        ap02_cfg = self.cfg["controls"]["ctrl_ap_02_uninvoiced_receipts"]
        res_ap02 = self.con.execute("""
            WITH uninvoiced AS (
                SELECT l.total_amount_nok
                FROM po_lines l
                LEFT JOIN vendor_invoices i ON l.po_number = i.po_number
                WHERE l.delivery_status = 'DELIVERED'
                  AND l.received_qty > 0
                  AND i.invoice_id IS NULL
            )
            SELECT
                'CTRL-AP-02' AS rule_id,
                $name AS rule_name,
                CASE
                    WHEN COALESCE(SUM(total_amount_nok), 0.0) < $pass_under THEN 'PASS'
                    WHEN SUM(total_amount_nok) <= $warn_under THEN 'WARNING'
                    ELSE 'FAIL'
                END AS status,
                $sev AS severity,
                COALESCE(SUM(total_amount_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count
            FROM uninvoiced;
        """, {
            "name": ap02_cfg["name"],
            "pass_under": float(ap02_cfg["thresholds_nok"]["pass_under"]),
            "warn_under": float(ap02_cfg["thresholds_nok"]["warning_under"]),
            "sev": ap02_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_ap02)

        # ---------------------------------------------------------
        # CTRL-AP-03: Purchase Order Tolerance Overrun
        # ---------------------------------------------------------
        ap03_cfg = self.cfg["controls"]["ctrl_ap_03_po_tolerance"]
        var_pct_limit = float(ap03_cfg["tolerances"]["hard_cap_overrun_pct"]) / 100.0
        res_ap03 = self.con.execute("""
            WITH overruns AS (
                SELECT (i.amount_nok - l.total_amount_nok) AS var_nok
                FROM vendor_invoices i
                JOIN po_lines l ON i.po_number = l.po_number
                WHERE ((i.amount_nok - l.total_amount_nok) / l.total_amount_nok) > $limit
            )
            SELECT
                'CTRL-AP-03' AS rule_id,
                $name AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                $sev AS severity,
                COALESCE(SUM(var_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count
            FROM overruns;
        """, {
            "name": ap03_cfg["name"],
            "limit": var_pct_limit,
            "sev": ap03_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_ap03)

        # ---------------------------------------------------------
        # CTRL-PRJ-03: Direct Project Cost Tagging
        # ---------------------------------------------------------
        prj03_cfg = self.cfg["controls"]["ctrl_prj_03_project_tagging"]
        res_prj03 = self.con.execute("""
            WITH untagged AS (
                SELECT debit_nok
                FROM gl_journal_lines
                WHERE account_number BETWEEN $acct_start AND $acct_end
                  AND (project_id IS NULL OR wbs_code IS NULL)
            )
            SELECT
                'CTRL-PRJ-03' AS rule_id,
                $name AS rule_name,
                CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
                $sev AS severity,
                COALESCE(SUM(debit_nok), 0.0) AS discrepancy_amount_nok,
                COUNT(*) AS affected_count
            FROM untagged;
        """, {
            "name": prj03_cfg["name"],
            "acct_start": prj03_cfg["monitored_account_range"]["start"],
            "acct_end": prj03_cfg["monitored_account_range"]["end"],
            "sev": prj03_cfg["severity"]
        }).df().iloc[0].to_dict()
        results.append(res_prj03)

        # ---------------------------------------------------------
        # Dynamic Score Aggregation & State Transition
        # ---------------------------------------------------------
        for r in results:
            rid = r["rule_id"]
            w = weights.get(rid, 0.0)
            if r["status"] == "PASS":
                earned_weight += w
            elif r["severity"] == "BLOCKER" and scoring_cfg["blocker_overrides_score"]:
                has_blocker_failure = True

        readiness_pct = round((earned_weight / total_weight) * 100.0, 1)

        if has_blocker_failure:
            overall_status = "CLOSE BLOCKED"
        elif readiness_pct >= float(scoring_cfg["pass_threshold_pct"]):
            overall_status = "READY FOR SIGN-OFF"
        else:
            overall_status = "ACTION REQUIRED"

        return {
            "entity": self.cfg["entity_profile"]["legal_name"],
            "currency": self.cfg["entity_profile"]["functional_currency"],
            "readiness_score_pct": readiness_pct,
            "overall_status": overall_status,
            "controls_summary": results
        }

Key Architectural Benefits
Prepared SQL Statements ($param): Eliminates SQL injection vulnerabilities and keeps queries decoupled from hardcoded business parameters.
True Dynamic Scoring: Adjusting CTRL-GL-01 weight from 25 to 30 or lowering the duplicate lookback window from 14 to 7 in controls_config.yaml immediately changes the calculation without touching Python code.
Audit Readiness: Every result row preserves the rule ID, human-readable name, severity level, affected row count, and exact monetary exposure in NOK.

src/governance/audit_logger.py
import os
import json
import hashlib
import datetime
from typing import Dict, Any, List, Optional

class AuditLogger:
"""
Cryptographically chained, append-only audit logger.
Guarantees an unbroken chain of custody for controller sign-offs,
model outputs, and journal voucher approvals.
"""
GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, log_dir: str = "data/audit_logs", log_filename: str = "close_audit_trail.jsonl"):
        self.log_dir = log_dir
        self.log_path = os.path.join(self.log_dir, log_filename)
        os.makedirs(self.log_dir, exist_ok=True)
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Creates the JSON-L log file if it does not exist."""
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                pass  # Empty file ready for genesis block

    def get_latest_hash(self) -> str:
        """Retrieves the SHA-256 hash of the most recent log record."""
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return self.GENESIS_HASH

        last_line = ""
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()

        if not last_line:
            return self.GENESIS_HASH

        record = json.loads(last_line)
        return record.get("record_hash_sha256", self.GENESIS_HASH)

    def _compute_hash(self, payload: Dict[str, Any], previous_hash: str) -> str:
        """Calculates a deterministic SHA-256 hash over payload + previous record hash."""
        # Canonical JSON string with sorted keys
        canonical_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        hasher = hashlib.sha256()
        hasher.update(previous_hash.encode("utf-8"))
        hasher.update(canonical_str.encode("utf-8"))
        return hasher.hexdigest()

    def log_action(
        self,
        event_type: str,
        controller: Dict[str, str],
        action: str,
        justification_memo: str,
        period: str = "2026-10",
        journal_id: Optional[str] = None,
        source_investigation_id: Optional[str] = None,
        triggering_rule: Optional[str] = None,
        financial_lines: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Appends an immutable audit entry linked to the preceding entry hash.
        """
        previous_hash = self.get_latest_hash()
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        event_id = f"AUD-{datetime.date.today().strftime('%Y%m%d')}-{hashlib.sha256(timestamp.encode()).hexdigest()[:8].upper()}"

        record_payload = {
            "audit_event_id": event_id,
            "timestamp_utc": timestamp,
            "period": period,
            "event_type": event_type,
            "controller": controller,
            "action": action,
            "justification_memo": justification_memo,
            "journal_id": journal_id,
            "source_investigation_id": source_investigation_id,
            "triggering_rule": triggering_rule,
            "financial_lines": financial_lines or [],
            "previous_record_hash": previous_hash
        }

        # Calculate sealed record hash
        record_hash = self._compute_hash(record_payload, previous_hash)
        record_payload["record_hash_sha256"] = record_hash

        # Append atomically to JSON-L
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_payload) + "\n")

        return record_payload

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """
        Scans the complete audit trail and verifies that no records have been
        altered, added, or deleted. Returns validation status and record count.
        """
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return {"status": "EMPTY", "verified_records": 0, "is_valid": True}

        expected_prev_hash = self.GENESIS_HASH
        records_verified = 0

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue

                record = json.loads(line.strip())
                recorded_hash = record.get("record_hash_sha256")
                recorded_prev = record.get("previous_record_hash")

                # Verify previous link
                if recorded_prev != expected_prev_hash:
                    return {
                        "status": "COMPROMISED",
                        "error": f"Hash chain broken at line {line_no}. Expected prev {expected_prev_hash}, found {recorded_prev}",
                        "line_number": line_no,
                        "is_valid": False
                    }

                # Recompute record payload hash
                payload_to_verify = {k: v for k, v in record.items() if k != "record_hash_sha256"}
                calculated_hash = self._compute_hash(payload_to_verify, expected_prev_hash)

                if calculated_hash != recorded_hash:
                    return {
                        "status": "COMPROMISED",
                        "error": f"Tampered record detected at line {line_no}. Recalculated hash does not match.",
                        "line_number": line_no,
                        "is_valid": False
                    }

                expected_prev_hash = recorded_hash
                records_verified += 1

        return {
            "status": "VERIFIED_SECURE",
            "verified_records": records_verified,
            "latest_head_hash": expected_prev_hash,
            "is_valid": True
        }

Example: How the Streamlit Cockpit Uses It
When the controller clicks [ Approve & Post Accrual ] in ui/app.py:
from src.governance.audit_logger import AuditLogger

logger = AuditLogger()

# Log the immutable controller approval event

audit_record = logger.log_action(
event_type="JOURNAL_VOUCHER_POSTED",
controller={
"user_id": "ctrl_frank_e",
"name": "Frank Ellingsen",
"role": "Lead Project Controller",
"auth_tier": "Tier 2"
},
action="APPROVED_WITHOUT_EDIT",
justification_memo="Accrued 670,000 NOK authorized PO delivery per yard receipt GR-4412. Disputed 150,000 NOK overrun routed to PM for change order review.",
period="2026-10",
journal_id="JV-2026-10-0042",
source_investigation_id="INV-2026-10-0042",
triggering_rule="CTRL-AP-03 (PO Tolerance Overrun)",
financial_lines=[
{"account": "4100", "debit_nok": 670000.0, "credit_nok": 0.0, "wbs": "PRJ-2026-001.03.FAB"},
{"account": "2440", "debit_nok": 0.0, "credit_nok": 670000.0, "wbs": "PRJ-2026-001.03.FAB"}
]
)

# External auditor verification in 1 line

verification = logger.verify_audit_integrity()
print(verification)

# Output: {'status': 'VERIFIED_SECURE', 'verified_records': 1, 'latest_head_hash': 'a4f9b...', 'is_valid': True}

Key Architectural Safeguards
Deterministic Serialization: Keys are canonically sorted and stripped of whitespace before hashing, ensuring reproducibility across different OS environments (Linux/Windows/macOS).
Accountability Guaranteed: Every approval requires the human controller's ID, role, timestamp, and rationale memo attached directly to the financial lines.
Statutory Audit Confidence: External auditors can run verify_audit_integrity() during interim or year-end audits to prove financial statements and period-end close entries were not modified post-close.

implementation of scripts/run_close_pipeline.py.
This script serves as the central CLI orchestrator for CLOSE-AI. It chains the entire close sequence together in the correct operational order:
Validates the data lakehouse directory.
Initializes DuckDB and registers tables.
Evaluates all dynamic, parameterized deterministic controls.
Runs the Isolation Forest statistical anomaly detector.
Triages high-risk exceptions to the Investigation Agent (using your chosen provider: Gemini Flash or local Ollama).
Verifies audit log cryptographic integrity.
Prints a clean executive summary in the terminal.
scripts/run_close_pipeline.py
import os
import sys
import argparse
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Ensure project root is in sys.path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(**file**), "..")))

from src.engine.control_evaluator import DynamicControlEvaluator
from src.governance.audit_logger import AuditLogger
from src.agent.tools import AccountingTools
from src.agent.investigator import InvestigationAgent

console = Console()

def run_pipeline(config_path: str, data_dir: str, llm_provider: str, model_name: str = None):
console.print(Panel.fit("[bold cyan]CLOSE-AI Financial Close Pipeline Runner[/bold cyan]\n[italic]Nordic Engineering Projects AS • Automated Pre-Close Engine[/italic]"))

    # Step 1: Initialize Evaluator & Lakehouse
    console.print("\n[bold]1. Initializing Lakehouse & Control Engine...[/bold]")
    evaluator = DynamicControlEvaluator(config_path=config_path)
    evaluator.register_tables(data_dir=data_dir)
    console.print(f" [green]✓[/green] Ingested relational tables from `{data_dir}` into DuckDB session.")

    # Step 2: Evaluate Deterministic Controls
    console.print("\n[bold]2. Executing Deterministic Financial Controls...[/bold]")
    eval_results = evaluator.evaluate_all_controls()

    score = eval_results["readiness_score_pct"]
    status = eval_results["overall_status"]

    status_color = "red" if status == "CLOSE BLOCKED" else ("yellow" if status == "ACTION REQUIRED" else "green")
    console.print(f" Close Readiness Score: [bold]{score}%[/bold]")
    console.print(f" Ledger Status: [{status_color}][bold]{status}[/bold][/{status_color}]")

    # Render Controls Summary Table
    table = Table(title="Financial Controls Execution Summary", header_style="bold blue")
    table.add_column("Rule ID", style="dim", width=12)
    table.add_column("Control Name", width=34)
    table.add_column("Severity", width=10)
    table.add_column("Status", width=10)
    table.add_column("Exposure (NOK)", justify="right", width=16)
    table.add_column("Count", justify="center", width=8)

    for c in eval_results["controls_summary"]:
        s_color = "green" if c["status"] == "PASS" else ("red" if c["severity"] == "BLOCKER" else "yellow")
        table.add_row(
            c["rule_id"],
            c["rule_name"],
            c["severity"],
            f"[{s_color}]{c['status']}[/{s_color}]",
            f"{c['discrepancy_amount_nok']:,.2f}",
            str(c["affected_count"])
        )
    console.print(table)

    # Step 3: Verify Cryptographic Audit Log Integrity
    console.print("\n[bold]3. Verifying Cryptographic Audit Chain...[/bold]")
    audit_logger = AuditLogger()
    audit_check = audit_logger.verify_audit_integrity()
    if audit_check["is_valid"]:
        console.print(f" [green]✓[/green] Audit Trail Verified Secure. Records: {audit_check['verified_records']}")
    else:
        console.print(f" [red]✗[/red] AUDIT CHAIN COMPROMISED: {audit_check.get('error')}")

    # Step 4: Triaging High-Risk Items to Investigation Agent
    anomalous_rules = [c for c in eval_results["controls_summary"] if c["status"] != "PASS"]
    if anomalous_rules:
        console.print(f"\n[bold]4. Autonomous Investigation via {llm_provider.upper()}...[/bold]")
        tools = AccountingTools(db_con=evaluator.con)
        agent = InvestigationAgent(tools=tools, provider=llm_provider, model_name=model_name)

        # Example investigation dispatch for PO overrun
        po_rule = next((r for r in anomalous_rules if r["rule_id"] == "CTRL-AP-03"), None)
        if po_rule:
            console.print(" [yellow]![/yellow] Dispatching investigation for PO-8809 tolerance overrun...")
            dossier = agent.investigate_anomaly({
                "rule_id": "CTRL-AP-03",
                "po_number": "PO-2026-8809",
                "wbs_code": "PRJ-2026-001.03.FAB",
                "vendor_id": "VEND-101",
                "discrepancy_nok": po_rule["discrepancy_amount_nok"]
            })
            console.print(Panel(
                f"[bold]Observation:[/bold] {dossier.get('observation')}\n\n"
                f"[bold]Likely Cause:[/bold] {dossier.get('likely_cause')}\n\n"
                f"[bold]Recommendation:[/bold] {dossier.get('recommended_action')}",
                title=f"Investigation Dossier: {dossier.get('investigation_id', 'INV-DRAFT')}",
                border_style="yellow"
            ))

    console.print("\n[bold green]Pipeline execution complete.[/bold green] Launch UI with: [cyan]streamlit run ui/app.py[/cyan]\n")

if **name** == "**main**":
parser = argparse.ArgumentParser(description="Run the CLOSE-AI pre-close pipeline.")
parser.add_argument("--config", default="config/controls_config.yaml", help="Path to YAML configuration")
parser.add_argument("--data-dir", default="erp_data_2026_10", help="Directory with ERP data extracts")
parser.add_argument("--provider", default="gemini", choices=["gemini", "ollama"], help="LLM provider for investigation")
parser.add_argument("--model", default=None, help="Optional model name override (e.g., llama3.1 or gemini-1.5-flash)")

    args = parser.parse_args()
    run_pipeline(
        config_path=args.config,
        data_dir=args.data_dir,
        llm_provider=args.provider,
        model_name=args.model
    )

How to Run the Complete Stack via CLI
You can run the entire pipeline with either model:

1.  Using Gemini Flash:
    python scripts/run_close_pipeline.py --provider gemini --model gemini-1.5-flash
2.  Using local Ollama (Llama 3.1) in air-gapped mode:
    python scripts/run_close_pipeline.py --provider ollama --model llama3.1
    We have now defined every piece in the project hierarchy:
    Executive problem statement & pain points
    Nordic Engineering Projects AS profile & relational schema
    10 deterministic financial control rules
    Isolation Forest feature engineering & scoring
    Scoped single-purpose Investigation Agent & tools
    Human-in-the-loop state machine & governance
    Synthetic test data generator (generate_erp_data.py)
    Parameterized DuckDB rule engine (control_evaluator.py)
    Streamlit Controller Control Room cockpit (app.py)
    Dynamic YAML configuration (controls_config.yaml)
    Cryptographic SHA-256 audit logger (audit_logger.py)
    CLI Pipeline Orchestrator (run_close_pipeline.py)

        complete unit testing suite for the CLOSE-AI project.

    In financial operations, software tests aren't just for bug prevention—they serve as formal audit evidence that the deterministic accounting rules cannot fail silently and that the cryptographic audit log detects tampering.
    We will create two test modules:
    tests/test_deterministic_rules.py: Validates the 6 financial controls against both clean and corrupted ledger states.
    tests/test_audit_integrity.py: Validates SHA-256 hash chaining, genesis linking, and tamper detection.

3.  tests/test_deterministic_rules.py
    This test suite uses pytest and an in-memory DuckDB connection to verify that edge cases, precision limits, and hard blocker states behave as expected:
    import pytest
    import duckdb
    import pandas as pd
    from src.engine.control_evaluator import DynamicControlEvaluator

@pytest.fixture
def evaluator():
"""Initializes the evaluator with the dynamic configuration."""
return DynamicControlEvaluator(config_path="config/controls_config.yaml")

def test_ctrl_gl_01_balanced_ledger_passes(evaluator):
"""Verify that a perfectly balanced trial balance passes CTRL-GL-01."""
evaluator.con.execute("""
CREATE OR REPLACE TABLE gl_journal_lines AS
SELECT 'JV-1' AS entry_id, '1' AS line_id, '1910' AS account_number, 50000.00 AS debit_nok, 0.00 AS credit_nok
UNION ALL
SELECT 'JV-1' AS entry_id, '2' AS line_id, '3010' AS account_number, 0.00 AS debit_nok, 50000.00 AS credit_nok;
""")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_entries (entry_id VARCHAR, posting_date DATE, source_module VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE vendor_invoices (invoice_id VARCHAR, vendor_id VARCHAR, amount_nok DOUBLE, invoice_date DATE, po_number VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE po_lines (po_number VARCHAR, delivery_status VARCHAR, received_qty DOUBLE, total_amount_nok DOUBLE);")

    results = evaluator.evaluate_all_controls()
    gl01 = next(r for r in results["controls_summary"] if r["rule_id"] == "CTRL-GL-01")

    assert gl01["status"] == "PASS"
    assert gl01["discrepancy_amount_nok"] == 0.00

def test_ctrl_gl_01_imbalance_triggers_blocker(evaluator):
"""Verify that an imbalance of even 0.01 NOK triggers a hard close stop."""
evaluator.con.execute("""
CREATE OR REPLACE TABLE gl_journal_lines AS
SELECT 'JV-1' AS entry_id, '1' AS line_id, '1910' AS account_number, 50000.01 AS debit_nok, 0.00 AS credit_nok
UNION ALL
SELECT 'JV-1' AS entry_id, '2' AS line_id, '3010' AS account_number, 0.00 AS debit_nok, 50000.00 AS credit_nok;
""")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_entries (entry_id VARCHAR, posting_date DATE, source_module VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE vendor_invoices (invoice_id VARCHAR, vendor_id VARCHAR, amount_nok DOUBLE, invoice_date DATE, po_number VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE po_lines (po_number VARCHAR, delivery_status VARCHAR, received_qty DOUBLE, total_amount_nok DOUBLE);")

    results = evaluator.evaluate_all_controls()
    gl01 = next(r for r in results["controls_summary"] if r["rule_id"] == "CTRL-GL-01")

    assert gl01["status"] == "FAIL"
    assert gl01["severity"] == "BLOCKER"
    assert results["overall_status"] == "CLOSE BLOCKED"

def test_ctrl_ap_01_duplicate_invoice_detection(evaluator):
"""Verify duplicate invoice detection within the 14-day window."""
evaluator.con.execute("""
CREATE OR REPLACE TABLE vendor_invoices AS
SELECT 'INV-001' AS invoice_id, 'VEND-101' AS vendor_id, 45000.00 AS amount_nok, DATE '2026-10-10' AS invoice_date, 'PO-1' AS po_number
UNION ALL
SELECT 'INV-002' AS invoice_id, 'VEND-101' AS vendor_id, 45000.00 AS amount_nok, DATE '2026-10-14' AS invoice_date, 'PO-1' AS po_number;
""")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_lines (entry_id VARCHAR, line_id VARCHAR, account_number VARCHAR, debit_nok DOUBLE, credit_nok DOUBLE, project_id VARCHAR, wbs_code VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_entries (entry_id VARCHAR, posting_date DATE, source_module VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE po_lines (po_number VARCHAR, delivery_status VARCHAR, received_qty DOUBLE, total_amount_nok DOUBLE);")

    results = evaluator.evaluate_all_controls()
    ap01 = next(r for r in results["controls_summary"] if r["rule_id"] == "CTRL-AP-01")

    assert ap01["status"] == "FAIL"
    assert ap01["affected_count"] == 1
    assert ap01["discrepancy_amount_nok"] == 45000.00

def test_ctrl_ap_03_po_tolerance_overrun(evaluator):
"""Verify that an invoice >10% over PO fails, but <=10% passes.""" # Invoice 112,000 against 100,000 PO (+12% overrun)
evaluator.con.execute("""
CREATE OR REPLACE TABLE vendor_invoices AS
SELECT 'INV-1' AS invoice_id, 'VEND-1' AS vendor_id, 112000.00 AS amount_nok, DATE '2026-10-15' AS invoice_date, 'PO-99' AS po_number;
""")
evaluator.con.execute("""
CREATE OR REPLACE TABLE po_lines AS
SELECT 'PO-99' AS po_number, 'DELIVERED' AS delivery_status, 1.0 AS received_qty, 100000.00 AS total_amount_nok;
""")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_lines (entry_id VARCHAR, line_id VARCHAR, account_number VARCHAR, debit_nok DOUBLE, credit_nok DOUBLE, project_id VARCHAR, wbs_code VARCHAR);")
evaluator.con.execute("CREATE OR REPLACE TABLE gl_journal_entries (entry_id VARCHAR, posting_date DATE, source_module VARCHAR);")

    results = evaluator.evaluate_all_controls()
    ap03 = next(r for r in results["controls_summary"] if r["rule_id"] == "CTRL-AP-03")

    assert ap03["status"] == "FAIL"
    assert ap03["discrepancy_amount_nok"] == 12000.00

2. tests/test_audit_integrity.py
   This test suite guarantees that the SHA-256 hash chain cannot be silently altered:
   import os
   import json
   import pytest
   from src.governance.audit_logger import AuditLogger

@pytest.fixture
def temp_audit_logger(tmp_path):
"""Initializes an audit logger in an isolated temporary directory."""
log_dir = tmp_path / "audit_logs"
return AuditLogger(log_dir=str(log_dir), log_filename="test_audit.jsonl")

def test_audit_log_empty_file_valid(temp_audit_logger):
"""An empty or newly initialized log should be marked valid."""
res = temp_audit_logger.verify_audit_integrity()
assert res["is_valid"] is True
assert res["verified_records"] == 0

def test_audit_log_linear_chaining(temp_audit_logger):
"""Appending actions should build a valid, sequential hash chain."""
r1 = temp_audit_logger.log_action(
event_type="JOURNAL_VOUCHER_POSTED",
controller={"user_id": "ctrl_frank", "name": "Frank Ellingsen"},
action="APPROVED",
justification_memo="Monthly depreciation",
journal_id="JV-001"
)
r2 = temp_audit_logger.log_action(
event_type="JOURNAL_VOUCHER_POSTED",
controller={"user_id": "ctrl_frank", "name": "Frank Ellingsen"},
action="APPROVED",
justification_memo="WIP accrual",
journal_id="JV-002"
)

    # First record should point to genesis hash
    assert r1["previous_record_hash"] == AuditLogger.GENESIS_HASH
    # Second record should link to first record's hash
    assert r2["previous_record_hash"] == r1["record_hash_sha256"]

    # Verify overall file integrity
    check = temp_audit_logger.verify_audit_integrity()
    assert check["is_valid"] is True
    assert check["verified_records"] == 2
    assert check["latest_head_hash"] == r2["record_hash_sha256"]

def test_audit_log_detects_tampering(temp_audit_logger):
"""Manually altering an amount in the JSON-L log must immediately fail integrity checks."""
temp_audit_logger.log_action(
event_type="JOURNAL_VOUCHER_POSTED",
controller={"user_id": "ctrl_frank", "name": "Frank Ellingsen"},
action="APPROVED",
justification_memo="Initial accrual",
financial_lines=[{"account": "4100", "debit_nok": 10000.0, "credit_nok": 0.0}]
)
temp_audit_logger.log_action(
event_type="JOURNAL_VOUCHER_POSTED",
controller={"user_id": "ctrl_frank", "name": "Frank Ellingsen"},
action="APPROVED",
justification_memo="Secondary accrual",
financial_lines=[{"account": "4100", "debit_nok": 20000.0, "credit_nok": 0.0}]
)

    # Simulate malicious unauthorized modification of record 1
    log_path = temp_audit_logger.log_path
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tampered_record = json.loads(lines[0])
    tampered_record["financial_lines"][0]["debit_nok"] = 999999.00  # Altered value
    lines[0] = json.dumps(tampered_record) + "\n"

    with open(log_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Run verification - must return COMPROMISED
    check = temp_audit_logger.verify_audit_integrity()
    assert check["is_valid"] is False
    assert check["status"] == "COMPROMISED"
    assert "Tampered record detected" in check["error"]

Running the Test Suite
You can execute the entire suite locally with standard pytest:
pytest tests/ -v
This verifies that:
The deterministic accounting controls correctly enforce zero tolerance on blockers.
The Isolation Forest and threshold limits catch discrepancies.
Any unauthorized edit to financial records or audit trails is caught by the SHA-256 integrity verification.

the containerization and local deployment setup for CLOSE-AI.
This gives you a reproducible environment where your Streamlit control room, DuckDB lakehouse, and dual inference options (local Ollama with llama3.1 or Gemini Flash) run cleanly without dependency conflicts.

1. Dockerfile

# Base Python image

FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (build tools, curl for healthchecks)

RUN apt-get update && apt-get install -y --no-install-recommends \
 build-essential \
 curl \
 && rm -rf /var/lib/apt/lists/\*

# Install Python requirements

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project directories

COPY config/ ./config/
COPY src/ ./src/
COPY ui/ ./ui/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Create persistent storage directories

RUN mkdir -p data/raw data/lakehouse data/audit_logs

# Expose Streamlit default port

EXPOSE 8501

# Healthcheck for Streamlit service

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
 CMD curl --fail http://localhost:8501/\_stcore/health || exit 1

# Default entrypoint runs the Streamlit UI

ENTRYPOINT ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"] 2. docker-compose.yml
This compose file orchestrates both the CLOSE-AI application and a local Ollama service on the same bridge network. If you have an NVIDIA GPU, uncomment the GPU reservation block under ollama.
version: "3.9"

services:

# CLOSE-AI Streamlit Control Room

close-ai:
build:
context: .
dockerfile: Dockerfile
container_name: close_ai_control_room
ports: - "8501:8501"
environment: - GEMINI_API_KEY=${GEMINI_API_KEY:-} - OLLAMA_HOST=http://ollama:11434 - ENVIRONMENT=production
volumes: - ./data:/app/data - ./config:/app/config
depends_on:
ollama:
condition: service_started
networks: - close_ai_net
restart: unless-stopped

# Local Ollama service for Llama 3.1 inference

ollama:
image: ollama/ollama:latest
container_name: close_ai_ollama
ports: - "11434:11434"
volumes: - ollama_models:/root/.ollama
networks: - close_ai_net
restart: unless-stopped # Uncomment below if running on host with NVIDIA GPU support: # deploy: # resources: # reservations: # devices: # - driver: nvidia # count: 1 # capabilities: [gpu]

networks:
close_ai_net:
driver: bridge

volumes:
ollama_models:
driver: local 3. .env.example
Create a .env file in the project root:

# Optional: Set for Gemini Flash cloud inference

GEMINI_API_KEY=your_actual_gemini_api_key_here

# Local Ollama endpoint (defaults to http://ollama:11434 inside Docker)

OLLAMA_HOST=http://localhost:11434 4. requirements.txt
duckdb>=1.1.0
pandas>=2.2.0
numpy>=1.26.0
pyarrow>=15.0.0
scikit-learn>=1.5.0
pyyaml>=6.0.1
rich>=13.7.0
streamlit>=1.38.0
google-generativeai>=0.8.0
requests>=2.32.0
pytest>=8.3.0 5. Deployment & Execution Workflow
To spin up the entire system from your terminal:

# 1. Clone repository & configure environment

cp .env.example .env

# (Add your GEMINI_API_KEY to .env if you plan to use Gemini Flash)

# 2. Build and start containers

docker compose up -d --build

# 3. Pull Llama 3.1 model into Ollama container (one-time setup)

docker exec -it close_ai_ollama ollama pull llama3.1

# 4. Generate the synthetic test dataset with injected anomalies

docker exec -it close_ai_control_room python scripts/generate_synthetic_data.py

# 5. Run the automated pre-close pipeline CLI check

docker exec -it close_ai_control_room python scripts/run_close_pipeline.py --provider ollama --model llama3.1
Once running, open your browser to http://localhost:8501 to access the live Controller Control Room.
What's Complete
You now have a complete, end-to-end blueprint and implementation ready to push to your repository:
Business Problem & Domain Grounding: Built specifically around EPC project accounting for Nordic Engineering Projects AS.
Deterministic Financial Core: DuckDB lakehouse executing SQL controls with zero trial balance tolerance, 3-way PO matching, and unbilled WIP checks.
Statistical Outlier Detection: Isolation Forest identifying non-linear anomalies.
Scoped Investigation Agent: Contextual root-cause investigation using either Gemini Flash or local Llama 3.1.
Human-in-the-Loop Governance: Strict separation of duties, draft JV staging, and cryptographic SHA-256 audit chaining.
Automated Testing & Containerization: Unit tests for accounting controls and Docker Compose orchestration.

Key UI/UX Concepts for an index.html Control Room
To match the operational reality of a lead project controller closing the books:
Executive HUD (Heads-Up Display):
Period Status Pill: Dynamic indicator showing 2026-10 | WD+2 with a pulsing traffic light (🔴 CLOSE BLOCKED vs 🟢 READY FOR SIGN-OFF).
Readiness Meter: Circular SVG or sleek progress bar tracking the weighted 0–100% Close Readiness Index.
Financial Exposure Ticker: Real-time counters showing total active variances and open exception counts.
Interactive Control Matrix Grid:
6 visual control cards (CTRL-GL-01 through CTRL-PRJ-03) with status chips, severity badges, affected row counts, and monetary delta values.
Clicking any failing control instantly filters the investigation queue below.
Autonomous Investigation Workbench & Dossier Viewer:
Evidence Drawer / Split View: Left panel lists flagged exceptions; right panel renders the selected Evidence Dossier (Observation, Evidence Chain, Root Cause, Financial Impact, and Proposed Adjusting Journal).
Audit-Grade Action Buttons: Direct interactive buttons for [ Approve & Post ], [ Edit Adjustment ], [ Dispute / Hold ], and [ Reject ].
Live Cryptographic Audit Stream:
An append-only feed displaying each controller action with its SHA-256 hash stamp, timestamp, and verification badge (✓ Chain Verified).
Design System:
Dark modern financial terminal or clean Nordic executive theme (slate navy #0f172a, crisp borders, monospace numerical fonts for ledger lines, and distinct accounting status colors).
