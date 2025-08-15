# International Markets Guide

Complete guide to trading global stocks across 12 international exchanges using the IBKR MCP Server.

## Overview

Trade stocks from around the world with automatic exchange detection and real-time quotes in native currencies. The system supports 23 pre-configured international symbols across major global markets.

## Supported Markets

### European Exchanges (6)

#### **Netherlands - AEB (Euronext Amsterdam)**
- **Trading Hours:** 09:00-17:30 CET
- **Currency:** EUR
- **Key Stocks:** ASML, Unilever, ING, Philips, Heineken
- **Settlement:** T+2

#### **Germany - XETRA (Frankfurt)**
- **Trading Hours:** 09:00-17:30 CET  
- **Currency:** EUR
- **Key Stocks:** SAP, Siemens, BMW, Adidas, Deutsche Bank
- **Settlement:** T+2

#### **United Kingdom - LSE (London)**
- **Trading Hours:** 08:00-16:30 GMT/BST
- **Currency:** GBP
- **Key Stocks:** Vodafone, BP, Shell, HSBC, Unilever
- **Settlement:** T+2

#### **France - SBF (Euronext Paris)**
- **Trading Hours:** 09:00-17:30 CET
- **Currency:** EUR
- **Key Stocks:** LVMH, Total, Sanofi, L'Oréal, Airbus
- **Settlement:** T+2

#### **Switzerland - SWX (SIX Swiss Exchange)**
- **Trading Hours:** 09:00-17:30 CET
- **Currency:** CHF
- **Key Stocks:** Nestlé, Novartis, Roche, UBS, Zurich Insurance
- **Settlement:** T+2

#### **Denmark - KFX (Nasdaq Copenhagen)**
- **Trading Hours:** 09:00-17:00 CET
- **Currency:** DKK
- **Key Stocks:** Novo Nordisk, Maersk, Carlsberg, Ørsted
- **Settlement:** T+2

### Asian & Pacific Exchanges (4)

#### **Japan - TSE (Tokyo Stock Exchange)**
- **Trading Hours:** 09:00-11:30, 12:30-15:00 JST (lunch break)
- **Currency:** JPY
- **Key Stocks:** Toyota (7203), Sony (6758), Honda, Nintendo (7974)
- **Settlement:** T+2

#### **Hong Kong - SEHK**
- **Trading Hours:** 09:30-12:00, 13:00-16:00 HKT (lunch break)
- **Currency:** HKD
- **Key Stocks:** Tencent (00700), TSMC (2330), Alibaba
- **Settlement:** T+2

#### **South Korea - KSE**
- **Trading Hours:** 09:00-15:30 KST
- **Currency:** KRW  
- **Key Stocks:** Samsung (005930), LG, SK Hynix, Hyundai
- **Settlement:** T+2

#### **Australia - ASX**
- **Trading Hours:** 10:00-16:00 AEST/AEDT
- **Currency:** AUD
- **Key Stocks:** BHP, Commonwealth Bank (CBA), Woolworths
- **Settlement:** T+2

## Getting International Stock Quotes

### Single Stock Quote

```
"What's ASML trading at?"
```

**Response:**
```
📊 ASML (ASML Holding NV) - AEB/EUR

💹 Current Quote:
   • Last: €650.80 (+€8.40, +1.31%)
   • Bid: €650.60 (Size: 200)
   • Ask: €651.00 (Size: 150)
   • Volume: 1.2M shares
   • USD Equivalent: ~$706.47
```

### Multiple International Stocks

```
"Get quotes for ASML, Toyota, and SAP"
```

**Mixed Market Response:**
- ASML from Netherlands (AEB/EUR)
- Toyota from Japan (TSE/JPY) 
- SAP from Germany (XETRA/EUR)

### Symbol Resolution

```
"Where does ASML trade?"
"Resolve Apple symbol"
"Find symbol for Microsoft Corporation"
```

**Enhanced Resolution Examples:**
```
🔍 Unified Symbol Resolution:

📊 ASML Resolution:
   • Symbol: ASML, Exchange: AEB/EUR (Primary)
   • Name: ASML Holding NV, Confidence: 1.0
   • Alternative: NASDAQ/USD (ADR)
   • Trading Hours: 09:00-17:30 CET

🍎 Apple Resolution (Fuzzy Search):
   • Symbol: AAPL, Exchange: SMART/USD
   • Name: Apple Inc., Confidence: 1.0
   • Resolution Method: fuzzy_search

🏢 Microsoft Resolution (Company Name):
   • Symbol: MSFT, Exchange: SMART/USD
   • Name: Microsoft Corporation, Confidence: 1.0
   • Resolution Method: fuzzy_search
```

## Pre-Configured International Symbols

### European Stocks (12)

**Netherlands (AEB):**
- **ASML** - ASML Holding NV (Semiconductor Equipment)
- **UNA** - Unilever NV (Consumer Goods)

**Germany (XETRA):**
- **SAP** - SAP SE (Enterprise Software)
- **SIE** - Siemens AG (Industrial Conglomerate)

**United Kingdom (LSE):**
- **VOD** - Vodafone Group Plc (Telecommunications)
- **BP** - BP Plc (Oil & Gas)
- **SHEL** - Shell Plc (Oil & Gas)

**France (SBF):**
- **MC** - LVMH (Luxury Goods)
- **TTE** - TotalEnergies (Oil & Gas)

**Switzerland (SWX):**
- **NESN** - Nestlé SA (Food & Beverages)
- **NOVN** - Novartis AG (Pharmaceuticals)

**Denmark (KFX):**
- **NOVO-B** - Novo Nordisk (Pharmaceuticals)

### Asian Stocks (8)

**Japan (TSE):**
- **7203** - Toyota Motor Corporation
- **6758** - Sony Group Corporation
- **7974** - Nintendo Co., Ltd.

**Hong Kong (SEHK):**
- **00700** - Tencent Holdings Limited
- **2330** - Taiwan Semiconductor Manufacturing (TSMC)

**South Korea (KSE):**
- **005930** - Samsung Electronics Co., Ltd.

**Australia (ASX):**
- **BHP** - BHP Group Limited (Mining)
- **CBA** - Commonwealth Bank of Australia

### Other Regions (3)

**Canada:**
- **SHOP** - Shopify Inc. (E-commerce)

**Brazil:**
- **VALE** - Vale SA (Mining)

**Israel:**
- **WDAY** - Workday Inc. (Software)

## Currency Considerations

### Understanding Multi-Currency Trading

When trading international stocks, you're exposed to both:
1. **Stock Performance** - The underlying company's performance
2. **Currency Performance** - Exchange rate movements

### Currency Impact Examples

**ASML Example:**
- Stock rises 5% in EUR: €600 → €630
- But EUR weakens 3% vs USD
- Net USD performance: ~+2%

### Managing Currency Risk

**Convert to USD for Comparison:**
```
"Convert €650 ASML share price to USD"
```

**Monitor Currency Impact:**
```
"What's the EUR/USD rate today vs last week?"
```

**Portfolio Currency Analysis:**
```
"Convert all my European positions to USD equivalent"
```

## International Trading Workflows

### European Stock Analysis

1. **Get European Market Overview:**
```
"Get quotes for ASML, SAP, and Nestlé"
```

2. **Currency Conversion:**
```
"Convert €10,000 to USD for comparison"
```

3. **Market Hours Check:**
```
"What time do European markets close?"
```

### Asian Market Trading

1. **Asian Market Snapshot:**
```
"Get quotes for Toyota, Samsung, and Tencent"
```

2. **Currency Analysis:**
```
"Convert ¥2,450 Toyota share to USD"
```

3. **Time Zone Considerations:**
```
"When do Asian markets open in US Eastern Time?"
```

### Global Diversification Strategy

1. **Multi-Market Overview:**
```
"Get quotes for AAPL, ASML, Toyota, Vodafone, and BHP"
```

2. **Currency Diversification:**
```
"What currencies am I exposed to in my portfolio?"
```

3. **Regional Analysis:**
```
"Compare my US vs European vs Asian holdings"
```

## Advanced International Features

### Automatic Exchange Detection

The system automatically identifies the correct exchange and currency:

**Simple Query:**
```
"Get quote for Toyota"
```

**System Response:**
- Recognizes Toyota as Japanese stock (7203)
- Routes to Tokyo Stock Exchange (TSE)
- Provides quote in JPY
- Includes USD equivalent

### Multi-Exchange Listings

Some companies trade on multiple exchanges:

**ASML Example:**
- Primary: AEB (Amsterdam) in EUR
- ADR: NASDAQ in USD
- System defaults to primary listing

### Real-Time vs Delayed Data

**Real-Time Data Available for:**
- Major European exchanges
- US markets (SMART routing)
- Large Asian stocks

**May Have Delays:**
- Smaller exchanges
- Less liquid stocks
- Depends on IBKR subscriptions

## Trading Hours by Region

### European Markets
- **Winter (CET):** 09:00-17:30
- **Summer (CEST):** 09:00-17:30
- **Overlap with US:** 09:30-11:30 EST

### Asian Markets
- **Tokyo:** 09:00-11:30, 12:30-15:00 JST
- **Hong Kong:** 09:30-12:00, 13:00-16:00 HKT
- **Seoul:** 09:00-15:30 KST
- **Sydney:** 10:00-16:00 AEST/AEDT

### Trading Strategy by Time Zone

**US Morning (Asian Afternoon):**
- Asian markets closing
- European markets opening
- Good for Asian position review

**US Midday (European Afternoon):**
- European markets active
- Best liquidity for European stocks
- Currency volatility higher

**US Evening (Asian Morning):**
- Asian markets opening
- European markets closed
- Focus on Asian positions

## International Trading Best Practices

### 1. Understand Local Market Conditions

Each market has unique characteristics:
- **European:** Regulated, stable, good liquidity
- **Asian:** Higher volatility, different business culture
- **Emerging:** Higher risk, potentially higher returns

### 2. Monitor Currency Risk

Track both stock and currency performance:
```
"Show me ASML performance in both EUR and USD"
```

### 3. Consider Time Zones

Plan trading around market hours:
- **European:** Trade in US morning
- **Asian:** Monitor overnight, trade during their day
- **Australian:** Overlaps with Asian session

### 4. Diversify Across Regions

Don't concentrate in single geographic region:
```
"What percentage of my portfolio is in each region?"
```

### 5. Use Local Currency Analysis

Understand company performance in local currency first:
```
"How has SAP performed in EUR over the past month?"
```

## Common International Trading Scenarios

### Scenario 1: European Tech Investment

```
1. "Get quotes for ASML and SAP"
2. "Convert €20,000 to USD equivalent"  
3. "What's the EUR/USD trend this week?"
4. "Compare ASML vs US semiconductor stocks"
```

### Scenario 2: Asian Market Diversification

```
1. "Get quotes for Toyota, Samsung, and Tencent"
2. "Convert all positions to USD for comparison"
3. "What's my total Asian market exposure?"
4. "How do Asian markets correlate with US markets?"
```

### Scenario 3: Currency Hedging Analysis

```
1. "Show me all my EUR-denominated positions"
2. "Convert total EUR exposure to USD"
3. "What's the EUR/USD volatility recently?"
4. "Should I hedge my EUR currency risk?"
```

## Risk Management for International Trading

### Currency Risk Management

**Assess Exposure:**
```
"What's my total exposure to EUR vs USD?"
```

**Monitor Volatility:**
```
"How volatile has GBP been vs USD recently?"
```

**Consider Hedging:**
- Natural hedging through diversification
- Currency futures (advanced)
- Currency-hedged ETFs (alternative)

### Political and Economic Risk

**Stay Informed About:**
- Political stability in target countries
- Economic policy changes
- Trade relationships
- Regulatory changes

### Liquidity Considerations

**Higher Liquidity:**
- Large-cap stocks on major exchanges
- During local market hours
- Popular international stocks

**Lower Liquidity:**
- Small-cap international stocks
- During off-hours trading
- Less popular markets

## Troubleshooting International Trading

### Quote Issues

**Problem:** International quotes not updating
**Solutions:**
1. Check local market hours
2. Verify exchange is open (holidays differ by country)
3. Confirm data subscriptions

### Currency Conversion Problems

**Problem:** Currency rates seem wrong
**Solutions:**
1. Check if rates are delayed
2. Verify currency pair is supported
3. Consider market volatility

### Symbol Recognition Issues

**Problem:** Stock symbol not recognized
**Solutions:**
1. Try different symbol format
2. Specify exchange explicitly
3. Check if stock is supported

## Integration with Other Features

### With Forex Trading

```
"Get EUR/USD rate before buying European stocks"
"Convert planned investment to local currency"
```

### With Risk Management

```
"Set stop losses on international positions"
"Monitor currency-adjusted P&L"
```

### With Portfolio Analysis

```
"Show portfolio breakdown by country"
"Calculate currency-adjusted returns"
```

## Next Steps

- **Market Research:** Learn about specific international markets
- **Currency Analysis:** Understand major currency trends
- **Risk Management:** Implement international position protection
- **Advanced Strategies:** Explore international arbitrage opportunities

For more complex international trading strategies, see [Advanced Trading Examples](../examples/advanced-trading.md).

---

**Important:** International trading involves additional risks including currency fluctuations, political risk, regulatory differences, and varying market conditions. Always research local market conditions and consider currency impact on your investments.
