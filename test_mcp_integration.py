#!/usr/bin/env python3
"""
測試 MCP 整合功能

測試 MCP Server、Client 和 SQL Agent 的整合
"""

import asyncio
import json
import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.database_client import DatabaseMCPClient
from agents.sql_agent import SQLAgent

async def test_mcp_client():
    """測試 MCP Client"""
    print("🧪 測試 MCP Client...")
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
        
        # 測試取得表格資訊
        print("\n📋 測試取得表格資訊...")
        table_info = await client.call_tool("get_table_info", {"table_name": "products"})
        print(f"✅ 表格資訊: {json.dumps(table_info, ensure_ascii=False, indent=2)}")
        
        # 測試取得範例資料
        print("\n📄 測試取得範例資料...")
        sample_data = await client.call_tool("get_sample_data", {"table_name": "orders", "limit": 3})
        print(f"✅ 範例資料: {json.dumps(sample_data, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    finally:
        await client.disconnect()

async def test_sql_agent_with_mcp():
    """測試使用 MCP 的 SQL Agent"""
    print("\n🤖 測試使用 MCP 的 SQL Agent...")
    print("=" * 50)
    
    agent = SQLAgent()
    
    try:
        # 測試簡單查詢
        print("\n🔍 測試簡單查詢...")
        result = await agent.execute("顯示所有使用者")
        print(f"✅ 查詢結果:")
        print(f"   回應: {result['response']}")
        print(f"   SQL: {result['sql_generated']}")
        print(f"   資料: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        
        # 測試條件查詢
        print("\n🔍 測試條件查詢...")
        result = await agent.execute("找出價格超過 10000 的產品")
        print(f"✅ 查詢結果:")
        print(f"   回應: {result['response']}")
        print(f"   SQL: {result['sql_generated']}")
        print(f"   資料: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        
        # 測試聚合查詢
        print("\n🔍 測試聚合查詢...")
        result = await agent.execute("計算每個類別的產品數量")
        print(f"✅ 查詢結果:")
        print(f"   回應: {result['response']}")
        print(f"   SQL: {result['sql_generated']}")
        print(f"   資料: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        
        # 測試複雜查詢
        print("\n🔍 測試複雜查詢...")
        result = await agent.execute("顯示每個使用者的訂單總金額")
        print(f"✅ 查詢結果:")
        print(f"   回應: {result['response']}")
        print(f"   SQL: {result['sql_generated']}")
        print(f"   資料: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    finally:
        await agent.close()

async def main():
    """主測試函數"""
    print("🚀 開始 MCP 整合測試")
    print("=" * 60)
    
    # 測試 MCP Client
    await test_mcp_client()
    
    # 測試 SQL Agent with MCP
    await test_sql_agent_with_mcp()
    
    print("\n✅ 所有測試完成！")

if __name__ == "__main__":
    asyncio.run(main()) 