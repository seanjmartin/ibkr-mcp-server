@echo off
REM Individual MCP Tool Test Runner (Windows)
REM Purpose: Easy execution of individual MCP tool tests for debugging

echo ======================================
echo Individual MCP Tool Test Runner
echo ======================================

REM Check if test file specified
if "%1"=="" (
    echo Usage: %0 ^<tool_name^>
    echo.
    echo Available individual tests:
    echo - get_connection_status
    echo - get_accounts ^(coming soon^)
    echo - get_account_summary ^(coming soon^)
    echo - get_portfolio ^(coming soon^)
    echo.
    echo Example: %0 get_connection_status
    exit /b 1
)

set TOOL_NAME=%1
set TEST_FILE=tests\paper\individual\test_individual_%TOOL_NAME%.py

echo Tool Name: %TOOL_NAME%
echo Test File: %TEST_FILE%
echo.

REM Check if test file exists
if not exist "%TEST_FILE%" (
    echo ❌ Test file not found: %TEST_FILE%
    echo.
    echo Available test files:
    dir tests\paper\individual\test_individual_*.py /b 2>nul || echo No individual test files found
    exit /b 1
)

echo Prerequisites Check:
echo - IBKR Gateway running? ^(Check manually^)
echo - Paper trading login active? ^(Check manually^)
echo - API enabled on port 7497? ^(Check manually^)
echo.

pause
echo.

echo Executing individual test: %TOOL_NAME%
echo Command: pytest %TEST_FILE% -v -s --tb=short --timeout=15
echo.

REM Run the specific test with timeout and verbose output
pytest "%TEST_FILE%" -v -s --tb=short --timeout=15

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ======================================
if %EXIT_CODE%==0 (
    echo ✅ Individual test PASSED: %TOOL_NAME%
) else (
    echo ❌ Individual test FAILED: %TOOL_NAME%
    echo Check IBKR Gateway connection and API settings
)
echo ======================================

exit /b %EXIT_CODE%
