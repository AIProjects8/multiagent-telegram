#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SqlDB.migrations.migration_runner import run_migrations

if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        print(f"Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

