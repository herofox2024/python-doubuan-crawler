@echo off
chcp 65001 > nul
title 豆瓣书评爬虫工具 - 快速启动

echo ========================================
echo    豆瓣书评爬虫工具 - 快速启动菜单
echo ========================================
echo.
echo 请选择启动方式:
echo.
echo [1] GUI界面模式 (推荐)
echo [2] 命令行模式
echo [3] 运行功能测试
echo [4] 直接运行exe文件
echo [5] 查看项目结构
echo [0] 退出
echo.

:menu
set /p choice="请输入选项 (0-5): "

if "%choice%"=="1" (
    echo 启动GUI界面...
    python main.py
    goto end
)

if "%choice%"=="2" (
    echo 启动命令行模式...
    python main.py --cli
    goto end
)

if "%choice%"=="3" (
    echo 运行功能测试...
    python test_all.py
    pause
    goto menu
)

if "%choice%"=="4" (
    echo 启动exe文件...
    start "" "可执行文件\豆瓣书评爬虫.exe"
    goto end
)

if "%choice%"=="5" (
    echo 项目文件结构:
    tree /f
    pause
    goto menu
)

if "%choice%"=="0" (
    goto end
)

echo 无效选项，请重新选择
goto menu

:end
echo 感谢使用豆瓣书评爬虫工具！
pause