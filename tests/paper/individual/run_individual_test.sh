#!/bin/bash

# Individual MCP Tool Test Runner
# Purpose: Easy execution of individual MCP tool tests for debugging

echo "======================================"
echo "Individual MCP Tool Test Runner"
echo "======================================"

# Check if test file specified
if [ $# -eq 0 ]; then
    echo "Usage: $0 <tool_name>"
    echo ""
    echo "Available individual tests:"
    echo "- get_connection_status"
    echo "- get_accounts (coming soon)"
    echo "- get_account_summary (coming soon)"
    echo "- get_portfolio (coming soon)"
    echo ""
    echo "Example: $0 get_connection_status"
    exit 1
fi

TOOL_NAME=$1
TEST_FILE="tests/paper/individual/test_individual_${TOOL_NAME}.py"

echo "Tool Name: $TOOL_NAME"
echo "Test File: $TEST_FILE"
echo ""

# Check if test file exists
if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Test file not found: $TEST_FILE"
    echo ""
    echo "Available test files:"
    ls tests/paper/individual/test_individual_*.py 2>/dev/null || echo "No individual test files found"
    exit 1
fi

echo "Prerequisites Check:"
echo "- IBKR Gateway running? (Check manually)"
echo "- Paper trading login active? (Check manually)" 
echo "- API enabled on port 7497? (Check manually)"
echo ""

read -p "Press Enter to continue with test execution..."
echo ""

echo "Executing individual test: $TOOL_NAME"
echo "Command: pytest $TEST_FILE -v -s --tb=short --timeout=15"
echo ""

# Run the specific test with timeout and verbose output
pytest "$TEST_FILE" -v -s --tb=short --timeout=15

EXIT_CODE=$?

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Individual test PASSED: $TOOL_NAME"
else
    echo "❌ Individual test FAILED: $TOOL_NAME"
    echo "Check IBKR Gateway connection and API settings"
fi
echo "======================================"

exit $EXIT_CODE
