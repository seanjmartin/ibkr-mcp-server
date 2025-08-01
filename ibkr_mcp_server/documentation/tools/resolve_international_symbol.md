# resolve_international_symbol

## Overview
Look up which exchange and currency an international stock trades on. Access a comprehensive
database of 25+ international symbols with automatic exchange and currency detection.
Essential for international trading preparation and multi-currency portfolio management.

Finds the correct exchange routing and currency denomination for stocks like ASML (AEB/EUR),
SAP (XETRA/EUR), Toyota (TSE/JPY), and many others across European and Asian markets.

## Parameters

**symbol**: Stock symbol to resolve (required)
- International stock symbols like "ASML", "SAP", "7203"
- Supports both alphabetic and numeric symbols
- Case-insensitive (ASML = asml)

**exchange**: Filter by specific exchange (optional)
- Specify exchange if you want to verify a particular listing
- Examples: "AEB", "XETRA", "TSE", "SEHK"

**currency**: Filter by specific currency (optional)
- Specify currency if you want to confirm currency denomination
- Examples: "EUR", "GBP", "JPY", "HKD"

## Examples

### Look up Dutch stock ASML
```python
resolve_international_symbol("ASML")
```
Returns: AEB (Amsterdam) exchange, EUR currency, full company details

### Verify German stock SAP
```python
resolve_international_symbol("SAP")
```
Returns: XETRA exchange, EUR currency, company information

### Look up Japanese stock Toyota
```python
resolve_international_symbol("7203")
```
Returns: TSE (Tokyo) exchange, JPY currency, Toyota Motor Corp details

### Verify specific exchange listing
```python
resolve_international_symbol("ASML", exchange="AEB")
```  
Confirms ASML trades on AEB exchange in EUR

### Check currency denomination
```python
resolve_international_symbol("00700", currency="HKD")
```
Verifies Tencent trades in Hong Kong Dollars

## Workflow

**International Trading Preparation:**

1. **Symbol discovery**: Look up correct exchange for target stocks
2. **Currency planning**: Understand currency denomination for positions
3. **Exchange routing**: Ensure correct exchange for optimal execution
4. **Market hours**: Plan trades around local exchange hours
5. **Integration**: Use with get_market_data for live prices

**Portfolio Analysis Process:**
1. **Position review**: Identify international holdings needing resolution
2. **Currency exposure**: Map positions to their currencies
3. **Exchange diversification**: Understand geographic distribution
4. **Conversion planning**: Plan currency conversions if needed

**Research Workflow:**
1. **Stock screening**: Find interesting international opportunities
2. **Exchange validation**: Verify where stocks trade
3. **Currency impact**: Understand FX exposure of potential positions
4. **Market access**: Confirm you can trade on target exchanges

## Troubleshooting

### "Symbol not found in database"
• Symbol may not be in the international database yet
• Try alternative symbol formats (with/without leading zeros)
• Some stocks may have different symbols on different exchanges
• Use explicit format: get_market_data("SYMBOL.EXCHANGE.CURRENCY")

### "Multiple listings found"
• Some stocks trade on multiple exchanges
• Response shows all available listings with different currencies
• Choose appropriate exchange based on your trading strategy
• Consider liquidity and trading hours for optimal exchange

### "Exchange information incomplete"
• Some exotic stocks may have limited metadata
• Basic exchange and currency information always provided
• Additional details like trading hours depend on database completeness
• Core trading information (exchange/currency) is always accurate

### "Numeric symbols confusing"
• Asian markets often use numeric symbols (7203, 005930, 00700)
• Include leading zeros as shown in examples
• Japanese stocks: 4-digit numbers (7203)
• Hong Kong stocks: 5-digit with leading zeros (00700)
• Korean stocks: 6-digit numbers (005930)

### "Currency doesn't match expectation"
• Some stocks may trade in different currency than country's main currency
• ADRs trade in USD even for foreign companies
• Some exchanges allow multi-currency trading
• Verify currency is correct for your intended trading strategy

## Related Tools
• get_market_data - Get live prices using resolved exchange/currency
• convert_currency - Convert prices to your base currency
• get_forex_rates - Monitor relevant currency exchange rates
• get_portfolio - Check international positions in your account

## Supported International Symbols

**European Markets:**
• ASML (AEB/EUR) - ASML Holding, Netherlands
• SAP (XETRA/EUR) - SAP SE, Germany  
• VOD (LSE/GBP) - Vodafone, UK
• MC (SBF/EUR) - LVMH, France
• NESN (SWX/CHF) - Nestle, Switzerland

**Asian Markets:**
• 7203 (TSE/JPY) - Toyota Motor, Japan
• 00700 (SEHK/HKD) - Tencent, Hong Kong
• 005930 (KSE/KRW) - Samsung Electronics, Korea
• CBA (ASX/AUD) - Commonwealth Bank, Australia

**And 15+ additional international symbols across major global exchanges**
