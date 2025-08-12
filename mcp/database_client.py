#!/usr/bin/env python3
"""
MCP Database Client

用於連接 MCP Database Server 並提供資料庫操作介面
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, List, Optional
from pathlib import Path

class DatabaseMCPClient:
    """MCP Database Client 實現 - 連接到外部 MCP Server"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url.rstrip('/')
        self.session = None
        self.connected = False
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """發送 HTTP 請求到 MCP Server"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        url = f"{self.server_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    return await response.json()
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
        except Exception as e:
            raise Exception(f"請求失敗: {str(e)}")
    
    async def connect(self):
        """連接到 MCP Server"""
        try:
            # 進行健康檢查來確認連接
            health = await self._make_request("GET", "/health")
            if health.get("status") == "healthy":
                self.connected = True
                print("✅ MCP Database Server 連接成功")
            else:
                raise Exception("MCP Server 健康檢查失敗")
                
        except Exception as e:
            print(f"❌ MCP Server 連接失敗: {e}")
            self.connected = False
    
    async def disconnect(self):
        """斷開 MCP Server 連接"""
        if self.session:
            await self.session.close()
        self.session = None
        self.connected = False
        print("🔌 MCP Database Server 連接已斷開")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = {}) -> Dict[str, Any]:
        """調用 MCP 工具"""
        if not self.connected:
            raise Exception("MCP Server 未連接")
        
        try:
            # 根據工具名稱調用對應的 API
            if tool_name == "get_database_schema":
                return await self._make_request("GET", "/api/schema")
            elif tool_name == "execute_query":
                return await self._make_request("POST", "/api/query", {"sql": arguments.get("sql", "")})
            elif tool_name == "get_table_info":
                table_name = arguments.get("table_name", "")
                return await self._make_request("GET", f"/api/table/{table_name}")
            elif tool_name == "get_sample_data":
                table_name = arguments.get("table_name", "")
                limit = arguments.get("limit", 5)
                return await self._make_request("GET", f"/api/table/{table_name}/sample?limit={limit}")
            else:
                raise ValueError(f"未知工具: {tool_name}")
                
        except Exception as e:
            raise Exception(f"工具調用失敗: {str(e)}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        try:
            result = await self._make_request("GET", "/api/tools")
            return result.get("tools", [])
        except Exception as e:
            print(f"❌ 取得工具列表失敗: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return await self._make_request("GET", "/health")
    
    async def get_schema(self) -> Dict[str, Any]:
        """取得資料庫結構"""
        return await self._make_request("GET", "/api/schema")
    
    async def execute_query(self, sql: str) -> Dict[str, Any]:
        """執行 SQL 查詢"""
        return await self._make_request("POST", "/api/query", {"sql": sql})
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """取得表格資訊"""
        return await self._make_request("GET", f"/api/table/{table_name}")
    
    async def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """取得表格範例資料"""
        return await self._make_request("GET", f"/api/table/{table_name}/sample?limit={limit}")

# 同步版本的客戶端（用於非異步環境）
class DatabaseMCPClientSync:
    """同步版本的 MCP Database Client"""

    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url.rstrip('/')

    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        return asyncio.run(self._async_client().health_check())

    def get_schema(self) -> Dict[str, Any]:
        """取得資料庫結構"""
        return asyncio.run(self._async_client().get_schema())

    def execute_query(self, sql: str) -> Dict[str, Any]:
        """執行 SQL 查詢"""
        return asyncio.run(self._async_client().execute_query(sql))

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """取得表格資訊"""
        return asyncio.run(self._async_client().get_table_info(table_name))

    def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """取得表格範例資料"""
        return asyncio.run(self._async_client().get_sample_data(table_name, limit))

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        return asyncio.run(self._async_client().list_tools())

    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = {}) -> Dict[str, Any]:
        """調用工具（通用方法）"""
        return asyncio.run(self._async_client().call_tool(tool_name, arguments))

    def _async_client(self) -> DatabaseMCPClient:
        """取得異步客戶端實例"""
        return DatabaseMCPClient(self.server_url)

# 測試函數
async def test_mcp_client():
    """測試 MCP Client"""
    async with DatabaseMCPClient() as client:
        try:
            # 連接
            await client.connect()
            
            # 健康檢查
            health = await client.health_check()
            print("健康檢查:", json.dumps(health, ensure_ascii=False, indent=2))
            
            # 列出工具
            tools = await client.list_tools()
            print("可用工具:", json.dumps(tools, ensure_ascii=False, indent=2))
            
            # 測試取得資料庫結構
            schema = await client.get_schema()
            print("資料庫結構:", json.dumps(schema, ensure_ascii=False, indent=2))
            
            # 測試查詢
            result = await client.execute_query("SELECT * FROM users LIMIT 3")
            print("查詢結果:", json.dumps(result, ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"測試失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_client()) 