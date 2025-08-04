#!/usr/bin/env python3
"""
新設計驗證腳本

測試重新設計後的 AI Agent Backend
"""

import requests
import json
import time

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """測試基本端點"""
    print("🔍 測試基本端點...")
    
    # 測試根路徑
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 根路徑正常")
            data = response.json()
            print(f"   訊息: {data.get('message')}")
            print(f"   版本: {data.get('version')}")
        else:
            print(f"❌ 根路徑錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路徑異常: {e}")
    
    # 測試健康檢查
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康檢查正常")
            data = response.json()
            print(f"   狀態: {data.get('status')}")
            print(f"   Agent: {data.get('agent')}")
        else:
            print(f"❌ 健康檢查錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康檢查異常: {e}")
    
    # 測試 Agent 資訊
    try:
        response = requests.get(f"{BASE_URL}/agent-info")
        if response.status_code == 200:
            print("✅ Agent 資訊正常")
            data = response.json()
            print(f"   Agent 名稱: {data.get('name')}")
            print(f"   描述: {data.get('description')}")
            print(f"   功能: {data.get('capabilities')}")
            print(f"   工作流程: {data.get('workflow')}")
        else:
            print(f"❌ Agent 資訊錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent 資訊異常: {e}")

def test_agent_execution():
    """測試 AI Agent 執行"""
    print("\n🔍 測試 AI Agent 執行...")
    
    test_queries = [
        "查詢所有使用者",
        "查詢所有產品",
        "計算所有訂單的總金額"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   測試 {i}: {query}")
        
        try:
            payload = {
                "query": query,
                "context": {}
            }
            
            response = requests.post(
                f"{BASE_URL}/execute-agent",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print("   ✅ 查詢成功")
                result = response.json()
                print(f"   回應: {result.get('response', '')[:100]}...")
                print(f"   生成的 SQL: {result.get('sql_generated', '')}")
                if result.get('data'):
                    data = result['data']
                    print(f"   資料類型: {data.get('type', '')}")
                    if data.get('count'):
                        print(f"   結果數量: {data['count']}")
            else:
                print(f"   ❌ 查詢失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
        except Exception as e:
            print(f"   ❌ 查詢異常: {e}")
        
        time.sleep(1)  # 避免請求過於頻繁

def main():
    """主函數"""
    print("🚀 新設計驗證測試")
    print("=" * 50)
    
    # 檢查服務器是否運行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服務器未運行，請先啟動服務器")
            print("   執行: python start_uv.py")
            return
    except Exception:
        print("❌ 無法連接到服務器，請先啟動服務器")
        print("   執行: python start_uv.py")
        return
    
    print("✅ 服務器正在運行")
    
    # 測試基本端點
    test_basic_endpoints()
    
    # 測試 AI Agent 執行
    test_agent_execution()
    
    print("\n" + "=" * 50)
    print("🎉 新設計驗證完成！")
    print("\n💡 新設計特色:")
    print("   ✅ 單一 AI Agent (SQL Agent)")
    print("   ✅ 具有 reason、action、observe 功能")
    print("   ✅ 單一 API 端點 (/execute-agent)")
    print("   ✅ 使用 uv 進行專案管理")
    print("   ✅ 使用 pyproject.toml 進行模組管理")
    print("   ✅ 自然語言轉 SQL 查詢")
    print("   ✅ SQLite 資料庫整合")

if __name__ == "__main__":
    main() 