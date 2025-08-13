# IBKR MCP Server - Deployment & Configuration Guide

## Quick Start

### **Prerequisites**
- Python 3.9+ (tested with 3.13.2)
- Interactive Brokers account (paper or live)
- IB Gateway or TWS installed
- Claude Desktop (for MCP integration)

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd ibkr-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Configuration**
1. Copy `.env.example` to `.env`
2. Configure IBKR connection settings
3. Set safety parameters
4. Configure Claude Desktop MCP integration

## Environment Configuration

### **Basic Settings (.env)**
```bash
# IBKR Connection
IBKR_HOST=127.0.0.1
IBKR_PORT=7497                    # Paper trading: 7497, Live: 7496
IBKR_CLIENT_ID=1
IBKR_IS_PAPER=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ibkr-mcp-server.log

# Safety Settings (Production)
ENABLE_TRADING=false              # Master safety switch
ENABLE_FOREX_TRADING=false
ENABLE_INTERNATIONAL_TRADING=false
ENABLE_STOP_LOSS_ORDERS=false
REQUIRE_PAPER_ACCOUNT_VERIFICATION=true
```

### **Development Configuration**
```bash
# Development settings for safe testing
ENABLE_TRADING=true
ENABLE_FOREX_TRADING=true
ENABLE_INTERNATIONAL_TRADING=true
ENABLE_STOP_LOSS_ORDERS=true
REQUIRE_PAPER_ACCOUNT_VERIFICATION=true
MAX_ORDER_SIZE=100
MAX_DAILY_ORDERS=10
```

### **Production Configuration**
```bash
# Production settings with enhanced safety
ENABLE_TRADING=true
ENABLE_FOREX_TRADING=true
ENABLE_INTERNATIONAL_TRADING=true
ENABLE_STOP_LOSS_ORDERS=true
REQUIRE_PAPER_ACCOUNT_VERIFICATION=false  # Allow live trading
MAX_ORDER_SIZE=1000
MAX_ORDER_VALUE_USD=50000
MAX_DAILY_ORDERS=100
ENABLE_KILL_SWITCH=true
ENABLE_AUDIT_LOGGING=true
```

## IBKR Setup

### **Paper Trading Setup (Recommended for Testing)**
1. **IB Gateway Configuration:**
   - Mode: Paper Trading
   - Port: 7497
   - API Settings: Enable "ActiveX and Socket Clients"
   - Trusted IPs: Add 127.0.0.1
   - Socket port: 7497

2. **Account Setup:**
   - Paper account automatically created
   - Virtual funds: $1,000,000
   - All markets accessible
   - No real money at risk

### **Live Trading Setup (Production)**
1. **Account Requirements:**
   - Funded IBKR account
   - Market data subscriptions (optional but recommended)
   - API trading permissions enabled

2. **IB Gateway Configuration:**
   - Mode: Live Trading
   - Port: 7496
   - API Settings: Enable "ActiveX and Socket Clients"
   - Trusted IPs: Add production server IP
   - Socket port: 7496

3. **Market Data Subscriptions:**
   - US Securities Snapshot and Futures Value Bundle
   - European equity data (for European stocks)
   - Asian equity data (for Asian stocks)
   - Forex data (usually included)

## Claude Desktop Integration

### **MCP Configuration**
Add to Claude Desktop configuration file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ibkr": {
      "command": "C:\\path\\to\\ibkr-mcp-server\\venv\\Scripts\\python.exe",
      "args": ["-m", "ibkr_mcp_server.main"],
      "cwd": "C:\\path\\to\\ibkr-mcp-server",
      "env": {
        "LOG_FILE": "C:\\path\\to\\ibkr-mcp-server\\logs\\ibkr-mcp-server.log",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### **Restart Claude Desktop**
After configuration, restart Claude Desktop to load the MCP server.

## Safety Configuration

### **Master Safety Controls**
```python
# All trading disabled by default - must be explicitly enabled
enable_trading: bool = False                    # Master OFF switch
enable_forex_trading: bool = False
enable_international_trading: bool = False
enable_stop_loss_orders: bool = False
```

### **Account Protection**
```python
# Prevent accidental live trading
require_paper_account_verification: bool = True
allowed_account_prefixes: List[str] = ["DU", "DUH"]  # Paper prefixes
```

### **Order Limits**
```python
# Configurable safety limits
max_order_size: int = 1000              # Maximum shares/units per order
max_order_value_usd: float = 10000.0    # Maximum USD value per order
max_daily_orders: int = 50              # Maximum orders per day
max_stop_loss_orders: int = 25          # Maximum concurrent stop losses
```

### **Risk Management**
```python
# Portfolio protection
max_position_size_pct: float = 5.0      # Max % of portfolio per position
max_portfolio_value_at_risk: float = 0.20  # Max 20% of portfolio at risk
min_stop_distance_pct: float = 1.0      # Minimum 1% stop distance
```

### **Emergency Controls**
```python
# Crisis management
enable_kill_switch: bool = True
auto_cancel_orders_on_disconnect: bool = True
emergency_contact_email: str = "your-email@example.com"
```

## Operational Modes

### **Development Mode**
For safe development and testing:
```bash
IBKR_IS_PAPER=true
ENABLE_TRADING=true
REQUIRE_PAPER_ACCOUNT_VERIFICATION=true
MAX_ORDER_SIZE=100
LOG_LEVEL=DEBUG
```

### **Staging Mode**  
For pre-production testing:
```bash
IBKR_IS_PAPER=true
ENABLE_TRADING=true
ENABLE_FOREX_TRADING=true
ENABLE_INTERNATIONAL_TRADING=true
ENABLE_STOP_LOSS_ORDERS=true
MAX_ORDER_SIZE=500
ENABLE_AUDIT_LOGGING=true
```

### **Production Mode**
For live trading:
```bash
IBKR_IS_PAPER=false
ENABLE_TRADING=true
ENABLE_FOREX_TRADING=true
ENABLE_INTERNATIONAL_TRADING=true
ENABLE_STOP_LOSS_ORDERS=true
REQUIRE_PAPER_ACCOUNT_VERIFICATION=false
MAX_ORDER_SIZE=1000
MAX_ORDER_VALUE_USD=50000
ENABLE_KILL_SWITCH=true
ENABLE_AUDIT_LOGGING=true
```

## Monitoring & Logging

### **Log Configuration**
```bash
# Logging settings
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/ibkr-mcp-server.log
LOG_MAX_BYTES=10485760                  # 10MB
LOG_BACKUP_COUNT=5
```

### **Audit Logging**
When `ENABLE_AUDIT_LOGGING=true`, all trading operations are logged:
- Order attempts and placements
- Order modifications and cancellations
- Safety violations
- System events and errors

### **Log Analysis**
```bash
# View recent activity
tail -f logs/ibkr-mcp-server.log

# Search for trading activity
grep "TRADING_AUDIT" logs/ibkr-mcp-server.log

# Check for safety violations
grep "SAFETY_VIOLATION" logs/ibkr-mcp-server.log
```

## Performance Tuning

### **API Rate Limiting**
```python
# Respect IBKR API limits
max_orders_per_minute: int = 5
max_market_data_requests_per_minute: int = 30
api_rate_limit_buffer: float = 0.8      # Use 80% of limits
```

### **Caching Configuration**
```python
# Performance optimization
forex_rate_cache_seconds: int = 5       # Forex rate cache duration
market_data_cache_seconds: int = 2      # Market data cache duration
order_status_refresh_seconds: int = 1   # Order status refresh rate
```

### **Connection Management**
```python
# Connection reliability
connection_retry_attempts: int = 3
max_session_duration_hours: int = 12
auto_reconnect_on_disconnect: bool = True
```

## Troubleshooting

### **Common Issues**

**Connection Refused:**
- Verify IB Gateway is running
- Check port configuration (7497 for paper, 7496 for live)
- Ensure API is enabled in IB Gateway settings
- Verify trusted IP addresses

**Authentication Failed:**
- Check IBKR_CLIENT_ID is unique (not used by other applications)
- Verify API permissions are enabled
- Ensure account is properly funded (for live trading)

**Market Data Issues:**
- Paper trading has limited real-time data
- Verify market data subscriptions for live accounts
- Check exchange trading hours
- Some international stocks may not be available

**Tool Errors:**
- Check safety settings (trading may be disabled)
- Verify account type matches requirements
- Check order size limits
- Review audit logs for detailed error information

### **Diagnostic Commands**
```bash
# Test IBKR connection
python -c "from ibkr_mcp_server.client import IBKRClient; import asyncio; print(asyncio.run(IBKRClient().connect()))"

# Validate configuration
python -c "from ibkr_mcp_server.config import Settings; print(Settings())"

# Check MCP tools
python -m ibkr_mcp_server.main --list-tools
```

## Security Considerations

### **API Key Management**
- Never commit `.env` files to version control
- Use environment-specific configurations
- Rotate client IDs periodically
- Monitor API usage

### **Network Security**
- Use VPN for remote access
- Limit trusted IP addresses
- Monitor connection logs
- Use secure connections (HTTPS where applicable)

### **Trading Safety**
- Always test with paper trading first
- Start with small position sizes
- Monitor order execution carefully
- Have emergency procedures ready

### **Data Protection**
- Audit logs contain sensitive trading information
- Implement log rotation and archival
- Consider encryption for stored logs
- Comply with data retention policies

This configuration guide ensures safe and reliable deployment of the IBKR MCP Server in any environment.
