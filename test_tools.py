#!/usr/bin/env python3

# Test enhanced tools.py import
try:
    from ibkr_mcp_server.tools import TOOLS
    print(f"SUCCESS: {len(TOOLS)} MCP tools loaded")
    
    # List new tools
    tool_names = [tool.name for tool in TOOLS]
    print("Available tools:")
    for i, name in enumerate(tool_names, 1):
        print(f"  {i:2d}. {name}")
    
    # Check for new tools
    new_tools = ['get_forex_rates', 'convert_currency', 'get_international_market_data', 
                 'resolve_international_symbol', 'place_stop_loss', 'get_stop_losses', 
                 'modify_stop_loss', 'cancel_stop_loss']
    
    print(f"\nNew tools check:")
    for tool in new_tools:
        if tool in tool_names:
            print(f"  SUCCESS: {tool} found")
        else:
            print(f"  MISSING: {tool} not found")
            
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")
