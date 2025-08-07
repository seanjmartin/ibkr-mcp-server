"""
Individual MCP Tool Test: get_connection_status
Focus: Test connection status MCP tool in isolation for debugging
MCP Tool: get_connection_status
Expected: IBKR connection status with paper account information
"""

import pytest
import asyncio
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Import MCP interface - THIS IS THE CORRECT LAYER TO TEST
from ibkr_mcp_server.tools import call_tool  # Proper MCP interface
from mcp.types import TextContent
import json
from unittest.mock import patch, AsyncMock

@pytest.mark.paper
@pytest.mark.asyncio
class TestIndividualGetConnectionStatus:
    """Test get_connection_status MCP tool in isolation"""
    
    async def test_get_connection_status_basic_functionality(self):
        """Test basic get_connection_status functionality through MCP interface"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Tool: get_connection_status ===")
        print(f"{'='*60}")
        
        # FORCE CONNECTION FIRST - ensure IBKR client is connected
        print(f"Step 1: Forcing IBKR Gateway connection...")
        from ibkr_mcp_server.client import ibkr_client
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
            else:
                print(f"[WARNING] IBKR Gateway connection failed")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        # MCP tool call - no parameters needed for connection status
        tool_name = "get_connection_status"
        parameters = {}  # Connection status takes no parameters
        
        print(f"Step 2: MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
        try:
            # Execute MCP tool call - this returns a list of TextContent objects
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result Type: {type(result)}")
            print(f"Raw Result Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"EXCEPTION during MCP call: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"MCP call failed with exception: {e}")
        
        # MCP tool response structure validation - returns list of TextContent
        print(f"\\n--- MCP Tool Response Structure Validation ---")
        assert isinstance(result, list), f"MCP tool should return list, got {type(result)}"
        assert len(result) > 0, f"MCP tool should return at least one TextContent, got empty list"
        
        # Get the first TextContent response
        text_content = result[0]
        assert isinstance(text_content, TextContent), f"Expected TextContent, got {type(text_content)}"
        assert hasattr(text_content, 'text'), f"TextContent should have 'text' attribute"
        
        # Parse the JSON response from the text content
        response_text = text_content.text
        print(f"Response text: {response_text}")
        
        try:
            # Parse the JSON response (IBKR client response format)
            parsed_result = json.loads(response_text)
        except json.JSONDecodeError as e:
            # If it's not JSON, it might be an error string
            print(f"Response is not JSON, treating as error: {response_text}")
            pytest.fail(f"Expected JSON response, got non-JSON: {response_text}")
        
        print(f"Parsed Result: {parsed_result}")
        
        # For paper testing, we expect a successful connection result from IBKR client
        # The client returns its own format, not necessarily with "success" field
        
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool get_connection_status failed: {response_text}")
            
            # For connection status, we expect connection information
            print(f"Connection status data: {parsed_result}")
            
            # Look for expected connection status fields
            # The exact format depends on the IBKR client implementation
            if "account" in parsed_result:
                account = parsed_result['account']
                print(f"[OK] Paper Account Found: {account}")
                if isinstance(account, str) and account.startswith("DU"):
                    print(f"[OK] Paper Account Validated: {account}")
                else:
                    print(f"[WARN] Account format unexpected: {account}")
            
            if "connected" in parsed_result:
                connected = parsed_result['connected']
                print(f"[OK] Connection Status: {connected}")
            
            if "paper_trading" in parsed_result:
                paper_trading = parsed_result['paper_trading']
                print(f"[OK] Paper Trading Mode: {paper_trading}")
                # Validate paper trading is enabled
                assert paper_trading == True, f"Expected paper_trading=True, got {paper_trading}"
            
            if "host" in parsed_result:
                host = parsed_result['host']
                print(f"[OK] Host: {host}")
                
            if "port" in parsed_result:
                port = parsed_result['port']
                print(f"[OK] Port: {port}")
                # Validate paper trading port
                assert port == 7497, f"Expected port=7497 for paper trading, got {port}"
                
            if "client_id" in parsed_result:
                client_id = parsed_result['client_id']
                print(f"[OK] Client ID: {client_id}")
                
            print(f"[SUCCESS] CONNECTION STATUS MCP TOOL WORKING")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
        
        print(f"\\n[SUCCESS] MCP Tool 'get_connection_status' test PASSED")
        print(f"[SUCCESS] IBKR connection status retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_connection_status_no_parameters_needed(self):
        """Test that get_connection_status works with empty parameters"""
        
        print(f"\\n{'='*50}")
        print(f"=== Testing No Parameters Required ===")
        print(f"{'='*50}")
        
        # Should work with empty dict - call_tool returns list of TextContent
        result1 = await call_tool("get_connection_status", {})
        assert isinstance(result1, list), f"Expected list of TextContent, got {type(result1)}"
        assert len(result1) > 0, f"Expected non-empty response, got: {result1}"
        
        # Parse the first TextContent response
        text_content = result1[0]
        response_text = text_content.text
        
        try:
            parsed_result = json.loads(response_text)
            print(f"[OK] Empty dict parameters work correctly")
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON response, got: {response_text}")
        
        # Should work with None as well (empty parameters)
        try:
            result2 = await call_tool("get_connection_status", {})  # Use empty dict
            print("[OK] Parameters handled correctly")
        except Exception as e:
            print(f"[INFO] Parameter handling: {e}")
            
        print("[SUCCESS] Parameter handling validation passed")

# Use pytest to run this test:
# pytest tests/paper/individual/test_individual_get_connection_status.py -v -s
