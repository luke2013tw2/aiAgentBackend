from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from dotenv import load_dotenv
import os

from agents.sql_agent import SQLAgent

# 載入環境變數
load_dotenv()

# 檢查 OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("請設定 OPENAI_API_KEY 環境變數")

app = FastAPI(
    title="AI Agent Backend",
    description="Python 後端 API 程式，整合 LangChain 和 LangGraph 開發的 AI Agent",
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

# 初始化 SQL Agent
sql_agent = SQLAgent()

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
        "message": "AI Agent Backend API",
        "version": "1.0.0",
        "description": "使用 LangChain 和 LangGraph 開發的 AI Agent"
    }

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy", "agent": "SQL Agent"}

@app.post("/execute-agent")
async def execute_agent(request: QueryRequest):
    """
    執行 AI Agent
    
    這個單一 API route 用於執行具有 reason、action、observe 功能的 AI Agent。
    Agent 會根據自然語言查詢產生 SQL 並查詢 SQLite 資料庫。
    """
    try:
        # 執行 AI Agent
        result = await sql_agent.execute(request.query, request.context)
        
        return QueryResponse(
            response=result["response"],
            sql_generated=result.get("sql_generated", ""),
            data=result.get("data", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 執行錯誤: {str(e)}")

@app.get("/agent-info")
async def get_agent_info():
    """取得 AI Agent 資訊"""
    return {
        "name": "SQL Agent",
        "description": "具有 reason、action、observe 功能的 AI Agent，可將自然語言轉換為 SQL 查詢",
        "capabilities": [
            "自然語言處理",
            "SQL 生成",
            "資料庫查詢",
            "結果格式化"
        ],
        "workflow": [
            "reason: 分析使用者查詢意圖",
            "action: 生成並執行 SQL 查詢",
            "observe: 觀察結果並格式化回應"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 