import os
from ibkr_mcp_server.config import Settings

os.environ['LOG_FILE'] = 'C:\\Users\\sean\\Documents\\Projects\\ibkr-mcp-server\\logs\\ibkr-mcp-server.log'

settings = Settings()
print(f"Log file path: {settings.log_file}")
print(f"Environment LOG_FILE: {os.environ.get('LOG_FILE', 'Not set')}")
