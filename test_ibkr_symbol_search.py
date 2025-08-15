#!/usr/bin/env python3
"""
Quick test script to test IBKR's reqMatchingSymbols API directly.
This will help us understand what the native IBKR API provides for fuzzy symbol search.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'ibkr_mcp_server'))

from ib_async import IB, util

async def test_ibkr_symbol_search():
    """Test IBKR's reqMatchingSymbols API with various queries."""
    
    # Connect to IBKR
    ib = IB()
    
    # Test cases from the analysis report
    test_queries = [
        # US companies that should work
        "Apple",
        "Microsoft", 
        "Tesla",
        "Nvidia",
        "Snowflake",
        "Palantir",
        "Cloudflare",
        
        # European companies that fail in current implementation
        "Kongsberg",
        "Barclays", 
        "SAP",
        "ASML",
        "BMW",
        "Vodafone",
        "Lloyds",
        
        # Partial matches and typos
        "Appl",
        "Microsof",
        "Aple",
        
        # Explicit symbols for comparison
        "AAPL",
        "KOG.OSE",
        "BARC.LSE",
        "SAP.IBIS",
        "ASML.AEB"
    ]
    
    try:
        print("Connecting to IBKR...")
        await ib.connectAsync()
        print(f"Connected to IBKR: {ib.isConnected()}")
        
        results = {}
        
        for query in test_queries:
            print(f"\n=== Testing query: '{query}' ===")
            try:
                # Use the native IBKR reqMatchingSymbols API
                matches = await ib.reqMatchingSymbolsAsync(query)
                
                print(f"Found {len(matches)} matches:")
                for i, match in enumerate(matches[:5]):  # Show first 5 matches
                    contract_desc = match
                    contract = contract_desc.contract
                    print(f"  {i+1}. Symbol: {contract.symbol}")
                    print(f"     Exchange: {contract.exchange}")
                    print(f"     Currency: {contract.currency}")
                    print(f"     Name: {getattr(contract_desc, 'derivativeSecTypes', 'N/A')}")
                    print(f"     ConID: {contract.conId}")
                    print(f"     SecType: {contract.secType}")
                
                results[query] = {
                    'success': True,
                    'count': len(matches),
                    'matches': []
                }
                
                # Store first few matches for analysis
                for match in matches[:3]:
                    contract = match.contract
                    results[query]['matches'].append({
                        'symbol': contract.symbol,
                        'exchange': contract.exchange,
                        'currency': contract.currency,
                        'conId': contract.conId,
                        'secType': contract.secType
                    })
                    
            except Exception as e:
                print(f"Error searching for '{query}': {e}")
                results[query] = {
                    'success': False,
                    'error': str(e),
                    'count': 0,
                    'matches': []
                }
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY RESULTS")
        print("="*60)
        
        successful_queries = []
        failed_queries = []
        
        for query, result in results.items():
            if result['success'] and result['count'] > 0:
                successful_queries.append(query)
                print(f"✓ {query}: {result['count']} matches")
            else:
                failed_queries.append(query)
                print(f"✗ {query}: Failed or no matches")
        
        print(f"\nSuccess rate: {len(successful_queries)}/{len(test_queries)} ({len(successful_queries)/len(test_queries)*100:.1f}%)")
        
        # Analysis
        print("\n" + "="*60)
        print("ANALYSIS")
        print("="*60)
        
        print("\nUS Company Results:")
        us_companies = ["Apple", "Microsoft", "Tesla", "Nvidia", "Snowflake", "Palantir", "Cloudflare"]
        us_success = [q for q in us_companies if q in successful_queries]
        print(f"  Success: {len(us_success)}/{len(us_companies)} - {us_success}")
        
        print("\nEuropean Company Results:")
        eu_companies = ["Kongsberg", "Barclays", "SAP", "ASML", "BMW", "Vodafone", "Lloyds"]
        eu_success = [q for q in eu_companies if q in successful_queries]
        print(f"  Success: {len(eu_success)}/{len(eu_companies)} - {eu_success}")
        
        print("\nFuzzy Matching Results:")
        fuzzy_queries = ["Appl", "Microsof", "Aple"]
        fuzzy_success = [q for q in fuzzy_queries if q in successful_queries]
        print(f"  Success: {len(fuzzy_success)}/{len(fuzzy_queries)} - {fuzzy_success}")
        
        print("\nExplicit Symbol Results:")
        explicit_symbols = ["AAPL", "KOG.OSE", "BARC.LSE", "SAP.IBIS", "ASML.AEB"]
        explicit_success = [q for q in explicit_symbols if q in successful_queries]
        print(f"  Success: {len(explicit_success)}/{len(explicit_symbols)} - {explicit_success}")
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"ibkr_symbol_search_results_{timestamp}.txt"
        
        with open(results_file, 'w') as f:
            f.write("IBKR reqMatchingSymbols API Test Results\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write("="*60 + "\n\n")
            
            for query, result in results.items():
                f.write(f"Query: {query}\n")
                f.write(f"Success: {result['success']}\n")
                f.write(f"Count: {result['count']}\n")
                
                if result['success']:
                    for match in result['matches']:
                        f.write(f"  Match: {match}\n")
                else:
                    f.write(f"  Error: {result.get('error', 'Unknown')}\n")
                f.write("\n")
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure IBKR Gateway/TWS is running and connected")
        return None
        
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected from IBKR")

if __name__ == "__main__":
    print("IBKR Symbol Search API Test")
    print("="*40)
    print("This script tests IBKR's native reqMatchingSymbols API")
    print("to understand what symbol search capabilities are actually available.")
    print("")
    
    # Check if IBKR connection is likely available
    print("Prerequisites:")
    print("1. IBKR Gateway or TWS must be running")
    print("2. Must be logged in and connected")
    print("3. API settings must allow connections")
    print("")
    
    response = input("Continue with test? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        sys.exit(0)
    
    try:
        results = asyncio.run(test_ibkr_symbol_search())
        
        if results:
            print("\n" + "="*60)
            print("TEST COMPLETED SUCCESSFULLY")
            print("="*60)
            print("Now we know what IBKR's native API actually provides!")
            print("We can use this data to implement proper fuzzy search.")
        else:
            print("Test failed - check IBKR connection")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
