#!/usr/bin/env python3
"""
SQL Agent (Gemini 版本)

使用 Google Gemini 模型和 LangGraph 開發的 SQL 查詢 Agent
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from mcp.database_client import DatabaseMCPClient

class SQLAgentGemini:
    """
    SQL Agent (Gemini 版本)
    
    使用 LangChain 和 LangGraph 開發，能夠：
    - reason: 分析自然語言查詢意圖
    - action: 生成並執行 SQL 查詢
    - observe: 觀察結果並格式化回應
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        """初始化 SQL Agent"""
        self.mcp_server_url = mcp_server_url
        
        # 初始化 Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # 初始化 MCP Client
        self.mcp_client = DatabaseMCPClient(mcp_server_url)
        self.mcp_connected = False
        
        # 建立 LangGraph 工作流程
        self.workflow = self._create_workflow()
    
    async def _get_database_schema(self) -> str:
        """從 MCP Server 取得資料庫結構資訊"""
        try:
            if not self.mcp_connected:
                await self.mcp_client.connect()
                self.mcp_connected = True
            
            schema = await self.mcp_client.get_schema()
            tables = schema.get("tables", [])
            
            schema_info = []
            for table in tables:
                table_name = table.get("name", "")
                columns = table.get("columns", [])
                
                schema_info.append(f"表格: {table_name}")
                for col in columns:
                    col_name = col.get("name", "")
                    col_type = col.get("type", "")
                    schema_info.append(f"  - {col_name} ({col_type})")
                schema_info.append("")
            
            return "\n".join(schema_info)
            
        except Exception as e:
            return f"無法取得資料庫結構: {str(e)}"
    
    def _create_workflow(self) -> StateGraph:
        """建立 LangGraph 工作流程"""
        
        # 定義狀態結構
        from typing import TypedDict, Annotated
        
        class AgentState(TypedDict):
            query: str
            reasoning: str
            sql_query: str
            execution_result: Any
            response: str
            chart_description: str
            context: Dict[str, Any]
        
        # 1. REASON: 分析查詢意圖
        async def reason(state: AgentState) -> AgentState:
            """分析使用者查詢意圖"""
            query = state["query"]
            schema = await self._get_database_schema()
            
            system_prompt = f"""
            你是一個 SQL 查詢分析專家。請分析使用者的自然語言查詢，並理解其意圖。
            
            資料庫結構：
            {schema}
            
            請分析以下查詢的意圖：
            "{query}"
            
            請提供：
            1. 查詢類型（SELECT、INSERT、UPDATE、DELETE、分析等）
            2. 需要的表格
            3. 查詢條件
            4. 預期的結果格式
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            reasoning = response.content
            
            return {
                **state,
                "reasoning": reasoning
            }
        
        # 2. ACTION: 生成並執行 SQL
        async def action(state: AgentState) -> AgentState:
            """生成並執行 SQL 查詢"""
            query = state["query"]
            reasoning = state["reasoning"]
            schema = await self._get_database_schema()
            
            system_prompt = f"""
            你是一個 SQL 生成專家。根據使用者的查詢和分析結果，生成適當的 SQL 查詢。
            
            資料庫結構：
            {schema}
            
            使用者查詢：{query}
            分析結果：{reasoning}
            
            請生成對應的 SQL 查詢。只返回 SQL 語句，不要包含其他說明。
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            sql_query = self._extract_sql_query(response.content)
            
            # 使用 MCP Client 執行 SQL 查詢
            try:
                # 確保 MCP Client 已連接
                if not self.mcp_connected:
                    await self.mcp_client.connect()
                    self.mcp_connected = True
                
                # 通過 MCP 執行查詢
                execution_result = await self.mcp_client.call_tool("execute_query", {"sql": sql_query})
                
            except Exception as e:
                execution_result = {
                    "type": "error",
                    "error": str(e),
                    "sql": sql_query
                }
            
            return {
                **state,
                "sql_query": sql_query,
                "execution_result": execution_result
            }
        
        # 3. OBSERVE: 觀察結果並格式化回應
        def observe(state: AgentState) -> AgentState:
            """觀察執行結果並生成回應"""
            query = state["query"]
            reasoning = state["reasoning"]
            sql_query = state["sql_query"]
            execution_result = state["execution_result"]
            
            # 格式化查詢結果，特別是多筆資料的顯示
            formatted_result = self._format_execution_result(execution_result)
            
            system_prompt = f"""
            你是一個資料分析專家。請根據 SQL 查詢結果，為使用者提供清晰、易懂的回應。
            
            使用者原始查詢：{query}
            分析過程：{reasoning}
            執行的 SQL：{sql_query}
            查詢結果：{formatted_result}
            
            請提供：
            1. 簡潔明瞭的結果說明
            2. 如果有資料，請用自然語言描述，並以列表形式呈現多筆資料
            3. 如果有錯誤，請解釋問題並提供建議
            4. 保持專業但友善的語氣
            5. 對於多筆資料，請使用編號列表（1. 2. 3.）來呈現
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"查詢結果：{formatted_result}")
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                **state,
                "response": response.content
            }
        
        # 4. VISUALIZE: 如果有多筆資料，生成圖表
        async def visualize(state: AgentState) -> AgentState:
            """如果有多筆資料，生成圖表"""
            execution_result = state["execution_result"]
            query = state["query"]
            
            # 檢查是否有多筆資料需要生成圖表
            should_generate_chart = self._should_generate_chart(execution_result)
            
            if not should_generate_chart:
                return {
                    **state,
                    "chart_description": "無需生成圖表"
                }
            
            # 格式化資料用於圖表生成
            chart_data = self._prepare_chart_data(execution_result)
            
            system_prompt = f"""
            你是一個資料視覺化專家。請根據以下資料生成適合的圖表描述。
            
            使用者查詢：{query}
            資料內容：{chart_data}
            
            請提供：
            1. 建議的圖表類型（柱狀圖、折線圖、圓餅圖、散點圖等）
            2. 圖表的標題和軸標籤
            3. 圖表的顏色建議
            4. 圖表的關鍵洞察點
            5. 使用 Mermaid 語法生成圖表代碼
            
            請以以下格式回應：
            ## 圖表建議
            [圖表類型說明]
            
            ## 圖表代碼 (Mermaid)
            ```mermaid
            [Mermaid 圖表代碼]
            ```
            
            ## 關鍵洞察
            [資料分析洞察]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"請為以下資料生成圖表：{chart_data}")
            ]
            
            chart_response = self.llm.invoke(messages)
            
            return {
                **state,
                "chart_description": chart_response.content
            }
        
        # 建立工作流程圖
        workflow = StateGraph(AgentState)
        
        # 添加節點
        workflow.add_node("reason", reason)
        workflow.add_node("action", action)
        workflow.add_node("observe", observe)
        workflow.add_node("visualize", visualize)
        
        # 設定流程
        workflow.set_entry_point("reason")
        workflow.add_edge("reason", "action")
        workflow.add_edge("action", "observe")
        workflow.add_edge("observe", "visualize")
        workflow.add_edge("visualize", END)
        
        return workflow.compile()
    
    def _extract_sql_query(self, llm_response: str) -> str:
        """從 LLM 回應中提取 SQL 查詢"""
        # 移除可能的 markdown 格式
        sql_query = llm_response.strip()
        
        # 如果被 ```sql 包圍，移除
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        # 如果被 ``` 包圍，移除
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        return sql_query.strip()
    
    def _format_execution_result(self, execution_result: Any) -> str:
        """格式化執行結果，特別是多筆資料的顯示"""
        if not execution_result:
            return "無查詢結果"
        
        # 如果是錯誤結果
        if isinstance(execution_result, dict) and execution_result.get("type") == "error":
            return f"執行錯誤: {execution_result.get('error', '未知錯誤')}"
        
        # 如果是成功結果
        if isinstance(execution_result, dict) and execution_result.get("success"):
            data = execution_result.get("data", {})
            row_count = execution_result.get("row_count", 0)
            
            if row_count == 0:
                return "查詢成功，但沒有找到符合條件的資料"
            
            # 格式化多筆資料
            if isinstance(data, dict) and "rows" in data:
                rows = data["rows"]
                if len(rows) == 1:
                    # 單筆資料
                    return f"查詢成功，找到 1 筆資料：\n{json.dumps(rows[0], ensure_ascii=False, indent=2)}"
                else:
                    # 多筆資料 - 使用列表格式
                    formatted_rows = []
                    for i, row in enumerate(rows, 1):
                        row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
                        formatted_rows.append(f"{i}. {row_str}")
                    
                    return f"查詢成功，找到 {len(rows)} 筆資料：\n" + "\n".join(formatted_rows)
            
            # 其他格式的資料
            return f"查詢成功，找到 {row_count} 筆資料：\n{json.dumps(data, ensure_ascii=False, indent=2)}"
        
        # 其他格式的結果
        return json.dumps(execution_result, ensure_ascii=False, indent=2)
    
    def _should_generate_chart(self, execution_result: Any) -> bool:
        """判斷是否需要生成圖表"""
        if not execution_result:
            return False
        
        # 如果是錯誤結果，不需要生成圖表
        if isinstance(execution_result, dict) and execution_result.get("type") == "error":
            return False
        
        # 如果是成功結果且有資料
        if isinstance(execution_result, dict) and execution_result.get("success"):
            data = execution_result.get("data", {})
            row_count = execution_result.get("row_count", 0)
            
            # 需要至少 2 筆資料才生成圖表
            if row_count >= 2:
                # 檢查是否有數值型欄位適合繪圖
                if isinstance(data, dict) and "rows" in data and len(data["rows"]) > 0:
                    first_row = data["rows"][0]
                    # 檢查是否有數值型欄位
                    numeric_fields = []
                    for key, value in first_row.items():
                        if isinstance(value, (int, float)) and key not in ['id']:
                            numeric_fields.append(key)
                    
                    return len(numeric_fields) > 0
        
        return False
    
    def _prepare_chart_data(self, execution_result: Any) -> str:
        """準備圖表資料"""
        if not execution_result or not isinstance(execution_result, dict):
            return "無效的資料"
        
        data = execution_result.get("data", {})
        if not isinstance(data, dict) or "rows" not in data:
            return "無資料行"
        
        rows = data["rows"]
        if not rows:
            return "空資料"
        
        # 分析資料結構
        first_row = rows[0]
        columns = list(first_row.keys())
        
        # 分類欄位類型
        numeric_fields = []
        text_fields = []
        for key, value in first_row.items():
            if isinstance(value, (int, float)) and key not in ['id']:
                numeric_fields.append(key)
            elif isinstance(value, str) and key not in ['id']:
                text_fields.append(key)
        
        # 格式化資料摘要
        summary = f"""
資料摘要：
- 總筆數: {len(rows)}
- 欄位數: {len(columns)}
- 數值型欄位: {', '.join(numeric_fields) if numeric_fields else '無'}
- 文字型欄位: {', '.join(text_fields) if text_fields else '無'}

前 5 筆資料範例：
"""
        
        # 添加前 5 筆資料
        for i, row in enumerate(rows[:5], 1):
            row_str = ", ".join([f"{k}: {v}" for k, v in row.items()])
            summary += f"{i}. {row_str}\n"
        
        if len(rows) > 5:
            summary += f"... 還有 {len(rows) - 5} 筆資料"
        
        return summary
    
    async def execute(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        執行 AI Agent
        
        Args:
            query: 自然語言查詢
            context: 額外上下文資訊
        
        Returns:
            包含回應、生成的 SQL 和資料的字典
        """
        # 準備初始狀態
        initial_state = {
            "query": query,
            "reasoning": "",
            "sql_query": "",
            "execution_result": None,
            "response": "",
            "chart_description": "",
            "context": context
        }
        
        # 執行工作流程
        result = await self.workflow.ainvoke(initial_state)
        
        return {
            "response": result["response"],
            "sql_generated": result["sql_query"],
            "data": result["execution_result"],
            "reasoning": result["reasoning"],
            "chart_description": result.get("chart_description", "")
        }
    
    async def get_database_info(self) -> Dict[str, Any]:
        """取得資料庫資訊"""
        try:
            if not self.mcp_connected:
                await self.mcp_client.connect()
                self.mcp_connected = True
            
            schema = await self.mcp_client.get_schema()
            return {
                "mcp_server_url": self.mcp_server_url,
                "schema": schema
            }
        except Exception as e:
            return {
                "error": str(e),
                "mcp_server_url": self.mcp_server_url
            }
    
    async def close(self):
        """關閉 MCP Client 連接"""
        if self.mcp_connected:
            await self.mcp_client.disconnect()
            self.mcp_connected = False
    
    def __del__(self):
        """解構函數"""
        # 注意：這裡無法使用 await，所以只是標記
        pass 