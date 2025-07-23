from setuptools import setup, find_packages

setup(
    name="ibkr-mcp-server",
    version="1.0.0",
    description="Interactive Brokers MCP Server for Claude Desktop/Code",
    author="Arjun Divecha",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "ib_async>=0.9.86",
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "coverage[toml]>=7.0.0",
        ]
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ibkr-mcp-server=ibkr_mcp_server.main:cli",
        ],
    },
    python_requires=">=3.10",
)
