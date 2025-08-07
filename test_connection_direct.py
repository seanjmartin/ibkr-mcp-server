"""
Test IBKR Gateway connection with client ID 5
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ibkr_mcp_server.client import ibkr_client

async def test_connection():
    print("="*60)
    print("IBKR Gateway Connection Test")
    print("="*60)
    print(f"Host: {ibkr_client.host}")
    print(f"Port: {ibkr_client.port}")
    print(f"Client ID: {ibkr_client.client_id}")
    print(f"Paper Trading: {ibkr_client.is_paper}")
    print("-"*60)
    
    print("Attempting connection...")
    try:
        success = await ibkr_client.connect()
        if success:
            print(f"[SUCCESS] CONNECTION SUCCESS!")
            print(f"Connected: {ibkr_client._connected}")
            print(f"Accounts: {ibkr_client.accounts}")
            print(f"Current Account: {ibkr_client.current_account}")
            
            # Get connection status through MCP layer
            status = await ibkr_client.get_connection_status()
            print(f"Connection Status: {status}")
            
        else:
            print(f"[FAILED] CONNECTION FAILED")
            print(f"Connected: {ibkr_client._connected}")
            
    except Exception as e:
        print(f"[ERROR] CONNECTION ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_connection())
