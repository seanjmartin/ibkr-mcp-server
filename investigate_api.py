#!/usr/bin/env python3
"""Investigate ib-async API methods."""

from ib_async import IB

def main():
    ib = IB()
    
    print("=== Short selling related methods ===")
    short_methods = [method for method in dir(ib) if 'short' in method.lower()]
    for method in short_methods:
        print(f"  {method}")
    
    print("\n=== Account related methods ===")
    account_methods = [method for method in dir(ib) if 'account' in method.lower()]
    for method in account_methods:
        print(f"  {method}")
    
    print("\n=== Request methods (req*) ===")
    req_methods = [method for method in dir(ib) if method.startswith('req')]
    for method in sorted(req_methods):
        print(f"  {method}")
    
    print("\n=== Market data methods ===")
    market_methods = [method for method in dir(ib) if 'market' in method.lower() or 'tick' in method.lower() or 'data' in method.lower()]
    for method in sorted(market_methods):
        print(f"  {method}")

if __name__ == "__main__":
    main()
