from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from dotenv import load_dotenv
import os

# 使用 Gemini 版本的 SQL Agent
from agents.sql_agent_gemini import SQLAgentGemini

# 載入環境變數
load_dotenv()

app = FastAPI(
    title="AI Agent Backend (Gemini)",
    description="Python 後端 API 程式，整合 LangChain 和 LangGraph 開發的 AI Agent - Gemini 版本",
    version="1.0.0"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Gemini SQL Agent
sql_agent = SQLAgentGemini()

class QueryRequest(BaseModel):
    """查詢請求模型"""
    query: str
    context: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    """查詢回應模型"""
    response: str
    sql_generated: str = ""
    data: Dict[str, Any] = {}

@app.get("/")
async def root():
    """根路徑"""
    return {
        "message": "AI Agent Backend API (Gemini)",
        "version": "1.0.0",
        "description": "使用 LangChain 和 LangGraph 開發的 AI Agent - Gemini 版本",
        "mode": "gemini",
        "note": "此版本使用 Google Gemini API"
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy", 
        "agent": "SQL Agent (Gemini)",
        "mode": "gemini",
        "database": "SQLite"
    }

@app.post("/execute-agent")
async def execute_agent(request: QueryRequest):
    """
    執行 AI Agent（Gemini 版本）
    
    這個單一 API route 用於執行具有 reason、action、observe 功能的 AI Agent。
    Agent 會根據自然語言查詢產生 SQL 並查詢 SQLite 資料庫。
    
    Gemini 版本特點：
    - 使用 Google Gemini API
    - 真實的 AI 分析和回應
    - 支援複雜的自然語言查詢
    """
    try:
        # 執行 AI Agent
        result = await sql_agent.execute(request.query, request.context)
        
        return QueryResponse(
            response=result["response"],
            sql_generated=result.get("sql_generated", ""),
            data=result.get("data", {}) if isinstance(result.get("data"), dict) else {"rows": result.get("data", [])}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 執行錯誤: {str(e)}")

@app.get("/agent-info")
async def get_agent_info():
    """取得 AI Agent 資訊"""
    return {
        "name": "SQL Agent (Gemini)",
        "description": "具有 reason、action、observe 功能的 AI Agent，可將自然語言轉換為 SQL 查詢 - Gemini 版本",
        "mode": "gemini",
        "capabilities": [
            "自然語言處理（Gemini）",
            "SQL 生成",
            "資料庫查詢",
            "結果格式化"
        ],
        "workflow": [
            "reason: 分析使用者查詢意圖（Gemini）",
            "action: 生成並執行 SQL 查詢",
            "observe: 觀察結果並格式化回應"
        ],
        "supported_queries": [
            "查詢所有使用者",
            "顯示所有產品", 
            "查詢訂單",
            "複雜查詢（由 Gemini 分析）"
        ],
        "note": "此版本使用 Google Gemini API，提供真實的 AI 功能"
    }

@app.get("/database-info")
async def get_database_info():
    """取得資料庫資訊"""
    try:
        db_info = sql_agent.get_database_info()
        return {
            "status": "success",
            "database_info": db_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"無法取得資料庫資訊: {str(e)}")

if __name__ == "__main__":
    print("🚀 啟動 AI Agent Backend (Gemini)")
    print("📍 服務器將在 http://localhost:8000 運行")
    print("📖 API 文檔: http://localhost:8000/docs")
    print("🔧 模式: Gemini 模式（使用 Google Gemini API）")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 