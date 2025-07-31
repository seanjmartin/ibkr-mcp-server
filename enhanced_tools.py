"""Enhanced MCP tools for IBKR functionality with Forex, International Markets, and Stop Loss Management."""

import json
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolRequest

from .client import ibkr_client
from .utils import validate_symbols, IBKRError


# Create the server instance
server = Server("ibkr-mcp")


# Define all tools (6 original + 8 new = 14 total)
TOOLS = [
    # ============ ORIGINAL TOOLS ============
    Tool(
        name="get_portfolio",
        description="Retrieve current portfolio positions and P&L from IBKR",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_account_summary", 
        description="Get account balances and key metrics from IBKR",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID (optional, uses current account if not specified)"}
            },
            "additionalProperties": False
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
            "required": ["account_id"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_accounts",
        description="Get available IBKR accounts and current account", 
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
    ),
    Tool(
        name="get_market_data",
        description="Get real-time market quotes for securities",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {"type": "string", "description": "Comma-separated list of symbols (e.g., AAPL,TSLA,GOOGL)"}
            },
            "required": ["symbols"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_connection_status",
        description="Check IBKR TWS/Gateway connection status and account information",
        inputSchema={"type": "object", "properties": {}, "additionalProperties": False}
    ),
    
    # ============ FOREX TRADING TOOLS ============
    Tool(
        name="get_forex_rates",
        description="Get real-time forex exchange rates for currency pairs",
        inputSchema={
            "type": "object",
            "properties": {
                "currency_pairs": {
                    "type": "string", 
                    "description": "Comma-separated forex pairs (e.g., EURUSD,GBPUSD,USDJPY)"
                }
            },
            "required": ["currency_pairs"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="convert_currency",
        description="Convert amount between currencies using live exchange rates",
        inputSchema={
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to convert"},
                "from_currency": {"type": "string", "description": "Source currency code (e.g., USD)"},
                "to_currency": {"type": "string", "description": "Target currency code (e.g., EUR)"}
            },
            "required": ["amount", "from_currency", "to_currency"],
            "additionalProperties": False
        }
    ),
    
    # ============ INTERNATIONAL TRADING TOOLS ============
    Tool(
        name="get_international_market_data",
        description="Get market data for international stocks with auto-detection",
        inputSchema={
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "string", 
                    "description": "Symbols with optional exchange.currency format (e.g., ASML,SAP.XETRA.EUR,00700)"
                },
                "auto_detect": {"type": "boolean", "description": "Auto-detect exchange and currency", "default": True}
            },
            "required": ["symbols"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="resolve_international_symbol",
        description="Resolve international symbol with comprehensive exchange and currency information",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol to resolve"},
                "exchange": {"type": "string", "description": "Specific exchange code (optional)"},
                "currency": {"type": "string", "description": "Specific currency code (optional)"}
            },
            "required": ["symbol"],
            "additionalProperties": False
        }
    ),
    
    # ============ STOP LOSS MANAGEMENT TOOLS ============
    Tool(
        name="place_stop_loss",
        description="Place stop loss order for risk management",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock symbol"},
                "exchange": {"type": "string", "description": "Exchange code", "default": "SMART"},
                "currency": {"type": "string", "description": "Currency code", "default": "USD"},
                "action": {"type": "string", "description": "Order action (BUY/SELL)", "default": "SELL"},
                "quantity": {"type": "integer", "description": "Number of shares"},
                "stop_price": {"type": "number", "description": "Stop trigger price"},
                "order_type": {"type": "string", "description": "Stop order type (STP/STP LMT/TRAIL)", "default": "STP"},
                "limit_price": {"type": "number", "description": "Limit price for STP LMT orders"},
                "trail_amount": {"type": "number", "description": "Trail amount for TRAIL orders"},
                "trail_percent": {"type": "number", "description": "Trail percentage for TRAIL orders"},
                "time_in_force": {"type": "string", "description": "Time in force (GTC/DAY)", "default": "GTC"}
            },
            "required": ["symbol", "quantity", "stop_price"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="get_stop_losses",
        description="Get existing stop loss orders with filtering options",
        inputSchema={
            "type": "object",
            "properties": {
                "account": {"type": "string", "description": "Account ID filter"},
                "symbol": {"type": "string", "description": "Symbol filter"},
                "status": {"type": "string", "description": "Order status filter (active/open/all)", "default": "active"}
            },
            "additionalProperties": False
        }
    ),
    Tool(
        name="modify_stop_loss",
        description="Modify existing stop loss order parameters",
        inputSchema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to modify"},
                "stop_price": {"type": "number", "description": "New stop price"},
                "quantity": {"type": "integer", "description": "New quantity"},
                "limit_price": {"type": "number", "description": "New limit price (for STP LMT)"},
                "trail_amount": {"type": "number", "description": "New trail amount"},
                "trail_percent": {"type": "number", "description": "New trail percentage"},
                "time_in_force": {"type": "string", "description": "New time in force"}
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    ),
    Tool(
        name="cancel_stop_loss",
        description="Cancel existing stop loss order",
        inputSchema={
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID to cancel"}
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    )
]


# Register tools list handler
@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


# Register tool call handler with enhanced routing for new tools
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls with enhanced routing for forex, international, and stop loss tools."""
    try:
        # ============ ORIGINAL TOOLS ============
        if name == "get_portfolio":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_portfolio(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting portfolio: {str(e)}"
                )]
                
        elif name == "get_account_summary":
            account = arguments.get("account")
            try:
                result = await ibkr_client.get_account_summary(account)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting account summary: {str(e)}"
                )]
                
        elif name == "switch_account":
            account_id = arguments["account_id"]
            try:
                result = await ibkr_client.switch_account(account_id)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error switching account: {str(e)}"
                )]
                
        elif name == "get_accounts":
            try:
                result = await ibkr_client.get_accounts()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting accounts: {str(e)}"
                )]
                
        elif name == "get_market_data":
            symbols = arguments["symbols"]
            try:
                result = await ibkr_client.get_market_data(symbols)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting market data: {str(e)}"
                )]
                
        elif name == "get_connection_status":
            try:
                result = await ibkr_client.get_connection_status()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting connection status: {str(e)}"
                )]
        
        # ============ FOREX TRADING TOOLS ============
        elif name == "get_forex_rates":
            currency_pairs = arguments["currency_pairs"]
            try:
                result = await ibkr_client.get_forex_rates(currency_pairs)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting forex rates: {str(e)}"
                )]
                
        elif name == "convert_currency":
            amount = arguments["amount"]
            from_currency = arguments["from_currency"]
            to_currency = arguments["to_currency"]
            try:
                result = await ibkr_client.convert_currency(amount, from_currency, to_currency)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error converting currency: {str(e)}"
                )]
        
        # ============ INTERNATIONAL TRADING TOOLS ============
        elif name == "get_international_market_data":
            symbols = arguments["symbols"]
            auto_detect = arguments.get("auto_detect", True)
            try:
                result = await ibkr_client.get_international_market_data(symbols, auto_detect)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting international market data: {str(e)}"
                )]
                
        elif name == "resolve_international_symbol":
            symbol = arguments["symbol"]
            exchange = arguments.get("exchange")
            currency = arguments.get("currency")
            try:
                result = await ibkr_client.resolve_international_symbol(symbol, exchange, currency)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error resolving international symbol: {str(e)}"
                )]
        
        # ============ STOP LOSS MANAGEMENT TOOLS ============
        elif name == "place_stop_loss":
            try:
                result = await ibkr_client.place_stop_loss(**arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error placing stop loss: {str(e)}"
                )]
                
        elif name == "get_stop_losses":
            account = arguments.get("account")
            symbol = arguments.get("symbol")
            status = arguments.get("status", "active")
            try:
                result = await ibkr_client.get_stop_losses(account, symbol, status)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error getting stop losses: {str(e)}"
                )]
                
        elif name == "modify_stop_loss":
            order_id = arguments["order_id"]
            changes = {k: v for k, v in arguments.items() if k != "order_id"}
            try:
                result = await ibkr_client.modify_stop_loss(order_id, **changes)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error modifying stop loss: {str(e)}"
                )]
                
        elif name == "cancel_stop_loss":
            order_id = arguments["order_id"]
            try:
                result = await ibkr_client.cancel_stop_loss(order_id)
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error cancelling stop loss: {str(e)}"
                )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]
