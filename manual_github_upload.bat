@echo off
REM 手动GitHub上传脚本
REM 请在命令窗口中运行此脚本，以便能够输入GitHub凭证

REM 设置变量
set REPO_URL=https://github.com/zyjzyjlaohu/hackerone-domains-crawler
set BRANCH_NAME=main
set COMMIT_MESSAGE="Upload HackerOne crawl scripts"

REM 打印说明
cls
echo ===================================================
echo 手动GitHub上传脚本
 echo ===================================================
echo 此脚本将帮助你将hackerone目录上传到GitHub仓库
 echo 请确保你有GitHub账号和对目标仓库的写入权限
 echo 运行过程中需要输入GitHub用户名和个人访问令牌
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

REM 检查git用户信息
echo 检查Git用户配置...
git config user.name >nul 2>nul
git config user.email >nul 2>nul
if %errorlevel% neq 0 (
    echo Git用户信息未配置。请先配置Git用户信息：
    echo git config --global user.name "你的用户名"
    echo git config --global user.email "你的邮箱"
    pause
    exit /b 1
)

echo Git用户信息已配置。

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
) else (
    echo Git仓库已存在。
)

REM 添加所有文件
echo 添加文件到暂存区...
git add .
if %errorlevel% neq 0 (
    echo 添加文件失败。
    pause
    exit /b 1
)

echo 文件已添加。

REM 提交更改
echo 创建提交...
git commit -m %COMMIT_MESSAGE%
if %errorlevel% neq 0 (
    echo 创建提交失败。可能没有需要提交的更改。
    pause
)

REM 移除旧的远程仓库
echo 配置远程仓库...
git remote | findstr "origin" >nul
if %errorlevel% equ 0 (
    echo 移除已存在的origin远程仓库...
    git remote remove origin
)

REM 添加新的远程仓库
echo 添加远程仓库：%REPO_URL%
git remote add origin %REPO_URL%
if %errorlevel% neq 0 (
    echo 添加远程仓库失败。请检查URL是否正确。
    pause
    exit /b 1
)

echo 远程仓库配置完成。

REM 推送代码
echo. 
echo ===================================================
echo 即将推送到GitHub仓库
 echo 请在弹出的凭证提示框中输入你的GitHub用户名和个人访问令牌
 echo 注意：个人访问令牌需要有对仓库的写入权限
 echo ===================================================
pause
echo 推送到GitHub...
git push -u origin %BRANCH_NAME%

if %errorlevel% equ 0 (
    echo. 
echo ===================================================
echo 成功上传到GitHub仓库！
 echo 仓库地址：%REPO_URL%
echo ===================================================
) else (
    echo. 
echo ===================================================
echo 上传失败。可能的原因：
 echo 1. 网络连接问题
 echo 2. GitHub凭证不正确或没有写入权限
 echo 3. 防火墙或代理限制
 echo. 
echo 解决方案：
 echo 1. 检查网络连接
 echo 2. 确保个人访问令牌有正确的权限
 echo 3. 如果使用代理，配置Git代理：
 echo    git config --global http.proxy http://代理服务器:端口
 echo 4. 尝试使用SSH方式连接GitHub
 echo. 
echo 你也可以尝试手动推送：
 echo 1. 打开命令提示符
 echo 2. 导航到 %CD%
 echo 3. 运行：git push -u origin %BRANCH_NAME%
 echo ===================================================
)

pause