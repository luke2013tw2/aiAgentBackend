#!/usr/bin/env python3
"""
AI Agent Backend 啟動腳本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    if sys.version_info < (3, 10):
        print("錯誤: 需要Python 3.10或更高版本")
        print(f"當前版本: {sys.version}")
        return False
    return True

def check_env_file():
    """檢查環境變數檔案"""
    env_file = Path(".env")
    if not env_file.exists():
        print("警告: 未找到 .env 檔案")
        print("請複製 env.example 到 .env 並設定您的 OpenAI API Key")
        return False
    return True

def check_openai_key():
    """檢查OpenAI API Key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("錯誤: 請在 .env 檔案中設定有效的 OpenAI API Key")
        return False
    return True

def check_uv_installation():
    """檢查 uv 是否已安裝"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv 已安裝: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False

def install_uv():
    """安裝 uv"""
    print("📦 正在安裝 uv...")
    try:
        # 使用 pip 安裝 uv
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
        print("✅ uv 安裝成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ uv 安裝失敗: {e}")
        return False

def sync_dependencies():
    """同步專案依賴"""
    print("📦 同步專案依賴...")
    try:
        subprocess.run(['uv', 'sync'], check=True)
        print("✅ 依賴同步完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依賴同步失敗: {e}")
        return False

def start_server():
    """啟動伺服器"""
    print("🚀 啟動AI Agent Backend API伺服器...")
    print("📍 伺服器將在 http://localhost:8000 運行")
    print("📖 API 文檔: http://localhost:8000/docs")
    print("🔍 健康檢查: http://localhost:8000/health")
    print("ℹ️  Agent 資訊: http://localhost:8000/agent-info")
    print("=" * 50)
    print("🔄 按 Ctrl+C 停止伺服器")
    print("-" * 50)
    
    try:
        subprocess.run(['uv', 'run', 'python', 'main.py'])
    except KeyboardInterrupt:
        print("\n⏹️ 伺服器已停止")
    except Exception as e:
        print(f"❌ 啟動伺服器時發生錯誤: {e}")

def main():
    """主函數"""
    print("🤖 AI Agent Backend 啟動檢查")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 檢查並安裝 uv
    if not check_uv_installation():
        if not install_uv():
            print("❌ 無法安裝 uv，請手動安裝")
            sys.exit(1)
    
    # 檢查環境變數檔案
    if not check_env_file():
        print("請先設定環境變數檔案")
        sys.exit(1)
    
    # 載入環境變數
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("錯誤: 請先安裝 python-dotenv")
        print("執行: uv add python-dotenv")
        sys.exit(1)
    
    # 檢查OpenAI API Key
    if not check_openai_key():
        sys.exit(1)
    
    # 同步依賴套件
    if not sync_dependencies():
        sys.exit(1)
    
    # 啟動伺服器
    start_server()

if __name__ == "__main__":
    main() 