# convert_currency

## Overview
Convert amounts between currencies using live exchange rates from Interactive Brokers.
Intelligently handles direct pairs, inverse pairs, and cross-currency calculations through USD.
Essential for portfolio analysis, international trading planning, and multi-currency account management.

The system automatically determines the best conversion method:
- Direct pairs (EURUSD for EUR→USD)
- Inverse pairs (1/EURUSD for USD→EUR) 
- Cross-currency (EUR→GBP via USD when EURGBP unavailable)

## Parameters

**amount**: The amount to convert (positive number)

**from_currency**: Source currency (3-letter code like "USD", "EUR", "GBP")

**to_currency**: Target currency (3-letter code like "USD", "EUR", "GBP")

Supported currencies include:
- **Major**: USD, EUR, GBP, JPY, CHF, AUD, CAD, NZD
- **Asian**: HKD, KRW, SGD
- **European**: DKK, SEK, NOK

## Examples

### Simple USD to EUR conversion
```python
convert_currency(1000.0, "USD", "EUR")
```
Returns: $1000 USD → €921.66 EUR (using live EURUSD rate)

### Multi-currency portfolio calculation
```python
convert_currency(50000.0, "JPY", "USD")
```
Converts Japanese Yen position to USD equivalent

### Cross-currency conversion
```python
convert_currency(500.0, "EUR", "GBP")
```
Converts EUR to GBP via USD when direct EURGBP pair unavailable

### Same currency (validation)
```python
convert_currency(1000.0, "USD", "USD")
```
Returns 1:1 conversion with no exchange rate lookup

## Workflow

**Portfolio Multi-Currency Analysis:**

1. **Get current positions**: Use get_portfolio to see all holdings
2. **Identify currencies**: Note which positions are in EUR, GBP, JPY, etc.
3. **Convert to base**: Convert all positions to your base currency (usually USD)
4. **Calculate totals**: Sum converted values for portfolio analysis
5. **Monitor changes**: Regular conversion to track FX impact on portfolio

**International Trading Preparation:**
1. **Check account balances**: See available cash in each currency
2. **Convert buying power**: Determine how much you can invest in target currency
3. **Plan position sizes**: Convert position sizes to local currency before trading
4. **Risk assessment**: Understand FX exposure in addition to stock risk

## Troubleshooting

### "Cannot get exchange rate" error
• Some currency pairs may not be available in paper trading
• System falls back to mock rates - check if rate seems reasonable
• Verify currency codes are correct (USD not US, EUR not EURO)

### "Amount must be positive" error
• Only positive amounts accepted for conversions
• Use absolute value if working with profit/loss calculations
• Zero amounts return zero conversion

### "Mock rate used" in response
• Normal in paper trading when IBKR returns NaN values
• Mock rates are realistic and updated regularly
• Switch to live account for real-time rates

### Conversion seems wrong
• Check if currencies are swapped (EUR/USD vs USD/EUR)
• Verify the rate direction matches your expectation
• Cross-currency conversions use two rates, small differences expected

### Rate is outdated
• Rates cached for 5 seconds for performance
• During market hours, rates refresh automatically
• Outside trading hours, shows last available rate

## Related Tools
• get_forex_rates - See current exchange rates before conversion
• get_portfolio - Check multi-currency positions requiring conversion
• get_account_summary - View account balances in different currencies
• resolve_symbol - Find exchange and currency for any symbol with fuzzy search
