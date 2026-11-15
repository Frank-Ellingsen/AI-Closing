"""
Root convenience entrypoint for generating synthetic ERP dataset.
Delegates to src.data_generator.generate_erp_data.
"""

from src.data_generator.generate_erp_data import generate_erp_dataset

if __name__ == "__main__":
    result = generate_erp_dataset("erp_data_2026_10")
    print(f"Generated {result['gl_lines_count']} GL lines across {result['gl_entries_count']} journal entries.")
    print(f"Dataset successfully exported to directory '{result['output_dir']}'.")
