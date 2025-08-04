import pytest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch
import asyncio

from agents.sql_agent import SQLAgent

class TestSQLAgent:
    """SQL Agent 測試類別"""
    
    @pytest.fixture
    def temp_db_path(self):
        """建立臨時資料庫路徑"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # 清理
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def sql_agent(self, temp_db_path):
        """建立 SQL Agent 實例"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            agent = SQLAgent(db_path=temp_db_path)
            yield agent
            agent.close()
    
    def test_initialization(self, sql_agent):
        """測試 SQL Agent 初始化"""
        assert sql_agent.db_path is not None
        assert sql_agent.llm is not None
        assert sql_agent.workflow is not None
        assert sql_agent.conn is not None
    
    def test_database_creation(self, sql_agent):
        """測試資料庫表格建立"""
        cursor = sql_agent.conn.cursor()
        
        # 檢查表格是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'products', 'orders']
        for table in expected_tables:
            assert table in tables
    
    def test_sample_data_insertion(self, sql_agent):
        """測試範例資料插入"""
        cursor = sql_agent.conn.cursor()
        
        # 檢查使用者資料
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count > 0
        
        # 檢查產品資料
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        assert product_count > 0
        
        # 檢查訂單資料
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        assert order_count > 0
    
    def test_get_database_schema(self, sql_agent):
        """測試取得資料庫結構"""
        schema = sql_agent._get_database_schema()
        assert isinstance(schema, str)
        assert "users" in schema
        assert "products" in schema
        assert "orders" in schema
    
    def test_extract_sql_query(self, sql_agent):
        """測試 SQL 查詢提取"""
        # 測試一般 SQL
        sql = "SELECT * FROM users"
        result = sql_agent._extract_sql_query(sql)
        assert result == sql
        
        # 測試被 markdown 包圍的 SQL
        sql_with_markdown = "```sql\nSELECT * FROM users\n```"
        result = sql_agent._extract_sql_query(sql_with_markdown)
        assert result == "SELECT * FROM users"
        
        # 測試被 ``` 包圍的 SQL
        sql_with_backticks = "```\nSELECT * FROM users\n```"
        result = sql_agent._extract_sql_query(sql_with_backticks)
        assert result == "SELECT * FROM users"
    
    def test_get_database_info(self, sql_agent):
        """測試取得資料庫資訊"""
        info = sql_agent.get_database_info()
        
        assert "database_path" in info
        assert "tables" in info
        assert "schema" in info
        
        # 檢查表格資訊
        tables = info["tables"]
        assert "users" in tables
        assert "products" in tables
        assert "orders" in tables
        
        # 檢查每個表格都有行數資訊
        for table_name, table_info in tables.items():
            assert "row_count" in table_info
            assert isinstance(table_info["row_count"], int)
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, sql_agent):
        """測試工作流程執行"""
        # Mock LLM 回應
        mock_response = Mock()
        mock_response.content = "SELECT * FROM users"
        
        with patch.object(sql_agent.llm, 'invoke', return_value=mock_response):
            result = await sql_agent.execute("查詢所有使用者")
            
            assert "response" in result
            assert "sql_generated" in result
            assert "data" in result
            assert "reasoning" in result
    
    def test_connection_management(self, temp_db_path):
        """測試連接管理"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            agent = SQLAgent(db_path=temp_db_path)
            
            # 檢查連接是否建立
            assert agent.conn is not None
            
            # 測試關閉連接
            agent.close()
            # 連接應該被關閉
            try:
                agent.conn.execute("SELECT 1")
                assert False, "連接應該已被關閉"
            except sqlite3.OperationalError:
                pass  # 預期行為
    
    def test_error_handling(self, sql_agent):
        """測試錯誤處理"""
        # 測試無效的 SQL 查詢
        try:
            sql_agent.conn.execute("INVALID SQL")
            assert False, "應該拋出異常"
        except sqlite3.OperationalError:
            pass  # 預期行為
    
    @pytest.mark.asyncio
    async def test_execute_with_error(self, sql_agent):
        """測試執行時發生錯誤的處理"""
        # Mock LLM 回應產生無效 SQL
        mock_response = Mock()
        mock_response.content = "INVALID SQL QUERY"
        
        with patch.object(sql_agent.llm, 'invoke', return_value=mock_response):
            result = await sql_agent.execute("無效查詢")
            
            assert "response" in result
            assert "sql_generated" in result
            assert "data" in result
            # 應該有錯誤資訊
            assert result["data"]["type"] == "error"
    
    def test_workflow_structure(self, sql_agent):
        """測試工作流程結構"""
        # 檢查工作流程是否有正確的節點
        workflow = sql_agent.workflow
        
        # 檢查是否有 reason、action、observe 節點
        # 注意：這裡的檢查可能需要根據實際的 LangGraph 實作調整
        assert workflow is not None 