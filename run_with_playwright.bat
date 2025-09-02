@echo off

REM 这是一个用于运行HackerOne众测域名爬虫的批处理文件
REM 使用Playwright模式进行爬取

REM 确保在运行此脚本前已安装所需依赖
REM pip install playwright beautifulsoup4 requests selenium webdriver-manager
REM playwright install

REM 设置输出文件路径
set OUTPUT_FILE=hackerone_domains.csv

REM 运行爬虫，使用Playwright模式
REM 可选参数:
REM --playwright: 使用Playwright进行爬取
REM --playwright-login: 使用Playwright模拟登录HackerOne (需要提供用户名和密码)
REM -u 用户名: HackerOne用户名
REM --password 密码: HackerOne密码
REM -o 输出文件: 指定输出文件路径
REM -d 最小延迟 最大延迟: 设置请求延迟范围
REM -l 日志级别: 设置日志级别 (DEBUG, INFO, WARNING, ERROR)

REM 基本命令 (不登录)
python crawl_hackerone_domains.py --playwright -o %OUTPUT_FILE% -d 2 5 -l INFO

REM 如果需要登录，请取消下面一行的注释并替换为您的用户名和密码
REM python crawl_hackerone_domains.py --playwright --playwright-login -u "您的用户名" --password "您的密码" -o %OUTPUT_FILE% -d 2 5 -l INFO

REM 等待用户输入，防止窗口自动关闭
pause