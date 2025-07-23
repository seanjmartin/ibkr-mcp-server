"""Main entry point for IBKR MCP Server."""

import asyncio
import logging
import signal
import sys
from typing import Optional

import click
from mcp.server.stdio import stdio_server
from rich.console import Console
from rich.logging import RichHandler

from .config import settings


console = Console()


class GracefulKiller:
    """Handle shutdown signals gracefully."""
    
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        console.print(f"[yellow]Received signal {signum}, shutting down gracefully...[/yellow]")
        self.kill_now = True


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    handlers = [RichHandler(console=console, show_time=True, show_path=False)]
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers
    )
    
    # Reduce noise from ib_async
    logging.getLogger('ib_async').setLevel(logging.WARNING)


async def test_connection():
    """Test IBKR connection and basic functionality."""
    console.print("[bold blue]🧪 Testing IBKR MCP Server...[/bold blue]")
    
    try:
        # Test connection - placeholder for actual implementation
        console.print("📡 Testing IBKR connection...")
        console.print("[green]✅ Connection test placeholder - needs full implementation[/green]")
        
        return True
    except Exception as e:
        console.print(f"[red]❌ Connection test failed: {e}[/red]")
        return False


@click.command()
@click.option('--test', is_flag=True, help='Test the server connection')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(test: bool, debug: bool):
    """IBKR MCP Server CLI."""
    
    # Setup logging
    log_level = "DEBUG" if debug else settings.log_level
    setup_logging(log_level, settings.log_file)
    
    if test:
        # Run connection test
        asyncio.run(test_connection())
        return
    
    # Run the MCP server
    console.print("[bold green]🚀 Starting IBKR MCP Server...[/bold green]")
    console.print(f"Host: {settings.ibkr_host}:{settings.ibkr_port}")
    console.print(f"Paper Trading: {'Yes' if settings.ibkr_is_paper else 'No'}")
    
    # Placeholder for actual server implementation
    console.print("[yellow]⚠️  Server implementation needs to be completed[/yellow]")
    console.print("This is a placeholder - full MCP server needs implementation")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
