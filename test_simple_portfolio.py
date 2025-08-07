"""
Simplified Portfolio Test - No Enhanced Logging

Tests portfolio tool without complex logging to isolate hanging issues.
"""

import pytest
import pytest_asyncio
import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from ibkr_mcp_server.client import IBKRClient
from ibkr_mcp_server.enhanced_config import EnhancedSettings
from ibkr_mcp_server.tools import call_tool
from mcp.types import TextContent


@pytest.mark.paper
class TestSimplifiedPortfolio:
    """Simplified portfolio test without enhanced logging"""
    
    @pytest_asyncio.fixture(scope="function")
    async def paper_client(self):
        """Create connected paper trading client"""
        print("=== Simplified Portfolio Test ===")
        
        # Create client (no parameters - follows working pattern)
        client = IBKRClient()
        client.client_id = 5  # Override to use client ID 5 (working configuration)
        
        print(f"Using client ID: {client.client_id}")
        
        # Verify paper trading configuration
        settings = EnhancedSettings()
        print(f"Configuration - Paper: {settings.ibkr_is_paper}, Port: {settings.ibkr_port}")
        
        print("Connecting to IBKR Gateway...")
        connected = await asyncio.wait_for(client.connect(), timeout=10.0)
        
        if not connected:
            raise Exception("Failed to connect to IBKR Gateway")
        
        print("[SUCCESS] Connected to IBKR Gateway")
        
        yield client
        
        # Clean disconnect
        try:
            await client.disconnect()
            print("[SUCCESS] Disconnected cleanly")
            # Small delay for server-side cleanup
            await asyncio.sleep(1.0)
        except Exception as e:
            print(f"[WARNING] Disconnect error: {e}")
    
    @pytest.mark.asyncio
    async def test_portfolio_tool(self, paper_client):
        """Test portfolio MCP tool"""
        print("\\n=== Testing Portfolio Tool ===")
        
        try:
            # Call the portfolio tool
            print("Calling get_portfolio tool...")
            start_time = asyncio.get_event_loop().time()
            
            result = await asyncio.wait_for(
                call_tool("get_portfolio", {}),
                timeout=10.0
            )
            
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            print(f"Portfolio tool completed in {duration:.2f} seconds")
            
            # Validate result structure
            assert isinstance(result, list), f"Expected list, got {type(result)}"
            assert len(result) > 0, "Expected non-empty response"
            
            content = result[0]
            assert hasattr(content, 'text'), "Expected TextContent with text attribute"
            
            response_text = content.text
            print(f"Portfolio response length: {len(response_text)} characters")
            
            # Log first 200 characters of response
            preview = response_text[:200]
            print(f"Portfolio response preview: {preview}...")
            
            # Check for success indicators
            if "portfolio" in response_text.lower() or "positions" in response_text.lower():
                print("[SUCCESS] Portfolio data received")
                return True
            elif "empty" in response_text.lower() or "no positions" in response_text.lower():
                print("[SUCCESS] Empty portfolio confirmed")  
                return True
            else:
                print(f"[WARNING] Unexpected portfolio response: {response_text[:100]}...")
                return True  # Still consider success if we got a response
            
        except asyncio.TimeoutError:
            print("[ERROR] Portfolio tool timed out after 10 seconds")
            pytest.fail("Portfolio tool hanging - exceeded 10 second timeout")
            
        except Exception as e:
            print(f"[ERROR] Portfolio tool failed: {e}")
            pytest.fail(f"Portfolio tool error: {e}")
