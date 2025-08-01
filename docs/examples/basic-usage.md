# Basic Usage Examples

Practical examples for common operations with the IBKR MCP Server.

## 🚀 Getting Started Examples

### Connection and Setup

```
User: "Check my IBKR connection status"
Claude: 
✅ Connected to IBKR Paper Trading
• Server: 127.0.0.1:7497
• Account: DU1234567 (Paper Trading)
• Latency: 12ms
• Status: Active, all systems operational
```

```
User: "Show me all my IBKR accounts"
Claude:
📊 Available IBKR Accounts:
• DU1234567 (Paper Trading) - Currently Active ✅
• U9876543 (Live Trading) - Available
• Currency: USD (primary), EUR, GBP supported
```

## 📊 Portfolio Management Examples

### Portfolio Overview

```
User: "Show me my current portfolio"
Claude:
📈 Current Portfolio (Account: DU1234567)

🔹 AAPL - Apple Inc.
   • Position: 150 shares
   • Avg Cost: $175.50 | Current: $180.25
   • Market Value: $27,037.50
   • Unrealized P&L: +$712.50 (+2.71%) 💚

🔹 TSLA - Tesla Inc.
   • Position: 50 shares
   • Avg Cost: $245.00 | Current: $238.90
   • Market Value: $11,945.00
   • Unrealized P&L: -$305.00 (-2.49%) 🔴

📊 Portfolio Summary:
   • Total Value: $98,450.75
   • Day Change: +$1,247.30 (+1.28%)
   • Available Cash: $51,230.45
```

### Account Balance

```
User: "What's my account balance?"
Claude:
💰 Account Summary (DU1234567)

💵 Currency Balances:
   • USD: $51,230.45 (Available: $48,450.30)
   • EUR: €5,420.80 (Available: €5,420.80)
   • GBP: £2,150.60 (Available: £2,150.60)

📈 Portfolio Metrics:
   • Total Portfolio Value: $98,450.75
   • Buying Power: $48,450.30
   • Margin Used: $2,780.15
   • Maintenance Margin: $1,950.20
```

## 📈 Market Data Examples

### Single Stock Quote

```
User: "What's Apple trading at right now?"
Claude:
📊 AAPL (Apple Inc.) - SMART/USD

💹 Current Quote:
   • Last: $180.25 (+$2.15, +1.21%)
   • Bid: $180.20 (Size: 300)
   • Ask: $180.30 (Size: 250)
   • Volume: 45,234,567 shares

📈 Session Data:
   • Open: $178.10 | High: $181.50 | Low: $177.95
   • Previous Close: $178.10
   • Market Cap: $2.85T
```

### Multi-Market Quotes

```
User: "Get quotes for Apple, ASML, and Toyota"
Claude:
🌍 Global Market Quotes:

🇺🇸 AAPL (Apple Inc.) - SMART/USD
   • $180.25 (+$2.15, +1.21%)
   • Volume: 45.2M shares

🇳🇱 ASML (ASML Holding NV) - AEB/EUR  
   • €650.80 (+€8.40, +1.31%)
   • Volume: 1.2M shares
   • USD Equivalent: ~$706.47

🇯🇵 7203 (Toyota Motor Corp) - TSE/JPY
   • ¥2,450.00 (+¥35.00, +1.45%)
   • Volume: 8.5M shares
   • USD Equivalent: ~$16.33
```

### International Symbol Resolution

```
User: "Where does ASML trade?"
Claude:
🔍 ASML Symbol Resolution:

🏛️ Primary Listing:
   • Exchange: AEB (Euronext Amsterdam)
   • Currency: EUR
   • Full Name: ASML Holding NV
   • Sector: Technology (Semiconductor Equipment)
   • Country: Netherlands

🌐 Alternative Listings:
   • NASDAQ: ASML (USD) - ADR
   • Trading Hours: 09:00-17:30 CET
   • Settlement: T+2
```

## 💱 Forex and Currency Examples

### Forex Rates

```
User: "What's the current EUR/USD rate?"
Claude:
💱 EURUSD - Euro/US Dollar

📊 Live Quote:
   • Rate: 1.0856
   • Bid: 1.0855 | Ask: 1.0857
   • Spread: 0.2 pips
   • Change: +0.0012 (+0.11%)

📈 Session Data:
   • Open: 1.0844 | High: 1.0867 | Low: 1.0841
   • Previous Close: 1.0844
   • 24h Volume: $847M notional
```

```
User: "Show me major forex pairs"
Claude:
💱 Major Forex Pairs:

🔹 EURUSD: 1.0856 (+0.11%) | Spread: 0.2 pips
🔹 GBPUSD: 1.2654 (+0.08%) | Spread: 0.3 pips  
🔹 USDJPY: 110.25 (-0.15%) | Spread: 0.1 pips
🔹 USDCHF: 0.9124 (+0.05%) | Spread: 0.2 pips
🔹 AUDUSD: 0.7234 (+0.22%) | Spread: 0.2 pips
🔹 USDCAD: 1.3456 (-0.09%) | Spread: 0.2 pips
🔹 NZDUSD: 0.6789 (+0.18%) | Spread: 0.3 pips
```

### Currency Conversion

```
User: "Convert $5000 to Euros"
Claude:
💰 Currency Conversion:

💵 $5,000.00 USD → 💶 €4,608.95 EUR

📊 Conversion Details:
   • Exchange Rate: 1.0856 (EURUSD)
   • Rate Type: Real-time market rate
   • Conversion Method: Direct (using EURUSD pair)
   • Rate Timestamp: 2025-08-01 14:32:15 UTC

💡 Note: This is the mid-market rate. Actual trading rates may include spreads.
```

```
User: "How much is £2000 in Japanese Yen?"
Claude:
💰 Cross-Currency Conversion:

💷 £2,000.00 GBP → 💴 ¥278,450 JPY

📊 Conversion Details:
   • Via USD Cross-Rate:
     - GBP → USD: 1.2654 (GBPUSD)
     - USD → JPY: 110.25 (USDJPY)
   • Effective Rate: 139.225 (GBPJPY equivalent)
   • Conversion Method: Cross-currency via USD
   • Rate Timestamp: 2025-08-01 14:35:22 UTC
```

## 🛡️ Risk Management Examples

### Basic Stop Loss

```
User: "Set a stop loss on my Apple position at $175"
Claude:
🛡️ Stop Loss Order Placed:

📋 Order Details:
   • Symbol: AAPL (Apple Inc.)
   • Action: SELL (Protective Stop)
   • Quantity: 150 shares (full position)
   • Stop Price: $175.00
   • Order Type: STP (Stop Market)
   • Time in Force: GTC (Good Till Cancelled)

📊 Risk Analysis:
   • Current Price: $180.25
   • Stop Distance: -$5.25 (-2.91%)
   • Protection Level: $26,250.00
   • Max Loss from Current: -$787.50

✅ Order Status: Active and Monitoring
   • Order ID: 12345678
```

### Trailing Stop Loss

```
User: "Place a trailing stop on Tesla with 8% trail"
Claude:
🎯 Trailing Stop Order Placed:

📋 Order Details:
   • Symbol: TSLA (Tesla Inc.)
   • Action: SELL (Trailing Stop)
   • Quantity: 50 shares
   • Trail Percent: 8.00%
   • Current Stop Price: $219.79 (8% below $238.90)
   • Order Type: TRAIL
   • Time in Force: GTC

📈 Dynamic Protection:
   • If TSLA rises to $250: Stop adjusts to $230.00
   • If TSLA rises to $260: Stop adjusts to $239.20
   • Stop only moves up, never down

✅ Order Status: Active and Tracking
   • Order ID: 12345679
```

### Stop Loss Management

```
User: "Show me all my stop loss orders"
Claude:
🛡️ Active Stop Loss Orders:

🔹 AAPL Stop Loss:
   • Order ID: 12345678
   • Type: Stop Market at $175.00
   • Current Price: $180.25 | Distance: -2.91%
   • Status: Active ✅

🔹 TSLA Trailing Stop:
   • Order ID: 12345679  
   • Type: Trailing 8% (currently $219.79)
   • Current Price: $238.90 | Distance: -8.00%
   • Status: Active and Tracking ✅

📊 Portfolio Protection Summary:
   • Positions Protected: 2 of 5 (40%)
   • Total Protected Value: $38,187.50
   • Maximum Risk: $1,092.50 (2.86% of protected value)
```

## 📋 Order Management Examples

### Viewing Open Orders

```
User: "Show me my pending orders"
Claude:
📋 Open Orders (Account: DU1234567):

🔹 Buy Order - MSFT:
   • Order ID: 87654321
   • Type: Limit Buy at $420.00
   • Quantity: 25 shares
   • Status: Working (below market)
   • Current Price: $423.50
   • Time in Force: GTC
   • Submitted: 2025-08-01 09:30:15

🔹 Sell Order - GOOGL:
   • Order ID: 87654322
   • Type: Limit Sell at $175.00
   • Quantity: 10 shares  
   • Status: Working (above market)
   • Current Price: $172.80
   • Time in Force: DAY
   • Submitted: 2025-08-01 11:45:30

💡 2 orders working, estimated fill probability: MSFT 75%, GOOGL 25%
```

### Recent Executions

```
User: "Show me my recent trades"
Claude:
📈 Recent Executions (Last 24 Hours):

✅ TSLA - Buy Executed:
   • Quantity: 50 shares @ $238.90
   • Execution Time: 2025-08-01 10:15:22
   • Total Value: $11,945.00
   • Commission: $1.00
   • Venue: SMART/ISLAND

✅ EURUSD - Sell Executed:
   • Quantity: 25,000 @ 1.0845
   • Execution Time: 2025-08-01 13:22:15
   • Total Value: $27,112.50
   • Commission: $2.50
   • Venue: IDEALPRO

📊 Trading Summary:
   • Total Trades: 2
   • Total Volume: $39,057.50
   • Total Commissions: $3.50
```

## 🌍 International Trading Examples

### European Stocks

```
User: "Get quotes for SAP and Siemens"
Claude:
🇩🇪 German Stocks (XETRA):

🔹 SAP (SAP SE) - XETRA/EUR:
   • €134.25 (+€1.85, +1.40%)
   • Volume: 2.1M shares
   • USD Equivalent: ~$145.78
   • Market Cap: €164B

🔹 SIE (Siemens AG) - XETRA/EUR:
   • €178.90 (+€2.45, +1.39%)
   • Volume: 1.8M shares  
   • USD Equivalent: ~$194.32
   • Market Cap: €143B

📊 Session: 09:00-17:30 CET | Settlement: T+2
```

### Asian Market Hours

```
User: "What are the trading hours for Tokyo Stock Exchange?"
Claude:
🇯🇵 Tokyo Stock Exchange (TSE) Trading Hours:

⏰ Regular Sessions:
   • Morning: 09:00 - 11:30 JST
   • Lunch Break: 11:30 - 12:30 JST  
   • Afternoon: 12:30 - 15:00 JST

🌍 Time Zone Conversions (from JST):
   • EST/EDT: 19:00-01:30, 22:30-03:00 (previous day)
   • GMT/BST: 00:00-02:30, 03:30-06:00
   • CET/CEST: 01:00-03:30, 04:30-07:00

📋 Market Information:
   • Settlement: T+2
   • Currency: JPY
   • Market Status: Currently Open ✅ (14:25 JST)
```

## 💡 Advanced Usage Patterns

### Multi-Asset Portfolio Review

```
User: "Give me a complete portfolio analysis"
Claude:
📊 Complete Portfolio Analysis (DU1234567):

💰 Asset Allocation:
   • US Stocks: $67,245.30 (68.3%) 
   • International Stocks: $18,420.75 (18.7%)
   • Forex Positions: $8,950.20 (9.1%)
   • Cash: $3,834.50 (3.9%)

🌍 Geographic Diversification:
   • North America: 68.3%
   • Europe: 12.4% 
   • Asia Pacific: 6.3%
   • Cash/Other: 12.0%

💱 Currency Exposure:
   • USD: 77.2% | EUR: 15.1% | JPY: 4.8% | GBP: 2.9%

📈 Performance Metrics:
   • Today: +$1,247.30 (+1.28%)
   • Week: +$3,456.80 (+3.63%)
   • Month: -$892.45 (-0.90%)
   • YTD: +$12,450.75 (+14.5%)
```

### Cross-Currency Analysis

```
User: "Convert all my non-USD positions to USD equivalent"
Claude:
💱 Multi-Currency Position Analysis:

🇪🇺 EUR Positions → USD:
   • ASML: €10,500 → $11,399.30 (Rate: 1.0856)
   • Cash: €5,420.80 → $5,884.42
   • EUR Subtotal: $17,283.72

🇬🇧 GBP Positions → USD:  
   • VOD: £3,200 → $4,049.28 (Rate: 1.2654)
   • Cash: £2,150.60 → $2,721.71
   • GBP Subtotal: $6,770.99

🇯🇵 JPY Positions → USD:
   • 7203: ¥245,000 → $2,222.50 (Rate: 110.25)
   • Cash: ¥0 → $0.00
   • JPY Subtotal: $2,222.50

💵 Total Portfolio (USD): $98,450.75
   • USD Native: $72,173.54 (73.3%)
   • Converted: $26,277.21 (26.7%)
```

## 🆘 Error Handling Examples

### Connection Issues

```
User: "Check my connection"
Claude:
❌ IBKR Connection Issues Detected:

🔍 Diagnosis:
   • Status: Disconnected
   • Last Connection: 2025-08-01 12:45:30
   • Error: Connection refused (port 7497)

🛠️ Troubleshooting Steps:
   1. ✅ Check IB Gateway is running
   2. ✅ Verify port 7497 is correct for paper trading
   3. ✅ Ensure API is enabled in IB Gateway settings
   4. ✅ Check trusted IP addresses include 127.0.0.1

💡 Quick Fix: Restart IB Gateway and try again
```

### Trading Restrictions

```
User: "Buy 10000 shares of Apple"
Claude:
⚠️ Order Validation Failed:

🚫 Safety Limit Exceeded:
   • Requested: 10,000 shares AAPL
   • Order Value: ~$1,802,500
   • Account Limit: $10,000 per order
   • Buying Power: $48,450.30

✅ Suggested Alternatives:
   • Maximum Allowed: 55 shares ($9,913.75)
   • Scale into Position: Buy 55 shares now, more later
   • Increase Limits: Contact support to raise limits

💡 Safety features prevent accidental large orders
```

---

**Next Steps:**
- [Advanced Examples](advanced-trading.md) - Complex trading strategies
- [API Reference](../api/tools.md) - Complete tool documentation  
- [Trading Guide](../guides/trading.md) - Comprehensive trading workflows
