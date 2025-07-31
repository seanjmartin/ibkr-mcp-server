"""Enhanced validation framework for IBKR MCP Server trading operations."""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from decimal import Decimal

from .enhanced_config import enhanced_settings


# ========================================
# BASE VALIDATOR CLASS
# ========================================

class BaseValidator:
    """Base class for all validators with common utility methods."""
    
    @staticmethod
    def validate_positive_number(value: float, name: str) -> None:
        """Validate that a number is positive."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValidationError(f"{name} must be a positive number, got {value}")
    
    @staticmethod
    def validate_non_negative_number(value: float, name: str) -> None:
        """Validate that a number is non-negative."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValidationError(f"{name} must be non-negative, got {value}")
    
    @staticmethod
    def validate_string_not_empty(value: str, name: str) -> None:
        """Validate that a string is not empty."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{name} cannot be empty")
    
    @staticmethod
    def validate_choice(value: str, choices: List[str], name: str) -> None:
        """Validate that a value is in allowed choices."""
        if value not in choices:
            raise ValidationError(f"{name} must be one of {choices}, got {value}")


# ========================================
# TRADING SAFETY VALIDATORS
# ========================================

class TradingSafetyValidator(BaseValidator):
    """Core trading safety validation."""
    
    @staticmethod
    def validate_trading_enabled() -> None:
        """Validate that trading is enabled."""
        if not enhanced_settings.enable_trading:
            raise TradingDisabledError("Trading is disabled in configuration. Enable with enable_trading=True")
    
    @staticmethod
    def validate_paper_account(account_id: str) -> None:
        """Validate account is paper trading if required."""
        if enhanced_settings.require_paper_account_verification:
            if not any(account_id.startswith(prefix) for prefix in enhanced_settings.allowed_account_prefixes):
                raise SafetyViolationError(
                    f"Live trading account detected: {account_id}. "
                    f"Paper trading required. Expected prefixes: {enhanced_settings.allowed_account_prefixes}"
                )
    
    @staticmethod
    def validate_order_size(quantity: int) -> None:
        """Validate order size against limits."""
        TradingSafetyValidator.validate_positive_number(quantity, "Order quantity")
        
        if quantity > enhanced_settings.max_order_size:
            raise OrderSizeLimitError(
                f"Order size {quantity} exceeds maximum allowed {enhanced_settings.max_order_size}"
            )
    
    @staticmethod
    def validate_order_value(estimated_value: float) -> None:
        """Validate order value against limits."""
        TradingSafetyValidator.validate_positive_number(estimated_value, "Order value")
        
        if estimated_value > enhanced_settings.max_order_value_usd:
            raise OrderValueLimitError(
                f"Order value ${estimated_value:,.2f} exceeds maximum ${enhanced_settings.max_order_value_usd:,.2f}"
            )
    
    @staticmethod
    def validate_daily_order_limit(current_count: int) -> None:
        """Validate daily order count limit."""
        if current_count >= enhanced_settings.max_daily_orders:
            raise DailyLimitError(
                f"Daily order limit reached: {current_count}/{enhanced_settings.max_daily_orders}"
            )


# ========================================
# FOREX VALIDATORS
# ========================================

class ForexValidator(BaseValidator):
    """Forex trading validation."""
    
    @staticmethod
    def validate_forex_enabled() -> None:
        """Validate that forex trading is enabled."""
        TradingSafetyValidator.validate_trading_enabled()
        if not enhanced_settings.enable_forex_trading:
            raise ForexTradingDisabledError("Forex trading is disabled. Enable with enable_forex_trading=True")
    
    @staticmethod
    def validate_currency_pair(pair: str) -> None:
        """Validate forex currency pair format and availability."""
        ForexValidator.validate_string_not_empty(pair, "Currency pair")
        
        pair = pair.upper()
        
        # Check format
        if len(pair) != 6:
            raise ForexValidationError(f"Invalid forex pair format: {pair}. Must be 6 characters (e.g., EURUSD)")
        
        # Check if supported
        if pair not in enhanced_settings.supported_forex_pairs:
            raise ForexValidationError(
                f"Unsupported forex pair: {pair}. "
                f"Supported pairs: {', '.join(enhanced_settings.supported_forex_pairs)}"
            )
        
        # Validate currency codes
        base_currency = pair[:3]
        quote_currency = pair[3:]
        
        supported_currencies = enhanced_settings.supported_currencies
        if base_currency not in supported_currencies:
            raise ForexValidationError(f"Unsupported base currency: {base_currency}")
        
        if quote_currency not in supported_currencies:
            raise ForexValidationError(f"Unsupported quote currency: {quote_currency}")
    
    @staticmethod
    def validate_forex_order(order_data: Dict[str, Any]) -> None:
        """Validate forex order parameters."""
        # Basic validations
        pair = order_data.get('currency_pair', '')
        ForexValidator.validate_currency_pair(pair)
        
        action = order_data.get('action', '')
        ForexValidator.validate_choice(action, ['BUY', 'SELL'], "Action")
        
        quantity = order_data.get('quantity', 0)
        ForexValidator.validate_positive_number(quantity, "Quantity")
        
        # Forex minimum lot size
        if quantity < 1000:  # Minimum forex quantity
            raise ForexValidationError(f"Minimum forex quantity is 1000, got {quantity}")
        
        order_type = order_data.get('order_type', 'MKT')
        ForexValidator.validate_choice(order_type, ['MKT', 'LMT', 'STP', 'STP LMT'], "Order type")
        
        # Price validation for limit orders
        if order_type in ['LMT', 'STP LMT']:
            price = order_data.get('price')
            if price is None:
                raise ForexValidationError(f"Price required for {order_type} orders")
            ForexValidator.validate_positive_number(price, "Price")
        
        # Stop price validation
        if order_type in ['STP', 'STP LMT']:
            stop_price = order_data.get('stop_price')
            if stop_price is None:
                raise ForexValidationError(f"Stop price required for {order_type} orders")
            ForexValidator.validate_positive_number(stop_price, "Stop price")
    
    @staticmethod
    def validate_currency_conversion(amount: float, from_currency: str, to_currency: str) -> None:
        """Validate currency conversion parameters."""
        ForexValidator.validate_positive_number(amount, "Conversion amount")
        ForexValidator.validate_string_not_empty(from_currency, "From currency")
        ForexValidator.validate_string_not_empty(to_currency, "To currency")
        
        # Validate currency codes
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        supported = enhanced_settings.supported_currencies
        if from_curr not in supported:
            raise ForexValidationError(f"Unsupported from currency: {from_curr}")
        if to_curr not in supported:
            raise ForexValidationError(f"Unsupported to currency: {to_curr}")


# ========================================
# INTERNATIONAL TRADING VALIDATORS
# ========================================

class InternationalValidator(BaseValidator):
    """International trading validation."""
    
    @staticmethod
    def validate_international_enabled() -> None:
        """Validate that international trading is enabled."""
        TradingSafetyValidator.validate_trading_enabled()
        if not enhanced_settings.enable_international_trading:
            raise InternationalTradingDisabledError(
                "International trading is disabled. Enable with enable_international_trading=True"
            )
    
    @staticmethod
    def validate_symbol_format(symbol: str) -> None:
        """Validate international symbol format."""
        InternationalValidator.validate_string_not_empty(symbol, "Symbol")
        
        # Basic symbol format validation
        if not re.match(r'^[A-Z0-9.-]+$', symbol.upper()):
            raise InternationalValidationError(
                f"Invalid symbol format: {symbol}. Must contain only letters, numbers, dots, and hyphens"
            )
        
        # Check length
        if len(symbol) > 20:
            raise InternationalValidationError(f"Symbol too long: {symbol}. Maximum 20 characters")
    
    @staticmethod
    def validate_exchange_currency(exchange: str, currency: str) -> None:
        """Validate exchange and currency combination."""
        InternationalValidator.validate_string_not_empty(exchange, "Exchange")
        InternationalValidator.validate_string_not_empty(currency, "Currency")
        
        currency = currency.upper()
        if currency not in enhanced_settings.supported_currencies:
            raise InternationalValidationError(
                f"Unsupported currency: {currency}. "
                f"Supported: {', '.join(enhanced_settings.supported_currencies)}"
            )
        
        # Basic exchange format validation
        exchange = exchange.upper()
        if not re.match(r'^[A-Z]{2,10}$', exchange):
            raise InternationalValidationError(
                f"Invalid exchange format: {exchange}. Must be 2-10 uppercase letters"
            )
    
    @staticmethod
    def validate_international_order(order_data: Dict[str, Any]) -> None:
        """Validate international order parameters."""
        # Basic validations
        symbol = order_data.get('symbol', '')
        InternationalValidator.validate_symbol_format(symbol)
        
        exchange = order_data.get('exchange', 'SMART')
        currency = order_data.get('currency', 'USD')
        InternationalValidator.validate_exchange_currency(exchange, currency)
        
        action = order_data.get('action', '')
        InternationalValidator.validate_choice(action, ['BUY', 'SELL'], "Action")
        
        quantity = order_data.get('quantity', 0)
        InternationalValidator.validate_positive_number(quantity, "Quantity")
        
        order_type = order_data.get('order_type', 'MKT')
        InternationalValidator.validate_choice(
            order_type, ['MKT', 'LMT', 'STP', 'STP LMT'], "Order type"
        )
        
        # Price validations
        if order_type in ['LMT', 'STP LMT']:
            price = order_data.get('price')
            if price is None:
                raise InternationalValidationError(f"Price required for {order_type} orders")
            InternationalValidator.validate_positive_number(price, "Price")


# ========================================
# STOP LOSS VALIDATORS
# ========================================

class StopLossValidator(BaseValidator):
    """Stop loss order validation."""
    
    @staticmethod
    def validate_stop_loss_enabled() -> None:
        """Validate that stop loss orders are enabled."""
        TradingSafetyValidator.validate_trading_enabled()
        if not enhanced_settings.enable_stop_loss_orders:
            raise StopLossDisabledError(
                "Stop loss orders are disabled. Enable with enable_stop_loss_orders=True"
            )
    
    @staticmethod
    def validate_stop_loss_order(order_data: Dict[str, Any]) -> None:
        """Validate stop loss order parameters."""
        StopLossValidator.validate_stop_loss_enabled()
        
        # Basic validations
        symbol = order_data.get('symbol', '')
        StopLossValidator.validate_string_not_empty(symbol, "Symbol")
        
        action = order_data.get('action', '')
        StopLossValidator.validate_choice(action, ['BUY', 'SELL'], "Action")
        
        quantity = order_data.get('quantity', 0)
        StopLossValidator.validate_positive_number(quantity, "Quantity")
        
        stop_price = order_data.get('stop_price', 0)
        StopLossValidator.validate_positive_number(stop_price, "Stop price")
        
        order_type = order_data.get('order_type', 'STP')
        StopLossValidator.validate_choice(
            order_type, ['STP', 'STP LMT', 'TRAIL'], "Stop loss order type"
        )
        
        # Type-specific validation
        if order_type == 'STP LMT':
            limit_price = order_data.get('limit_price')
            if limit_price is not None:
                StopLossValidator.validate_positive_number(limit_price, "Limit price")
        
        elif order_type == 'TRAIL':
            trail_amount = order_data.get('trail_amount')
            trail_percent = order_data.get('trail_percent')
            
            if trail_amount is None and trail_percent is None:
                raise StopLossValidationError(
                    "Trailing stop requires either trail_amount or trail_percent"
                )
            
            if trail_amount is not None:
                StopLossValidator.validate_positive_number(trail_amount, "Trail amount")
            
            if trail_percent is not None:
                if not 0 < trail_percent <= enhanced_settings.max_trail_percent:
                    raise StopLossValidationError(
                        f"Trail percent must be between 0 and {enhanced_settings.max_trail_percent}, got {trail_percent}"
                    )
        
        # Time in force validation
        tif = order_data.get('time_in_force', 'GTC')
        StopLossValidator.validate_choice(tif, ['GTC', 'DAY', 'GTD'], "Time in force")
    
    @staticmethod
    def validate_bracket_order(order_data: Dict[str, Any]) -> None:
        """Validate bracket order parameters."""
        StopLossValidator.validate_stop_loss_enabled()
        
        if not enhanced_settings.enable_bracket_orders:
            raise StopLossValidationError("Bracket orders are disabled")
        
        # Basic validations
        symbol = order_data.get('symbol', '')
        StopLossValidator.validate_string_not_empty(symbol, "Symbol")
        
        action = order_data.get('action', '')
        StopLossValidator.validate_choice(action, ['BUY', 'SELL'], "Action")
        
        quantity = order_data.get('quantity', 0)
        StopLossValidator.validate_positive_number(quantity, "Quantity")
        
        take_profit_price = order_data.get('take_profit_price', 0)
        StopLossValidator.validate_positive_number(take_profit_price, "Take profit price")
        
        stop_loss_price = order_data.get('stop_loss_price', 0)
        StopLossValidator.validate_positive_number(stop_loss_price, "Stop loss price")
        
        # Logical price validation
        if action == 'BUY':
            if take_profit_price <= stop_loss_price:
                raise StopLossValidationError(
                    f"For BUY orders, take profit ({take_profit_price}) must be higher than stop loss ({stop_loss_price})"
                )
        else:  # SELL
            if take_profit_price >= stop_loss_price:
                raise StopLossValidationError(
                    f"For SELL orders, take profit ({take_profit_price}) must be lower than stop loss ({stop_loss_price})"
                )


# ========================================
# ENHANCED EXCEPTIONS
# ========================================

class ValidationError(Exception):
    """Base validation error."""
    pass

class TradingDisabledError(ValidationError):
    """Trading is disabled in configuration."""
    pass

class SafetyViolationError(ValidationError):
    """Safety violation detected."""
    pass

class OrderSizeLimitError(ValidationError):
    """Order size exceeds limits."""
    pass

class OrderValueLimitError(ValidationError):
    """Order value exceeds limits."""
    pass

class DailyLimitError(ValidationError):
    """Daily limits exceeded."""
    pass

class ForexTradingDisabledError(ValidationError):
    """Forex trading is disabled."""
    pass

class ForexValidationError(ValidationError):
    """Forex-specific validation error."""
    pass

class InternationalTradingDisabledError(ValidationError):
    """International trading is disabled."""
    pass

class InternationalValidationError(ValidationError):
    """International trading validation error."""
    pass

class StopLossDisabledError(ValidationError):
    """Stop loss orders are disabled."""
    pass

class StopLossValidationError(ValidationError):
    """Stop loss validation error."""
    pass


# ========================================
# VALIDATION UTILITIES
# ========================================

def validate_symbols_list(symbols: str) -> List[str]:
    """Validate and parse comma-separated symbols list."""
    if not symbols or not symbols.strip():
        raise ValidationError("Symbols list cannot be empty")
    
    symbol_list = [s.strip().upper() for s in symbols.split(',')]
    
    # Remove empty entries
    symbol_list = [s for s in symbol_list if s]
    
    if not symbol_list:
        raise ValidationError("No valid symbols found")
    
    if len(symbol_list) > 50:  # Reasonable limit
        raise ValidationError(f"Too many symbols: {len(symbol_list)}. Maximum 50 allowed")
    
    return symbol_list


def validate_order_common_fields(order_data: Dict[str, Any]) -> None:
    """Validate common order fields across all order types."""
    # Safety checks first
    TradingSafetyValidator.validate_trading_enabled()
    
    # Basic field validation
    if 'symbol' not in order_data:
        raise ValidationError("Symbol is required")
    
    if 'action' not in order_data:
        raise ValidationError("Action is required")
    
    if 'quantity' not in order_data:
        raise ValidationError("Quantity is required")
    
    # Order size validation
    quantity = order_data['quantity']
    TradingSafetyValidator.validate_order_size(quantity)
    
    # Estimate order value for validation (simplified)
    price = order_data.get('price', 100)  # Default estimate if no price
    estimated_value = quantity * price
    TradingSafetyValidator.validate_order_value(estimated_value)
