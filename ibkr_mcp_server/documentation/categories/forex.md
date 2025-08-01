# Forex Trading

## Overview
Complete forex trading and currency management system supporting 20+ major currency pairs.
The forex category includes tools for real-time rate monitoring, currency conversion, 
and comprehensive currency analysis for international portfolio management.

**Core Capabilities:**
• Real-time exchange rates for major, cross, and exotic currency pairs
• Intelligent currency conversion with multiple calculation methods  
• Rate caching for performance optimization
• Paper trading compatibility with mock rate fallbacks
• Integration with international trading and portfolio management

**Safety Note:** The system prioritizes rate monitoring and conversion for analysis 
and planning purposes. All currency operations include comprehensive validation.

## Tools
• get_forex_rates - Monitor real-time exchange rates
• convert_currency - Convert amounts between currencies

## Supported Pairs
**Major Pairs** (highest liquidity):
EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD

**Cross Pairs** (no USD):
EURGBP, EURJPY, GBPJPY, CHFJPY, EURCHF, AUDJPY, CADJPY, NZDJPY

**Exotic Pairs** (wider spreads):
EURNZD, GBPAUD, GBPNZD, AUDCAD, AUDNZD

**Trading Hours:** 24/5 (Sunday 5pm ET - Friday 5pm ET)
**Best Trading Times:** London (8am-12pm GMT), New York (1pm-5pm GMT) overlap

## Workflow
**Complete Forex Analysis Workflow:**

**Phase 1: Market Analysis**
1. Monitor major pairs with get_forex_rates
2. Analyze bid/ask spreads for liquidity assessment
3. Check correlation between related pairs
4. Use convert_currency to calculate position values

**Phase 2: Portfolio Integration**
1. Review international positions requiring currency conversion
2. Calculate FX exposure across portfolio
3. Monitor currency hedging opportunities
4. Assess impact of FX moves on total returns

**Phase 3: Planning & Analysis**
1. Plan international trades with proper currency consideration
2. Calculate real returns including FX impact
3. Review performance and refine currency strategy
4. Monitor for optimal conversion timing

**Best Practices:**
• Start with major pairs for tightest spreads
• Understand correlation between currency pairs
• Use economic calendar for high-impact events
• Consider FX impact on international investments
• Monitor central bank policy changes

## Market Characteristics
**Forex Market Unique Features:**
• 24-hour trading Sunday 5pm ET - Friday 5pm ET
• Highest liquidity during London/New York overlap
• Affected by central bank policies and economic data
• No central exchange - over-the-counter market
• Critical component of international investing

**Currency Influences:**
• Interest rate differentials between countries
• Economic indicators (GDP, inflation, employment)
• Central bank interventions and policy changes
• Political stability and geopolitical events
• Risk sentiment and safe-haven flows
