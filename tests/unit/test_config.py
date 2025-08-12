"""
Unit tests for Basic Configuration System.

Tests basic config module functionality:
- Module imports and basic functionality (4 tests)
- Default configuration values
- Environment variable integration
- Backwards compatibility with enhanced_config

Total: 4 comprehensive configuration tests
"""
import pytest
import os
from unittest.mock import patch, MagicMock

from ibkr_mcp_server.config import Settings, settings


@pytest.mark.unit
class TestBasicConfiguration:
    """Test basic configuration system (4 tests)"""
    
    def test_config_module_imports(self):
        """Test basic config module functionality"""
        # Test that all required components can be imported
        from ibkr_mcp_server.config import Settings, settings
        
        # Test Settings class exists and can be instantiated
        assert Settings is not None
        test_settings = Settings()
        assert isinstance(test_settings, Settings)
        
        # Test global settings instance exists
        assert settings is not None
        assert isinstance(settings, Settings)
        
        # Test that Settings inherits from BaseSettings
        from pydantic_settings import BaseSettings
        assert issubclass(Settings, BaseSettings)
        
        # Test key methods exist
        assert hasattr(Settings, 'parse_managed_accounts')
        assert hasattr(Settings, 'validate_log_level')
        
        # Test model configuration exists
        assert hasattr(Settings, 'model_config')
        assert isinstance(Settings.model_config, dict)
        assert 'env_file' in Settings.model_config
        assert Settings.model_config['env_file'] == '.env'
    
    def test_config_default_values(self):
        """Test default configuration values"""
        # Create Settings without environment file loading to test true defaults
        with patch.object(Settings, 'model_config', {'env_file': None, 'env_file_encoding': 'utf-8', 'case_sensitive': False, 'extra': 'ignore'}):
            test_settings = Settings()
            
            # Test IBKR Connection defaults
            assert test_settings.ibkr_host == "127.0.0.1"
            assert test_settings.ibkr_port == 7497
            assert test_settings.ibkr_client_id == 1
            assert test_settings.ibkr_is_paper is True
            
            # Test Account Management defaults
            assert test_settings.ibkr_default_account is None
            assert test_settings.ibkr_managed_accounts is None
            
            # Test Logging defaults
            assert test_settings.log_level == "INFO"
            assert test_settings.log_file == "C:/temp/ibkr-mcp-server.log"
            
            # Test Reconnection defaults
            assert test_settings.max_reconnect_attempts == 5
            assert test_settings.reconnect_delay == 5
            
            # Test Market Data defaults
            assert test_settings.ibkr_market_data_type == 3  # Delayed
            
            # Test Trading Safety defaults
            assert test_settings.enable_live_trading is False
            assert test_settings.max_order_size == 1000
            assert test_settings.require_order_confirmation is True
            
            # Test MCP Server defaults
            assert test_settings.mcp_server_name == "ibkr-mcp"
            assert test_settings.mcp_server_version == "1.0.0"
    
    def test_config_environment_integration(self):
        """Test environment variable integration"""
        # Test environment variable override for string values
        with patch.dict(os.environ, {'IBKR_HOST': '192.168.1.100'}):
            test_settings = Settings()
            assert test_settings.ibkr_host == '192.168.1.100'
        
        # Test environment variable override for integer values
        with patch.dict(os.environ, {'IBKR_PORT': '7496'}):
            test_settings = Settings()
            assert test_settings.ibkr_port == 7496
        
        # Test environment variable override for boolean values
        with patch.dict(os.environ, {'IBKR_IS_PAPER': 'false'}):
            test_settings = Settings()
            assert test_settings.ibkr_is_paper is False
        
        # Test environment variable override for log level (with validation)
        with patch.dict(os.environ, {'LOG_LEVEL': 'debug'}):
            test_settings = Settings()
            assert test_settings.log_level == 'DEBUG'  # Should be uppercased
        
        # Test case insensitive environment variables (Pydantic feature)
        with patch.dict(os.environ, {'log_level': 'warning'}):
            test_settings = Settings()
            assert test_settings.log_level == 'WARNING'
        
        # Test managed accounts parsing from environment
        with patch.dict(os.environ, {'IBKR_MANAGED_ACCOUNTS': 'DU123456, DU789012, DU345678'}):
            test_settings = Settings()
            expected_accounts = ['DU123456', 'DU789012', 'DU345678']
            assert test_settings.ibkr_managed_accounts == expected_accounts
    
    def test_config_backwards_compatibility(self):
        """Test compatibility with enhanced_config"""
        # Test that basic config provides the essential fields that enhanced_config might depend on
        test_settings = Settings()
        
        # Essential IBKR connection fields that enhanced_config would need
        essential_ibkr_fields = ['ibkr_host', 'ibkr_port', 'ibkr_client_id', 'ibkr_is_paper']
        for field in essential_ibkr_fields:
            assert hasattr(test_settings, field), f"Missing essential IBKR field: {field}"
        
        # Essential logging fields
        essential_logging_fields = ['log_level', 'log_file']
        for field in essential_logging_fields:
            assert hasattr(test_settings, field), f"Missing essential logging field: {field}"
        
        # Essential safety fields
        essential_safety_fields = ['enable_live_trading', 'max_order_size']
        for field in essential_safety_fields:
            assert hasattr(test_settings, field), f"Missing essential safety field: {field}"
        
        # Test that global settings instance is accessible
        from ibkr_mcp_server.config import settings as global_settings
        assert global_settings is not None
        assert isinstance(global_settings, Settings)
        
        # Test that the settings can be imported in a way that enhanced_config might use
        try:
            from ibkr_mcp_server.config import Settings as ConfigSettings
            from ibkr_mcp_server.config import settings as config_settings
            assert ConfigSettings is not None
            assert config_settings is not None
        except ImportError:
            pytest.fail("Basic config should be importable in backwards-compatible way")


@pytest.mark.unit
class TestConfigValidators:
    """Test config validation methods"""
    
    def test_parse_managed_accounts_validator(self):
        """Test managed accounts parsing validator"""
        # Test with valid comma-separated accounts
        test_settings = Settings(ibkr_managed_accounts="DU123456, DU789012, DU345678")
        expected = ['DU123456', 'DU789012', 'DU345678']
        assert test_settings.ibkr_managed_accounts == expected
        
        # Test with extra whitespace
        test_settings = Settings(ibkr_managed_accounts="  DU123456  ,   DU789012  ,  DU345678  ")
        assert test_settings.ibkr_managed_accounts == expected
        
        # Test with empty string
        test_settings = Settings(ibkr_managed_accounts="")
        assert test_settings.ibkr_managed_accounts is None
        
        # Test with None (default)
        test_settings = Settings()
        assert test_settings.ibkr_managed_accounts is None
    
    def test_validate_log_level_validator(self):
        """Test log level validation"""
        # Test valid log levels (case insensitive)
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in valid_levels:
            test_settings = Settings(log_level=level)
            assert test_settings.log_level == level.upper()
            
            # Test lowercase versions
            test_settings = Settings(log_level=level.lower())
            assert test_settings.log_level == level.upper()
        
        # Test invalid log level
        with pytest.raises(ValueError, match="Log level must be one of"):
            Settings(log_level="INVALID")
        
        # Test empty string
        with pytest.raises(ValueError):
            Settings(log_level="")
        
        # Test mixed case
        test_settings = Settings(log_level="dEbUg")
        assert test_settings.log_level == "DEBUG"
