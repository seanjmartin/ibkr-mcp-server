"""Enhanced configuration for IBKR MCP Server with comprehensive trading capabilities."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class EnhancedSettings(BaseSettings):
    """Enhanced application settings with comprehensive trading safety and feature controls."""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    # ========================================
    # IBKR CONNECTION SETTINGS
    # ========================================
    
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 7497
    ibkr_client_id: int = 1
    ibkr_is_paper: bool = True
    
    # Account Management
    ibkr_default_account: Optional[str] = None
    ibkr_managed_accounts: Optional[str] = None
    
    # Reconnection
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5
    
    # Market Data
    ibkr_market_data_type: int = 3  # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed Frozen
    
    # ========================================
    # ENHANCED TRADING SAFETY FRAMEWORK
    # ========================================
    
    # Master trading controls (OFF by default for safety)
    enable_trading: bool = False  # Master switch - must be explicitly enabled
    enable_live_trading: bool = False  # Legacy compatibility field
    enable_forex_trading: bool = False
    enable_international_trading: bool = False
    enable_stop_loss_orders: bool = False
    
    # Account safety verification
    require_paper_account_verification: bool = True
    allowed_account_prefixes: List[str] = ["DU", "DUH"]  # Paper account prefixes
    
    # Order size and value limits
    max_order_size: int = 1000  # Maximum shares/units per order
    max_order_value_usd: float = 10000.0  # Maximum USD value per order
    max_daily_orders: int = 50  # Maximum orders per day
    max_stop_loss_orders: int = 25  # Maximum concurrent stop losses
    
    # Position and portfolio limits
    max_position_size_pct: float = 5.0  # Max % of portfolio per position
    max_portfolio_value_at_risk: float = 0.20  # Max 20% of portfolio at risk
    
    # Order confirmation and preview
    require_order_confirmation: bool = True
    enable_order_preview: bool = True
    min_stop_distance_pct: float = 1.0  # Minimum 1% stop distance
    max_trail_percent: float = 25.0  # Maximum trailing stop percentage
    
    # Rate limiting and API usage
    max_orders_per_minute: int = 5
    max_market_data_requests_per_minute: int = 30
    api_rate_limit_buffer: float = 0.8  # Use 80% of IBKR limits
    
    # Time-based trading restrictions
    trading_hours_only: bool = True
    allow_weekend_trading: bool = False
    max_session_duration_hours: int = 12
    
    # Emergency controls
    enable_kill_switch: bool = True
    emergency_contact_email: str = ""
    auto_cancel_orders_on_disconnect: bool = True
    
    # ========================================
    # FOREX TRADING CONFIGURATION
    # ========================================
    
    # Forex rate caching and refresh
    forex_rate_cache_seconds: int = 5
    supported_forex_pairs: List[str] = [
        # Major pairs
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
        # Cross pairs  
        "EURGBP", "EURJPY", "GBPJPY", "CHFJPY", "EURCHF", "AUDJPY", "CADJPY"
    ]
    default_forex_lot_size: int = 25000
    forex_exchange: str = "IDEALPRO"  # Default forex exchange
    
    # ========================================
    # INTERNATIONAL TRADING CONFIGURATION
    # ========================================
    
    # Symbol resolution and market data
    auto_detect_international_symbols: bool = True
    international_market_data_timeout: int = 10
    validate_trading_hours: bool = True
    
    # Supported currencies for international trading
    supported_currencies: List[str] = [
        "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "HKD", "KRW", "DKK"
    ]
    
    # Exchange-specific settings
    default_us_exchange: str = "SMART"
    default_european_exchange: str = "SMART"
    default_asian_exchange: str = "SMART"
    
    # ========================================
    # STOP LOSS CONFIGURATION
    # ========================================
    
    # Default stop loss settings
    default_stop_loss_tif: str = "GTC"  # Good Till Cancelled
    allow_trailing_stops: bool = True
    min_stop_distance_pct: float = 0.5  # Minimum 0.5% stop distance
    
    # Bracket order settings
    enable_bracket_orders: bool = True
    default_bracket_tif: str = "GTC"
    
    # ========================================
    # PERFORMANCE AND CACHING
    # ========================================
    
    # Caching intervals
    market_data_cache_seconds: int = 2
    order_status_refresh_seconds: int = 1
    symbol_resolution_cache_hours: int = 24
    
    # Connection and retry settings
    connection_retry_attempts: int = 3
    connection_timeout_seconds: int = 10
    
    # ========================================
    # MONITORING AND AUDIT
    # ========================================
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/tmp/ibkr-mcp-server.log"
    
    # Audit and compliance logging
    enable_audit_logging: bool = True
    audit_log_file: str = "/tmp/ibkr-trading-audit.log"
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    performance_log_file: str = "/tmp/ibkr-performance.log"
    
    # Health check settings
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 60
    
    # ========================================
    # MCP SERVER SETTINGS
    # ========================================
    
    mcp_server_name: str = "ibkr-mcp"
    mcp_server_version: str = "2.0.0"  # Updated for enhanced version
    
    # ========================================
    # VALIDATORS
    # ========================================
    
    @field_validator('ibkr_managed_accounts')
    @classmethod
    def parse_managed_accounts(cls, v) -> Optional[List[str]]:
        """Parse comma-separated managed accounts."""
        if v:
            return [acc.strip() for acc in v.split(',') if acc.strip()]
        return None
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "IBKR_"  # Environment variables should be prefixed with IBKR_
    }


# Global enhanced settings instance
enhanced_settings = EnhancedSettings()
