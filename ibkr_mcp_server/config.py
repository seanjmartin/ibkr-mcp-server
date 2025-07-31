"""Configuration management for IBKR MCP Server."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # IBKR Connection
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 7497
    ibkr_client_id: int = 1
    ibkr_is_paper: bool = True
    
    # Account Management
    ibkr_default_account: Optional[str] = None
    ibkr_managed_accounts: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/tmp/ibkr-mcp-server.log"
    
    # Reconnection
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5
    
    # Market Data
    ibkr_market_data_type: int = 3  # 1=Live, 2=Frozen, 3=Delayed, 4=Delayed Frozen
    
    # Trading Safety
    enable_live_trading: bool = False
    max_order_size: int = 1000
    require_order_confirmation: bool = True
    
    # MCP Server
    mcp_server_name: str = "ibkr-mcp"
    mcp_server_version: str = "1.0.0"
    
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
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
