#!/usr/bin/env python3
"""
MCP Database Client

用於連接 MCP Database Server 並提供資料庫操作介面
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

class DatabaseMCPClient:
    """簡化版 MCP Database Client 實現"""
    
    def __init__(self, server_script: str = "mcp/database_server.py"):
        self.server_script = server_script
        self.server = None
        self.connected = False
    
    async def connect(self):
        """連接到 MCP Server"""
        try:
            # 直接創建 Server 實例
            from .database_server import DatabaseMCPServer
            self.server = DatabaseMCPServer()
            self.connected = True
            print("✅ MCP Database Server 連接成功")
                
        except Exception as e:
            print(f"❌ MCP Server 連接失敗: {e}")
            self.connected = False
    
    async def disconnect(self):
        """斷開 MCP Server 連接"""
        self.server = None
        self.connected = False
        print("🔌 MCP Database Server 連接已斷開")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = {}) -> Dict[str, Any]:
        """調用 MCP 工具"""
        if not self.connected or not self.server:
            raise Exception("MCP Server 未連接")
        
        try:
            # 直接調用 Server 的工具
            return await self.server.call_tool(tool_name, arguments)
                
        except Exception as e:
            raise Exception(f"工具調用失敗: {str(e)}")
    

    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        if not self.connected or not self.server:
            return []
        return self.server.list_tools()

# 測試函數
async def test_mcp_client():
    """測試 MCP Client"""
    client = DatabaseMCPClient()
    
    try:
        # 連接
        await client.connect()
        
        # 列出工具
        tools = await client.list_tools()
        print("可用工具:", json.dumps(tools, ensure_ascii=False, indent=2))
        
        # 測試取得資料庫結構
        schema = await client.call_tool("get_database_schema")
        print("資料庫結構:", json.dumps(schema, ensure_ascii=False, indent=2))
        
        # 測試查詢
        result = await client.call_tool("execute_query", {"sql": "SELECT * FROM users LIMIT 3"})
        print("查詢結果:", json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"測試失敗: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_mcp_client()) 