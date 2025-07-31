"""Quick validation test for Phase 2 implementation."""

import sys
import importlib.util

def test_module_import(module_path, module_name):
    """Test if a module can be imported successfully."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"[OK] {module_name}: Import successful")
        return True
    except Exception as e:
        print(f"[ERROR] {module_name}: Import failed - {e}")
        return False

def main():
    """Run validation tests."""
    print("Phase 2 Implementation Validation")
    print("=" * 50)
    
    test_modules = [
        ("ibkr_mcp_server/data/forex_pairs.py", "forex_pairs"),
        ("ibkr_mcp_server/data/international_symbols.py", "international_symbols"),
        ("ibkr_mcp_server/data/exchange_info.py", "exchange_info"),
        ("ibkr_mcp_server/trading/forex.py", "forex_manager"),
        ("ibkr_mcp_server/trading/international.py", "international_manager"),
        ("ibkr_mcp_server/trading/stop_loss.py", "stop_loss_manager")
    ]
    
    passed = 0
    total = len(test_modules)
    
    for module_path, module_name in test_modules:
        if test_module_import(module_path, module_name):
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} modules passed validation")
    
    if passed == total:
        print("All modules validated successfully! Ready for testing.")
        return True
    else:
        print("Some modules have issues. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
