# AI Agent Backend

Python 後端 API 程式，整合 LangChain 和 LangGraph 開發的 AI Agent，支援 MCP (Model Context Protocol) 架構。

## 專案特色

- **單一 AI Agent**: 具有 `reason`、`action`、`observe` 功能的 SQL Agent
- **MCP 架構**: Agent 透過 MCP Client 連接 MCP Server 存取資料庫
- **自然語言查詢**: 將自然語言轉換為 SQL 查詢
- **SQLite 資料庫**: 內建範例資料，支援複雜查詢
- **LangGraph 工作流程**: 使用 LangChain 和 LangGraph 建立 AI Agent
- **FastAPI 後端**: 高效能的 Python Web 框架
- **uv 專案管理**: 使用 `uv` 進行依賴管理和專案配置

## 安裝與執行

### 方法一：使用 uv（推薦）

1. **安裝 uv**（如果尚未安裝）：
   ```bash
   pip install uv
   ```

2. **安裝依賴**：
   ```bash
   uv sync
   ```

3. **設定環境變數**：
   ```bash
   cp env.example .env
   # 編輯 .env 檔案，填入您的 OpenAI API Key
   ```

4. **執行應用程式**：
   ```bash
   uv run python main.py
   ```

### 方法二：使用傳統 pip

1. **安裝依賴**：
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數**：
   ```bash
   cp env.example .env
   # 編輯 .env 檔案，填入您的 OpenAI API Key
   ```

3. **執行應用程式**：
   ```bash
   python main.py
   ```

## API 端點

### 1. 根路徑
```
GET /
```
取得 API 基本資訊

### 2. 健康檢查
```
GET /health
```
檢查服務狀態

### 3. 執行 AI Agent（主要端點）
```
POST /execute-agent
```
執行具有 reason、action、observe 功能的 AI Agent

**請求格式**：
```json
{
  "query": "查詢所有使用者",
  "context": {}
}
```

**回應格式**：
```json
{
  "response": "根據您的查詢，我找到了以下使用者...",
  "sql_generated": "SELECT * FROM users",
  "data": {
    "type": "select",
    "columns": ["id", "name", "email", "age"],
    "rows": [...],
    "count": 4
  }
}
```

### 4. Agent 資訊
```
GET /agent-info
```
取得 AI Agent 的詳細資訊

## AI Agent 工作流程

### Reason（分析）
- 分析使用者的自然語言查詢意圖
- 理解查詢類型和需要的資料
- 確定查詢條件和預期結果

### Action（執行）
- 根據分析結果生成適當的 SQL 查詢
- 執行 SQL 查詢到 SQLite 資料庫
- 處理查詢結果或錯誤

### Observe（觀察）
- 觀察 SQL 執行結果
- 格式化結果為自然語言回應
- 提供清晰易懂的資料說明

## 資料庫結構

專案包含以下範例表格：

### users（使用者）
- id: 主鍵
- name: 姓名
- email: 電子郵件
- age: 年齡
- created_at: 建立時間

### products（產品）
- id: 主鍵
- name: 產品名稱
- price: 價格
- category: 類別
- stock: 庫存
- created_at: 建立時間

### orders（訂單）
- id: 主鍵
- user_id: 使用者 ID（外鍵）
- product_id: 產品 ID（外鍵）
- quantity: 數量
- total_price: 總價
- order_date: 訂單日期

## 使用範例

### 1. 查詢所有使用者
```bash
curl -X POST "http://localhost:8000/execute-agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "查詢所有使用者"}'
```

### 2. 查詢特定產品
```bash
curl -X POST "http://localhost:8000/execute-agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "查詢所有手機類別的產品"}'
```

### 3. 統計分析
```bash
curl -X POST "http://localhost:8000/execute-agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "計算所有訂單的總金額"}'
```

### 4. 複雜查詢
```bash
curl -X POST "http://localhost:8000/execute-agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "查詢每個使用者的訂單總金額，並按金額排序"}'
```

## 開發指南

### 使用 uv 進行開發

1. **安裝開發依賴**：
   ```bash
   uv sync --extra dev
   ```

2. **執行測試**：
   ```bash
   uv run pytest
   ```

3. **程式碼格式化**：
   ```bash
   uv run black .
   uv run isort .
   ```

4. **程式碼檢查**：
   ```bash
   uv run flake8 .
   uv run mypy .
   ```

5. **新增依賴**：
   ```bash
   uv add package-name
   ```

### 使用 Makefile

```bash
make install      # 安裝依賴
make install-dev  # 安裝開發依賴
make run          # 執行應用程式
make test         # 執行測試
make format       # 格式化程式碼
make lint         # 程式碼檢查
make clean        # 清理快取
make dev          # 完整開發工作流程
```

## 專案結構

```
aiAgentBackend/
├── main.py                 # FastAPI 應用程式主檔案
├── pyproject.toml          # uv 專案配置
├── requirements.txt        # pip 依賴（備用）
├── env.example            # 環境變數範例
├── start_uv.py           # uv 啟動腳本
├── start.py              # 傳統啟動腳本
├── test_api.py           # API 測試腳本
├── test_mcp_integration.py # MCP 整合測試
├── Makefile              # 開發命令
├── .gitignore            # Git 忽略檔案
├── README.md             # 專案說明
├── agents/
│   ├── __init__.py       # 套件初始化
│   └── sql_agent.py      # SQL Agent 實作（整合 MCP）
├── mcp/
│   ├── __init__.py       # MCP 模組初始化
│   ├── database_server.py # MCP Database Server
│   └── database_client.py # MCP Database Client
├── tests/
│   ├── __init__.py       # 測試套件初始化
│   └── test_sql_agent.py # SQL Agent 測試
└── examples/
    └── api_usage.py      # API 使用範例
```

## 環境變數

建立 `.env` 檔案並設定以下變數：

```env
# OpenAI API 設定
OPENAI_API_KEY=your_openai_api_key_here

# 應用程式設定
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# 資料庫設定
DATABASE_PATH=data/ai_agent.db

# 日誌設定
LOG_LEVEL=INFO
```

## MCP 架構

本專案採用 MCP (Model Context Protocol) 架構，實現 AI Agent 與外部系統的解耦：

### 架構組成

1. **MCP Server** (`mcp/database_server.py`)
   - 提供資料庫操作功能
   - 支援的工具：
     - `get_database_schema`: 取得資料庫結構
     - `execute_query`: 執行 SQL 查詢
     - `get_table_info`: 取得表格資訊
     - `get_sample_data`: 取得範例資料

2. **MCP Client** (`mcp/database_client.py`)
   - 連接 MCP Server
   - 提供統一的工具調用介面
   - 處理與 Server 的通訊

3. **SQL Agent** (`agents/sql_agent.py`)
   - 透過 MCP Client 存取資料庫
   - 實現 reason-action-observe 工作流程
   - 將自然語言轉換為 SQL 查詢

### 工作流程

```
使用者查詢 → SQL Agent → MCP Client → MCP Server → SQLite 資料庫
                ↓
            自然語言回應 ← 格式化結果 ← 查詢結果
```

### 優勢

- **解耦**: Agent 與資料庫操作分離
- **擴展性**: 可輕鬆添加新的 MCP Server
- **標準化**: 使用標準 MCP 協議
- **可維護性**: 清晰的架構分工

## 技術架構

- **FastAPI**: 高效能 Python Web 框架
- **LangChain**: LLM 應用程式開發框架
- **LangGraph**: 狀態化多角色應用程式開發
- **OpenAI GPT**: 大型語言模型
- **SQLite**: 輕量級關聯式資料庫
- **MCP**: Model Context Protocol 標準
- **uv**: 快速 Python 套件管理工具
- **Pydantic**: 資料驗證和設定管理

## 授權

MIT License 