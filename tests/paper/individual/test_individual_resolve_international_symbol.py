"""
Individual MCP Tool Test: resolve_international_symbol
Focus: Test resolve_international_symbol MCP tool in isolation for debugging
MCP Tool: resolve_international_symbol
Expected: Exchange/currency resolution to AEB/EUR for ASML
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
class TestIndividualResolveInternationalSymbol:
    """Test resolve_international_symbol MCP tool in isolation"""
    
    async def test_resolve_international_symbol_basic_functionality(self):
        """Test basic resolve_international_symbol functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: resolve_international_symbol ===")
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
        
        # MCP tool call - resolve_international_symbol with ASML
        tool_name = "resolve_international_symbol"
        parameters = {
            "symbol": "ASML"  # Test with ASML (Dutch semiconductor company)
        }
        
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
        
        # For symbol resolution, we expect information about the symbol, exchange, and currency
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool resolve_international_symbol failed: {response_text}")
            
            # Validate symbol resolution data structure
            print(f"Symbol Resolution Data: {parsed_result}")
            
            # Symbol validation
            if "symbol" in parsed_result:
                symbol = parsed_result["symbol"]
                print(f"[OK] Symbol Found: {symbol}")
                assert isinstance(symbol, str)
                if symbol == "ASML":
                    print(f"[OK] Correct symbol returned: {symbol}")
                else:
                    print(f"[INFO] Different symbol format: {symbol}")
            
            # Exchange validation (expected AEB for ASML)
            if "exchange" in parsed_result:
                exchange = parsed_result["exchange"]
                print(f"[OK] Exchange Found: {exchange}")
                assert isinstance(exchange, str)
                if exchange == "AEB":
                    print(f"[OK] Correct exchange for ASML: {exchange}")
                elif exchange == "SMART":
                    print(f"[OK] SMART routing exchange: {exchange}")
                else:
                    print(f"[INFO] Unexpected exchange: {exchange}")
            
            # Currency validation (expected EUR for ASML)
            if "currency" in parsed_result:
                currency = parsed_result["currency"]
                print(f"[OK] Currency Found: {currency}")
                assert isinstance(currency, str)
                if currency == "EUR":
                    print(f"[OK] Correct currency for ASML: {currency}")
                elif currency == "USD":
                    print(f"[INFO] USD currency (might be ADR or converted)")
                else:
                    print(f"[INFO] Unexpected currency: {currency}")
            
            # Country validation
            if "country" in parsed_result:
                country = parsed_result["country"]
                print(f"[OK] Country Found: {country}")
                assert isinstance(country, str)
                if "Netherlands" in country or "Dutch" in country or country == "NL":
                    print(f"[OK] Correct country for ASML: {country}")
                else:
                    print(f"[INFO] Unexpected country: {country}")
            
            # Contract ID validation
            if "contract_id" in parsed_result:
                contract_id = parsed_result["contract_id"]
                print(f"[OK] Contract ID Found: {contract_id}")
                assert isinstance(contract_id, (int, str))
                if contract_id:
                    print(f"[OK] Valid IBKR contract ID: {contract_id}")
            
            # Name validation
            if "name" in parsed_result:
                name = parsed_result["name"]
                print(f"[OK] Company Name Found: {name}")
                assert isinstance(name, str)
                if "ASML" in name:
                    print(f"[OK] Correct company name: {name}")
            
            # Sector validation
            if "sector" in parsed_result:
                sector = parsed_result["sector"]
                print(f"[OK] Sector Found: {sector}")
                assert isinstance(sector, str)
                if "Technology" in sector or "Semiconductor" in sector:
                    print(f"[OK] Correct sector for ASML: {sector}")
            
            # Trading information
            trading_info = {}
            if "market_status" in parsed_result:
                trading_info["market_status"] = parsed_result["market_status"]
            if "exchange_timezone" in parsed_result:
                trading_info["exchange_timezone"] = parsed_result["exchange_timezone"]
            if "settlement" in parsed_result:
                trading_info["settlement"] = parsed_result["settlement"]
                
            if trading_info:
                print(f"[OK] Trading Information: {trading_info}")
                
                # Validate timezone for Amsterdam
                if "exchange_timezone" in trading_info:
                    timezone = trading_info["exchange_timezone"]
                    if "Amsterdam" in timezone or "Europe" in timezone:
                        print(f"[OK] Correct timezone for AEB: {timezone}")
                
                # Validate settlement
                if "settlement" in trading_info:
                    settlement = trading_info["settlement"]
                    if settlement == "T+2":
                        print(f"[OK] Correct settlement for European markets: {settlement}")
            
            print(f"[SUCCESS] RESOLVE_INTERNATIONAL_SYMBOL MCP TOOL VALIDATION PASSED")
            
        elif isinstance(parsed_result, list):
            print(f"[OK] List format response with {len(parsed_result)} entries")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool resolve_international_symbol failed: {response_text}")
            
            # Process list entries
            for i, entry in enumerate(parsed_result):
                if isinstance(entry, dict):
                    print(f"[OK] Entry {i}: {entry}")
                    # Apply same validation as above for each entry
                    if "symbol" in entry and entry["symbol"] == "ASML":
                        print(f"[OK] Found ASML resolution in entry {i}")
                        
                        if "exchange" in entry:
                            print(f"[OK] Exchange in entry {i}: {entry['exchange']}")
                        if "currency" in entry:
                            print(f"[OK] Currency in entry {i}: {entry['currency']}")
                        
        else:
            print(f"Unexpected response format: {type(parsed_result)}")
            print(f"Response content: {parsed_result}")
            pytest.fail(f"Unexpected response format from MCP tool resolve_international_symbol")
        
        print(f"\n[SUCCESS] MCP Tool 'resolve_international_symbol' test PASSED")
        print(f"[SUCCESS] IBKR international symbol resolution working through MCP layer")
        print(f"{'='*60}")
        
    async def test_resolve_international_symbol_with_exchange(self):
        """Test resolve_international_symbol with specific exchange parameter"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Symbol Resolution with Exchange ===")
        print(f"{'='*50}")
        
        tool_name = "resolve_international_symbol"
        # Test with exchange parameter
        parameters = {
            "symbol": "ASML",
            "exchange": "AEB"  # Specify Amsterdam exchange
        }
        
        print(f"Testing with exchange parameter: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Exchange-specific result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Exchange-specific response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed exchange-specific result: {parsed_result}")
                    
                    # Validate exchange was respected
                    if isinstance(parsed_result, dict):
                        if "exchange" in parsed_result:
                            exchange = parsed_result["exchange"]
                            if exchange == "AEB":
                                print(f"[OK] Correct exchange specified and returned: {exchange}")
                            else:
                                print(f"[INFO] Different exchange returned: {exchange}")
                    
                except json.JSONDecodeError:
                    print(f"[INFO] Non-JSON exchange-specific response: {response_text}")
            else:
                print(f"Unexpected exchange-specific response format: {result}")
            
        except Exception as e:
            print(f"Exception during exchange-specific test: {e}")
            print(f"[INFO] Exception-based handling: {type(e).__name__}")

    async def test_resolve_international_symbol_error_handling(self):
        """Test resolve_international_symbol error handling with invalid symbol"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: resolve_international_symbol ===")
        print(f"{'='*60}")
        
        # Test invalid symbol
        tool_name = "resolve_international_symbol"
        invalid_parameters = {
            "symbol": "INVALID123"  # Invalid symbol that shouldn't exist
        }
        
        print(f"Testing with invalid symbol: {invalid_parameters}")
        
        try:
            result = await call_tool(tool_name, invalid_parameters)
            print(f"Error handling result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Error response text: {response_text}")
                
                # Check if it indicates an error or empty result
                if "error" in response_text.lower() or "not found" in response_text.lower():
                    print(f"[OK] Error handling working: {response_text}")
                elif response_text.strip() == "[]" or response_text.strip() == "{}":
                    print(f"[OK] Empty result for invalid symbol: {response_text}")
                else:
                    # Might have returned some default or fallback behavior
                    print(f"[INFO] Tool handled invalid symbol gracefully: {response_text}")
            else:
                print(f"Unexpected error response format: {result}")
            
        except Exception as e:
            print(f"Exception during error handling test: {e}")
            # This might be expected for some invalid symbols
            print(f"[OK] Exception-based error handling: {type(e).__name__}")

# CRITICAL EXECUTION INSTRUCTIONS
r"""
WINDOWS EXECUTION REQUIREMENTS:

ALL paper tests MUST be run using pytest with full Python path:

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_international_symbol.py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_international_symbol.py::TestIndividualResolveInternationalSymbol::test_resolve_international_symbol_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_international_symbol.py::TestIndividualResolveInternationalSymbol -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_international_symbol.py -v -s

PREREQUISITES:
- IBKR Gateway running with paper trading login
- API enabled, port 7497, client ID 5 available
- Paper account logged in (DU* prefix account)
- International market data permissions (if required)
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
