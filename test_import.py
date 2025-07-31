#!/usr/bin/env python3

# Quick import test for enhanced IBKR MCP Server
try:
    from ibkr_mcp_server.client import IBKRClient
    print("SUCCESS: Core client imports successfully")
    
    # Test trading managers
    from ibkr_mcp_server.trading.forex import ForexManager
    from ibkr_mcp_server.trading.international import InternationalManager
    from ibkr_mcp_server.trading.stop_loss import StopLossManager
    print("SUCCESS: Trading managers import successfully")
    
    # Test data modules
    from ibkr_mcp_server.data.forex_pairs import MAJOR_FOREX_PAIRS
    from ibkr_mcp_server.data.international_symbols import INTERNATIONAL_SYMBOLS
    from ibkr_mcp_server.data.exchange_info import EXCHANGE_INFO
    print("SUCCESS: Reference data imports successfully")
    
    print(f"SUCCESS: System Status: {len(MAJOR_FOREX_PAIRS)} forex pairs, {len(INTERNATIONAL_SYMBOLS)} intl symbols loaded")
    print("SUCCESS: All enhanced modules operational")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
