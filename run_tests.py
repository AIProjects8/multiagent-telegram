#!/usr/bin/env python3
"""
Simple test runner script for the multiagent-telegram project.
Run this from the root directory to execute all tests.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests using pytest."""
    print("🚀 Running tests for multiagent-telegram project...")
    print("=" * 60)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", "-v"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ All tests passed successfully!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install it with: pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
