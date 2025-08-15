"""
Test suite for bidirectional cache mapping in IBKR symbol resolution.
Tests the fix for cache mismatch between explicit and fuzzy searches.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

from ibkr_mcp_server.trading.international import InternationalManager


class TestBidirectionalCache:
    """Test bidirectional cache mapping functionality."""
    
    @pytest.fixture
    def mock_ib_client(self):
        """Create mock IBKR client."""
        mock_ib = Mock()
        mock_ib.isConnected.return_value = True
        return mock_ib
    
    @pytest.fixture
    def international_manager(self, mock_ib_client):
        """Create InternationalManager with mock client."""
        return InternationalManager(mock_ib_client)
    
    def test_cache_stats_initialization(self, international_manager):
        """Test that reverse lookup stats are initialized."""
        # Check that new cache stats are added
        cache_stats = international_manager.cache_stats
        assert 'reverse_lookup_hits' in cache_stats
        assert 'reverse_lookup_entries' in cache_stats
        assert cache_stats['reverse_lookup_hits'] == 0
        assert cache_stats['reverse_lookup_entries'] == 0
    
    def test_normalize_company_name(self, international_manager):
        """Test company name normalization for cache keys."""
        # Test basic normalization
        assert international_manager._normalize_company_name("Apple Inc") == "apple_inc"
        assert international_manager._normalize_company_name("Microsoft Corporation") == "microsoft_corporation"
        assert international_manager._normalize_company_name("SAP SE") == "sap_se"
        
        # Test with special characters
        assert international_manager._normalize_company_name("AT&T Inc.") == "at&t_inc"
        assert international_manager._normalize_company_name("Johnson & Johnson") == "johnson_&_johnson"
        
        # Test with spaces and case
        assert international_manager._normalize_company_name("  TESLA  ") == "tesla"
    
    def test_clean_company_name(self, international_manager):
        """Test company name cleaning (suffix removal)."""
        # Test suffix removal
        assert international_manager._clean_company_name("Apple Inc") == "Apple"
        assert international_manager._clean_company_name("Microsoft Corporation") == "Microsoft"
        assert international_manager._clean_company_name("SAP SE") == "SAP"
        assert international_manager._clean_company_name("Kongsberg Gruppen ASA") == "Kongsberg Gruppen"
        
        # Test no suffix
        assert international_manager._clean_company_name("Tesla") == "Tesla"
        assert international_manager._clean_company_name("Google") == "Google"
        
        # Test case insensitive
        assert international_manager._clean_company_name("Apple inc") == "Apple"
        assert international_manager._clean_company_name("microsoft corp") == "microsoft"
    
    def test_extract_company_name_variations(self, international_manager):
        """Test extraction of company name variations for caching."""
        # Sample match data
        match = {
            'name': 'Apple Inc',
            'symbol': 'AAPL',
            'exchange': 'NASDAQ'
        }
        
        variations = international_manager._extract_company_name_variations(match)
        
        expected_variations = ['Apple Inc', 'Apple', 'AAPL']
        assert all(var in variations for var in expected_variations)
        
        # Test with complex name
        match_complex = {
            'name': 'Kongsberg Gruppen ASA',
            'symbol': 'KOG',
            'exchange': 'OSE'
        }
        
        variations_complex = international_manager._extract_company_name_variations(match_complex)
        expected_complex = ['Kongsberg Gruppen ASA', 'Kongsberg Gruppen', 'KOG']
        assert all(var in variations_complex for var in expected_complex)
    
    def test_cache_resolution_with_reverse_lookup(self, international_manager):
        """Test that caching creates reverse lookup entries."""
        # Sample resolution result
        result = {
            'matches': [
                {
                    'name': 'Apple Inc',
                    'symbol': 'AAPL',
                    'exchange': 'NASDAQ',
                    'currency': 'USD',
                    'confidence': 1.0
                }
            ],
            'resolution_method': 'exact_symbol'
        }
        
        cache_key = "AAPL_NASDAQ_USD_STK_5_False"
        
        # Cache the resolution
        international_manager._cache_resolution(cache_key, result)
        
        # Check main cache entry exists
        assert cache_key in international_manager.resolution_cache
        
        # Check reverse lookup entries were created
        reverse_keys = [
            "reverse_lookup_apple_inc",
            "reverse_lookup_apple", 
            "reverse_lookup_aapl"
        ]
        
        for reverse_key in reverse_keys:
            assert reverse_key in international_manager.resolution_cache
            cached_entry = international_manager.resolution_cache[reverse_key]
            assert cached_entry['data']['redirect_to'] == cache_key
            assert cached_entry.get('is_reverse_lookup') == True
    
    def test_get_cached_resolution_with_redirect(self, international_manager):
        """Test that reverse lookup redirects work correctly."""
        # Setup main cache entry
        main_result = {
            'matches': [
                {
                    'name': 'Tesla Inc',
                    'symbol': 'TSLA',
                    'exchange': 'NASDAQ',
                    'currency': 'USD'
                }
            ]
        }
        
        main_cache_key = "TSLA_NASDAQ_USD_STK_5_False"
        
        # Manually create cache entries to test redirect
        timestamp = datetime.now(timezone.utc).timestamp()
        
        international_manager.resolution_cache[main_cache_key] = {
            'data': main_result,
            'timestamp': timestamp,
            'hit_count': 0
        }
        
        reverse_key = "reverse_lookup_tesla"
        international_manager.resolution_cache[reverse_key] = {
            'data': {'redirect_to': main_cache_key},
            'timestamp': timestamp,
            'hit_count': 0,
            'is_reverse_lookup': True
        }
        
        # Test reverse lookup redirect
        result = international_manager._get_cached_resolution(reverse_key)
        
        assert result is not None
        assert result['matches'][0]['symbol'] == 'TSLA'
        
        # Check hit counts were updated
        assert international_manager.resolution_cache[reverse_key]['hit_count'] == 1
        assert international_manager.resolution_cache[main_cache_key]['hit_count'] == 1
    
    def test_check_reverse_lookup_cache(self, international_manager):
        """Test reverse lookup cache checking functionality."""
        # Setup cache with reverse lookup
        main_result = {
            'matches': [
                {
                    'name': 'Microsoft Corporation',
                    'symbol': 'MSFT',
                    'exchange': 'NASDAQ',
                    'currency': 'USD'
                }
            ]
        }
        
        main_cache_key = "MSFT_NASDAQ_USD_STK_5_False"
        timestamp = datetime.now(timezone.utc).timestamp()
        
        international_manager.resolution_cache[main_cache_key] = {
            'data': main_result,
            'timestamp': timestamp,
            'hit_count': 0
        }
        
        international_manager.resolution_cache["reverse_lookup_microsoft"] = {
            'data': {'redirect_to': main_cache_key},
            'timestamp': timestamp,
            'hit_count': 0,
            'is_reverse_lookup': True
        }
        
        # Test exact match
        result = international_manager._check_reverse_lookup_cache("Microsoft")
        assert result is not None
        assert len(result) == 1
        assert result[0]['symbol'] == 'MSFT'
        
        # Test variation match
        result = international_manager._check_reverse_lookup_cache("MICROSOFT")
        assert result is not None
        assert len(result) == 1
        assert result[0]['symbol'] == 'MSFT'
        
        # Test no match
        result = international_manager._check_reverse_lookup_cache("NonExistentCompany")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fuzzy_search_with_reverse_lookup(self, international_manager):
        """Test that fuzzy search checks reverse lookup cache first."""
        # Setup cache with explicit resolution
        main_result = {
            'matches': [
                {
                    'name': 'Advanced Semiconductor Materials Lithography',
                    'symbol': 'ASML',
                    'exchange': 'AEB',
                    'currency': 'EUR'
                }
            ]
        }
        
        main_cache_key = "ASML_AEB_EUR_STK_5_False"
        timestamp = datetime.now(timezone.utc).timestamp()
        
        international_manager.resolution_cache[main_cache_key] = {
            'data': main_result,
            'timestamp': timestamp,
            'hit_count': 0
        }
        
        international_manager.resolution_cache["reverse_lookup_asml"] = {
            'data': {'redirect_to': main_cache_key},
            'timestamp': timestamp,
            'hit_count': 0,
            'is_reverse_lookup': True
        }
        
        # Mock rate limiting to pass
        with patch.object(international_manager, '_enforce_rate_limiting', return_value=True):
            # Test fuzzy search should find cached result via reverse lookup
            result = await international_manager._resolve_fuzzy_search("ASML")
            
            assert len(result) == 1
            assert result[0]['symbol'] == 'ASML'
            assert result[0]['exchange'] == 'AEB'
            
            # Verify it was a cache hit, not a new search
            assert international_manager.cache_stats['hits'] > 0
    
    def test_cache_cleanup_preserves_reverse_lookups(self, international_manager):
        """Test that cache cleanup properly handles reverse lookup entries."""
        # Create main entry and reverse lookup
        timestamp = datetime.now(timezone.utc).timestamp()
        
        # Main entry with high hit count (should be preserved)
        main_key = "AAPL_NASDAQ_USD_STK_5_False"
        international_manager.resolution_cache[main_key] = {
            'data': {'matches': [{'symbol': 'AAPL'}]},
            'timestamp': timestamp,
            'hit_count': 100
        }
        
        # Reverse lookup pointing to main entry
        reverse_key = "reverse_lookup_apple"
        international_manager.resolution_cache[reverse_key] = {
            'data': {'redirect_to': main_key},
            'timestamp': timestamp,
            'hit_count': 50,
            'is_reverse_lookup': True
        }
        
        # Low hit count entry (should be removed)
        old_key = "OLD_SYMBOL_KEY"
        international_manager.resolution_cache[old_key] = {
            'data': {'matches': [{'symbol': 'OLD'}]},
            'timestamp': timestamp - 1000,  # Old timestamp
            'hit_count': 1
        }
        
        # Fill cache to trigger cleanup
        international_manager.max_cache_size = 2
        
        # Add one more entry to trigger cleanup
        international_manager._cache_resolution("NEW_KEY", {'matches': []})
        
        # Verify that main and reverse lookup entries are preserved
        assert main_key in international_manager.resolution_cache
        assert reverse_key in international_manager.resolution_cache
        # Old entry should be removed
        assert old_key not in international_manager.resolution_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
