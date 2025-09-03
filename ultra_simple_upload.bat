@echo off

:: 非常简单的GitHub上传脚本
:: 配置变量
set REPO_URL=https://github.com/zyjzyjlaohu/hackerone-domains-crawler
set BRANCH_NAME=main
set COMMIT_MESSAGE="Upload HackerOne crawl scripts"

cls
echo ========== 简单GitHub上传脚本 ==========

echo 1. 检查Git是否安装...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Git！请先安装Git
    echo 下载地址：https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git已安装

:: 检查是否有.git目录
echo 2. 检查Git仓库状态...
if not exist ".git" (
    echo 初始化Git仓库...
    git init
)

echo 3. 配置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

:: 添加所有文件
echo 4. 添加所有文件...
git add .

:: 提交更改
echo 5. 提交更改...
git commit -m %COMMIT_MESSAGE% >nul 2>&1

:: 推送
echo 6. 推送代码到GitHub (这将强制覆盖远程仓库内容！)...
echo 请在弹出的提示框中输入你的GitHub用户名和个人访问令牌
git push --force origin %BRANCH_NAME%

if %errorlevel% equ 0 (
    echo.
    echo ========== 上传成功！ ==========
    echo 你的代码已成功上传到：
    echo %REPO_URL%
) else (
    echo.
    echo ========== 上传失败！ ==========
    echo 可能的问题：
    echo 1. 个人访问令牌无效或权限不足
    echo 2. 网络连接问题
    echo 3. 仓库不存在或权限不足
    echo.
    echo 请手动尝试以下命令：
    echo cd "%cd%"
    echo git push --force origin %BRANCH_NAME%
)

pause