# IBKR MCP Server - API Quick Reference

**Version**: 2.0.0 | **Status**: Production Ready | **Test Coverage**: 100% (140/140 tests)

## 🚀 **Quick Start Commands**

### **Connection & Status**
```
"Check my IBKR connection status"
"Show me all my IBKR accounts" 
"Switch to my paper account DU1234567"
```

### **Portfolio & Account**
```
"Show me my current portfolio"
"What's my account balance?"
"Get my portfolio performance summary"
```

### **Market Data**
```
"What's Apple trading at right now?"
"Get quotes for AAPL, MSFT, GOOGL"
"Get quotes for Apple, ASML, and Toyota"  # Mixed global markets
```

### **Forex & Currency**
```
"What's the EUR/USD rate?"
"Show me major forex pairs"
"Convert $5000 to Euros"
"How much is £2000 in Japanese Yen?"
```

### **Risk Management**
```
"Set a stop loss on my Apple position at $180"
"Place a trailing stop on Tesla with 8% trail"
"Show me all my stop loss orders"
"Cancel my Tesla stop loss order"
```

## 📊 **17 MCP Tools Reference**

### **Portfolio & Account (5 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_portfolio` | View positions & P&L | "Show my portfolio" |
| `get_account_summary` | Account balance & metrics | "What's my balance?" |
| `get_accounts` | List all accounts | "Show my accounts" |
| `switch_account` | Change active account | "Switch to DU123456" |
| `get_connection_status` | Check IBKR connection | "Check connection" |

### **Market Data (2 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_market_data` | Live quotes (global) | "Quote for AAPL,ASML" |
| `resolve_international_symbol` | Find exchange/currency | "Where does ASML trade?" |

### **Forex & Currency (2 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_forex_rates` | Live forex rates | "EUR/USD rate?" |  
| `convert_currency` | Multi-currency conversion | "Convert $1000 to EUR" |

### **Risk Management (4 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `place_stop_loss` | Create stop orders | "Stop loss AAPL at $180" |
| `get_stop_losses` | View active stops | "Show stop orders" |
| `modify_stop_loss` | Change stop order | "Move AAPL stop to $185" |
| `cancel_stop_loss` | Remove stop order | "Cancel TSLA stop" |

### **Order Management (3 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_open_orders` | View pending orders | "Show pending orders" |
| `get_completed_orders` | View recent trades | "Show recent trades" |
| `get_executions` | Detailed trade info | "AAPL execution details" |

### **Documentation (1 tool)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_tool_documentation` | Help system | "Help with forex trading" |

## 🌍 **Global Market Coverage**

### **Auto-Detection Examples**
```
"AAPL"  → SMART/USD (US)
"ASML"  → AEB/EUR (Netherlands)  
"7203"  → TSE/JPY (Japan)
"SAP"   → XETRA/EUR (Germany)
"VOD"   → LSE/GBP (UK)
```

### **12 Exchanges Supported**
- **US**: SMART (all US stocks)
- **Europe**: XETRA, LSE, AEB, SBF, SWX, KFX
- **Asia**: TSE, SEHK, KSE, ASX  
- **Forex**: IDEALPRO (21 pairs)

### **21 Forex Pairs**
**Major (7)**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD  
**Cross (14)**: EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, etc.

## 🛡️ **Safety Framework**

### **Built-in Protection**
- **Kill Switch**: Instant trading halt capability
- **Daily Limits**: Maximum orders/value per day
- **Rate Limiting**: API abuse prevention
- **Order Validation**: Size and value limits
- **Audit Logging**: Complete operation tracking

### **Safety Commands**
```
"Activate emergency kill switch"
"Show safety status"
"What are my current trading limits?"
```

### **Configuration-Based Safety**
All trading features **OFF by default**:
- `ENABLE_TRADING=false`
- `ENABLE_FOREX_TRADING=false` 
- `ENABLE_INTERNATIONAL_TRADING=false`
- `ENABLE_STOP_LOSS_ORDERS=false`

## 💡 **Common Workflows**

### **Portfolio Review**
```
1. "Check my IBKR connection"
2. "Show me my portfolio"  
3. "What's my account balance?"
4. "Get quotes for my holdings"
```

### **Risk Management Setup**
```
1. "Show me my current positions"
2. "Set stop losses at 10% below cost for all positions"
3. "Show me all my stop orders"
4. "Place trailing stops on growth stocks"
```

### **Global Trading**
```
1. "Get quotes for ASML, SAP, Toyota"
2. "Where does ASML trade?" 
3. "Convert €10,000 to USD"
4. "What's the EUR/USD rate trend?"
```

### **Forex Trading**
```
1. "Show me major forex pairs"
2. "What's driving EUR/USD today?"
3. "Convert my EUR balance to USD"
4. "Get GBPJPY and EURJPY rates"
```

## 🚨 **Emergency Procedures**

### **Kill Switch Activation**
```
"Activate emergency kill switch - connection lost"
"Stop all trading immediately"
"Enable emergency mode"
```

### **Error Recovery**
```
"Check connection status"
"Reconnect to IBKR"
"Show recent error logs"
"Verify safety systems"
```

## 📈 **Advanced Features**

### **Multi-Currency Support**
- **Account Balances**: USD, EUR, GBP, JPY, CHF, AUD, CAD, etc.
- **Position Tracking**: Native currency + USD equivalent
- **Real-time Conversion**: Live forex rates for all calculations

### **Order Types**
- **Stop Market (STP)**: Basic stop loss protection  
- **Stop Limit (STP LMT)**: Stop with limit price control
- **Trailing Stop (TRAIL)**: Dynamic stop that follows price

### **International Symbol Resolution**
- **Auto-Detection**: Automatically finds correct exchange
- **Currency Conversion**: Real-time USD equivalents
- **Trading Hours**: Respects local market schedules

## 🔧 **Configuration Examples**

### **Conservative Settings**
```bash
IBKR_MAX_ORDER_SIZE=100
IBKR_MAX_ORDER_VALUE_USD=1000.0  
IBKR_MAX_DAILY_ORDERS=10
IBKR_REQUIRE_PAPER_ACCOUNT_VERIFICATION=true
```

### **Active Trading Settings**
```bash
IBKR_MAX_ORDER_SIZE=1000
IBKR_MAX_ORDER_VALUE_USD=10000.0
IBKR_MAX_DAILY_ORDERS=50
IBKR_MAX_STOP_LOSS_ORDERS=25
```

## 📞 **Help & Support**

### **Built-in Help**
```
"Help with forex trading"
"Show me stop loss examples"
"How do I use international markets?"
"What are my current limits?"
```

### **Documentation Links**
- [Complete API Reference](../api/tools.md)
- [Trading Guide](../guides/trading.md)
- [Safety Framework](../architecture/safety-measures.md)
- [Troubleshooting](../examples/troubleshooting.md)

---

**Status**: ✅ **Production Ready**  
**Last Updated**: August 1, 2025  
**Version**: 2.0.0 - Enhanced Global Trading Platform
