# CLOSE-AI: Autonomous Financial Close & Complex Reconciliation Engine (v2.0)

A next-generation financial close, transaction matching, and exception governance architecture for project-driven enterprises (Nordic Engineering Projects AS).

## Core Capabilities
1. **Pre-Match vs. Final Match:** Two-stage matching pipeline with candidate staging and hard cryptographic clearing.
2. **Complex Multi-Way Matching:** 1:Many, Many:1, and Many:Many matching with bounded combinatorial subset-sum solvers.
3. **Autonomous Regex Agent:** Fast deterministic tokenization + adaptive pattern induction.
4. **Spin-Off & Paired Bilagsgenerator:** Automated balancing entries for bank fees, interest, agio, and paired accrual/reversal entries.
5. **Aging Analysis (Aldersfordelte Poster):** Automated stratification across 0-30, 31-60, 61-90, and 90+ day buckets with IFRS 9 loss provisioning.
6. **Immutable Audit Trail:** Append-only SHA-256 linear hash chain verifying full financial lineage.

## Quickstart

```bash
# Run unit tests
python3 -m unittest discover -s tests

# Run end-to-end pre-close pipeline
python3 scripts/run_close_pipeline.py

# Run performance benchmark
python3 scripts/benchmark_matching_speed.py
```
