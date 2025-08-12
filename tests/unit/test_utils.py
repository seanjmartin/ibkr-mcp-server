"""
Tests for utility functions in utils.py
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from ibkr_mcp_server.utils import (
    rate_limit,
    retry_on_failure,
    safe_float,
    safe_int,
    ValidationError,
    ConnectionError,
    format_currency,
    format_percentage,
    validate_symbol,
    validate_symbols
)


class TestRateLimitDecorator:
    """Test rate limiting decorator functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator(self):
        """Test that rate_limit decorator enforces proper timing intervals"""
        calls_per_second = 4.0  # 4 calls per second = 0.25 second intervals
        expected_interval = 1.0 / calls_per_second  # 0.25 seconds
        
        @rate_limit(calls_per_second=calls_per_second)
        async def mock_api_call():
            return "success"
        
        # Record times of multiple calls
        call_times = []
        
        # Make 3 consecutive calls
        for i in range(3):
            start_time = time.time()
            result = await mock_api_call()
            call_times.append(time.time())
            assert result == "success"
        
        # Verify minimum intervals between calls
        for i in range(1, len(call_times)):
            actual_interval = call_times[i] - call_times[i-1]
            # Allow 10ms tolerance for timing precision
            assert actual_interval >= (expected_interval - 0.01), \
                f"Interval {actual_interval:.3f}s too short, expected >={expected_interval:.3f}s"
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_first_call_immediate(self):
        """Test that first call executes immediately without delay"""
        @rate_limit(calls_per_second=1.0)  # 1 second intervals
        async def mock_api_call():
            return "immediate"
        
        start_time = time.time()
        result = await mock_api_call()
        execution_time = time.time() - start_time
        
        assert result == "immediate"
        # First call should be immediate (less than 50ms)
        assert execution_time < 0.05
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_with_exception(self):
        """Test that rate limiter still updates timing even when function raises exception"""
        @rate_limit(calls_per_second=2.0)  # 0.5 second intervals
        async def failing_api_call():
            raise ValueError("API Error")
        
        # First call should fail immediately
        start_time = time.time()
        with pytest.raises(ValueError, match="API Error"):
            await failing_api_call()
        first_call_time = time.time()
        
        # Second call should still be rate limited
        with pytest.raises(ValueError, match="API Error"):
            await failing_api_call()
        second_call_time = time.time()
        
        # Verify interval was enforced despite exception
        interval = second_call_time - first_call_time
        assert interval >= 0.49  # Allow small tolerance
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_different_rates(self):
        """Test rate limiter with different call rates"""
        # Fast rate: 10 calls per second (0.1 second intervals)
        @rate_limit(calls_per_second=10.0)
        async def fast_call():
            return "fast"
        
        # Slow rate: 0.5 calls per second (2 second intervals)  
        @rate_limit(calls_per_second=0.5)
        async def slow_call():
            return "slow"
        
        # Test fast rate
        start_time = time.time()
        await fast_call()
        await fast_call()
        fast_duration = time.time() - start_time
        assert fast_duration >= 0.09  # Should take at least 0.1 seconds
        
        # Test slow rate  
        start_time = time.time()
        await slow_call()
        await slow_call()
        slow_duration = time.time() - start_time
        assert slow_duration >= 1.9  # Should take at least 2 seconds
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata"""
        @rate_limit(calls_per_second=1.0)
        async def documented_function():
            """This function has documentation"""
            return "metadata_preserved"
        
        # Check that metadata is preserved
        assert documented_function.__name__ == "documented_function"
        assert "This function has documentation" in documented_function.__doc__
        
        # Check function still works
        result = await documented_function()
        assert result == "metadata_preserved"


class TestRetryOnFailureDecorator:
    """Test retry on failure decorator functionality"""
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_success_first_try(self):
        """Test that successful function executes once without retry"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3)
        async def success_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await success_function()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_eventual_success(self):
        """Test that function retries until success"""
        call_count = 0
        
        @retry_on_failure(max_attempts=3, delay=0.01)  # Fast retry for testing
        async def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "eventual_success"
        
        result = await eventually_successful()
        assert result == "eventual_success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_max_attempts_exceeded(self):
        """Test that function gives up after max attempts"""
        call_count = 0
        
        @retry_on_failure(max_attempts=2, delay=0.01)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            await always_fails()
        
        assert call_count == 2  # Should have tried exactly max_attempts times
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_decorator(self):
        """Test retry decorator with comprehensive scenarios including backoff, timing, and metadata preservation"""
        import time
        
        # Test 1: Exponential backoff timing
        attempt_times = []
        call_count = 0
        
        @retry_on_failure(max_attempts=3, delay=0.1, backoff=2.0)
        async def test_backoff():
            nonlocal call_count, attempt_times
            call_count += 1
            attempt_times.append(time.time())
            if call_count < 3:
                raise ConnectionError(f"Attempt {call_count} failed")
            return "backoff_success"
        
        start_time = time.time()
        result = await test_backoff()
        
        # Verify result and attempt count
        assert result == "backoff_success"
        assert call_count == 3
        assert len(attempt_times) == 3
        
        # Verify exponential backoff timing (0.1s, 0.2s delays)
        # First attempt should be immediate
        assert attempt_times[0] - start_time < 0.05
        
        # Second attempt should be after ~0.1s delay  
        second_delay = attempt_times[1] - attempt_times[0]
        assert 0.08 <= second_delay <= 0.15  # Allow timing tolerance
        
        # Third attempt should be after ~0.2s delay (0.1 * 2^1)
        third_delay = attempt_times[2] - attempt_times[1] 
        assert 0.18 <= third_delay <= 0.25  # Allow timing tolerance
        
        # Test 2: Function metadata preservation
        @retry_on_failure(max_attempts=2, delay=0.01)
        async def documented_retry_function():
            """This function has documentation and should preserve metadata"""
            return "metadata_preserved"
        
        # Verify metadata is preserved
        assert documented_retry_function.__name__ == "documented_retry_function"
        assert "This function has documentation" in documented_retry_function.__doc__
        
        # Verify function still works
        result = await documented_retry_function()
        assert result == "metadata_preserved"
        
        # Test 3: Different exception types
        exception_types = []
        attempt_count = 0
        
        @retry_on_failure(max_attempts=4, delay=0.01)
        async def different_exceptions():
            nonlocal attempt_count, exception_types
            attempt_count += 1
            
            if attempt_count == 1:
                exc = ValueError("First failure")
                exception_types.append(type(exc))
                raise exc
            elif attempt_count == 2:
                exc = ConnectionError("Second failure")
                exception_types.append(type(exc))
                raise exc
            elif attempt_count == 3:
                exc = RuntimeError("Third failure")
                exception_types.append(type(exc))
                raise exc
            else:
                return "all_exceptions_handled"
        
        result = await different_exceptions()
        assert result == "all_exceptions_handled"
        assert attempt_count == 4
        assert ValueError in exception_types
        assert ConnectionError in exception_types
        assert RuntimeError in exception_types
        
        # Test 4: Zero delay behavior
        zero_delay_count = 0
        
        @retry_on_failure(max_attempts=2, delay=0.0)
        async def zero_delay_test():
            nonlocal zero_delay_count
            zero_delay_count += 1
            if zero_delay_count == 1:
                raise ValueError("Zero delay test")
            return "zero_delay_success"
        
        start_time = time.time()
        result = await zero_delay_test()
        total_time = time.time() - start_time
        
        assert result == "zero_delay_success"
        assert zero_delay_count == 2
        # Should complete very quickly with zero delay
        assert total_time < 0.05
        
        # Test 5: Custom delay and backoff parameters
        custom_call_count = 0
        custom_times = []
        
        @retry_on_failure(max_attempts=3, delay=0.05, backoff=3.0)
        async def custom_parameters():
            nonlocal custom_call_count, custom_times
            custom_call_count += 1
            custom_times.append(time.time())
            if custom_call_count < 3:
                raise ValueError("Custom params test")
            return "custom_success"
        
        result = await custom_parameters()
        assert result == "custom_success"
        assert custom_call_count == 3
        
        # Verify custom backoff: delays should be 0.05s, 0.15s (0.05 * 3^1)
        if len(custom_times) >= 2:
            first_delay = custom_times[1] - custom_times[0]
            assert 0.04 <= first_delay <= 0.08  # ~0.05s with tolerance
        
        if len(custom_times) >= 3:
            second_delay = custom_times[2] - custom_times[1]
            assert 0.13 <= second_delay <= 0.18  # ~0.15s with tolerance


class TestSafeConversions:
    """Test safe conversion utility functions"""
    
    def test_safe_float_conversion(self):
        """Test safe float conversion with various inputs"""
        # Valid conversions
        assert safe_float("123.45") == 123.45
        assert safe_float(123.45) == 123.45
        assert safe_float(123) == 123.0
        
        # Invalid inputs should return default
        assert safe_float(None) == 0.0
        assert safe_float("") == 0.0
        assert safe_float("invalid") == 0.0
        assert safe_float([1, 2, 3]) == 0.0
        
        # Custom default
        assert safe_float("invalid", default=99.9) == 99.9
        assert safe_float(None, default=-1.0) == -1.0
    
    def test_safe_int_conversion(self):
        """Test safe int conversion with various inputs"""
        # Valid conversions
        assert safe_int("123") == 123
        assert safe_int(123) == 123
        assert safe_int(123.7) == 123  # Truncates float
        assert safe_int("123.0") == 123  # Handles string float
        
        # Invalid inputs should return default
        assert safe_int(None) == 0
        assert safe_int("") == 0
        assert safe_int("invalid") == 0
        assert safe_int([1, 2, 3]) == 0
        
        # Custom default
        assert safe_int("invalid", default=999) == 999
        assert safe_int(None, default=-1) == -1


class TestValidationFunctions:
    """Test validation utility functions"""
    
    def test_validate_symbol_valid_inputs(self):
        """Test symbol validation with valid inputs"""
        assert validate_symbol("AAPL") == "AAPL"
        assert validate_symbol("aapl") == "AAPL"  # Should uppercase
        assert validate_symbol(" MSFT ") == "MSFT"  # Should trim
        assert validate_symbol("BRK.A") == "BRK.A"  # Allow dots
        assert validate_symbol("7203") == "7203"  # Allow numbers
    
    def test_validate_symbol_invalid_inputs(self):
        """Test symbol validation with invalid inputs"""
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol("")
        
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol(None)
        
        with pytest.raises(ValidationError, match="Symbol too long"):
            validate_symbol("VERY_LONG_SYMBOL_NAME")  # Over 12 chars
    
    def test_validate_symbols_valid_inputs(self):
        """Test multiple symbols validation with valid inputs"""
        result = validate_symbols("AAPL,MSFT,GOOGL")
        assert result == ["AAPL", "MSFT", "GOOGL"]
        
        # Should handle spaces and duplicates
        result = validate_symbols(" aapl , MSFT, aapl ")
        assert result == ["AAPL", "MSFT"]  # Removes duplicate
    
    def test_validate_symbols_invalid_inputs(self):
        """Test multiple symbols validation with invalid inputs"""
        with pytest.raises(ValidationError, match="Symbols string cannot be empty"):
            validate_symbols("")
        
        # Test too many symbols (over 50)
        many_symbols = ",".join([f"SYM{i}" for i in range(51)])
        with pytest.raises(ValidationError, match="Too many symbols"):
            validate_symbols(many_symbols)


class TestFormattingFunctions:
    """Test formatting utility functions"""
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(1234.56, "EUR") == "1,234.56 EUR"
        assert format_currency(0) == "$0.00"
        assert format_currency("invalid") == "N/A USD"
        assert format_currency(None, "GBP") == "N/A GBP"
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        assert format_percentage(12.3456) == "12.35%"
        assert format_percentage(0) == "0.00%"
        assert format_percentage("5.5") == "5.50%"
        assert format_percentage("invalid") == "N/A%"
        assert format_percentage(None) == "N/A%"


class TestExceptionClasses:
    """Test custom exception classes"""
    
    def test_exception_hierarchy(self):
        """Test that custom exceptions have proper inheritance"""
        from ibkr_mcp_server.utils import IBKRError, ConnectionError, ValidationError
        
        # Test inheritance
        assert issubclass(ConnectionError, IBKRError)
        assert issubclass(ValidationError, IBKRError)
        
        # Test exception creation
        conn_error = ConnectionError("Connection failed")
        assert str(conn_error) == "Connection failed"
        assert isinstance(conn_error, IBKRError)
        
        val_error = ValidationError("Invalid input") 
        assert str(val_error) == "Invalid input"
        assert isinstance(val_error, IBKRError)
    
    def test_validation_error_handling(self):
        """Test ValidationError class functionality and usage patterns"""
        from ibkr_mcp_server.utils import ValidationError, validate_symbol, validate_symbols
        
        # Test ValidationError creation with different messages
        error1 = ValidationError("Symbol validation failed")
        assert str(error1) == "Symbol validation failed"
        assert error1.args[0] == "Symbol validation failed"
        
        error2 = ValidationError("Order parameter invalid: quantity must be positive")
        assert str(error2) == "Order parameter invalid: quantity must be positive"
        
        # Test ValidationError is raised by validation functions
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol("")
        
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol(None)
        
        with pytest.raises(ValidationError, match="Symbol too long"):
            validate_symbol("VERY_LONG_SYMBOL_NAME_THAT_EXCEEDS_LIMIT")
        
        with pytest.raises(ValidationError, match="Symbols string cannot be empty"):
            validate_symbols("")
        
        # Test ValidationError can be caught and handled
        try:
            validate_symbol("INVALID@")  # Contains invalid character but short enough
        except ValidationError as e:
            assert "Symbol must contain only alphanumeric characters" in str(e)
            assert isinstance(e, Exception)  # Inherits from base Exception
        else:
            pytest.fail("Expected ValidationError to be raised")
        
        # Test ValidationError with custom message formatting
        def custom_validation_function(value):
            if not value:
                raise ValidationError(f"Value '{value}' is invalid: must not be empty")
            if len(str(value)) > 10:
                raise ValidationError(f"Value '{value}' is invalid: too long (max 10 chars)")
            return value
        
        # Test custom validation function
        assert custom_validation_function("valid") == "valid"
        
        with pytest.raises(ValidationError, match="Value '' is invalid: must not be empty"):
            custom_validation_function("")
        
        with pytest.raises(ValidationError, match="Value 'toolongvalue' is invalid: too long"):
            custom_validation_function("toolongvalue")
        
        # Test ValidationError in exception chaining
        try:
            try:
                validate_symbol("")
            except ValidationError as e:
                raise ValidationError("Outer validation failed") from e
        except ValidationError as outer_error:
            assert str(outer_error) == "Outer validation failed"
            assert isinstance(outer_error.__cause__, ValidationError)
            assert "Symbol must be a non-empty string" in str(outer_error.__cause__)
    
    def test_connection_error_handling(self):
        """Test ConnectionError class functionality and usage patterns"""
        from ibkr_mcp_server.utils import ConnectionError, IBKRError
        
        # Test ConnectionError creation with different messages
        error1 = ConnectionError("Connection to IBKR failed")
        assert str(error1) == "Connection to IBKR failed"
        assert error1.args[0] == "Connection to IBKR failed"
        
        error2 = ConnectionError("Network timeout occurred")
        assert str(error2) == "Network timeout occurred"
        
        # Test ConnectionError inheritance
        conn_error = ConnectionError("Gateway disconnected")
        assert isinstance(conn_error, IBKRError)
        assert isinstance(conn_error, Exception)
        
        # Test ConnectionError can be caught and handled
        def simulate_connection_failure():
            raise ConnectionError("Simulated connection failure")
        
        try:
            simulate_connection_failure()
        except ConnectionError as e:
            assert "Simulated connection failure" in str(e)
            assert isinstance(e, IBKRError)
        else:
            pytest.fail("Expected ConnectionError to be raised")
        
        # Test ConnectionError with custom message formatting
        def custom_connection_function(host, port):
            if not host:
                raise ConnectionError(f"Connection failed: host '{host}' is invalid")
            if port <= 0:
                raise ConnectionError(f"Connection failed: port {port} is invalid (must be positive)")
            # Simulate connection attempt
            raise ConnectionError(f"Failed to connect to {host}:{port} - connection refused")
        
        # Test custom connection function with different error scenarios
        with pytest.raises(ConnectionError, match="host '' is invalid"):
            custom_connection_function("", 7497)
        
        with pytest.raises(ConnectionError, match="port -1 is invalid"):
            custom_connection_function("localhost", -1)
        
        with pytest.raises(ConnectionError, match="Failed to connect to localhost:7497"):
            custom_connection_function("localhost", 7497)
        
        # Test ConnectionError in exception chaining
        try:
            try:
                custom_connection_function("localhost", 7497)
            except ConnectionError as e:
                raise ConnectionError("Outer connection error") from e
        except ConnectionError as outer_error:
            assert str(outer_error) == "Outer connection error"
            assert isinstance(outer_error.__cause__, ConnectionError)
            assert "Failed to connect to localhost:7497" in str(outer_error.__cause__)
        
        # Test different ConnectionError contexts
        network_error = ConnectionError("Network unreachable")
        timeout_error = ConnectionError("Connection timeout after 30 seconds")
        auth_error = ConnectionError("Authentication failed")
        
        # All should be ConnectionError instances
        for error in [network_error, timeout_error, auth_error]:
            assert isinstance(error, ConnectionError)
            assert isinstance(error, IBKRError)
            assert isinstance(error, Exception)
    
    def test_utility_edge_cases(self):
        """Test utility functions with edge cases (empty strings, None values, etc.)"""
        from ibkr_mcp_server.utils import (
            safe_float, safe_int, format_currency, format_percentage, 
            validate_symbol, validate_symbols, ValidationError, IBKRError, APIError, TradingError
        )
        import math
        
        # Test safe_float edge cases
        assert safe_float(float('inf')) == 0.0  # Infinity is unsafe -> default
        assert safe_float(float('-inf')) == 0.0  # Negative infinity is unsafe -> default
        import math
        assert safe_float(float('nan')) == 0.0  # NaN is unsafe -> default
        assert safe_float([]) == 0.0  # Empty list -> default
        assert safe_float({}) == 0.0  # Empty dict -> default
        assert safe_float(set()) == 0.0  # Empty set -> default
        assert safe_float(object()) == 0.0  # Random object -> default
        assert safe_float("   ") == 0.0  # Whitespace only -> default
        assert safe_float("\n\t") == 0.0  # Whitespace characters -> default
        assert safe_float("123.456.789") == 0.0  # Multiple decimals -> default
        assert safe_float("12abc") == 0.0  # Mixed alphanumeric -> default
        assert safe_float("1e400") == 0.0  # Number too large -> default
        assert safe_float("-0") == 0.0  # Negative zero -> default
        assert safe_float("+123.45") == 123.45  # Positive sign handled
        assert safe_float("-123.45") == -123.45  # Negative sign handled
        assert safe_float("1.23e-5") == 1.23e-5  # Scientific notation handled
        
        # Test safe_int edge cases  
        # Infinity values will raise OverflowError when converting to int, so they go to default
        assert safe_int(float('inf')) == 0  # Infinity -> default (OverflowError caught)
        assert safe_int(float('-inf')) == 0  # Negative infinity -> default (OverflowError caught)
        assert safe_int(float('nan')) == 0  # NaN -> default (ValueError caught)
        assert safe_int(123.99999) == 123  # Float truncation
        assert safe_int(123.00001) == 123  # Float truncation
        assert safe_int(-123.99999) == -123  # Negative float truncation
        assert safe_int("123.") == 123  # Trailing decimal point
        assert safe_int(".123") == 0  # Leading decimal only -> default
        assert safe_int("1.23e2") == 123  # Scientific notation as string
        assert safe_int("1e400") == 0  # Number too large -> default
        assert safe_int([1, 2, 3]) == 0  # List -> default
        assert safe_int({"value": 123}) == 0  # Dict -> default
        assert safe_int(True) == 1  # Boolean True -> 1
        assert safe_int(False) == 0  # Boolean False -> 0
        assert safe_int("  123  ") == 123  # Whitespace around number
        assert safe_int("0xFF") == 0  # Hex string -> default (not supported)
        assert safe_int("0o755") == 0  # Octal string -> default (not supported)
        
        # Test format_currency edge cases
        # format_currency uses safe_float internally, so infinity/NaN values become 0.0 -> "$0.00"
        assert format_currency(float('inf')) == "$0.00"  # Infinity -> safe_float(inf) -> 0.0 -> "$0.00"
        assert format_currency(float('-inf')) == "$0.00"  # Negative infinity -> safe_float(-inf) -> 0.0 -> "$0.00"
        assert format_currency(float('nan')) == "$0.00"  # NaN -> safe_float(nan) -> 0.0 -> "$0.00"
        assert format_currency(1e20) == "$100,000,000,000,000,000,000.00"  # Very large number
        assert format_currency(-1e20) == "$-100,000,000,000,000,000,000.00"  # Very large negative
        assert format_currency(1e-10) == "$0.00"  # Very small number
        assert format_currency(None, "XYZ") == "N/A XYZ"  # Custom invalid currency
        assert format_currency("not_a_number", "CHF") == "N/A CHF"  # Invalid string
        assert format_currency([123.45]) == "N/A USD"  # List input
        assert format_currency({"amount": 123}) == "N/A USD"  # Dict input
        assert format_currency("") == "N/A USD"  # Empty string
        assert format_currency("   ") == "N/A USD"  # Whitespace only
        assert format_currency(0.001) == "$0.00"  # Very small positive value
        assert format_currency(-0.001) == "$0.00"  # Very small negative value
        
        # Test format_percentage edge cases
        # format_percentage uses safe_float internally, so infinity/NaN values become 0.0 -> "0.00%"
        assert format_percentage(float('inf')) == "0.00%"  # Infinity -> safe_float(inf) -> 0.0 -> "0.00%"
        assert format_percentage(float('-inf')) == "0.00%"  # Negative infinity -> safe_float(-inf) -> 0.0 -> "0.00%"
        assert format_percentage(float('nan')) == "0.00%"  # NaN -> safe_float(nan) -> 0.0 -> "0.00%"
        assert format_percentage(1000) == "1000.00%"  # Large percentage
        assert format_percentage(-100) == "-100.00%"  # Negative percentage
        assert format_percentage(1e-10) == "0.00%"  # Very small percentage
        assert format_percentage("") == "N/A%"  # Empty string
        assert format_percentage("   ") == "N/A%"  # Whitespace only
        assert format_percentage([12.34]) == "N/A%"  # List input
        assert format_percentage({"percent": 12}) == "N/A%"  # Dict input
        assert format_percentage("not_a_number") == "N/A%"  # Invalid string
        assert format_percentage(None) == "N/A%"  # None input
        
        # Test validate_symbol edge cases
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol(None)
        
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol("")
        
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol("   ")  # Whitespace only
        
        with pytest.raises(ValidationError, match="Symbol must be a non-empty string"):
            validate_symbol("\t\n")  # Whitespace characters only
        
        with pytest.raises(ValidationError, match="Symbol too long"):
            validate_symbol("A" * 13)  # Exactly one character too long
        
        with pytest.raises(ValidationError, match="Symbol too long"):
            validate_symbol("VERY_LONG_SYMBOL_NAME_THAT_EXCEEDS_12_CHARS")
        
        # Test edge cases that should work
        assert validate_symbol("A") == "A"  # Single character
        assert validate_symbol("A" * 12) == "A" * 12  # Maximum length (12 chars)
        assert validate_symbol("aapl") == "AAPL"  # Lowercase conversion
        assert validate_symbol("  MSFT  ") == "MSFT"  # Whitespace trimming
        assert validate_symbol("brk.a") == "BRK.A"  # Dot and lowercase
        assert validate_symbol("7203") == "7203"  # Numbers only
        assert validate_symbol("BRK-A") == "BRK-A"  # Dash character
        assert validate_symbol("BRK/A") == "BRK/A"  # Slash character
        
        # Test validate_symbols edge cases
        with pytest.raises(ValidationError, match="Symbols string cannot be empty"):
            validate_symbols("")
        
        with pytest.raises(ValidationError, match="Symbols string cannot be empty"):
            validate_symbols("   ")  # Whitespace only
        
        with pytest.raises(ValidationError, match="Symbols string cannot be empty"):
            validate_symbols("\t\n")  # Whitespace characters only
        
        with pytest.raises(ValidationError, match="Too many symbols"):
            validate_symbols(",".join([f"SYM{i:02d}" for i in range(51)]))  # 51 symbols
        
        # Test symbols edge cases that should work
        assert validate_symbols("AAPL") == ["AAPL"]  # Single symbol
        assert validate_symbols("aapl,MSFT") == ["AAPL", "MSFT"]  # Mixed case
        assert validate_symbols("AAPL,MSFT,AAPL") == ["AAPL", "MSFT"]  # Duplicate removal
        assert validate_symbols("  AAPL  ,  MSFT  ") == ["AAPL", "MSFT"]  # Whitespace
        assert validate_symbols("AAPL,,MSFT") == ["AAPL", "MSFT"]  # Empty elements
        assert validate_symbols("AAPL,") == ["AAPL"]  # Trailing comma
        assert validate_symbols(",AAPL") == ["AAPL"]  # Leading comma
        assert validate_symbols("7203,005930") == ["7203", "005930"]  # Number symbols
        
        # Test all exception classes have proper inheritance and can be raised
        base_error = IBKRError("Base IBKR error")
        assert isinstance(base_error, Exception)
        assert str(base_error) == "Base IBKR error"
        
        api_error = APIError("API rate limit exceeded")
        assert isinstance(api_error, IBKRError)
        assert isinstance(api_error, Exception)
        assert str(api_error) == "API rate limit exceeded"
        
        trading_error = TradingError("Order rejected by exchange")
        assert isinstance(trading_error, IBKRError)
        assert isinstance(trading_error, Exception)
        assert str(trading_error) == "Order rejected by exchange"
        
        # Test exception raising and catching
        def raise_api_error():
            raise APIError("Simulated API error")
        
        def raise_trading_error():
            raise TradingError("Simulated trading error")
        
        with pytest.raises(APIError, match="Simulated API error"):
            raise_api_error()
        
        with pytest.raises(TradingError, match="Simulated trading error"):
            raise_trading_error()
        
        # Test catching by parent class
        with pytest.raises(IBKRError):
            raise_api_error()
        
        with pytest.raises(IBKRError):
            raise_trading_error()
        
        # Test exception chaining with all error types
        try:
            try:
                raise APIError("Original API error")
            except APIError as e:
                raise TradingError("Trading error caused by API issue") from e
        except TradingError as outer_error:
            assert str(outer_error) == "Trading error caused by API issue"
            assert isinstance(outer_error.__cause__, APIError)
            assert str(outer_error.__cause__) == "Original API error"
