#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from SqlDB.migrations.migration_runner import run_migrations

if __name__ == "__main__":
    run_migrations()

