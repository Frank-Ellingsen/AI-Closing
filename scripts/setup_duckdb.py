"""
Scripts entrypoint for setup_duckdb.
Delegates to setup_duckdb.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from setup_duckdb import setup_databases

if __name__ == '__main__':
    setup_databases()
