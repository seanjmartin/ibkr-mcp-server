#!/usr/bin/env python3
"""
IBKR Gateway Connection Diagnostic
Diagnoses specific API connection failures
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
import logging

# Enable detailed ib_async logging
logging.basicConfig(level=logging.DEBUG)
ib_logger = logging.getLogger('ib_async')
ib_logger.setLevel(logging.DEBUG)

async def diagnose_connection():
    """Diagnose IBKR Gateway connection with detailed error reporting."""
    print("🔍 IBKR Gateway Connection Diagnostic")
    print("=" * 50)
    
    settings = EnhancedSettings()
    print(f"Host: {settings.ibkr_host}")
    print(f"Port: {settings.ibkr_port}")
    print(f"Paper Trading: {settings.ibkr_is_paper}")
    print()
    
    # Test with multiple client IDs to check for conflicts
    for client_id in [200, 201, 1, 94]:
        print(f"🧪 Testing Client ID: {client_id}")
        
        client = IBKRClient()
        client.client_id = client_id
        
        try:
            # Very short timeout to get immediate feedback
            print(f"   Attempting connection...")
            connected = await asyncio.wait_for(client.connect(), timeout=3.0)
            
            if connected:
                print(f"   ✅ SUCCESS: Connected with client ID {client_id}")
                
                # Test basic operations
                try:
                    accounts = await client.get_accounts()
                    print(f"   📊 Account: {accounts.get('current_account', 'Unknown')}")
                    
                    status = await client.get_connection_status()
                    print(f"   🔌 Status: {status.get('connected', False)}")
                    
                except Exception as e:
                    print(f"   ⚠️  Connected but API calls failed: {e}")
                
                # Clean disconnect
                await client.disconnect()
                print(f"   🔌 Disconnected cleanly")
                return client_id  # Return successful client ID
                
            else:
                print(f"   ❌ FAILED: Connection returned False")
                
        except asyncio.TimeoutError:
            print(f"   ⏱️  TIMEOUT: Connection timed out after 3 seconds")
        except Exception as e:
            print(f"   💥 ERROR: {type(e).__name__}: {e}")
        
        print()
    
    print("❌ All client IDs failed to connect")
    return None

async def check_gateway_requirements():
    """Check Gateway configuration requirements."""
    print("📋 Gateway Configuration Requirements:")
    print("1. IB Gateway running in Paper Trading mode")
    print("2. Configuration → Settings → API:")
    print("   ✅ Enable ActiveX and Socket Clients")
    print("   ✅ Socket port: 7497")
    print("   ✅ Trusted IP: 127.0.0.1")
    print("   ✅ Read-Only API: NO (allow trading)")
    print("3. Account must be logged in and active")
    print("4. No other applications using the same client ID")
    print()

if __name__ == "__main__":
    asyncio.run(check_gateway_requirements())
    successful_client = asyncio.run(diagnose_connection())
    
    if successful_client:
        print(f"🎉 RECOMMENDATION: Use client ID {successful_client} for tests")
    else:
        print("🚨 ISSUE: Gateway configuration needs to be checked")
        print("   Most likely causes:")
        print("   - API not enabled in Gateway settings")
        print("   - 127.0.0.1 not in trusted IPs")
        print("   - All client IDs in use by other applications")
        print("   - Gateway not logged in to paper account")
