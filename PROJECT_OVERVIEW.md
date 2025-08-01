# IBKR MCP Server - Enhanced Global Trading Platform

## Overview

The IBKR MCP Server is a comprehensive Model Context Protocol (MCP) server that provides Claude AI with professional-grade trading capabilities through Interactive Brokers. The system supports global markets including forex, international stocks, and advanced risk management through stop loss orders.

## Core Capabilities

### **Global Market Access**
- **US Markets**: All major US exchanges (NASDAQ, NYSE, AMEX)
- **European Markets**: XETRA (Germany), LSE (UK), AEB (Netherlands), SBF (France), SWX (Switzerland)
- **Asian Markets**: TSE (Japan), SEHK (Hong Kong), KSE (Korea), ASX (Australia)
- **Forex Markets**: 20+ major currency pairs with real-time rates and conversion

### **Trading Features**
- **Portfolio Management**: Real-time positions, P&L, account summaries
- **Market Data**: Live quotes for stocks worldwide with intelligent exchange detection
- **Currency Conversion**: Real-time forex rates with cross-currency calculations
- **Stop Loss Orders**: Advanced risk management with multiple order types
- **Multi-Currency Accounts**: Support for USD, EUR, GBP, JPY, HKD, KRW, AUD, CHF, DKK

### **Safety & Risk Management**
- **Safety-First Design**: All trading disabled by default
- **Paper Trading Ready**: Full compatibility with IBKR paper trading accounts
- **Order Limits**: Configurable size, value, and daily count restrictions
- **Audit Logging**: Complete audit trail of all trading operations
- **Rate Limiting**: API usage protection with intelligent throttling

## Architecture

### **Modular Design**
```
ibkr_mcp_server/
├── client.py                 # Enhanced IBKR client with global trading
├── tools.py                  # 17 MCP tools for Claude integration
├── config.py                 # Configuration management
├── utils.py                  # Utilities and base exceptions
├── data/                     # Reference data for global markets
│   ├── forex_pairs.py        # 20+ forex pairs with metadata
│   ├── international_symbols.py # 25+ international stocks
│   └── exchange_info.py      # Global exchange information
├── trading/                  # Specialized trading managers
│   ├── forex.py              # Forex trading and conversion
│   ├── international.py      # Global market symbol resolution
│   └── stop_loss.py          # Advanced order management
├── documentation/            # Comprehensive tool documentation
├── enhanced_config.py        # Safety and trading configuration
├── enhanced_validators.py    # Input validation framework
└── safety_framework.py      # Audit logging and protection
```

### **Trading Managers**
- **ForexManager**: Real-time rates, currency conversion, forex trading
- **InternationalManager**: Global symbol resolution, multi-currency market data
- **StopLossManager**: Order lifecycle management, bracket orders, trailing stops

### **Safety Framework**
- **TradingSafetyManager**: Unified safety orchestration
- **TradingAuditLogger**: Complete operation audit trail
- **EmergencyKillSwitch**: Instant trading halt capability
- **RateLimiter**: API usage protection

## MCP Tools (17 Total)

### **Portfolio & Account Management**
- `get_portfolio` - View current positions and P&L
- `get_account_summary` - Account balances and metrics
- `get_accounts` - List all available accounts
- `switch_account` - Change active trading account
- `get_connection_status` - IBKR connection status

### **Market Data & Analysis**
- `get_market_data` - Live quotes for any stock worldwide (auto-detects exchange)
- `resolve_international_symbol` - Look up exchange and currency for international stocks

### **Forex Trading**
- `get_forex_rates` - Real-time rates for 20+ currency pairs
- `convert_currency` - Convert amounts between currencies using live rates

### **Risk Management**
- `place_stop_loss` - Set automatic sell orders to limit losses
- `get_stop_losses` - View existing stop loss orders
- `modify_stop_loss` - Adjust stop prices or quantities
- `cancel_stop_loss` - Remove stop loss orders

### **Order Management**
- `get_open_orders` - View pending orders
- `get_completed_orders` - View recently executed trades
- `get_executions` - Detailed trade execution information

### **Documentation**
- `get_tool_documentation` - Comprehensive help system for all tools

## Key Features

### **Intelligent Symbol Detection**
```python
# These all work automatically:
get_market_data("AAPL")        # US stock → SMART/USD
get_market_data("ASML")        # Dutch stock → AEB/EUR  
get_market_data("7203")        # Japanese stock → TSE/JPY
get_market_data("AAPL,ASML,7203") # Mixed query handled seamlessly
```

### **Multi-Currency Conversion**
```python
convert_currency(1000, "USD", "EUR")  # Direct conversion
convert_currency(500, "GBP", "JPY")   # Cross-currency via USD
convert_currency(100, "EUR", "EUR")   # Same currency (1:1 rate)
```

### **Advanced Risk Management**
```python
place_stop_loss(symbol="AAPL", action="SELL", quantity=100, 
                stop_price=180.00, order_type="STP")
                
# Trailing stops for dynamic protection
place_stop_loss(symbol="TSLA", action="SELL", quantity=50,
                order_type="TRAIL", trail_percent=5.0)
```

## Configuration

### **Safety Configuration**
All trading features are disabled by default for maximum safety:

```python
# Default safe settings
enable_trading: bool = False                    # Master OFF switch
enable_forex_trading: bool = False
enable_international_trading: bool = False
enable_stop_loss_orders: bool = False
require_paper_account_verification: bool = True
max_order_size: int = 1000
max_order_value_usd: float = 10000.0
```

### **Paper Trading Setup**
For safe testing and development:
```python
enable_trading = True
enable_forex_trading = True
enable_international_trading = True
enable_stop_loss_orders = True
require_paper_account_verification = True  # Paper accounts only
```

## Global Market Coverage

### **Supported Exchanges & Currencies**
- **XETRA** (Germany) - EUR
- **LSE** (London) - GBP
- **TSE** (Tokyo) - JPY
- **SEHK** (Hong Kong) - HKD
- **ASX** (Australia) - AUD
- **AEB** (Amsterdam) - EUR
- **SWX** (Switzerland) - CHF
- **KSE** (Korea) - KRW

### **International Stocks Database**
25+ major international stocks with auto-detection:
- **European**: ASML, SAP, Nestle, Vodafone, LVMH
- **Asian**: Toyota (7203), Samsung (005930), Tencent (00700), TSMC (2330)
- **Others**: BHP, CBA, Novo Nordisk

### **Forex Pairs**
20+ major currency pairs including:
- **Majors**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD
- **Crosses**: EURGBP, EURJPY, GBPJPY, CHFJPY
- **Exotics**: EURNZD, GBPAUD, AUDNZD

## Paper Trading Compatibility

The system is fully compatible with IBKR paper trading accounts:
- **Mock Rate System**: Provides realistic forex rates when paper trading returns invalid data
- **Subscription Handling**: Graceful degradation for unavailable market data
- **Contract Qualification**: Handles limited international access in paper accounts
- **Safety Compliance**: All operations respect paper trading limitations

## Integration with Claude Desktop

The server integrates seamlessly with Claude Desktop through the MCP protocol:
1. **Automatic Tool Discovery**: All 17 tools automatically available to Claude
2. **Natural Language Interface**: Claude can use tools through natural conversation
3. **Error Handling**: Structured error messages for troubleshooting
4. **Documentation**: Built-in help system accessible through Claude

## Security & Safety

### **Defense in Depth**
- **Multiple Validation Layers**: Prevent unsafe operations
- **Fail-Safe Defaults**: Everything disabled until explicitly enabled
- **Account Verification**: Prevent accidental live trading
- **Order Limits**: Configurable size and value restrictions

### **Audit & Monitoring**
- **Complete Audit Trail**: Every operation logged with context
- **Session Tracking**: Operational correlation and analysis
- **Safety Violations**: Pattern analysis and alerting
- **Emergency Controls**: Kill switch for crisis situations

## Development Status

**Status: PRODUCTION READY**

All major enhancements complete and tested:
- ✅ **Safety Framework**: Complete protection with audit logging
- ✅ **Global Markets**: Forex, European, Asian market support
- ✅ **Risk Management**: Stop loss orders with multiple types
- ✅ **Paper Trading**: Full compatibility with mock data systems
- ✅ **Documentation**: Comprehensive help system
- ✅ **Integration**: Seamless Claude Desktop integration

## Usage Examples

### **Portfolio Management**
```
"Show me my current portfolio"
→ Uses get_portfolio tool

"What's my account balance?"
→ Uses get_account_summary tool
```

### **Global Market Data**
```
"Get quotes for Apple, ASML, and Toyota"
→ Uses get_market_data with auto-detection
→ Returns AAPL (US), ASML (Dutch), 7203 (Japanese)

"What's the current EUR/USD rate?"
→ Uses get_forex_rates tool
```

### **Risk Management**
```
"Set a stop loss on my AAPL position at $180"
→ Uses place_stop_loss tool with safety validation

"Show me all my stop loss orders"
→ Uses get_stop_losses tool
```

### **Currency Operations**
```
"Convert $1000 to Euros"
→ Uses convert_currency with live rates

"What's 500 British pounds in Japanese yen?"
→ Uses convert_currency with cross-currency calculation
```

This comprehensive platform provides professional-grade global trading capabilities while maintaining the highest standards of safety and user protection.
