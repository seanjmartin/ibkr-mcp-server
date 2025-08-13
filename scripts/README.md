# Scripts Directory

Utility scripts for the IBKR MCP Server project.

## 📋 Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `commit.bat` | Git commit wrapper (recommended) | `scripts\commit.bat "message"` |
| `git-commit.py` | Cross-platform git commit | `python scripts\git-commit.py "message"` |
| `git-commit.bat` | Windows batch git commit | `scripts\git-commit.bat "message"` |
| `git-commit.ps1` | PowerShell git commit | `.\scripts\git-commit.ps1 "message"` |
| `diagnose_gateway.py` | IBKR Gateway diagnostics | `python scripts\diagnose_gateway.py` |
| `fix_unicode.py` | Unicode character cleanup | `python scripts\fix_unicode.py` |
| `setup-claude-desktop.bat` | Claude Desktop configuration | `scripts\setup-claude-desktop.bat` |
| `setup.bat` | Windows project setup | `scripts\setup.bat` |
| `setup.sh` | Unix/Linux project setup | `./scripts/setup.sh` |

## 🔧 Setup Scripts

### `setup.bat` - Windows Project Setup
**Purpose**: Complete Windows environment setup for the IBKR MCP Server

**Features**:
- Python version detection and validation
- Virtual environment creation
- Dependency installation from requirements.txt
- Environment configuration (.env file setup)
- Project structure verification

**Usage**:
```batch
scripts\setup.bat
```

**Requirements**: Python 3.9+ installed and in PATH

### `setup.sh` - Unix/Linux Project Setup
**Purpose**: Complete Unix/Linux environment setup for the IBKR MCP Server

**Features**:
- Python 3.10+ version validation
- Virtual environment creation with venv
- Cross-platform dependency installation
- Environment configuration
- Permission setting for scripts

**Usage**:
```bash
./scripts/setup.sh
```

**Requirements**: Python 3.10+ installed

### `setup-claude-desktop.bat` - Claude Desktop Configuration Helper
**Purpose**: Assists users in configuring Claude Desktop for MCP integration

**Features**:
- Locates Claude Desktop configuration directory
- Provides template configuration JSON
- Generates proper file paths for user's system
- Interactive guidance for MCP server setup
- Validation of configuration file structure

**Usage**:
```batch
scripts\setup-claude-desktop.bat
```

**Output**: 
- Displays current project directory
- Shows Claude config file location (`%APPDATA%\Claude\claude_desktop_config.json`)
- Provides template JSON configuration
- Guides user through setup process

## 🐛 Diagnostic Scripts

### `diagnose_gateway.py` - IBKR Gateway Connection Diagnostics
**Purpose**: Comprehensive diagnostic tool for IBKR Gateway API connection issues

**Features**:
- Detailed connection testing with multiple retry attempts
- API endpoint verification
- Authentication status checking
- Port connectivity validation
- Enhanced logging for debugging
- Error categorization and suggested fixes

**Usage**:
```bash
python scripts\diagnose_gateway.py
```

**Output**:
- Connection status and error details
- Port accessibility test results
- Authentication verification
- Suggested troubleshooting steps
- Detailed logging output for debugging

**Use Cases**:
- Gateway won't connect
- API authentication failures
- Port binding issues
- General connectivity troubleshooting

### `fix_unicode.py` - Unicode Character Cleanup
**Purpose**: Finds and replaces Unicode characters in Python files for Windows terminal compatibility

**Features**:
- Scans Python files for Unicode characters
- Maps Unicode symbols to ASCII alternatives
- Batch processing of multiple files
- Safe backup creation before modifications
- Detailed reporting of changes made

**Unicode Mappings**:
- Arrows: → becomes `->`, ← becomes `<-`
- Check marks: ✓ becomes `[OK]`, ✗ becomes `[ERROR]`
- Emojis: 🚀 becomes `[ROCKET]`, ⚠️ becomes `[WARNING]`
- Special symbols: ❌ becomes `[X]`, ✅ becomes `[OK]`

**Usage**:
```bash
python scripts\fix_unicode.py
```

**Use Cases**:
- Preparing code for Windows terminal execution
- Fixing test files that fail with UnicodeEncodeError
- Ensuring cross-platform compatibility
- Cleaning up copied code from Unicode-rich sources

## 📝 Git Commit Scripts

We've had persistent issues with git commit commands and quotation handling. These scripts solve that problem:

### `commit.bat` - Convenient Wrapper (RECOMMENDED)
**Purpose**: Easy-to-use wrapper that calls the robust Python git commit script

**Features**:
- Simplest interface for git commits
- Automatic path resolution
- Fallback error handling
- Interactive mode when no message provided

**Usage**:
```batch
# With message
scripts\commit.bat "Your commit message here"

# Interactive mode
scripts\commit.bat
```

### `git-commit.py` - Cross-platform Python Version (MOST ROBUST)
**Purpose**: Comprehensive git commit solution with advanced error handling

**Features**:
- Unicode and special character support
- Proper quotation mark handling
- Interactive commit message prompting
- Git status display before commit
- Recent commit history after successful commit
- Comprehensive error handling and rollback
- Cross-platform compatibility (Windows/Mac/Linux)

**Usage**:
```bash
# Direct usage
python scripts\git-commit.py "Your commit message"

# Interactive mode
python scripts\git-commit.py
```

**Advanced Features**:
- Validates git repository status
- Shows staged vs unstaged changes
- Handles commit message edge cases
- Provides informative error messages
- Automatic staging of all changes

### `git-commit.bat` - Windows Batch Version
**Purpose**: Native Windows batch script for git commits

**Features**:
- Native Windows CMD support
- Basic quotation handling
- Fast execution
- Simple error reporting

**Usage**:
```batch
scripts\git-commit.bat "Your commit message"
```

**Limitations**:
- Limited Unicode support
- Basic error handling
- Windows-only compatibility

### `git-commit.ps1` - PowerShell Version
**Purpose**: Advanced PowerShell script with Windows-specific optimizations

**Features**:
- PowerShell parameter validation
- Advanced error handling
- Windows-optimized file handling
- Rich output formatting

**Usage**:
```powershell
.\scripts\git-commit.ps1 "Your commit message"
```

**Requirements**: PowerShell execution policy must allow script execution

## 🔍 Why These Scripts Exist

### The Git Commit Problem
The project repeatedly had issues with git commit commands due to:
- **Windows CMD/PowerShell quotation parsing** - Different shells handle quotes differently
- **Special characters in commit messages** - Unicode, apostrophes, and symbols cause failures
- **Unicode characters causing terminal errors** - Windows terminals reject Unicode output
- **Inconsistent behavior across different shells** - CMD vs PowerShell vs Git Bash differences

### The Unicode Problem
Windows terminals frequently fail with `UnicodeEncodeError: 'charmap' codec can't encode character` when:
- Test files contain Unicode emoji or symbols
- Output includes non-ASCII characters
- Code copied from documentation with fancy formatting

### The Setup Problem
New developers and users need:
- Consistent environment setup across different systems
- Proper Claude Desktop configuration
- IBKR Gateway connection validation
- Quick troubleshooting when things don't work

## 🚀 Quick Start Recommendations

### For New Users
1. **Setup**: Run `scripts\setup.bat` (Windows) or `./scripts/setup.sh` (Unix/Linux)
2. **Claude Desktop**: Run `scripts\setup-claude-desktop.bat` for MCP configuration
3. **Diagnostics**: Run `python scripts\diagnose_gateway.py` to test IBKR connection

### For Developers
1. **Commits**: Always use `scripts\commit.bat "message"` for reliable git commits
2. **Unicode Issues**: Run `python scripts\fix_unicode.py` when encountering encoding errors
3. **Testing**: Use diagnostic script before reporting connection issues

### For Troubleshooting
1. **Connection Issues**: `python scripts\diagnose_gateway.py`
2. **Unicode Errors**: `python scripts\fix_unicode.py`
3. **Setup Problems**: Re-run setup scripts with elevated permissions

## 📁 Script Locations

All scripts are located in the `scripts/` directory at the project root:
```
scripts/
├── commit.bat              # Git commit wrapper (recommended)
├── git-commit.py           # Cross-platform git commit (robust)
├── git-commit.bat          # Windows batch git commit
├── git-commit.ps1          # PowerShell git commit
├── diagnose_gateway.py     # IBKR Gateway diagnostics
├── fix_unicode.py          # Unicode character cleanup
├── setup-claude-desktop.bat # Claude Desktop config helper
├── setup.bat               # Windows project setup
├── setup.sh                # Unix/Linux project setup
└── README.md               # This documentation
```

## 🎯 Best Practices

### Git Commits
- **Always use `scripts\commit.bat`** for the most reliable experience
- **Avoid direct git commit commands** to prevent quotation issues
- **Use descriptive commit messages** - the scripts handle complex formatting

### Unicode Handling
- **Run `fix_unicode.py` proactively** before committing test files
- **Test scripts on Windows terminals** before considering them complete
- **Use ASCII alternatives** for symbols in user-facing output

### Development Workflow
- **Run diagnostics first** when encountering connection issues
- **Use setup scripts** for consistent environment configuration
- **Keep scripts updated** as project requirements evolve

---

**Note**: These scripts solve real problems encountered during development. They represent lessons learned and best practices for maintaining a robust, cross-platform development environment.
