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
2. "Where does SAP trade?" -> Exchange and currency detection with fallback
3. "Resolve CUSIP 037833100" -> Alternative identifier support
4. "Try XETRA for SAP" -> Exchange alias mapping (XETRA->IBIS/IBIS2)
```

## Enhanced Exchange Mapping System

### Smart Exchange Resolution
The system implements intelligent exchange mapping that automatically handles:
- **Standard Exchange Names**: FRANKFURT, LONDON, TOKYO work automatically
- **MIC Codes**: Market Identifier Codes (XETR, XLON, XTKS) mapped to working alternatives
- **Cascading Fallback**: User request → Exchange aliases → SMART routing
- **Regional Variants**: Different codes for stocks vs ETFs, domestic vs foreign

### Validated Exchange Mappings

#### European Markets
**Germany**:
- `FRANKFURT` → FWB (domestic) + FWB2 (foreign) segments
- `XETRA` → IBIS (stocks) + IBIS2 (ETFs) segments  
- `TRADEGATE` → TGATE (validated: TRADEGATE fails, TGATE works)

**Switzerland**:
- `SWISS` → EBS (validated: SWX fails, EBS works)
- MIC `XSWX` → EBS

**Sweden**:
- `STOCKHOLM` → SFB (validated: OMX fails, SFB works)
- MIC `XSTO` → SFB

**Italy**:
- `MILAN` → BVME (validated: BIT/MIL fail, BVME works)
- MIC `XMIL` → BVME

**United Kingdom**:
- `LONDON` → LSE (stocks) + LSEETF (ETFs)
- MIC `XLON` → LSE variants

#### North American Markets
**Canada**:
- `TORONTO` → TSE (validated: TSX fails, TSE works)
- MIC `XTSE` → TSE

**United States**:
- `NYSE` → NYSE + ARCA routing variants
- `NASDAQ` → NASDAQ + ISLAND routing variants
- MIC codes `XNYS`, `XNAS` → Working IBKR equivalents

#### Asian Markets
**Japan**:
- `TOKYO` → TSEJ (validated: TSE fails for Japan, TSEJ works)
- MIC `XTKS` → TSEJ

**India**:
- `INDIA` → NSE (validated: BSE fails, NSE works)
- MIC `XBOM`, `XNSE` → NSE

### Market Coverage (60+ Exchanges)
- **Europe (25+)**: Germany, UK, Switzerland, Sweden, Italy, Euronext, Nordic, Eastern Europe
- **North America (8+)**: US major exchanges + routing, Canada, Mexico
- **Asia (20+)**: Japan, China, Hong Kong, Singapore, India, Korea, Taiwan, Southeast Asia
- **Other Regions (12+)**: Australia, Brazil, Middle East, Africa
- **Special Systems (2)**: SMART routing, IDEALPRO forex

### Auto-Detection Examples
- "AAPL" -> SMART/USD (US - Apple)
- "ASML" -> AEB/EUR (Netherlands - ASML)
- "7203" -> TSEJ/JPY (Japan - Toyota) 
- "00700" -> SEHK/HKD (Hong Kong - Tencent)
- "005930" -> KSE/KRW (South Korea - Samsung)
- "SAP" -> IBIS/EUR (Germany - SAP)
- "VOD" -> LSE/GBP (UK - Vodafone)

### Exchange Mapping Examples
- User requests "SAP on XETRA" → System tries XETRA → Falls back to IBIS → Success
- User requests "Tesla on FRANKFURT" → System tries FRANKFURT → Falls back to FWB → Success
- User requests "Apple on XNYS" → System maps XNYS to NYSE → Success
- User requests "Toyota on TSE" → System maps TSE to TSEJ for Japan → Success

## Key Features

### Smart Symbol Resolution
- **Fuzzy Search**: "Apple" -> "AAPL"
- **Company Names**: "Microsoft" -> "MSFT"  
- **Alternative IDs**: CUSIP, ISIN, FIGI support
- **Confidence Scoring**: Multiple match ranking
- **Exchange Mapping**: Standard names and MIC codes work automatically
- **Cascading Fallback**: User request → Aliases → SMART routing
- **Regional Intelligence**: Domestic vs foreign, stocks vs ETFs

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
2. **Use Standard Names**: FRANKFURT, LONDON, TOKYO work automatically
3. **Trust Exchange Mapping**: System handles MIC codes and aliases transparently
4. **Use Fuzzy Search**: Company names when symbol unknown
5. **Check Alternatives**: Multiple exchanges for same company
6. **Verify Results**: Review confidence scores and resolution metadata

### Exchange Selection Best Practices
1. **Use Standard Names**: LONDON over LSE, FRANKFURT over FWB
2. **Let System Map**: MIC codes automatically converted to working alternatives
3. **Trust Fallbacks**: System tries aliases before failing
4. **Check Resolution Info**: See which exchange actually worked
5. **Leverage SMART**: Default routing when exchange uncertain

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
**Global Coverage**: 60+ exchanges with smart mapping, 21 forex pairs, 13 currencies  
**Enhanced Features**: Cascading exchange resolution, MIC code support, regional intelligence
