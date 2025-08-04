import os
import sqlite3
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import threading

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnablePassthrough

from mcp.database_client import DatabaseMCPClient

class SQLAgent:
    """
    SQL Agent - 具有 reason、action、observe 功能的 AI Agent
    
    使用 LangChain 和 LangGraph 開發，能夠：
    - reason: 分析自然語言查詢意圖
    - action: 生成並執行 SQL 查詢
    - observe: 觀察結果並格式化回應
    """
    
    def __init__(self, db_path: str = "data/ai_agent.db"):
        """初始化 SQL Agent"""
        self.db_path = db_path
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 初始化 MCP Client
        self.mcp_client = DatabaseMCPClient()
        self.mcp_connected = False
        
        # 初始化資料庫
        self._init_database()
        
        # 建立 LangGraph 工作流程
        self.workflow = self._create_workflow()
    
    def _init_database(self):
        """初始化 SQLite 資料庫"""
        # 確保 data 目錄存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # 建立表格和範例資料
        self._create_tables()
        self._insert_sample_data()
    
    def _get_connection(self):
        """取得新的資料庫連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """建立資料庫表格"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 使用者表格
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 產品表格
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 訂單表格
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _insert_sample_data(self):
        """插入範例資料"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 檢查是否已有資料
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # 插入使用者資料
            users_data = [
                ("張小明", "zhang@example.com", 25),
                ("李小華", "li@example.com", 30),
                ("王小美", "wang@example.com", 28),
                ("陳小強", "chen@example.com", 35)
            ]
            cursor.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                users_data
            )
            
            # 插入產品資料
            products_data = [
                ("iPhone 15", 29999.0, "手機", 50),
                ("MacBook Pro", 59999.0, "筆電", 20),
                ("AirPods Pro", 6999.0, "耳機", 100),
                ("iPad Air", 19999.0, "平板", 30),
                ("Apple Watch", 12999.0, "手錶", 40)
            ]
            cursor.executemany(
                "INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
                products_data
            )
            
            # 插入訂單資料
            orders_data = [
                (1, 1, 2, 59998.0),
                (2, 3, 1, 6999.0),
                (3, 2, 1, 59999.0),
                (1, 4, 1, 19999.0),
                (4, 5, 1, 12999.0)
            ]
            cursor.executemany(
                "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                orders_data
            )
            
            conn.commit()
        
        conn.close()
    
    def _get_database_schema(self) -> str:
        """取得資料庫結構資訊"""
        conn = self._get_connection()
        cursor = conn.cursor()
        schema_info = []
        
        # 取得所有表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_info.append(f"表格: {table_name}")
            for col in columns:
                schema_info.append(f"  - {col[1]} ({col[2]})")
            schema_info.append("")
        
        conn.close()
        return "\n".join(schema_info)
    
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
        def reason(state: AgentState) -> AgentState:
            """分析使用者查詢意圖"""
            query = state["query"]
            schema = self._get_database_schema()
            
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
            schema = self._get_database_schema()
            
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
    
    def get_database_info(self) -> Dict[str, Any]:
        """取得資料庫資訊"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 取得表格資訊
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_info[table_name] = {"row_count": count}
        
        conn.close()
        
        return {
            "database_path": self.db_path,
            "tables": table_info,
            "schema": self._get_database_schema()
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