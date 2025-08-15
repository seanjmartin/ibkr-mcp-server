# IBKR MCP Server - Enhanced Global Trading Platform

A comprehensive Model Context Protocol (MCP) server that provides Claude AI with professional-grade global trading capabilities through Interactive Brokers.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IBKR API](https://img.shields.io/badge/IBKR-API%20Compatible-green.svg)](https://interactivebrokers.github.io/tws-api/)
[![Development Complete](https://img.shields.io/badge/Status-Development%20Complete-green.svg)](docs/PRODUCTION_DEPLOYMENT.md)
[![Test Coverage](https://img.shields.io/badge/Tests-140%2F140%20Passing-brightgreen.svg)](TESTING_STATUS.md)

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

**🎉 DEVELOPMENT TO DATE**: >250 tests 100% passing, comprehensive safety framework, ready for paper trading validation!

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

### Modular Design
```
ibkr_mcp_server/
├── client.py                 # Enhanced IBKR client with global trading
├── tools.py                  # 23 MCP tools for Claude integration
├── main.py                   # MCP server entry point
├── config.py                 # Configuration management
├── utils.py                  # Utilities and base exceptions
├── data/                     # Reference data for global markets
│   ├── forex_pairs.py        # 21+ forex pairs with metadata
│   ├── international_symbols.py # 23+ international stocks
│   └── exchange_info.py      # Global exchange information
├── trading/                  # Specialized trading managers
│   ├── forex.py              # Forex trading and conversion
│   ├── international.py      # Global market symbol resolution
│   ├── stop_loss.py          # Advanced order management
│   └── order_management.py   # Order placement and lifecycle
├── documentation/            # Comprehensive tool documentation
├── enhanced_config.py        # Safety and trading configuration
├── enhanced_validators.py    # Input validation framework
└── safety_framework.py      # Audit logging and protection
```

### Trading Managers
- **ForexManager**: Real-time rates, currency conversion, forex trading
- **InternationalManager**: Global symbol resolution, multi-currency market data
- **StopLossManager**: Order lifecycle management, bracket orders, trailing stops

### Safety Framework Components
- **TradingSafetyManager**: Unified safety orchestration
- **TradingAuditLogger**: Complete operation audit trail
- **EmergencyKillSwitch**: Instant trading halt capability
- **RateLimiter**: API usage protection

## 🛠️ Available Tools (23 Total)

### Portfolio & Account Management
- `get_portfolio` - View current positions and P&L
- `get_account_summary` - Account balances and metrics  
- `get_accounts` - List available accounts
- `switch_account` - Change active account
- `get_connection_status` - IBKR connection status

### Global Market Data
- `get_market_data` - Live quotes for any stock worldwide (auto-detects exchange)
- `resolve_international_symbol` - Look up exchange/currency for international stocks

### Forex Trading
- `get_forex_rates` - Real-time rates for 21 currency pairs
- `convert_currency` - Convert amounts between currencies using live rates

### Risk Management
- `place_stop_loss` - Set automatic sell orders to limit losses
- `get_stop_losses` - View existing stop loss orders
- `modify_stop_loss` - Adjust stop prices or quantities
- `cancel_stop_loss` - Remove stop loss orders

### Order Placement & Management 🆕
- `place_market_order` - Execute immediate market orders
- `place_limit_order` - Place orders with price control
- `place_bracket_order` - Advanced orders with entry/stop/target
- `cancel_order` - Cancel pending orders
- `modify_order` - Modify existing orders
- `get_order_status` - Check order status and execution

### Order History & Tracking
- `get_open_orders` - View pending orders
- `get_completed_orders` - View recent trades
- `get_executions` - Detailed execution information

### Documentation
- `get_tool_documentation` - Comprehensive help system

## 🌍 Global Market Support

### Supported Exchanges & Currencies (48 Total)

**Europe (19):**
- **XETRA** (Germany) - EUR: Frankfurt Stock Exchange
- **LSE** (United Kingdom) - GBP: London Stock Exchange
- **SBF** (France) - EUR: Euronext Paris
- **AEB** (Netherlands) - EUR: Euronext Amsterdam
- **SWX** (Switzerland) - CHF: SIX Swiss Exchange
- **KFX** (Denmark) - DKK: Nasdaq Copenhagen
- **BIT** (Italy) - EUR: Borsa Italiana
- **MIL** (Italy) - EUR: Milan Stock Exchange
- **BME** (Spain) - EUR: Bolsas y Mercados Españoles
- **BVME** (Spain) - EUR: Madrid Stock Exchange
- **VIX** (Austria) - EUR: Vienna Stock Exchange
- **BEL** (Belgium) - EUR: Euronext Brussels
- **OSE** (Norway) - NOK: Oslo Stock Exchange
- **OMX** (Sweden) - SEK: Nasdaq Stockholm
- **HEX** (Finland) - EUR: Nasdaq Helsinki
- **WSE** (Poland) - PLN: Warsaw Stock Exchange
- **LSEETF** (United Kingdom) - GBP: London Stock Exchange ETF Segment
- **GETTEX** (Germany) - EUR: Gettex Exchange
- **TRADEGATE** (Germany) - EUR: Tradegate Exchange

**North America (7):**
- **NYSE** (United States) - USD: New York Stock Exchange
- **NASDAQ** (United States) - USD: NASDAQ Stock Market
- **ARCA** (United States) - USD: NYSE Arca
- **BATS** (United States) - USD: Cboe BZX Exchange
- **IEX** (United States) - USD: Investors Exchange
- **TSX** (Canada) - CAD: Toronto Stock Exchange
- **TSXV** (Canada) - CAD: TSX Venture Exchange

**Latin America (2):**
- **MEXI** (Mexico) - MXN: Mexican Stock Exchange
- **BOVESPA** (Brazil) - BRL: B3 Stock Exchange

**Asia (12):**
- **TSE** (Japan) - JPY: Tokyo Stock Exchange
- **SEHK** (Hong Kong) - HKD: Stock Exchange of Hong Kong
- **KSE** (South Korea) - KRW: Korea Exchange
- **TWSE** (Taiwan) - TWD: Taiwan Stock Exchange
- **SSE** (China) - CNY: Shanghai Stock Exchange
- **SZSE** (China) - CNY: Shenzhen Stock Exchange
- **BSE** (India) - INR: Bombay Stock Exchange
- **NSE** (India) - INR: National Stock Exchange of India
- **SGX** (Singapore) - SGD: Singapore Exchange
- **SET** (Thailand) - THB: Stock Exchange of Thailand
- **IDX** (Indonesia) - IDR: Indonesia Stock Exchange
- **KLSE** (Malaysia) - MYR: Bursa Malaysia

**Pacific (2):**
- **ASX** (Australia) - AUD: Australian Securities Exchange
- **NZX** (New Zealand) - NZD: New Zealand Exchange

**Middle East & Africa (4):**
- **TASE** (Israel) - ILS: Tel Aviv Stock Exchange
- **TADAWUL** (Saudi Arabia) - SAR: Saudi Stock Exchange
- **EGX** (Egypt) - EGP: Egyptian Exchange
- **JSE** (South Africa) - ZAR: Johannesburg Stock Exchange

**Global/Special (2):**
- **SMART** (Global) - USD: IBKR Smart Routing
- **IDEALPRO** (Global) - Multiple: IBKR Forex Exchange

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

### Supported Currencies (29 Total)
- **Major (8)**: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD
- **Asian (6)**: HKD, KRW, CNY, SGD, TWD, CNH
- **European (3)**: DKK, SEK, NOK  
- **Americas (2)**: BRL, MXN
- **Middle East & Africa (3)**: ZAR, AED, SAR
- **Additional Global (7)**: INR, PLN, ILS, TRY, CZK, HUF, MYR

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

## 🏗️ Architecture

### Modular Design
- **ForexManager**: Currency trading and conversion
- **InternationalManager**: Global symbol resolution  
- **StopLossManager**: Advanced risk management
- **Safety Framework**: Comprehensive protection system

### Reference Data
- **25+ International Stocks**: Complete metadata with auto-detection
- **21 Forex Pairs**: Complete trading specifications and metadata
- **10+ Global Exchanges**: Trading hours, currencies, settlement rules

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
