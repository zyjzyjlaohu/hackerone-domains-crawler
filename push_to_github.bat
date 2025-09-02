@echo off

REM 此批处理文件用于将HackerOne域名爬虫代码推送到GitHub仓库
REM 由于需要GitHub认证，无法在自动化环境中完成，请您手动运行此文件

setlocal enabledelayedexpansion

REM 设置仓库信息
set REPO_OWNER=zyjzyjlaohu
set REPO_NAME=hackerone-domains-crawler
set GITHUB_URL=https://github.com/%REPO_OWNER%/%REPO_NAME%.git

REM 导航到脚本目录
cd /d "%~dp0"

REM 检查是否已添加远程仓库
for /f "tokens=2" %%i in ('git remote -v ^| findstr "origin"') do (
    set EXISTING_REMOTE=%%i
)

REM 如果尚未添加远程仓库，则添加
if not defined EXISTING_REMOTE (
    echo 添加远程仓库: %GITHUB_URL%
    git remote add origin %GITHUB_URL%
    if errorlevel 1 (
        echo 添加远程仓库失败！
        echo 错误可能是：
        echo 1. GitHub仓库不存在，请先在GitHub上创建
        echo 2. 网络连接问题
        echo 3. 权限问题
        pause
        exit /b 1
    )
) else (
    echo 远程仓库已存在: !EXISTING_REMOTE!
)

REM 显示推送说明
cls
echo =======================================================
echo                推送代码到GitHub指南
========================================================
echo.
echo 此操作需要GitHub账号认证。由于安全限制，我们无法直接获取您的
 echo GitHub凭据，因此需要您手动输入。
echo.
echo 推荐使用个人访问令牌(PAT)作为密码：
echo 1. 访问 https://github.com/settings/tokens
 echo 2. 点击 "Generate new token"
 echo 3. 选择适当的权限(至少需要 repo 权限)
 echo 4. 生成令牌并复制保存
 echo 5. 在下面提示输入密码时，粘贴此令牌
 echo.
echo 注意：输入的密码不会显示在屏幕上
 echo.
 pause

REM 执行推送操作
echo 开始推送代码到GitHub仓库...
git push -u origin main

if errorlevel 1 (
    echo.
    echo 推送失败！常见原因：
    echo 1. 用户名或密码/令牌错误
    echo 2. 仓库不存在(请先在GitHub上创建)
    echo 3. 网络连接问题
    echo 4. 权限不足
    echo.
    echo 请检查以上问题，然后重新运行此脚本。
) else (
    echo.
    echo 恭喜！代码已成功推送到GitHub仓库：
    echo %GITHUB_URL%
)

pause