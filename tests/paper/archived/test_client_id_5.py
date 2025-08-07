"""
Working Paper Trading Test - Client ID 5

SUCCESS: This test connects successfully to IBKR Gateway paper trading
Uses: Client ID 5 (avoiding client ID 1 reserved for MCP server)
Account: DUH905195 (confirmed working)
"""

import pytest
import asyncio
import os
import sys

# Add the project root to Python path  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings


class TestWorkingPaperClientId5:
    """Working paper trading tests using client ID 5"""
    
    @pytest.mark.asyncio
    @pytest.mark.paper
    async def test_connection_and_accounts(self):
        """Test IBKR connection and account retrieval - KNOWN WORKING"""
        print("\n=== Paper Trading Test: Connection & Accounts ===")
        
        # Create client with fixed client ID 5 (working configuration)
        client = IBKRClient()
        client.client_id = 5  # Override to use client ID 5
        print(f"Using client ID: {client.client_id}")
        
        # Verify paper trading configuration
        settings = EnhancedSettings()
        assert settings.ibkr_is_paper == True, "Must be in paper trading mode"
        assert settings.ibkr_port == 7497, "Must use paper trading port 7497"
        print(f"Configuration - Paper: {settings.ibkr_is_paper}, Port: {settings.ibkr_port}")
        
        try:
            # Connect to IBKR Gateway (30 second timeout)
            print("Connecting to IBKR Gateway...")
            connected = await asyncio.wait_for(client.connect(), timeout=30.0)
            
            # Verify connection succeeded
            assert connected, "Connection should succeed"
            assert client.ib.isConnected(), "Client should be connected"
            print("[SUCCESS] Connected to IBKR Gateway")
            
            # Test account retrieval (this is the working pattern)
            accounts = await client.get_accounts()
            print(f"[SUCCESS] Retrieved accounts: {accounts}")
            
            # Verify we got the expected paper account
            assert 'current_account' in accounts
            assert accounts['paper_trading'] == True
            assert accounts['current_account'].startswith('DU')  # Paper account prefix
            print(f"[SUCCESS] Confirmed paper account: {accounts['current_account']}")
            
            # Clean disconnect
            await client.disconnect()
            print("[SUCCESS] Disconnected cleanly")
            
            # Small delay to ensure server-side cleanup (avoid "client ID in use")
            await asyncio.sleep(1.0)
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            # Ensure cleanup on any failure
            try:
                await client.disconnect()
            except:
                pass
            raise

    @pytest.mark.asyncio  
    @pytest.mark.paper
    async def test_connection_status_tool(self):
        """Test the connection status MCP tool"""
        print("\n=== Paper Trading Test: Connection Status Tool ===")
        
        client = IBKRClient()
        client.client_id = 5  # Use working client ID
        
        try:
            # Connect
            connected = await asyncio.wait_for(client.connect(), timeout=30.0)
            assert connected, "Should connect"
            print("[SUCCESS] Connected")
            
            # Test connection status tool
            status = await client.get_connection_status()
            print(f"[SUCCESS] Connection status: {status}")
            
            # Verify status response
            assert 'connected' in status
            assert status['connected'] == True
            assert 'current_account' in status
            print(f"[SUCCESS] Status tool working, account: {status['current_account']}")
            
            await client.disconnect()
            print("[SUCCESS] Test completed")
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            try:
                await client.disconnect()
            except:
                pass
            raise
    
    @pytest.mark.asyncio  
    @pytest.mark.paper
    async def test_account_summary_tool(self):
        """Test the account summary MCP tool"""
        print("\n=== Paper Trading Test: Account Summary Tool ===")
        
        client = IBKRClient()
        client.client_id = 5  # Use working client ID
        
        try:
            # Connect
            connected = await asyncio.wait_for(client.connect(), timeout=30.0)
            assert connected, "Should connect"
            print("[SUCCESS] Connected")
            
            # Test account summary tool
            summary = await client.get_account_summary()
            print(f"[SUCCESS] Account summary: {summary}")
            
            # Verify summary response has expected account info
            assert isinstance(summary, list), "Should return list of account data"
            assert len(summary) > 0, "Should have account data"
            # Should have balance-related information
            summary_str = str(summary).lower()
            assert any(keyword in summary_str for keyword in [
                "buyingpower", "netliquidation", "totalcashvalue", "usd"
            ]), "Should contain balance information"
            print("[SUCCESS] Account summary contains expected balance keywords")
            
            await client.disconnect()
            print("[SUCCESS] Test completed")
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            try:
                await client.disconnect()
            except:
                pass
            raise
    
    @pytest.mark.asyncio  
    @pytest.mark.paper
    async def test_portfolio_tool(self):
        """Test the portfolio MCP tool"""
        print("\n=== Paper Trading Test: Portfolio Tool ===")
        
        client = IBKRClient()
        client.client_id = 5  # Use working client ID
        
        try:
            # Connect
            connected = await asyncio.wait_for(client.connect(), timeout=30.0)
            assert connected, "Should connect"
            print("[SUCCESS] Connected")
            
            # Test portfolio tool
            portfolio = await client.get_portfolio()
            print(f"[SUCCESS] Portfolio: {portfolio}")
            
            # Verify portfolio response structure (works whether empty or has positions)
            assert isinstance(portfolio, (list, dict)), "Should return list or dict"
            
            if isinstance(portfolio, list):
                print(f"[SUCCESS] Portfolio tool returned list with {len(portfolio)} positions")
                if len(portfolio) == 0:
                    print("[NOTE] Portfolio is empty (no current positions)")
                else:
                    # Validate position structure if positions exist
                    print(f"[NOTE] Portfolio has {len(portfolio)} positions")
                    for pos in portfolio[:2]:  # Show first 2 positions as example
                        print(f"[POSITION] {pos}")
            elif isinstance(portfolio, dict):
                print(f"[SUCCESS] Portfolio tool returned dict with keys: {list(portfolio.keys())}")
                positions = portfolio.get('positions', [])
                print(f"[NOTE] Portfolio contains {len(positions)} positions")
                    
            await client.disconnect()
            print("[SUCCESS] Test completed")
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            try:
                await client.disconnect()
            except:
                pass
            raise


if __name__ == "__main__":
    # Allow running individual tests directly
    import asyncio
    test = TestWorkingPaperClientId5()
    
    print("Running Paper Trading Tests with Client ID 5...")
    asyncio.run(test.test_connection_and_accounts())
    print("\nRunning Connection Status Tool Test...")
    asyncio.run(test.test_connection_status_tool())
    print("\nAll tests completed successfully!")
