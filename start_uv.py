#!/usr/bin/env python3
"""
AI Agent Backend 啟動腳本 (uv 版本)

使用 uv 管理專案依賴和執行
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 8):
        print("❌ 錯誤: 需要 Python 3.8 或更高版本")
        print(f"   當前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python 版本檢查通過: {sys.version}")

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

def check_env_file():
    """檢查 .env 檔案"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 建立 .env 檔案...")
            shutil.copy(env_example, env_file)
            print("✅ .env 檔案已建立")
            print("⚠️  請編輯 .env 檔案並填入您的 OpenAI API Key")
            return False
        else:
            print("❌ 找不到 env.example 檔案")
            return False
    else:
        print("✅ .env 檔案存在")
        return True

def check_openai_key():
    """檢查 OpenAI API Key"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            print("⚠️  警告: 請在 .env 檔案中設定有效的 OPENAI_API_KEY")
            return False
        else:
            print("✅ OpenAI API Key 已設定")
            return True
    except ImportError:
        print("❌ 無法載入 python-dotenv")
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

def run_tests():
    """執行測試"""
    print("🧪 執行測試...")
    try:
        subprocess.run(['uv', 'run', 'pytest'], check=True)
        print("✅ 測試完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 測試失敗: {e}")
        return False

def format_code():
    """格式化程式碼"""
    print("🎨 格式化程式碼...")
    try:
        subprocess.run(['uv', 'run', 'black', '.'], check=True)
        subprocess.run(['uv', 'run', 'isort', '.'], check=True)
        print("✅ 程式碼格式化完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 程式碼格式化失敗: {e}")
        return False

def lint_code():
    """檢查程式碼品質"""
    print("🔍 檢查程式碼品質...")
    try:
        subprocess.run(['uv', 'run', 'flake8', '.'], check=True)
        subprocess.run(['uv', 'run', 'mypy', '.'], check=True)
        print("✅ 程式碼品質檢查完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 程式碼品質檢查失敗: {e}")
        return False

def start_server():
    """啟動服務器"""
    print("🚀 啟動 AI Agent Backend 服務器...")
    print("=" * 60)
    print("📍 服務器網址:")
    print("   🌐 主頁面: http://localhost:8000")
    print("   📖 API 文檔: http://localhost:8000/docs")
    print("   🔍 健康檢查: http://localhost:8000/health")
    print("   ℹ️  Agent 資訊: http://localhost:8000/agent-info")
    print("=" * 60)
    print("🔄 按 Ctrl+C 停止服務器")
    print("-" * 60)
    
    try:
        subprocess.run(['uv', 'run', 'python', 'main.py'])
    except KeyboardInterrupt:
        print("\n⏹️  服務器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服務器啟動失敗: {e}")

def show_help():
    """顯示幫助資訊"""
    print("""
🤖 AI Agent Backend 啟動腳本

使用方法:
  python start_uv.py [命令]

命令:
  test     執行測試
  format   格式化程式碼
  lint     檢查程式碼品質
  dev      完整開發工作流程 (測試 + 格式化 + 檢查)
  help     顯示此幫助資訊
  (無參數) 啟動服務器

範例:
  python start_uv.py test
  python start_uv.py format
  python start_uv.py dev
  python start_uv.py
""")

def main():
    """主函數"""
    print("🤖 AI Agent Backend (uv 版本)")
    print("=" * 50)
    
    # 檢查 Python 版本
    check_python_version()
    
    # 檢查並安裝 uv
    if not check_uv_installation():
        if not install_uv():
            print("❌ 無法安裝 uv，請手動安裝")
            sys.exit(1)
    
    # 檢查環境檔案
    env_ok = check_env_file()
    
    # 同步依賴
    if not sync_dependencies():
        print("❌ 依賴同步失敗")
        sys.exit(1)
    
    # 檢查 OpenAI API Key
    if env_ok:
        check_openai_key()
    
    # 處理命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            run_tests()
        elif command == 'format':
            format_code()
        elif command == 'lint':
            lint_code()
        elif command == 'dev':
            print("🔄 執行完整開發工作流程...")
            run_tests()
            format_code()
            lint_code()
            print("✅ 開發工作流程完成")
        elif command == 'help':
            show_help()
        else:
            print(f"❌ 未知命令: {command}")
            show_help()
    else:
        # 啟動服務器
        start_server()

if __name__ == "__main__":
    main() 