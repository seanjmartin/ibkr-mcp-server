# Forex Trading Guide

Complete guide to currency trading and conversion using the IBKR MCP Server.

## Overview

The IBKR MCP Server provides access to 21 major and cross currency pairs with real-time rates and intelligent conversion capabilities. This guide covers all forex-related functionality.

## Supported Currency Pairs

### Major Pairs (7)
- **EURUSD** - Euro/US Dollar
- **GBPUSD** - British Pound/US Dollar  
- **USDJPY** - US Dollar/Japanese Yen
- **USDCHF** - US Dollar/Swiss Franc
- **AUDUSD** - Australian Dollar/US Dollar
- **USDCAD** - US Dollar/Canadian Dollar
- **NZDUSD** - New Zealand Dollar/US Dollar

### Cross Pairs (14)
- **EURGBP** - Euro/British Pound
- **EURJPY** - Euro/Japanese Yen
- **GBPJPY** - British Pound/Japanese Yen
- **CHFJPY** - Swiss Franc/Japanese Yen
- **EURCHF** - Euro/Swiss Franc
- **AUDJPY** - Australian Dollar/Japanese Yen
- **CADJPY** - Canadian Dollar/Japanese Yen
- **NZDJPY** - New Zealand Dollar/Japanese Yen
- **EURAUD** - Euro/Australian Dollar
- **EURNZD** - Euro/New Zealand Dollar
- **GBPAUD** - British Pound/Australian Dollar
- **GBPNZD** - British Pound/New Zealand Dollar
- **AUDCAD** - Australian Dollar/Canadian Dollar
- **AUDNZD** - Australian Dollar/New Zealand Dollar

## Getting Forex Rates

### Single Currency Pair

```
"What's the current EUR/USD rate?"
```

**Response includes:**
- Current bid/ask prices
- Last traded price
- Daily change and percentage
- High/low for the session

### Multiple Pairs

```
"Show me rates for EUR/USD, GBP/USD, and USD/JPY"
```

**Displays:**
- All requested pairs with live rates
- Bid/ask spreads
- Daily performance
- Market session information

### All Major Pairs

```
"Show me all major forex pairs"
```

**Returns:**
- Complete overview of 7 major pairs
- Sorted by liquidity and trading volume
- Real-time rates with spreads

## Currency Conversion

### Simple Conversions

**USD to EUR:**
```
"Convert $1000 to Euros"
```

**EUR to GBP:**
```
"Convert €5000 to British Pounds"
```

**JPY to USD:**
```
"Convert ¥100,000 to US Dollars"
```

### Complex Cross-Currency Conversions

**GBP to JPY (via USD):**
```
"How much is £2000 in Japanese Yen?"
```

**CHF to AUD:**
```
"Convert 5000 Swiss Francs to Australian Dollars"
```

The system automatically handles cross-currency conversions using the most efficient routing via USD or direct pairs.

## Supported Currencies

The system supports conversion between these 13 currencies:

| Currency | Code | Full Name |
|----------|------|-----------|
| US Dollar | USD | United States Dollar |
| Euro | EUR | European Union Euro |
| British Pound | GBP | British Pound Sterling |
| Japanese Yen | JPY | Japanese Yen |
| Swiss Franc | CHF | Swiss Franc |
| Australian Dollar | AUD | Australian Dollar |
| Canadian Dollar | CAD | Canadian Dollar |
| New Zealand Dollar | NZD | New Zealand Dollar |
| Hong Kong Dollar | HKD | Hong Kong Dollar |
| South Korean Won | KRW | South Korean Won |
| Danish Krone | DKK | Danish Krone |
| Swedish Krona | SEK | Swedish Krona |
| Norwegian Krone | NOK | Norwegian Krone |

## Forex Trading Workflows

### Basic Rate Monitoring

1. **Check Key Pairs:**
```
"Show me EUR/USD, GBP/USD, and USD/JPY rates"
```

2. **Monitor Spreads:**
```
"What's the bid/ask spread on EUR/USD?"
```

3. **Track Daily Changes:**
```
"How much has GBP/USD moved today?"
```

### Currency Hedging Strategy

1. **Assess Currency Exposure:**
```
"Show me my portfolio in different currencies"
```

2. **Calculate Hedge Amounts:**
```
"Convert my €50,000 European stock position to USD"
```

3. **Monitor Hedge Effectiveness:**
```
"What's the current EUR/USD rate vs yesterday?"
```

### International Investment Analysis

1. **Convert Investment Amounts:**
```
"Convert $25,000 to Euros for European investing"
```

2. **Compare Costs Across Markets:**
```
"Convert €650 per ASML share to USD"
```

3. **Analyze Currency Impact:**
```
"If EUR strengthens 5% vs USD, what's my position worth?"
```

## Advanced Forex Features

### Cross-Rate Analysis

**Implied Rates:**
Calculate what GBP/JPY should be based on GBP/USD and USD/JPY:

```
"Show me GBP/USD and USD/JPY rates"
"What should GBP/JPY be based on these cross rates?"
```

### Multi-Currency Portfolio Management

**Portfolio Currency Breakdown:**
```
"Convert all my positions to USD equivalent"
```

**Currency Risk Assessment:**
```
"What's my total exposure to EUR vs USD?"
```

**Rebalancing Analysis:**
```
"If I convert €10,000 to USD, what's my new currency allocation?"
```

## Forex Market Hours

### Trading Sessions

**Asian Session:** 22:00-08:00 GMT
- Primary pairs: USD/JPY, AUD/USD, NZD/USD
- Lower volatility, range-bound trading

**London Session:** 08:00-17:00 GMT  
- Primary pairs: EUR/USD, GBP/USD, EUR/GBP
- Highest liquidity and volatility

**New York Session:** 13:00-22:00 GMT
- Overlap with London creates peak activity
- All major pairs highly active

**Best Trading Times:** London-New York overlap (13:00-17:00 GMT)

## Understanding Forex Quotes

### Reading Quotes

**EUR/USD: 1.0856**
- Base currency: EUR (1 Euro)
- Quote currency: USD (costs 1.0856 US Dollars)
- If rate increases, EUR is strengthening vs USD

### Bid/Ask Spreads

**EUR/USD Bid: 1.0855, Ask: 1.0857**
- Bid: Price dealers will buy EUR
- Ask: Price dealers will sell EUR
- Spread: 0.0002 (2 pips)

### Pip Values

- **Major pairs:** 1 pip = 0.0001
- **JPY pairs:** 1 pip = 0.01
- **USD/CHF:** 1 pip = 0.0001

## Risk Management in Forex

### Position Sizing

**Calculate Position Value:**
```
"If I trade 25,000 EUR/USD, what's the USD value?"
```

**Risk Assessment:**
```
"What's my risk if EUR/USD moves 100 pips against me?"
```

### Currency Correlation

**Correlated Pairs:**
- EUR/USD and GBP/USD often move together
- USD/JPY and AUD/USD often move opposite
- CHF pairs often move inverse to EUR pairs

## Common Forex Scenarios

### Scenario 1: European Investment Funding

```
1. "What's my USD balance?"
2. "What's the current EUR/USD rate?"
3. "Convert $50,000 to Euros"
4. "How much ASML stock can I buy with €46,000?"
```

### Scenario 2: Currency Risk Assessment

```
1. "Show me all my European stock positions"
2. "Convert my total EUR exposure to USD"
3. "What percentage of my portfolio is in EUR risk?"
4. "How much would a 5% EUR decline cost me?"
```

### Scenario 3: Arbitrage Research

```
1. "Show me EUR/USD and GBP/USD rates"
2. "What's the EUR/GBP cross rate?"
3. "Calculate implied EUR/GBP from USD crosses"
4. "Is there a discrepancy worth investigating?"
```

## Forex Trading Best Practices

### 1. Understand Market Hours
Trade during high-liquidity sessions for better spreads.

### 2. Monitor Economic Events
Major economic releases can cause significant currency moves.

### 3. Consider Correlations
Understand how different currency pairs relate to each other.

### 4. Use Appropriate Position Sizing
Forex can be highly volatile - size positions appropriately.

### 5. Account for Rollover Costs
Holding positions overnight incurs financing costs.

## Troubleshooting Forex Issues

### Rate Update Problems

**Issue:** Forex rates not updating
**Solution:**
1. Check market hours (forex markets are closed weekends)
2. Verify internet connection
3. Restart IBKR connection

### Conversion Errors

**Issue:** Currency conversion failing
**Solution:**
1. Verify both currencies are supported
2. Check for typos in currency codes
3. Ensure amount is reasonable (not zero or negative)

### Spread Issues

**Issue:** Very wide spreads on exotic pairs
**Solution:**
1. Focus on major pairs for better spreads
2. Trade during high-liquidity hours
3. Consider market conditions affecting specific currencies

## Integration with Stock Trading

### Currency Hedging

When trading international stocks, consider currency impact:

```
1. "Get quote for ASML in EUR"
2. "Convert position size to USD equivalent"  
3. "Monitor EUR/USD rate for currency risk"
```

### Multi-Currency Account Management

```
1. "Show me balances in all currencies"
2. "Convert excess EUR to USD for US trading"
3. "What's my total buying power in USD equivalent?"
```

## Next Steps

- **Advanced Analysis:** Learn to read currency trends and correlations
- **Risk Management:** Implement currency hedging strategies
- **Integration:** Combine forex analysis with international stock trading
- **Monitoring:** Set up regular forex rate monitoring workflows

For more complex forex strategies, see [Advanced Trading Examples](../examples/advanced-trading.md).

---

**Important:** Forex trading involves substantial risk. Currency values can fluctuate significantly based on economic, political, and market factors. Always trade with appropriate risk management and within your risk tolerance.
