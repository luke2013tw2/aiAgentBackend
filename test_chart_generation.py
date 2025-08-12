#!/usr/bin/env python3
"""
測試圖表生成功能
"""

import asyncio
import os
from agents.sql_agent_gemini import SQLAgentGemini

async def test_chart_generation():
    """測試圖表生成功能"""
    
    # 檢查環境變數
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ 請設定 GEMINI_API_KEY 環境變數")
        return
    
    print("🚀 開始測試圖表生成功能...")
    print("=" * 50)
    
    # 初始化 Agent
    agent = SQLAgentGemini()
    
    try:
        # 測試查詢列表 - 這些查詢會產生多筆資料，適合生成圖表
        test_queries = [
            "查詢所有使用者的年齡分布",
            "查詢所有產品的價格分布",
            "查詢每個產品類別的庫存數量",
            "查詢每個使用者的訂單總金額",
            "查詢產品的價格和庫存關係"
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
                
                # 檢查圖表生成
                if result.get('chart_description'):
                    print(f"\n📊 圖表描述:")
                    print(result['chart_description'])
                else:
                    print(f"\n📊 圖表描述: 無需生成圖表")
                
                # 檢查資料格式
                if result.get('data'):
                    data = result['data']
                    if isinstance(data, dict) and data.get('success'):
                        row_count = data.get('row_count', 0)
                        print(f"\n📋 資料筆數: {row_count}")
                        
                        if row_count > 1:
                            print("✅ 多筆資料，已觸發圖表生成")
                        elif row_count == 1:
                            print("📋 單筆資料，無需圖表")
                        else:
                            print("📋 無資料")
                
            except Exception as e:
                print(f"❌ 查詢失敗: {e}")
            
            print()
        
        print("=" * 50)
        print("✅ 圖表生成測試完成")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
    
    finally:
        # 關閉連接
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test_chart_generation())
