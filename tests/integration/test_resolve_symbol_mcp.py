"""
Integration tests for resolve_symbol MCP tool functionality.

Tests the resolve_symbol tool through the MCP interface to ensure proper
integration between the tool layer and the underlying implementation.
"""
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from ibkr_mcp_server.tools import call_tool
from mcp.types import TextContent


def extract_json_from_mcp_response(response_list):
    """Helper to extract JSON data from MCP TextContent response"""
    if not response_list or not isinstance(response_list, list):
        return None
    
    first_response = response_list[0]
    if not isinstance(first_response, TextContent):
        return None
    
    try:
        return json.loads(first_response.text)
    except (json.JSONDecodeError, AttributeError):
        return None


def extract_text_from_mcp_response(response_list):
    """Helper to extract plain text from MCP TextContent response"""
    if not response_list or not isinstance(response_list, list):
        return None
    
    first_response = response_list[0]
    if not isinstance(first_response, TextContent):
        return None
    
    return first_response.text


@pytest.mark.integration
class TestResolveSymbolMCPIntegration:
    """Test resolve_symbol through MCP tool interface"""
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_basic_mocked(self):
        """Test basic resolve_symbol MCP tool call with mocked backend"""
        # Mock the client method to avoid IBKR connection requirement
        mock_result = {
            "symbol": "AAPL",
            "matches": [{
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "conid": 265598,
                "exchange": "SMART",
                "currency": "USD",
                "confidence": 0.7
            }],
            "resolution_method": "exact_symbol",
            "cache_info": {"cache_hit": False, "cache_key": "aapl_smart_usd_stk_5"}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = mock_result
            
            # Test the MCP tool interface
            response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            
            # Validate MCP response structure
            assert isinstance(response, list), "MCP response should be a list"
            assert len(response) == 1, "MCP response should have one TextContent item"
            assert isinstance(response[0], TextContent), "Response item should be TextContent"
            
            # Extract and validate JSON content
            result = extract_json_from_mcp_response(response)
            assert result is not None, "Should be able to parse JSON from response"
            assert "matches" in result, "Result should have matches field"
            assert "symbol" in result, "Result should have symbol field"
            assert result["symbol"] == "AAPL", "Symbol should match input"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_parameters_mocked(self):
        """Test resolve_symbol MCP tool with various parameters"""
        mock_result = {
            "symbol": "ASML",
            "matches": [{
                "symbol": "ASML",
                "name": "ASML Holding NV",
                "conid": 117589399,
                "exchange": "AEB",
                "currency": "EUR",
                "confidence": 0.6
            }],
            "resolution_method": "exact_symbol",
            "cache_info": {"cache_hit": False, "cache_key": "asml_aeb_eur_stk_5"}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = mock_result
            
            test_cases = [
                # Basic symbol
                {"symbol": "AAPL"},
                
                # With exchange and currency
                {"symbol": "ASML", "exchange": "AEB", "currency": "EUR"},
                
                # With fuzzy search
                {"symbol": "Apple", "fuzzy_search": True},
                
                # With max results
                {"symbol": "AAPL", "max_results": 3},
                
                # With include alternatives
                {"symbol": "AAPL", "include_alternatives": True},
                
                # All parameters
                {
                    "symbol": "ASML",
                    "exchange": "SMART",
                    "currency": "USD", 
                    "fuzzy_search": False,
                    "include_alternatives": True,
                    "max_results": 5
                }
            ]
            
            for case in test_cases:
                response = await call_tool("resolve_symbol", case)
                
                # Each call should return a valid MCP response
                assert isinstance(response, list), f"Should return list for {case}"
                assert len(response) == 1, f"Should have one response for {case}"
                assert isinstance(response[0], TextContent), f"Should be TextContent for {case}"
                
                # Should be able to extract result (either JSON or error text)
                result = extract_json_from_mcp_response(response)
                if result is None:
                    # If not JSON, should be error text
                    error_text = extract_text_from_mcp_response(response)
                    assert error_text is not None, f"Should have error text for {case}"
                    assert "Error" in error_text, f"Error text should indicate error for {case}"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_validation(self):
        """Test MCP tool parameter validation"""
        invalid_cases = [
            # Missing required symbol
            {},
            
            # Invalid max_results (outside 1-16 range)
            {"symbol": "AAPL", "max_results": 0},
            {"symbol": "AAPL", "max_results": 20},
            
            # Invalid types
            {"symbol": 123},
            {"symbol": "AAPL", "fuzzy_search": "invalid"},
            {"symbol": "AAPL", "include_alternatives": "invalid"},
            {"symbol": "AAPL", "max_results": "invalid"},
        ]
        
        for case in invalid_cases:
            try:
                response = await call_tool("resolve_symbol", case)
                
                # Should return error response
                assert isinstance(response, list), f"Should return list for invalid case: {case}"
                assert len(response) == 1, f"Should have one response for invalid case: {case}"
                
                # Should be error text (not JSON)
                result = extract_json_from_mcp_response(response)
                if result is not None:
                    # If it's JSON, should have error field
                    assert "error" in result or result.get("success") == False, f"JSON result should indicate error for {case}"
                else:
                    # If not JSON, should be error text
                    error_text = extract_text_from_mcp_response(response)
                    assert error_text is not None, f"Should have error text for {case}"
                    assert "Error" in error_text, f"Should indicate error for {case}"
                    
            except Exception as e:
                # Parameter validation errors are also acceptable
                assert isinstance(e, (ValueError, TypeError, KeyError)), f"Should raise appropriate exception for {case}"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_error_handling(self):
        """Test MCP tool error handling and propagation"""
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            # Mock different types of errors
            error_cases = [
                (ValueError("Invalid symbol"), "symbol validation error"),
                (ConnectionError("Not connected"), "connection error"),
                (Exception("General error"), "general error"),
            ]
            
            for exception, description in error_cases:
                mock_resolve.side_effect = exception
                
                response = await call_tool("resolve_symbol", {"symbol": "TEST"})
                
                # Should handle errors gracefully
                assert isinstance(response, list), f"Should return list for {description}"
                assert len(response) == 1, f"Should have one response for {description}"
                
                # Should be error text
                error_text = extract_text_from_mcp_response(response)
                assert error_text is not None, f"Should have error text for {description}"
                assert "Error resolving symbol:" in error_text, f"Should have specific error prefix for {description}"
                assert str(exception) in error_text, f"Should contain original error message for {description}"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_response_format(self):
        """Test that MCP tool returns properly formatted response"""
        mock_result = {
            "symbol": "AAPL",
            "matches": [{
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "conid": 265598,
                "exchange": "SMART",
                "currency": "USD",
                "confidence": 0.7
            }],
            "resolution_method": "exact_symbol",
            "cache_info": {"cache_hit": False, "cache_key": "aapl_smart_usd_stk_5"}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = mock_result
            
            response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            
            # Validate MCP response structure
            assert isinstance(response, list), "Response should be list"
            assert len(response) == 1, "Response should have one item"
            assert isinstance(response[0], TextContent), "Response item should be TextContent"
            assert response[0].type == "text", "TextContent should have type 'text'"
            
            # Extract and validate JSON structure
            result = extract_json_from_mcp_response(response)
            assert result is not None, "Should be valid JSON"
            
            # Check resolve_symbol response structure
            expected_fields = ["symbol", "matches", "resolution_method", "cache_info"]
            for field in expected_fields:
                assert field in result, f"Response should have {field} field"
            
            # Validate matches structure
            assert isinstance(result["matches"], list), "matches should be list"
            if len(result["matches"]) > 0:
                match = result["matches"][0]
                assert isinstance(match, dict), "Match should be dict"
                assert "symbol" in match, "Match should have symbol"
                assert "conid" in match, "Match should have conid"
                assert "confidence" in match, "Match should have confidence"
            
            # Validate cache_info structure
            assert isinstance(result["cache_info"], dict), "cache_info should be dict"
            assert "cache_hit" in result["cache_info"], "cache_info should have cache_hit"
            assert "cache_key" in result["cache_info"], "cache_info should have cache_key"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_safety_integration(self):
        """Test integration with safety framework"""
        mock_result = {"symbol": "AAPL", "matches": [], "resolution_method": "exact_symbol", "cache_info": {}}
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = mock_result
            
            # resolve_symbol should be classified as market_data operation (safe)
            response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            
            # Should not be blocked by safety framework
            assert isinstance(response, list), "Should return response list"
            
            # Should not have safety validation errors
            result = extract_json_from_mcp_response(response)
            error_text = extract_text_from_mcp_response(response)
            
            if result is not None:
                assert result.get("error") != "Safety validation failed", "resolve_symbol should not be blocked by safety framework"
            if error_text is not None:
                assert "Safety validation failed" not in error_text, "resolve_symbol should not be blocked by safety framework"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_concurrent_calls(self):
        """Test concurrent MCP tool calls"""
        import asyncio
        
        mock_results = [
            {"symbol": "AAPL", "matches": [{"symbol": "AAPL", "conid": 265598}], "resolution_method": "exact_symbol", "cache_info": {}},
            {"symbol": "MSFT", "matches": [{"symbol": "MSFT", "conid": 272093}], "resolution_method": "exact_symbol", "cache_info": {}},
            {"symbol": "GOOGL", "matches": [{"symbol": "GOOGL", "conid": 208813719}], "resolution_method": "exact_symbol", "cache_info": {}},
        ]
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.side_effect = mock_results
            
            # Make multiple concurrent calls
            tasks = [
                call_tool("resolve_symbol", {"symbol": "AAPL"}),
                call_tool("resolve_symbol", {"symbol": "MSFT"}),
                call_tool("resolve_symbol", {"symbol": "GOOGL"}),
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All calls should complete
            assert len(responses) == 3, "Should have 3 responses"
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    pytest.fail(f"Concurrent call {i} raised exception: {response}")
                
                assert isinstance(response, list), f"Concurrent call {i} should return list"
                assert len(response) == 1, f"Concurrent call {i} should have one response"
                assert isinstance(response[0], TextContent), f"Concurrent call {i} should be TextContent"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_rate_limiting(self):
        """Test that MCP tool respects rate limiting"""
        with patch('ibkr_mcp_server.tools.safety_manager.rate_limiter.check_rate_limit') as mock_rate_limit:
            # Test rate limit exceeded scenario
            mock_rate_limit.return_value = False  # Rate limit exceeded
            
            response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            
            # Should return rate limit error
            assert isinstance(response, list), "Should return response list"
            assert len(response) == 1, "Should have one response"
            
            result = extract_json_from_mcp_response(response)
            assert result is not None, "Should be JSON response"
            assert result.get("success") == False, "Should indicate failure"
            assert "Rate limit exceeded" in result.get("error", ""), "Should indicate rate limit error"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_mcp_tool_special_commands(self):
        """Test special cache management commands"""
        with patch('ibkr_mcp_server.tools.ibkr_client.international_manager') as mock_manager:
            mock_manager.clear_cache = Mock()
            mock_manager.get_cache_statistics = Mock(return_value={"hits": 10, "misses": 5})
            mock_manager.api_call_stats = {"total_calls": 15}
            mock_manager.fuzzy_search_stats = {"fuzzy_calls": 3}
            
            # Test cache clear command
            response = await call_tool("resolve_symbol", {"symbol": "CLEAR_CACHE"})
            result = extract_json_from_mcp_response(response)
            
            assert result is not None, "Should return JSON for CLEAR_CACHE"
            assert result.get("success") == True, "CLEAR_CACHE should succeed"
            assert "cache_cleared" in result.get("action", ""), "Should indicate cache cleared"
            mock_manager.clear_cache.assert_called_once()
            
            # Test cache stats command
            response = await call_tool("resolve_symbol", {"symbol": "CACHE_STATS"})
            result = extract_json_from_mcp_response(response)
            
            assert result is not None, "Should return JSON for CACHE_STATS"
            assert result.get("success") == True, "CACHE_STATS should succeed"
            assert "cache_statistics" in result, "Should have cache statistics"
            assert "api_call_statistics" in result, "Should have API call statistics"


@pytest.mark.integration
class TestResolveSymbolMCPToolWorkflows:
    """Test common workflows using resolve_symbol MCP tool"""
    
    @pytest.mark.asyncio
    async def test_symbol_resolution_workflow_mocked(self):
        """Test typical symbol resolution workflow"""
        # Mock resolve_symbol result
        mock_resolve_result = {
            "symbol": "AAPL",
            "matches": [{
                "symbol": "AAPL",
                "conid": 265598,
                "exchange": "SMART",
                "currency": "USD"
            }],
            "resolution_method": "exact_symbol",
            "cache_info": {}
        }
        
        # Mock market data result
        mock_market_result = {
            "AAPL": {
                "symbol": "AAPL",
                "price": 150.25,
                "contract_id": 265598,
                "exchange": "SMART"
            }
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve, \
             patch('ibkr_mcp_server.tools.ibkr_client.get_market_data', new_callable=AsyncMock) as mock_market:
            
            mock_resolve.return_value = mock_resolve_result
            mock_market.return_value = mock_market_result
            
            # Step 1: Resolve symbol
            resolve_response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            resolve_result = extract_json_from_mcp_response(resolve_response)
            
            assert resolve_result is not None, "Should get resolve result"
            assert "matches" in resolve_result, "Should have matches"
            assert len(resolve_result["matches"]) > 0, "Should have at least one match"
            
            symbol = resolve_result["matches"][0]["symbol"]
            assert symbol == "AAPL", "Should resolve to AAPL"
            
            # Step 2: Get market data for resolved symbol
            market_response = await call_tool("get_market_data", {"symbols": symbol})
            market_result = extract_json_from_mcp_response(market_response)
            
            assert market_result is not None, "Should get market data result"
            assert "AAPL" in market_result, "Should have AAPL data"
            
            # ConIDs should match between resolve and market data
            resolved_conid = resolve_result["matches"][0]["conid"]
            market_conid = market_result["AAPL"]["contract_id"]
            assert resolved_conid == market_conid, "ConIDs should match between resolve_symbol and get_market_data"
    
    @pytest.mark.asyncio
    async def test_fuzzy_search_workflow_mocked(self):
        """Test fuzzy search workflow"""
        # Mock fuzzy search result
        mock_fuzzy_result = {
            "symbol": "Apple",
            "matches": [{
                "symbol": "AAPL",
                "conid": 265598,
                "confidence": 0.5
            }],
            "resolution_method": "fuzzy_search",
            "cache_info": {}
        }
        
        # Mock exact search result
        mock_exact_result = {
            "symbol": "AAPL",
            "matches": [{
                "symbol": "AAPL",
                "conid": 265598,
                "confidence": 0.7
            }],
            "resolution_method": "exact_symbol",
            "cache_info": {}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.side_effect = [mock_fuzzy_result, mock_exact_result]
            
            # Step 1: Try fuzzy search for company name
            fuzzy_response = await call_tool("resolve_symbol", {
                "symbol": "Apple",
                "fuzzy_search": True
            })
            
            fuzzy_result = extract_json_from_mcp_response(fuzzy_response)
            assert fuzzy_result is not None, "Should get fuzzy result"
            
            if fuzzy_result.get("matches") and len(fuzzy_result["matches"]) > 0:
                resolved_symbol = fuzzy_result["matches"][0]["symbol"]
                assert resolved_symbol == "AAPL", "Should resolve to AAPL"
                
                # Step 2: Verify with exact symbol lookup
                exact_response = await call_tool("resolve_symbol", {"symbol": resolved_symbol})
                exact_result = extract_json_from_mcp_response(exact_response)
                
                assert exact_result is not None, "Should get exact result"
                if exact_result.get("matches") and len(exact_result["matches"]) > 0:
                    # ConIDs should match
                    fuzzy_conid = fuzzy_result["matches"][0]["conid"]
                    exact_conid = exact_result["matches"][0]["conid"]
                    assert fuzzy_conid == exact_conid, "ConIDs should match between fuzzy and exact resolution"
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow_mocked(self):
        """Test error recovery workflow"""
        mock_valid_result = {
            "symbol": "AAPL",
            "matches": [{"symbol": "AAPL", "conid": 265598}],
            "resolution_method": "exact_symbol",
            "cache_info": {}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            # First call fails
            mock_resolve.side_effect = [Exception("Invalid symbol"), mock_valid_result]
            
            # Step 1: Try invalid symbol
            invalid_response = await call_tool("resolve_symbol", {"symbol": "INVALIDXYZ"})
            
            # Should handle error gracefully
            assert isinstance(invalid_response, list), "Should return response for invalid symbol"
            error_text = extract_text_from_mcp_response(invalid_response)
            assert error_text is not None, "Should have error text"
            assert "Error resolving symbol:" in error_text, "Should indicate error"
            
            # Step 2: Try valid symbol - should work even after error
            valid_response = await call_tool("resolve_symbol", {"symbol": "AAPL"})
            valid_result = extract_json_from_mcp_response(valid_response)
            
            # Valid symbol should work even after invalid one
            assert valid_result is not None, "Should get valid result after error"
            assert "matches" in valid_result, "Should have matches"
    
    @pytest.mark.asyncio
    async def test_parameter_variation_workflow_mocked(self):
        """Test workflow with parameter variations"""
        mock_result = {
            "symbol": "AAPL",
            "matches": [{"symbol": "AAPL", "conid": 265598}],
            "resolution_method": "exact_symbol",
            "cache_info": {}
        }
        
        with patch('ibkr_mcp_server.tools.ibkr_client.resolve_symbol', new_callable=AsyncMock) as mock_resolve:
            mock_resolve.return_value = mock_result
            
            base_params = {"symbol": "AAPL"}
            
            # Test different parameter combinations
            param_variations = [
                {},
                {"max_results": 1},
                {"max_results": 5},
                {"include_alternatives": True},
                {"fuzzy_search": False},
                {"exchange": "SMART"},
                {"currency": "USD"},
            ]
            
            results = []
            for variation in param_variations:
                params = {**base_params, **variation}
                response = await call_tool("resolve_symbol", params)
                results.append((variation, response))
            
            # All variations should work
            for variation, response in results:
                assert isinstance(response, list), f"Should return list for variation: {variation}"
                assert len(response) == 1, f"Should have one response for variation: {variation}"
                
                # Should have consistent structure (either JSON or error)
                result = extract_json_from_mcp_response(response)
                if result is not None:
                    # Check if it's a successful response or an error response
                    if result.get("success", True) and "matches" in result:
                        # Successful response
                        assert "matches" in result, f"Should have matches for variation: {variation}"
                        if len(result["matches"]) > 0:
                            match = result["matches"][0]
                            assert match["symbol"] == "AAPL", f"Should resolve to AAPL for variation: {variation}"
                    elif not result.get("success", True):
                        # Error response (like rate limiting) - this is acceptable in integration tests
                        assert "error" in result, f"Error response should have error field for variation: {variation}"
                        # Rate limiting errors are acceptable in integration tests
                        if "rate limit" in result.get("error", "").lower():
                            continue  # Skip validation for rate-limited requests
                        else:
                            # Other errors should still be validated
                            assert False, f"Unexpected error for variation {variation}: {result['error']}"
                    else:
                        assert False, f"Unexpected response structure for variation {variation}: {result}"
                else:
                    # If not JSON, should be error text
                    error_text = extract_text_from_mcp_response(response)
                    assert error_text is not None, f"Should have error text for variation: {variation}"
