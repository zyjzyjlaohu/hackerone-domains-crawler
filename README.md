# HackerOne众测域名爬虫

一个用于爬取 HackerOne 平台上所有众测项目域名的爬虫工具。支持多种爬取方式，包括crawl4ai、Playwright、Firecrawl API和基本HTTP请求，特别支持使用 Playwright 进行模拟登录以访问更多项目。

## 功能特点

- 🚀 **多引擎支持**：集成crawl4ai、Playwright、Firecrawl API和基本HTTP请求四种爬取模式
- 🔄 **自动重试**：网络请求失败时自动重试，支持指数退避
- 🔐 **代理支持**：可配置代理服务器，避免IP限制
- 💾 **进度保存**：定期保存爬取进度，支持断点续爬
- 📊 **详细日志**：记录爬取过程的详细信息，便于调试
- 🎯 **精确解析**：多种解析策略，确保准确提取域名信息
- 👥 **模拟登录**：支持Playwright模拟登录HackerOne，访问更多私有或受限项目

## 安装依赖

### 基本依赖

```bash
# 安装基础依赖
pip install requests beautifulsoup4
```

### 可选依赖

如果需要使用crawl4ai功能（推荐）：

```bash
pip install crawl4ai
```

如果需要使用Playwright功能：

```bash
pip install playwright
playwright install
```

如果需要使用Firecrawl API功能：

```bash
pip install firecrawl-py
```

### 快速安装

使用提供的批处理文件可自动安装所有必要依赖：

```bash
run_crawl4ai.bat
```

## 使用方法

### 快速开始

最简单的方法是使用提供的批处理文件：

```bash
# 双击运行或在命令行中执行
run_crawl4ai.bat
```

这将自动安装必要的依赖并启动爬虫。

### 命令行参数

```bash
python crawl_hackerone_domains_updated.py [参数]
```

### 爬取模式选择

根据您的环境和需求，选择最适合的爬取模式：

1. **crawl4ai模式**（推荐）：
   
   ```bash
   python crawl_hackerone_domains_updated.py --use-crawl4ai
   ```
   
   使用浏览器界面（非无头模式）：
   
   ```bash
   python crawl_hackerone_domains_updated.py --use-crawl4ai --use-browser-use
   ```

2. **Playwright模式**：
   
   ```bash
   python crawl_hackerone_domains_updated.py --playwright
   ```
   
   使用Playwright模拟登录：
   
   ```bash
   python crawl_hackerone_domains_updated.py --playwright --playwright-login -u 你的用户名 --password 你的密码
   ```

3. **Firecrawl API模式**：
   
   ```bash
   python crawl_hackerone_domains_updated.py --use-firecrawl --firecrawl-api-key 你的API密钥
   ```

4. **基本HTTP请求模式**（作为回退选项）：
   
   ```bash
   python crawl_hackerone_domains_updated.py
   ```

### 代理配置

如果需要使用代理，可以创建`proxies.txt`文件，每行一个代理，格式为：

```
ip:port
```

然后运行：

```bash
python crawl_hackerone_domains_updated.py --use-proxy --proxy-file proxies.txt
```

## 命令行参数

脚本支持以下命令行参数：

```
-h, --help            显示帮助信息
-o OUTPUT, --output OUTPUT
                      输出文件路径 (默认: hackerone_domains.csv)
-p, --use-proxy       使用代理服务器
-f PROXY_FILE, --proxy-file PROXY_FILE
                      包含代理列表的文件路径
-d DELAY DELAY, --delay DELAY DELAY
                      请求延迟范围 (默认: 1 3)
-r MAX_RETRIES, --max-retries MAX_RETRIES
                      最大重试次数 (默认: 3)
-b BACKOFF_FACTOR, --backoff-factor BACKOFF_FACTOR
                      退避因子 (默认: 0.3)
-i PROGRESS_INTERVAL, --progress-interval PROGRESS_INTERVAL
                      进度保存间隔 (默认: 10)
-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                      日志级别 (默认: INFO)
--use-crawl4ai        使用crawl4ai进行爬取
--use-browser-use     在crawl4ai模式下使用浏览器界面（非无头模式）
--browser-type {chrome,firefox,edge}
                      浏览器类型 (默认: chrome)
--use-firecrawl       使用Firecrawl API进行爬取
--firecrawl-api-key FIRECRAWL_API_KEY
                      Firecrawl API密钥
--playwright          使用Playwright进行爬取
--playwright-login    使用Playwright模拟登录HackerOne
-u USERNAME, --username USERNAME
                      HackerOne用户名 (用于Playwright登录)
--password PASSWORD   HackerOne密码 (用于Playwright登录)
--use-mcp-playwright  使用MCP服务器调用Playwright
--use-mcp-firecrawl   使用MCP服务器调用Firecrawl
--mcp-host MCP_HOST
                      MCP服务器主机地址 (默认: localhost)
--mcp-port MCP_PORT
                      MCP服务器端口 (默认: 8000)
```

## 代理文件格式

代理文件应为文本文件，每行一个代理，格式为：`ip:port`

```
127.0.0.1:8080
192.168.1.1:3128
```

run_crawl4ai.bat脚本会自动检测并使用此文件中的代理。

## 常见问题排查

### 网络连接问题

如果遇到连接超时或失败的问题，请参考以下解决方案：

1. **检查网络连接**：确保您的网络连接正常，尝试访问其他网站验证

2. **检查防火墙设置**：确认防火墙或安全软件没有阻止连接

3. **使用代理或VPN**：如果您的IP被限制，尝试使用不同的网络环境

4. **运行网络测试工具**：
   
   ```bash
   python network_test.py
   ```
   
   此工具将帮助诊断DNS解析、SSL连接和HTTP请求问题。

### 爬取模式选择

根据您的环境和需求，选择最适合的爬取模式：

1. **crawl4ai模式**（推荐）：
   - 支持JavaScript渲染
   - 界面友好，适合调试
   - 安装命令：`pip install crawl4ai`

2. **Playwright模式**：
   - 功能强大，支持复杂交互
   - 安装命令：`pip install playwright && playwright install`

3. **基本HTTP请求模式**：
   - 最简单，但可能无法处理需要JavaScript的内容
   - 作为其他模式失败时的回退选项

### 其他常见问题

- **HackerOne需要JavaScript**：这是一个单页应用，建议使用crawl4ai或Playwright模式
- **爬取速度慢**：可以调整`--delay`参数减少请求间隔，但注意不要触发网站的速率限制
- **无法找到众测项目**：尝试更新脚本或使用不同的爬取模式

## 输出文件

- `hackerone_domains.csv`：包含爬取到的域名和对应的HackerOne项目URL
- `hackerone_domains.csv.tmp`：临时文件，用于保存爬取进度
- `hackerone_page.html`：调试文件，包含最近爬取的页面内容

## 注意事项

1. **遵守网站规则**：请确保您的爬取活动符合HackerOne的服务条款
2. **合理设置请求间隔**：过快的请求可能会导致您的IP被临时或永久限制
3. **保护API密钥**：如果使用Firecrawl API，请妥善保管您的API密钥
4. **定期更新依赖**：爬虫库和网站结构可能会变化，定期更新依赖以保持兼容性

## 示例输出

CSV文件格式示例：

```csv
domain,url
example.com,https://hackerone.com/example-company
api.example.org,https://hackerone.com/example-company
```

## 高级配置

### 自定义请求头

您可以在脚本中修改`USER_AGENTS`列表，添加更多的用户代理字符串。

### 自定义解析策略

如果HackerOne网站结构发生变化，您可能需要更新`parse_programs_page`和`parse_program_details`方法中的解析逻辑。

### 批量处理

对于大规模爬取，可以调整`progress_interval`参数，更频繁地保存进度，避免数据丢失。

## 免责声明

本脚本仅用于教育和研究目的，请确保你的爬取行为符合相关网站的使用条款和法律法规。