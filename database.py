import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple
import json

class DoubanBookDB:
    def __init__(self, db_path: str = "douban_books.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库，创建表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建书籍表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                publish_date TEXT,
                douban_url TEXT UNIQUE,
                rating TEXT,
                review_content TEXT,
                review_date TEXT,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                user_name TEXT,
                last_crawl_time TIMESTAMP,
                total_books INTEGER DEFAULT 0,
                books_with_reviews INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建爬取记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                pages_crawled INTEGER,
                books_found INTEGER,
                reviews_found INTEGER,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_book(self, title: str, author: str, publish_date: str, douban_url: str, 
                 rating: str, review_content: str, review_date: str, user_id: str) -> bool:
        """添加或更新书籍记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 使用 INSERT OR REPLACE 来处理重复的 URL
            cursor.execute('''
                INSERT OR REPLACE INTO books 
                (title, author, publish_date, douban_url, rating, review_content, 
                 review_date, user_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (title, author, publish_date, douban_url, rating, review_content, review_date, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加书籍失败: {e}")
            return False
    
    def get_books_by_user(self, user_id: str, has_review: Optional[bool] = None) -> List[Tuple]:
        """获取用户的书籍列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if has_review is None:
            cursor.execute('''
                SELECT title, author, publish_date, douban_url, rating, 
                       review_content, review_date, created_at
                FROM books WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        elif has_review:
            cursor.execute('''
                SELECT title, author, publish_date, douban_url, rating, 
                       review_content, review_date, created_at
                FROM books 
                WHERE user_id = ? AND review_content IS NOT NULL AND review_content != ''
                ORDER BY created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT title, author, publish_date, douban_url, rating, 
                       review_content, review_date, created_at
                FROM books 
                WHERE user_id = ? AND (review_content IS NULL OR review_content = '')
                ORDER BY created_at DESC
            ''', (user_id,))
        
        books = cursor.fetchall()
        conn.close()
        return books
    
    def get_books_by_rating(self, user_id: str, rating: str) -> List[Tuple]:
        """根据评分获取书籍列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, author, publish_date, douban_url, rating, 
                   review_content, review_date, created_at
            FROM books 
            WHERE user_id = ? AND rating = ?
            ORDER BY created_at DESC
        ''', (user_id, rating))
        
        books = cursor.fetchall()
        conn.close()
        return books
    
    def get_user_stats(self, user_id: str) -> dict:
        """获取用户统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总书籍数
        cursor.execute('SELECT COUNT(*) FROM books WHERE user_id = ?', (user_id,))
        total_books = cursor.fetchone()[0]
        
        # 有书评的书籍数
        cursor.execute('''
            SELECT COUNT(*) FROM books 
            WHERE user_id = ? AND review_content IS NOT NULL AND review_content != ''
        ''', (user_id,))
        books_with_reviews = cursor.fetchone()[0]
        
        # 各评分统计
        cursor.execute('''
            SELECT rating, COUNT(*) 
            FROM books 
            WHERE user_id = ? AND rating IS NOT NULL 
            GROUP BY rating
            ORDER BY rating DESC
        ''', (user_id,))
        rating_stats = dict(cursor.fetchall())
        
        # 最近爬取时间
        cursor.execute('''
            SELECT MAX(created_at) FROM books WHERE user_id = ?
        ''', (user_id,))
        last_crawl = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_books': total_books,
            'books_with_reviews': books_with_reviews,
            'rating_stats': rating_stats,
            'last_crawl': last_crawl
        }
    
    def update_user_info(self, user_id: str, user_name: str = None):
        """更新用户信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, user_name, last_crawl_time)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, user_name))
        
        conn.commit()
        conn.close()
    
    def log_crawl_session(self, user_id: str, start_time: datetime, end_time: datetime,
                         pages_crawled: int, books_found: int, reviews_found: int,
                         status: str = "success", error_message: str = None):
        """记录爬取会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crawl_logs 
            (user_id, start_time, end_time, pages_crawled, books_found, 
             reviews_found, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, start_time, end_time, pages_crawled, books_found, 
              reviews_found, status, error_message))
        
        conn.commit()
        conn.close()
    
    def clear_user_books(self, user_id: str):
        """清空用户的书籍数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM books WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def export_to_dict(self, user_id: str) -> dict:
        """导出用户数据为字典格式，用于HTML生成"""
        books = self.get_books_by_user(user_id)
        stats = self.get_user_stats(user_id)
        
        return {
            'user_id': user_id,
            'stats': stats,
            'books': [
                {
                    'title': book[0],
                    'author': book[1],
                    'publish_date': book[2],
                    'douban_url': book[3],
                    'rating': book[4],
                    'review_content': book[5],
                    'review_date': book[6],
                    'created_at': book[7]
                }
                for book in books
            ]
        }