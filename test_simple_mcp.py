#!/usr/bin/env python3
"""
簡單的 MCP 測試腳本

測試簡化版的 MCP Server 和 Client 功能
"""

import asyncio
import json
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.database_server import DatabaseMCPServer
from mcp.database_client import DatabaseMCPClient

async def test_mcp_server():
    """測試 MCP Server"""
    print("🧪 測試 MCP Server...")
    print("=" * 50)
    
    server = DatabaseMCPServer()
    
    try:
        # 列出工具
        tools = server.list_tools()
        print("✅ 可用工具:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 測試取得資料庫結構
        print("\n📊 測試取得資料庫結構...")
        schema = await server.call_tool("get_database_schema")
        print(f"✅ 資料庫結構: {json.dumps(schema, ensure_ascii=False, indent=2)}")
        
        # 測試查詢
        print("\n🔍 測試 SQL 查詢...")
        result = await server.call_tool("execute_query", {"sql": "SELECT * FROM users LIMIT 3"})
        print(f"✅ 查詢結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 測試取得表格資訊
        print("\n📋 測試取得表格資訊...")
        table_info = await server.call_tool("get_table_info", {"table_name": "products"})
        print(f"✅ 表格資訊: {json.dumps(table_info, ensure_ascii=False, indent=2)}")
        
        # 測試取得範例資料
        print("\n📄 測試取得範例資料...")
        sample_data = await server.call_tool("get_sample_data", {"table_name": "orders", "limit": 3})
        print(f"✅ 範例資料: {json.dumps(sample_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")

async def test_mcp_client():
    """測試 MCP Client"""
    print("\n🧪 測試 MCP Client...")
    print("=" * 50)
    
    client = DatabaseMCPClient()
    
    try:
        # 連接
        await client.connect()
        
        # 列出工具
        tools = await client.list_tools()
        print("✅ 可用工具:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 測試取得資料庫結構
        print("\n📊 測試取得資料庫結構...")
        schema = await client.call_tool("get_database_schema")
        print(f"✅ 資料庫結構: {json.dumps(schema, ensure_ascii=False, indent=2)}")
        
        # 測試查詢
        print("\n🔍 測試 SQL 查詢...")
        result = await client.call_tool("execute_query", {"sql": "SELECT * FROM users LIMIT 3"})
        print(f"✅ 查詢結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    finally:
        await client.disconnect()

async def main():
    """主測試函數"""
    print("🚀 開始簡化版 MCP 測試")
    print("=" * 60)
    
    # 測試 MCP Server
    await test_mcp_server()
    
    # 測試 MCP Client
    await test_mcp_client()
    
    print("\n✅ 所有測試完成！")

if __name__ == "__main__":
    asyncio.run(main()) 