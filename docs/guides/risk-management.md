# Risk Management Guide

Comprehensive guide to portfolio protection and risk management using stop losses and safety features.

## Overview

Risk management is crucial for successful trading. The IBKR MCP Server provides advanced stop loss capabilities, emergency controls, and comprehensive safety monitoring to protect your investments.

## Types of Stop Loss Orders

### 1. Basic Stop Loss (STP)

A market order triggered when price hits your stop level.

**Example:**
```
"Set a stop loss on my Apple position at $175"
```

**Characteristics:**
- Executes as market order when triggered
- Guaranteed execution but not guaranteed price
- Best for liquid stocks during market hours

### 2. Stop Limit Orders (STP LMT)

A limit order triggered when price hits your stop level.

**Example:**
```
"Set a stop limit on Microsoft: stop at $400, limit at $395"
```

**Characteristics:**
- More control over execution price
- May not execute if price gaps beyond limit
- Better for volatile stocks

### 3. Trailing Stop Orders (TRAIL)

Stop level automatically adjusts as price moves favorably.

**Example:**
```
"Place a trailing stop on Tesla with 8% trail"
```

**Characteristics:**
- Follows price up, never down
- Captures more of upward moves
- Ideal for trending stocks

## Setting Up Stop Losses

### Basic Stop Loss Setup

1. **Check Current Position:**
```
"Show me my current Apple position"
```

2. **Set Stop Loss:**
```
"Set a stop loss on Apple at $175"
```

3. **Confirm Order:**
```
"Show me my stop loss orders"
```

### Advanced Stop Loss Parameters

**Complete Stop Loss Order:**
```
"Set a stop limit on AAPL: 100 shares, stop at $180, limit at $178, good till cancelled"
```

**Parameters Explained:**
- **Symbol:** AAPL
- **Quantity:** 100 shares  
- **Stop Price:** $180 (trigger level)
- **Limit Price:** $178 (execution limit)
- **Time in Force:** GTC (Good Till Cancelled)

### Trailing Stop Configuration

**Percentage-Based Trailing Stop:**
```
"Place a trailing stop on Microsoft with 10% trail"
```

**Dollar-Amount Trailing Stop:**
```
"Set a trailing stop on Google with $25 trail amount"
```

**How Trailing Stops Work:**
- If MSFT at $400, 10% trail sets stop at $360
- If MSFT rises to $450, stop adjusts to $405  
- If MSFT falls to $405, stop order triggers
- Stop never moves down, only up

## Managing Stop Loss Orders

### Viewing All Stop Orders

```
"Show me all my stop loss orders"
```

**Response includes:**
- Order ID and symbol
- Order type and parameters
- Current trigger distance
- Order status and time remaining

### Modifying Stop Orders

**Change Stop Price:**
```
"Move my Apple stop loss to $185"
```

**Adjust Trailing Percentage:**
```
"Change my Tesla trailing stop to 12%"
```

**Modify Quantity:**
```
"Reduce my Microsoft stop loss to 50 shares"
```

### Canceling Stop Orders

**Cancel Specific Order:**
```
"Cancel my Tesla stop loss order"
```

**Cancel All Stops for Symbol:**
```
"Cancel all Apple stop loss orders"
```

## Portfolio Protection Strategies

### 1. Systematic Stop Loss Placement

**Set Stops on All Positions:**
```
"Show me my portfolio"
"Set stop losses on all positions at 10% below cost"
```

**Benefits:**
- Consistent risk management
- Prevents emotional decision-making
- Limits maximum loss per position

### 2. Tiered Stop Loss Strategy

**Multiple Stop Levels:**
```
"Set stop loss on half my Apple position at $175"
"Set stop loss on remaining Apple at $165"
```

**Advantages:**
- Partial profit protection
- Allows for position size adjustment
- Reduces whipsaw risk

### 3. Trailing Stop Implementation

**For Trending Positions:**
```
"Place trailing stops on profitable positions with 15% trail"
```

**Best For:**
- Capturing extended moves
- Letting winners run
- Automatic profit protection

## Advanced Risk Management

### Position Sizing with Stop Losses

**Calculate Risk Before Entry:**
```
"If I buy 100 shares of Apple at $180 with stop at $170, what's my risk?"
```

**Answer:** $1,000 maximum loss (100 shares × $10 difference)

**Risk-Based Position Sizing:**
- Decide maximum loss per trade (e.g., 2% of portfolio)
- Calculate position size based on stop distance
- Example: $100,000 portfolio, 2% risk = $2,000 max loss
- If stop is $10 away, maximum position = 200 shares

### Portfolio-Level Risk Management

**Assess Total Risk:**
```
"Show me all my stop loss orders with total protected value"
```

**Calculate Concentration Risk:**
```
"What percentage of my portfolio is in tech stocks?"
```

**Monitor Correlation Risk:**
```
"Show me my positions in correlated stocks"
```

### Currency Risk Management

**For International Positions:**
```
"Convert my ASML position to USD equivalent"
"What's my total EUR exposure?"
"Set stop losses on international positions accounting for currency risk"
```

## Emergency Risk Controls

### Kill Switch Activation

**Emergency Stop All Trading:**
```
"Activate emergency kill switch due to market volatility"
```

**Features:**
- Immediately halts all new trading
- Requires manual override to reactivate
- Complete audit trail of activation
- Safety-first approach to risk management

### Daily Limits Monitoring

**Check Daily Activity:**
```
"Show me my daily trading statistics"
```

**Automatic Protections:**
- Maximum orders per day
- Maximum trading volume limits
- Rate limiting for API protection
- Audit logging of all activities

## Risk Monitoring and Alerts

### Stop Loss Monitoring

**Current Protection Status:**
```
"Show me portfolio protection summary"
```

**Response includes:**
- Positions with stop losses
- Positions without protection
- Total protected value
- Maximum potential loss

### Risk Metrics Tracking

**Position Risk Analysis:**
```
"What's my maximum risk if all stops are triggered?"
```

**Portfolio Heat Map:**
```
"Show me my riskiest positions"
```

## Common Risk Management Scenarios

### Scenario 1: New Position Protection

```
1. "Buy 100 shares of Apple at current market price"
2. "Set a stop loss at 8% below my purchase price"
3. "Show me my new risk profile"
```

### Scenario 2: Profit Protection

```
1. "Show me my profitable positions"
2. "Place trailing stops on profitable positions with 12% trail"
3. "Monitor trailing stop adjustments"
```

### Scenario 3: Portfolio Rebalancing

```
1. "Show me my portfolio by sector concentration"
2. "Set tighter stops on overweight positions"
3. "Use stop proceeds to rebalance portfolio"
```

### Scenario 4: Market Volatility Response

```
1. "Check VIX and market volatility"
2. "Tighten stop losses during high volatility periods"
3. "Consider activating kill switch if needed"
```

## Best Practices for Risk Management

### 1. Always Use Stop Losses

**Never Trade Without Protection:**
- Set stops immediately after entry
- Use appropriate stop distance (5-15% typically)
- Don't move stops against your position

### 2. Position Sizing Discipline

**Risk-Based Sizing:**
- Never risk more than 1-2% of portfolio per trade
- Larger positions require tighter stops
- Smaller positions allow wider stops

### 3. Diversification

**Spread Risk Across:**
- Different sectors
- Different countries/currencies
- Different time horizons
- Different market capitalizations

### 4. Regular Review and Adjustment

**Weekly Risk Review:**
```
"Show me my weekly risk summary"
"Are any positions becoming too large?"
"Do I need to adjust any stop losses?"
```

### 5. Emotional Discipline

**Stick to Your Rules:**
- Don't cancel stops in panic
- Don't move stops against your position
- Accept small losses to avoid large ones
- Let the system protect you

## Risk Management Mistakes to Avoid

### 1. Moving Stops Against Your Position

**Wrong:** Stock drops, move stop lower to "give it more room"
**Right:** Accept the loss and move on

### 2. Not Using Stops

**Wrong:** "I'll just watch it closely"
**Right:** Set stops automatically and systematically

### 3. Position Size Too Large

**Wrong:** Risk 10% of portfolio on one trade
**Right:** Risk 1-2% maximum per trade

### 4. Inadequate Diversification

**Wrong:** All positions in same sector
**Right:** Spread across sectors, countries, currencies

### 5. Emotional Decision Making

**Wrong:** Cancel stops because "feeling lucky"
**Right:** Trust your system and rules

## Integration with Trading Workflows

### With Market Analysis

```
1. "Analyze potential Apple entry point"
2. "Calculate stop loss level before buying"
3. "Determine position size based on risk"
4. "Execute trade with stop loss protection"
```

### With Portfolio Management

```
1. "Review current portfolio risk"
2. "Identify unprotected positions"
3. "Set appropriate stop losses"
4. "Monitor and adjust as needed"
```

### With International Trading

```
1. "Account for currency risk in international positions"
2. "Set stops in local currency"
3. "Monitor currency-adjusted risk"
4. "Consider hedging large exposures"
```

## Advanced Risk Concepts

### Value at Risk (VaR)

**Portfolio VaR Estimation:**
```
"What's my maximum likely loss over next month?"
```

**Position-Level Risk:**
```
"What's the 95% confidence maximum loss on my Apple position?"
```

### Correlation Risk

**Monitor Related Positions:**
```
"Show me my tech stock correlation risk"
"How correlated are my international positions?"
```

### Black Swan Protection

**Tail Risk Management:**
- Keep some cash reserves
- Consider portfolio insurance
- Don't be over-leveraged
- Maintain diversification

## System Safety Features

### Automatic Protections

**Built-in Safety Measures:**
- Daily trading limits
- Order size limits
- Rate limiting protection
- Emergency kill switch
- Complete audit logging

### Audit Trail

**Risk Management History:**
```
"Show me my stop loss history"
"Review my risk management performance"
```

## Next Steps

- **Practice:** Start with small positions and basic stops
- **Education:** Learn about different order types
- **Refinement:** Develop your risk management style
- **Monitoring:** Regular review and adjustment

Remember: The goal of risk management is not to eliminate risk, but to manage it intelligently and systematically.

---

**Key Principle:** Successful trading is not about being right all the time - it's about cutting losses quickly and letting profits run. Stop losses are your best friend in achieving this goal.
