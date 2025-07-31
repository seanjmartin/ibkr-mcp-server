#!/usr/bin/env python3
"""Simple test to verify the IBKR MCP Server package is installed correctly."""

try:
    import ibkr_mcp_server
    print("SUCCESS: IBKR MCP Server package imported successfully")
    
    from ibkr_mcp_server.main import server
    print("SUCCESS: MCP server module imported successfully")
    
    print("\nInstallation verification complete!")
    print("The IBKR MCP Server is ready to use.")
    print("\nNext steps:")
    print("1. Configure your IBKR connection settings in the .env file")
    print("2. Start Interactive Brokers TWS or IB Gateway")
    print("3. Configure Claude Desktop to use this MCP server")
    
except Exception as e:
    print(f"ERROR: Import test failed: {e}")
    exit(1)
