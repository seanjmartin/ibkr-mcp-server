#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    print("Testing enhanced_test_logger import...")
    from tests.paper.enhanced_test_logger import enhanced_test_logging, log_api_call_with_timing
    print("[SUCCESS] Enhanced test logger imported successfully")
except Exception as e:
    print(f"[ERROR] Import error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Testing IBKR client import...")
    from ibkr_mcp_server.client import IBKRClient
    print("[SUCCESS] IBKR client imported successfully")
except Exception as e:
    print(f"[ERROR] IBKR client import error: {e}")
    import traceback
    traceback.print_exc()

print("Import test completed")
