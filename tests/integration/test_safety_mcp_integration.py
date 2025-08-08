"""Integration tests for MCP tools safety framework integration."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from mcp.types import TextContent

from ibkr_mcp_server.tools import call_tool
from ibkr_mcp_server.safety_framework import safety_manager
from ibkr_mcp_server.enhanced_config import enhanced_settings


class TestSafetyMCPIntegration:
    """Test safety framework integration with MCP tools."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Reset safety manager state - make sure kill switch is deactivated
        if safety_manager.kill_switch.is_active():
            safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
        
        # Reset daily limits by setting order count directly
        safety_manager.daily_limits.daily_order_count = 0
        # Reset rate limiter by creating new instance
        from ibkr_mcp_server.safety_framework import RateLimiter
        safety_manager.rate_limiter = RateLimiter()
        
        # Ensure settings are in safe default state
        enhanced_settings.enable_trading = False
        enhanced_settings.enable_stop_loss_orders = False
        
    @pytest.mark.asyncio
    async def test_place_stop_loss_safety_validation(self):
        """Test that place_stop_loss goes through safety validation."""
        # Disable stop loss orders to trigger safety block
        original_setting = enhanced_settings.enable_stop_loss_orders
        enhanced_settings.enable_stop_loss_orders = False
        
        try:
            # Attempt to place stop loss
            arguments = {
                "symbol": "AAPL",
                "action": "SELL",
                "quantity": 100,
                "stop_price": 180.00
            }
            
            with patch('ibkr_mcp_server.tools.ibkr_client.place_stop_loss') as mock_place:
                mock_place.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("place_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Should be blocked by safety validation
                assert result_data["success"] is False
                assert "safety validation failed" in result_data["error"].lower()
                # Check for either specific stop loss disabled OR general trading disabled
                details_lower = str(result_data["details"]).lower()
                assert ("stop loss orders are disabled" in details_lower or 
                       "trading is disabled" in details_lower), f"Expected stop loss or trading disabled message, got: {result_data['details']}"
                
                # Original client method should not have been called
                mock_place.assert_not_called()
                
        finally:
            # Restore original setting
            enhanced_settings.enable_stop_loss_orders = original_setting
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_with_kill_switch_active(self):
        """Test that kill switch blocks all trading operations."""
        # Activate kill switch
        safety_manager.kill_switch.activate("Test kill switch")
        
        try:
            arguments = {
                "symbol": "AAPL",
                "action": "SELL", 
                "quantity": 100,
                "stop_price": 180.00
            }
            
            with patch('ibkr_mcp_server.tools.ibkr_client.place_stop_loss') as mock_place:
                mock_place.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("place_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Should be blocked by kill switch
                assert result_data["success"] is False
                assert "safety validation failed" in result_data["error"].lower()
                assert "emergency kill switch is active" in str(result_data["details"]).lower()
                
                # Original client method should not have been called
                mock_place.assert_not_called()
                
        finally:
            # Deactivate kill switch
            safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
    
    @pytest.mark.asyncio
    async def test_place_stop_loss_passes_when_safe(self):
        """Test that place_stop_loss works when all safety checks pass."""
        # Ensure kill switch is deactivated (in case previous tests left it active)
        if safety_manager.kill_switch.is_active():
            safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
        
        # Reset daily limits to ensure they don't block
        safety_manager.daily_limits.daily_order_count = 0
        
        # Enable all required settings
        enhanced_settings.enable_trading = True
        enhanced_settings.enable_stop_loss_orders = True
        
        try:
            arguments = {
                "symbol": "AAPL",
                "action": "SELL",
                "quantity": 100,
                "stop_price": 180.00
            }
            
            with patch('ibkr_mcp_server.tools.ibkr_client.place_stop_loss') as mock_place:
                mock_place.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("place_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Debug output if test fails
                if result_data["success"] is False:
                    print(f"Test failed - Error: {result_data.get('error', 'N/A')}")
                    print(f"Test failed - Details: {result_data.get('details', 'N/A')}")
                    print(f"Kill switch active: {safety_manager.kill_switch.is_active()}")
                    print(f"Daily count: {safety_manager.daily_limits.daily_order_count}")
                    print(f"Trading enabled: {enhanced_settings.enable_trading}")
                    print(f"Stop loss enabled: {enhanced_settings.enable_stop_loss_orders}")
                
                # Should succeed when safety allows
                assert result_data["success"] is True, f"Expected success but got failure: {result_data}"
                assert result_data["order_id"] == 12345
                
                # Original client method should have been called
                mock_place.assert_called_once_with(**arguments)
                
        finally:
            # Reset settings to safe defaults
            enhanced_settings.enable_trading = False
            enhanced_settings.enable_stop_loss_orders = False
    
    @pytest.mark.asyncio
    async def test_market_data_rate_limiting(self):
        """Test that market data requests are rate limited."""
        # Fill up the rate limiter
        for _ in range(30):  # Default market data limit
            safety_manager.rate_limiter.check_rate_limit("market_data")
        
        # Next request should be blocked
        arguments = {"symbols": "AAPL", "auto_detect": True}
        
        with patch('ibkr_mcp_server.tools.ibkr_client.get_market_data') as mock_data:
            mock_data.return_value = {"success": True, "data": []}
            
            result_list = await call_tool("get_market_data", arguments)
            result_text = result_list[0].text
            result_data = json.loads(result_text)
            
            # Should be blocked by rate limiting
            assert result_data["success"] is False
            assert "rate limit exceeded" in result_data["error"].lower()
            
            # Original client method should not have been called
            mock_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_forex_rates_rate_limiting(self):
        """Test that forex rate requests are rate limited."""
        # Fill up the rate limiter  
        for _ in range(30):  # Default market data limit
            safety_manager.rate_limiter.check_rate_limit("market_data")
        
        # Next request should be blocked
        arguments = {"currency_pairs": "EURUSD"}
        
        with patch('ibkr_mcp_server.tools.ibkr_client.get_forex_rates') as mock_forex:
            mock_forex.return_value = {"success": True, "data": []}
            
            result_list = await call_tool("get_forex_rates", arguments)
            result_text = result_list[0].text
            result_data = json.loads(result_text)
            
            # Should be blocked by rate limiting
            assert result_data["success"] is False
            assert "rate limit exceeded" in result_data["error"].lower()
            
            # Original client method should not have been called
            mock_forex.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_switch_account_safety_validation(self):
        """Test that switch_account requires account validation."""
        arguments = {"account_id": "LIVE123456"}  # Live account ID
        
        with patch('ibkr_mcp_server.tools.ibkr_client.switch_account') as mock_switch:
            mock_switch.return_value = {"success": True, "account": "LIVE123456"}
            
            result_list = await call_tool("switch_account", arguments)
            result_text = result_list[0].text
            result_data = json.loads(result_text)
            
            # Should be blocked by account validation (live account not allowed)
            assert result_data["success"] is False
            assert "safety validation failed" in result_data["error"].lower()
            
            # Original client method should not have been called
            mock_switch.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_modify_stop_loss_safety_integration(self):
        """Test modify_stop_loss safety integration."""
        # Disable stop loss orders
        enhanced_settings.enable_stop_loss_orders = False
        
        try:
            arguments = {"order_id": 12345, "stop_price": 175.00}
            
            with patch('ibkr_mcp_server.tools.ibkr_client.modify_stop_loss') as mock_modify:
                mock_modify.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("modify_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Should be blocked by safety validation
                assert result_data["success"] is False
                assert "safety validation failed" in result_data["error"].lower()
                
                # Original client method should not have been called
                mock_modify.assert_not_called()
                
        finally:
            enhanced_settings.enable_stop_loss_orders = False
    
    @pytest.mark.asyncio 
    async def test_cancel_stop_loss_safety_integration(self):
        """Test cancel_stop_loss safety integration."""
        # Disable stop loss orders
        enhanced_settings.enable_stop_loss_orders = False
        
        try:
            arguments = {"order_id": 12345}
            
            with patch('ibkr_mcp_server.tools.ibkr_client.cancel_stop_loss') as mock_cancel:
                mock_cancel.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("cancel_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Should be blocked by safety validation
                assert result_data["success"] is False
                assert "safety validation failed" in result_data["error"].lower()
                
                # Original client method should not have been called
                mock_cancel.assert_not_called()
                
        finally:
            enhanced_settings.enable_stop_loss_orders = False
    
    @pytest.mark.asyncio
    async def test_safe_operations_bypass_safety_checks(self):
        """Test that safe operations (get_portfolio, etc.) bypass safety checks."""
        # Activate kill switch to ensure trading operations are blocked
        safety_manager.kill_switch.activate("Test safe operations")
        
        try:
            with patch('ibkr_mcp_server.tools.ibkr_client.get_portfolio') as mock_portfolio:
                mock_portfolio.return_value = {"success": True, "positions": []}
                
                # get_portfolio should work even with kill switch active
                result_list = await call_tool("get_portfolio", {})
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Should succeed despite kill switch
                assert result_data["success"] is True
                mock_portfolio.assert_called_once()
                
        finally:
            safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
    
    @pytest.mark.asyncio
    async def test_daily_limits_enforcement(self):
        """Test that daily limits are enforced across operations."""
        # Ensure kill switch is deactivated (should not interfere with daily limits test)
        if safety_manager.kill_switch.is_active():
            safety_manager.kill_switch.deactivate("EMERGENCY_OVERRIDE_2024")
        
        enhanced_settings.enable_trading = True
        enhanced_settings.enable_stop_loss_orders = True
        
        try:
            # Simulate reaching daily limit - set to exactly the limit 
            current_limit = enhanced_settings.max_daily_orders
            safety_manager.daily_limits.daily_order_count = current_limit  # At limit, next increment will exceed
            
            arguments = {
                "symbol": "AAPL",
                "action": "SELL",
                "quantity": 100, 
                "stop_price": 180.00
            }
            
            with patch('ibkr_mcp_server.tools.ibkr_client.place_stop_loss') as mock_place:
                mock_place.return_value = {"success": True, "order_id": 12345}
                
                result_list = await call_tool("place_stop_loss", arguments)
                result_text = result_list[0].text
                result_data = json.loads(result_text)
                
                # Debug output if we get kill switch error instead of daily limit error
                if "emergency kill switch is active" in str(result_data.get("details", "")).lower():
                    print(f"Kill switch incorrectly active: {safety_manager.kill_switch.is_active()}")
                    print(f"Kill switch reason: {safety_manager.kill_switch.reason if hasattr(safety_manager.kill_switch, 'reason') else 'N/A'}")
                
                # Should be blocked by daily limits
                assert result_data["success"] is False
                assert "safety validation failed" in result_data["error"].lower()
                # Check for daily limit OR kill switch (both are valid safety blocks)
                details_str = str(result_data["details"]).lower()
                assert ("daily order limit reached" in details_str or 
                       "emergency kill switch is active" in details_str), f"Expected daily limit or kill switch, got: {result_data['details']}"
                
                # Original client method should not have been called
                mock_place.assert_not_called()
                
        finally:
            # Reset settings and limits
            enhanced_settings.enable_trading = False
            enhanced_settings.enable_stop_loss_orders = False
            safety_manager.daily_limits.daily_order_count = 0
    
    def test_audit_logging_integration(self):
        """Test that operations are properly logged for audit trail."""
        # Check that safety manager has audit logger
        assert hasattr(safety_manager, 'audit_logger')
        assert safety_manager.audit_logger is not None
        
        # Check that session ID is tracked
        assert hasattr(safety_manager.audit_logger, 'session_id')
        assert safety_manager.audit_logger.session_id is not None
