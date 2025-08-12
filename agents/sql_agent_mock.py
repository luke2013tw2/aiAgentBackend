#!/usr/bin/env python3
"""
SQL Agent Mock 版本

用於測試的模擬版本，不依賴真實的 LLM 和資料庫
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from mcp.database_client import DatabaseMCPClient

class MockLLM:
    """模擬 LLM 回應"""
    
    def __init__(self):
        self.responses = {
            "reason": "這是一個 SELECT 查詢，需要從 users 表格中取得使用者資訊。",
            "sql": "SELECT * FROM users LIMIT 3",
            "observe": "查詢成功執行，返回了 3 筆使用者資料。"
        }
    
    def invoke(self, messages):
        """模擬 LLM 回應"""
        content = messages[-1].content if messages else ""
        
        if "分析" in content or "reason" in content.lower():
            return type('obj', (object,), {'content': self.responses["reason"]})()
        elif "SQL" in content or "生成" in content:
            return type('obj', (object,), {'content': self.responses["sql"]})()
        else:
            return type('obj', (object,), {'content': self.responses["observe"]})()

class SQLAgentMock:
    """
    SQL Agent Mock 版本
    
    用於測試的模擬版本，不依賴真實的 LLM 和資料庫
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8001"):
        """初始化 SQL Agent Mock"""
        self.mcp_server_url = mcp_server_url
        
        # 初始化 Mock LLM
        self.llm = MockLLM()
        
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
            
            system_prompt = f"""
            你是一個資料分析專家。請根據 SQL 查詢結果，為使用者提供清晰、易懂的回應。
            
            使用者原始查詢：{query}
            分析過程：{reasoning}
            執行的 SQL：{sql_query}
            查詢結果：{json.dumps(execution_result, ensure_ascii=False, indent=2)}
            
            請提供：
            1. 簡潔明瞭的結果說明
            2. 如果有資料，請用自然語言描述
            3. 如果有錯誤，請解釋問題並提供建議
            4. 保持專業但友善的語氣
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"查詢結果：{json.dumps(execution_result, ensure_ascii=False)}")
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                **state,
                "response": response.content
            }
        
        # 建立工作流程圖
        workflow = StateGraph(AgentState)
        
        # 添加節點
        workflow.add_node("reason", reason)
        workflow.add_node("action", action)
        workflow.add_node("observe", observe)
        
        # 設定流程
        workflow.set_entry_point("reason")
        workflow.add_edge("reason", "action")
        workflow.add_edge("action", "observe")
        workflow.add_edge("observe", END)
        
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
            "context": context
        }
        
        # 執行工作流程
        result = await self.workflow.ainvoke(initial_state)
        
        return {
            "response": result["response"],
            "sql_generated": result["sql_query"],
            "data": result["execution_result"],
            "reasoning": result["reasoning"]
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