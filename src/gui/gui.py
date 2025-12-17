import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import base64
import json
from datetime import datetime
from src.database.database import DoubanBookDB
from src.exporter.html_exporter import HTMLExporter
from src.exporter.csv_exporter import CSVExporter
from src.utils.logger import logger

class DoubanBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("豆瓣书评爬虫工具")
        self.root.geometry("800x750")
        
        # 初始化数据库和导出器
        self.db = DoubanBookDB()
        self.html_exporter = HTMLExporter()
        self.csv_exporter = CSVExporter()
        
        # 爬虫状态
        self.is_crawling = False
        self.crawl_thread = None
        self._progress_thread = None
        self.export_running = False
        
        # 配置参数
        self._progress_update_interval = 0.05  # 进度条更新间隔（秒）
        
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
        main_frame.columnconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="豆瓣书评爬虫工具", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
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
        self.max_pages_entry = ttk.Entry(main_frame, textvariable=self.max_pages_var, width=10)
        self.max_pages_entry.grid(row=3, column=1, sticky=(tk.W), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="(留空表示爬取所有页面)").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 日期范围选择（年、月、日下拉框模式）
        ttk.Label(main_frame, text="爬取时间范围:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # 生成年份、月份、日期列表
        from datetime import datetime
        current_year = datetime.now().year
        years = [str(year) for year in range(2000, current_year + 2)]  # 包括当前年份和下一年
        months = [f"{month:02d}" for month in range(1, 13)]  # 01-12
        days = [f"{day:02d}" for day in range(1, 32)]  # 01-31
        
        # 开始日期
        ttk.Label(main_frame, text="开始日期:").grid(row=5, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 开始年份
        self.start_year_var = tk.StringVar(value="")
        self.start_year_entry = ttk.Combobox(main_frame, textvariable=self.start_year_var, values=years, width=7, state="readonly")
        self.start_year_entry.grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="年").grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(65, 0))
        
        # 开始月份
        self.start_month_var = tk.StringVar(value="")
        self.start_month_entry = ttk.Combobox(main_frame, textvariable=self.start_month_var, values=months, width=5, state="readonly")
        self.start_month_entry.grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(95, 0))
        ttk.Label(main_frame, text="月").grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(130, 0))
        
        # 开始日期
        self.start_day_var = tk.StringVar(value="")
        self.start_day_entry = ttk.Combobox(main_frame, textvariable=self.start_day_var, values=days, width=5, state="readonly")
        self.start_day_entry.grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(155, 0))
        ttk.Label(main_frame, text="日").grid(row=5, column=2, sticky=(tk.W), pady=5, padx=(190, 0))
        
        # 结束日期
        ttk.Label(main_frame, text="结束日期:").grid(row=6, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # 结束年份
        self.end_year_var = tk.StringVar(value="")
        self.end_year_entry = ttk.Combobox(main_frame, textvariable=self.end_year_var, values=years, width=7, state="readonly")
        self.end_year_entry.grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="年").grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(65, 0))
        
        # 结束月份
        self.end_month_var = tk.StringVar(value="")
        self.end_month_entry = ttk.Combobox(main_frame, textvariable=self.end_month_var, values=months, width=5, state="readonly")
        self.end_month_entry.grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(95, 0))
        ttk.Label(main_frame, text="月").grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(130, 0))
        
        # 结束日期
        self.end_day_var = tk.StringVar(value="")
        self.end_day_entry = ttk.Combobox(main_frame, textvariable=self.end_day_var, values=days, width=5, state="readonly")
        self.end_day_entry.grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(155, 0))
        ttk.Label(main_frame, text="日").grid(row=6, column=2, sticky=(tk.W), pady=5, padx=(190, 0))
        
        # 绑定选择事件，实现单选逻辑
        self.max_pages_var.trace_add("write", self._handle_option_change)
        # 绑定所有日期相关变量的变化事件
        self.start_year_var.trace_add("write", self._handle_option_change)
        self.start_month_var.trace_add("write", self._handle_option_change)
        self.start_day_var.trace_add("write", self._handle_option_change)
        self.end_year_var.trace_add("write", self._handle_option_change)
        self.end_month_var.trace_add("write", self._handle_option_change)
        self.end_day_var.trace_add("write", self._handle_option_change)
        
        # 调试选项
        debug_frame = ttk.Frame(main_frame)
        debug_frame.grid(row=7, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E))
        
        self.save_debug_pages_var = tk.BooleanVar(value=False)
        self.save_debug_pages_check = ttk.Checkbutton(
            debug_frame, 
            text="保存调试页面", 
            variable=self.save_debug_pages_var,
            onvalue=True, 
            offvalue=False
        )
        self.save_debug_pages_check.grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(debug_frame, text="(开启后会保存每页HTML内容到debug_page_*.html文件)").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=20, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)
        
        self.crawl_btn = ttk.Button(button_frame, text="开始爬取", command=self.start_crawl)
        self.crawl_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.stop_btn = ttk.Button(button_frame, text="停止爬取", command=self.stop_crawl, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.export_html_btn = ttk.Button(button_frame, text="导出HTML", command=self.export_html)
        self.export_html_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        self.export_csv_btn = ttk.Button(button_frame, text="导出CSV", command=self.export_csv)
        self.export_csv_btn.grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))
        
        # 进度显示区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度信息", padding="10")
        progress_frame.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
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
        log_frame.grid(row=10, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 文本框与滚动条
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 设置网格权重
        main_frame.rowconfigure(10, weight=1)
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(main_frame, text="用户统计", padding="10")
        stats_frame.grid(row=11, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_var = tk.StringVar(value="请输入用户名并开始爬取")
        self.stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, 
                                   font=("Arial", 10))
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # 加载保存的配置
        self.load_config()
    
    def export_csv(self):
        """导出CSV文件，带动态进度条"""
        user_id = self.user_id_var.get().strip()
        if not self._validate_export_data(user_id):
            return
        
        start_date, end_date = self._get_date_range()
        if start_date == "" and end_date == "" and (
            self.start_year_var.get().strip() or 
            self.start_month_var.get().strip() or 
            self.start_day_var.get().strip() or
            self.end_year_var.get().strip() or 
            self.end_month_var.get().strip() or 
            self.end_day_var.get().strip()
        ):
            return  # 日期验证失败，已显示错误信息
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialfile=f"{user_id}_豆瓣书评.csv"
        )
        
        if filename:
            self._export_with_progress("CSV", filename, user_id, start_date, end_date, self.csv_exporter)
    

    
    def _export_with_progress(self, export_type, filename, user_id, start_date, end_date, exporter):
        """通用导出方法，带进度条"""
        try:
            self.update_status(f"正在导出{export_type}...")
            
            # 启动动态进度条线程
            self._start_progress_thread()
            
            # 在独立线程中执行导出
            def export_worker():
                try:
                    success = exporter.export_user_books(
                        self.db, user_id, filename, start_date, end_date
                    )
                    
                    # 在主线程中更新UI
                    self.root.after(0, lambda: self._handle_export_result(success, filename, export_type))
                except Exception as e:
                    self.root.after(0, lambda: self._handle_export_error(e, export_type))
            
            export_thread = threading.Thread(target=export_worker, daemon=True)
            export_thread.start()
            
        except Exception as e:
            self.export_running = False
            self.update_progress(0)
            self.update_status(f"{export_type}导出失败")
            self.log(f"{export_type}导出失败: {e}")
            messagebox.showerror("错误", f"{export_type}导出失败: {e}")
    
    def _handle_export_result(self, success, filename, export_type):
        """处理导出结果"""
        # 导出完成，停止进度条
        self.export_running = False
        self.update_progress(100)
        
        if success:
            self.update_status(f"{export_type}导出完成")
            self.log(f"{export_type}文件已保存到: {filename}")
            messagebox.showinfo("成功", f"{export_type}文件已导出到:\n{filename}")
            self._reset_export_ui()
        else:
            self.update_status(f"{export_type}导出失败")
            messagebox.showerror("错误", f"{export_type}导出失败，请查看日志信息")
    
    def _handle_export_error(self, error, export_type):
        """处理导出错误"""
        self.export_running = False
        self.update_progress(0)
        self.update_status(f"{export_type}导出失败")
        self.log(f"{export_type}导出失败: {error}")
        messagebox.showerror("错误", f"{export_type}导出失败: {error}")
    
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
    
    def _validate_date(self, year, month, day):
        """验证日期有效性"""
        if not year or not month or not day:
            return True  # 空日期是有效的
        
        try:
            datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _get_date_range(self):
        """获取日期范围字符串"""
        start_parts = [
            self.start_year_var.get().strip(),
            self.start_month_var.get().strip(),
            self.start_day_var.get().strip()
        ]
        end_parts = [
            self.end_year_var.get().strip(),
            self.end_month_var.get().strip(),
            self.end_day_var.get().strip()
        ]
        
        # 验证日期有效性
        if all(start_parts) and not self._validate_date(*start_parts):
            messagebox.showerror("错误", "开始日期无效")
            return "", ""
        
        if all(end_parts) and not self._validate_date(*end_parts):
            messagebox.showerror("错误", "结束日期无效")
            return "", ""
        
        start_date = "-".join(start_parts) if all(start_parts) else ""
        end_date = "-".join(end_parts) if all(end_parts) else ""
        return start_date, end_date
    
    def _validate_export_data(self, user_id):
        """验证导出数据"""
        if not user_id:
            messagebox.showerror("错误", "请先输入用户名！")
            return False
        
        stats = self.db.get_user_stats(user_id)
        if stats['total_books'] == 0:
            messagebox.showwarning("警告", "没有找到该用户的书籍数据，请先爬取！")
            return False
        return True
    
    def _start_progress_thread(self):
        """启动进度条线程"""
        # 确保之前的进度线程已清理
        if self._progress_thread and self._progress_thread.is_alive():
            self.export_running = False
            self._progress_thread.join(timeout=1.0)
        
        self.export_progress = 0
        self.export_running = True
        
        def update_progress_bar():
            while self.export_running:
                self.export_progress = min(100, self.export_progress + 1)
                self.update_progress(self.export_progress)
                import time
                time.sleep(self._progress_update_interval)
        
        self._progress_thread = threading.Thread(target=update_progress_bar, daemon=True)
        self._progress_thread.start()
    
    def _handle_option_change(self, *args):
        """处理选项变化，移除互斥关系，日期范围只在导出时使用"""
        # 不再禁用任何输入，让用户可以同时设置最大页数和日期范围
        # 最大页数用于爬取，日期范围只用于导出
        pass
    
    def _get_config_path(self):
        """获取配置文件路径"""
        config_dir = os.path.expanduser('~/.douban_crawler')
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.enc')
    
    def _encode_cookie(self, cookie):
        """简单编码Cookie（仅用于隐藏，非加密）"""
        return base64.b64encode(cookie.encode('utf-8')).decode('utf-8')
    
    def _decode_cookie(self, encoded_cookie):
        """解码Cookie"""
        try:
            return base64.b64decode(encoded_cookie.encode('utf-8')).decode('utf-8')
        except:
            return ""
    
    def load_config(self):
        """加载保存的配置"""
        try:
            config_path = self._get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.user_id_var.set(config.get('user_id', ''))
                    encoded_cookie = config.get('cookie', '')
                    self.cookie_var.set(self._decode_cookie(encoded_cookie))
        except Exception as e:
            self.log(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config_path = self._get_config_path()
            config = {
                'user_id': self.user_id_var.get(),
                'cookie': self._encode_cookie(self.cookie_var.get())
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            self.log(f"保存配置失败: {e}")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # 同时输出到日志文件
        logger.info(message)
        
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
        """更新用户统计信息，支持日期范围过滤"""
        try:
            # 获取当前选择的日期范围（年-月-日格式）
            start_year = self.start_year_var.get().strip()
            start_month = self.start_month_var.get().strip()
            start_day = self.start_day_var.get().strip()
            end_year = self.end_year_var.get().strip()
            end_month = self.end_month_var.get().strip()
            end_day = self.end_day_var.get().strip()
            
            # 组合成完整日期
            start_date = f"{start_year}-{start_month}-{start_day}" if (start_year and start_month and start_day) else ""
            end_date = f"{end_year}-{end_month}-{end_day}" if (end_year and end_month and end_day) else ""
            
            stats = self.db.get_user_stats(user_id, start_date, end_date)
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
        self.export_html_btn.config(state=tk.DISABLED)
        self.export_csv_btn.config(state=tk.DISABLED)
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        
        # 爬取时不使用日期范围过滤，只在导出时使用
        # 启动爬取线程
        self.crawl_thread = threading.Thread(
            target=self._crawl_worker, 
            args=(user_id, cookie, max_pages, None, None)  # 传递None作为日期范围，让爬虫忽略
        )
        self.crawl_thread.start()
    
    def stop_crawl(self):
        """停止爬取"""
        self.is_crawling = False
        self.update_status("正在停止...")
        self.log("用户请求停止爬取")
    
    def _crawl_worker(self, user_id, cookie, max_pages, start_date, end_date):
        """爬取工作线程"""
        try:
            # 导入爬虫模块
            from src.crawler.crawler import DoubanCrawler
            
            crawler = DoubanCrawler(self.db, self, save_debug_pages=self.save_debug_pages_var.get())
            crawler.crawl_user_books(user_id, cookie, max_pages, start_date, end_date)
            
        except Exception as e:
            import traceback
            self.log(f"爬取过程出现错误: {e}")
            self.log(f"错误堆栈: {traceback.format_exc()}")
            self.update_status("爬取失败")
        finally:
            # 恢复UI状态
            self.root.after(0, self._crawl_finished)
    
    def _crawl_finished(self):
        """爬取完成后的UI更新"""
        self.is_crawling = False
        self.crawl_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_html_btn.config(state=tk.NORMAL)
        self.export_csv_btn.config(state=tk.NORMAL)
        
        if self.user_id_var.get().strip():
            self.update_stats(self.user_id_var.get().strip())
    
    def export_html(self):
        """导出HTML文件，带动态进度条"""
        user_id = self.user_id_var.get().strip()
        if not self._validate_export_data(user_id):
            return
        
        start_date, end_date = self._get_date_range()
        if start_date == "" and end_date == "" and (
            self.start_year_var.get().strip() or 
            self.start_month_var.get().strip() or 
            self.start_day_var.get().strip() or
            self.end_year_var.get().strip() or 
            self.end_month_var.get().strip() or 
            self.end_day_var.get().strip()
        ):
            return  # 日期验证失败，已显示错误信息
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML文件", "*.html"), ("所有文件", "*.*")],
            initialfile=f"{user_id}_豆瓣书评.html"
        )
        
        if filename:
            self._export_with_progress("HTML", filename, user_id, start_date, end_date, self.html_exporter)
    
    def _reset_export_ui(self):
        """导出完成后重置UI"""
        # 清空用户名
        self.user_id_var.set("")
        
        # 清空统计信息
        self.stats_var.set("请输入用户名并开始爬取")
        
        # 重置进度条
        self.update_progress(0)
        
        # 清空日期范围（年-月-日）
        self.start_year_var.set("")
        self.start_month_var.set("")
        self.start_day_var.set("")
        self.end_year_var.set("")
        self.end_month_var.set("")
        self.end_day_var.set("")
        
        # 清空最大页数
        self.max_pages_var.set("")
        
        # 更新状态为就绪
        self.update_status("就绪")

def main():
    root = tk.Tk()
    app = DoubanBookGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()