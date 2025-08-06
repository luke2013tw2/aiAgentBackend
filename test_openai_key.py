import os
import openai
from dotenv import load_dotenv

def test_openai_api():
    """測試 OpenAI API Key 是否有效"""
    print("🔍 測試 OpenAI API Key...")
    print("=" * 50)
    
    # 載入環境變數
    load_dotenv()
    
    # 取得 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ 錯誤：未找到 OPENAI_API_KEY 環境變數")
        print("請在 .env 檔案中設定您的 OpenAI API Key")
        return False
    
    if api_key == "your_openai_api_key_here" or api_key == "OPENAI_API_KEY 1111":
        print("❌ 錯誤：API Key 是預設值，請設定有效的 API Key")
        return False
    
    print(f"✅ 找到 API Key: {api_key[:10]}...")
    
    try:
        # 設定 OpenAI 客戶端
        client = openai.OpenAI(api_key=api_key)
        
        # 測試簡單的 API 呼叫
        print("🔄 正在測試 API 呼叫...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "請回覆 'Hello'"}
            ],
            max_tokens=10
        )
        
        print("✅ API 呼叫成功！")
        print(f"回應: {response.choices[0].message.content}")
        return True
        
    except openai.AuthenticationError:
        print("❌ 認證錯誤：API Key 無效或已過期")
        return False
    except openai.RateLimitError:
        print("❌ 速率限制：API 呼叫次數已達上限")
        return False
    except openai.APIError as e:
        print(f"❌ API 錯誤：{e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤：{e}")
        return False

if __name__ == "__main__":
    success = test_openai_api()
    if success:
        print("\n🎉 OpenAI API Key 測試成功！可以正常使用。")
    else:
        print("\n⚠️  OpenAI API Key 測試失敗，建議使用模擬模式。") 