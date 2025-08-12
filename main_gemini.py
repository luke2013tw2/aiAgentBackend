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
    reasoning: str = ""
    chart_description: str = ""

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
            data=result.get("data", {}) if isinstance(result.get("data"), dict) else {"rows": result.get("data", [])},
            reasoning=result.get("reasoning", ""),
            chart_description=result.get("chart_description", "")
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
            "observe: 觀察結果並格式化回應",
            "visualize: 自動生成圖表（多筆資料時）"
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

@app.get("/chart-viewer")
async def get_chart_viewer():
    """取得圖表檢視器 HTML 頁面"""
    from fastapi.responses import HTMLResponse
    
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Agent 圖表檢視器</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; }
            .chart-section { margin: 20px 0; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafafa; }
            .chart-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; padding: 10px; background: #e3f2fd; border-radius: 5px; }
            .mermaid { text-align: center; margin: 20px 0; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .input-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }
            .input-section input[type="text"] { width: 70%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            .input-section button { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 10px; }
            .insights { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4caf50; }
            .data-info { background: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #ff9800; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎨 AI Agent 圖表檢視器</h1>
                <p>將 Mermaid 語法轉換為美觀的圖表</p>
            </div>

            <div class="input-section">
                <h3>🔍 測試查詢</h3>
                <input type="text" id="queryInput" placeholder="輸入查詢，例如：查詢所有產品的價格分布" value="查詢所有產品的價格分布">
                <button onclick="executeQuery()">執行查詢</button>
            </div>

            <div id="loading" style="display: none; text-align: center; padding: 20px; color: #666;">
                <p>🔄 正在處理查詢，請稍候...</p>
            </div>

            <div id="error" style="display: none; background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #f44336;"></div>

            <div id="results" style="display: none;">
                <div class="chart-section">
                    <div class="chart-title">📊 圖表建議</div>
                    <div id="chartAdvice"></div>
                </div>

                <div class="chart-section">
                    <div class="chart-title">🎨 圖表顯示</div>
                    <div id="chartContainer" class="mermaid"></div>
                </div>

                <div class="chart-section">
                    <div class="chart-title">💡 關鍵洞察</div>
                    <div id="insights" class="insights"></div>
                </div>

                <div class="chart-section">
                    <div class="chart-title">📋 查詢結果</div>
                    <div id="dataInfo" class="data-info"></div>
                </div>
            </div>
        </div>

        <script>
            mermaid.initialize({ startOnLoad: true, theme: 'default' });

            async function executeQuery() {
                const query = document.getElementById('queryInput').value;
                if (!query.trim()) { alert('請輸入查詢內容'); return; }

                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                document.getElementById('results').style.display = 'none';

                try {
                    const response = await fetch('/execute-agent', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: query, context: {} })
                    });

                    if (!response.ok) { throw new Error(`HTTP error! status: ${response.status}`); }

                    const result = await response.json();
                    document.getElementById('loading').style.display = 'none';
                    displayResults(result);
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').innerHTML = `<strong>錯誤：</strong>${error.message}`;
                }
            }

            function displayResults(result) {
                // 顯示圖表建議
                const chartAdvice = document.getElementById('chartAdvice');
                if (result.chart_description && result.chart_description !== '無需生成圖表') {
                    const adviceMatch = result.chart_description.match(/## 圖表建議\s*([\s\S]*?)(?=##|$)/);
                    chartAdvice.innerHTML = adviceMatch ? adviceMatch[1].trim() : result.chart_description;
                } else {
                    chartAdvice.innerHTML = '<p>此查詢不需要生成圖表</p>';
                }

                // 顯示圖表
                const chartContainer = document.getElementById('chartContainer');
                if (result.chart_description && result.chart_description.includes('```mermaid')) {
                    const mermaidMatch = result.chart_description.match(/```mermaid\s*([\s\S]*?)\s*```/);
                    if (mermaidMatch) {
                        chartContainer.innerHTML = mermaidMatch[1].trim();
                        mermaid.init();
                    } else {
                        chartContainer.innerHTML = '<p>無法解析 Mermaid 代碼</p>';
                    }
                } else {
                    chartContainer.innerHTML = '<p>無圖表代碼</p>';
                }

                // 顯示關鍵洞察
                const insights = document.getElementById('insights');
                if (result.chart_description && result.chart_description.includes('## 關鍵洞察')) {
                    const insightsMatch = result.chart_description.match(/## 關鍵洞察\s*([\s\S]*?)(?=##|$)/);
                    insights.innerHTML = `<h4>📈 分析洞察</h4><p>${insightsMatch ? insightsMatch[1].trim() : '無洞察資訊'}</p>`;
                } else {
                    insights.innerHTML = '<h4>📈 分析洞察</h4><p>無洞察資訊</p>';
                }

                // 顯示查詢結果
                const dataInfo = document.getElementById('dataInfo');
                if (result.data && result.data.success) {
                    const rowCount = result.data.row_count || 0;
                    dataInfo.innerHTML = `
                        <h4>📊 查詢結果</h4>
                        <p><strong>資料筆數：</strong>${rowCount}</p>
                        <p><strong>生成的 SQL：</strong><code>${result.sql_generated}</code></p>
                        <p><strong>回應：</strong>${result.response}</p>
                    `;
                } else {
                    dataInfo.innerHTML = '<h4>📊 查詢結果</h4><p>查詢失敗或無資料</p>';
                }

                document.getElementById('results').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 啟動 AI Agent Backend (Gemini)")
    print("📍 服務器將在 http://localhost:8000 運行")
    print("📖 API 文檔: http://localhost:8000/docs")
    print("🔧 模式: Gemini 模式（使用 Google Gemini API）")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 