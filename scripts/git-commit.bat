@echo off
REM Git Commit Script - Handles quotation issues properly
REM Usage: git-commit.bat "Your commit message here"
REM Usage: git-commit.bat (prompts for message)

setlocal enabledelayedexpansion

REM Check if message was provided as argument
if "%~1"=="" (
    echo.
    echo Enter your commit message:
    set /p "MESSAGE="
) else (
    set "MESSAGE=%~1"
)

REM Validate message is not empty
if "!MESSAGE!"=="" (
    echo Error: Commit message cannot be empty
    exit /b 1
)

echo.
echo Committing with message: !MESSAGE!
echo.

REM Stage all changes
echo Adding all changes...
git add -A
if errorlevel 1 (
    echo Error: Failed to stage changes
    exit /b 1
)

REM Show status before commit
echo.
echo Current status:
git status --short
echo.

REM Commit with proper escaping
git commit -m "!MESSAGE!"
if errorlevel 1 (
    echo Error: Commit failed
    exit /b 1
)

echo.
echo Commit successful!
echo.

REM Show recent commits
echo Recent commits:
git log --oneline -3
echo.

endlocal
