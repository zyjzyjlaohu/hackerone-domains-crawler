@echo off
REM 解决远程仓库冲突并上传脚本
REM 此脚本会先拉取远程仓库内容，处理冲突，然后再推送

REM 设置变量
set REPO_URL=https://github.com/zyjzyjlaohu/hackerone-domains-crawler
set BRANCH_NAME=main

REM 打印说明
cls
echo ===================================================
echo 解决远程仓库冲突并上传脚本
 echo ===================================================
echo 此脚本将帮助你解决GitHub远程仓库冲突问题
echo 脚本会：1. 拉取远程仓库最新内容 2. 处理可能的冲突 3. 重新推送
 echo ===================================================
pause

REM 检查git是否安装
echo 检查Git是否已安装...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git没有安装。请先安装Git再运行此脚本。
    pause
    exit /b 1
)

echo Git已安装。

REM 切换到当前目录
echo 切换到脚本所在目录...
cd /d %~dp0
echo 当前目录：%CD%

REM 检查是否已经是git仓库
if not exist .git (
    echo 初始化Git仓库...
    git init
    if %errorlevel% neq 0 (
        echo 初始化Git仓库失败。
        pause
        exit /b 1
    )
    
    echo 添加远程仓库：%REPO_URL%
git remote add origin %REPO_URL%
) else (
    echo Git仓库已存在。
    
    REM 检查远程仓库配置
echo 检查远程仓库配置...
git remote -v | findstr "origin" >nul
if %errorlevel% neq 0 (
    echo 远程仓库未配置。添加远程仓库：%REPO_URL%
git remote add origin %REPO_URL%
) else (
    echo 远程仓库已配置。
)
)

REM 拉取远程仓库最新内容
echo.
echo ===================================================
echo 开始从远程仓库拉取最新内容
 echo 这将下载远程仓库的最新代码并尝试合并
 echo 如果有冲突，需要手动解决冲突
 echo ===================================================
pause
echo 拉取远程仓库内容...
git pull origin %BRANCH_NAME% --rebase

if %errorlevel% neq 0 (
    echo. 
echo ===================================================
echo 拉取失败，可能存在冲突！
 echo 解决方案：
 echo 1. 使用Git客户端（如Git GUI或VS Code）打开当前目录
 echo 2. 手动解决显示为冲突的文件
 echo 3. 解决冲突后，运行以下命令：
 echo    git add .
 echo    git rebase --continue
 echo 4. 完成后，再次运行此脚本
 echo ===================================================
    pause
    exit /b 1
)

REM 添加所有文件
echo 添加文件到暂存区...
git add .

REM 提交更改（如果有）
echo 检查是否有更改需要提交...
git status --porcelain >nul
if %errorlevel% equ 0 (
    set COMMIT_MESSAGE="Sync and update HackerOne crawl scripts"
    echo 创建提交...
    git commit -m %COMMIT_MESSAGE%
    if %errorlevel% neq 0 (
        echo 没有需要提交的更改。
    )
)

REM 推送代码
echo. 
echo ===================================================
echo 即将推送到GitHub仓库
 echo 请在弹出的凭证提示框中输入你的GitHub用户名和个人访问令牌
 echo ===================================================
pause
echo 推送到GitHub...
git push origin %BRANCH_NAME%

if %errorlevel% equ 0 (
    echo. 
echo ===================================================
echo 成功上传到GitHub仓库！
 echo 仓库地址：%REPO_URL%
echo ===================================================
) else (
    echo. 
echo ===================================================
echo 上传失败。请尝试手动推送：
 echo 1. 打开命令提示符
 echo 2. 导航到 %CD%
 echo 3. 运行：git push origin %BRANCH_NAME%
 echo. 
echo 如果仍然失败，可以尝试强制推送（谨慎使用）：
 echo git push origin %BRANCH_NAME% --force
 echo ===================================================
)

pause