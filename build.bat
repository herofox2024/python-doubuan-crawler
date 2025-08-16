@echo off
chcp 65001 > nul
echo ===============================================
echo 豆瓣书评爬虫工具 - 自动打包脚本
echo ===============================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo [2/4] 安装打包依赖...
pip install pyinstaller
if errorlevel 1 (
    echo 警告: PyInstaller安装可能有问题，但继续尝试打包
)

echo [3/4] 开始打包程序...
echo 使用配置文件打包（推荐）...
pyinstaller --clean 豆瓣书评爬虫.spec

if not errorlevel 1 (
    echo [SUCCESS] 打包成功！
    echo 可执行文件位置: dist\豆瓣书评爬虫.exe
    echo.
    echo [4/4] 检查打包结果...
    if exist "dist\豆瓣书评爬虫.exe" (
        echo ✓ exe文件已生成
        for %%A in ("dist\豆瓣书评爬虫.exe") do echo   文件大小: %%~zA 字节
        echo.
        echo 使用说明:
        echo 1. 将 dist\豆瓣书评爬虫.exe 复制到任意位置
        echo 2. 双击运行即可启动GUI界面
        echo 3. 首次运行会创建数据库文件
        echo.
        choice /c YN /m "是否立即测试运行exe文件"
        if errorlevel 2 goto end
        echo 启动测试...
        start "" "dist\豆瓣书评爬虫.exe"
    ) else (
        echo ✗ exe文件生成失败
    )
) else (
    echo [FAIL] 打包失败，尝试简单打包...
    pyinstaller --onefile --windowed --name="豆瓣书评爬虫" main.py
    if errorlevel 1 (
        echo 简单打包也失败，请检查错误信息
    )
)

:end
echo.
echo 打包完成！
pause