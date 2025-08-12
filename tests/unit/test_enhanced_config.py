"""
Unit tests for Enhanced Configuration System.

Tests all configuration functionality:
- Enhanced settings initialization (8 tests)
- Environment variable overrides  
- Settings validation
- Safety defaults
- Trading enablement validation
- IBKR connection settings
- Order limits validation
- Paper account settings

Total: 8 comprehensive configuration tests
"""
import pytest
import os
from unittest.mock import patch, Mock

from ibkr_mcp_server.enhanced_config import EnhancedSettings


@pytest.mark.unit
class TestEnhancedConfig:
    """Test enhanced configuration system (8 tests)"""
    
    def test_enhanced_settings_initialization(self):
        """Test default settings load correctly"""
        settings = EnhancedSettings()
        
        # Test basic initialization
        assert hasattr(settings, 'ibkr_host')
        assert hasattr(settings, 'ibkr_port')
        assert hasattr(settings, 'ibkr_client_id')
        assert hasattr(settings, 'ibkr_is_paper')
        
        # Test actual configuration (with .env file overrides)
        # NOTE: .env file has IBKR_ENABLE_TRADING=true for paper trading
        assert settings.enable_trading is True  # Enabled via .env for paper trading
        assert settings.enable_forex_trading is True  # Enabled via .env for paper trading
        assert settings.enable_international_trading is True  # Enabled via .env for paper trading  
        assert settings.enable_stop_loss_orders is True  # Enabled via .env for paper trading
    
    def test_enhanced_settings_environment_override(self):
        """Test environment variable overrides"""
        # Mock environment variables (note: EnhancedSettings uses IBKR_ prefix)
        env_vars = {
            'IBKR_IBKR_HOST': '192.168.1.100',
            'IBKR_IBKR_PORT': '7496', 
            'IBKR_IBKR_CLIENT_ID': '10',
            'IBKR_ENABLE_TRADING': 'true',
            'IBKR_ENABLE_FOREX_TRADING': 'true'
        }
        
        with patch.dict(os.environ, env_vars):
            settings = EnhancedSettings()
            
            assert settings.ibkr_host == '192.168.1.100'
            assert settings.ibkr_port == 7496
            assert settings.ibkr_client_id == 10
            assert settings.enable_trading is True
            assert settings.enable_forex_trading is True
    
    def test_enhanced_settings_validation(self):
        """Test settings validation"""
        settings = EnhancedSettings()
        
        # Test valid port range
        assert 1 <= settings.ibkr_port <= 65535
        
        # Test valid client ID
        assert settings.ibkr_client_id >= 0
        
        # Test host format
        assert isinstance(settings.ibkr_host, str)
        assert len(settings.ibkr_host) > 0
    
    def test_enhanced_settings_safety_defaults(self):
        """Test safety settings default to False"""
        # Clear all IBKR-related environment variables to test actual defaults
        # We need to actually remove them from the environment, not set to empty string
        env_vars_to_remove = [
            'IBKR_ENABLE_TRADING',
            'IBKR_ENABLE_FOREX_TRADING', 
            'IBKR_ENABLE_INTERNATIONAL_TRADING',
            'IBKR_ENABLE_STOP_LOSS_ORDERS',
            'IBKR_REQUIRE_PAPER_ACCOUNT_VERIFICATION'
        ]
        
        # Save existing values to restore later
        saved_env = {}
        for var in env_vars_to_remove:
            if var in os.environ:
                saved_env[var] = os.environ[var]
                del os.environ[var]
        
        try:
            # Create settings with no environment overrides
            settings = EnhancedSettings(
                _env_file=None,  # Don't load .env file
            )
            
            # All trading features should be disabled by default
            assert settings.enable_trading is False
            assert settings.enable_forex_trading is False
            assert settings.enable_international_trading is False
            assert settings.enable_stop_loss_orders is False
            
            # Paper account verification should be enabled by default
            assert settings.require_paper_account_verification is True
            
        finally:
            # Restore original environment variables
            for var, value in saved_env.items():
                os.environ[var] = value
    
    def test_enhanced_settings_trading_enabled_validation(self):
        """Test trading enablement validation"""
        # Test explicit enablement - use correct IBKR_ prefix and no .env file
        with patch.dict(os.environ, {'IBKR_ENABLE_TRADING': 'true'}):
            settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert settings.enable_trading is True
        
        # Test explicit disablement
        with patch.dict(os.environ, {'IBKR_ENABLE_TRADING': 'false'}):
            settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert settings.enable_trading is False
        
        # Test case insensitivity
        with patch.dict(os.environ, {'IBKR_ENABLE_TRADING': 'TRUE'}):
            settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert settings.enable_trading is True
    
    def test_enhanced_settings_ibkr_connection_settings(self):
        """Test IBKR connection configuration"""
        settings = EnhancedSettings()
        
        # Test default paper trading settings
        assert settings.ibkr_port == 7497  # Paper trading port
        assert settings.ibkr_is_paper is True
        assert settings.ibkr_host == "127.0.0.1"
        
        # Test live trading override - use correct IBKR_ prefix
        env_vars = {
            'IBKR_IBKR_PORT': '7496',
            'IBKR_IBKR_IS_PAPER': 'false'
        }
        
        with patch.dict(os.environ, env_vars):
            live_settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert live_settings.ibkr_port == 7496  # Live trading port
            assert live_settings.ibkr_is_paper is False
    
    def test_enhanced_settings_limits_validation(self):
        """Test order/value limit validation"""
        settings = EnhancedSettings()
        
        # Test default limits
        assert settings.max_order_size > 0
        assert settings.max_order_value_usd > 0
        assert settings.max_daily_orders > 0
        
        # Test environment overrides - use correct IBKR_ prefix
        env_vars = {
            'IBKR_MAX_ORDER_SIZE': '500',
            'IBKR_MAX_ORDER_VALUE_USD': '5000.0',
            'IBKR_MAX_DAILY_ORDERS': '25'
        }
        
        with patch.dict(os.environ, env_vars):
            custom_settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert custom_settings.max_order_size == 500
            assert custom_settings.max_order_value_usd == 5000.0
            assert custom_settings.max_daily_orders == 25
    
    def test_enhanced_settings_paper_account_settings(self):
        """Test paper account configuration"""
        settings = EnhancedSettings()
        
        # Test default paper account settings
        assert settings.require_paper_account_verification is True
        assert "DU" in settings.allowed_account_prefixes
        assert "DUH" in settings.allowed_account_prefixes
        
        # Test paper account requirement can be disabled - use correct IBKR_ prefix
        with patch.dict(os.environ, {'IBKR_REQUIRE_PAPER_ACCOUNT_VERIFICATION': 'false'}):
            live_settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert live_settings.require_paper_account_verification is False
        
        # Test custom account prefixes - use correct IBKR_ prefix and JSON format for list
        with patch.dict(os.environ, {'IBKR_ALLOWED_ACCOUNT_PREFIXES': '["TEST", "DEMO"]'}):
            custom_settings = EnhancedSettings(_env_file=None)  # Skip .env file
            assert "TEST" in custom_settings.allowed_account_prefixes
            assert "DEMO" in custom_settings.allowed_account_prefixes
