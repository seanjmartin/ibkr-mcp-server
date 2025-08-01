"""Safety framework and audit logging for IBKR MCP Server trading operations."""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import deque, defaultdict

from .enhanced_config import enhanced_settings
from .enhanced_validators import (
    TradingSafetyValidator, SafetyViolationError, DailyLimitError
)


# ========================================
# AUDIT LOGGING SYSTEM
# ========================================

class TradingAuditLogger:
    """Comprehensive audit logging for all trading operations."""
    
    def __init__(self):
        self.logger = self._setup_audit_logger()
        self.session_id = f"session_{int(time.time())}"
    
    def _setup_audit_logger(self) -> logging.Logger:
        """Setup dedicated audit logger."""
        audit_logger = logging.getLogger('trading_audit')
        audit_logger.setLevel(logging.INFO)
        
        # Ensure log directory exists
        log_file = Path(enhanced_settings.audit_log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler for audit logs
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s|%(levelname)s|%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        if not audit_logger.handlers:
            audit_logger.addHandler(handler)
        
        return audit_logger
    
    def log_order_attempt(self, order_data: Dict, validation_result: Dict):
        """Log order placement attempt."""
        audit_entry = {
            "event_type": "ORDER_ATTEMPT",
            "order_data": self._sanitize_order_data(order_data),
            "validation_result": validation_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"ORDER_ATTEMPT|{json.dumps(audit_entry)}")
    
    def log_order_placement(self, order_data: Dict, ibkr_response: Dict):
        """Log successful order placement."""
        audit_entry = {
            "event_type": "ORDER_PLACED",
            "order_data": self._sanitize_order_data(order_data),
            "ibkr_response": self._sanitize_ibkr_response(ibkr_response),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"ORDER_PLACED|{json.dumps(audit_entry)}")
    
    def log_order_modification(self, order_id: int, changes: Dict):
        """Log order modification."""
        audit_entry = {
            "event_type": "ORDER_MODIFIED",
            "order_id": order_id,
            "changes": changes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"ORDER_MODIFIED|{json.dumps(audit_entry)}")
    
    def log_order_cancellation(self, order_id: int, reason: str):
        """Log order cancellation."""
        audit_entry = {
            "event_type": "ORDER_CANCELLED",
            "order_id": order_id,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"ORDER_CANCELLED|{json.dumps(audit_entry)}")
    
    def log_safety_violation(self, violation_type: str, details: Dict):
        """Log safety violations."""
        audit_entry = {
            "event_type": "SAFETY_VIOLATION",
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.warning(f"SAFETY_VIOLATION|{json.dumps(audit_entry)}")
    
    def log_system_event(self, event_type: str, details: Dict):
        """Log system events."""
        audit_entry = {
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"SYSTEM_EVENT|{json.dumps(audit_entry)}")
    
    def log_market_data_request(self, symbols: List[str], request_type: str):
        """Log market data requests."""
        audit_entry = {
            "event_type": "MARKET_DATA_REQUEST",
            "symbols": symbols,
            "request_type": request_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id
        }
        
        self.logger.info(f"MARKET_DATA|{json.dumps(audit_entry)}")
    
    def _sanitize_order_data(self, order_data: Dict) -> Dict:
        """Sanitize order data for logging (remove sensitive info)."""
        # Create a copy to avoid modifying original
        sanitized = order_data.copy()
        
        # Remove any potentially sensitive data
        sensitive_fields = ['api_key', 'password', 'token']
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***REDACTED***"
        
        return sanitized
    
    def _sanitize_ibkr_response(self, response: Dict) -> Dict:
        """Sanitize IBKR response for logging."""
        # Keep only essential fields
        sanitized = {
            "order_id": response.get("order_id"),
            "status": response.get("status"),
            "timestamp": response.get("timestamp")
        }
        return sanitized


# ========================================
# DAILY LIMITS TRACKER
# ========================================

class DailyLimitsTracker:
    """Track daily trading limits and restrictions."""
    
    def __init__(self):
        self.daily_order_count = 0
        self.daily_volume = 0.0
        self.last_reset_date = datetime.now().date()
        self.order_history = deque(maxlen=100)  # Keep last 100 orders
        self.violation_count = 0
    
    def check_and_increment_order_count(self) -> None:
        """Check daily order limit and increment counter."""
        self._reset_if_new_day()
        
        if self.daily_order_count >= enhanced_settings.max_daily_orders:
            raise DailyLimitError(
                f"Daily order limit reached: {self.daily_order_count}/{enhanced_settings.max_daily_orders}"
            )
        
        self.daily_order_count += 1
        self.order_history.append({
            'timestamp': datetime.now(timezone.utc),
            'count': self.daily_order_count
        })
    
    def add_order_volume(self, volume: float) -> None:
        """Add to daily volume tracking."""
        self._reset_if_new_day()
        self.daily_volume += volume
    
    def get_daily_stats(self) -> Dict:
        """Get current daily statistics."""
        self._reset_if_new_day()
        
        return {
            'order_count': self.daily_order_count,
            'max_orders': enhanced_settings.max_daily_orders,
            'remaining_orders': enhanced_settings.max_daily_orders - self.daily_order_count,
            'daily_volume': self.daily_volume,
            'violation_count': self.violation_count,
            'reset_date': self.last_reset_date.isoformat()
        }
    
    def _reset_if_new_day(self) -> None:
        """Reset counters if it's a new day."""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_order_count = 0
            self.daily_volume = 0.0
            self.last_reset_date = today
            self.violation_count = 0


# ========================================
# RATE LIMITER
# ========================================

class RateLimiter:
    """Advanced rate limiting for API calls."""
    
    def __init__(self):
        self.request_history = defaultdict(deque)
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, operation_type: str) -> bool:
        """Check if operation is within rate limits."""
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self.last_cleanup > 60:  # Every minute
            self._cleanup_old_entries()
        
        history = self.request_history[operation_type]
        
        # Check specific limits based on operation type
        if operation_type == 'order_placement':
            limit = enhanced_settings.max_orders_per_minute
            window = 60  # 1 minute window
        elif operation_type == 'market_data':
            limit = enhanced_settings.max_market_data_requests_per_minute
            window = 60
        else:
            limit = 10  # Default limit
            window = 60
        
        # Count requests in the window
        cutoff_time = now - window
        recent_requests = sum(1 for timestamp in history if timestamp > cutoff_time)
        
        if recent_requests >= limit:
            return False
        
        # Record this request
        history.append(now)
        
        # Keep only recent entries
        while history and history[0] <= cutoff_time:
            history.popleft()
        
        return True
    
    def _cleanup_old_entries(self):
        """Remove old entries from request history."""
        now = time.time()
        cutoff = now - 3600  # Keep last hour
        
        for operation_type in list(self.request_history.keys()):
            history = self.request_history[operation_type]
            while history and history[0] <= cutoff:
                history.popleft()
            
            # Remove empty histories
            if not history:
                del self.request_history[operation_type]
        
        self.last_cleanup = now


# ========================================
# EMERGENCY KILL SWITCH
# ========================================

class EmergencyKillSwitch:
    """Emergency system to halt all trading operations."""
    
    def __init__(self):
        self.is_activated = False
        self.activation_reason = None
        self.activation_time = None
        self.logger = logging.getLogger(__name__)
    
    def activate(self, reason: str = "Manual activation") -> Dict:
        """Activate emergency kill switch."""
        if self.is_activated:
            return {
                "status": "already_activated",
                "reason": self.activation_reason,
                "activated_at": self.activation_time
            }
        
        self.is_activated = True
        self.activation_reason = reason
        self.activation_time = datetime.now(timezone.utc).isoformat()
        
        self.logger.critical(f"EMERGENCY KILL SWITCH ACTIVATED: {reason}")
        
        # In a full implementation, this would:
        # 1. Cancel all open orders
        # 2. Disable all trading functionality
        # 3. Send emergency notifications
        # 4. Create incident report
        
        return {
            "status": "activated",
            "reason": reason,
            "activated_at": self.activation_time,
            "message": "All trading operations have been halted"
        }
    
    def is_active(self) -> bool:
        """Check if kill switch is active."""
        return self.is_activated
    
    def deactivate(self, override_code: str = None) -> Dict:
        """Deactivate kill switch (requires override)."""
        if not self.is_activated:
            return {"status": "not_activated"}
        
        # In production, this would require proper authentication
        if override_code != "EMERGENCY_OVERRIDE_2024":
            return {"status": "invalid_override_code"}
        
        self.is_activated = False
        deactivation_time = datetime.now(timezone.utc).isoformat()
        
        self.logger.warning(f"KILL_SWITCH_DEACTIVATED at {deactivation_time}")
        
        return {
            "status": "deactivated",
            "deactivated_at": deactivation_time,
            "was_active_for": f"Activated at {self.activation_time}",
            "note": "Manual re-enabling of trading features may be required"
        }


# ========================================
# COMPREHENSIVE SAFETY MANAGER
# ========================================

class TradingSafetyManager:
    """Comprehensive trading safety and risk management."""
    
    def __init__(self):
        self.audit_logger = TradingAuditLogger()
        self.daily_limits = DailyLimitsTracker()
        self.rate_limiter = RateLimiter()
        self.kill_switch = EmergencyKillSwitch()
        
        # Safety state tracking
        self.safety_violations = deque(maxlen=50)
        self.account_verified = False
        self.last_account_check = None
    
    def validate_trading_operation(self, operation_type: str, operation_data: Dict) -> Dict:
        """Comprehensive validation for any trading operation."""
        validation_result = {
            "is_safe": False,
            "warnings": [],
            "errors": [],
            "safety_checks": []
        }
        
        try:
            # Kill switch check
            if self.kill_switch.is_active():
                validation_result["errors"].append("Emergency kill switch is active")
                return validation_result
            
            # Rate limiting check
            if not self.rate_limiter.check_rate_limit(operation_type):
                validation_result["errors"].append(f"Rate limit exceeded for {operation_type}")
                return validation_result
            
            # Daily limits check
            try:
                self.daily_limits.check_and_increment_order_count()
                validation_result["safety_checks"].append("Daily limits OK")
            except DailyLimitError as e:
                validation_result["errors"].append(str(e))
                return validation_result
            
            # Account safety verification
            account_id = operation_data.get('account_id')
            if account_id:
                try:
                    TradingSafetyValidator.validate_paper_account(account_id)
                    validation_result["safety_checks"].append("Account verification OK")
                except SafetyViolationError as e:
                    validation_result["errors"].append(str(e))
                    return validation_result
            
            # Operation-specific validation
            if operation_type == 'order_placement':
                self._validate_order_operation(operation_data, validation_result)
            elif operation_type == 'stop_loss_placement':
                self._validate_stop_loss_operation(operation_data, validation_result)
            elif operation_type == 'order_modification':
                self._validate_order_modification(operation_data, validation_result)
            elif operation_type == 'order_cancellation':
                self._validate_order_cancellation(operation_data, validation_result)
            elif operation_type == 'market_data':
                self._validate_market_data_operation(operation_data, validation_result)
            
            # If we get here with no errors, operation is safe
            if not validation_result["errors"]:
                validation_result["is_safe"] = True
                validation_result["safety_checks"].append("All safety checks passed")
            
        except Exception as e:
            validation_result["errors"].append(f"Safety validation error: {str(e)}")
            self.audit_logger.log_system_event("SAFETY_VALIDATION_ERROR", {
                "error": str(e),
                "operation_type": operation_type
            })
        
        # Log the validation attempt
        self.audit_logger.log_order_attempt(operation_data, validation_result)
        
        # Track safety violations
        if validation_result["errors"]:
            self.safety_violations.append({
                "timestamp": datetime.now(timezone.utc),
                "operation_type": operation_type,
                "errors": validation_result["errors"]
            })
        
        return validation_result
    
    def _validate_order_operation(self, order_data: Dict, validation_result: Dict):
        """Validate order-specific safety requirements."""
        try:
            # Basic order validation
            TradingSafetyValidator.validate_trading_enabled()
            
            quantity = order_data.get('quantity', 0)
            TradingSafetyValidator.validate_order_size(quantity)
            
            # Estimate order value
            price = order_data.get('price', order_data.get('stop_price', 100))
            estimated_value = quantity * price
            TradingSafetyValidator.validate_order_value(estimated_value)
            
            validation_result["safety_checks"].append("Order size and value validation OK")
            
        except Exception as e:
            validation_result["errors"].append(f"Order validation failed: {str(e)}")
    
    def _validate_stop_loss_operation(self, order_data: Dict, validation_result: Dict):
        """Validate stop loss order specific safety requirements."""
        try:
            # Import here to avoid circular imports
            from .enhanced_validators import StopLossValidator
            
            # Validate stop loss orders are enabled
            StopLossValidator.validate_stop_loss_enabled()
            
            # Basic order validation  
            quantity = order_data.get('quantity', 0)
            TradingSafetyValidator.validate_order_size(quantity)
            
            # Estimate order value
            price = order_data.get('price', order_data.get('stop_price', 100))
            estimated_value = quantity * price
            TradingSafetyValidator.validate_order_value(estimated_value)
            
            # Validate stop loss specific parameters
            StopLossValidator.validate_stop_loss_order(order_data)
            
            validation_result["safety_checks"].append("Stop loss order validation OK")
            
        except Exception as e:
            validation_result["errors"].append(f"Stop loss validation failed: {str(e)}")
    
    def _validate_order_modification(self, order_data: Dict, validation_result: Dict):
        """Validate order modification safety requirements."""
        try:
            from .enhanced_validators import StopLossValidator
            
            # For stop loss modifications, check if stop loss orders are enabled
            if 'stop_price' in order_data or 'trail_percent' in order_data:
                StopLossValidator.validate_stop_loss_enabled()
            
            validation_result["safety_checks"].append("Order modification validation OK")
            
        except Exception as e:
            validation_result["errors"].append(f"Order modification validation failed: {str(e)}")
    
    def _validate_order_cancellation(self, order_data: Dict, validation_result: Dict):
        """Validate order cancellation safety requirements."""
        try:
            from .enhanced_validators import StopLossValidator 
            
            # For stop loss cancellations, check if stop loss orders are enabled
            # This allows cancelling existing stop losses even if new ones are disabled
            validation_result["safety_checks"].append("Order cancellation validation OK")
            
        except Exception as e:
            validation_result["errors"].append(f"Order cancellation validation failed: {str(e)}")
    
    def _validate_market_data_operation(self, data_request: Dict, validation_result: Dict):
        """Validate market data request safety."""
        symbols = data_request.get('symbols', [])
        if len(symbols) > 50:  # Reasonable limit
            validation_result["warnings"].append(f"Large symbol request: {len(symbols)} symbols")
        
        validation_result["safety_checks"].append("Market data request validation OK")
    
    def get_safety_status(self) -> Dict:
        """Get comprehensive safety system status."""
        return {
            "kill_switch_active": self.kill_switch.is_active(),
            "daily_stats": self.daily_limits.get_daily_stats(),
            "recent_violations": len(self.safety_violations),
            "account_verified": self.account_verified,
            "trading_enabled": enhanced_settings.enable_trading,
            "forex_enabled": enhanced_settings.enable_forex_trading,
            "international_enabled": enhanced_settings.enable_international_trading,
            "stop_loss_enabled": enhanced_settings.enable_stop_loss_orders,
            "session_id": self.audit_logger.session_id
        }


# ========================================
# GLOBAL SAFETY MANAGER INSTANCE
# ========================================

# Global safety manager instance
safety_manager = TradingSafetyManager()
