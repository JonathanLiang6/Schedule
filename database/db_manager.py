import sqlite3
import os

class DBManager:
    """
    数据库管理器，负责处理数据库连接和基本操作
    """
    
    def __init__(self, db_path='schedule.db'):
        """
        初始化数据库管理器
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """
        连接数据库
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        # 启用外键约束
        self.cursor.execute('PRAGMA foreign_keys = ON')
        return self.conn
    
    def disconnect(self):
        """
        断开数据库连接
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def execute(self, query, params=None):
        """
        执行SQL查询
        """
        if not self.conn:
            self.connect()
        
        if params:
            return self.cursor.execute(query, params)
        else:
            return self.cursor.execute(query)
    
    def commit(self):
        """
        提交事务
        """
        if self.conn:
            self.conn.commit()
    
    def fetch_all(self, query, params=None):
        """
        执行查询并返回所有结果
        """
        self.execute(query, params)
        return self.cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """
        执行查询并返回第一个结果
        """
        self.execute(query, params)
        return self.cursor.fetchone()
    
    def get_last_insert_id(self):
        """
        获取最后插入的ID
        """
        return self.cursor.lastrowid
    
    def __enter__(self):
        """
        进入上下文管理器
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文管理器
        """
        if exc_type is None:
            self.commit()
        self.disconnect()

# 全局数据库管理器实例
db_manager = DBManager()

# 测试函数
def test_db_connection():
    """
    测试数据库连接
    """
    from .init_db import init_database
    
    # 初始化数据库
    init_database()
    
    # 测试连接
    with DBManager() as db:
        # 测试查询
        result = db.fetch_all('SELECT name FROM sqlite_master WHERE type=\"table\"')
        print("数据库表:")
        for row in result:
            print(f"- {row[0]}")
        print("数据库连接测试成功！")

if __name__ == "__main__":
    test_db_connection()