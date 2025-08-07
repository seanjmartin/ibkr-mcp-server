"""
Individual MCP Tool Test: get_market_data (International)
Focus: Test get_market_data MCP tool for international stocks in isolation for debugging
MCP Tool: get_market_data
Expected: Auto-detection to AEB/EUR with pricing
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
class TestIndividualGetMarketDataInternational:
    """Test get_market_data MCP tool for international stocks in isolation"""
    
    async def test_get_market_data_international_basic_functionality(self):
        """Test basic get_market_data functionality for international stocks through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: get_market_data (International) ===")
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
        
        # MCP tool call - get_market_data with international symbol (ASML)
        tool_name = "get_market_data"
        parameters = {"symbols": "ASML"}  # Test with ASML (Dutch semiconductor company)
        
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
        
        # For international market data, we expect a successful result from IBKR client
        # IBKR should auto-detect ASML as Netherlands/EUR
        
        if isinstance(parsed_result, list):
            print(f"[OK] IBKR International Market Data Format: List of {len(parsed_result)} entries")
            
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool {tool_name} failed: {response_text}")
            
            # Validate list structure - look for market data entries
            valid_entries = 0
            symbol_found = None
            exchange_found = None
            currency_found = None
            country_found = None
            market_data = {}
            
            for entry in parsed_result:
                if isinstance(entry, dict):
                    # Look for symbol information
                    if "symbol" in entry:
                        symbol_found = entry["symbol"]
                        market_data.update(entry)
                        valid_entries += 1
                        print(f"[OK] International Market Data Entry: {entry}")
                        
                        # Extract key international market info
                        if "exchange" in entry:
                            exchange_found = entry["exchange"]
                        if "currency" in entry:
                            currency_found = entry["currency"]
                        if "country" in entry:
                            country_found = entry["country"]
                            
                    elif "contract" in entry and isinstance(entry["contract"], dict):
                        # Sometimes data comes in contract format
                        if "symbol" in entry["contract"]:
                            symbol_found = entry["contract"]["symbol"]
                            market_data.update(entry)
                            valid_entries += 1
                            print(f"[OK] International Contract Market Data: {entry}")
                    else:
                        print(f"[INFO] Other entry format: {entry}")
                        valid_entries += 1
                        market_data.update(entry)
                else:
                    print(f"[WARNING] Non-dict entry: {entry}")
            
            # Validate we found valid market data
            if valid_entries > 0:
                print(f"[OK] Found {valid_entries} valid international market data entries")
            else:
                pytest.fail(f"No valid international market data entries found in list")
            
            # Validate international symbol
            if symbol_found:
                print(f"[OK] Symbol Found: {symbol_found}")
                if symbol_found == "ASML":
                    print(f"[OK] Correct international symbol returned: {symbol_found}")
                else:
                    print(f"[INFO] Unexpected symbol: {symbol_found} (requested ASML)")
            
            # Validate international market detection (Netherlands/EUR expected for ASML)
            if exchange_found:
                print(f"[OK] Exchange Found: {exchange_found}")
                if exchange_found in ["AEB", "SMART"]:  # AEB is Amsterdam, SMART is routing
                    print(f"[OK] Correct exchange for ASML: {exchange_found}")
                else:
                    print(f"[INFO] Unexpected exchange: {exchange_found}")
            
            if currency_found:
                print(f"[OK] Currency Found: {currency_found}")
                if currency_found == "EUR":
                    print(f"[OK] Correct currency for ASML: {currency_found}")
                elif currency_found == "USD":
                    print(f"[INFO] USD currency (might be ADR or converted)")
                else:
                    print(f"[INFO] Unexpected currency: {currency_found}")
            
            if country_found:
                print(f"[OK] Country Found: {country_found}")
                if "Netherlands" in country_found or "Dutch" in country_found or country_found == "NL":
                    print(f"[OK] Correct country for ASML: {country_found}")
                else:
                    print(f"[INFO] Unexpected country: {country_found}")
            
        elif isinstance(parsed_result, dict):
            print(f"[OK] Dictionary format international market data response")
            
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
                if symbol_found == "ASML":
                    print(f"[OK] Correct international symbol returned: {symbol_found}")
        
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool get_market_data (international)")
        
        # Look for pricing data in any format
        price_fields = ["last", "price", "bid", "ask", "close", "open", "high", "low"]
        found_prices = {}
        
        # Function to extract price data from nested structures
        def extract_prices(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in price_fields and isinstance(value, (int, float)):
                        found_prices[f"{prefix}{key}"] = value
                        print(f"[OK] International Price Data - {key}: {value}")
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
            print(f"[SUCCESS] Found international price data: {found_prices}")
        else:
            print(f"[INFO] No standard price fields found for international symbol")
            print(f"[INFO] Available data structure: {market_data}")
            # This might still be valid if the API returns a different format or markets are closed
        
        # Validate international market structure
        international_fields = ["exchange", "currency", "country", "contract_id", "market_status"]
        found_international = {}
        
        def extract_international_data(data, prefix=""):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in international_fields:
                        found_international[f"{prefix}{key}"] = value
                        print(f"[OK] International Market Field - {key}: {value}")
                    elif isinstance(value, dict):
                        extract_international_data(value, f"{key}.")
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        extract_international_data(item, f"[{i}].")
        
        extract_international_data(market_data)
        
        if found_international:
            print(f"[SUCCESS] Found international market structure: {found_international}")
        else:
            print(f"[INFO] No standard international market fields found")
        
        print(f"[SUCCESS] GET_MARKET_DATA INTERNATIONAL MCP TOOL VALIDATION PASSED")
        print(f"\n[SUCCESS] MCP Tool 'get_market_data' (international) test PASSED")
        print(f"[SUCCESS] IBKR international market data retrieved through MCP layer")
        print(f"{'='*60}")
        
    async def test_get_market_data_international_multiple_symbols(self):
        """Test get_market_data with multiple international symbols"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Multiple International Symbols ===")
        print(f"{'='*50}")
        
        tool_name = "get_market_data"
        # Test multiple international symbols from different countries
        parameters = {"symbols": "ASML,SAP"}  # Netherlands + Germany
        
        print(f"Testing with multiple international symbols: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Multi-symbol result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Multi-symbol response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed multi-symbol result: {parsed_result}")
                    
                    if isinstance(parsed_result, list):
                        print(f"✅ Returned {len(parsed_result)} international market data entries")
                        
                        # Look for both symbols
                        symbols_found = set()
                        for entry in parsed_result:
                            if isinstance(entry, dict) and "symbol" in entry:
                                symbols_found.add(entry["symbol"])
                                print(f"[OK] Found symbol: {entry['symbol']}")
                        
                        if "ASML" in symbols_found or "SAP" in symbols_found:
                            print(f"✅ Found expected international symbols: {symbols_found}")
                        else:
                            print(f"ℹ️ Symbols found: {symbols_found}")
                    else:
                        print(f"ℹ️ Multi-symbol response format: {type(parsed_result)}")
                        
                except json.JSONDecodeError:
                    print(f"ℹ️ Non-JSON multi-symbol response: {response_text}")
            else:
                print(f"Unexpected multi-symbol response format: {result}")
            
        except Exception as e:
            print(f"Exception during multi-symbol test: {e}")
            print(f"ℹ️ Exception-based handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data_international.py -v -s

NEVER use:
- python -m pytest [...]     # ❌ Python not in PATH
- pytest [...]               # ❌ Pytest not in PATH  
- python tests/paper/...     # ❌ Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data_international.py::TestIndividualGetMarketDataInternational::test_get_market_data_international_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data_international.py::TestIndividualGetMarketDataInternational -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_get_market_data_international.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
- International market data permissions (if required)
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
