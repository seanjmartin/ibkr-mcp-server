"""
Tests for data modules (reference data, forex pairs, international symbols, etc.)

This module tests the static reference data used throughout the IBKR MCP Server.
"""

import pytest
from typing import Dict, List, Set

from ibkr_mcp_server.data import (
    forex_manager,
    exchange_manager,
    MAJOR_FOREX_PAIRS,
    SUPPORTED_CURRENCIES,
    EXCHANGE_INFO
)


class TestReferenceDataLoading:
    """Test reference data loading and integrity"""
    
    def test_reference_data_loading(self):
        """Test reference data loading (forex pairs, exchanges, etc.)"""
        # Test forex pairs data loading
        assert MAJOR_FOREX_PAIRS is not None
        assert isinstance(MAJOR_FOREX_PAIRS, dict)
        assert len(MAJOR_FOREX_PAIRS) > 0
        
        # Test supported currencies data
        assert SUPPORTED_CURRENCIES is not None
        assert isinstance(SUPPORTED_CURRENCIES, (list, set))
        assert len(SUPPORTED_CURRENCIES) > 0
        
        # Test exchange info data
        assert EXCHANGE_INFO is not None
        assert isinstance(EXCHANGE_INFO, dict)
        assert len(EXCHANGE_INFO) > 0
        
        # Test manager objects are properly initialized
        assert forex_manager is not None
        assert exchange_manager is not None
        
        # Test critical forex pairs are present
        critical_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
        for pair in critical_pairs:
            assert pair in MAJOR_FOREX_PAIRS, f"Critical forex pair {pair} missing"
        
        # Test critical exchanges are present
        critical_exchanges = ['AEB', 'XETRA', 'TSE', 'SMART']
        for exchange in critical_exchanges:
            assert exchange in EXCHANGE_INFO, f"Critical exchange {exchange} missing"
        
        # NOTE: International symbols are now resolved dynamically via IBKR API
        # instead of using a hardcoded database - see test_international_manager.py
    
    def test_international_symbols_migration_note(self):
        """Test note about international symbols migration to IBKR API"""
        # NOTE: International symbols are now resolved dynamically via IBKR's 
        # reqMatchingSymbolsAsync API instead of using a hardcoded database.
        # This provides:
        # - Coverage of thousands of symbols instead of ~15 hardcoded ones
        # - Automatic updates when IBKR adds new symbols
        # - Support for European companies that were previously failing
        # - Professional-grade fuzzy matching and typo tolerance
        #
        # For testing international symbol resolution, see:
        # - tests/unit/test_international_manager.py::test_ibkr_native_fuzzy_search_integration
        # - test_symbol_resolution_fix.py (integration verification)
        
        # Verify that we no longer have the hardcoded international symbols
        from ibkr_mcp_server.data import __all__
        assert 'INTERNATIONAL_SYMBOLS' not in __all__, "INTERNATIONAL_SYMBOLS should no longer be exported"
        assert 'international_db' not in __all__, "international_db should no longer be exported"
        
        # This test serves as documentation of the architectural change
        assert True, "International symbols now resolved via IBKR API instead of hardcoded data"
    
    def test_forex_pairs_data(self):
        """Test forex pairs reference data"""
        # Test that we have comprehensive forex pairs
        assert len(MAJOR_FOREX_PAIRS) >= 20, "Should have at least 20 forex pairs"
        
        # Test each pair has required fields
        required_fields = ['base', 'quote', 'name', 'pip_value', 'min_size', 'category']
        for pair, data in MAJOR_FOREX_PAIRS.items():
            assert isinstance(pair, str), f"Pair {pair} should be string"
            assert len(pair) == 6, f"Pair {pair} should be 6 characters (BASEPAIR format)"
            
            for field in required_fields:
                assert field in data, f"Pair {pair} missing required field: {field}"
                assert data[field] is not None, f"Pair {pair} field {field} is None"
        
        # Test major pairs are present
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        for pair in major_pairs:
            assert pair in MAJOR_FOREX_PAIRS, f"Major pair {pair} not found"
            assert MAJOR_FOREX_PAIRS[pair]['category'] == 'major', f"Pair {pair} should be categorized as major"
        
        # Test cross pairs are present
        cross_pairs = ['EURGBP', 'EURJPY', 'GBPJPY']
        for pair in cross_pairs:
            assert pair in MAJOR_FOREX_PAIRS, f"Cross pair {pair} not found"
        
        # Test currency consistency
        currencies = set()
        for pair, data in MAJOR_FOREX_PAIRS.items():
            currencies.add(data['base'])
            currencies.add(data['quote'])
            
            # Test pair format consistency
            expected_pair = data['base'] + data['quote']
            assert pair == expected_pair, f"Pair {pair} doesn't match base+quote: {expected_pair}"
        
        # Test we have major currencies
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
        for currency in major_currencies:
            assert currency in currencies, f"Major currency {currency} not found in pairs"
        
        # Test pip values are reasonable
        for pair, data in MAJOR_FOREX_PAIRS.items():
            pip_value = data['pip_value']
            if data['quote'] == 'JPY':
                assert pip_value == 0.01, f"JPY pair {pair} should have pip value 0.01"
            else:
                assert pip_value == 0.0001, f"Non-JPY pair {pair} should have pip value 0.0001"
        
        # Test minimum sizes are reasonable
        for pair, data in MAJOR_FOREX_PAIRS.items():
            min_size = data['min_size']
            assert isinstance(min_size, int), f"Pair {pair} min_size should be integer"
            assert min_size >= 1000, f"Pair {pair} min_size {min_size} too small"
            assert min_size <= 100000, f"Pair {pair} min_size {min_size} too large"
    
    def test_exchange_data(self):
        """Test exchange information data"""
        # Test that we have comprehensive exchange data
        assert len(EXCHANGE_INFO) >= 10, "Should have at least 10 exchanges"
        
        # Test each exchange has required fields
        required_fields = ['name', 'country', 'currency', 'timezone', 'trading_hours']
        for exchange, data in EXCHANGE_INFO.items():
            assert isinstance(exchange, str), f"Exchange {exchange} should be string"
            assert len(exchange) > 0, f"Exchange {exchange} should not be empty"
            
            for field in required_fields:
                assert field in data, f"Exchange {exchange} missing required field: {field}"
                assert data[field] is not None, f"Exchange {exchange} field {field} is None"
        
        # Test critical exchanges are present
        critical_exchanges = {
            'SMART': {'country': 'United States', 'currency': 'USD'},
            'AEB': {'country': 'Netherlands', 'currency': 'EUR'},
            'XETRA': {'country': 'Germany', 'currency': 'EUR'},
            'TSE': {'country': 'Japan', 'currency': 'JPY'},
            'LSE': {'country': 'United Kingdom', 'currency': 'GBP'},
            'IDEALPRO': {'currency': 'Multiple'}  # Forex exchange
        }
        
        for exchange, expected in critical_exchanges.items():
            assert exchange in EXCHANGE_INFO, f"Critical exchange {exchange} not found"
            actual = EXCHANGE_INFO[exchange]
            
            for key, value in expected.items():
                if key == 'country' and exchange == 'IDEALPRO':
                    # IDEALPRO is a global forex exchange, country might be different
                    continue
                assert actual[key] == value, f"Exchange {exchange} {key}: expected {value}, got {actual[key]}"
        
        # Test regional coverage
        countries = set()
        currencies = set()
        
        for exchange, data in EXCHANGE_INFO.items():
            if 'country' in data:
                countries.add(data['country'])
            currencies.add(data['currency'])
        
        # Test we cover major regions
        assert len(countries) >= 5, "Should cover at least 5 countries"
        
        # Test we cover major currencies
        major_currencies = ['USD', 'EUR', 'JPY', 'GBP']
        for currency in major_currencies:
            assert currency in currencies, f"Major currency {currency} not covered"
        
        # Test trading hours format (should be time objects)
        for exchange, data in EXCHANGE_INFO.items():
            trading_hours = data['trading_hours']
            assert isinstance(trading_hours, dict), f"Exchange {exchange} trading_hours should be dict"
            
            # Check if exchange has lunch break (different format)
            has_lunch_break = data.get('has_lunch_break', False)
            
            if has_lunch_break:
                # Exchanges with lunch break have morning/afternoon sessions
                assert 'morning_open' in trading_hours, f"Exchange {exchange} missing morning_open time"
                assert 'morning_close' in trading_hours, f"Exchange {exchange} missing morning_close time"
                assert 'afternoon_open' in trading_hours, f"Exchange {exchange} missing afternoon_open time"
                assert 'afternoon_close' in trading_hours, f"Exchange {exchange} missing afternoon_close time"
                
                # Test that all times are time objects
                for time_field in ['morning_open', 'morning_close', 'afternoon_open', 'afternoon_close']:
                    time_obj = trading_hours[time_field]
                    assert hasattr(time_obj, 'hour'), f"Exchange {exchange} {time_field} should be time object"
            else:
                # Regular exchanges have simple open/close
                assert 'open' in trading_hours, f"Exchange {exchange} missing open time"
                assert 'close' in trading_hours, f"Exchange {exchange} missing close time"
                
                # Test that times are time objects
                open_time = trading_hours['open']
                close_time = trading_hours['close']
                assert hasattr(open_time, 'hour'), f"Exchange {exchange} open time should be time object"
                assert hasattr(close_time, 'hour'), f"Exchange {exchange} close time should be time object"
    
    def test_data_validation(self):
        """Test data integrity validation"""
        # Test forex pairs data integrity
        for pair, data in MAJOR_FOREX_PAIRS.items():
            # Test pair format
            assert len(pair) == 6, f"Forex pair {pair} should be 6 characters"
            assert pair.isupper(), f"Forex pair {pair} should be uppercase"
            assert pair.isalpha(), f"Forex pair {pair} should contain only letters"
            
            # Test base and quote currencies
            base = data['base']
            quote = data['quote']
            assert len(base) == 3, f"Base currency {base} should be 3 characters"
            assert len(quote) == 3, f"Quote currency {quote} should be 3 characters"
            assert base.isupper(), f"Base currency {base} should be uppercase"
            assert quote.isupper(), f"Quote currency {quote} should be uppercase"
            assert base != quote, f"Base and quote currencies should be different for {pair}"
            
            # Test pair consistency
            assert pair == base + quote, f"Pair {pair} should equal base+quote: {base}{quote}"
            
            # Test pip value consistency
            pip_value = data['pip_value']
            if quote == 'JPY':
                assert pip_value == 0.01, f"JPY pair {pair} should have pip value 0.01, got {pip_value}"
            else:
                assert pip_value == 0.0001, f"Non-JPY pair {pair} should have pip value 0.0001, got {pip_value}"
            
            # Test minimum size validity
            min_size = data['min_size']
            assert isinstance(min_size, int), f"Min size for {pair} should be integer, got {type(min_size)}"
            assert min_size > 0, f"Min size for {pair} should be positive, got {min_size}"
            assert min_size >= 1000, f"Min size for {pair} should be at least 1000, got {min_size}"
        
        # NOTE: International symbols data integrity is now tested via IBKR API integration
        # See test_international_manager.py for symbol resolution testing
        pass
        
        # Test exchange data integrity
        for exchange, data in EXCHANGE_INFO.items():
            # Test exchange code format
            assert isinstance(exchange, str), f"Exchange code {exchange} should be string"
            assert len(exchange) > 0, f"Exchange code {exchange} should not be empty"
            assert exchange.isupper(), f"Exchange code {exchange} should be uppercase"
            assert exchange.strip() == exchange, f"Exchange code {exchange} should not have whitespace"
            
            # Test name is not empty
            name = data['name']
            assert isinstance(name, str), f"Exchange {exchange} name should be string"
            assert len(name.strip()) > 0, f"Exchange {exchange} name should not be empty"
            
            # Test country is valid
            country = data['country']
            assert isinstance(country, str), f"Exchange {exchange} country should be string"
            assert len(country.strip()) > 0, f"Exchange {exchange} country should not be empty"
            
            # Test currency is valid
            currency = data['currency']
            assert isinstance(currency, str), f"Exchange {exchange} currency should be string"
            if currency != 'Multiple':  # IDEALPRO has Multiple currencies
                assert len(currency) == 3, f"Exchange {exchange} currency {currency} should be 3 characters"
                assert currency.isupper(), f"Exchange {exchange} currency {currency} should be uppercase"
            
            # Test timezone is valid
            timezone = data['timezone']
            assert isinstance(timezone, str), f"Exchange {exchange} timezone should be string"
            assert len(timezone.strip()) > 0, f"Exchange {exchange} timezone should not be empty"
            
            # Test trading hours exist
            trading_hours = data['trading_hours']
            assert isinstance(trading_hours, dict), f"Exchange {exchange} trading_hours should be dict"
            assert len(trading_hours) > 0, f"Exchange {exchange} trading_hours should not be empty"
        
        # Test cross-reference integrity for remaining static data
        # Test that major forex currencies are supported
        forex_currencies = set()
        for pair, data in MAJOR_FOREX_PAIRS.items():
            forex_currencies.add(data['base'])
            forex_currencies.add(data['quote'])
        
        for currency in forex_currencies:
            assert currency in SUPPORTED_CURRENCIES, f"Forex currency {currency} not in SUPPORTED_CURRENCIES"
        
        # Test data consistency - ensure we have good coverage
        assert len(MAJOR_FOREX_PAIRS) >= 20, f"Should have at least 20 forex pairs, got {len(MAJOR_FOREX_PAIRS)}"
        assert len(EXCHANGE_INFO) >= 10, f"Should have at least 10 exchanges, got {len(EXCHANGE_INFO)}"
        assert len(SUPPORTED_CURRENCIES) >= 10, f"Should have at least 10 supported currencies, got {len(SUPPORTED_CURRENCIES)}"
        
        # NOTE: International symbols coverage is now unlimited via IBKR API integration
