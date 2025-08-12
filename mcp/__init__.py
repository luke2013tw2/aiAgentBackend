"""
MCP (Model Context Protocol) 模組

提供 MCP Client 實現，用於 AI Agent 與外部 MCP Server 的互動
"""

from .database_client import DatabaseMCPClient, DatabaseMCPClientSync

__all__ = [
    "DatabaseMCPClient",
    "DatabaseMCPClientSync"
]

__version__ = "1.0.0" 