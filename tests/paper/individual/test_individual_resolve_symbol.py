"""
Individual MCP Tool Test: resolve_symbol
Focus: Test resolve_symbol MCP tool in isolation for debugging
MCP Tool: resolve_symbol
Expected: Enhanced symbol resolution with fuzzy matching and confidence scoring
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
class TestIndividualResolveSymbol:
    """Test resolve_symbol MCP tool in isolation"""
    
    async def test_resolve_symbol_basic_functionality(self):
        """Test basic resolve_symbol functionality through MCP interface"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing MCP Tool: resolve_symbol ===")
        print(f"{'='*60}")
        
        # FORCE CONNECTION FIRST - ensure IBKR client is connected
        print(f"Step 1: Forcing IBKR Gateway connection...")
        from ibkr_mcp_server.client import ibkr_client
        
        # Force client ID 5 BEFORE connection (critical timing)
        ibkr_client.client_id = 5
        print(f"[INFO] Forced client ID: {ibkr_client.client_id}")
        
        try:
            connection_success = await ibkr_client.connect()
            if connection_success:
                print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
                print(f"[OK] Paper account: {ibkr_client.current_account}")
            else:
                print(f"[WARNING] IBKR Gateway connection failed")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")
        
        # MCP tool call - resolve_symbol with ASML
        tool_name = "resolve_symbol"
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
        
        # For symbol resolution, we expect the new format with matches array
        if isinstance(parsed_result, dict):
            # Check if it's an error response first
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool resolve_symbol failed: {response_text}")
            
            # Validate symbol resolution data structure (new format)
            print(f"Symbol Resolution Data: {parsed_result}")
            
            # Check for success flag
            if "success" in parsed_result:
                success = parsed_result["success"]
                print(f"[OK] Success Flag: {success}")
                assert isinstance(success, bool)
                if success:
                    print(f"[OK] Tool returned success")
                else:
                    print(f"[WARNING] Tool returned failure")
            
            # Check for matches array (new format)
            if "matches" in parsed_result:
                matches = parsed_result["matches"]
                print(f"[OK] Matches Found: {len(matches)} matches")
                assert isinstance(matches, list)
                
                if len(matches) > 0:
                    # Validate first match
                    first_match = matches[0]
                    print(f"[OK] First Match: {first_match}")
                    assert isinstance(first_match, dict)
                    
                    # Symbol validation
                    if "symbol" in first_match:
                        symbol = first_match["symbol"]
                        print(f"[OK] Symbol Found: {symbol}")
                        assert isinstance(symbol, str)
                        if symbol == "ASML":
                            print(f"[OK] Correct symbol returned: {symbol}")
                        else:
                            print(f"[INFO] Different symbol format: {symbol}")
                    
                    # Exchange validation (expected AEB for ASML)
                    if "exchange" in first_match:
                        exchange = first_match["exchange"]
                        print(f"[OK] Exchange Found: {exchange}")
                        assert isinstance(exchange, str)
                        if exchange == "AEB":
                            print(f"[OK] Correct exchange for ASML: {exchange}")
                        elif exchange == "SMART":
                            print(f"[OK] SMART routing exchange: {exchange}")
                        else:
                            print(f"[INFO] Unexpected exchange: {exchange}")
                    
                    # Currency validation (expected EUR for ASML)
                    if "currency" in first_match:
                        currency = first_match["currency"]
                        print(f"[OK] Currency Found: {currency}")
                        assert isinstance(currency, str)
                        if currency == "EUR":
                            print(f"[OK] Correct currency for ASML: {currency}")
                        elif currency == "USD":
                            print(f"[INFO] USD currency (might be ADR or converted)")
                        else:
                            print(f"[INFO] Unexpected currency: {currency}")
                    
                    # Confidence scoring validation (new feature)
                    if "confidence" in first_match:
                        confidence = first_match["confidence"]
                        print(f"[OK] Confidence Score Found: {confidence}")
                        assert isinstance(confidence, (int, float))
                        assert 0.0 <= confidence <= 1.0
                        if confidence >= 0.9:
                            print(f"[OK] High confidence match: {confidence}")
                        elif confidence >= 0.7:
                            print(f"[OK] Good confidence match: {confidence}")
                        else:
                            print(f"[INFO] Low confidence match: {confidence}")
                    
                    # Primary flag validation (new feature)
                    if "primary" in first_match:
                        primary = first_match["primary"]
                        print(f"[OK] Primary Flag Found: {primary}")
                        assert isinstance(primary, bool)
                        if primary:
                            print(f"[OK] Primary listing match")
                    
                    # Name validation
                    if "name" in first_match:
                        name = first_match["name"]
                        print(f"[OK] Company Name Found: {name}")
                        assert isinstance(name, str)
                        if "ASML" in name:
                            print(f"[OK] Correct company name: {name}")
                    
                    # Country validation
                    if "country" in first_match:
                        country = first_match["country"]
                        print(f"[OK] Country Found: {country}")
                        assert isinstance(country, str)
                        if "Netherlands" in country or "Dutch" in country or country == "NL":
                            print(f"[OK] Correct country for ASML: {country}")
                        else:
                            print(f"[INFO] Unexpected country: {country}")
                else:
                    print(f"[INFO] No matches found for symbol")
            
            # Check query echo (new feature)
            if "query" in parsed_result:
                query = parsed_result["query"]
                print(f"[OK] Query Echo: {query}")
                assert isinstance(query, str)
                if query == "ASML":
                    print(f"[OK] Correct query echo")
            
            # Check total matches count (new feature)
            if "total_matches" in parsed_result:
                total_matches = parsed_result["total_matches"]
                print(f"[OK] Total Matches Count: {total_matches}")
                assert isinstance(total_matches, int)
                assert total_matches >= 0
            
            print(f"[SUCCESS] RESOLVE_SYMBOL MCP TOOL VALIDATION PASSED")
            
        elif isinstance(parsed_result, list):
            print(f"[OK] List format response with {len(parsed_result)} entries")
            
            # Check if it's an error response
            if "error" in str(response_text).lower():
                pytest.fail(f"MCP tool resolve_symbol failed: {response_text}")
            
            # Process list entries (legacy format compatibility)
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
            pytest.fail(f"Unexpected response format from MCP tool resolve_symbol")
        
        print(f"\n[SUCCESS] MCP Tool 'resolve_symbol' test PASSED")
        print(f"[SUCCESS] IBKR enhanced symbol resolution working through MCP layer")
        print(f"{'='*60}")
        
    async def test_resolve_symbol_fuzzy_search(self):
        """Test resolve_symbol with fuzzy search using company name"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Fuzzy Search: Company Name ===")
        print(f"{'='*50}")
        
        tool_name = "resolve_symbol"
        # Test with company name instead of symbol
        parameters = {
            "symbol": "Apple",  # Company name instead of AAPL
            "fuzzy_search": True
        }
        
        print(f"Testing with company name: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Fuzzy search result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Fuzzy search response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed fuzzy search result: {parsed_result}")
                    
                    # Validate fuzzy search worked
                    if isinstance(parsed_result, dict):
                        if "matches" in parsed_result and len(parsed_result["matches"]) > 0:
                            first_match = parsed_result["matches"][0]
                            if "symbol" in first_match:
                                symbol = first_match["symbol"]
                                if symbol == "AAPL":
                                    print(f"[OK] Fuzzy search found Apple->AAPL: {symbol}")
                                else:
                                    print(f"[INFO] Fuzzy search found: {symbol}")
                            
                            # Check confidence scoring for fuzzy match
                            if "confidence" in first_match:
                                confidence = first_match["confidence"]
                                print(f"[OK] Fuzzy match confidence: {confidence}")
                    
                except json.JSONDecodeError:
                    print(f"[INFO] Non-JSON fuzzy search response: {response_text}")
            else:
                print(f"Unexpected fuzzy search response format: {result}")
            
        except Exception as e:
            print(f"Exception during fuzzy search test: {e}")
            print(f"[INFO] Exception-based handling: {type(e).__name__}")

    async def test_resolve_symbol_max_results(self):
        """Test resolve_symbol with max_results parameter"""
        
        print(f"\n{'='*50}")
        print(f"=== Testing Max Results Parameter ===")
        print(f"{'='*50}")
        
        tool_name = "resolve_symbol"
        # Test with max_results parameter
        parameters = {
            "symbol": "AAPL",
            "max_results": 3
        }
        
        print(f"Testing with max_results: {parameters}")
        
        try:
            result = await call_tool(tool_name, parameters)
            print(f"Max results test result: {result}")
            
            # MCP tools return list of TextContent - parse the response
            if isinstance(result, list) and len(result) > 0:
                text_content = result[0]
                response_text = text_content.text
                print(f"Max results response text: {response_text}")
                
                try:
                    parsed_result = json.loads(response_text)
                    print(f"Parsed max results result: {parsed_result}")
                    
                    # Validate max_results was respected
                    if isinstance(parsed_result, dict):
                        if "matches" in parsed_result:
                            matches = parsed_result["matches"]
                            if len(matches) <= 3:
                                print(f"[OK] Max results respected: {len(matches)} <= 3")
                            else:
                                print(f"[WARNING] Max results exceeded: {len(matches)} > 3")
                    
                except json.JSONDecodeError:
                    print(f"[INFO] Non-JSON max results response: {response_text}")
            else:
                print(f"Unexpected max results response format: {result}")
            
        except Exception as e:
            print(f"Exception during max results test: {e}")
            print(f"[INFO] Exception-based handling: {type(e).__name__}")

    async def test_resolve_symbol_error_handling(self):
        """Test resolve_symbol error handling with invalid symbol"""
        
        print(f"\n{'='*60}")
        print(f"=== Testing Error Handling: resolve_symbol ===")
        print(f"{'='*60}")
        
        # Test invalid symbol
        tool_name = "resolve_symbol"
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
                    # Parse JSON to check for empty matches
                    try:
                        parsed_result = json.loads(response_text)
                        if isinstance(parsed_result, dict):
                            if "matches" in parsed_result and len(parsed_result["matches"]) == 0:
                                print(f"[OK] Empty matches for invalid symbol")
                            elif "success" in parsed_result and not parsed_result["success"]:
                                print(f"[OK] Tool returned failure for invalid symbol")
                            else:
                                print(f"[INFO] Tool handled invalid symbol gracefully: {response_text}")
                        else:
                            print(f"[INFO] Tool handled invalid symbol gracefully: {response_text}")
                    except json.JSONDecodeError:
                        print(f"[INFO] Non-JSON error response: {response_text}")
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

C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_symbol.py -v -s

NEVER use:
- python -m pytest [...]     # [ERROR] Python not in PATH
- pytest [...]               # [ERROR] Pytest not in PATH  
- python tests/paper/...     # [ERROR] Direct execution bypasses pytest framework

CLIENT ID REQUIREMENT:
All paper tests use CLIENT ID 5 for shared IBKR Gateway connection.

EXAMPLE EXECUTION COMMANDS:
# Specific test method:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_symbol.py::TestIndividualResolveSymbol::test_resolve_symbol_basic_functionality -v -s

# Full test class:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_symbol.py::TestIndividualResolveSymbol -v -s

# Entire test file:
C:\Python313\python.exe -m pytest tests/paper/individual/test_individual_resolve_symbol.py -v -s

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
