import os
import logging
from ibkr_mcp_server.config import Settings

# Test with environment variable set
settings = Settings()
print(f"Log file from settings: {settings.log_file}")

# Test that we can create the log file
try:
    logging.basicConfig(filename=settings.log_file, level=logging.INFO)
    logging.info("Test log entry")
    print("SUCCESS: Can write to log file")
except Exception as e:
    print(f"ERROR: Cannot write to log file: {e}")
