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

from .client import ibkr_client
from .config import settings
from .tools import server


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
        # Test connection
        console.print("📡 Testing IBKR connection...")
        await ibkr_client.connect()
        console.print("✅ IBKR connection successful")
        
        # Test account discovery
        console.print("🔍 Discovering accounts...")
        accounts = ibkr_client.get_accounts()
        console.print(f"✅ Found accounts: {accounts['available_accounts']}")
        console.print(f"📊 Current account: {accounts['current_account']}")
        
        # Test basic portfolio data
        console.print("📈 Testing portfolio data...")
        try:
            portfolio = await ibkr_client.get_portfolio()
            console.print(f"✅ Portfolio loaded: {len(portfolio)} positions")
        except Exception as e:
            console.print(f"⚠️ Portfolio test failed: {e}")
        
        # Test account summary
        console.print("💰 Testing account summary...")
        try:
            summary = await ibkr_client.get_account_summary()
            console.print(f"✅ Account summary loaded: {len(summary)} items")
        except Exception as e:
            console.print(f"⚠️ Account summary test failed: {e}")
        
        console.print("\n[bold green]🎉 All tests passed! Server is ready.[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Test failed: {e}[/bold red]")
        return False
    finally:
        await ibkr_client.disconnect()
    
    return True


async def run_server():
    """Run the MCP server with connection management."""
    logger = logging.getLogger(__name__)
    killer = GracefulKiller()
    
    console.print("[bold blue]🚀 Starting IBKR MCP Server...[/bold blue]")
    
    while not killer.kill_now:
        try:
            # Connect to IBKR
            console.print("📡 Connecting to IBKR...")
            await ibkr_client.connect()
            console.print("✅ IBKR connection established")
            
            # Start MCP server
            console.print("🔧 Starting MCP server...")
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break
        except ConnectionError as e:
            logger.error(f"IBKR connection failed: {e}")
            console.print(f"[yellow]⏳ Retrying in 30 seconds...[/yellow]")
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Server error: {e}")
            console.print(f"[yellow]⏳ Restarting in 10 seconds...[/yellow]")
            await asyncio.sleep(10)
        finally:
            await ibkr_client.disconnect()
    
    console.print("[bold green]👋 Server shutdown complete[/bold green]")


@click.command()
@click.option('--test', is_flag=True, help='Test connection and exit')
@click.option('--log-level', default=settings.log_level, help='Logging level')
@click.option('--log-file', default=settings.log_file, help='Log file path')
def cli(test: bool, log_level: str, log_file: str):
    """IBKR MCP Server - Interactive Brokers integration for Claude."""
    setup_logging(log_level, log_file)
    
    if test:
        # Run connection test
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    else:
        # Run the server
        asyncio.run(run_server())


async def main():
    """Main entry point when called as module."""
    setup_logging(settings.log_level, settings.log_file)
    await run_server()


if __name__ == "__main__":
    cli()
