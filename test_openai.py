#!/usr/bin/env python3
"""
測試 OpenAI API Key 是否有效
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_api():
    """測試 OpenAI API"""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # 測試簡單的 API 調用
        print("🧪 測試 OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            max_tokens=10
        )
        
        print("✅ OpenAI API 測試成功！")
        print(f"📝 回應: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API 測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_openai_api() 