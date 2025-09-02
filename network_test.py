import requests
import time
import sys
import socket
import ssl
import json
from urllib.parse import urlparse

# 设置中文字符支持
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 测试目标
test_urls = [
    "https://hackerone.com",
    "https://hackerone.com/opportunities/all",
    "https://www.google.com",
    "https://www.github.com"
]

# 测试超时时间
timeout = 30

# 代理配置（如果有）
proxy_file = "proxies.txt"
proxies = None

# 打印分隔线
def print_separator():
    print("=" * 70)

# 测试DNS解析
def test_dns(url):
    print(f"\n测试DNS解析: {url}")
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        print(f"成功解析 {hostname} 到 IP 地址: {', '.join(ip_addresses)}")
        return True
    except Exception as e:
        print(f"DNS解析失败: {e}")
        return False

# 测试SSL连接
def test_ssl(url):
    print(f"\n测试SSL连接: {url}")
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"SSL连接成功: {hostname}")
                print(f"SSL版本: {ssock.version()}")
                print(f"证书颁发者: {dict(x[0] for x in cert['issuer'])}")
                print(f"证书有效期至: {cert['notAfter']}")
        return True
    except Exception as e:
        print(f"SSL连接失败: {e}")
        return False

# 测试HTTP请求
def test_http_request(url, use_proxy=False):
    print(f"\n测试HTTP请求: {url}")
    print(f"使用代理: {use_proxy}")
    print(f"超时时间: {timeout}秒")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, proxies=proxies if use_proxy else None, timeout=timeout, allow_redirects=True)
        elapsed_time = time.time() - start_time
        
        print(f"请求成功，状态码: {response.status_code}")
        print(f"请求耗时: {elapsed_time:.2f}秒")
        print(f"响应大小: {len(response.text)} 字节")
        print(f"最终URL: {response.url}")
        
        # 检查是否是HackerOne的页面
        if "hackerone.com" in url:
            # 检查页面内容是否包含预期的元素
            if "opportunities" in url and "bug bounty" in response.text.lower():
                print("✅ 页面内容包含预期的众测项目相关内容")
            elif "JavaScript is disabled" in response.text:
                print("⚠️ 警告: 页面检测到JavaScript被禁用，可能无法获取完整内容")
            else:
                print("✅ 页面内容看起来正常")
        
        # 保存一小部分内容用于调试
        debug_file = f"debug_{urlparse(url).netloc.replace('.', '_')}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text[:1000] + "\n\n<!-- 内容已截断 -->")
        print(f"调试信息已保存到: {debug_file}")
        
        return True
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时: 超过{timeout}秒")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: 无法建立连接")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

# 加载代理
def load_proxies():
    global proxies
    if not proxies and os.path.exists(proxy_file):
        print(f"\n从文件加载代理: {proxy_file}")
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                proxy_lines = f.readlines()
                if proxy_lines:
                    # 只使用第一个代理进行测试
                    proxy = proxy_lines[0].strip()
                    proxies = {
                        'http': f'http://{proxy}',
                        'https': f'https://{proxy}'
                    }
                    print(f"已加载代理: {proxy}")
                    return True
                else:
                    print("代理文件为空")
        except Exception as e:
            print(f"加载代理文件失败: {e}")
    return False

# 主函数
def main():
    print_separator()
    print("HackerOne爬虫网络连接测试工具")
    print_separator()
    print("此工具将帮助您诊断爬取HackerOne时可能遇到的网络问题。")
    print("\n测试内容包括：")
    print("1. DNS解析")
    print("2. SSL连接")
    print("3. HTTP请求（直接连接和代理连接）")
    print_separator()
    
    # 加载代理
    has_proxies = load_proxies()
    
    # 进行测试
    for url in test_urls:
        print_separator()
        print(f"\n正在测试: {url}")
        
        # DNS解析测试
        dns_ok = test_dns(url)
        
        # SSL连接测试
        if dns_ok:
            ssl_ok = test_ssl(url)
        else:
            ssl_ok = False
        
        # HTTP请求测试（直接连接）
        if ssl_ok:
            http_ok = test_http_request(url, use_proxy=False)
        else:
            http_ok = False
        
        # HTTP请求测试（代理连接）
        if has_proxies and "hackerone.com" in url:
            print("\n--- 使用代理再次测试 ---\n")
            test_http_request(url, use_proxy=True)
    
    print_separator()
    print("\n测试完成！根据测试结果，以下是可能的解决方案：")
    print("\n1. 如果所有测试都失败：")
    print("   - 检查您的网络连接")
    print("   - 确认防火墙/安全软件没有阻止连接")
    print("   - 尝试使用VPN或代理服务器")
    
    print("\n2. 如果只有HackerOne相关测试失败：")
    print("   - HackerOne可能限制了您的IP地址")
    print("   - 尝试使用不同的代理服务器")
    print("   - 稍后再试，可能是临时性限制")
    
    print("\n3. 如果使用代理时失败但直接连接成功：")
    print("   - 检查代理服务器配置是否正确")
    print("   - 尝试使用其他代理服务器")
    print("   - 确认代理服务器没有被HackerOne屏蔽")
    
    print("\n4. 关于JavaScript的问题：")
    print("   - 安装crawl4ai: pip install crawl4ai")
    print("   - 或安装Playwright: pip install playwright && playwright install")
    print("   - 这些工具能够执行JavaScript，更好地处理单页应用")
    
    print_separator()
    print("建议：使用run_crawl4ai.bat脚本运行爬虫，它会自动安装必要的依赖。")
    print("如果您有代理，请确保在proxies.txt文件中正确配置。")
    print_separator()

if __name__ == "__main__":
    import os
    main()