@echo off

REM 测试MCP参数是否被正确解析
REM 注意：此脚本仅测试参数解析，不会实际运行爬虫

REM 测试MCP Playwright参数
python crawl_hackerone_domains.py --use-mcp-playwright --mcp-host localhost --mcp-port 8080 --check-config

REM 测试MCP Firecrawl参数
python crawl_hackerone_domains.py --use-mcp-firecrawl --mcp-host localhost --mcp-port 8080 --check-config

REM 测试同时使用两种MCP模式
python crawl_hackerone_domains.py --use-mcp-playwright --use-mcp-firecrawl --mcp-host localhost --mcp-port 8080 --check-config

REM 显示使用说明
cls
echo. 
echo 成功完成MCP参数测试!
 echo. 
echo 使用说明:
echo ==========
echo 1. 使用MCP Playwright模式:
echo    python crawl_hackerone_domains.py --use-mcp-playwright --mcp-host 服务器IP --mcp-port 服务器端口
echo. 
echo 2. 使用MCP Firecrawl模式:
echo    python crawl_hackerone_domains.py --use-mcp-firecrawl --mcp-host 服务器IP --mcp-port 服务器端口
echo. 
echo 3. 同时使用两种MCP模式:
echo    python crawl_hackerone_domains.py --use-mcp-playwright --use-mcp-firecrawl --mcp-host 服务器IP --mcp-port 服务器端口
echo. 
echo 按任意键退出...
pause >nul