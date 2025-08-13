# IBKR MCP Server - API Quick Reference


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

### **Order Placement & Management** 🆕
```
"Buy 100 shares of Apple at market price"
"Place a limit order to buy Tesla at $240"
"Place a bracket order: buy ASML at €640, stop €620, target €680"
"Cancel my pending order #12345"
"Modify my GOOGL order to 200 shares at $2750"
"Check the status of my order #12345"
```

## 📊 **23 MCP Tools Reference**

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

### **Order Placement (6 tools)** 🆕
| Tool | Purpose | Example |
|------|---------|---------|
| `place_market_order` | Execute market orders | "Buy 100 AAPL at market" |
| `place_limit_order` | Place limit orders | "Buy Tesla at $240 limit" |
| `place_bracket_order` | Advanced bracket orders | "Bracket ASML €640/€620/€680" |
| `cancel_order` | Cancel pending orders | "Cancel order #12345" |
| `modify_order` | Modify existing orders | "Change order to 200 shares" |
| `get_order_status` | Check order status | "Status of order #12345" |

### **Order History (3 tools)**
| Tool | Purpose | Example |
|------|---------|---------|
| `get_open_orders` | View pending orders | "Show pending orders" |
| `get_completed_orders` | Order-level view (summary) | "Show my recent completed orders" |
| `get_executions` | Execution-level view (detailed fills) | "Get execution details for my Apple trades" |

**Key Difference:** `get_completed_orders` shows one record per order with average prices, while `get_executions` shows individual fill records with exact prices and venues.

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
- `ENABLE_ORDER_PLACEMENT=false` 🆕

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

### **Order History Analysis**
```
1. "Show me my recent completed orders"           # Order summaries
2. "Get execution details for my Apple trades"    # Individual fills  
3. "Show me all executions from the last 30 days" # Detailed analysis
4. "Get executions for TSLA from my DU account"   # Symbol-specific
```

**Two-Level Analysis:** Start with completed orders for overview, then drill down to executions for detailed fill analysis.

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

### **Order Placement & Management** 🆕
```
1. "Get quote for AAPL" → Research
2. "Buy 100 shares of AAPL at market price" → Execute
3. "Check status of order #12345" → Monitor
4. "Modify order to 150 shares at $185" → Adjust
5. "Set stop loss at $180" → Protect
```

### **Complete Trading Workflow** 🆕
```
1. "Check my buying power"
2. "Get quotes for AAPL, TSLA, MSFT"
3. "Buy 100 AAPL at market price"
4. "Place bracket order: buy Tesla at $240, stop $220, target $260"
5. "Set trailing stop on Microsoft with 8% trail"
6. "Show all my orders and positions"
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
- **Market Orders (MKT)**: Immediate execution at current market price 🆕
- **Limit Orders (LMT)**: Execute only at specified price or better 🆕
- **Bracket Orders**: Entry order with automatic stop loss and profit target 🆕
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

