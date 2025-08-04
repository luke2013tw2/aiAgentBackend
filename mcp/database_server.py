#!/usr/bin/env python3
"""
簡化版 MCP Database Server

提供資料庫操作功能的 MCP Server，支援：
- 查詢資料庫結構
- 執行 SQL 查詢
- 插入、更新、刪除資料
"""

import asyncio
import json
import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class DatabaseMCPServer:
    """簡化版 MCP Database Server 實現"""
    
    def __init__(self, db_path: str = "data/ai_agent.db"):
        self.db_path = db_path
        
        # 初始化資料庫
        self._init_database()
    
    def _init_database(self):
        """初始化資料庫"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_tables()
        self._insert_sample_data()
    
    def _get_connection(self):
        """取得資料庫連接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """建立資料表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 使用者表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 產品表
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
        
        # 訂單表
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
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # 插入使用者資料
        users = [
            ("張三", "zhang@example.com", 25),
            ("李四", "li@example.com", 30),
            ("王五", "wang@example.com", 28),
            ("趙六", "zhao@example.com", 35),
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            users
        )
        
        # 插入產品資料
        products = [
            ("筆記型電腦", 29999.0, "電子產品", 10),
            ("智慧型手機", 15999.0, "電子產品", 20),
            ("咖啡機", 3999.0, "家電", 5),
            ("書桌", 2999.0, "家具", 8),
            ("運動鞋", 1999.0, "服飾", 15),
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)",
            products
        )
        
        # 插入訂單資料
        orders = [
            (1, 1, 1, 29999.0),
            (2, 2, 2, 31998.0),
            (3, 3, 1, 3999.0),
            (1, 4, 1, 2999.0),
            (2, 5, 2, 3998.0),
        ]
        cursor.executemany(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
            orders
        )
        
        conn.commit()
        conn.close()
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        return [
            {
                "name": "get_database_schema",
                "description": "取得資料庫結構資訊"
            },
            {
                "name": "execute_query",
                "description": "執行 SQL 查詢"
            },
            {
                "name": "get_table_info",
                "description": "取得指定表格的資訊"
            },
            {
                "name": "get_sample_data",
                "description": "取得表格的範例資料"
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = {}) -> Dict[str, Any]:
        """調用工具"""
        try:
            if name == "get_database_schema":
                return self._get_database_schema()
            elif name == "execute_query":
                return self._execute_query(arguments["sql"])
            elif name == "get_table_info":
                return self._get_table_info(arguments["table_name"])
            elif name == "get_sample_data":
                limit = arguments.get("limit", 5)
                return self._get_sample_data(arguments["table_name"], limit)
            else:
                raise ValueError(f"未知工具: {name}")
        except Exception as e:
            return {"error": str(e)}
    
    def _get_database_schema(self) -> Dict[str, Any]:
        """取得資料庫結構"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 取得所有表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "primary_key": bool(row[5])
                })
            
            # 取得記錄數
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            schema[table] = {
                "columns": columns,
                "row_count": count
            }
        
        conn.close()
        return {
            "database": self.db_path,
            "tables": schema,
            "total_tables": len(tables)
        }
    
    def _execute_query(self, sql: str) -> Dict[str, Any]:
        """執行 SQL 查詢"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            
            # 判斷查詢類型
            if sql.strip().upper().startswith("SELECT"):
                # SELECT 查詢
                columns = [description[0] for description in cursor.description]
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(row))
                
                result = {
                    "type": "select",
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }
            else:
                # INSERT, UPDATE, DELETE 查詢
                conn.commit()
                result = {
                    "type": "dml",
                    "affected_rows": cursor.rowcount,
                    "message": "查詢執行成功"
                }
            
            conn.close()
            return result
            
        except Exception as e:
            conn.close()
            raise Exception(f"SQL 執行錯誤: {str(e)}")
    
    def _get_table_info(self, table_name: str) -> Dict[str, Any]:
        """取得表格資訊"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 檢查表格是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                raise ValueError(f"表格 '{table_name}' 不存在")
            
            # 取得表格結構
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "primary_key": bool(row[5])
                })
            
            # 取得記錄數
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            conn.close()
            return {
                "table_name": table_name,
                "columns": columns,
                "row_count": count
            }
            
        except Exception as e:
            conn.close()
            raise Exception(f"取得表格資訊錯誤: {str(e)}")
    
    def _get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """取得表格範例資料"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 檢查表格是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                raise ValueError(f"表格 '{table_name}' 不存在")
            
            # 取得範例資料
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            columns = [description[0] for description in cursor.description]
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(row))
            
            conn.close()
            return {
                "table_name": table_name,
                "columns": columns,
                "rows": rows,
                "limit": limit,
                "actual_count": len(rows)
            }
            
        except Exception as e:
            conn.close()
            raise Exception(f"取得範例資料錯誤: {str(e)}")
    
    async def run(self):
        """運行 MCP Server（簡化版）"""
        print("🚀 MCP Database Server 已啟動")
        print("📍 可用工具:")
        tools = self.list_tools()
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 保持運行狀態
        while True:
            await asyncio.sleep(1)

async def main():
    """主函數"""
    server = DatabaseMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 