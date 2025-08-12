# MCP Client 更新說明

## 更新內容

### 1. 修改 `aiAgentBackend/mcp/database_client.py`

**主要變更：**
- 將原本直接使用本地 `DatabaseMCPServer` 的方式改為 HTTP 連接到外部 MCP Server
- 預設連接到 `http://localhost:8001` 的 MCP Server
- 添加了 `aiohttp` 依賴用於 HTTP 請求
- 新增同步版本客戶端 `DatabaseMCPClientSync`

**新增功能：**
- 異步上下文管理器支援 (`async with`)
- 健康檢查 API
- 完整的 HTTP 請求處理
- 錯誤處理和重試機制

### 2. 移除 `aiAgentBackend/mcp/database_server.py`

**移除原因：**
- 不再需要本地的 MCP Server 實作
- 統一使用外部的 MCP Server (`aiMcpServer`)
- 簡化架構，避免重複實作

### 3. 更新 `pyproject.toml`

**新增依賴：**
```toml
dependencies = [
    # ... 其他依賴 ...
    "aiohttp>=3.9.0,<4.0.0",
]
```

**移除 `requirements.txt`：**
- 統一使用 `pyproject.toml` 管理套件依賴
- 使用 `uv` 作為套件管理工具

### 4. 更新 `mcp/__init__.py`

**移除導出：**
```python
# 移除
from .database_server import DatabaseMCPServer

# 保留
from .database_client import DatabaseMCPClient, DatabaseMCPClientSync
```

### 5. 更新測試檔案

**`test_simple_mcp.py` 更新：**
- 移除對本地 `DatabaseMCPServer` 的測試
- 改為測試與外部 MCP Server 的連接
- 添加更詳細的錯誤處理和診斷資訊

### 6. 更新啟動腳本

**`start.py` 更新：**
- 使用 `uv` 而不是 `pip` 管理依賴
- 添加 `uv sync` 命令同步依賴
- 使用 `uv run` 執行 Python 腳本

## 架構變更

### 之前（本地 MCP Server）
```
aiAgentBackend/
├── mcp/
│   ├── database_server.py    # ❌ 已移除
│   └── database_client.py    # ✅ 更新為 HTTP 客戶端
```

### 現在（外部 MCP Server）
```
myAiAgent/
├── aiAgentBackend/           # AI Agent 後端
│   └── mcp/
│       └── database_client.py # HTTP 客戶端
└── aiMcpServer/              # 獨立的 MCP Server
    └── mcp_server/
        └── database.py       # MCP Server 實作
```

## 使用方式

### 安裝依賴

```bash
# 使用 uv 同步依賴
uv sync

# 或者使用 uv add 添加新依賴
uv add aiohttp
```

### 異步版本（推薦）

```python
from mcp.database_client import DatabaseMCPClient

async def example():
    async with DatabaseMCPClient() as client:
        await client.connect()
        
        # 健康檢查
        health = await client.health_check()
        
        # 執行查詢
        result = await client.execute_query("SELECT * FROM users LIMIT 3")
        
        # 取得資料庫結構
        schema = await client.get_schema()
```

### 同步版本

```python
from mcp.database_client import DatabaseMCPClientSync

def example():
    client = DatabaseMCPClientSync()
    
    # 健康檢查
    health = client.health_check()
    
    # 執行查詢
    result = client.execute_query("SELECT * FROM users LIMIT 3")
    
    # 取得資料庫結構
    schema = client.get_schema()
```

## API 端點對應

| 工具名稱 | HTTP 方法 | 端點 | 說明 |
|---------|----------|------|------|
| `get_database_schema` | GET | `/api/schema` | 取得資料庫結構 |
| `execute_query` | POST | `/api/query` | 執行 SQL 查詢 |
| `get_table_info` | GET | `/api/table/{table_name}` | 取得表格資訊 |
| `get_sample_data` | GET | `/api/table/{table_name}/sample` | 取得範例資料 |
| `health_check` | GET | `/health` | 健康檢查 |

## 測試

執行測試腳本：
```bash
cd aiAgentBackend
uv run python test_mcp_client_update.py

# 或執行簡化測試
uv run python test_simple_mcp.py
```

## 啟動服務

### 使用 uv 啟動

```bash
# 啟動 AI Agent Backend
cd aiAgentBackend
uv run python start_uv.py

# 啟動 MCP Server
cd aiMcpServer
uv run python start_server.py
```

## 注意事項

1. **MCP Server 必須運行**：確保 `aiMcpServer` 在 `http://localhost:8001` 運行
2. **網路連接**：需要網路連接來訪問 MCP Server
3. **錯誤處理**：所有 HTTP 請求都有適當的錯誤處理
4. **依賴管理**：使用 `uv sync` 同步依賴，而不是 `pip install -r requirements.txt`
5. **Python 版本**：需要 Python 3.10 或更高版本
6. **架構簡化**：移除了本地的 MCP Server，統一使用外部服務

## 相容性

- 保持與現有 SQL Agent 的相容性
- 所有現有的 `call_tool` 方法都繼續支援
- 新增了更直接的 API 方法（如 `execute_query`, `get_schema` 等）
- 統一使用 `pyproject.toml` 管理套件依賴
- 簡化了架構，移除了重複的本地 MCP Server 實作

## 開發工具

### 程式碼格式化
```bash
uv run black .
uv run isort .
```

### 程式碼品質檢查
```bash
uv run flake8 .
uv run mypy .
```

### 執行測試
```bash
uv run pytest
```

### 完整開發工作流程
```bash
uv run python start_uv.py dev
```
