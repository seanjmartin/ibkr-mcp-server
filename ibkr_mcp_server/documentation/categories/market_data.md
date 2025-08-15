# Market Data Category Documentation

## Overview
Market data tools provide real-time and on-demand access to global financial markets, including stocks, forex, and international securities with automatic exchange detection.

## Core Philosophy
- **Global Coverage**: Access markets worldwide with unified interface
- **Smart Resolution**: Automatic exchange and currency detection
- **Real-time Data**: Live quotes and market information
- **Multi-currency**: Native currency quotes plus USD equivalents

## Available Tools

### Market Data Tools
- **get_market_data**: Live stock quotes for global markets with automatic exchange detection
- **get_forex_rates**: Real-time forex rates for 21 major currency pairs  
- **resolve_symbol**: Universal symbol resolution with fuzzy search and company name matching

## Workflow Examples

### Basic Market Data Workflow
```
1. "Get quote for Apple" -> get_market_data
2. "What's the EUR/USD rate?" -> get_forex_rates  
3. "Where does ASML trade?" -> resolve_symbol
```

### Global Trading Research
```
1. "Get quotes for AAPL, ASML, Toyota" -> Mixed global markets
2. "Resolve Apple symbol" -> Company name to symbol resolution
3. "Convert quote to USD" -> Currency conversion for comparison
```

### International Symbol Resolution
```
1. "Find Microsoft symbol" -> Fuzzy search capability
2. "Where does SAP trade?" -> Exchange and currency detection
3. "Resolve CUSIP 037833100" -> Alternative identifier support
```

## Market Coverage

### Exchanges Supported (12 Total)
- **US**: SMART (all US stocks)
- **Europe**: XETRA, LSE, AEB, SBF, SWX, KFX  
- **Asia**: TSE, SEHK, KSE, ASX
- **Forex**: IDEALPRO (21 pairs)

### Auto-Detection Examples
- "AAPL" -> SMART/USD (US)
- "ASML" -> AEB/EUR (Netherlands)
- "7203" -> TSE/JPY (Japan - Toyota)
- "SAP" -> XETRA/EUR (Germany)

## Key Features

### Smart Symbol Resolution
- **Fuzzy Search**: "Apple" -> "AAPL"
- **Company Names**: "Microsoft" -> "MSFT"  
- **Alternative IDs**: CUSIP, ISIN, FIGI support
- **Confidence Scoring**: Multiple match ranking

### Multi-Currency Support  
- **Native Quotes**: Prices in local currency
- **USD Conversion**: Real-time USD equivalents
- **Cross-Currency**: 13 supported currencies
- **Rate Tracking**: Live forex rate integration

### Performance Features
- **Smart Caching**: Two-phase cache system
- **Rate Limiting**: API protection  
- **Auto-Detection**: Exchange/currency inference
- **Batch Requests**: Multiple symbols efficiently

## Best Practices

### Efficient Market Data Usage
1. **Use Auto-Detection**: Let system find correct exchange
2. **Batch Queries**: "Get quotes for AAPL,MSFT,GOOGL"
3. **Cache Awareness**: Repeated queries use cached data
4. **Currency Consistency**: Consider USD conversion for comparison

### Symbol Resolution Strategy
1. **Start Simple**: Try direct symbol first
2. **Use Fuzzy Search**: Company names when symbol unknown
3. **Check Alternatives**: Multiple exchanges for same company
4. **Verify Results**: Review confidence scores and metadata

### Global Market Considerations
1. **Market Hours**: Respect local trading hours
2. **Currency Impact**: Consider forex movements
3. **Settlement**: Different T+2 vs T+1 schedules
4. **Regulations**: Local market restrictions

## Error Handling
- **Invalid Symbols**: Graceful error with suggestions
- **Market Closed**: Clear status with next open time
- **Rate Limits**: Automatic retry with backoff
- **Network Issues**: Cached data when available

## Integration Patterns
Market data tools work together for comprehensive analysis:
- **Research**: resolve_symbol -> get_market_data -> get_forex_rates
- **Analysis**: Multiple quotes -> currency conversion -> comparison
- **Monitoring**: Real-time quotes -> rate changes -> alerts

---

**Related Categories**: forex, international, portfolio  
**Key Tools**: get_market_data, get_forex_rates, resolve_symbol  
**Global Coverage**: 12 exchanges, 21 forex pairs, 13 currencies
