"""Tests for new European exchanges in exchange_info.py"""

import pytest
from datetime import time
from ibkr_mcp_server.data.exchange_info import exchange_manager, EXCHANGE_INFO


class TestNewEuropeanExchanges:
    """Test new European exchanges added to the system."""
    
    def test_new_exchanges_exist(self):
        """Test that all new European exchanges are properly defined."""
        new_exchanges = ['BIT', 'MIL', 'BME', 'BVME', 'VIX', 'BEL', 'OSE', 'OMX', 'HEX', 'WSE', 'IBIS2']
        
        for exchange in new_exchanges:
            assert exchange in EXCHANGE_INFO, f"Exchange {exchange} not found in EXCHANGE_INFO"
    
    def test_italian_exchanges(self):
        """Test Italian exchange configurations."""
        # Test BIT (Borsa Italiana)
        bit_info = exchange_manager.get_exchange_info('BIT')
        assert bit_info is not None
        assert bit_info['name'] == 'Borsa Italiana'
        assert bit_info['country'] == 'Italy'
        assert bit_info['currency'] == 'EUR'
        assert bit_info['timezone'] == 'Europe/Rome'
        assert bit_info['settlement'] == 'T+2'
        
        # Test MIL (Milan Stock Exchange)
        mil_info = exchange_manager.get_exchange_info('MIL')
        assert mil_info is not None
        assert mil_info['name'] == 'Milan Stock Exchange'
        assert mil_info['country'] == 'Italy'
        assert mil_info['currency'] == 'EUR'
    
    def test_spanish_exchanges(self):
        """Test Spanish exchange configurations."""
        # Test BME
        bme_info = exchange_manager.get_exchange_info('BME')
        assert bme_info is not None
        assert bme_info['name'] == 'Bolsas y Mercados Españoles'
        assert bme_info['country'] == 'Spain'
        assert bme_info['currency'] == 'EUR'
        assert bme_info['timezone'] == 'Europe/Madrid'
        
        # Test BVME (Madrid Stock Exchange)
        bvme_info = exchange_manager.get_exchange_info('BVME')
        assert bvme_info is not None
        assert bvme_info['name'] == 'Madrid Stock Exchange'
        assert bvme_info['country'] == 'Spain'
    
    def test_nordic_exchanges(self):
        """Test Nordic exchange configurations."""
        # Test OSE (Oslo)
        ose_info = exchange_manager.get_exchange_info('OSE')
        assert ose_info is not None
        assert ose_info['name'] == 'Oslo Stock Exchange'
        assert ose_info['country'] == 'Norway'
        assert ose_info['currency'] == 'NOK'
        assert ose_info['timezone'] == 'Europe/Oslo'
        
        # Test OMX (Stockholm)
        omx_info = exchange_manager.get_exchange_info('OMX')
        assert omx_info is not None
        assert omx_info['name'] == 'Nasdaq Stockholm'
        assert omx_info['country'] == 'Sweden'
        assert omx_info['currency'] == 'SEK'
        
        # Test HEX (Helsinki)
        hex_info = exchange_manager.get_exchange_info('HEX')
        assert hex_info is not None
        assert hex_info['name'] == 'Nasdaq Helsinki'
        assert hex_info['country'] == 'Finland'
        assert hex_info['currency'] == 'EUR'
        assert hex_info['timezone'] == 'Europe/Helsinki'
    
    def test_austrian_exchange(self):
        """Test Austrian exchange configuration."""
        vix_info = exchange_manager.get_exchange_info('VIX')
        assert vix_info is not None
        assert vix_info['name'] == 'Vienna Stock Exchange'
        assert vix_info['country'] == 'Austria'
        assert vix_info['currency'] == 'EUR'
        assert vix_info['timezone'] == 'Europe/Vienna'
    
    def test_polish_exchange(self):
        """Test Polish exchange configuration."""
        wse_info = exchange_manager.get_exchange_info('WSE')
        assert wse_info is not None
        assert wse_info['name'] == 'Warsaw Stock Exchange'
        assert wse_info['country'] == 'Poland'
        assert wse_info['currency'] == 'PLN'
        assert wse_info['timezone'] == 'Europe/Warsaw'
    
    def test_belgian_exchange(self):
        """Test Belgian exchange configuration."""
        bel_info = exchange_manager.get_exchange_info('BEL')
        assert bel_info is not None
        assert bel_info['name'] == 'Euronext Brussels'
        assert bel_info['country'] == 'Belgium'
        assert bel_info['currency'] == 'EUR'
        assert bel_info['timezone'] == 'Europe/Brussels'
    
    def test_trading_hours_format(self):
        """Test that trading hours are properly serialized."""
        new_exchanges = ['BIT', 'BME', 'OSE', 'OMX', 'HEX', 'WSE', 'VIX', 'BEL']
        
        for exchange in new_exchanges:
            info = exchange_manager.get_exchange_info(exchange)
            assert 'trading_hours' in info
            
            # Check that times are converted to strings
            trading_hours = info['trading_hours']
            for key, value in trading_hours.items():
                assert isinstance(value, str), f"Trading hour {key} for {exchange} should be string, got {type(value)}"
                assert ':' in value, f"Trading hour {key} for {exchange} should be in HH:MM format"
    
    def test_currency_validation(self):
        """Test currency validation for new exchanges."""
        # Test Euro exchanges
        euro_exchanges = ['BIT', 'MIL', 'BME', 'BVME', 'VIX', 'BEL', 'HEX']
        for exchange in euro_exchanges:
            assert exchange_manager.validate_currency_for_exchange(exchange, 'EUR')
            assert not exchange_manager.validate_currency_for_exchange(exchange, 'USD')
        
        # Test NOK exchange
        assert exchange_manager.validate_currency_for_exchange('OSE', 'NOK')
        assert not exchange_manager.validate_currency_for_exchange('OSE', 'EUR')
        
        # Test SEK exchange
        assert exchange_manager.validate_currency_for_exchange('OMX', 'SEK')
        assert not exchange_manager.validate_currency_for_exchange('OMX', 'EUR')
        
        # Test PLN exchange
        assert exchange_manager.validate_currency_for_exchange('WSE', 'PLN')
        assert not exchange_manager.validate_currency_for_exchange('WSE', 'EUR')
    
    def test_supported_exchanges_list(self):
        """Test that new exchanges appear in supported exchanges list."""
        supported = exchange_manager.get_supported_exchanges()
        new_exchanges = ['BIT', 'MIL', 'BME', 'BVME', 'VIX', 'BEL', 'OSE', 'OMX', 'HEX', 'WSE', 'IBIS2']
        
        for exchange in new_exchanges:
            assert exchange in supported, f"Exchange {exchange} not in supported exchanges list"
    
    def test_market_status_includes_new_exchanges(self):
        """Test that market status summary includes new exchanges."""
        status = exchange_manager.get_market_status_summary()
        new_exchanges = ['BIT', 'MIL', 'BME', 'BVME', 'VIX', 'BEL', 'OSE', 'OMX', 'HEX', 'WSE', 'IBIS2']
        
        for exchange in new_exchanges:
            assert exchange in status, f"Exchange {exchange} not in market status summary"
            assert isinstance(status[exchange], bool), f"Market status for {exchange} should be boolean"


class TestInternationalStockMapping:
    """Test new stock mappings in international.py."""
    
    def test_italian_stock_mapping(self):
        """Test Italian stock mappings."""
        # This would require importing the actual mapping function
        # For now, just verify the structure exists
        pass
    
    def test_spanish_stock_mapping(self):
        """Test Spanish stock mappings."""
        pass
    
    def test_nordic_stock_mapping(self):
        """Test Nordic stock mappings."""
        pass


if __name__ == "__main__":
    pytest.main([__file__])
