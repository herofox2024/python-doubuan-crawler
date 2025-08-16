from datetime import datetime
from database import DoubanBookDB
from typing import Dict, List

class HTMLExporter:
    def __init__(self):
        self.template = self._get_html_template()
    
    def _get_html_template(self) -> str:
        """HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_id} 的豆瓣书评收藏</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .header h1 {{
            color: #2E7D32;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px 25px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2E7D32;
            display: block;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .rating-filter {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .rating-btn {{
            display: inline-block;
            padding: 8px 16px;
            margin: 5px;
            background-color: #e8f5e8;
            border: 1px solid #4CAF50;
            border-radius: 20px;
            text-decoration: none;
            color: #2E7D32;
            transition: all 0.3s;
            cursor: pointer;
        }}
        
        .rating-btn:hover, .rating-btn.active {{
            background-color: #4CAF50;
            color: white;
        }}
        
        .search-box {{
            text-align: center;
            margin: 20px 0;
        }}
        
        .search-input {{
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            width: 300px;
            font-size: 14px;
        }}
        
        .book-list {{
            margin-top: 30px;
        }}
        
        .book-item {{
            display: flex;
            margin-bottom: 25px;
            padding: 20px;
            background-color: #fafafa;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
            transition: all 0.3s;
        }}
        
        .book-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .book-info {{
            flex: 1;
        }}
        
        .book-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2E7D32;
        }}
        
        .book-title a {{
            color: #2E7D32;
            text-decoration: none;
        }}
        
        .book-title a:hover {{
            text-decoration: underline;
        }}
        
        .book-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        
        .book-rating {{
            display: inline-block;
            padding: 4px 12px;
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 15px;
            color: #856404;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .rating-5星 {{ background-color: #d4edda; border-color: #c3e6cb; color: #155724; }}
        .rating-4星 {{ background-color: #cce7ff; border-color: #99d6ff; color: #004085; }}
        .rating-3星 {{ background-color: #fff3cd; border-color: #ffeaa7; color: #856404; }}
        .rating-2星 {{ background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }}
        .rating-1星 {{ background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }}
        
        .book-review {{
            margin-top: 15px;
            padding: 15px;
            background-color: white;
            border-radius: 6px;
            border-left: 3px solid #4CAF50;
            font-style: italic;
            line-height: 1.8;
        }}
        
        .review-label {{
            font-weight: bold;
            color: #2E7D32;
            margin-bottom: 8px;
            display: block;
        }}
        
        .no-review {{
            color: #999;
            font-size: 0.9em;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
        }}
        
        .hidden {{
            display: none;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .book-item {{
                flex-direction: column;
            }}
            
            .search-input {{
                width: 100%;
                max-width: 300px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 {user_id} 的豆瓣书评收藏</h1>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{total_books}</span>
                    <span class="stat-label">总书籍数</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{books_with_reviews}</span>
                    <span class="stat-label">有书评</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{export_date}</span>
                    <span class="stat-label">导出时间</span>
                </div>
            </div>
            
            {rating_stats_html}
            
            <div class="search-box">
                <input type="text" class="search-input" placeholder="搜索书名、作者或书评内容..." 
                       onkeyup="searchBooks(this.value)">
            </div>
            
            <div class="rating-filter">
                <span class="rating-btn active" onclick="filterByRating('all')">全部</span>
                <span class="rating-btn" onclick="filterByRating('has-review')">有书评</span>
                {rating_filter_buttons}
            </div>
        </div>
        
        <div class="book-list" id="bookList">
            {books_html}
        </div>
        
        <div class="footer">
            <p>📊 数据来源：豆瓣读书 | 生成时间：{export_date} | 工具：豆瓣书评爬虫</p>
        </div>
    </div>
    
    <script>
        function filterByRating(rating) {{
            const books = document.querySelectorAll('.book-item');
            const buttons = document.querySelectorAll('.rating-btn');
            
            // 更新按钮状态
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            books.forEach(book => {{
                const bookRating = book.dataset.rating;
                const hasReview = book.dataset.hasReview === 'true';
                
                if (rating === 'all') {{
                    book.style.display = 'flex';
                }} else if (rating === 'has-review') {{
                    book.style.display = hasReview ? 'flex' : 'none';
                }} else {{
                    book.style.display = bookRating === rating ? 'flex' : 'none';
                }}
            }});
        }}
        
        function searchBooks(query) {{
            const books = document.querySelectorAll('.book-item');
            const searchTerm = query.toLowerCase();
            
            books.forEach(book => {{
                const title = book.querySelector('.book-title').textContent.toLowerCase();
                const author = book.querySelector('.book-meta').textContent.toLowerCase();
                const review = book.querySelector('.book-review') ? 
                    book.querySelector('.book-review').textContent.toLowerCase() : '';
                
                const matches = title.includes(searchTerm) || 
                               author.includes(searchTerm) || 
                               review.includes(searchTerm);
                
                book.style.display = matches ? 'flex' : 'none';
            }});
        }}
    </script>
</body>
</html>
        """
    
    def _generate_rating_stats_html(self, rating_stats: Dict[str, int]) -> str:
        """生成评分统计HTML"""
        if not rating_stats:
            return ""
        
        stats_html = '<div class="stats" style="margin-top: 20px;">'
        for rating, count in sorted(rating_stats.items(), reverse=True):
            stats_html += f'''
                <div class="stat-item">
                    <span class="stat-number">{count}</span>
                    <span class="stat-label">{rating}</span>
                </div>
            '''
        stats_html += '</div>'
        return stats_html
    
    def _generate_rating_filter_buttons(self, rating_stats: Dict[str, int]) -> str:
        """生成评分筛选按钮"""
        if not rating_stats:
            return ""
        
        buttons_html = ""
        for rating in sorted(rating_stats.keys(), reverse=True):
            count = rating_stats[rating]
            buttons_html += f'<span class="rating-btn" onclick="filterByRating(\'{rating}\')">{rating} ({count})</span>'
        
        return buttons_html
    
    def _generate_book_html(self, book: Dict) -> str:
        """生成单本书的HTML"""
        title = book['title'] or '未知书名'
        author = book['author'] or '未知作者'
        publish_date = book['publish_date'] or '未知'
        douban_url = book['douban_url'] or '#'
        rating = book['rating'] or '未评分'
        review_content = book['review_content'] or ''
        review_date = book['review_date'] or '未知日期'
        
        # 安全的HTML转义
        title = self._escape_html(title)
        author = self._escape_html(author)
        review_content = self._escape_html(review_content)
        
        has_review = bool(review_content.strip())
        rating_class = f"rating-{rating}" if rating != '未评分' else "rating-unrated"
        
        review_html = ""
        if has_review:
            review_html = f'''
                <div class="book-review">
                    <span class="review-label">📝 我的书评：</span>
                    {review_content}
                </div>
            '''
        else:
            review_html = '<div class="no-review">📝 暂无书评</div>'
        
        return f'''
            <div class="book-item" data-rating="{rating}" data-has-review="{str(has_review).lower()}">
                <div class="book-info">
                    <div class="book-title">
                        <a href="{douban_url}" target="_blank">{title}</a>
                    </div>
                    <div class="book-meta">
                        👤 作者：{author} | 📅 出版：{publish_date} | 🕒 评分时间：{review_date}
                    </div>
                    <div>
                        <span class="book-rating {rating_class}">⭐ {rating}</span>
                    </div>
                    {review_html}
                </div>
            </div>
        '''
    
    def _escape_html(self, text: str) -> str:
        """HTML转义"""
        if not text:
            return ""
        
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#x27;"))
    
    def export_user_books(self, db: DoubanBookDB, user_id: str, output_file: str) -> bool:
        """导出用户书籍数据为HTML文件"""
        try:
            # 获取用户数据
            data = db.export_to_dict(user_id)
            
            if not data['books']:
                print(f"用户 {user_id} 没有书籍数据")
                return False
            
            # 生成各部分HTML
            rating_stats_html = self._generate_rating_stats_html(data['stats']['rating_stats'])
            rating_filter_buttons = self._generate_rating_filter_buttons(data['stats']['rating_stats'])
            
            books_html = ""
            for book in data['books']:
                books_html += self._generate_book_html(book)
            
            # 填充模板
            html_content = self.template.format(
                user_id=user_id,
                total_books=data['stats']['total_books'],
                books_with_reviews=data['stats']['books_with_reviews'],
                export_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                rating_stats_html=rating_stats_html,
                rating_filter_buttons=rating_filter_buttons,
                books_html=books_html
            )
            
            # 写入文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML文件已导出到: {output_file}")
            return True
            
        except Exception as e:
            print(f"HTML导出失败: {e}")
            return False
    
    def export_books_by_rating(self, db: DoubanBookDB, user_id: str, rating: str, output_file: str) -> bool:
        """按评分导出书籍"""
        try:
            books = db.get_books_by_rating(user_id, rating)
            
            if not books:
                print(f"用户 {user_id} 没有 {rating} 的书籍")
                return False
            
            # 转换为字典格式
            book_dicts = []
            for book in books:
                book_dicts.append({
                    'title': book[0],
                    'author': book[1],
                    'publish_date': book[2],
                    'douban_url': book[3],
                    'rating': book[4],
                    'review_content': book[5],
                    'review_date': book[6],
                    'created_at': book[7]
                })
            
            # 生成HTML
            books_html = ""
            for book in book_dicts:
                books_html += self._generate_book_html(book)
            
            # 简化的模板用于单评分导出
            html_content = self.template.format(
                user_id=f"{user_id} - {rating}",
                total_books=len(book_dicts),
                books_with_reviews=len([b for b in book_dicts if b['review_content'].strip()]),
                export_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                rating_stats_html="",
                rating_filter_buttons="",
                books_html=books_html
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"{rating} 书籍HTML文件已导出到: {output_file}")
            return True
            
        except Exception as e:
            print(f"按评分导出HTML失败: {e}")
            return False