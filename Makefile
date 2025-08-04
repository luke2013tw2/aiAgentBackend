# AI Agent Backend Makefile
# 使用 uv 進行專案管理

.PHONY: help install install-dev run test format lint clean dev

# 預設目標
help:
	@echo "🤖 AI Agent Backend Makefile"
	@echo "================================"
	@echo ""
	@echo "可用命令:"
	@echo "  make install      - 安裝生產依賴"
	@echo "  make install-dev  - 安裝開發依賴"
	@echo "  make run          - 啟動服務器"
	@echo "  make test         - 執行測試"
	@echo "  make format       - 格式化程式碼"
	@echo "  make lint         - 檢查程式碼品質"
	@echo "  make clean        - 清理快取和臨時檔案"
	@echo "  make dev          - 完整開發工作流程"
	@echo "  make help         - 顯示此幫助資訊"
	@echo ""
	@echo "範例:"
	@echo "  make install-dev  # 安裝所有依賴"
	@echo "  make run          # 啟動服務器"
	@echo "  make dev          # 執行完整開發流程"

# 安裝生產依賴
install:
	@echo "📦 安裝生產依賴..."
	uv sync
	@echo "✅ 生產依賴安裝完成"

# 安裝開發依賴
install-dev:
	@echo "📦 安裝開發依賴..."
	uv sync --extra dev
	@echo "✅ 開發依賴安裝完成"

# 啟動服務器
run:
	@echo "🚀 啟動 AI Agent Backend 服務器..."
	@echo "📍 服務器將在 http://localhost:8000 運行"
	@echo "📖 API 文檔: http://localhost:8000/docs"
	@echo "🔄 按 Ctrl+C 停止服務器"
	@echo "----------------------------------------"
	uv run python main.py

# 執行測試
test:
	@echo "🧪 執行測試..."
	uv run pytest -v
	@echo "✅ 測試完成"

# 格式化程式碼
format:
	@echo "🎨 格式化程式碼..."
	uv run black .
	uv run isort .
	@echo "✅ 程式碼格式化完成"

# 檢查程式碼品質
lint:
	@echo "🔍 檢查程式碼品質..."
	uv run flake8 .
	uv run mypy .
	@echo "✅ 程式碼品質檢查完成"

# 清理快取和臨時檔案
clean:
	@echo "🧹 清理快取和臨時檔案..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".uv" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

# 完整開發工作流程
dev: clean install-dev test format lint
	@echo "🎉 完整開發工作流程完成！"
	@echo ""
	@echo "📋 工作流程摘要:"
	@echo "  ✅ 清理快取和臨時檔案"
	@echo "  ✅ 安裝開發依賴"
	@echo "  ✅ 執行測試"
	@echo "  ✅ 格式化程式碼"
	@echo "  ✅ 檢查程式碼品質"

# 快速啟動（包含依賴檢查）
quick-start: install-dev
	@echo "🚀 快速啟動..."
	make run

# 測試 API
test-api:
	@echo "🔍 測試 API..."
	uv run python test_api.py

# 執行範例
example:
	@echo "📖 執行 API 使用範例..."
	uv run python examples/api_usage.py

# 顯示專案資訊
info:
	@echo "📊 專案資訊:"
	@echo "  專案名稱: AI Agent Backend"
	@echo "  版本: 1.0.0"
	@echo "  描述: Python 後端 API 程式，整合 LangChain 和 LangGraph 開發的 AI Agent"
	@echo ""
	@echo "🔧 技術架構:"
	@echo "  - FastAPI: 高效能 Python Web 框架"
	@echo "  - LangChain: LLM 應用程式開發框架"
	@echo "  - LangGraph: 狀態化多角色應用程式開發"
	@echo "  - SQLite: 輕量級關聯式資料庫"
	@echo "  - uv: 快速 Python 套件管理工具"
	@echo ""
	@echo "🤖 AI Agent 功能:"
	@echo "  - reason: 分析自然語言查詢意圖"
	@echo "  - action: 生成並執行 SQL 查詢"
	@echo "  - observe: 觀察結果並格式化回應" 