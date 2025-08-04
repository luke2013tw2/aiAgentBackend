#!/usr/bin/env python3
"""
AI Agent Backend API 使用範例

展示如何使用新的單一 AI Agent API
"""

import requests
import json
import time

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def print_separator(title):
    """印出分隔線"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_response(response_data, title="回應"):
    """格式化印出回應"""
    print(f"\n📋 {title}:")
    print("-" * 40)
    if isinstance(response_data, dict):
        for key, value in response_data.items():
            if key == "response" and isinstance(value, str) and len(value) > 100:
                print(f"{key}: {value[:100]}...")
            elif key == "data" and isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    if k == "rows" and isinstance(v, list) and len(v) > 3:
                        print(f"  {k}: {len(v)} 筆資料 (顯示前 3 筆)")
                        for i, row in enumerate(v[:3]):
                            print(f"    {i+1}. {row}")
                    else:
                        print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")
    else:
        print(response_data)

def test_basic_endpoints():
    """測試基本端點"""
    print_separator("基本端點測試")
    
    # 測試根路徑
    print("🔍 測試根路徑...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ 根路徑正常")
            print_response(response.json(), "根路徑回應")
        else:
            print(f"❌ 根路徑錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路徑異常: {e}")
    
    # 測試健康檢查
    print("\n🔍 測試健康檢查...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康檢查正常")
            print_response(response.json(), "健康檢查回應")
        else:
            print(f"❌ 健康檢查錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康檢查異常: {e}")
    
    # 測試 Agent 資訊
    print("\n🔍 測試 Agent 資訊...")
    try:
        response = requests.get(f"{BASE_URL}/agent-info")
        if response.status_code == 200:
            print("✅ Agent 資訊正常")
            print_response(response.json(), "Agent 資訊")
        else:
            print(f"❌ Agent 資訊錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ Agent 資訊異常: {e}")

def test_simple_queries():
    """測試簡單查詢"""
    print_separator("簡單查詢測試")
    
    simple_queries = [
        {
            "query": "查詢所有使用者",
            "description": "基本查詢 - 所有使用者"
        },
        {
            "query": "查詢所有產品",
            "description": "基本查詢 - 所有產品"
        },
        {
            "query": "查詢所有訂單",
            "description": "基本查詢 - 所有訂單"
        }
    ]
    
    for i, query_info in enumerate(simple_queries, 1):
        print(f"\n🔍 測試 {i}: {query_info['description']}")
        print(f"   查詢: {query_info['query']}")
        
        try:
            payload = {
                "query": query_info["query"],
                "context": {}
            }
            
            response = requests.post(
                f"{BASE_URL}/execute-agent",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print("✅ 查詢成功")
                result = response.json()
                print_response(result, f"查詢 {i} 結果")
            else:
                print(f"❌ 查詢失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
        except Exception as e:
            print(f"❌ 查詢異常: {e}")
        
        time.sleep(1)  # 避免請求過於頻繁

def test_conditional_queries():
    """測試條件查詢"""
    print_separator("條件查詢測試")
    
    conditional_queries = [
        {
            "query": "查詢所有手機類別的產品",
            "description": "條件查詢 - 特定類別產品"
        },
        {
            "query": "查詢年齡大於 30 的使用者",
            "description": "條件查詢 - 年齡篩選"
        },
        {
            "query": "查詢庫存少於 50 的產品",
            "description": "條件查詢 - 庫存篩選"
        }
    ]
    
    for i, query_info in enumerate(conditional_queries, 1):
        print(f"\n🔍 測試 {i}: {query_info['description']}")
        print(f"   查詢: {query_info['query']}")
        
        try:
            payload = {
                "query": query_info["query"],
                "context": {}
            }
            
            response = requests.post(
                f"{BASE_URL}/execute-agent",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print("✅ 查詢成功")
                result = response.json()
                print_response(result, f"條件查詢 {i} 結果")
            else:
                print(f"❌ 查詢失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
        except Exception as e:
            print(f"❌ 查詢異常: {e}")
        
        time.sleep(1)

def test_aggregation_queries():
    """測試聚合查詢"""
    print_separator("聚合查詢測試")
    
    aggregation_queries = [
        {
            "query": "計算所有訂單的總金額",
            "description": "聚合查詢 - 總金額計算"
        },
        {
            "query": "計算每個類別的產品數量",
            "description": "聚合查詢 - 分組統計"
        },
        {
            "query": "計算每個使用者的訂單總金額",
            "description": "聚合查詢 - 使用者統計"
        }
    ]
    
    for i, query_info in enumerate(aggregation_queries, 1):
        print(f"\n🔍 測試 {i}: {query_info['description']}")
        print(f"   查詢: {query_info['query']}")
        
        try:
            payload = {
                "query": query_info["query"],
                "context": {}
            }
            
            response = requests.post(
                f"{BASE_URL}/execute-agent",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print("✅ 查詢成功")
                result = response.json()
                print_response(result, f"聚合查詢 {i} 結果")
            else:
                print(f"❌ 查詢失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
        except Exception as e:
            print(f"❌ 查詢異常: {e}")
        
        time.sleep(1)

def test_complex_queries():
    """測試複雜查詢"""
    print_separator("複雜查詢測試")
    
    complex_queries = [
        {
            "query": "查詢每個使用者的訂單總金額，並按金額排序",
            "description": "複雜查詢 - 關聯查詢 + 排序"
        },
        {
            "query": "查詢每個產品類別的總庫存和平均價格",
            "description": "複雜查詢 - 分組聚合"
        },
        {
            "query": "查詢訂單金額最高的前 3 名使用者",
            "description": "複雜查詢 - 排序限制"
        }
    ]
    
    for i, query_info in enumerate(complex_queries, 1):
        print(f"\n🔍 測試 {i}: {query_info['description']}")
        print(f"   查詢: {query_info['query']}")
        
        try:
            payload = {
                "query": query_info["query"],
                "context": {}
            }
            
            response = requests.post(
                f"{BASE_URL}/execute-agent",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                print("✅ 查詢成功")
                result = response.json()
                print_response(result, f"複雜查詢 {i} 結果")
            else:
                print(f"❌ 查詢失敗: {response.status_code}")
                print(f"   錯誤: {response.text}")
        except Exception as e:
            print(f"❌ 查詢異常: {e}")
        
        time.sleep(1)

def main():
    """主函數"""
    print("🚀 AI Agent Backend API 使用範例")
    print("請確保服務器正在運行在 http://localhost:8000")
    
    try:
        # 測試基本端點
        test_basic_endpoints()
        
        # 測試簡單查詢
        test_simple_queries()
        
        # 測試條件查詢
        test_conditional_queries()
        
        # 測試聚合查詢
        test_aggregation_queries()
        
        # 測試複雜查詢
        test_complex_queries()
        
        print_separator("測試完成")
        print("🎉 所有測試完成！")
        print("\n💡 提示:")
        print("   - 您可以嘗試其他自然語言查詢")
        print("   - 查詢會自動轉換為 SQL 並執行")
        print("   - 結果會以自然語言形式回傳")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  測試被使用者中斷")
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    main() 