# IBKR MCP Server - Enhanced Global Trading Platform

A comprehensive Model Context Protocol (MCP) server that provides Claude AI with professional-grade global trading capabilities through Interactive Brokers.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IBKR API](https://img.shields.io/badge/IBKR-API%20Compatible-green.svg)](https://interactivebrokers.github.io/tws-api/)
[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](docs/architecture/system-architecture.md)
[![Test Coverage](https://img.shields.io/badge/Tests-254%2F254%20Passing-brightgreen.svg)](docs/architecture/testing-strategy.md)

## 🌟 Features

### **Global Market Access**
- 🇺🇸 **US Markets**: NASDAQ, NYSE, AMEX
- 🇪🇺 **European Markets**: XETRA, LSE, AEB, SBF, SWX, KFX
- 🌏 **Asian Markets**: TSE, SEHK, KSE, ASX
- 💱 **Forex Trading**: 21+ currency pairs across 29 currencies with real-time conversion

### **Advanced Trading Capabilities**
- 📊 **Portfolio Management**: Real-time positions, P&L, multi-currency accounts
- 💹 **Market Data**: Live quotes with intelligent exchange detection
- 🛡️ **Risk Management**: Stop loss orders, bracket orders, trailing stops
- 🔄 **Currency Conversion**: Real-time forex rates with cross-currency calculations
- 🎯 **Order Management**: Complete order lifecycle with modification and cancellation

### **Safety & Security**
- 🔒 **Safety-First Design**: All trading disabled by default
- 📝 **Complete Audit Trail**: Every operation logged with context
- ⚡ **Emergency Controls**: Kill switch for instant trading halt
- 🧪 **Paper Trading Ready**: Full compatibility with IBKR paper accounts
- ⚖️ **Risk Limits**: Configurable order size, value, and count restrictions

## 🚀 Quick Start

**🎉 DEVELOPMENT COMPLETE**: 254 unit tests 100% passing, comprehensive safety framework, production-ready global trading platform!

👉 **[API Quick Reference](docs/API_QUICK_REFERENCE.md)** - Essential commands & examples  
👉 **[Production Deployment Guide](docs/PRODUCTION_DEPLOYMENT.md)** - Complete setup instructions

### Prerequisites
- Python 3.9+ (tested with 3.13.2)
- Interactive Brokers account (paper or live)
- IB Gateway or TWS
- Claude Desktop

### Installation
```bash
git clone <repository-url>
cd ibkr-mcp-server
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Configure IBKR connection:
   ```bash
   IBKR_HOST=127.0.0.1
   IBKR_PORT=7497        # Paper: 7497, Live: 7496
   IBKR_IS_PAPER=true
   ```
3. Set safety parameters:
   ```bash
   ENABLE_TRADING=false  # Enable explicitly when ready
   ```

### Claude Desktop Integration
Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "ibkr": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "ibkr_mcp_server.main"],
      "cwd": "/path/to/ibkr-mcp-server"
    }
  }
}
```

## 🏗️ Architecture

### Professional Trading Platform
The IBKR MCP Server is built as a comprehensive trading platform with:

- **Enhanced IBKR Client**: Central orchestrator with 29 methods managing all IBKR interactions
- **23 MCP Tools**: Complete Claude Desktop integration for natural language trading
- **Safety Framework**: Multi-layer protection with audit logging and emergency controls
- **Trading Managers**: Specialized managers for forex, international markets, and risk management
- **Global Market Support**: 12 exchanges, 21 forex pairs, intelligent symbol detection

### Key Components
- **Trading Safety**: Emergency kill switch, rate limiting, comprehensive audit trails
- **Global Markets**: Automatic exchange detection for US, European, and Asian stocks
- **Risk Management**: Advanced stop loss orders, bracket orders, trailing stops
- **Currency Trading**: Real-time forex rates with cross-currency conversion

📖 **[Complete Technical Architecture](docs/architecture/system-architecture.md)**

## 🛠️ Complete MCP Tools (23 Total)

### **Portfolio & Account Management (5 tools)**
- `get_portfolio` - View current positions with P&L analysis
- `get_account_summary` - Account balances and metrics
- `get_accounts` - List all available IBKR accounts
- `switch_account` - Change active trading account
- `get_connection_status` - IBKR connection health and system status

### **Market Data & Analysis (2 tools)**
- `get_market_data` - Live quotes for stocks worldwide with intelligent exchange detection
- `resolve_symbol` - Unified symbol resolution with fuzzy search and company data

### **Forex & Currency (2 tools)**
- `get_forex_rates` - Real-time forex rates for 21 currency pairs
- `convert_currency` - Multi-currency conversion with live rates

### **Risk Management (4 tools)**
- `place_stop_loss` - Create stop orders for loss protection
- `get_stop_losses` - View all active stop loss orders
- `modify_stop_loss` - Adjust existing stop loss orders
- `cancel_stop_loss` - Remove stop loss orders

### **Order History & Tracking (3 tools)**
- `get_open_orders` - View pending orders
- `get_completed_orders` - Order-level trade history (summary)
- `get_executions` - Execution-level details (individual fills)

### **Order Placement & Management (6 tools)**
- `place_market_order` - Execute market orders for immediate execution
- `place_limit_order` - Place limit orders with price control
- `place_bracket_order` - Advanced bracket orders (entry + stop + target)
- `cancel_order` - Cancel pending orders
- `modify_order` - Modify existing orders (quantity, price, time-in-force)
- `get_order_status` - Get comprehensive order status information

### **Documentation (1 tool)**
- `get_tool_documentation` - Built-in help system for all tools

## 🌍 Global Market Support

### Supported Exchanges (12 Total)

**US Markets:**
- **SMART** - IBKR Smart Routing across all US exchanges (NYSE, NASDAQ, AMEX)

**European Markets (6):**
- **XETRA** (Germany) - EUR: Frankfurt Stock Exchange  
- **LSE** (United Kingdom) - GBP: London Stock Exchange
- **SBF** (France) - EUR: Euronext Paris
- **AEB** (Netherlands) - EUR: Euronext Amsterdam
- **SWX** (Switzerland) - CHF: SIX Swiss Exchange
- **KFX** (Denmark) - DKK: Nasdaq Copenhagen

**Asian Markets (4):**
- **TSE** (Japan) - JPY: Tokyo Stock Exchange
- **SEHK** (Hong Kong) - HKD: Stock Exchange of Hong Kong
- **KSE** (South Korea) - KRW: Korea Exchange
- **ASX** (Australia) - AUD: Australian Securities Exchange

**Forex Trading:**
- **IDEALPRO** - IBKR's institutional forex platform with 21 currency pairs

### Intelligent Symbol Detection
```python
# Global stock quotes work automatically:
get_market_data("AAPL")        # US stock → SMART/USD (Apple)
get_market_data("ASML")        # Dutch stock → AEB/EUR (ASML)  
get_market_data("7203")        # Japanese stock → TSE/JPY (Toyota)
get_market_data("00700")       # Hong Kong stock → SEHK/HKD (Tencent)
get_market_data("005930")      # Korean stock → KSE/KRW (Samsung)
get_market_data("SAP")         # German stock → XETRA/EUR (SAP)
get_market_data("RDSA")        # UK stock → LSE/GBP (Shell)

# Mixed international queries handled seamlessly:
get_market_data("AAPL,ASML,7203,00700,005930,SAP,RDSA")
```

### Advanced Risk Management
```python
# Basic stop loss
place_stop_loss(symbol="AAPL", action="SELL", quantity=100, 
                stop_price=180.00, order_type="STP")
                
# Trailing stops for dynamic protection
place_stop_loss(symbol="TSLA", action="SELL", quantity=50,
                order_type="TRAIL", trail_percent=5.0)
                
# Stop-limit orders for price control
place_stop_loss(symbol="MSFT", action="SELL", quantity=75,
                stop_price=400.00, limit_price=395.00, order_type="STP LMT")
```

## 💱 Forex & Currency Features

### Supported Currency Pairs (21 Total)
- **Major Pairs (7)**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- **Cross Pairs (14)**: EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, CADJPY, NZDJPY, EURAUD, EURNZD, GBPAUD, GBPNZD, AUDCAD, AUDNZD

### Supported Currencies (13 Total)
**Major Currencies**: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD  
**Additional**: HKD, KRW, DKK, SEK, NOK

**All currencies support:**
- Real-time conversion using live forex rates
- Cross-currency calculations via USD routing
- Multi-currency account balance tracking

### Currency Conversion
```python
convert_currency(1000, "USD", "EUR")  # Direct conversion
convert_currency(500, "GBP", "JPY")   # Cross-currency via USD
```

## 🛡️ Safety Configuration

### Default Safety Settings
```python
# All trading disabled by default
enable_trading: bool = False
enable_forex_trading: bool = False
enable_international_trading: bool = False
enable_stop_loss_orders: bool = False
require_paper_account_verification: bool = True
```

### Order Limits
```python
max_order_size: int = 1000              # Maximum shares per order
max_order_value_usd: float = 10000.0    # Maximum USD value per order
max_daily_orders: int = 50              # Maximum orders per day
```

## 📚 Documentation

### **📖 Complete Documentation Hub**
- **[Documentation Center](docs/README.md)** - Navigate all documentation sections

### **🚀 Getting Started**
- **[Quick Start Guide](docs/guides/quick-start.md)** - Get up and running in 5 minutes
- **[Basic Usage Examples](docs/examples/basic-usage.md)** - Real Claude conversations and workflows

### **🔧 API & Technical Reference**
- **[MCP Tools Reference](docs/api/tools.md)** - Complete documentation for all 23 tools
- **[System Architecture](docs/architecture/system-architecture.md)** - Comprehensive technical architecture
- **[Supported Markets](docs/reference/markets.md)** - Complete global markets, exchanges, and currencies

### **🏢 System Information** 
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment guide
- **[CHANGELOG.md](CHANGELOG.md)** - Complete implementation history

### **👥 For Different Users**
- **New Users**: Start with [Quick Start Guide](docs/guides/quick-start.md) → [Basic Examples](docs/examples/basic-usage.md)
- **Developers**: Check [System Architecture](docs/architecture/system-architecture.md) → [API Reference](docs/api/tools.md)
- **Traders**: Review [Supported Markets](docs/reference/markets.md) → [Trading Examples](docs/examples/basic-usage.md)

## 🧪 Paper Trading

Perfect for testing and learning with full feature compatibility:

### Paper Trading Features
- **Virtual $1,000,000 account** - Start with substantial virtual funds
- **All markets accessible** - Full global market access
- **No real money at risk** - Complete safety for learning
- **Real market data** - Live quotes and actual market conditions

### Paper Trading Enhancements
- **Mock Rate System**: Provides realistic forex rates when paper trading returns invalid data
- **Subscription Handling**: Graceful degradation for unavailable market data
- **Contract Qualification**: Handles limited international access in paper accounts
- **Safety Compliance**: All operations respect paper trading limitations

### Integration with Claude Desktop
The server integrates seamlessly with Claude Desktop through the MCP protocol:
1. **Automatic Tool Discovery**: All 23 tools automatically available to Claude
2. **Natural Language Interface**: Claude can use tools through natural conversation
3. **Error Handling**: Structured error messages for troubleshooting
4. **Documentation**: Built-in help system accessible through Claude

## 🔧 Usage Examples

### Portfolio Management
```
"Show me my current portfolio"
"What's my account balance in different currencies?"
"Switch to my other IBKR account"
```

### Global Trading
```
"Get quotes for Apple, ASML, and Toyota"
"What's the current EUR/USD exchange rate?"
"Convert $5000 to British pounds"
```

### Risk Management
```
"Set a stop loss on my Tesla position at $200"
"Show me all my stop loss orders"
"Place a bracket order for AAPL with stop at $180 and target at $200"
```



## 🚨 Safety & Security

### Defense in Depth
- **Multiple Validation Layers**: Prevent unsafe operations at every level
- **Fail-Safe Defaults**: Everything disabled until explicitly enabled
- **Account Verification**: Prevent accidental live trading
- **Order Limits**: Configurable size and value restrictions

### Audit & Monitoring
- **Complete Audit Trail**: Every operation logged with context
- **Session Tracking**: Operational correlation and analysis
- **Safety Violations**: Pattern analysis and alerting
- **Emergency Controls**: Kill switch for crisis situations

### Safety Framework Components
- **Emergency Kill Switch**: Instant trading halt capability
- **Rate Limiting**: API usage protection with intelligent throttling
- **Order Validation**: Size, value, and daily count restrictions
- **Paper Trading Mode**: Safe testing environment with virtual funds

## 📈 Performance

- **Response Times**: Sub-second for cached data, 2-3 seconds for fresh data
- **Intelligent Caching**: 5-second forex cache, automatic cleanup
- **Rate Limiting**: Respects IBKR API limits
- **Memory Efficient**: Optimized resource usage


## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and informational purposes. Trading involves risk of financial loss. Always test with paper trading before using real money. The authors are not responsible for any financial losses.

## 🔗 Links

- [Interactive Brokers API Documentation](https://interactivebrokers.github.io/tws-api/)
- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)
- [ib-async Library](https://github.com/erdewit/ib_async)

---

**Status**: Production Ready - Global Trading Platform with Comprehensive Safety Protection
