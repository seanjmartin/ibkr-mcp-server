#!/usr/bin/env python3
"""
Quick validation test for exchange mapping strategy implementation.
Tests the EXCHANGE_ALIASES mappings from the international manager.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ibkr_mcp_server'))

from ibkr_mcp_server.trading.international import InternationalManager

def test_exchange_mappings():
    """Test key exchange mappings from validation results"""
    
    # Get the EXCHANGE_ALIASES directly from the class
    aliases = InternationalManager.EXCHANGE_ALIASES
    
    print("=== Testing Key Exchange Mappings ===\n")
    
    # Test cases based on validation results from the strategy documents
    test_cases = [
        # German exchanges
        ('TRADEGATE', ['TGATE'], "German alternative - TRADEGATE fails, TGATE works"),
        ('XETRA', ['IBIS', 'IBIS2'], "German Xetra - MIC code fails, IBIS variants work"),
        ('FRANKFURT', ['FWB', 'FWB2'], "Frankfurt domestic vs foreign segments"),
        
        # Swiss exchanges  
        ('SWX', ['EBS'], "Swiss - SWX fails, EBS works"),
        ('SWISS', ['EBS'], "Swiss market - EBS only"),
        
        # Swedish exchanges
        ('OMX', ['SFB'], "Swedish - OMX fails, SFB works"),
        ('STOCKHOLM', ['SFB'], "Stockholm market - SFB only"),
        
        # Canadian exchanges
        ('TSX', ['TSE'], "Canadian - TSX fails, TSE works"),
        ('TORONTO', ['TSE'], "Toronto market - TSE only"),
        
        # Japanese exchanges
        ('TOKYO', ['TSEJ'], "Japanese - TSE fails for Japan, TSEJ works"),
        ('XTKS', ['TSEJ'], "Tokyo MIC code - maps to TSEJ"),
        
        # Italian exchanges
        ('BIT', ['BVME'], "Italian - BIT fails, BVME works"),
        ('MIL', ['BVME'], "Milan - MIL fails, BVME works"),
        ('MILAN', ['BVME'], "Milan market - BVME only"),
        
        # Indian exchanges
        ('BSE', ['NSE'], "Indian - BSE fails, NSE works"),
        ('INDIA', ['NSE'], "Indian market - NSE only"),
        
        # MIC code mappings
        ('XNYS', ['NYSE'], "NYSE MIC code - not supported, maps to NYSE"),
        ('XLON', ['LSE', 'LSEETF'], "London MIC code - maps to LSE variants"),
        ('XMIL', ['BVME'], "Milan MIC code - maps to BVME"),
    ]
    
    passed = 0
    failed = 0
    
    for exchange_code, expected_aliases, description in test_cases:
        actual_aliases = aliases.get(exchange_code)
        
        if actual_aliases == expected_aliases:
            print(f"✅ {exchange_code:12} → {expected_aliases} ({description})")
            passed += 1
        else:
            print(f"❌ {exchange_code:12} → Expected: {expected_aliases}, Got: {actual_aliases}")
            print(f"   Description: {description}")
            failed += 1
    
    print(f"\n=== Results ===")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total mappings in EXCHANGE_ALIASES: {len(aliases)}")
    
    # Show some additional stats
    print(f"\n=== Exchange Coverage ===")
    regions = {
        'German': ['FRANKFURT', 'XETRA', 'TRADEGATE', 'GETTEX', 'IBIS'],
        'UK': ['LONDON', 'LSE', 'LSEETF'],
        'Italian': ['MILAN', 'BIT', 'MIL', 'BVME'],
        'Swiss': ['SWISS', 'SWX', 'EBS'],
        'Canadian': ['TORONTO', 'TSX', 'TSE'],
        'Japanese': ['TOKYO', 'TSEJ'],
        'Indian': ['INDIA', 'BSE', 'NSE'],
        'MIC codes': ['XNYS', 'XNAS', 'XLON', 'XTKS', 'XMIL', 'XSWX']
    }
    
    for region, codes in regions.items():
        covered = sum(1 for code in codes if code in aliases)
        print(f"  {region:12}: {covered}/{len(codes)} exchanges mapped")
    
    return failed == 0

if __name__ == "__main__":
    success = test_exchange_mappings()
    sys.exit(0 if success else 1)
