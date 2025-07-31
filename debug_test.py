#!/usr/bin/env python3
"""Simple test to debug output issue"""

print("Script starting...")

try:
    print("Testing imports...")
    import sys
    import os
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    print("Adding path...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    print("Importing IBKRClient...")
    from ibkr_mcp_server.client import IBKRClient
    print("Import successful!")
    
    print("Creating client...")
    client = IBKRClient()
    print("Client created!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("Script completed.")
