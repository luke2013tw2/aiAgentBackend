"""
MCP (Model Context Protocol) 模組

提供 MCP Server 和 Client 實現，用於 AI Agent 與外部系統的互動
"""

from .database_server import DatabaseMCPServer
from .database_client import DatabaseMCPClient

__all__ = [
    "DatabaseMCPServer",
    "DatabaseMCPClient"
]

__version__ = "1.0.0" 