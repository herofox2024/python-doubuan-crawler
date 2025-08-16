import requests
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Tuple
from database import DoubanBookDB

class DoubanCrawler:
    def __init__(self, db: DoubanBookDB, gui_callback=None):
        self.db = db
        self.gui_callback = gui_callback
        self.is_running = True
        
    def log(self, message):
        """日志输出"""
        print(message)
        if self.gui_callback:
            self.gui_callback.log(message)
    
    def update_status(self, status):
        """更新状态"""
        if self.gui_callback:
            self.gui_callback.update_status(status)
    
    def update_progress(self, value):
        """更新进度"""
        if self.gui_callback:
            self.gui_callback.update_progress(value)
    
    def check_stop_signal(self):
        """检查是否需要停止"""
        if self.gui_callback:
            return not self.gui_callback.is_crawling
        return not self.is_running
    
    def get_book_details(self, book_url, headers):
        """获取书籍详细信息：作者和出版年月"""
        try:
            time.sleep(1)
            response = requests.get(book_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 获取作者信息
            author = "未知作者"
            info_elem = soup.select_one('#info')
            if info_elem:
                info_text = info_elem.get_text(separator=' ', strip=True)
                author_element = info_elem.select_one('a[href*="/author/"]')
                if author_element:
                    author = author_element.text.strip()
                else:
                    author_match = re.search(r'作者[:：]?\s*([^/\n]+)', info_text)
                    if author_match:
                        author = author_match.group(1).strip()
            
            # 获取出版年月
            publish_date = "未知"
            if info_elem:
                info_text = info_elem.text
                date_match = re.search(r'出版年:?\s*(\d{4}[-年]\d{1,2}[月]?)', info_text)
                if date_match:
                    publish_date = date_match.group(1)
            
            return author, publish_date
        except Exception as e:
            self.log(f"获取书籍详情失败 {book_url}: {e}")
            return "获取失败", "获取失败"
    
    def extract_rating_from_class(self, item):
        """从豆瓣页面的CSS class中提取评分"""
        rating_span = item.select_one('span[class*="rating"]')
        if rating_span:
            class_names = rating_span.get('class', [])
            for class_name in class_names:
                match = re.search(r'rating(\d+)', class_name)
                if match:
                    rating_num = int(match.group(1))
                    return f"{rating_num}星"
        return None
    
    def extract_review_content(self, item):
        """提取书评内容"""
        comment_elem = item.select_one('p.comment.comment-item')
        if comment_elem:
            return comment_elem.get_text().strip()
        
        comment_elem = item.select_one('p.comment')
        if comment_elem:
            return comment_elem.get_text().strip()
        
        return None
    
    def extract_book_info_from_page(self, item) -> Tuple[str, str]:
        """从页面元素中提取书籍信息"""
        author = "未知作者"
        publish_date = "未知"
        
        pub_elem = item.select_one('.pub')
        if pub_elem:
            pub_text = pub_elem.get_text().strip()
            parts = pub_text.split(' / ')
            
            if len(parts) >= 1:
                author = parts[0].strip()
            
            for part in parts:
                part = part.strip()
                if any(pattern in part for pattern in ['20', '19']) and any(char in part for char in ['-', '/', '年']):
                    if re.search(r'\b(19|20)\d{2}[-年/]\d{1,2}[月]?', part) or re.search(r'\b(19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}', part):
                        publish_date = part
                        break
                    elif re.search(r'\b(19|20)\d{2}', part) and len(part) <= 10:
                        publish_date = part
                        break
        
        return author, publish_date
    
    def crawl_user_books(self, user_id: str, cookie: str, max_pages: int = None):
        """爬取用户书籍数据并存储到数据库"""
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        start_time = datetime.now()
        page = 0
        total_books = 0
        total_reviews = 0
        failed_pages = []
        max_retries = 3
        base_delay = 2
        max_delay = 10
        
        self.log(f"开始爬取用户 {user_id} 的豆瓣书籍数据...")
        self.update_status("正在爬取数据...")
        
        # 清空该用户的旧数据
        self.db.clear_user_books(user_id)
        self.log("已清空旧数据")
        
        while not self.check_stop_signal():
            if max_pages and page >= max_pages:
                self.log(f"已达到设置的最大页数限制 ({max_pages})，停止爬取")
                break
            
            url = f'https://book.douban.com/people/{user_id}/collect?start={page*15}'
            success = False
            
            for attempt in range(max_retries):
                if self.check_stop_signal():
                    break
                
                try:
                    self.log(f"正在请求第{page+1}页 (尝试 {attempt+1}/{max_retries})")
                    self.update_status(f"正在爬取第{page+1}页...")
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    time.sleep(delay)
                    
                    temp_headers = headers.copy()
                    temp_headers.pop('Accept-Encoding', None)
                    res = requests.get(url, headers=temp_headers, timeout=30)
                    
                    if 'sec.douban.com' in res.url or '禁止访问' in res.text or res.status_code == 403:
                        self.log("遇到反爬虫验证，Cookie可能已过期")
                        self.update_status("遇到反爬虫验证")
                        return
                    
                    res.raise_for_status()
                    success = True
                    break
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"第{page+1}页请求失败 (尝试 {attempt+1}): {e}")
                    if attempt < max_retries - 1:
                        error_delay = min(base_delay * (3 ** attempt), max_delay)
                        time.sleep(error_delay)
                    else:
                        failed_pages.append(page)
                        self.log(f"第{page+1}页重试{max_retries}次后仍然失败，跳过此页")
            
            if not success:
                page += 1
                if page > (max_pages * 2 if max_pages else 100):
                    self.log("达到最大重试页数，停止爬取")
                    break
                continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('li.subject-item')
            
            if not items:
                self.log(f"第{page+1}页没有找到书籍条目，已到达最后一页")
                break
            
            self.log(f"第{page+1}页找到 {len(items)} 本书籍")
            page_books_count = 0
            
            for i, item in enumerate(items, 1):
                if self.check_stop_signal():
                    break
                
                try:
                    # 获取书籍信息
                    title_element = item.select_one('h2 a')
                    if not title_element:
                        continue
                    
                    title = title_element.get('title', '').strip()
                    if not title:
                        title = title_element.get_text().strip()
                    
                    link = title_element.get('href', '').strip()
                    
                    # 从当前页面提取作者和出版信息
                    author, publish_date = self.extract_book_info_from_page(item)
                    
                    # 提取评分
                    rating = self.extract_rating_from_class(item)
                    if rating is None:
                        rating_tag = item.select_one('.rating_nums')
                        if rating_tag:
                            try:
                                rating = f"{rating_tag.text.strip()}分"
                            except ValueError:
                                rating = "未评分"
                        else:
                            rating = "未评分"
                    
                    # 提取书评内容
                    review = self.extract_review_content(item)
                    
                    # 获取评分日期
                    date_elem = item.select_one('.date')
                    date = date_elem.get_text().strip() if date_elem else '未知日期'
                    
                    # 存储到数据库
                    success = self.db.add_book(
                        title=title,
                        author=author,
                        publish_date=publish_date,
                        douban_url=link,
                        rating=rating,
                        review_content=review or '',
                        review_date=date,
                        user_id=user_id
                    )
                    
                    if success:
                        page_books_count += 1
                        total_books += 1
                        
                        if review and review.strip():
                            total_reviews += 1
                        
                        self.log(f"  已保存: 《{title}》- {rating}")
                    else:
                        self.log(f"  保存失败: 《{title}》")
                    
                except Exception as e:
                    self.log(f"处理第{i}本书时出错: {e}")
                    continue
            
            self.log(f"第{page+1}页处理完成，本页保存{page_books_count}本书籍")
            
            # 更新进度（这里是估算，如果有最大页数的话）
            if max_pages:
                progress = min(100, (page + 1) * 100 / max_pages)
                self.update_progress(progress)
            
            page += 1
        
        # 完成爬取
        end_time = datetime.now()
        
        # 更新用户信息
        self.db.update_user_info(user_id)
        
        # 记录爬取日志
        status = "success" if not self.check_stop_signal() else "stopped"
        self.db.log_crawl_session(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            pages_crawled=page,
            books_found=total_books,
            reviews_found=total_reviews,
            status=status
        )
        
        self.log(f"爬取完成！")
        self.log(f"总共处理了{page}页")
        self.log(f"找到{total_books}本书籍")
        self.log(f"其中{total_reviews}本有书评")
        self.log(f"失败的页面: {failed_pages}")
        
        if self.check_stop_signal():
            self.update_status("爬取已停止")
        else:
            self.update_status("爬取完成")
            self.update_progress(100)

# 兼容原有代码的函数
def export_douban_books_with_reviews(user_id: str, max_pages: int = None, cookie: str = None):
    """为了兼容原有代码提供的函数"""
    if not cookie:
        import os
        cookie = os.getenv('DOUBAN_COOKIE', '')
        if not cookie:
            print("❌ 错误：未配置Cookie")
            return
    
    db = DoubanBookDB()
    crawler = DoubanCrawler(db)
    crawler.crawl_user_books(user_id, cookie, max_pages)