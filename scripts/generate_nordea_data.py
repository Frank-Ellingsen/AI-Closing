"""
Script entrypoint for generating Nordea bank & GL dataset.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.data_generator.nordea_generator import generate_nordea_dataset

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    result = generate_nordea_dataset(data_dir)
    print(f"Generated {result['bank_rows']} bank transactions and {result['erp_rows']} ERP lines.")
    print(f"Files written to {data_dir}:")
    print(f" - {result['bank_csv']}")
    print(f" - {result['erp_csv']}")
    print(f" - {result['bank_json']}")
    print(f" - {result['erp_json']}")
