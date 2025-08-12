#!/usr/bin/env python3
"""
測試更新後的 MCP Client 連接
"""

import asyncio
import json
from mcp.database_client import DatabaseMCPClient

async def test_mcp_client():
    """測試 MCP Client 連接"""
    print("🧪 測試 MCP Client 連接...")
    print("=" * 50)
    
    async with DatabaseMCPClient() as client:
        try:
            # 連接測試
            print("1. 測試連接...")
            await client.connect()
            
            # 健康檢查
            print("2. 健康檢查...")
            health = await client.health_check()
            print(f"   狀態: {health.get('status', 'unknown')}")
            print(f"   時間: {health.get('timestamp', 'unknown')}")
            
            # 列出工具
            print("3. 列出可用工具...")
            tools = await client.list_tools()
            print(f"   工具數量: {len(tools)}")
            for tool in tools:
                print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
            
            # 取得資料庫結構
            print("4. 取得資料庫結構...")
            schema = await client.get_schema()
            print(f"   資料庫: {schema.get('database', 'unknown')}")
            print(f"   表格數量: {schema.get('total_tables', 0)}")
            
            # 測試查詢
            print("5. 測試 SQL 查詢...")
            result = await client.execute_query("SELECT * FROM users LIMIT 3")
            print(f"   查詢成功: {result.get('success', False)}")
            print(f"   資料筆數: {result.get('row_count', 0)}")
            
            print("\n✅ 所有測試通過！")
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            print(f"   錯誤類型: {type(e).__name__}")
            import traceback
            traceback.print_exc()

def test_sync_client():
    """測試同步版本的客戶端"""
    print("\n🧪 測試同步版本 MCP Client...")
    print("=" * 50)
    
    from mcp.database_client import DatabaseMCPClientSync
    
    try:
        client = DatabaseMCPClientSync()
        
        # 健康檢查
        print("1. 健康檢查...")
        health = client.health_check()
        print(f"   狀態: {health.get('status', 'unknown')}")
        
        # 取得資料庫結構
        print("2. 取得資料庫結構...")
        schema = client.get_schema()
        print(f"   資料庫: {schema.get('database', 'unknown')}")
        print(f"   表格數量: {schema.get('total_tables', 0)}")
        
        # 測試查詢
        print("3. 測試 SQL 查詢...")
        result = client.execute_query("SELECT * FROM users LIMIT 3")
        print(f"   查詢成功: {result.get('success', False)}")
        print(f"   資料筆數: {result.get('row_count', 0)}")
        
        print("\n✅ 同步版本測試通過！")
        
    except Exception as e:
        print(f"❌ 同步版本測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 測試異步版本
    asyncio.run(test_mcp_client())
    
    # 測試同步版本
    test_sync_client()
