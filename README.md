# IBKR MCP Server - Enhanced Global Trading Platform

A comprehensive Model Context Protocol (MCP) server that provides Claude AI with professional-grade global trading capabilities through Interactive Brokers.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![IBKR API](https://img.shields.io/badge/IBKR-API%20Compatible-green.svg)](https://interactivebrokers.github.io/tws-api/)

## 🌟 Features

### **Global Market Access**
- 🇺🇸 **US Markets**: NASDAQ, NYSE, AMEX
- 🇪🇺 **European Markets**: XETRA, LSE, AEB, SBF, SWX, KFX
- 🌏 **Asian Markets**: TSE, SEHK, KSE, ASX
- 💱 **Forex Trading**: 21 currency pairs across 13 currencies with real-time conversion

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

## 🛠️ Available Tools (17 Total)

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

### Order Management
- `get_open_orders` - View pending orders
- `get_completed_orders` - View recent trades
- `get_executions` - Detailed execution information

### Documentation
- `get_tool_documentation` - Comprehensive help system

## 🌍 Global Market Support

### Supported Exchanges & Currencies (12 Total)

**European Exchanges (6):**
- **XETRA** (Germany) - EUR: SAP, Siemens, BMW
- **LSE** (London) - GBP: Vodafone, BP, Shell  
- **SBF** (Euronext Paris) - EUR: LVMH, Total, Sanofi
- **AEB** (Euronext Amsterdam) - EUR: ASML, Unilever, ING
- **SWX** (SIX Swiss Exchange) - CHF: Nestle, Novartis, Roche
- **KFX** (Nasdaq Copenhagen) - DKK: Novo Nordisk, Maersk, Carlsberg

**Asian & Pacific Exchanges (4):**
- **TSE** (Tokyo) - JPY: Toyota (7203), Honda, Sony
- **SEHK** (Hong Kong) - HKD: Tencent (00700), TSMC (2330)
- **KSE** (Korea) - KRW: Samsung (005930), LG, SK Hynix
- **ASX** (Australia) - AUD: BHP, CBA, Woolworths

**Global Trading (2):**
- **SMART** (IBKR Routing) - USD: All US stocks
- **IDEALPRO** (Forex) - Multiple: 21 currency pairs, 13 currencies

### Auto-Detection Examples
```python
# These work automatically:
get_market_data("AAPL")      # US stock → SMART/USD
get_market_data("ASML")      # Dutch stock → AEB/EUR  
get_market_data("7203")      # Japanese stock → TSE/JPY
get_market_data("AAPL,ASML") # Mixed markets handled seamlessly
```

## 💱 Forex & Currency Features

### Supported Currency Pairs (21 Total)
- **Major Pairs (7)**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD
- **Cross Pairs (14)**: EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, CADJPY, NZDJPY, EURAUD, EURNZD, GBPAUD, GBPNZD, AUDCAD, AUDNZD
- **Supported Currencies (13)**: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD, HKD, KRW, DKK, SEK, NOK

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

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Complete system overview
- **[TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md)** - Technical architecture details
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Configuration and deployment
- **[CHANGELOG.md](CHANGELOG.md)** - Implementation history

## 🧪 Paper Trading

Perfect for testing and learning:
- Virtual $1,000,000 account
- All markets accessible
- No real money at risk
- Mock data systems for API limitations

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

## 🚨 Safety Features

- **Multiple Validation Layers**: Prevent unsafe operations
- **Complete Audit Trail**: Every operation logged
- **Emergency Kill Switch**: Instant trading halt
- **Paper Trading Mode**: Safe testing environment
- **Order Size Limits**: Configurable restrictions
- **Account Protection**: Prevent accidental live trading

## 📈 Performance

- **Response Times**: Sub-second for cached data, 2-3 seconds for fresh data
- **Intelligent Caching**: 5-second forex cache, automatic cleanup
- **Rate Limiting**: Respects IBKR API limits
- **Memory Efficient**: Optimized resource usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with paper trading
4. Submit a pull request

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
