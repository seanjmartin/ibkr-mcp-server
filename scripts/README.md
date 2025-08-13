# Scripts Directory

Utility scripts for the IBKR MCP Server project.

## Git Commit Scripts

We've had persistent issues with git commit commands and quotation handling. These scripts solve that problem:

### Quick Usage

**Recommended**: Use the convenient wrapper:
```batch
scripts\commit.bat "Your commit message here"
```

Or for interactive mode:
```batch
scripts\commit.bat
```

### Available Scripts

1. **`commit.bat`** - Convenient wrapper (recommended)
   - Calls the Python script with proper paths
   - Usage: `scripts\commit.bat "message"` or `scripts\commit.bat`

2. **`git-commit.py`** - Cross-platform Python version (most robust)
   - Handles Unicode, special characters, and complex messages
   - Proper error handling and status display
   - Usage: `python scripts\git-commit.py "message"`

3. **`git-commit.bat`** - Windows batch version
   - Native Windows batch script
   - Usage: `scripts\git-commit.bat "message"`

4. **`git-commit.ps1`** - PowerShell version
   - Advanced PowerShell features
   - Usage: `.\scripts\git-commit.ps1 "message"`

### Features

- **Quotation Handling**: No more struggling with quotes and special characters
- **Interactive Mode**: Prompts for message if not provided
- **Status Display**: Shows what's being committed
- **Error Handling**: Proper error messages and rollback
- **Recent Commits**: Shows recent commit history after successful commit

## Other Scripts

- **`diagnose_gateway.py`** - IBKR Gateway connection diagnostics
- **`fix_unicode.py`** - Unicode character cleanup for test files
- **`setup-claude-desktop.bat`** - Claude Desktop configuration setup
- **`setup.bat`** / **`setup.sh`** - Project setup scripts

## Why These Scripts?

The project repeatedly had issues with git commit commands due to:
- Windows CMD/PowerShell quotation parsing
- Special characters in commit messages
- Unicode characters causing terminal errors
- Inconsistent behavior across different shells

These scripts provide a consistent, reliable way to commit changes without quotation headaches.
