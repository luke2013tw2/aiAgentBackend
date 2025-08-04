#!/usr/bin/env python3
"""
AI Agent Backend API 測試腳本

測試新的單一 AI Agent API 端點
"""

import requests
import json
import time

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """測試健康檢查端點"""
    print("🔍 測試健康檢查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康檢查通過")
            print(f"   回應: {response.json()}")
        else:
            print(f"❌ 健康檢查失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康檢查錯誤: {e}")

def test_root():
    """測試根路徑端點"""
    print("\n🔍 測試根路徑...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 根路徑測試通過")
            print(f"   回應: {response.json()}")
        else:
            print(f"❌ 根路徑測試失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路徑測試錯誤: {e}")

def test_agent_info():
    """測試 Agent 資訊端點"""
    print("\n🔍 測試 Agent 資訊...")
    try:
        response = requests.get(f"{BASE_URL}/agent-info")
        if response.status_code == 200:
            print("✅ Agent 資訊測試通過")
            data = response.json()
            print(f"   Agent 名稱: {data.get('name')}")
            print(f"   描述: {data.get('description')}")
            print(f"   功能: {data.get('capabilities')}")
        else:
            print(f"❌ Agent 資訊測試失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent 資訊測試錯誤: {e}")

def test_execute_agent(query, description):
    """測試執行 AI Agent"""
    print(f"\n🔍 測試執行 AI Agent: {description}")
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
            print("✅ AI Agent 執行成功")
            data = response.json()
            print(f"   回應: {data.get('response', '')[:100]}...")
            print(f"   生成的 SQL: {data.get('sql_generated', '')}")
            if data.get('data'):
                print(f"   資料類型: {data['data'].get('type', '')}")
                if data['data'].get('count'):
                    print(f"   結果數量: {data['data']['count']}")
        else:
            print(f"❌ AI Agent 執行失敗: {response.status_code}")
            print(f"   錯誤: {response.text}")
    except Exception as e:
        print(f"❌ AI Agent 執行錯誤: {e}")

def run_all_tests():
    """執行所有測試"""
    print("🚀 開始測試 AI Agent Backend API")
    print("=" * 50)
    
    # 基本端點測試
    test_health_check()
    test_root()
    test_agent_info()
    
    # AI Agent 執行測試
    test_queries = [
        ("查詢所有使用者", "基本查詢測試"),
        ("查詢所有手機類別的產品", "條件查詢測試"),
        ("計算所有訂單的總金額", "統計查詢測試"),
        ("查詢每個使用者的訂單總金額，並按金額排序", "複雜查詢測試"),
        ("查詢庫存少於 30 的產品", "條件篩選測試")
    ]
    
    for query, description in test_queries:
        test_execute_agent(query, description)
        time.sleep(1)  # 避免請求過於頻繁
    
    print("\n" + "=" * 50)
    print("🎉 所有測試完成！")

if __name__ == "__main__":
    run_all_tests() 