# 豆瓣书评爬虫工具使用说明

## 功能特性
- ✅ 爬取豆瓣用户的读书收藏和书评
- ✅ 数据存储在SQLite数据库中，支持增量更新  
- ✅ 提供美观的HTML导出格式，支持搜索和筛选
- ✅ 同时支持GUI界面和命令行两种使用方式

## 新增文件说明
1. **database.py** - 数据库操作模块，提供SQLite数据存储
2. **gui.py** - GUI界面模块，基于Tkinter
3. **crawler_with_db.py** - 改进的爬虫模块，支持数据库存储
4. **html_exporter.py** - HTML导出模块，生成美观的书评报告
5. **main.py** - 主程序入口，支持多种启动方式

## 使用方法

### 1. GUI界面模式（推荐）
```bash
python main.py
```
或直接运行：
```bash
python gui.py
```

### 2. 命令行模式
```bash
# 交互式爬取
python main.py --cli

# 指定参数爬取
python main.py --cli --user your_username --cookie "your_cookie" --max-pages 5

# 仅导出已有数据的HTML
python main.py --export your_username --output report.html
```

## Cookie获取方法
1. 在浏览器中登录豆瓣网站
2. 访问你的豆瓣收藏页面
3. 按F12打开开发者工具
4. 切换到Network（网络）标签页
5. 刷新页面，找到页面请求
6. 在请求头中复制Cookie字段的完整值

## 数据库结构
- **books表** - 存储书籍信息、评分和书评
- **users表** - 存储用户信息和统计数据
- **crawl_logs表** - 记录爬取历史和状态

## HTML导出特性
- 📊 统计信息展示（总书籍数、书评数、各星级分布）
- 🔍 实时搜索功能（支持书名、作者、书评内容）
- 🏷️ 评分筛选（按星级、是否有书评筛选）
- 📱 响应式设计，支持移动端访问
- 🎨 美观的卡片式布局

## 主要改进
1. **数据持久化** - 使用SQLite数据库替代Excel文件
2. **增量更新** - 支持在已有数据基础上继续爬取
3. **用户界面** - 提供友好的GUI界面
4. **数据导出** - 生成交互式HTML报告
5. **错误处理** - 完善的异常处理和重试机制

## 注意事项
- 首次使用需要配置豆瓣Cookie
- 爬取过程中请保持网络连接稳定
- 建议设置合理的页数限制，避免过度爬取
- 生成的HTML文件包含完整的交互功能