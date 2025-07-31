"""Simple syntax validation for Phase 2 implementation."""

import os
import py_compile
from pathlib import Path

def validate_syntax(file_path):
    """Check if Python file has valid syntax."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """Run syntax validation on all Python files."""
    print("Phase 2 Syntax Validation")
    print("=" * 40)
    
    # Files to validate
    files_to_check = [
        "ibkr_mcp_server/data/forex_pairs.py",
        "ibkr_mcp_server/data/international_symbols.py", 
        "ibkr_mcp_server/data/exchange_info.py",
        "ibkr_mcp_server/data/__init__.py",
        "ibkr_mcp_server/trading/forex.py",
        "ibkr_mcp_server/trading/international.py",
        "ibkr_mcp_server/trading/stop_loss.py",
        "ibkr_mcp_server/trading/__init__.py",
        "ibkr_mcp_server/client.py",
        "ibkr_mcp_server/tools.py"
    ]
    
    passed = 0
    total = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            total += 1
            valid, error = validate_syntax(file_path)
            if valid:
                print(f"[OK] {file_path}")
                passed += 1
            else:
                print(f"[ERROR] {file_path}: {error}")
        else:
            print(f"[MISSING] {file_path}")
    
    print("=" * 40)
    print(f"Results: {passed}/{total} files passed syntax check")
    
    # Check file structure
    print("\nFile Structure Check:")
    expected_dirs = [
        "ibkr_mcp_server/data",
        "ibkr_mcp_server/trading"
    ]
    
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"[OK] Directory exists: {dir_path}")
        else:
            print(f"[ERROR] Missing directory: {dir_path}")
    
    if passed == total:
        print(f"\nAll {total} files have valid syntax!")
        print("Phase 2 implementation is syntactically correct.")
        return True
    else:
        print(f"\n{total - passed} files have syntax errors.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
