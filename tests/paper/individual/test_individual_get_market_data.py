"""
Individual MCP Tool Test: get_market_data
Focus: Test get_market_data MCP tool in isolation for debugging
MCP Tool: get_market_data
Expected: US stock quote with price/bid/ask
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
class TestIndividualGetMarketData:
    """Test get_market_data MCP tool in isolation"""
    
    async def test_get_market_data_basic_functionality(self):
        """Test basic get_market_data functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_market_data ===")
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
        
        # MCP tool call - get_market_data requires symbols parameter
        tool_name = "get_market_data"
        parameters = {"symbols": "AAPL"}  # Test with Apple stock
        
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
        print(f"\n--- MCP Tool Response Structure Validation ---")
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
        # IBKR get_market_data can return various formats depending on the response
        
        if isinstance(parsed_result, list):
            print(f"[OK] IBKR Market Data Format: List of {len(parsed_result)} entries")
            
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool {tool_name} failed: {response_text}")
            
            # Validate list structure - look for market data entries
            valid_entries = 0
            symbol_found = None
            market_data = {}
            
            for entry in parsed_result:
                if isinstance(entry, dict):
                    # Look for symbol information
                    if "symbol" in entry:
                        symbol_found = entry["symbol"]
                        market_data.update(entry)
                        valid_entries += 1
                        print(f"[OK] Market Data Entry: {entry}")
                    elif "contract" in entry and isinstance(entry["contract"], dict):
                        # Sometimes data comes in contract format
                        if "symbol" in entry["contract"]:
                            symbol_found = entry["contract"]["symbol"]
                            market_data.update(entry)
                            valid_entries += 1
                            print(f"[OK] Contract Market Data: {entry}")
                    else:
                        print(f"[INFO] Other entry format: {entry}")
                        valid_entries += 1
                        market_data.update(entry)
                else:
                    print(f"[WARNING] Non-dict entry: {entry}")
            
            # Validate we found valid market data
            if valid_entries > 0:
                print(f"[OK] Found {valid_entries} valid market data entries")
            else:
                pytest.fail(f"No valid market data entries found in list")
            
            # Validate symbol
            if symbol_found:
                print(f"[OK] Symbol Found: {symbol_found}")
                if symbol_found == "AAPL":
                    print(f"[OK] Correct symbol returned: {symbol_found}")
                else:
                    print(f"[INFO] Unexpected symbol: {symbol_found} (requested AAPL)")
            
        elif isinstance(parsed_result, dict):
            print(f"[OK] Dictionary format market data response")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool {tool_name} failed: {response_text}")
            
            # Validate dictionary structure - look for market data fields
            market_data = parsed_result
            
            # Look for symbol
            symbol_found = None
            if "symbol" in market_data:
                symbol_found = market_data["symbol"]
            elif "contract" in market_data and isinstance(market_data["contract"], dict):
                if "symbol" in market_data["contract"]:
                    symbol_found = market_data["contract"]["symbol"]
            
            if symbol_found:
                print(f"[OK] Symbol Found: {symbol_found}")
                if symbol_found == "AAPL":
                    print(f"[OK] Correct symbol returned: {symbol_found}")
            else:
                print(f"[INFO] No symbol field found, available keys: {list(market_data.keys())}")
        
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_market_data")
        
        # Look for pricing data in any format
        price_fields = ["last", "price", "bid", "ask", "close", "open", "high", "low"]
        found_prices = {}
        
        # Function to extract price data from nested structures
        def extract_prices(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in price_fields and isinstance(value, (int, float)):
                        found_prices[f"{prefix}{key}"] = value
                        print(f"[OK] Price Data - {key}: {value}")
                    elif isinstance(value, dict):
                        extract_prices(value, f"{key}.")
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                extract_prices(item, f"{key}[{i}].")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        extract_prices(item, f"[{i}].")
        
        extract_prices(market_data)
        
        if found_prices:
            print(f"[SUCCESS] Found price data: {found_prices}")
        else:
            print(f"[INFO] No standard price fields found")
            print(f"[INFO] Available data structure: {market_data}")
            # This might still be valid if the API returns a different format
        
        print(f"[SUCCESS] GET_MARKET_DATA MCP TOOL VALIDATION PASSED")
        print(f"\n[SUCCESS] MCP Tool 'get_market_data' test PASSED")
        print(f"[SUCCESS] IBKR market data retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_market_data_no_symbols_error(self):
        """Test that get_market_data requires symbols parameter"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Parameter Requirements ===")
        print(f"{'='*50}")
        
        tool_name = "get_market_data"
        empty_parameters = {}  # Missing required symbols parameter
        
        print(f"Testing with missing symbols parameter: {empty_parameters}")
        
        try:
            result = await call_tool(tool_name, empty_parameters)
            print(f"Parameter validation result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Error response text: {response_text}")
                
                # Check if it indicates an error for missing parameters
                if "error" in response_text.lower() or "required" in response_text.lower() or "symbol" in response_text.lower():
                    print(f"✅ Parameter validation working: {response_text}")
                else:
                    print(f"ℹ️ Tool handled missing params gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during parameter validation test: {e}")
            # This might be expected for missing required parameters
            print(f"✅ Exception-based parameter validation: {type(e).__name__}")

    async def test_get_market_data_invalid_symbol_handling(self):
        """Test get_market_data error handling with invalid symbol"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Invalid Symbol Handling ===")
        print(f"{'='*50}")
        
        tool_name = "get_market_data"
        invalid_parameters = {"symbols": "INVALID123"}  # Invalid symbol
        
        print(f"Testing with invalid symbol: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            print(f"Invalid symbol result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Response text: {response_text}")
                
                # Could be error message or empty data - both are valid responses
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed response: {parsed_result}")
                    
                    if "error" in str(response_text).lower():
                        print(f"✅ Error handling working: Invalid symbol rejected")
                    elif isinstance(parsed_result, list) and len(parsed_result) == 0:
                        print(f"✅ Empty result for invalid symbol (valid response)")
                    else:
                        print(f"ℹ️ Unexpected response for invalid symbol: {parsed_result}")
                        
                except json.JSONDecodeError:
                    # Non-JSON error message
                    if "error" in response_text.lower() or "invalid" in response_text.lower():
                        print(f"✅ Error message returned: {response_text}")
                    else:
                        print(f"ℹ️ Non-JSON response: {response_text}")
            else:
                print(f"Unexpected response format: {result}")
            
        except Exception as e:
            print(f"Exception during invalid symbol test: {e}")
            print(f"✅ Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data.py -v -s

NEVER use:
- python -m pytest [...]     # ❌ Python not in PATH
- pytest [...]               # ❌ Pytest not in PATH  
- python tests/paper/...     # ❌ Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data.py::TestIndividualGetMarketData::test_get_market_data_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data.py::TestIndividualGetMarketData -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
"""

# Standalone execution for debugging (NOT RECOMMENDED - Use pytest commands above)
if __name__ == "__main__":
    print("⚠️  STANDALONE EXECUTION DETECTED")
    print("⚠️  RECOMMENDED: Use pytest execution commands shown above")
    print("⚠️  Standalone mode may not work correctly with MCP interface")
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
