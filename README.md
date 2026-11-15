# AI-Closing

A prototype financial close and audit control room for engineering and project-heavy organizations. The solution combines deterministic accounting checks, anomaly detection, evidence-based investigation, and a human approval gate for close-management workflows.

## What this project does

- Detects close exceptions such as trial-balance imbalances, duplicate invoices, untagged project costs, and PO overrun conditions.
- Applies deterministic accounting controls with DuckDB-powered SQL logic.
- Runs anomaly detection using an Isolation Forest model.
- Builds an investigation dossier from the evidence graph and drafts proposal-only journal suggestions.
- Maintains a tamper-evident audit trail with hash chaining.
- Exposes the workflow in a Streamlit control-room cockpit.

## Repository highlights

- `app.py` – Streamlit control-room interface.
- `src/engine/evaluate_controls.py` – deterministic close controls.
- `src/ml/anomaly_detector.py` – anomaly scoring.
- `src/agent/evidence_graph.py` – evidence lineage and provenance tracing.
- `src/agent/investigator.py` – investigation orchestration.
- `src/agent/llm_client.py` – structured dossier validation and fallback logic.
- `src/audit/audit_manager.py` – audit log and workflow persistence.
- `test_close_system.py` – end-to-end validation suite.

## Architecture summary

1. Deterministic controls validate the ledger and procurement data.
2. Statistical anomaly detection ranks suspect transactions.
3. The investigation agent gathers evidence and creates a grounded dossier.
4. The workflow requires human approval before any accounting treatment is treated as final.
5. The audit manager records operational actions in a hash-chained log for tamper detection.

## Running the project

### Install dependencies

```bash
pip install pandas numpy duckdb scikit-learn streamlit requests
```

### Generate ERP data and controls output

```bash
python generate_erp_data.py
python evaluate_controls.py
```

### Run the Streamlit app

```bash
streamlit run app.py
```

### Run the tests

```bash
python -m pytest -q test_close_system.py
```

## Current status

This is a working prototype focused on close governance, evidence-backed investigation, and audit hardening. It is not a production replacement for an ERP, but it is structured to keep deterministic finance logic separate from AI-driven analysis and to preserve a clear human approval boundary.

## Notes

- The project uses synthetic ERP data for testing and demonstration.
- Local audit/workflow files are intentionally ignored in Git to avoid committing generated operational artifacts.
- AI output is treated as proposal-only and must pass validation before it is accepted into the workflow.

## License

This project is provided as a prototype for internal evaluation and experimentation.
