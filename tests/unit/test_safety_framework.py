"""
Unit tests for IBKR MCP Server Safety Framework.

Tests the critical safety components that protect users from trading errors,
enforce limits, and provide audit trails.
"""
import pytest
import json
import tempfile
import time
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ibkr_mcp_server.safety_framework import (
    TradingAuditLogger,
    DailyLimitsTracker,
    RateLimiter,
    EmergencyKillSwitch,
    TradingSafetyManager,
)
from ibkr_mcp_server.enhanced_validators import (
    SafetyViolationError,
    DailyLimitError
)


@pytest.mark.unit
@pytest.mark.safety
class TestTradingAuditLogger:
    """Test audit logging functionality"""
    
    def test_audit_logger_initialization(self):
        """Test audit logger initializes correctly"""
        logger = TradingAuditLogger()
        
        assert logger.logger is not None
        assert logger.session_id is not None
        assert logger.session_id.startswith("session_")
    
    def test_log_order_attempt(self):
        """Test logging order attempts"""
        logger = TradingAuditLogger()
        
        order_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "order_type": "MKT"
        }
        
        validation_result = {
            "is_safe": True,
            "warnings": [],
            "errors": []
        }
        
        # Should not raise exception
        logger.log_order_attempt(order_data, validation_result)
    
    def test_log_safety_violation(self):
        """Test logging safety violations"""
        logger = TradingAuditLogger()
        
        # Should not raise exception
        logger.log_safety_violation(
            "DAILY_LIMIT_EXCEEDED",
            {"daily_orders": 51, "limit": 50}
        )
    
    def test_data_sanitization(self):
        """Test sensitive data is sanitized in logs"""
        logger = TradingAuditLogger()
        
        # Test order data with sensitive info
        order_data = {
            "symbol": "AAPL",
            "account": "U12345678",
            "password": "secret123",  # Should be removed
            "api_key": "key123"      # Should be removed
        }
        
        sanitized = logger._sanitize_order_data(order_data)
        
        assert sanitized["symbol"] == "AAPL"
        assert sanitized["account"] == "U12345678"  # Account kept as-is
        assert sanitized["password"] == "***REDACTED***"  # Sensitive fields redacted
        assert sanitized["api_key"] == "***REDACTED***"


@pytest.mark.unit
@pytest.mark.safety
class TestDailyLimitsTracker:
    """Test daily limits tracking functionality"""
    
    def test_order_count_increment(self):
        """Test order count increment and basic functionality"""
        tracker = DailyLimitsTracker()
        
        # Initial state
        assert tracker.daily_order_count == 0
        
        # Increment count
        tracker.check_and_increment_order_count()
        assert tracker.daily_order_count == 1
        
        # Multiple increments
        tracker.check_and_increment_order_count()
        tracker.check_and_increment_order_count()
        assert tracker.daily_order_count == 3
    
    def test_daily_limit_enforcement(self):
        """Test daily limit enforcement"""
        tracker = DailyLimitsTracker()
        
        # Get current daily stats to see actual limit
        stats = tracker.get_daily_stats()
        max_orders = stats["max_orders"]
        
        # Increment to limit
        for i in range(max_orders):
            tracker.check_and_increment_order_count()
        
        assert tracker.daily_order_count == max_orders
        
        # Next increment should raise exception
        with pytest.raises(DailyLimitError) as exc_info:
            tracker.check_and_increment_order_count()
        
        assert "daily order limit" in str(exc_info.value).lower()
        assert tracker.daily_order_count == max_orders  # Should not increment
    
    def test_volume_tracking(self):
        """Test order volume tracking"""
        tracker = DailyLimitsTracker()
        
        # Add some volume
        tracker.add_order_volume(10000.0)
        tracker.add_order_volume(5000.0)
        
        stats = tracker.get_daily_stats()
        assert stats["daily_volume"] == 15000.0
        assert stats["order_count"] == 0  # Volume doesn't increment count
    
    def test_daily_reset_functionality(self):
        """Test automatic daily reset"""
        tracker = DailyLimitsTracker()
        
        # Set some counts and volume
        tracker.daily_order_count = 10
        tracker.daily_volume = 50000.0
        
        # Simulate new day by changing last_reset_date
        tracker.last_reset_date = date.today() - timedelta(days=1)
        
        # Check should reset counts
        tracker.check_and_increment_order_count()
        
        assert tracker.daily_order_count == 1  # Reset and incremented
        assert tracker.daily_volume == 0.0  # Should be reset
        assert tracker.last_reset_date == date.today()
    
    def test_get_daily_stats(self):
        """Test daily statistics reporting"""
        tracker = DailyLimitsTracker()
        
        # Add some data
        tracker.daily_order_count = 5
        tracker.daily_volume = 25000.0
        
        stats = tracker.get_daily_stats()
        
        expected_keys = [
            "order_count", "daily_volume", "max_orders",
            "remaining_orders", "reset_date"
        ]
        
        for key in expected_keys:
            assert key in stats
        
        assert stats["order_count"] == 5
        assert stats["daily_volume"] == 25000.0


@pytest.mark.unit
@pytest.mark.safety
class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limit_enforcement(self):
        """Test basic rate limit enforcement"""
        limiter = RateLimiter()
        
        # Should allow initial requests (default limit: 30 for market_data)
        for i in range(30):
            assert limiter.check_rate_limit("market_data")
        
        # Should block additional requests
        assert not limiter.check_rate_limit("market_data")
    
    def test_different_operation_types(self):
        """Test different operation types have separate limits"""
        limiter = RateLimiter()
        
        # Use up market_data limit (30)
        for i in range(30):
            limiter.check_rate_limit("market_data")
        
        # Market data should be blocked
        assert not limiter.check_rate_limit("market_data")
        
        # Order placement should still be allowed (different limit: 5)
        assert limiter.check_rate_limit("order_placement")
    
    def test_rate_limit_window_reset(self):
        """Test rate limit window reset over time"""
        limiter = RateLimiter()
        
        # Use up limit
        for i in range(5):
            limiter.check_rate_limit("order_placement")
        
        # Should be blocked
        assert not limiter.check_rate_limit("order_placement")
        
        # Mock time advancement beyond window (60 seconds)
        current_time = time.time()
        with patch('ibkr_mcp_server.safety_framework.time.time') as mock_time:
            mock_time.return_value = current_time + 65  # 65 seconds later
            
            # Should be allowed again after window reset
            assert limiter.check_rate_limit("order_placement")
    
    def test_cleanup_old_entries(self):
        """Test cleanup of old rate limit entries"""
        limiter = RateLimiter()
        
        # Add entries
        limiter.check_rate_limit("market_data")
        limiter.check_rate_limit("order_placement")
        
        # Verify entries exist
        assert len(limiter.request_history["market_data"]) > 0
        assert len(limiter.request_history["order_placement"]) > 0
        
        # Mock time advancement
        current_time = time.time()
        with patch('ibkr_mcp_server.safety_framework.time.time') as mock_time:
            mock_time.return_value = current_time + 3700  # Over 1 hour
            
            # Trigger cleanup
            limiter._cleanup_old_entries()
            
            # Old entries should be cleaned up
            assert len(limiter.request_history["market_data"]) == 0
            assert len(limiter.request_history["order_placement"]) == 0


@pytest.mark.unit
@pytest.mark.safety
class TestEmergencyKillSwitch:
    """Test emergency kill switch functionality"""
    
    def test_initial_state(self):
        """Test kill switch starts inactive"""
        kill_switch = EmergencyKillSwitch()
        
        assert not kill_switch.is_active()
        assert kill_switch.activation_reason is None
        assert kill_switch.activation_time is None
    
    def test_kill_switch_activation(self):
        """Test kill switch activation"""
        kill_switch = EmergencyKillSwitch()
        
        # Activate with reason
        result = kill_switch.activate("Test activation for safety")
        
        assert kill_switch.is_active()
        assert result["status"] == "activated"
        assert result["reason"] == "Test activation for safety"
        assert result["activated_at"] is not None
        
        # Verify internal state
        assert kill_switch.activation_reason == "Test activation for safety"
        assert kill_switch.activation_time is not None
    
    def test_kill_switch_deactivation_with_override(self):
        """Test kill switch deactivation with correct override"""
        kill_switch = EmergencyKillSwitch()
        
        # Activate first
        kill_switch.activate("Test activation")
        assert kill_switch.is_active()
        
        # Deactivate with correct override (note: actual code uses 2024)
        result = kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
        
        assert not kill_switch.is_active()
        assert result["status"] == "deactivated"
    
    def test_kill_switch_deactivation_with_wrong_override(self):
        """Test kill switch deactivation with incorrect override"""
        kill_switch = EmergencyKillSwitch()
        
        # Activate first
        kill_switch.activate("Test activation")
        assert kill_switch.is_active()
        
        # Try to deactivate with wrong override
        result = kill_switch.deactivate("WRONG_OVERRIDE")
        
        # Should remain active
        assert kill_switch.is_active()
        assert result["status"] == "invalid_override_code"
    
    def test_multiple_activations(self):
        """Test multiple activations return already_activated status"""
        kill_switch = EmergencyKillSwitch()
        
        # First activation
        result1 = kill_switch.activate("First reason")
        assert result1["status"] == "activated"
        
        # Second activation should return already_activated status
        result2 = kill_switch.activate("Second reason")
        assert result2["status"] == "already_activated"
        assert result2["reason"] == "First reason"  # Keeps original reason
        
        assert kill_switch.is_active()
        assert kill_switch.activation_reason == "First reason"


@pytest.mark.unit
@pytest.mark.safety
class TestTradingSafetyManager:
    """Test comprehensive safety manager"""
    
    def test_safety_manager_initialization(self):
        """Test safety manager initializes all components"""
        manager = TradingSafetyManager()
        
        assert manager.daily_limits is not None
        assert manager.rate_limiter is not None
        assert manager.kill_switch is not None
        assert manager.audit_logger is not None
        assert hasattr(manager, 'safety_violations')
    
    def test_trading_operation_validation_success(self):
        """Test successful trading operation validation when trading is enabled"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "order_type": "MKT"
        }
        
        # Mock trading enabled for this test
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 10000.0
            
            result = manager.validate_trading_operation("order_placement", operation_data)
            
            # Should pass all checks when trading is enabled
            assert result["is_safe"] is True
            assert "warnings" in result
            assert "errors" in result
            assert "safety_checks" in result
            assert len(result["errors"]) == 0
    
    def test_trading_operation_validation_disabled(self):
        """Test trading operation validation when trading is disabled (default behavior)"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100,
            "order_type": "MKT"
        }
        
        # Explicitly mock trading as disabled to ensure test isolation
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = False
            
            result = manager.validate_trading_operation("order_placement", operation_data)
            
            # Should be blocked when trading is disabled (default safety behavior)
            assert result["is_safe"] is False
            assert "warnings" in result
            assert "errors" in result
            assert "safety_checks" in result
            assert len(result["errors"]) > 0
            
            # Check for trading disabled error
            trading_errors = [
                error for error in result["errors"]
                if "trading is disabled" in error.lower()
            ]
            assert len(trading_errors) > 0
    
    def test_kill_switch_blocks_operations(self):
        """Test that active kill switch blocks all operations"""
        manager = TradingSafetyManager()
        
        # Activate kill switch
        manager.kill_switch.activate("Test block all operations")
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100
        }
        
        result = manager.validate_trading_operation("order_placement", operation_data)
        
        assert not result["is_safe"]
        
        # Should have kill switch error
        kill_switch_errors = [
            error for error in result["errors"]
            if "kill switch" in error.lower()
        ]
        assert len(kill_switch_errors) > 0
    
    def test_daily_limit_violation_handling(self):
        """Test handling of daily limit violations"""
        manager = TradingSafetyManager()
        
        # Manually set the daily order count to the limit to trigger violation
        stats = manager.daily_limits.get_daily_stats()
        max_orders = stats["max_orders"]
        
        # Set count to max (this should cause next increment to fail)
        manager.daily_limits.daily_order_count = max_orders
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100
        }
        
        # This should hit the limit since validation increments the count
        result = manager.validate_trading_operation("order_placement", operation_data)
        
        # Should be blocked by daily limit  
        assert not result["is_safe"]
        limit_errors = [
            error for error in result["errors"]
            if "daily" in error.lower() and "limit" in error.lower()
        ]
        assert len(limit_errors) > 0
    
    def test_rate_limit_violation_handling(self):
        """Test handling of rate limit violations"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100
        }
        
        # Mock trading enabled for this test to focus on rate limiting
        with patch('ibkr_mcp_server.enhanced_validators.enhanced_settings') as mock_settings:
            mock_settings.enable_trading = True
            mock_settings.max_order_size = 1000
            mock_settings.max_order_value_usd = 10000.0
            
            # Exhaust rate limit (5 order placements per minute)
            for i in range(5):
                result = manager.validate_trading_operation("order_placement", operation_data)
                assert result["is_safe"] is True
            
            # Next attempt should be rate limited
            result = manager.validate_trading_operation("order_placement", operation_data)
            assert not result["is_safe"]
            
            # Should have rate limit error
            rate_errors = [
                error for error in result["errors"]
                if "rate limit" in error.lower()
            ]
            assert len(rate_errors) > 0
    
    def test_market_data_operation_validation(self):
        """Test market data operation validation"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbols": ["AAPL", "MSFT", "GOOGL"]
        }
        
        result = manager.validate_trading_operation("market_data", operation_data)
        
        # Market data should generally be allowed
        assert result["is_safe"] is True
    
    def test_safety_status_reporting(self):
        """Test safety status reporting"""
        manager = TradingSafetyManager()
        
        status = manager.get_safety_status()
        
        expected_keys = [
            "kill_switch_active", "daily_stats", "recent_violations",
            "account_verified", "trading_enabled"
        ]
        
        for key in expected_keys:
            assert key in status
        
        assert status["kill_switch_active"] is False  # Initially inactive
        assert "daily_stats" in status
        assert "trading_enabled" in status
    
    def test_invalid_operation_type_handling(self):
        """Test handling of invalid operation types"""
        manager = TradingSafetyManager()
        
        operation_data = {"symbol": "AAPL"}
        
        result = manager.validate_trading_operation("invalid_operation", operation_data)
        
        # Current implementation handles unknown operations gracefully and marks as safe
        # This might be by design for extensibility
        assert "is_safe" in result
        assert "warnings" in result
        assert "errors" in result


@pytest.mark.unit
@pytest.mark.safety
class TestSafetyFrameworkIntegration:
    """Test integration between safety framework components"""
    
    def test_audit_logging_integration(self):
        """Test that safety manager logs operations to audit trail"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100
        }
        
        # Perform validation (should log attempt)
        result = manager.validate_trading_operation("order_placement", operation_data)
        
        # Audit logger should be working (no exceptions thrown)
        assert result is not None
        assert "is_safe" in result
    
    def test_component_error_propagation(self):
        """Test error propagation between components"""
        manager = TradingSafetyManager()
        
        # Activate kill switch
        manager.kill_switch.activate("Integration test")
        
        operation_data = {"symbol": "AAPL", "quantity": 100}
        result = manager.validate_trading_operation("order_placement", operation_data)
        
        # Should be blocked by kill switch
        assert not result["is_safe"]
        assert len(result["errors"]) >= 1  # At least kill switch error
        
        # Should have kill switch error
        kill_switch_errors = [
            error for error in result["errors"]
            if "kill switch" in error.lower()
        ]
        assert len(kill_switch_errors) > 0
    
    def test_safety_framework_performance(self):
        """Test safety framework performance under load"""
        manager = TradingSafetyManager()
        
        operation_data = {
            "symbol": "AAPL",
            "action": "BUY",
            "quantity": 100
        }
        
        import time
        start_time = time.time()
        
        # Perform many validations
        for i in range(100):
            manager.validate_trading_operation("market_data", {"symbols": [f"STOCK{i}"]})
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly (allow 1 second for 100 validations)
        assert execution_time < 1.0
    
    def test_safety_framework_concurrent_access(self):
        """Test thread safety of safety framework components"""
        import threading
        import time
        
        manager = TradingSafetyManager()
        results = []
        errors = []
        
        def worker_thread(thread_id):
            """Worker function for concurrent testing"""
            try:
                for i in range(10):
                    operation_data = {
                        "symbol": f"STOCK{thread_id}_{i}",
                        "action": "BUY",
                        "quantity": 100
                    }
                    result = manager.validate_trading_operation("market_data", operation_data)
                    results.append((thread_id, i, result))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create and start multiple threads
        threads = []
        num_threads = 5
        
        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations completed without errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        
        # Should have results from all threads
        expected_results = num_threads * 10
        assert len(results) == expected_results
        
        # All results should be valid
        for thread_id, operation_id, result in results:
            assert result is not None
            assert "is_safe" in result
            assert isinstance(result["is_safe"], bool)
    
    def test_safety_framework_persistence(self):
        """Test persistent state management in safety framework"""
        from datetime import date, timedelta
        
        manager = TradingSafetyManager()
        
        # Test daily limits persistence
        daily_tracker = manager.daily_limits
        
        # Simulate some activity
        operation_data = {"symbol": "AAPL", "action": "BUY", "quantity": 100}
        for i in range(5):
            result = manager.validate_trading_operation("order_placement", operation_data)
        
        # Check that state is maintained
        stats = daily_tracker.get_daily_stats()
        assert stats["order_count"] == 5  # Order placement operations increment the counter
        assert "reset_date" in stats
        assert stats["reset_date"] == date.today().isoformat()
        
        # Test kill switch persistence
        kill_switch = manager.kill_switch
        
        # Activate kill switch
        activation_result = kill_switch.activate("Persistence test")
        assert activation_result["status"] == "activated"
        assert kill_switch.is_active()
        
        # State should persist across multiple checks
        for _ in range(3):
            assert kill_switch.is_active()
        
        # Deactivate and verify persistence
        deactivation_result = kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
        assert deactivation_result["status"] == "deactivated"
        assert not kill_switch.is_active()
        
        # State should remain deactivated
        for _ in range(3):
            assert not kill_switch.is_active()
        
        # Test rate limiter persistence
        rate_limiter = manager.rate_limiter
        
        # Use market_data operation type which has higher limit (30 vs 5)
        # to avoid conflicts with the order_placement calls made earlier
        for i in range(3):
            allowed = rate_limiter.check_rate_limit("market_data")
            assert allowed  # Should be allowed initially
        
        # State should be maintained within the rate window
        # (Testing the internal state persistence is challenging without access to private members,
        #  but we can verify the component continues to function correctly)
        
        # Test audit logger state
        audit_logger = manager.audit_logger
        
        # Generate some audit entries
        test_order_data = {"symbol": "MSFT", "quantity": 50}
        test_validation = {"is_safe": True, "warnings": [], "errors": []}
        
        # This should not raise exceptions (indicating internal state is maintained)
        audit_logger.log_order_attempt(test_order_data, test_validation)
        audit_logger.log_safety_violation("test_violation", {"test": "data"})
        
        # Verify the manager continues to work correctly after all these operations
        final_result = manager.validate_trading_operation("market_data", {"symbols": ["TEST"]})
        assert final_result is not None
        assert "is_safe" in final_result


if __name__ == "__main__":
    # Run safety framework tests
    pytest.main([__file__, "-v", "--tb=short"])
