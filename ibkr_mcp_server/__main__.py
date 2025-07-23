"""
Entry point for running IBKR MCP Server as a module.
This allows the package to be executed with: python -m ibkr_mcp_server
"""

from .main import cli

if __name__ == "__main__":
    cli() 