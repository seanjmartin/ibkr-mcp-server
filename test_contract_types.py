#!/usr/bin/env python3
"""
Test international stock symbols through existing market data tool
and explore IBKR contract types
"""
from ib_async import Stock, Forex, Index, Future, Option

def test_contract_creation():
    """Test creating international contracts without connection"""
    
    print("IBKR International Exchange Support Test")
    print("=" * 50)
    
    print("\n1. European Stock Contracts:")
    european_stocks = [
        ("ASML", "AEB", "EUR", "ASML Holding - Netherlands"),
        ("SAP", "XETRA", "EUR", "SAP SE - Germany"), 
        ("NESN", "SWX", "CHF", "Nestle - Switzerland"),
        ("VOD", "LSE", "GBP", "Vodafone - UK"),
        ("MC", "SBF", "EUR", "LVMH - France"),
        ("UNA", "AEB", "EUR", "Unilever - Netherlands"),
        ("NOVO-B", "KFX", "DKK", "Novo Nordisk - Denmark"),
    ]
    
    print("   Available European exchanges:")
    for symbol, exchange, currency, description in european_stocks:
        try:
            stock = Stock(symbol, exchange, currency)
            print(f"   ✅ {stock} - {description}")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    print("\n2. Asian Stock Contracts:")
    asian_stocks = [
        ("7203", "TSE", "JPY", "Toyota Motor - Japan"),
        ("2330", "SEHK", "HKD", "Taiwan Semiconductor - Hong Kong"),
        ("005930", "KSE", "KRW", "Samsung Electronics - South Korea"),
        ("CBA", "ASX", "AUD", "Commonwealth Bank - Australia"),
        ("00700", "SEHK", "HKD", "Tencent - Hong Kong"),
        ("BHP", "ASX", "AUD", "BHP Group - Australia"),
    ]
    
    print("   Available Asian exchanges:")
    for symbol, exchange, currency, description in asian_stocks:
        try:
            stock = Stock(symbol, exchange, currency)
            print(f"   ✅ {stock} - {description}")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    print("\n3. International Forex Pairs:")
    forex_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", 
        "EURGBP", "EURJPY", "GBPJPY", "CHFJPY"
    ]
    
    print("   Available forex pairs:")
    for pair in forex_pairs:
        try:
            forex = Forex(pair)
            print(f"   ✅ {forex}")
        except Exception as e:
            print(f"   ❌ {pair}: {e}")
    
    print("\n4. International Indices:")
    indices = [
        ("DAX", "XETRA", "EUR", "German DAX"),
        ("FTSE", "LSE", "GBP", "FTSE 100"),
        ("N225", "TSE", "JPY", "Nikkei 225"),
        ("HSI", "SEHK", "HKD", "Hang Seng Index"),
    ]
    
    print("   Available international indices:")
    for symbol, exchange, currency, description in indices:
        try:
            index = Index(symbol, exchange, currency)
            print(f"   ✅ {index} - {description}")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    print("\n5. Trading Hours & Sessions:")
    print("   IBKR supports multiple trading sessions:")
    print("   - European markets: Generally 9:00-17:30 CET")
    print("   - Asian markets: Various times (JST, HKT, etc.)")
    print("   - Forex: 24/5 trading")
    print("   - Overlap trading possible across time zones")
    
    print("\n6. Account Currency & Settlement:")  
    print("   - Base currency conversion automatically handled")
    print("   - Multi-currency portfolio support")
    print("   - Settlement in local exchange currency")
    print("   - FX rates applied automatically")

if __name__ == "__main__":
    test_contract_creation()
