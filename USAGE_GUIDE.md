# HackerOne众测域名爬虫使用指南

## 概述

这个工具设计用于爬取HackerOne平台上的众测项目域名信息。由于HackerOne是一个需要JavaScript的单页应用，并且可能存在网络访问限制，本指南将帮助您正确配置和使用爬虫工具。

## 已提供的文件

- **crawl_hackerone_domains_updated.py**: 主要爬虫脚本，支持crawl4ai、Playwright和基本HTTP请求模式
- **run_crawl4ai.bat**: 批处理文件，提供简便的运行方式
- **direct_hackerone_crawl.py**: 直接爬取脚本，不依赖复杂库
- **hackerone_domains_sample.csv**: 模拟数据文件，展示预期的输出格式
- **proxy_test.py**: 代理测试工具
- **detailed_network_test.py**: 详细网络诊断工具
- **simple_crawl_test.py**: 简化版测试脚本

## 安装依赖

确保已安装所有必要的依赖：

```bash
pip install beautifulsoup4 requests python-dotenv
# 可选，但推荐
pip install crawl4ai
```

## 使用方法

### 方法1：使用批处理文件（推荐）

运行`run_crawl4ai.bat`文件，它会自动：
1. 检查并激活虚拟环境
2. 安装必要的依赖
3. 测试网络连接
4. 询问是否使用代理
5. 运行爬虫脚本

### 方法2：命令行直接运行

根据您的网络环境和需求，选择以下命令之一：

#### 1. 使用crawl4ai模式（推荐）

```bash
python crawl_hackerone_domains_updated.py --use-crawl4ai --log-level DEBUG
```

#### 2. 不使用代理直接爬取

```bash
python crawl_hackerone_domains_updated.py --log-level DEBUG
```

#### 3. 使用代理爬取

```bash
python crawl_hackerone_domains_updated.py --use-proxy --proxy-file proxies.txt --log-level DEBUG
```

## 网络连接问题解决方案

如果您遇到网络连接问题（超时、连接错误等），请尝试以下解决方案：

### 1. 检查网络连接

- 确认您的网络连接正常
- 尝试访问其他网站验证网络连接
- 检查防火墙和安全软件设置

### 2. 使用代理服务器

编辑`proxies.txt`文件，添加有效的代理服务器：

```
# 格式：主机名:端口
127.0.0.1:10808  # 本地代理示例
```

使用`proxy_test.py`测试代理是否有效：

```bash
python proxy_test.py
```

### 3. 使用VPN

如果直接连接受限，尝试使用VPN服务访问HackerOne。

### 4. 更换爬取模式

尝试不同的爬取模式：
- crawl4ai模式（推荐）
- Playwright模式（需要安装Playwright）
- 基本HTTP请求模式

## 模拟数据文件说明

为了展示爬虫的预期输出格式，我们提供了`hackerone_domains_sample.csv`文件，其中包含模拟的HackerOne众测域名数据。这个文件可以帮助您了解爬虫成功时的输出结构。

## 常见问题解答

### Q: 为什么爬虫只返回了少量域名或没有返回任何域名？
**A:** 可能的原因包括：
- 网络连接问题
- HackerOne网站结构变更
- 需要登录才能访问完整的众测列表
- JavaScript渲染问题

### Q: 如何获取更好的爬取效果？
**A:** 建议：
- 使用crawl4ai或Playwright模式
- 确保有稳定的网络连接或使用有效的代理
- 考虑创建HackerOne账号并使用登录功能
- 调整请求延迟参数，避免触发速率限制

### Q: 为什么之前的版本会输出example.com？
**A:** 之前的版本在初始化时默认添加了一个example.com作为测试条目，现在这个默认条目已经被移除，爬虫只会输出实际爬取到的域名。

## 注意事项

1. 请遵守HackerOne的服务条款和爬虫政策
2. 避免过于频繁的请求，以免触发速率限制
3. 尊重网站的robots.txt规则
4. 仅将此工具用于合法和道德的目的

## 输出文件

- **hackerone_domains.csv**: 包含爬取到的域名和对应的HackerOne项目URL
- **hackerone_domains.csv.tmp**: 临时文件，用于保存爬取进度

## 高级配置

如果您需要自定义爬虫行为，可以修改以下参数：

- `--delay 2 5`: 设置请求延迟范围（秒）
- `--max-retries 5`: 设置最大重试次数
- `--backoff-factor 0.5`: 设置退避因子
- `--log-level DEBUG`: 设置日志级别（DEBUG、INFO、WARNING、ERROR）