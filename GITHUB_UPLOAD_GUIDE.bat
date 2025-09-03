@echo off
cls

:: GitHub上传指南 - 最终版
:: 由于自动化环境的限制，本脚本将帮助你手动完成上传

title GitHub上传指南

:START
cls
echo ===========================
echo      GitHub上传指南       
echo ===========================
echo.
echo 这个工具将帮助你将代码上传到GitHub仓库：
echo https://github.com/zyjzyjlaohu/hackerone-domains-crawler
echo.
echo 请确保你：
echo 1. 已安装Git（https://git-scm.com/download/win）
echo 2. 拥有GitHub账号和个人访问令牌（PAT）
echo 3. 有仓库的写入权限
echo.
echo [1] 检查Git安装状态
echo [2] 显示上传命令列表
echo [3] 查看项目结构
echo [4] 退出
echo.

set /p choice=请选择操作 [1-4]: 

if %choice%==1 goto CHECK_GIT
if %choice%==2 goto SHOW_COMMANDS
if %choice%==3 goto SHOW_STRUCTURE
if %choice%==4 goto EXIT

echo 无效的选择，请重试。
pause
goto START

:CHECK_GIT
echo.
echo 正在检查Git安装...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo 成功：Git已安装！
    git --version
    echo.
    echo Git用户配置：
    git config user.name
    git config user.email
    echo.
    if "%USERNAME%"=="" (
        echo 提示：建议先配置你的Git用户信息：
        echo git config --global user.name "你的GitHub用户名"
        echo git config --global user.email "你的GitHub邮箱"
    )
) else (
    echo 错误：未找到Git！
    echo 请先从以下地址下载并安装Git：
    echo https://git-scm.com/download/win
    echo 安装完成后请重新运行本脚本。
)
echo.
pause
goto START

:SHOW_COMMANDS
echo.
echo 以下是上传所需的Git命令：
echo ===========================
echo.
echo :: 1. 切换到项目目录
echo cd "i:\渗透测试脚本\爬取hackerone的众测url"
echo.
echo :: 2. 初始化Git仓库（如果尚未初始化）
echo git init
echo.
echo :: 3. 设置Git用户信息（只需设置一次）
echo git config --global user.name "你的GitHub用户名"
echo git config --global user.email "你的GitHub邮箱"
echo.
echo :: 4. 添加所有文件
echo git add .
echo.
echo :: 5. 提交更改
echo git commit -m "Upload HackerOne crawl scripts"
echo.
echo :: 6. 添加远程仓库
echo git remote add origin https://github.com/zyjzyjlaohu/hackerone-domains-crawler
echo.
echo :: 7. 强制推送到GitHub
echo git push --force origin main
echo.
echo 注意：执行最后一步时，系统会提示你输入GitHub用户名和个人访问令牌。
echo 请确保你的个人访问令牌具有仓库的写入权限。
echo.
echo 命令已保存到 GITHUB_UPLOAD_COMMANDS.txt 文件中。
echo.
pause
goto START

:SHOW_STRUCTURE
echo.
echo 项目文件结构：
echo ===========================
echo.
dir /b /o:n
echo.
echo 总计 %__CD__% 目录下的文件
echo.
echo .gitignore 文件已配置，会自动排除不需要上传的文件。
echo.
pause
goto START

:EXIT
echo.
echo 感谢使用GitHub上传指南！
echo 祝你上传成功！
echo.
pause
exit