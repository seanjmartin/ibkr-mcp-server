"""MCP tools for IBKR functionality."""

import json
from typing import List

from mcp.server import Server
from mcp.types import Tool, TextContent

from .client import ibkr_client
from .utils import validate_symbols, IBKRError


server = Server("ibkr-mcp")


@server.call_tool()
async def get_portfolio(account: str = None) -> List[TextContent]:
    """Get current portfolio positions from IBKR."""
    try:
        positions = await ibkr_client.get_portfolio(account)
        return [TextContent(
            type="text",
            text=json.dumps(positions, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting portfolio: {str(e)}"
        )]


@server.call_tool()
async def get_account_summary(account: str = None) -> List[TextContent]:
    """Get account summary from IBKR."""
    try:
        summary = await ibkr_client.get_account_summary(account)
        return [TextContent(
            type="text",
            text=json.dumps(summary, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting account summary: {str(e)}"
        )]


@server.call_tool()
async def switch_account(account_id: str) -> List[TextContent]:
    """Switch to a different IBKR account."""
    try:
        success = ibkr_client.switch_account(account_id)
        result = {
            "success": success,
            "message": f"{'Switched to' if success else 'Failed to switch to'} account: {account_id}",
            "current_account": ibkr_client.current_account,
            "available_accounts": ibkr_client.accounts
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error switching account: {str(e)}")]


@server.call_tool()
async def get_accounts() -> List[TextContent]:
    """Get available IBKR accounts."""
    try:
        accounts_info = ibkr_client.get_accounts()
        return [TextContent(type="text", text=json.dumps(accounts_info, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting accounts: {str(e)}")]


@server.call_tool()
async def check_shortable_shares(symbols: str) -> List[TextContent]:
    """Check short selling availability for a list of symbols."""
    try:
        symbol_list = validate_symbols(symbols)
        shortable_info = await ibkr_client.get_shortable_shares(symbol_list)
        
        return [TextContent(type="text", text=json.dumps(shortable_info, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error checking shortable shares: {str(e)}")]


@server.call_tool()
async def get_margin_requirements(symbols: str, account: str = None) -> List[TextContent]:
    """Get margin requirements for a list of symbols."""
    try:
        symbol_list = validate_symbols(symbols)
        margin_info = await ibkr_client.get_margin_requirements(symbol_list, account)
        
        return [TextContent(type="text", text=json.dumps(margin_info, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting margin requirements: {str(e)}")]


@server.call_tool()
async def short_selling_analysis(symbols: str, account: str = None) -> List[TextContent]:
    """Complete short selling analysis: availability, cost, margin requirements."""
    try:
        symbol_list = validate_symbols(symbols)
        
        # Get all short selling related data
        shortable_info = await ibkr_client.get_shortable_shares(symbol_list)
        margin_info = await ibkr_client.get_margin_requirements(symbol_list, account)
        
        # Combine all information
        analysis = {
            "account": account or ibkr_client.current_account,
            "symbols_analyzed": symbol_list,
            "shortable_shares": shortable_info,
            "margin_requirements": margin_info,
            "summary": {
                "total_symbols": len(symbol_list),
                "symbols_with_data": len([s for s in shortable_info.values() if "error" not in s]),
                "symbols_with_errors": len([s for s in shortable_info.values() if "error" in s])
            }
        }
        
        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in short selling analysis: {str(e)}")]


@server.call_tool()
async def get_connection_status() -> List[TextContent]:
    """Check IBKR connection status."""
    try:
        status = {
            "connected": ibkr_client.is_connected(),
            "host": ibkr_client.host,
            "port": ibkr_client.port,
            "client_id": ibkr_client.client_id,
            "current_account": ibkr_client.current_account,
            "available_accounts": ibkr_client.accounts,
            "paper_trading": ibkr_client.port in [7497, 4002]  # Common paper trading ports
        }
        
        return [TextContent(type="text", text=json.dumps(status, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting connection status: {str(e)}")]


# Register all tools
server.list_tools = lambda: [
    Tool(
        name="get_portfolio",
        description="Retrieve current portfolio positions and P&L from IBKR",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            }
        }
    ),
    Tool(
        name="get_account_summary",
        description="Get account balances and key metrics from IBKR",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            }
        }
    ),
    Tool(
        name="switch_account",
        description="Switch between IBKR accounts",
        inputSchema={
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Account ID to switch to"}
            },
            "required": ["account_id"]
        }
    ),
    Tool(
        name="get_accounts",
        description="Get available IBKR accounts and current account",
        inputSchema={"type": "object", "properties": {}}
    ),
    Tool(
        name="check_shortable_shares",
        description="Check short selling availability for securities",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated list of symbols (e.g., 'AAPL,TSLA,MSFT')"}
            },
            "required": ["symbols"]
        }
    ),
    Tool(
        name="get_margin_requirements",
        description="Get margin requirements for securities",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated list of symbols"},
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "required": ["symbols"]
        }
    ),
    Tool(
        name="short_selling_analysis",
        description="Complete short selling analysis: availability, margin requirements, and summary",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated list of symbols"},
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "required": ["symbols"]
        }
    ),
    Tool(
        name="get_connection_status",
        description="Check IBKR TWS/Gateway connection status and account information",
        inputSchema={"type": "object", "properties": {}}
    )
]
