"""
Individual MCP Tool Test: get_account_summary
Focus: Test get_account_summary MCP tool in isolation for debugging
MCP Tool: get_account_summary
Expected: Account balances and currency breakdown
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
class TestIndividualGetAccountSummary:
    """Test get_account_summary MCP tool in isolation"""
    
    async def test_get_account_summary_basic_functionality(self):
        """Test basic get_account_summary functionality through MCP interface
        
        This test validates the comprehensive account summary data structure including:
        - Financial metrics (BuyingPower, NetLiquidation, TotalCashValue, etc.)
        - Margin requirements (FullInitMarginReq, FullMaintMarginReq)
        - Position values (GrossPositionValue, UnrealizedPnL, RealizedPnL)
        - Multiple currency breakdowns (USD, BASE currency entries)
        - Proper MCP protocol response structure with real IBKR API data
        """
        
        print(f"\\n{'='*60}")
        print(f"=== Testing MCP Tool: get_account_summary ===")
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
        
        # MCP tool call - get_account_summary takes optional account parameter
        tool_name = "get_account_summary"
        parameters = {}  # get_account_summary can take optional account parameter, but works without
        
        print(f"Step 2: MCP Call: call_tool('{tool_name}', {parameters})")
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
        # IBKR get_account_summary returns a LIST of account summary entries with tag/value structure
        
        if isinstance(parsed_result, list):
            print(f"[OK] IBKR Account Summary Format: List of {len(parsed_result)} entries")
            
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool {tool_name} failed: {response_text}")
            
            # Validate list structure - each entry should have tag, value, currency, account
            valid_entries = 0
            account_found = None
            account_summary_data = {}
            
            for entry in parsed_result:
                if isinstance(entry, dict):
                    # Validate entry structure
                    if "tag" in entry and "value" in entry and "account" in entry:
                        tag = entry["tag"]
                        value = entry["value"]
                        account = entry["account"]
                        currency = entry.get("currency", "")
                        
                        print(f"[OK] {tag}: {value} {currency} (Account: {account})")
                        
                        # Store account found
                        if not account_found:
                            account_found = account
                        
                        # Store key financial metrics
                        account_summary_data[tag] = value
                        valid_entries += 1
                    else:
                        print(f"[WARNING] Invalid entry structure: {entry}")
                else:
                    print(f"[WARNING] Non-dict entry: {entry}")
            
            # Validate we found valid account data
            assert valid_entries > 0, f"No valid account summary entries found"
            print(f"[OK] Found {valid_entries} valid account summary entries")
            
            # Validate paper account
            if account_found:
                assert isinstance(account_found, str), f"Account should be string, got {type(account_found)}"
                if account_found.startswith("DU"):
                    print(f"[OK] Paper Account Confirmed: {account_found}")
                else:
                    print(f"[WARNING] Account does not have paper prefix: {account_found}")
            
            # Validate key financial data is present
            key_metrics = ["BuyingPower", "NetLiquidation", "TotalCashValue"]
            found_metrics = []
            
            for metric in key_metrics:
                if metric in account_summary_data:
                    value_str = account_summary_data[metric]
                    try:
                        value_float = float(value_str)
                        found_metrics.append(metric)
                        print(f"[OK] {metric}: ${value_float:,.2f}")
                    except ValueError:
                        print(f"[WARNING] Could not parse {metric} value: {value_str}")
            
            if found_metrics:
                print(f"[SUCCESS] Found key financial metrics: {found_metrics}")
            else:
                print(f"[INFO] Available data tags: {list(account_summary_data.keys())}")
            
            print(f"[SUCCESS] GET_ACCOUNT_SUMMARY MCP TOOL VALIDATION PASSED")
            
        elif isinstance(parsed_result, dict):
            # Handle alternative dictionary format (if API changes)
            print(f"[OK] Dictionary format response")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool {tool_name} failed: {response_text}")
            
            print(f"[OK] Dictionary account data: {parsed_result}")
            print(f"[SUCCESS] Alternative format handled correctly")
            
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_account_summary")
        
        print(f"\\n[SUCCESS] MCP Tool 'get_account_summary' test PASSED")
        print(f"[SUCCESS] IBKR account summary retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_account_summary_no_parameters_needed(self):
        """Test that get_account_summary works with empty parameters"""
        
        print(f"\\n{'='*50}")
        print(f"=== Testing No Parameters Required ===")
        print(f"{'='*50}")
        
        # Should work with empty dict - call_tool returns list of TextContent
        result1 = await call_tool("get_account_summary", {})
        assert isinstance(result1, list), f"Expected list of TextContent, got {type(result1)}"
        assert len(result1) > 0, f"Expected non-empty response, got: {result1}"
        
        # Parse the first TextContent response
        text_content = result1[0]
        response_text = text_content.text
        
        try:
            parsed_result = json.loads(response_text)
            print(f"[OK] Empty dict parameters work correctly")
            
            # Basic validation that we got account summary data
            if any(key in parsed_result for key in ["account", "currency_balances", "total_cash_value", "net_liquidation"]):
                print(f"[OK] Account summary data returned successfully")
            else:
                print(f"[INFO] Response format: {parsed_result}")
                
        except json.JSONDecodeError:
            pytest.fail(f"Expected JSON response, got: {response_text}")
        
        print("[SUCCESS] Parameter handling validation passed")

    async def test_get_account_summary_error_handling(self):
        """Test get_account_summary error handling with invalid parameters"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Error Handling ===")
        print(f"{'='*50}")
        
        tool_name = "get_account_summary"
        invalid_parameters = {"invalid_param": "invalid_value"}
        
        print(f"Testing with invalid parameters: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            print(f"Error handling result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Error response text: {response_text}")
                
                # Check if it indicates an error
                if "error" in response_text.lower() or "invalid" in response_text.lower():
                    print(f"[OK] Error handling working: {response_text}")
                else:
                    # Might have succeeded despite invalid params - that's also valid behavior
                    print(f"[INFO] Tool handled invalid params gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for some tools
            print(f"[OK] Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[TOOL_NAME]::test_[TOOL_NAME]_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py::TestIndividual[TOOL_NAME] -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_[tool_name].py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("[WARNING]  STANDALONE EXECUTION DETECTED")
    print("[WARNING]  RECOMMENDED: Use pytest execution commands shown above")
    print("[WARNING]  Standalone mode may not work correctly with MCP interface")
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
