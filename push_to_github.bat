@echo off
REM 这个脚本用于将HackerOne爬取脚本代码推送到GitHub仓库
REM 运行此脚本后，系统会提示您输入GitHub用户名和密码

cd /d "%~dp0"

echo 正在将代码推送到GitHub仓库...
git push origin main

if %errorlevel% equ 0 (
    echo 推送成功！
) else (
    echo 推送失败，请检查您的GitHub凭证是否正确。
    pause
)

pause