"""
Individual MCP Tool Test: get_accounts
Focus: Test get_accounts MCP tool in isolation for debugging
MCP Tool: get_accounts
Expected: List of available accounts with current account marked
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
class TestIndividualGetAccounts:
    """Test get_accounts MCP tool in isolation"""
    
    async def test_get_accounts_basic_functionality(self):
        """Test basic get_accounts functionality through MCP interface"""
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Tool: get_accounts ===")
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
        
        # MCP tool call - get_accounts takes no parameters
        tool_name = "get_accounts"
        parameters = {}  # get_accounts takes no parameters
        
        print(f"MCP Call: call_tool('{tool_name}', {parameters})")
        print(f"Executing...")
        
        try:
            # Execute MCP tool call
            result = await call_tool(tool_name, parameters)
            print(f"Raw Result: {result}")
            
        except Exception as e:
            print(f"EXCEPTION during MCP call: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            pytest.fail(f"MCP call failed with exception: {e}")
        
        # MCP response structure validation - MCP tools return list of TextContent
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
        
        # For paper testing, we expect a successful result from IBKR client
        # The client returns its own format, not necessarily with "success" field
        
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool [tool_name] failed: {response_text}")
            
            # For successful responses, validate the data structure
            print(f"[tool_name] data: {parsed_result}")
            
            # get_accounts specific validation
            if "accounts" in parsed_result:
                accounts = parsed_result['accounts']
                print(f"[OK] Accounts List Found: {accounts}")
                assert isinstance(accounts, list), f"Accounts should be a list, got {type(accounts)}"
                assert len(accounts) > 0, f"Should have at least one account, got {len(accounts)}"
                
                # Check each account has required fields
                for account in accounts:
                    assert isinstance(account, str), f"Account should be string, got {type(account)}"
                    if account.startswith("DU"):
                        print(f"[OK] Paper Account Found: {account}")
                    else:
                        print(f"[INFO] Account: {account}")
            
            if "current_account" in parsed_result:
                current_account = parsed_result['current_account']
                print(f"[OK] Current Account: {current_account}")
                assert isinstance(current_account, str), f"Current account should be string, got {type(current_account)}"
                # Verify it's a paper account
                if current_account.startswith("DU"):
                    print(f"[OK] Current account is paper trading: {current_account}")
                else:
                    print(f"[WARN] Current account format unexpected: {current_account}")
            
            if "total_accounts" in parsed_result:
                total_accounts = parsed_result['total_accounts']
                print(f"[OK] Total Accounts: {total_accounts}")
                assert isinstance(total_accounts, int), f"Total accounts should be int, got {type(total_accounts)}"
                assert total_accounts > 0, f"Should have at least 1 account, got {total_accounts}"
            
            print(f"[SUCCESS] GET_ACCOUNTS VALIDATION PASSED")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_accounts")
        
        print(f"\\n[SUCCESS] MCP Tool 'get_accounts' test PASSED")
        print(f"[SUCCESS] IBKR accounts retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_accounts_no_parameters_needed(self):
        """Test that get_accounts works with empty parameters"""
        
        print(f"\\n{'='*50}")
        print(f"=== Testing No Parameters Required ===")
        print(f"{'='*50}")
        
        # Should work with empty dict - call_tool returns list of TextContent
        result1 = await call_tool("get_accounts", {})
        assert isinstance(result1, list), f"Expected list of TextContent, got {type(result1)}"
        assert len(result1) > 0, f"Expected non-empty response, got: {result1}"
        
        # Parse the first TextContent response
        text_content = result1[0]
        response_text = text_content.text
        
        try:
            parsed_result = json.loads(response_text)
            print(f"[OK] Empty dict parameters work correctly")
            
            # Basic validation that we got accounts data
            if "accounts" in parsed_result or "current_account" in parsed_result:
                print(f"[OK] Account data returned successfully")
            else:
                print(f"[INFO] Response format: {parsed_result}")
                
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON response, got: {response_text}")
        
        print("[SUCCESS] Parameter handling validation passed")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_accounts.py -v -s

NEVER use:
- python -m pytest [...]     # ❌ Python not in PATH
- pytest [...]               # ❌ Pytest not in PATH  
- python tests/paper/...     # ❌ Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_accounts.py::TestIndividualGetAccounts::test_get_accounts_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_accounts.py::TestIndividualGetAccounts -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_accounts.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("[WARNING] STANDALONE EXECUTION DETECTED")
    print("[WARNING] RECOMMENDED: Use pytest execution commands shown above")
    print("[WARNING] Standalone mode may not work correctly with MCP interface")
    print()
    print("IBKR Gateway must be running with paper trading login and API enabled!")
    print("Port 7497 for paper trading, Client ID 5")
    
    # Run just this test file using pytest
    exit_code = pytest.main([
        __file__, 
        "-v", 
        "-s", 
        "--tb=short"
    ])
    
    sys.exit(exit_code)
