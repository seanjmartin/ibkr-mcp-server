"""Tests for all major exchanges added to the IBKR MCP server."""

import pytest
from datetime import time
from ibkr_mcp_server.data.exchange_info import exchange_manager, EXCHANGE_INFO


class TestMajorGlobalExchanges:
    """Test all major global exchanges added to the system."""
    
    def test_all_major_exchanges_exist(self):
        """Test that all major global exchanges are properly defined."""
        # Americas
        americas_exchanges = ['NYSE', 'NASDAQ', 'ARCA', 'BATS', 'IEX', 'TSX', 'TSXV', 'B3', 'MEXI']
        # Asia-Pacific 
        asia_exchanges = ['TWSE', 'SSE', 'SZSE', 'BSE', 'NSE', 'SGX', 'SET', 'IDX', 'KLSE', 'NZX']
        # Middle East & Africa
        mea_exchanges = ['TASE', 'TADAWUL', 'EGX', 'JSE']
        # Additional European
        euro_additional = ['LSEETF', 'GETTEX', 'TRADEGATE']
        
        all_new_exchanges = americas_exchanges + asia_exchanges + mea_exchanges + euro_additional
        
        for exchange in all_new_exchanges:
            assert exchange in EXCHANGE_INFO, f"Exchange {exchange} not found in EXCHANGE_INFO"
    
    def test_us_exchanges(self):
        """Test US exchange configurations."""
        us_exchanges = ['NYSE', 'NASDAQ', 'ARCA', 'BATS', 'IEX']
        
        for exchange in us_exchanges:
            info = exchange_manager.get_exchange_info(exchange)
            assert info is not None
            assert info['country'] == 'United States'
            assert info['currency'] == 'USD'
            assert info['timezone'] == 'America/New_York'
            assert info['settlement'] == 'T+2'
            
            # Check standard US trading hours
            trading_hours = info['trading_hours']
            assert trading_hours['open'] == '09:30'
            assert trading_hours['close'] == '16:00'
            
            # Check extended hours for main exchanges
            if exchange in ['NYSE', 'NASDAQ', 'ARCA', 'BATS', 'IEX']:
                assert 'extended_hours' in EXCHANGE_INFO[exchange]
    
    def test_canadian_exchanges(self):
        """Test Canadian exchange configurations."""
        canadian_exchanges = ['TSX', 'TSXV']
        
        for exchange in canadian_exchanges:
            info = exchange_manager.get_exchange_info(exchange)
            assert info is not None
            assert info['country'] == 'Canada'
            assert info['currency'] == 'CAD'
            assert info['timezone'] == 'America/Toronto'
            assert info['settlement'] == 'T+2'
    
    def test_latin_american_exchanges(self):
        """Test Latin American exchange configurations."""
        # Test B3 (Brazil)
        b3_info = exchange_manager.get_exchange_info('B3')
        assert b3_info is not None
        assert b3_info['name'] == 'B3 Stock Exchange'
        assert b3_info['country'] == 'Brazil'
        assert b3_info['currency'] == 'BRL'
        assert b3_info['timezone'] == 'America/Sao_Paulo'
        
        # Test MEXI (Mexico)
        mexi_info = exchange_manager.get_exchange_info('MEXI')
        assert mexi_info is not None
        assert mexi_info['name'] == 'Mexican Stock Exchange'
        assert mexi_info['country'] == 'Mexico'
        assert mexi_info['currency'] == 'MXN'
        assert mexi_info['timezone'] == 'America/Mexico_City'
    
    def test_asian_exchanges(self):
        """Test Asian exchange configurations."""
        # Test major Asian exchanges
        asian_configs = [
            ('TWSE', 'Taiwan', 'TWD', 'Asia/Taipei'),
            ('SSE', 'China', 'CNY', 'Asia/Shanghai'),
            ('SZSE', 'China', 'CNY', 'Asia/Shanghai'),
            ('BSE', 'India', 'INR', 'Asia/Kolkata'),
            ('NSE', 'India', 'INR', 'Asia/Kolkata'),
            ('SGX', 'Singapore', 'SGD', 'Asia/Singapore'),
            ('SET', 'Thailand', 'THB', 'Asia/Bangkok'),
            ('IDX', 'Indonesia', 'IDR', 'Asia/Jakarta'),
            ('KLSE', 'Malaysia', 'MYR', 'Asia/Kuala_Lumpur'),
            ('NZX', 'New Zealand', 'NZD', 'Pacific/Auckland')
        ]
        
        for exchange, country, currency, timezone in asian_configs:
            info = exchange_manager.get_exchange_info(exchange)
            assert info is not None
            assert info['country'] == country
            assert info['currency'] == currency
            assert info['timezone'] == timezone
    
    def test_lunch_break_exchanges(self):
        """Test exchanges with lunch breaks."""
        lunch_break_exchanges = ['SSE', 'SZSE', 'SET', 'IDX', 'KLSE']
        
        for exchange in lunch_break_exchanges:
            exchange_info = EXCHANGE_INFO[exchange]
            assert exchange_info.get('has_lunch_break') == True
            
            # Should have morning and afternoon sessions
            trading_hours = exchange_info['trading_hours']
            assert 'morning_open' in trading_hours
            assert 'morning_close' in trading_hours
            assert 'afternoon_open' in trading_hours
            assert 'afternoon_close' in trading_hours
    
    def test_middle_east_africa_exchanges(self):
        """Test Middle East and African exchange configurations."""
        # Test TASE (Israel)
        tase_info = exchange_manager.get_exchange_info('TASE')
        assert tase_info is not None
        assert tase_info['name'] == 'Tel Aviv Stock Exchange'
        assert tase_info['country'] == 'Israel'
        assert tase_info['currency'] == 'ILS'
        assert tase_info['timezone'] == 'Asia/Jerusalem'
        
        # Test TADAWUL (Saudi Arabia)
        tadawul_info = exchange_manager.get_exchange_info('TADAWUL')
        assert tadawul_info is not None
        assert tadawul_info['name'] == 'Saudi Stock Exchange'
        assert tadawul_info['country'] == 'Saudi Arabia'
        assert tadawul_info['currency'] == 'SAR'
        
        # Test JSE (South Africa)
        jse_info = exchange_manager.get_exchange_info('JSE')
        assert jse_info is not None
        assert jse_info['name'] == 'Johannesburg Stock Exchange'
        assert jse_info['country'] == 'South Africa'
        assert jse_info['currency'] == 'ZAR'
        assert jse_info['settlement'] == 'T+3'  # Different from T+2
    
    def test_special_settlement_periods(self):
        """Test exchanges with non-standard settlement periods."""
        # Chinese exchanges use T+1
        chinese_exchanges = ['SSE', 'SZSE']
        for exchange in chinese_exchanges:
            info = exchange_manager.get_exchange_info(exchange)
            assert info['settlement'] == 'T+1'
        
        # South African exchange uses T+3
        jse_info = exchange_manager.get_exchange_info('JSE')
        assert jse_info['settlement'] == 'T+3'
        
        # Most others use T+2
        t2_exchanges = ['NYSE', 'NASDAQ', 'TSX', 'B3', 'TWSE', 'BSE', 'NSE', 'SGX']
        for exchange in t2_exchanges:
            info = exchange_manager.get_exchange_info(exchange)
            assert info['settlement'] == 'T+2'
    
    def test_currency_validation_all_exchanges(self):
        """Test currency validation for all new exchanges."""
        currency_mappings = {
            'USD': ['NYSE', 'NASDAQ', 'ARCA', 'BATS', 'IEX'],
            'CAD': ['TSX', 'TSXV'],
            'BRL': ['B3'],
            'MXN': ['MEXI'],
            'TWD': ['TWSE'],
            'CNY': ['SSE', 'SZSE'],
            'INR': ['BSE', 'NSE'],
            'SGD': ['SGX'],
            'THB': ['SET'],
            'IDR': ['IDX'],
            'MYR': ['KLSE'],
            'NZD': ['NZX'],
            'ILS': ['TASE'],
            'SAR': ['TADAWUL'],
            'EGP': ['EGX'],
            'ZAR': ['JSE'],
            'EUR': ['LSEETF', 'GETTEX', 'TRADEGATE']
        }
        
        for currency, exchanges in currency_mappings.items():
            for exchange in exchanges:
                assert exchange_manager.validate_currency_for_exchange(exchange, currency)
                # Test that wrong currency fails
                wrong_currency = 'USD' if currency != 'USD' else 'EUR'
                assert not exchange_manager.validate_currency_for_exchange(exchange, wrong_currency)
    
    def test_extended_hours_trading(self):
        """Test extended hours configurations."""
        # US exchanges should have extended hours
        us_exchanges = ['NYSE', 'NASDAQ', 'ARCA', 'BATS', 'IEX', 'TSX', 'TSXV']
        for exchange in us_exchanges:
            assert exchange_manager.is_extended_hours_supported(exchange)
        
        # Most Asian exchanges don't have extended hours in our config
        asian_exchanges = ['TWSE', 'BSE', 'NSE', 'SET', 'IDX', 'KLSE']
        for exchange in asian_exchanges:
            assert not exchange_manager.is_extended_hours_supported(exchange)
    
    def test_continuous_trading_exchanges(self):
        """Test exchanges with continuous trading."""
        continuous_exchanges = ['GETTEX', 'TRADEGATE', 'IDEALPRO']
        
        for exchange in continuous_exchanges:
            exchange_info = EXCHANGE_INFO[exchange]
            assert exchange_info.get('continuous_trading') == True
    
    def test_total_exchange_count(self):
        """Test that we now have a comprehensive list of exchanges."""
        supported = exchange_manager.get_supported_exchanges()
        
        # Should have significantly more exchanges now
        assert len(supported) >= 45, f"Expected at least 45 exchanges, got {len(supported)}"
        
        # Major regions should be represented
        us_count = len([ex for ex in supported if exchange_manager.get_exchange_info(ex)['country'] == 'United States'])
        assert us_count >= 5, "Should have multiple US exchanges"
        
        asian_count = len([ex for ex in supported if exchange_manager.get_exchange_info(ex)['country'] in 
                          ['Japan', 'China', 'India', 'Singapore', 'Taiwan', 'Thailand', 'Indonesia', 'Malaysia']])
        assert asian_count >= 10, "Should have substantial Asian coverage"
    
    def test_market_status_all_exchanges(self):
        """Test that market status works for all exchanges."""
        status = exchange_manager.get_market_status_summary()
        
        # All new exchanges should be in the status summary
        new_major_exchanges = ['NYSE', 'NASDAQ', 'TSX', 'B3', 'TWSE', 'SSE', 'BSE', 'NSE', 'SGX', 'TASE', 'JSE']
        
        for exchange in new_major_exchanges:
            assert exchange in status, f"Exchange {exchange} not in market status summary"
            assert isinstance(status[exchange], bool), f"Market status for {exchange} should be boolean"


if __name__ == "__main__":
    pytest.main([__file__])
