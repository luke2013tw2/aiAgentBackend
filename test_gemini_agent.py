#!/usr/bin/env python3
"""
測試 Gemini SQL Agent 的改進功能
"""

import asyncio
import os
from agents.sql_agent_gemini import SQLAgentGemini

async def test_gemini_agent():
    """測試 Gemini SQL Agent"""
    
    # 檢查環境變數
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ 請設定 GEMINI_API_KEY 環境變數")
        return
    
    print("🚀 開始測試 Gemini SQL Agent...")
    print("=" * 50)
    
    # 初始化 Agent
    agent = SQLAgentGemini()
    
    try:
        # 測試查詢列表
        test_queries = [
            "查詢所有使用者",
            "查詢所有產品",
            "查詢所有訂單",
            "查詢每個使用者的訂單數量",
            "查詢庫存少於 20 的產品"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 測試查詢: {query}")
            print("-" * 40)
            
            try:
                result = await agent.execute(query)
                
                print(f"✅ 查詢成功")
                print(f"生成的 SQL: {result['sql_generated']}")
                print(f"分析過程: {result['reasoning'][:100]}...")
                print(f"回應: {result['response']}")
                
                # 檢查資料格式
                if result.get('data'):
                    data = result['data']
                    if isinstance(data, dict) and data.get('success'):
                        row_count = data.get('row_count', 0)
                        print(f"📊 資料筆數: {row_count}")
                        
                        if row_count > 1:
                            print("📋 多筆資料已格式化為列表顯示")
                        elif row_count == 1:
                            print("📋 單筆資料")
                        else:
                            print("📋 無資料")
                
            except Exception as e:
                print(f"❌ 查詢失敗: {e}")
            
            print()
        
        print("=" * 50)
        print("✅ 所有測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
    
    finally:
        # 關閉連接
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test_gemini_agent())
