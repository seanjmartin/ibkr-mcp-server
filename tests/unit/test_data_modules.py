"""
Tests for data modules (reference data, forex pairs, international symbols, etc.)

This module tests the static reference data used throughout the IBKR MCP Server.
"""

import pytest
from typing import Dict, List, Set

from ibkr_mcp_server.data import (
    forex_manager,
    international_db,
    exchange_manager,
    MAJOR_FOREX_PAIRS,
    SUPPORTED_CURRENCIES,
    INTERNATIONAL_SYMBOLS,
    EXCHANGE_INFO
)


class TestReferenceDataLoading:
    """Test reference data loading and integrity"""
    
    def test_reference_data_loading(self):
        """Test reference data loading (forex pairs, symbols, etc.)"""
        # Test forex pairs data loading
        assert MAJOR_FOREX_PAIRS is not None
        assert isinstance(MAJOR_FOREX_PAIRS, dict)
        assert len(MAJOR_FOREX_PAIRS) > 0
        
        # Test supported currencies data
        assert SUPPORTED_CURRENCIES is not None
        assert isinstance(SUPPORTED_CURRENCIES, (list, set))
        assert len(SUPPORTED_CURRENCIES) > 0
        
        # Test international symbols data
        assert INTERNATIONAL_SYMBOLS is not None
        assert isinstance(INTERNATIONAL_SYMBOLS, dict)
        assert len(INTERNATIONAL_SYMBOLS) > 0
        
        # Test exchange info data
        assert EXCHANGE_INFO is not None
        assert isinstance(EXCHANGE_INFO, dict)
        assert len(EXCHANGE_INFO) > 0
        
        # Test manager objects are properly initialized
        assert forex_manager is not None
        assert international_db is not None
        assert exchange_manager is not None
        
        # Test critical forex pairs are present
        critical_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
        for pair in critical_pairs:
            assert pair in MAJOR_FOREX_PAIRS, f"Critical forex pair {pair} missing"
        
        # Test critical international symbols are present
        critical_symbols = ['ASML', 'SAP', '7203']  # Netherlands, Germany, Japan
        for symbol in critical_symbols:
            assert symbol in INTERNATIONAL_SYMBOLS, f"Critical symbol {symbol} missing"
        
        # Test critical exchanges are present
        critical_exchanges = ['AEB', 'XETRA', 'TSE', 'SMART']
        for exchange in critical_exchanges:
            assert exchange in EXCHANGE_INFO, f"Critical exchange {exchange} missing"
    
    def test_international_symbols_data(self):
        """Test international symbols reference data"""
        # Test that we have comprehensive symbol data
        assert len(INTERNATIONAL_SYMBOLS) >= 15, "Should have at least 15 international symbols"
        
        # Test each symbol has required fields
        required_fields = ['exchange', 'currency', 'name', 'country', 'sector']
        for symbol, data in INTERNATIONAL_SYMBOLS.items():
            assert isinstance(symbol, str), f"Symbol {symbol} should be string"
            assert len(symbol) > 0, f"Symbol {symbol} should not be empty"
            
            for field in required_fields:
                assert field in data, f"Symbol {symbol} missing required field: {field}"
                assert data[field] is not None, f"Symbol {symbol} field {field} is None"
                assert len(str(data[field])) > 0, f"Symbol {symbol} field {field} is empty"
        
        # Test regional coverage
        regions = set()
        exchanges = set()
        currencies = set()
        
        for symbol, data in INTERNATIONAL_SYMBOLS.items():
            regions.add(data['country'])
            exchanges.add(data['exchange'])
            currencies.add(data['currency'])
        
        # Test we cover major regions
        assert 'Netherlands' in regions, "Should include Dutch stocks"
        assert 'Germany' in regions, "Should include German stocks"
        assert 'Japan' in regions, "Should include Japanese stocks"
        assert 'United Kingdom' in regions or 'UK' in regions, "Should include UK stocks"
        
        # Test we cover major exchanges
        assert 'AEB' in exchanges, "Should include Euronext Amsterdam"
        assert 'XETRA' in exchanges, "Should include Frankfurt exchange"
        assert 'TSE' in exchanges, "Should include Tokyo exchange"
        
        # Test we cover major currencies
        assert 'EUR' in currencies, "Should include Euro currency"
        assert 'JPY' in currencies, "Should include Japanese Yen"
        assert 'GBP' in currencies, "Should include British Pound"
        
        # Test specific known symbols
        test_symbols = {
            'ASML': {'exchange': 'AEB', 'currency': 'EUR', 'country': 'Netherlands'},
            'SAP': {'exchange': 'XETRA', 'currency': 'EUR', 'country': 'Germany'},
            '7203': {'exchange': 'TSE', 'currency': 'JPY', 'country': 'Japan'}
        }
        
        for symbol, expected in test_symbols.items():
            assert symbol in INTERNATIONAL_SYMBOLS, f"Critical symbol {symbol} not found"
            actual = INTERNATIONAL_SYMBOLS[symbol]
            for key, value in expected.items():
                assert actual[key] == value, f"Symbol {symbol} {key}: expected {value}, got {actual[key]}"
    
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
        
        # Test international symbols data integrity
        for symbol, data in INTERNATIONAL_SYMBOLS.items():
            # Test symbol format
            assert isinstance(symbol, str), f"Symbol {symbol} should be string"
            assert len(symbol) > 0, f"Symbol {symbol} should not be empty"
            assert symbol.strip() == symbol, f"Symbol {symbol} should not have leading/trailing whitespace"
            
            # Test exchange validity
            exchange = data['exchange']
            assert exchange in EXCHANGE_INFO, f"Symbol {symbol} exchange {exchange} not found in EXCHANGE_INFO"
            
            # Test currency consistency with exchange
            symbol_currency = data['currency']
            exchange_currency = EXCHANGE_INFO[exchange]['currency']
            if exchange_currency != 'Multiple':  # IDEALPRO has Multiple currencies
                assert symbol_currency == exchange_currency, f"Symbol {symbol} currency {symbol_currency} doesn't match exchange {exchange} currency {exchange_currency}"
            
            # Test required fields are not empty
            required_fields = ['name', 'country', 'sector']
            for field in required_fields:
                value = data[field]
                assert isinstance(value, str), f"Symbol {symbol} field {field} should be string"
                assert len(value.strip()) > 0, f"Symbol {symbol} field {field} should not be empty"
            
            # Test sector is valid (get all actual sectors from data first to validate they exist)
            all_sectors = set(data_item['sector'] for data_item in INTERNATIONAL_SYMBOLS.values())
            valid_sectors = [
                'Technology', 'Healthcare', 'Energy', 'Finance', 'Consumer', 'Consumer Goods', 
                'Industrial', 'Telecommunications', 'Automotive', 'Materials', 'Utilities', 
                'Pharmaceuticals', 'Mining', 'Real Estate', 'Financial Services'
            ]
            sector = data['sector']
            assert sector in valid_sectors or sector in all_sectors, f"Symbol {symbol} has unexpected sector: {sector}. All sectors: {sorted(all_sectors)}"
        
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
        
        # Test cross-reference integrity
        # Ensure all currencies in INTERNATIONAL_SYMBOLS exist in SUPPORTED_CURRENCIES
        symbol_currencies = set()
        for symbol, data in INTERNATIONAL_SYMBOLS.items():
            symbol_currencies.add(data['currency'])
        
        for currency in symbol_currencies:
            assert currency in SUPPORTED_CURRENCIES, f"Currency {currency} from INTERNATIONAL_SYMBOLS not in SUPPORTED_CURRENCIES"
        
        # Ensure all exchanges in INTERNATIONAL_SYMBOLS exist in EXCHANGE_INFO
        symbol_exchanges = set()
        for symbol, data in INTERNATIONAL_SYMBOLS.items():
            symbol_exchanges.add(data['exchange'])
        
        for exchange in symbol_exchanges:
            assert exchange in EXCHANGE_INFO, f"Exchange {exchange} from INTERNATIONAL_SYMBOLS not in EXCHANGE_INFO"
        
        # Test that major forex currencies are supported
        forex_currencies = set()
        for pair, data in MAJOR_FOREX_PAIRS.items():
            forex_currencies.add(data['base'])
            forex_currencies.add(data['quote'])
        
        for currency in forex_currencies:
            assert currency in SUPPORTED_CURRENCIES, f"Forex currency {currency} not in SUPPORTED_CURRENCIES"
        
        # Test data consistency - ensure we have good coverage
        assert len(MAJOR_FOREX_PAIRS) >= 20, f"Should have at least 20 forex pairs, got {len(MAJOR_FOREX_PAIRS)}"
        assert len(INTERNATIONAL_SYMBOLS) >= 15, f"Should have at least 15 international symbols, got {len(INTERNATIONAL_SYMBOLS)}"
        assert len(EXCHANGE_INFO) >= 10, f"Should have at least 10 exchanges, got {len(EXCHANGE_INFO)}"
        assert len(SUPPORTED_CURRENCIES) >= 10, f"Should have at least 10 supported currencies, got {len(SUPPORTED_CURRENCIES)}"
