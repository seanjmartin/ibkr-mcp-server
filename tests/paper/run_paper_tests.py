"""
Paper Trading Test Runner

Convenient script to run paper trading tests with proper setup and safety checks.

Usage:
    python run_paper_tests.py [--quick] [--verbose]
    
    --quick: Run only basic connection and market data tests
    --verbose: Show detailed test output
"""

import os
import sys
import subprocess
import argparse

def check_ibkr_gateway():
    """Check if IB Gateway is running"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run([
                'powershell', '-Command', 
                'Get-Process | Where-Object {$_.ProcessName -like "*ibgateway*" -or $_.ProcessName -like "*tws*"}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                print("Connected: IB Gateway/TWS is running")
                return True
            else:
                print("Error: IB Gateway/TWS is not running")
                print("Please start IB Gateway in paper trading mode before running tests")
                return False
        else:
            # Linux/Mac - basic check
            result = subprocess.run(['pgrep', '-f', 'gateway'], capture_output=True)
            return result.returncode == 0
            
    except Exception as e:
        print(f"⚠️  Could not check IB Gateway status: {e}")
        return True  # Assume it's running and let tests handle the error

def check_environment():
    """Check environment configuration"""
    try:
        from ibkr_mcp_server.enhanced_config import EnhancedSettings
        settings = EnhancedSettings()
        
        print("Environment Configuration:")
        print(f"   Paper Trading: {'YES' if settings.ibkr_is_paper else 'NO (DANGER!)'}")
        print(f"   Port: {settings.ibkr_port} {'OK' if settings.ibkr_port == 7497 else 'WARNING'}")
        print(f"   Paper Verification: {'ON' if settings.require_paper_account_verification else 'OFF'}")
        print(f"   Trading Enabled: {'YES' if settings.enable_trading else 'NO'}")
        
        if not settings.ibkr_is_paper:
            print("\nDANGER: Not configured for paper trading!")
            print("Please set IBKR_IS_PAPER=true in your .env file")
            return False
            
        if settings.ibkr_port != 7497:
            print(f"\nWARNING: Port {settings.ibkr_port} is not the standard paper trading port (7497)")
            
        return True
        
    except Exception as e:
        print(f"Error checking environment: {e}")
        return False

def run_tests(test_level="full", verbose=False):
    """Run paper trading tests"""
    
    # Determine which tests to run
    if test_level == "quick":
        test_files = [
            "tests/paper/test_paper_trading_integration.py::TestPaperTradingConnection",
            "tests/paper/test_paper_trading_integration.py::TestPaperTradingMarketData",
            "tests/paper/test_mcp_tools_paper.py::TestPaperTradingMCPTools"
        ]
        print("Running quick paper trading tests...")
    else:
        test_files = [
            "tests/paper/"
        ]
        print("Running full paper trading test suite...")
    
    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest"
    ] + test_files + [
        "-m", "paper",
        "--tb=short"
    ]
    
    if verbose:
        cmd.extend(["-v", "-s"])
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run tests
    result = subprocess.run(cmd)
    
    print("-" * 50)
    if result.returncode == 0:
        print("All paper trading tests passed!")
    else:
        print("Some paper trading tests failed")  
        print("Check the output above for details")
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run IBKR MCP Server paper trading tests")
    parser.add_argument("--quick", action="store_true", help="Run only basic tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("IBKR MCP Server - Paper Trading Test Suite")
    print("=" * 50)
    
    # Safety checks
    if not check_environment():
        return 1
        
    if not check_ibkr_gateway():
        return 1
    
    print("\nSafety checks passed - proceeding with paper trading tests")
    print("These tests will connect to your IBKR paper trading account\n")
    
    # Run tests
    test_level = "quick" if args.quick else "full"
    return run_tests(test_level, args.verbose)

if __name__ == "__main__":
    sys.exit(main())
