# Trading Guide

Complete workflows for using the IBKR MCP Server for global trading operations.

## Overview

This guide covers practical trading workflows using Claude AI with the IBKR MCP Server. All examples use paper trading for safety.

## Prerequisites

- IBKR MCP Server configured and connected
- Paper trading account recommended for learning
- Claude Desktop with IBKR tools enabled

## Basic Trading Workflow

### 1. Check Connection Status

Always start by verifying your connection:

```
"Check my IBKR connection status"
```

**Expected Response:**
```
✅ Connected to IBKR Paper Trading
• Server: 127.0.0.1:7497
• Account: DU1234567 (Paper Trading)
• Status: Active, all systems operational
```

### 2. Review Portfolio

Get an overview of your current positions:

```
"Show me my current portfolio"
```

**Response includes:**
- Current positions with quantities
- Market values and P&L
- Currency breakdown
- Total portfolio value

### 3. Check Account Balance

Understand your buying power:

```
"What's my account balance?"
```

**Response shows:**
- Available cash in multiple currencies
- Total portfolio value
- Buying power for new positions
- Margin information

## Market Data and Research

### Getting Stock Quotes

**Single Stock:**
```
"What's Apple trading at right now?"
```

**Multiple Stocks:**
```
"Get quotes for Apple, Microsoft, and Google"
```

**International Stocks:**
```
"Get quotes for ASML, Toyota, and SAP"
```

The system automatically detects the correct exchange and currency for international stocks.

### Currency Information

**Forex Rates:**
```
"What's the current EUR/USD rate?"
```

**Currency Conversion:**
```
"Convert $5000 to Euros"
```

**Multiple Forex Pairs:**
```
"Show me rates for EUR/USD, GBP/USD, and USD/JPY"
```

## Risk Management

### Setting Stop Losses

**Basic Stop Loss:**
```
"Set a stop loss on my Apple position at $175"
```

**Trailing Stop:**
```
"Place a trailing stop on Tesla with 8% trail"
```

**Stop Limit Order:**
```
"Set a stop limit on Microsoft: stop at $400, limit at $395"
```

### Managing Stop Orders

**View All Stop Orders:**
```
"Show me all my stop loss orders"
```

**Modify Stop Order:**
```
"Move my AAPL stop loss to $180"
```

**Cancel Stop Order:**
```
"Cancel my Tesla stop loss"
```

## International Trading

### European Markets

**Stock Quotes:**
```
"Get quotes for ASML and SAP"
```

**Market Information:**
```
"Where does ASML trade and in what currency?"
```

### Asian Markets

**Japanese Stocks:**
```
"What's Toyota (7203) trading at?"
```

**Currency Considerations:**
```
"Convert ¥500,000 to USD for comparison"
```

## Forex Trading

### Major Currency Pairs

**Get Live Rates:**
```
"Show me major forex pairs"
```

**Specific Pair Analysis:**
```
"What's the EUR/USD rate with bid/ask spread?"
```

### Cross-Currency Operations

**Complex Conversions:**
```
"How much is £2000 in Japanese Yen?"
```

**Portfolio Currency Analysis:**
```
"Convert all my EUR positions to USD equivalent"
```

## Order Management

### Viewing Orders

**Pending Orders:**
```
"Show me my pending orders"
```

**Recent Trades:**
```
"Show me my recent executions"
```

**Order History:**
```
"Show me today's completed orders"
```

## Advanced Workflows

### Portfolio Protection Strategy

1. **Assess Current Risk:**
```
"Show me my portfolio with current P&L"
```

2. **Set Stop Losses:**
```
"Set stop losses on all positions at 10% below cost"
```

3. **Monitor Protection:**
```
"Show me all my stop loss orders with current distances"
```

### Multi-Market Analysis

1. **Global Market Overview:**
```
"Get quotes for AAPL, ASML, Toyota, and Vodafone"
```

2. **Currency Impact Analysis:**
```
"Convert all international positions to USD"
```

3. **Risk Assessment:**
```
"What's my total exposure by currency?"
```

### Forex Arbitrage Research

1. **Rate Comparison:**
```
"Show me EUR/USD, EUR/GBP, and GBP/USD rates"
```

2. **Cross-Rate Analysis:**
```
"Calculate implied GBP/USD rate from EUR crosses"
```

3. **Opportunity Assessment:**
```
"Is there an arbitrage opportunity in these rates?"
```

## Safety Best Practices

### 1. Always Use Paper Trading for Learning

Start with paper trading to understand the system without financial risk.

### 2. Set Position Limits

Use stop losses to limit potential losses on all positions.

### 3. Diversify Across Markets

Don't concentrate all positions in a single market or currency.

### 4. Monitor Regularly

Check positions and stop orders regularly to ensure they're appropriate.

### 5. Understand Currency Risk

When trading international stocks, understand currency exposure.

## Common Trading Scenarios

### Scenario 1: US Stock with Stop Loss

```
1. "Get a quote for Apple"
2. "What's my buying power?"
3. [Decision to buy - done outside the system]
4. "Set a stop loss on my Apple position at $175"
5. "Show me my stop loss orders"
```

### Scenario 2: International Diversification

```
1. "Get quotes for ASML, SAP, and Toyota"
2. "Convert €10,000 to USD for US trading"
3. "Where do these international stocks trade?"
4. [Make investment decisions]
5. "Set trailing stops on international positions with 10% trail"
```

### Scenario 3: Forex Analysis

```
1. "Show me major forex pairs"
2. "Convert my EUR balance to USD"
3. "What's the 24-hour range for EUR/USD?"
4. "How much would €50,000 be worth in GBP?"
```

## Troubleshooting Common Issues

### Connection Problems

**Issue:** "Connection failed" errors
**Solution:** 
1. Check IB Gateway is running
2. Verify API settings are enabled
3. Restart IBKR MCP Server

### Order Issues

**Issue:** Stop loss orders not working
**Solution:**
1. Verify stop loss orders are enabled in configuration
2. Check order parameters are valid
3. Ensure sufficient position size

### Market Data Issues

**Issue:** Quotes not updating
**Solution:**
1. Check market hours for international stocks
2. Verify data subscriptions are active
3. Try refreshing the connection

## Next Steps

- **Risk Management:** Learn advanced stop loss strategies
- **International Trading:** Explore global market opportunities  
- **Forex Trading:** Understand currency pair relationships
- **Portfolio Analysis:** Monitor and optimize your positions

For more advanced strategies, see [Advanced Trading Examples](../examples/advanced-trading.md).

---

**Remember:** This system provides market data and order management capabilities. All trading decisions should be based on your own research and risk tolerance. Past performance does not guarantee future results.
