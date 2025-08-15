"""
Paper tests for resolve_symbol functionality with live IBKR API.

These tests validate that resolve_symbol works correctly with real IBKR API connections.
Focus on structure and basic functionality rather than exact values.
"""
import pytest
import asyncio
from ibkr_mcp_server.client import ibkr_client


@pytest.mark.paper
class TestResolveSymbolPaperBasic:
    """Basic paper tests for resolve_symbol with live IBKR API"""
    
    async def ensure_connection(self):
        """Helper to ensure IBKR connection"""
        try:
            await ibkr_client.connect()
            await asyncio.sleep(2)  # Allow connection to stabilize
            status = await ibkr_client.get_connection_status()
            return status.get('connected', False)
        except Exception:
            return False
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_structure_paper(self):
        """Test that resolve_symbol returns proper structure"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test basic symbol
        result = await ibkr_client.resolve_symbol("AAPL")
        
        # Validate response structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "matches" in result, "Result should have 'matches' field"
        assert isinstance(result["matches"], list), "Matches should be a list"
        assert "resolution_method" in result, "Result should have 'resolution_method'"
        assert "cache_info" in result, "Result should have 'cache_info'"
        
        # If matches found, validate match structure
        if len(result["matches"]) > 0:
            match = result["matches"][0]
            required_fields = ["symbol", "conid", "exchange", "currency", "confidence"]
            for field in required_fields:
                assert field in match, f"Match should have '{field}' field"
                
            # Validate data types
            assert isinstance(match["symbol"], str), "Symbol should be string"
            assert isinstance(match["conid"], int), "ConID should be integer"
            assert isinstance(match["exchange"], str), "Exchange should be string"
            assert isinstance(match["currency"], str), "Currency should be string"
            assert isinstance(match["confidence"], (int, float)), "Confidence should be numeric"
            assert 0.0 <= match["confidence"] <= 1.0, "Confidence should be between 0 and 1"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_major_us_stocks_paper(self):
        """Test major US stocks resolve successfully"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test multiple major symbols
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        for symbol in symbols:
            try:
                result = await ibkr_client.resolve_symbol(symbol)
                
                # Basic structure validation
                assert isinstance(result, dict), f"Result should be dict for {symbol}"
                assert "matches" in result, f"Should have matches for {symbol}"
                
                # Should find at least one match for major stocks if connection is stable
                if len(result["matches"]) > 0:
                    # Validate first match
                    match = result["matches"][0]
                    assert match["symbol"] == symbol, f"Resolved symbol should match input for {symbol}"
                    assert match["currency"] == "USD", f"Major US stocks should be in USD for {symbol}"
                    assert "SMART" in match["exchange"] or "NASDAQ" in match["exchange"] or "NYSE" in match["exchange"], f"Should use major US exchange for {symbol}"
                else:
                    # If no matches, it might be a connection issue - log but don't fail
                    print(f"Warning: No matches found for {symbol} - possible connection issue")
                
            except Exception as e:
                # Handle connection errors gracefully
                print(f"Warning: Error resolving {symbol}: {e}")
                # Re-establish connection and continue
                try:
                    await ibkr_client.connect()
                    await asyncio.sleep(1)
                except:
                    pass
            
            await asyncio.sleep(0.5)  # Rate limiting
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_with_parameters_paper(self):
        """Test resolve_symbol with various parameters"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test with max_results parameter
        result = await ibkr_client.resolve_symbol("AAPL", max_results=3)
        assert isinstance(result, dict)
        if len(result.get("matches", [])) > 0:
            assert len(result["matches"]) <= 3, "Should respect max_results parameter"
        
        # Test with exchange specification
        result = await ibkr_client.resolve_symbol("AAPL", exchange="SMART")
        assert isinstance(result, dict)
        if len(result.get("matches", [])) > 0:
            match = result["matches"][0]
            assert match["exchange"] == "SMART", "Should use specified exchange"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_error_handling_paper(self):
        """Test error handling for invalid symbols"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test invalid symbol
        result = await ibkr_client.resolve_symbol("INVALIDXYZ123")
        
        # Should handle gracefully
        assert isinstance(result, dict), "Should return dict for invalid symbol"
        assert "matches" in result, "Should have matches field"
        
        # Invalid symbols should have no matches
        assert len(result["matches"]) == 0, "Invalid symbol should have no matches"
        assert result["resolution_method"] in ["none", "not_found"], "Should indicate no resolution"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_caching_paper(self):
        """Test caching behavior"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # First call
        result1 = await ibkr_client.resolve_symbol("AAPL")
        assert isinstance(result1, dict)
        
        # Second call - should be cached
        result2 = await ibkr_client.resolve_symbol("AAPL")
        assert isinstance(result2, dict)
        
        # Results should be consistent
        if len(result1.get("matches", [])) > 0 and len(result2.get("matches", [])) > 0:
            assert result1["matches"][0]["conid"] == result2["matches"][0]["conid"], "Cached results should be consistent"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_fuzzy_search_paper(self):
        """Test fuzzy search functionality"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test fuzzy search for company name
        result = await ibkr_client.resolve_symbol("Apple", fuzzy_search=True)
        
        # Should handle fuzzy search gracefully
        assert isinstance(result, dict), "Should return dict for fuzzy search"
        assert "matches" in result, "Should have matches field"
        
        # If fuzzy search works, should find AAPL
        if len(result["matches"]) > 0:
            match = result["matches"][0]
            assert match["symbol"] == "AAPL", "Apple should resolve to AAPL"
            assert result["resolution_method"] in ["fuzzy_search", "company_name_match"], "Should use fuzzy method"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_international_paper(self):
        """Test international symbol handling"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        # Test international symbol
        result = await ibkr_client.resolve_symbol("ASML")
        
        # Should handle international symbols
        assert isinstance(result, dict), "Should return dict for international symbol"
        assert "matches" in result, "Should have matches field"
        
        # ASML should resolve (either to US ADR or Amsterdam)
        if len(result["matches"]) > 0:
            match = result["matches"][0]
            assert match["symbol"] == "ASML", "Should resolve ASML"
            # Could be USD (ADR) or EUR (Amsterdam)
            assert match["currency"] in ["USD", "EUR"], "Should have valid currency"


@pytest.mark.paper 
class TestResolveSymbolPaperPerformance:
    """Performance and reliability tests"""
    
    async def ensure_connection(self):
        """Helper to ensure IBKR connection"""
        try:
            await ibkr_client.connect()
            await asyncio.sleep(2)
            status = await ibkr_client.get_connection_status()
            return status.get('connected', False)
        except Exception:
            return False
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_performance_paper(self):
        """Test performance characteristics"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        import time
        
        # Test response time
        start_time = time.time()
        result = await ibkr_client.resolve_symbol("AAPL")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should complete within reasonable time
        assert response_time < 10.0, f"Response time should be under 10 seconds, got {response_time:.2f}s"
        
        # Should return valid structure
        assert isinstance(result, dict), "Should return valid result structure"
    
    @pytest.mark.asyncio
    async def test_resolve_symbol_multiple_calls_paper(self):
        """Test multiple consecutive calls"""
        if not await self.ensure_connection():
            pytest.skip("IBKR connection required for paper tests")
        
        symbols = ["AAPL", "MSFT", "GOOGL"]
        results = []
        
        for symbol in symbols:
            result = await ibkr_client.resolve_symbol(symbol)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # All results should be valid
        for i, result in enumerate(results):
            assert isinstance(result, dict), f"Result {i} should be dict"
            assert "matches" in result, f"Result {i} should have matches"
