import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from datetime import datetime
from database import DoubanBookDB
from html_exporter import HTMLExporter

class DoubanBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("豆瓣书评爬虫工具")
        self.root.geometry("800x600")
        
        # 初始化数据库
        self.db = DoubanBookDB()
        self.html_exporter = HTMLExporter()
        
        # 爬虫状态
        self.is_crawling = False
        self.crawl_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置根窗口的网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="豆瓣书评爬虫工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 用户输入区域
        ttk.Label(main_frame, text="豆瓣用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_id_var = tk.StringVar()
        self.user_id_entry = ttk.Entry(main_frame, textvariable=self.user_id_var, width=30)
        self.user_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Cookie配置区域
        ttk.Label(main_frame, text="Cookie:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cookie_var = tk.StringVar()
        self.cookie_entry = ttk.Entry(main_frame, textvariable=self.cookie_var, width=30, show="*")
        self.cookie_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        cookie_help_btn = ttk.Button(main_frame, text="?", width=3, 
                                   command=self.show_cookie_help)
        cookie_help_btn.grid(row=2, column=2, pady=5, padx=(5, 0))
        
        # 爬取页数限制
        ttk.Label(main_frame, text="最大页数:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.max_pages_var = tk.StringVar(value="")
        max_pages_entry = ttk.Entry(main_frame, textvariable=self.max_pages_var, width=30)
        max_pages_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(留空表示爬取所有页面)").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self.crawl_btn = ttk.Button(button_frame, text="开始爬取", command=self.start_crawl)
        self.crawl_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.stop_btn = ttk.Button(button_frame, text="停止爬取", command=self.stop_crawl, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.export_btn = ttk.Button(button_frame, text="导出HTML", command=self.export_html)
        self.export_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度信息", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 文本框与滚动条
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 设置网格权重
        main_frame.rowconfigure(6, weight=1)
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_frame, text="用户统计", padding="10")
        stats_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_var = tk.StringVar(value="请输入用户名并开始爬取")
        self.stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, 
                                   font=("Arial", 10))
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # 加载保存的配置
        self.load_config()
    
    def show_cookie_help(self):
        """显示Cookie获取帮助"""
        help_text = """如何获取豆瓣Cookie：

1. 在浏览器中登录豆瓣网站
2. 访问你的豆瓣收藏页面
3. 按F12打开开发者工具
4. 切换到Network（网络）标签页
5. 刷新页面
6. 找到页面请求，点击查看请求头
7. 复制Cookie字段的完整值
8. 粘贴到上面的Cookie输入框中

注意：Cookie包含登录信息，请妥善保管！"""
        
        messagebox.showinfo("Cookie获取帮助", help_text)
    
    def load_config(self):
        """加载保存的配置"""
        try:
            if os.path.exists('gui_config.txt'):
                with open('gui_config.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        self.user_id_var.set(lines[0].strip())
                        self.cookie_var.set(lines[1].strip())
        except Exception as e:
            self.log(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            with open('gui_config.txt', 'w', encoding='utf-8') as f:
                f.write(f"{self.user_id_var.get()}\n")
                f.write(f"{self.cookie_var.get()}\n")
        except Exception as e:
            self.log(f"保存配置失败: {e}")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # 在主线程中更新UI
        self.root.after(0, self._update_log, log_message)
    
    def _update_log(self, message):
        """在主线程中更新日志"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def update_status(self, status):
        """更新状态"""
        self.root.after(0, lambda: self.status_var.set(status))
    
    def update_progress(self, value):
        """更新进度条"""
        self.root.after(0, lambda: self.progress_var.set(value))
    
    def update_stats(self, user_id):
        """更新用户统计信息"""
        try:
            stats = self.db.get_user_stats(user_id)
            stats_text = f"总书籍: {stats['total_books']} | 有书评: {stats['books_with_reviews']} | "
            
            if stats['rating_stats']:
                rating_info = " | ".join([f"{rating}: {count}本" for rating, count in stats['rating_stats'].items()])
                stats_text += rating_info
            
            if stats['last_crawl']:
                stats_text += f" | 最后更新: {stats['last_crawl'][:16]}"
            
            self.root.after(0, lambda: self.stats_var.set(stats_text))
        except Exception as e:
            self.log(f"更新统计信息失败: {e}")
    
    def start_crawl(self):
        """开始爬取"""
        user_id = self.user_id_var.get().strip()
        cookie = self.cookie_var.get().strip()
        
        if not user_id:
            messagebox.showerror("错误", "请输入豆瓣用户名！")
            return
        
        if not cookie:
            messagebox.showerror("错误", "请输入Cookie！")
            return
        
        # 保存配置
        self.save_config()
        
        # 获取最大页数
        max_pages = None
        if self.max_pages_var.get().strip():
            try:
                max_pages = int(self.max_pages_var.get().strip())
            except ValueError:
                messagebox.showerror("错误", "最大页数必须是数字！")
                return
        
        # 更新UI状态
        self.is_crawling = True
        self.crawl_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.DISABLED)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 启动爬取线程
        self.crawl_thread = threading.Thread(
            target=self._crawl_worker, 
            args=(user_id, cookie, max_pages)
        )
        self.crawl_thread.start()
    
    def stop_crawl(self):
        """停止爬取"""
        self.is_crawling = False
        self.update_status("正在停止...")
        self.log("用户请求停止爬取")
    
    def _crawl_worker(self, user_id, cookie, max_pages):
        """爬取工作线程"""
        try:
            # 导入爬虫模块
            from crawler_with_db import DoubanCrawler
            
            crawler = DoubanCrawler(self.db, self)
            crawler.crawl_user_books(user_id, cookie, max_pages)
            
        except Exception as e:
            self.log(f"爬取过程出现错误: {e}")
            self.update_status("爬取失败")
        finally:
            # 恢复UI状态
            self.root.after(0, self._crawl_finished)
    
    def _crawl_finished(self):
        """爬取完成后的UI更新"""
        self.is_crawling = False
        self.crawl_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL)
        
        if self.user_id_var.get().strip():
            self.update_stats(self.user_id_var.get().strip())
    
    def export_html(self):
        """导出HTML文件"""
        user_id = self.user_id_var.get().strip()
        if not user_id:
            messagebox.showerror("错误", "请先输入用户名！")
            return
        
        # 检查是否有数据
        stats = self.db.get_user_stats(user_id)
        if stats['total_books'] == 0:
            messagebox.showwarning("警告", "没有找到该用户的书籍数据，请先爬取！")
            return
        
        # 选择保存位置
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
            initialfile=f"{user_id}_豆瓣书评.html"
        )
        
        if filename:
            try:
                self.update_status("正在导出HTML...")
                success = self.html_exporter.export_user_books(self.db, user_id, filename)
                
                if success:
                    self.update_status("HTML导出完成")
                    self.log(f"HTML文件已保存到: {filename}")
                    messagebox.showinfo("成功", f"HTML文件已导出到:\n{filename}")
                else:
                    self.update_status("HTML导出失败")
                    messagebox.showerror("错误", "HTML导出失败，请查看日志信息")
            except Exception as e:
                self.update_status("HTML导出失败")
                self.log(f"HTML导出失败: {e}")
                messagebox.showerror("错误", f"HTML导出失败: {e}")

def main():
    root = tk.Tk()
    app = DoubanBookGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()