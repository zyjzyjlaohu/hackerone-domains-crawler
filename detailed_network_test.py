import requests
import socket
import ssl
import time
import urllib3
import http.client as http_client

# 启用详细日志记录
http_client.HTTPConnection.debuglevel = 1
urllib3.disable_warnings()

# 测试代理
proxy = '127.0.0.1:10808'
proxy_url_http = f'http://{proxy}'
proxy_url_https = f'https://{proxy}'
proxy_dict = {
    'http': proxy_url_http,
    'https': proxy_url_https
}

# 测试URL
test_urls = [
    ('HackerOne', 'https://www.hackerone.com'),
    ('Google', 'https://www.google.com'),
    ('GitHub', 'https://www.github.com'),
    ('Example.com', 'https://www.example.com'),
]

def log(message):
    """打印带时间戳的日志"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def test_dns_resolution(domain):
    """测试DNS解析"""
    try:
        log(f"测试DNS解析: {domain}")
        ip_address = socket.gethostbyname(domain)
        log(f"✓ DNS解析成功: {domain} -> {ip_address}")
        return ip_address
    except socket.gaierror as e:
        log(f"✗ DNS解析失败: {e}")
        return None

def test_tcp_connection(ip, port=443, timeout=10):
    """测试TCP连接"""
    try:
        log(f"测试TCP连接: {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start_time = time.time()
        result = sock.connect_ex((ip, port))
        elapsed_time = time.time() - start_time
        sock.close()
        
        if result == 0:
            log(f"✓ TCP连接成功: {ip}:{port} (响应时间: {elapsed_time:.2f}秒)")
            return True
        else:
            log(f"✗ TCP连接失败: 错误代码 {result}")
            return False
    except Exception as e:
        log(f"✗ TCP连接异常: {e}")
        return False

def test_ssl_connection(ip, domain, port=443, timeout=10):
    """测试SSL连接"""
    try:
        log(f"测试SSL连接: {domain} ({ip}:{port})")
        context = ssl.create_default_context()
        # 为了测试，我们可以暂时不验证SSL证书
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # 包装SSL连接
        ssock = context.wrap_socket(sock, server_hostname=domain)
        ssock.settimeout(timeout)
        
        # 获取SSL证书信息
        cert = ssock.getpeercert()
        log(f"✓ SSL连接成功: {domain}")
        log(f"   SSL版本: {ssock.version()}")
        ssock.close()
        return True
    except ssl.SSLError as e:
        log(f"✗ SSL连接错误: {e}")
        return False
    except Exception as e:
        log(f"✗ SSL连接异常: {e}")
        return False

def test_proxy_connectivity(proxy):
    """测试代理服务器连通性"""
    host, port = proxy.split(':')
    port = int(port)
    
    log(f"测试代理服务器连通性: {host}:{port}")
    
    # 测试代理服务器的TCP连接
    tcp_ok = test_tcp_connection(host, port)
    if not tcp_ok:
        log("✗ 无法连接到代理服务器")
        return False
    
    log("✓ 代理服务器TCP连接成功")
    return True

def test_http_with_proxy(url, proxy_dict):
    """使用代理测试HTTP请求"""
    try:
        log(f"使用代理测试HTTP请求: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        start_time = time.time()
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=20, allow_redirects=True)
        elapsed_time = time.time() - start_time
        
        log(f"✓ HTTP请求成功: 状态码 {response.status_code} (响应时间: {elapsed_time:.2f}秒)")
        log(f"   页面大小: {len(response.text)/1024:.2f} KB")
        
        # 验证页面内容
        if len(response.text) > 100:
            log(f"   页面内容预览: {response.text[:100]}...")
        
        return True
    except requests.exceptions.Timeout:
        log("✗ HTTP请求超时")
        return False
    except requests.exceptions.ConnectionError as e:
        log(f"✗ HTTP连接错误: {e}")
        # 打印更详细的错误信息
        if hasattr(e, 'args') and len(e.args) > 0:
            log(f"   详细错误: {e.args[0]}")
        return False
    except requests.exceptions.ProxyError as e:
        log(f"✗ HTTP代理错误: {e}")
        return False
    except Exception as e:
        log(f"✗ HTTP请求异常: {e}")
        return False

def main():
    log("====== 详细网络诊断工具 ======")
    
    # 1. 测试代理服务器连通性
    proxy_ok = test_proxy_connectivity(proxy)
    if not proxy_ok:
        log("代理服务器不可用，无法继续测试")
        return
    
    log("\n====== 开始测试各网站连接 ======")
    
    # 2. 对每个测试URL进行完整测试
    for site_name, url in test_urls:
        log(f"\n=== 测试 {site_name}: {url} ===")
        
        # 提取域名
        domain = url.split('//')[1].split('/')[0]
        log(f"域名: {domain}")
        
        # 测试DNS解析
        ip = test_dns_resolution(domain)
        if not ip:
            log(f"跳过后续测试: {site_name}")
            continue
        
        # 测试TCP连接
        tcp_ok = test_tcp_connection(ip)
        if not tcp_ok:
            log(f"跳过SSL测试: {site_name}")
        else:
            # 测试SSL连接
            test_ssl_connection(ip, domain)
        
        # 测试使用代理的HTTP请求
        http_ok = test_http_with_proxy(url, proxy_dict)
        
        log(f"\n{site_name} 测试结果: {'成功' if http_ok else '失败'}")
        log("=" * 60)
        
    # 3. 提供诊断结论和建议
    log("\n====== 诊断结论与建议 ======")
    log("1. 如果代理服务器TCP连接成功但HTTP请求失败，可能是:")
    log("   - 代理服务器配置问题")
    log("   - 代理服务器不支持HTTPS或特定网站")
    log("   - 网络防火墙限制")
    log("2. 解决方案:")
    log("   - 确认代理服务器配置正确")
    log("   - 尝试使用不同的代理协议 (HTTP/HTTPS/SOCKS5)")
    log("   - 检查防火墙和安全软件设置")
    log("   - 尝试使用crawl4ai或Playwright，它们可能有更好的代理支持")

if __name__ == "__main__":
    main()