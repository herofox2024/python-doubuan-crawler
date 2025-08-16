# 豆瓣书评爬虫工具

## 📁 项目结构

```
豆瓣书评爬虫项目/
├── README.md                    # 项目说明文档
├── main.py                      # 主程序入口
├── database.py                  # 数据库操作模块
├── gui.py                       # GUI界面模块
├── crawler_with_db.py           # 爬虫核心模块
├── html_exporter.py             # HTML导出模块
├── test_all.py                  # 功能测试脚本
├── requirements.txt             # 项目依赖
├── build.bat                    # 自动打包脚本
├── 豆瓣书评爬虫.spec             # PyInstaller配置
├── 使用指南.md                   # 详细使用指南
├── README_NEW.md                # 功能说明文档
├── 原版代码/
│   ├── 豆瓣已看书籍评分.py        # 原始爬虫代码
│   └── 爬豆瓣书评.py             # 原版爬虫代码
└── 可执行文件/
    ├── 豆瓣书评爬虫.exe          # 独立可执行文件
    └── 使用说明.txt              # exe使用说明
```

## 🚀 快速开始

### 方式1: 直接运行exe文件（推荐）
```bash
cd 可执行文件/
# 双击 豆瓣书评爬虫.exe
```

### 方式2: Python源码运行
```bash
# 安装依赖
pip install -r requirements.txt

# GUI模式
python main.py

# 命令行模式
python main.py --cli

# 查看帮助
python main.py --help
```

### 方式3: 自行打包
```bash
# 运行自动打包脚本
build.bat

# 或手动打包
pyinstaller --clean 豆瓣书评爬虫.spec
```

## ✨ 核心功能

1. **数据爬取** - 爬取豆瓣用户的读书收藏和书评
2. **数据存储** - SQLite数据库持久化存储
3. **GUI界面** - 友好的图形用户界面
4. **HTML导出** - 生成美观的交互式报告
5. **数据管理** - 支持搜索、筛选、统计分析

## 🛠️ 技术栈

- **Python 3.7+** - 主要开发语言
- **Tkinter** - GUI界面框架
- **SQLite** - 数据库存储
- **Requests** - HTTP请求库
- **BeautifulSoup** - HTML解析
- **Pandas** - 数据处理
- **PyInstaller** - 程序打包

## 📋 使用说明

### Cookie获取
1. 浏览器登录豆瓣网站
2. 访问你的收藏页面
3. F12开发者工具 → Network标签页
4. 刷新页面 → 找到页面请求 → 复制Cookie

### 数据导出
- **Excel格式** - 兼容原版，便于数据分析
- **HTML格式** - 交互式网页报告，支持搜索筛选

## ⚠️ 注意事项

1. **合规使用** - 仅用于个人数据备份，请遵守豆瓣服务条款
2. **频率控制** - 合理设置爬取间隔，避免对服务器造成压力
3. **Cookie管理** - 定期更新Cookie，注意隐私保护
4. **数据备份** - 重要数据请及时备份

## 📞 联系方式

如有问题或建议，请查看使用指南或联系开发者。

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。

---

**开始您的豆瓣书评数据管理之旅！** 📚✨