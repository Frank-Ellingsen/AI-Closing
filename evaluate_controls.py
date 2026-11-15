"""
Root convenience entrypoint for running close controls.
Delegates to src.engine.evaluate_controls.
"""

import json
from src.engine.evaluate_controls import run_close_controls, get_duckdb_connection

if __name__ == "__main__":
    summary = run_close_controls("erp_data_2026_10")
    print(json.dumps(summary, indent=2))
