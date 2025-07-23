"""IBKR MCP Server - Interactive Brokers Model Context Protocol Server."""

__version__ = "1.0.0"
__author__ = "Arjun Divecha"
__email__ = "your.email@example.com"
__description__ = "Interactive Brokers MCP Server for Claude Desktop/Code"

from .client import IBKRClient
from .main import main, cli

__all__ = ["IBKRClient", "main", "cli"]
