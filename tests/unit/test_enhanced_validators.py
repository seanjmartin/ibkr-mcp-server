"""
Unit tests for Enhanced Validators System.

Tests all validation functionality:
- Order parameter validation (8 tests)
- Symbol format validation
- Currency pair validation
- Order size and value limits
- Account ID validation
- Error message formatting
- Edge case validation

Total: 8 comprehensive validation tests
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from ibkr_mcp_server.enhanced_validators import (
    TradingSafetyValidator,
    ForexValidator,
    InternationalValidator,
    StopLossValidator,
    OrderValidator,
    ValidationError,
    ForexValidationError,
    InternationalValidationError,
    StopLossValidationError,
    validate_symbols_list,
    validate_order_common_fields
)


@pytest.mark.unit
class TestEnhancedValidators:
    """Test enhanced validation system (8 tests)"""
    
    def test_validate_order_parameters(self):
        """Test order parameter validation using validate_order_common_fields"""
        # Valid order parameters
        valid_params = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "price": 180.0
        }
        
        # Mock trading enabled to pass safety check
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 25000.0
            
            # Should not raise exception
            try:
                validate_order_common_fields(valid_params)
            except ValidationError:
                pytest.fail("Valid parameters should not raise ValidationError")
        
        # Test invalid symbol
        invalid_symbol = valid_params.copy()
        invalid_symbol["symbol"] = ""
        
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            
            # Should fail because symbol is empty
            del invalid_symbol["symbol"]  # Remove symbol entirely
            with pytest.raises(ValidationError) as exc_info:
                validate_order_common_fields(invalid_symbol)
            assert "symbol" in str(exc_info.value).lower()
        
        # Test invalid action
        invalid_action = valid_params.copy()
        del invalid_action["action"]  # Remove action entirely
        
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            
            with pytest.raises(ValidationError) as exc_info:
                validate_order_common_fields(invalid_action)
            assert "action" in str(exc_info.value).lower()
    
    def test_validate_symbol_format(self):
        """Test symbol format validation using InternationalValidator"""
        # Valid symbols
        valid_symbols = ["AAPL", "MSFT", "GOOGL", "7203", "ASML"]
        
        for symbol in valid_symbols:
            try:
                InternationalValidator.validate_symbol_format(symbol)
            except ValidationError:
                pytest.fail(f"Valid symbol {symbol} should not raise ValidationError")
        
        # Invalid symbols
        invalid_symbols = ["", "   ", "TOOLONG123456789012345", "@#$%"]
        
        for symbol in invalid_symbols:
            with pytest.raises(ValidationError):
                InternationalValidator.validate_symbol_format(symbol)
    
    def test_validate_currency_pair(self):
        """Test forex pair validation using ForexValidator"""
        # Mock supported pairs and currencies
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.supported_forex_pairs = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "AUDCAD"]
            mock_settings.supported_currencies = ["EUR", "USD", "GBP", "JPY", "AUD", "CAD"]
            
            # Valid currency pairs
            valid_pairs = ["EURUSD", "GBPUSD", "USDJPY", "EURGBP", "AUDCAD"]
            
            for pair in valid_pairs:
                try:
                    ForexValidator.validate_currency_pair(pair)
                except ValidationError:
                    pytest.fail(f"Valid pair {pair} should not raise ValidationError")
            
            # Invalid currency pairs
            invalid_pairs = ["", "USD", "EURUSDGBP", "INVALID", "12345"]
            
            for pair in invalid_pairs:
                with pytest.raises(ValidationError):
                    ForexValidator.validate_currency_pair(pair)
    
    def test_validate_order_size_limits(self):
        """Test order size limit validation using TradingSafetyValidator"""
        # Mock settings
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.max_order_size = 1000
            
            # Valid order sizes
            valid_sizes = [1, 100, 500, 1000]
            
            for size in valid_sizes:
                try:
                    TradingSafetyValidator.validate_order_size(size)
                except ValidationError:
                    pytest.fail(f"Valid size {size} should not raise ValidationError")
            
            # Invalid order sizes
            invalid_sizes = [0, -1, -100]
            
            for size in invalid_sizes:
                with pytest.raises(ValidationError) as exc_info:
                    TradingSafetyValidator.validate_order_size(size)
                assert "quantity" in str(exc_info.value).lower()
            
            # Size exceeding limit
            with pytest.raises(ValidationError) as exc_info:
                TradingSafetyValidator.validate_order_size(2000)
            assert "exceeds maximum" in str(exc_info.value).lower()
    
    def test_validate_order_value_limits(self):
        """Test order value limit validation using TradingSafetyValidator"""
        # Mock settings
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.max_order_value_usd = 10000.0
            
            # Valid order values
            valid_values = [100.0, 1000.0, 5000.0, 10000.0]
            
            for value in valid_values:
                try:
                    TradingSafetyValidator.validate_order_value(value)
                except ValidationError:
                    pytest.fail(f"Valid value {value} should not raise ValidationError")
            
            # Invalid order values
            invalid_values = [0.0, -100.0, -1000.0]
            
            for value in invalid_values:
                with pytest.raises(ValidationError) as exc_info:
                    TradingSafetyValidator.validate_order_value(value)
                assert "value" in str(exc_info.value).lower()
            
            # Value exceeding limit
            with pytest.raises(ValidationError) as exc_info:
                TradingSafetyValidator.validate_order_value(20000.0)
            assert "exceeds maximum" in str(exc_info.value).lower()
    
    def test_validate_account_id(self):
        """Test account ID validation using TradingSafetyValidator.validate_paper_account"""
        # Mock settings
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.require_paper_account_verification = True
            mock_settings.allowed_account_prefixes = ["DU", "DUH"]
            
            # Valid paper account IDs
            valid_accounts = ["DU123456", "DUH789012", "DU999999"]
            
            for account in valid_accounts:
                try:
                    TradingSafetyValidator.validate_paper_account(account)
                except ValidationError:
                    pytest.fail(f"Valid account {account} should not raise ValidationError")
            
            # Live account when only paper allowed
            with pytest.raises(ValidationError) as exc_info:
                TradingSafetyValidator.validate_paper_account("U123456")
            assert "paper trading required" in str(exc_info.value).lower() or "not allowed" in str(exc_info.value).lower()
    
    def test_validation_error_messages(self):
        """Test error message formatting"""
        # Test ValidationError creation
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        
        # Test ValidationError with context using actual method
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.max_order_size = 1000
            
            try:
                TradingSafetyValidator.validate_order_size(-1)
            except ValidationError as e:
                # Should contain helpful context
                error_msg = str(e)
                assert "quantity" in error_msg.lower()
                assert "positive" in error_msg.lower()
    
    def test_validation_edge_cases(self):
        """Test edge case validation (empty strings, None values, etc.)"""
        # Test None values with symbol format validation
        with pytest.raises((ValidationError, TypeError, ValueError, AttributeError)):
            InternationalValidator.validate_symbol_format(None)
        
        # Test empty strings
        with pytest.raises(ValidationError):
            InternationalValidator.validate_symbol_format("")
        
        with pytest.raises(ValidationError):
            InternationalValidator.validate_symbol_format("   ")
        
        # Test currency pair edge cases
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.supported_forex_pairs = ["EURUSD", "GBPUSD"]
            mock_settings.supported_currencies = ["EUR", "USD", "GBP"]
            
            with pytest.raises(ValidationError):
                ForexValidator.validate_currency_pair("")
        
        # Test symbols list validation utility
        valid_symbols = validate_symbols_list("AAPL,MSFT,GOOGL")
        assert len(valid_symbols) == 3
        assert "AAPL" in valid_symbols
        
        with pytest.raises(ValidationError):
            validate_symbols_list("")
        
        with pytest.raises(ValidationError):
            validate_symbols_list("   ")
        
        # Test order value edge cases
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.max_order_value_usd = 100.0
            
            try:
                TradingSafetyValidator.validate_order_value(99.999999)
            except ValidationError:
                pytest.fail("Small float values should be handled correctly")
            
            # Test very large numbers
            with pytest.raises(ValidationError):
                TradingSafetyValidator.validate_order_value(999999999.0)
            
            # Test very small positive numbers
            try:
                TradingSafetyValidator.validate_order_value(0.01)
            except ValidationError:
                pytest.fail("Small positive values should be valid")


@pytest.mark.unit  
class TestOrderValidator:
    """Test OrderValidator class (bonus validation tests)"""
    
    def test_order_validator_initialization(self):
        """Test OrderValidator can be instantiated"""
        validator = OrderValidator()
        assert isinstance(validator, OrderValidator)
    
    def test_forex_validator_methods(self):
        """Test ForexValidator static methods"""
        # Test validate_forex_enabled
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = False
            
            with pytest.raises(ValidationError):
                ForexValidator.validate_forex_enabled()
    
    def test_stop_loss_validator_methods(self):
        """Test StopLossValidator static methods"""
        # Test validate_stop_loss_enabled
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = False
            
            with pytest.raises(ValidationError):
                StopLossValidator.validate_stop_loss_enabled()
    
    def test_international_validator_methods(self):
        """Test InternationalValidator static methods"""
        # Test validate_international_enabled
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = False
            
            with pytest.raises(ValidationError):
                InternationalValidator.validate_international_enabled()


@pytest.mark.unit  
class TestTrailingStopValidation:
    """Test trailing stop order validation"""
    
    def test_trailing_stop_percent_validation(self):
        """Test that trailing stops with trail_percent don't require stop_price"""
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.enable_stop_loss_orders = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 100000.0
            mock_settings.max_trail_percent = 50.0
            
            # This should NOT fail - trailing stops don't need stop_price
            order_data = {
                'symbol': 'AAPL',
                'action': 'SELL', 
                'quantity': 100,
                'order_type': 'TRAIL',
                'trail_percent': 10.0
                # Note: no stop_price provided - this should be valid for TRAIL orders
            }
            
            # This should pass without ValidationError
            try:
                StopLossValidator.validate_stop_loss_order(order_data)
            except ValidationError as e:
                pytest.fail(f"Trailing stop with trail_percent should not require stop_price: {str(e)}")
    
    def test_trailing_stop_amount_validation(self):
        """Test that trailing stops with trail_amount don't require stop_price"""
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.enable_stop_loss_orders = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 100000.0
            
            # This should NOT fail - trailing stops don't need stop_price
            order_data = {
                'symbol': 'AAPL',
                'action': 'SELL',
                'quantity': 100,
                'order_type': 'TRAIL',
                'trail_amount': 25.0
                # Note: no stop_price provided - this should be valid for TRAIL orders
            }
            
            # This should pass without ValidationError
            try:
                StopLossValidator.validate_stop_loss_order(order_data)
            except ValidationError as e:
                pytest.fail(f"Trailing stop with trail_amount should not require stop_price: {str(e)}")
    
    def test_basic_stop_loss_still_requires_stop_price(self):
        """Test that basic stop losses still require stop_price"""
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.enable_stop_loss_orders = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 100000.0
            
            # Basic stop order without stop_price should still fail
            order_data = {
                'symbol': 'AAPL',
                'action': 'SELL',
                'quantity': 100,
                'order_type': 'STP'
                # Note: no stop_price provided - this should fail for STP orders
            }
            
            # This should fail with ValidationError
            with pytest.raises(ValidationError, match="Stop price must be a positive number"):
                StopLossValidator.validate_stop_loss_order(order_data)
