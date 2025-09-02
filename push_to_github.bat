@echo off
REM 这个脚本用于将hackerone目录的内容上传到GitHub仓库

REM 设置变量
set REPO_URL="https://github.com/zyjzyjlaohu/hackerone-domains-crawler"
set BRANCH_NAME="main"
set COMMIT_MESSAGE="Upload HackerOne crawl scripts"

REM 检查git是否安装
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git没有安装。请先安装Git再运行此脚本。
    pause
    exit /b 1
)

REM 切换到当前目录
cd /d %~dp0

REM 检查是否已经是git仓库
if not exist .git (
    echo 初始化git仓库...
    git init
)

REM 添加所有文件（除了.gitignore中指定的文件）
echo 添加文件到暂存区...
git add .

REM 提交更改
echo 提交更改...
git commit -m %COMMIT_MESSAGE%

REM 添加远程仓库
echo 添加远程仓库...
git remote add origin %REPO_URL%

REM 推送代码到GitHub
echo 推送到GitHub仓库...
git push -u origin %BRANCH_NAME%

if %errorlevel% equ 0 (
    echo 成功上传到GitHub仓库！
) else (
    echo 上传失败。可能需要检查以下几点：
    echo 1. 确认GitHub用户名和仓库名称正确
    echo 2. 确认你有该仓库的写入权限
    echo 3. 确认网络连接正常
    echo 4. 可能需要先设置git的用户信息：
    echo    git config --global user.name "Your Name"
    echo    git config --global user.email "your.email@example.com"
)

pause