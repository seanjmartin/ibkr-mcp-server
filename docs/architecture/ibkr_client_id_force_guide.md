# IBKR Client ID Force Connection Guide

## Overview

This guide documents the proven method for forcing a specific client ID when connecting to the IBKR Gateway, based on analysis of the paper test suite in the IBKR MCP Server project.

## The Problem

By default, the IBKR client uses `client_id = 1` from configuration. However, for testing, debugging, or avoiding connection conflicts, you may need to force a specific client ID (like client ID 5 used in paper tests).

## Solution Methods

### Method 1: Direct Client ID Override (Recommended)

This is the **proven pattern** used throughout the paper test suite:

```python
# Step 1: Import the global client instance
from ibkr_mcp_server.client import ibkr_client

# Step 2: Set client ID BEFORE calling connect()
ibkr_client.client_id = 5  # Force client ID 5 (standard for paper tests)

# Step 3: Connect to IBKR Gateway
try:
    connection_success = await ibkr_client.connect()
    if connection_success:
        print(f"[OK] IBKR Gateway connected with client ID {ibkr_client.client_id}")
        print(f"[OK] Paper account: {ibkr_client.current_account}")
    else:
        print("Connection failed")
except Exception as e:
    print(f"Connection error: {e}")
```

### Method 2: Environment Variable Configuration

Set the client ID via environment variables in `.env`:

```bash
# In .env file
IBKR_CLIENT_ID=5
```

Then restart the application to pick up the new setting.

## How It Works

### Architecture Overview

1. **Global Instance**: There's a global `ibkr_client` instance created at module level in `client.py`:
   ```python
   # At the end of client.py
   ibkr_client = IBKRClient()
   ```

2. **Client ID Storage**: The client ID is stored in `self.client_id` during initialization:
   ```python
   def __init__(self):
       # ... other initialization
       self.client_id = settings.ibkr_client_id  # Default: 1
   ```

3. **Override Pattern**: Paper tests override the client ID **before** connection:
   ```python
   ibkr_client.client_id = 5  # Override default
   ```

4. **Connection**: When `connect()` is called, it uses the stored `client_id` value

5. **Validation**: Tests verify the correct client ID:
   ```python
   assert client_id == 5  # Required client ID for paper tests
   ```

## Why Client ID 5?

From analysis of the paper test suite, client ID 5 is used because:

- **Standard for Testing**: Consistently used across all paper test files
- **Prevents Conflicts**: Different from default client ID 1
- **Shared Connection**: Allows multiple tests to reuse the same Gateway connection
- **Paper Trading Optimized**: Specifically chosen for paper account workflows
- **Documentation**: Well-documented in test comments as "Required client ID for paper tests"

## Evidence from Paper Tests

Multiple test files use this exact pattern:

```python
# Found in multiple test files:
ibkr_client.client_id = 5

# Validation assertions:
assert parsed_result['client_id'] == 5  # Required client ID
assert client_id == 5, f"Expected client ID 5, got {client_id}"
assert client_id == 5  # Required client ID for paper tests
```

**Test files using this pattern:**
- `test_individual_cancel_order.py`
- `test_individual_get_completed_orders.py`
- `test_individual_get_open_orders.py`
- `test_individual_get_order_status.py`
- `test_individual_modify_order.py`
- `test_individual_place_bracket_order.py`
- `test_individual_place_limit_order.py`
- `test_individual_place_market_order.py`
- And many more...

## Complete Example Usage

### For Testing/Debugging Scripts

```python
import asyncio
from ibkr_mcp_server.client import ibkr_client

async def main():
    # Force client ID before any operations
    ibkr_client.client_id = 5  # Or any desired client ID
    
    # Connect to IBKR Gateway
    print("Connecting to IBKR Gateway...")
    connection_success = await ibkr_client.connect()
    
    if connection_success:
        print(f"✅ Connected with client ID: {ibkr_client.client_id}")
        print(f"📊 Account: {ibkr_client.current_account}")
        print(f"🏦 Paper trading: {ibkr_client.is_paper}")
        
        # Your operations here...
        
    else:
        print("❌ Connection failed")

if __name__ == "__main__":
    asyncio.run(main())
```

### For pytest Tests

```python
@pytest.mark.asyncio
async def test_with_specific_client_id():
    """Test with forced client ID"""
    
    # Force client ID BEFORE connection
    from ibkr_mcp_server.client import ibkr_client
    ibkr_client.client_id = 5
    
    # Connect and test
    connection_success = await ibkr_client.connect()
    assert connection_success
    assert ibkr_client.client_id == 5
    
    # Your test logic here...
```

## Important Notes

### Timing Is Critical

⚠️ **The client ID MUST be set BEFORE calling `connect()`**

```python
# ✅ CORRECT - Set before connect()
ibkr_client.client_id = 5
await ibkr_client.connect()

# ❌ WRONG - Setting after connect() has no effect
await ibkr_client.connect()
ibkr_client.client_id = 5  # Too late!
```

### Gateway Configuration

Ensure your IBKR Gateway/TWS is configured to accept the client ID:
- Enable "ActiveX and Socket Clients"
- Add trusted IP addresses (127.0.0.1 for local)
- Set correct port (7497 for paper, 7496 for live)

### Client ID Conflicts

Each client ID can only have one active connection to the Gateway:
- Use different client IDs for different applications/scripts
- Close connections properly to free up client IDs
- Client ID 5 appears to be reserved for testing in this project

## Configuration Reference

### Default Settings (enhanced_config.py)

```python
class EnhancedSettings(BaseSettings):
    # Connection settings
    ibkr_host: str = "127.0.0.1"
    ibkr_port: int = 7497  # Paper trading
    ibkr_client_id: int = 1  # Default client ID
    ibkr_is_paper: bool = True
```

### Override Priority

1. **Direct assignment**: `ibkr_client.client_id = 5` (highest priority)
2. **Environment variable**: `IBKR_CLIENT_ID=5` in `.env`
3. **Default setting**: `ibkr_client_id: int = 1` in config

## Troubleshooting

### Connection Refused
- Check if client ID is already in use
- Verify IBKR Gateway is running and logged in
- Confirm API settings are enabled

### Wrong Client ID
- Set client ID **before** calling `connect()`
- Check environment variables aren't overriding your setting
- Verify the global `ibkr_client` instance is being used

### Testing Issues
- Use client ID 5 for consistency with existing paper tests
- Ensure Gateway is configured for paper trading (port 7497)
- Close previous connections before running new tests

This method is **proven and tested** across the entire paper test suite and provides reliable client ID control for IBKR Gateway connections.