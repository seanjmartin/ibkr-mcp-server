# Supported Markets Reference

Complete reference for all supported exchanges, currencies, and symbols in the IBKR MCP Server.

## 🌍 Global Exchanges (12 Total)

### European Exchanges (6)

#### **XETRA** (Frankfurt Stock Exchange)
- **Country**: Germany
- **Currency**: EUR
- **Trading Hours**: 09:00 - 17:30 CET
- **Settlement**: T+2
- **Sample Stocks**: SAP, Siemens, BMW, Adidas, Deutsche Bank
- **Market Cap**: €2.0+ trillion
- **Note**: Largest European exchange by trading volume

#### **LSE** (London Stock Exchange)
- **Country**: United Kingdom  
- **Currency**: GBP
- **Trading Hours**: 08:00 - 16:30 GMT/BST
- **Settlement**: T+2
- **Sample Stocks**: Vodafone, BP, Shell, HSBC, Unilever
- **Market Cap**: £3.0+ trillion
- **Note**: One of the world's oldest exchanges (1571)

#### **SBF** (Euronext Paris)
- **Country**: France
- **Currency**: EUR
- **Trading Hours**: 09:00 - 17:30 CET
- **Settlement**: T+2
- **Sample Stocks**: LVMH, Total, Sanofi, L'Oréal, Airbus
- **Market Cap**: €2.5+ trillion
- **Note**: Part of Euronext pan-European exchange

#### **AEB** (Euronext Amsterdam)
- **Country**: Netherlands
- **Currency**: EUR
- **Trading Hours**: 09:00 - 17:30 CET
- **Settlement**: T+2
- **Sample Stocks**: ASML, Unilever, ING, Philips, Heineken
- **Market Cap**: €1.0+ trillion
- **Note**: Home to ASML, world's largest semiconductor equipment maker

#### **SWX** (SIX Swiss Exchange)
- **Country**: Switzerland
- **Currency**: CHF
- **Trading Hours**: 09:00 - 17:30 CET
- **Settlement**: T+2
- **Sample Stocks**: Nestlé, Novartis, Roche, UBS, Zurich Insurance
- **Market Cap**: CHF 1.5+ trillion
- **Note**: Known for pharmaceutical and financial companies

#### **KFX** (Nasdaq Copenhagen)
- **Country**: Denmark
- **Currency**: DKK
- **Trading Hours**: 09:00 - 17:00 CET
- **Settlement**: T+2
- **Sample Stocks**: Novo Nordisk, Maersk, Carlsberg, Ørsted
- **Market Cap**: DKK 2.0+ trillion
- **Note**: Strong in shipping, pharmaceuticals, and renewable energy

### Asian & Pacific Exchanges (4)

#### **TSE** (Tokyo Stock Exchange)
- **Country**: Japan
- **Currency**: JPY
- **Trading Hours**: 09:00-11:30, 12:30-15:00 JST (lunch break)
- **Settlement**: T+2
- **Sample Stocks**: Toyota (7203), Sony, Honda, SoftBank, Nintendo
- **Market Cap**: ¥700+ trillion
- **Note**: World's third-largest exchange by market cap

#### **SEHK** (Stock Exchange of Hong Kong)
- **Country**: Hong Kong
- **Currency**: HKD
- **Trading Hours**: 09:30-12:00, 13:00-16:00 HKT (lunch break)
- **Settlement**: T+2
- **Sample Stocks**: Tencent (00700), TSMC (2330), Alibaba, China Mobile
- **Market Cap**: HKD 40+ trillion
- **Note**: Gateway to Chinese markets, tech-heavy

#### **KSE** (Korea Exchange)
- **Country**: South Korea
- **Currency**: KRW
- **Trading Hours**: 09:00 - 15:30 KST
- **Settlement**: T+2
- **Sample Stocks**: Samsung (005930), LG, SK Hynix, Hyundai
- **Market Cap**: KRW 2,000+ trillion
- **Note**: Tech and manufacturing focus

#### **ASX** (Australian Securities Exchange)
- **Country**: Australia
- **Currency**: AUD
- **Trading Hours**: 10:00 - 16:00 AEST/AEDT
- **Settlement**: T+2
- **Sample Stocks**: BHP, Commonwealth Bank (CBA), Woolworths, CSL
- **Market Cap**: AUD 2.5+ trillion
- **Note**: Resource and banking heavy

### Global Trading (2)

#### **SMART** (IBKR Smart Routing)
- **Country**: United States (Global Routing)
- **Currency**: USD (Primary)
- **Trading Hours**: 09:30 - 16:00 EST/EDT (regular), 04:00 - 20:00 (extended)
- **Settlement**: T+2
- **Coverage**: All major US exchanges (NASDAQ, NYSE, AMEX, etc.)
- **Note**: Intelligent order routing across all US venues

#### **IDEALPRO** (IBKR Forex Exchange)
- **Country**: Global
- **Currency**: Multiple (21 pairs)
- **Trading Hours**: 24/5 (Sunday 22:00 UTC - Friday 22:00 UTC)
- **Settlement**: T+2
- **Coverage**: 21 major and cross currency pairs
- **Note**: Institutional forex platform with tight spreads

## 💱 Forex Markets

### Supported Currency Pairs (21 Total)

#### **Major Pairs (7) - USD Based**
| Pair | Base | Quote | Name | Typical Spread | Min Size |
|------|------|-------|------|----------------|----------|
| EURUSD | EUR | USD | Euro/US Dollar | 0.1 pips | 25,000 |
| GBPUSD | GBP | USD | British Pound/US Dollar | 0.2 pips | 25,000 |
| USDJPY | USD | JPY | US Dollar/Japanese Yen | 0.1 pips | 25,000 |
| USDCHF | USD | CHF | US Dollar/Swiss Franc | 0.2 pips | 25,000 |
| AUDUSD | AUD | USD | Australian Dollar/US Dollar | 0.2 pips | 25,000 |
| USDCAD | USD | CAD | US Dollar/Canadian Dollar | 0.2 pips | 25,000 |
| NZDUSD | NZD | USD | New Zealand Dollar/US Dollar | 0.3 pips | 25,000 |

#### **Cross Pairs (14) - Non-USD**
| Pair | Base | Quote | Name | Typical Spread | Min Size |
|------|------|-------|------|----------------|----------|
| EURGBP | EUR | GBP | Euro/British Pound | 0.3 pips | 25,000 |
| EURJPY | EUR | JPY | Euro/Japanese Yen | 0.2 pips | 25,000 |
| GBPJPY | GBP | JPY | British Pound/Japanese Yen | 0.3 pips | 25,000 |
| CHFJPY | CHF | JPY | Swiss Franc/Japanese Yen | 0.4 pips | 25,000 |
| EURCHF | EUR | CHF | Euro/Swiss Franc | 0.3 pips | 25,000 |
| AUDJPY | AUD | JPY | Australian Dollar/Japanese Yen | 0.3 pips | 25,000 |
| CADJPY | CAD | JPY | Canadian Dollar/Japanese Yen | 0.4 pips | 25,000 |
| NZDJPY | NZD | JPY | New Zealand Dollar/Japanese Yen | 0.4 pips | 25,000 |
| EURAUD | EUR | AUD | Euro/Australian Dollar | 0.4 pips | 25,000 |
| EURNZD | EUR | NZD | Euro/New Zealand Dollar | 0.5 pips | 25,000 |
| GBPAUD | GBP | AUD | British Pound/Australian Dollar | 0.5 pips | 25,000 |
| GBPNZD | GBP | NZD | British Pound/New Zealand Dollar | 0.6 pips | 25,000 |
| AUDCAD | AUD | CAD | Australian Dollar/Canadian Dollar | 0.4 pips | 25,000 |
| AUDNZD | AUD | NZD | Australian Dollar/New Zealand Dollar | 0.4 pips | 25,000 |

### Supported Currencies (13 Total)

| Currency | Code | Name | Region | Major Pairs |
|----------|------|------|--------|-------------|
| US Dollar | USD | United States Dollar | Americas | 7 pairs |
| Euro | EUR | European Union Euro | Europe | 6 pairs |
| British Pound | GBP | British Pound Sterling | Europe | 4 pairs |
| Japanese Yen | JPY | Japanese Yen | Asia | 7 pairs |
| Swiss Franc | CHF | Swiss Franc | Europe | 3 pairs |
| Australian Dollar | AUD | Australian Dollar | Oceania | 5 pairs |
| Canadian Dollar | CAD | Canadian Dollar | Americas | 3 pairs |
| New Zealand Dollar | NZD | New Zealand Dollar | Oceania | 4 pairs |
| Hong Kong Dollar | HKD | Hong Kong Dollar | Asia | Cross-convert |
| Korean Won | KRW | South Korean Won | Asia | Cross-convert |
| Danish Krone | DKK | Danish Krone | Europe | Cross-convert |
| Swedish Krona | SEK | Swedish Krona | Europe | Cross-convert |
| Norwegian Krone | NOK | Norwegian Krone | Europe | Cross-convert |

**Note**: Currencies without direct pairs use cross-conversion via USD.

## 📈 International Symbols (23 Total)

### European Symbols (12)

#### **Netherlands (AEB)**
- **ASML** - ASML Holding NV (Semiconductor Equipment)
- **UNA** - Unilever NV (Consumer Goods)

#### **Germany (XETRA)**
- **SAP** - SAP SE (Enterprise Software)
- **SIE** - Siemens AG (Industrial Conglomerate)

#### **United Kingdom (LSE)**
- **VOD** - Vodafone Group Plc (Telecommunications)
- **BP** - BP Plc (Oil & Gas)
- **SHEL** - Shell Plc (Oil & Gas)

#### **France (SBF)**
- **MC** - LVMH (Luxury Goods)
- **TTE** - TotalEnergies (Oil & Gas)

#### **Switzerland (SWX)**
- **NESN** - Nestlé SA (Food & Beverages)
- **NOVN** - Novartis AG (Pharmaceuticals)

#### **Denmark (KFX)**
- **NOVO-B** - Novo Nordisk (Pharmaceuticals)

### Asian Symbols (8)

#### **Japan (TSE)**
- **7203** - Toyota Motor Corporation
- **6758** - Sony Group Corporation
- **7974** - Nintendo Co., Ltd.

#### **Hong Kong (SEHK)**
- **00700** - Tencent Holdings Limited
- **2330** - Taiwan Semiconductor Manufacturing (TSMC)

#### **South Korea (KSE)**
- **005930** - Samsung Electronics Co., Ltd.

#### **Australia (ASX)**
- **BHP** - BHP Group Limited (Mining)
- **CBA** - Commonwealth Bank of Australia

### Other Regions (3)

#### **Canada**
- **SHOP** - Shopify Inc. (E-commerce)

#### **Brazil**
- **VALE** - Vale SA (Mining)

#### **Israel**
- **WDAY** - Workday Inc. (Software)

## 🕐 Trading Hours by Region

### **European Markets**
- **Winter (CET)**: 09:00 - 17:30
- **Summer (CEST)**: 09:00 - 17:30
- **Pre-market**: 08:00 - 09:00 (some exchanges)
- **Post-market**: 17:30 - 18:30 (some exchanges)

### **Asian Markets**
- **Tokyo**: 09:00-11:30, 12:30-15:00 JST (lunch break)
- **Hong Kong**: 09:30-12:00, 13:00-16:00 HKT (lunch break)
- **Seoul**: 09:00 - 15:30 KST
- **Sydney**: 10:00 - 16:00 AEST/AEDT

### **American Markets**
- **Regular**: 09:30 - 16:00 EST/EDT
- **Pre-market**: 04:00 - 09:30 EST/EDT
- **After-hours**: 16:00 - 20:00 EST/EDT

### **Forex Markets**
- **24/7**: Sunday 22:00 UTC - Friday 22:00 UTC
- **Peak Hours**: London (08:00-17:00 GMT) + New York (13:00-22:00 GMT) overlap
- **Asian Session**: 22:00-08:00 GMT
- **London Session**: 08:00-17:00 GMT
- **New York Session**: 13:00-22:00 GMT

## 💰 Settlement & Clearing

### **Settlement Periods**
- **Most Markets**: T+2 (Trade date + 2 business days)
- **Some European Markets**: T+2
- **Forex**: T+2 (spot transactions)
- **US Markets**: T+2 (changed from T+3 in 2017)

### **Currency Settlement**
- **Multi-currency accounts**: Automatic currency conversion available
- **Currency balances**: Hold positions in native currencies
- **FX settlement**: Same day for major pairs
- **Cross-currency**: Via USD for complex conversions

## 📊 Market Data Specifications

### **Real-time Data**
- **Level I**: Last, bid, ask, volume, change
- **Updates**: Tick-by-tick for active symbols
- **Currencies**: Native currency plus USD equivalent
- **Extended data**: High, low, open, close, VWAP

### **Data Quality**
- **US Markets**: Real-time with IBKR subscriptions
- **International**: Real-time with exchange subscriptions
- **Paper Trading**: May have 15-minute delays
- **Forex**: Always real-time (included in IBKR)

### **Historical Data**
- **Timeframes**: 1 minute to monthly
- **History**: Up to 2 years for most symbols
- **Adjustments**: Split and dividend adjusted
- **Formats**: OHLCV bars, tick data available

## ⚠️ Important Notes

### **Market Access**
- **Subscriptions**: Some exchanges require paid data subscriptions
- **Permissions**: International trading permissions may be needed
- **Paper Trading**: Full access to all markets for testing
- **Live Trading**: Subject to account permissions and data subscriptions

### **Symbol Formats**
- **US Stocks**: Simple symbols (AAPL, MSFT, GOOGL)
- **International**: May include exchange suffix (ASML.AEB)
- **Forex**: 6-character format (EURUSD, GBPJPY)
- **Auto-detection**: System automatically resolves exchange/currency

### **Limitations**
- **Pink Sheets**: Not supported
- **Penny Stocks**: May have restrictions
- **IPO Stocks**: May not be immediately available
- **Delisted Stocks**: Removed from database

---

**Next Steps:**
- [Trading Guide](../guides/trading.md) - How to trade these markets
- [API Reference](../api/tools.md) - Technical tool documentation
- [Examples](../examples/basic-usage.md) - Practical trading examples
