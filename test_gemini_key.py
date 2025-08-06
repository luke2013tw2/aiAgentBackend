import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_api():
    """測試 Gemini API Key 是否有效"""
    print("🔍 測試 Gemini API Key...")
    print("=" * 50)
    
    # 載入環境變數
    load_dotenv()
    
    # 取得 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ 錯誤：未找到 GEMINI_API_KEY 環境變數")
        print("請在 .env 檔案中設定您的 Gemini API Key")
        return False
    
    if api_key == "your_gemini_api_key_here":
        print("❌ 錯誤：API Key 是預設值，請設定有效的 Gemini API Key")
        return False
    
    print(f"✅ 找到 API Key: {api_key[:10]}...")
    
    try:
        # 設定 Gemini 客戶端
        genai.configure(api_key=api_key)
        
        # 測試簡單的 API 呼叫
        print("🔄 正在測試 API 呼叫...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("請回覆 'Hello'")
        
        print("✅ API 呼叫成功！")
        print(f"回應: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ API 錯誤：{e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("\n🎉 Gemini API Key 測試成功！可以正常使用。")
    else:
        print("\n⚠️  Gemini API Key 測試失敗，建議檢查 API Key 設定。") 