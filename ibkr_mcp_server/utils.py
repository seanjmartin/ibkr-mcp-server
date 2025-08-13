"""Utility functions for IBKR MCP Server."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar, Union
from decimal import Decimal

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def rate_limit(calls_per_second: float = 2.0):
    """
    Rate limiting decorator for IBKR API calls.
    
    Args:
        calls_per_second: Maximum calls allowed per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                await asyncio.sleep(left_to_wait)
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                last_called[0] = time.time()
        
        return wrapper
    return decorator


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry decorator for failed operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def format_currency(value: Union[float, Decimal, str], currency: str = "USD") -> str:
    """Format currency values for display."""
    try:
        # Check for None values explicitly - these should show as N/A
        if value is None:
            return f"N/A {currency}"
        
        # Check for invalid types (lists, dicts, sets, etc.) - these should show as N/A
        if isinstance(value, (list, dict, set, tuple)):
            return f"N/A {currency}"
        
        # Check for empty or whitespace-only strings - these should show as N/A
        if isinstance(value, str) and not value.strip():
            return f"N/A {currency}"
        
        # For non-empty string inputs, try direct conversion first to detect truly invalid strings
        if isinstance(value, str):
            try:
                float(value)  # Just test conversion, don't use result
            except (ValueError, TypeError):
                return f"N/A {currency}"
        
        num_value = safe_float(value, 0.0)
        
        # Round to 2 decimal places first, then check if it's effectively zero
        # This prevents displaying "-0.00" for very small negative numbers
        rounded_value = round(num_value, 2)
        if rounded_value == 0.0:
            rounded_value = 0.0  # Ensure it's positive zero
        
        if currency == "USD":
            return f"${rounded_value:,.2f}"
        else:
            return f"{rounded_value:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"N/A {currency}"


def format_percentage(value: Union[float, Decimal, str]) -> str:
    """Format percentage values for display."""
    try:
        # Check for None values explicitly - these should show as N/A
        if value is None:
            return "N/A%"
        
        # Check for invalid types (lists, dicts, sets, etc.) - these should show as N/A
        if isinstance(value, (list, dict, set, tuple)):
            return "N/A%"
        
        # Check for empty or whitespace-only strings - these should show as N/A
        if isinstance(value, str) and not value.strip():
            return "N/A%"
        
        # For non-empty string inputs, try direct conversion first to detect truly invalid strings
        if isinstance(value, str):
            try:
                float(value)  # Just test conversion, don't use result
            except (ValueError, TypeError):
                return "N/A%"
        
        num_value = safe_float(value, 0.0)
        
        # Round to 2 decimal places first, then check if it's effectively zero
        # This prevents displaying "-0.00%" for very small negative numbers
        rounded_value = round(num_value, 2)
        if rounded_value == 0.0:
            rounded_value = 0.0  # Ensure it's positive zero
        
        return f"{rounded_value:.2f}%"
    except (ValueError, TypeError):
        return "N/A%"


def validate_symbol(symbol: str) -> str:
    """Validate and clean stock symbol."""
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string")
    
    cleaned = symbol.strip().upper()
    
    # Check if symbol becomes empty after stripping whitespace
    if not cleaned:
        raise ValidationError("Symbol must be a non-empty string")
    
    if len(cleaned) > 12:  # IBKR symbol length limit
        raise ValidationError("Symbol too long (max 12 characters)")
    
    # Allow alphanumeric characters plus common symbol characters
    import re
    if not re.match(r'^[A-Z0-9.\-/]+$', cleaned):
        raise ValidationError("Symbol must contain only alphanumeric characters, dots, dashes, or slashes")
    
    return cleaned


def validate_symbols(symbols_str: str) -> list[str]:
    """Validate and clean a comma-separated list of symbols."""
    if not symbols_str:
        raise ValidationError("Symbols string cannot be empty")
    
    # Check if symbols_str becomes empty after stripping whitespace
    if not symbols_str.strip():
        raise ValidationError("Symbols string cannot be empty")
    
    symbols = []
    for symbol in symbols_str.split(','):
        # Skip empty symbols (from double commas, etc.)
        if not symbol.strip():
            continue
        
        cleaned = validate_symbol(symbol)
        if cleaned not in symbols:  # Avoid duplicates
            symbols.append(cleaned)
    
    if len(symbols) > 50:  # Reasonable limit to avoid API overload
        raise ValidationError("Too many symbols (max 50)")
    
    return symbols


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    import math
    import logging
    
    # Add diagnostic logging for zero price issue
    logger = logging.getLogger(__name__)
    
    try:
        if value is None or value == '':
            logger.debug(f"safe_float: None/empty value, returning default {default}")
            return default
        result = float(value)
        # Check for infinity and NaN values - these are unsafe for financial calculations
        if math.isinf(result) or math.isnan(result):
            logger.warning(f"safe_float: Invalid float value {value} (inf/nan), returning default {default}")
            return default
        
        # Log when we get zero values for price data - this might indicate IBKR API issues
        if result == 0.0 and default == 0.0:
            logger.warning(f"safe_float: Zero price value detected - input: {value} (type: {type(value)})")
        
        return result
    except (ValueError, TypeError) as e:
        logger.debug(f"safe_float: Conversion failed for {value} (type: {type(value)}): {e}, returning default {default}")
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    import math
    try:
        if value is None or value == '':
            return default
        # First convert to float to handle string floats like "100.0"
        float_value = float(value)
        # Check for infinity and NaN values - these are unsafe for integer conversion
        if math.isinf(float_value) or math.isnan(float_value):
            return default
        return int(float_value)
    except (ValueError, TypeError, OverflowError):
        return default


class IBKRError(Exception):
    """Base exception for IBKR-related errors."""
    pass


class ConnectionError(IBKRError):
    """IBKR connection-related errors."""
    pass


class APIError(IBKRError):
    """IBKR API-related errors."""
    pass


class ValidationError(IBKRError):
    """Input validation errors."""
    pass


class TradingError(IBKRError):
    """Trading-related errors."""
    pass
