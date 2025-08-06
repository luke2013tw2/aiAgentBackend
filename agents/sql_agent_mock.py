import os
import sqlite3
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import threading

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnablePassthrough

from mcp.database_client import DatabaseMCPClient

class MockLLM:
    """模擬 LLM 類別，用於在沒有 API Key 時提供預設回應"""
    
    def __init__(self):
        self.mock_responses = {
            "reason": {
                "查詢所有使用者": "這是一個 SELECT 查詢，需要從 users 表格中取得所有使用者資料。查詢類型：SELECT，需要的表格：users，查詢條件：無，預期結果：所有使用者資訊。",
                "顯示所有產品": "這是一個 SELECT 查詢，需要從 products 表格中取得所有產品資料。查詢類型：SELECT，需要的表格：products，查詢條件：無，預期結果：所有產品資訊。",
                "查詢訂單": "這是一個 SELECT 查詢，需要從 orders 表格中取得訂單資料。查詢類型：SELECT，需要的表格：orders，查詢條件：無，預期結果：所有訂單資訊。",
                "default": "這是一個資料庫查詢請求。查詢類型：SELECT，需要的表格：根據查詢內容決定，查詢條件：根據查詢內容決定，預期結果：相關資料。"
            },
            "action": {
                "查詢所有使用者": "SELECT * FROM users",
                "顯示所有產品": "SELECT * FROM products", 
                "查詢訂單": "SELECT * FROM orders",
                "default": "SELECT * FROM users LIMIT 5"
            },
            "observe": {
                "default": "根據您的查詢，我已經執行了相應的 SQL 查詢並取得了結果。查詢執行成功，返回了相關的資料。"
            }
        }
    
    def invoke(self, messages):
        """模擬 LLM 回應"""
        # 取得最後一個使用者訊息
        user_message = None
        for msg in messages:
            if hasattr(msg, 'content'):
                user_message = msg.content
                break
        
        if not user_message:
            return type('MockResponse', (), {'content': '無法理解查詢內容'})()
        
        # 根據訊息內容選擇回應
        for key, response in self.mock_responses["reason"].items():
            if key in user_message:
                return type('MockResponse', (), {'content': response})()
        
        return type('MockResponse', (), {'content': self.mock_responses["reason"]["default"]})()

class SQLAgentMock:
    """
    SQL Agent 模擬版本 - 具有 reason、action、observe 功能的 AI Agent
    
    使用 LangChain 和 LangGraph 開發，能夠：
    - reason: 分析自然語言查詢意圖
    - action: 生成並執行 SQL 查詢
    - observe: 觀察結果並格式化回應
    """
    
    def __init__(self, db_path: str = "data/ai_agent.db"):
        """初始化 SQL Agent"""
        self.db_path = db_path
        self.llm = MockLLM()
        
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
            
            # 使用模擬 LLM 進行分析
            response = self.llm.invoke([HumanMessage(content=query)])
            reasoning = response.content
            
            return {
                **state,
                "reasoning": reasoning
            }
        
        # 2. ACTION: 生成並執行 SQL
        async def action(state: AgentState) -> AgentState:
            """生成並執行 SQL 查詢"""
            query = state["query"]
            
            # 根據查詢內容生成 SQL
            sql_query = self._generate_sql_from_query(query)
            
            # 執行 SQL 查詢
            try:
                execution_result = self._execute_sql_query(sql_query)
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
            execution_result = state["execution_result"]
            
            if isinstance(execution_result, dict) and execution_result.get("type") == "error":
                response = f"查詢執行時發生錯誤：{execution_result['error']}"
            else:
                # execution_result 是一個列表
                result_list = execution_result if isinstance(execution_result, list) else []
                response = f"查詢執行成功！共找到 {len(result_list)} 筆資料。"
                if len(result_list) > 0:
                    response += f"\n\n前 3 筆資料：\n{json.dumps(result_list[:3], ensure_ascii=False, indent=2)}"
            
            return {
                **state,
                "response": response
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
    
    def _generate_sql_from_query(self, query: str) -> str:
        """根據查詢內容生成 SQL"""
        query_lower = query.lower()
        
        if "使用者" in query or "用戶" in query or "user" in query_lower:
            return "SELECT * FROM users"
        elif "產品" in query or "商品" in query or "product" in query_lower:
            return "SELECT * FROM products"
        elif "訂單" in query or "order" in query_lower:
            return "SELECT * FROM orders"
        else:
            return "SELECT * FROM users LIMIT 5"
    
    def _execute_sql_query(self, sql_query: str) -> List[Dict]:
        """執行 SQL 查詢"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            
            # 轉換為字典格式
            result = []
            for row in rows:
                result.append(dict(row))
            
            return result
        finally:
            conn.close()
    
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
            "data": result["execution_result"] if isinstance(result["execution_result"], dict) else {"rows": result["execution_result"]},
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
        pass 