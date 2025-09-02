import requests
import time
import json
from bs4 import BeautifulSoup

# 尝试导入crawl4ai
try:
    from crawl4ai import WebCrawler
    print("✓ 成功导入crawl4ai库")
    crawl4ai_available = True
except ImportError:
    print("✗ 未安装crawl4ai，请运行 'pip install crawl4ai'")
    crawl4ai_available = False

# 配置代理
proxy = {'http': 'http://127.0.0.1:10808', 'https': 'https://127.0.0.1:10808'}

# 测试URL
test_urls = [
    'https://www.hackerone.com/opportunities/all',
    'https://www.hackerone.com/bug-bounty-programs',
    'https://www.hackerone.com/programs/github',
    # 测试一些常见网站以验证代理是否正常工作
    'https://www.google.com',
    'https://www.github.com',
]

# 简单的页面解析函数
def parse_domains(html, url):
    """从页面HTML中解析域名"""
    if not html:
        print(f"✗ 页面内容为空: {url}")
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    domains = set()
    
    # 检查是否需要JavaScript
    if 'js-disabled' in html and 'It looks like your JavaScript is disabled' in html:
        print("⚠️  检测到页面需要JavaScript")
        
    # 尝试从script标签中提取JSON数据
    script_tags = soup.find_all('script', type='application/json')
    for script in script_tags:
        try:
            script_content = script.string
            if script_content:
                # 简单检查是否包含项目数据
                if 'opportunities' in script_content or 'programs' in script_content:
                    print(f"✓ 找到可能包含项目数据的script标签")
                    # 保存部分内容用于检查
                    with open('script_content_sample.txt', 'w', encoding='utf-8') as f:
                        f.write(script_content[:5000])  # 只保存前5000字符
                    print("✓ script内容已保存到 script_content_sample.txt")
                    break
        except Exception as e:
            print(f"解析script标签时出错: {e}")
    
    # 尝试查找域名相关的元素
    domain_elements = soup.find_all('code')
    if domain_elements:
        print(f"✓ 找到 {len(domain_elements)} 个code标签")
        for elem in domain_elements[:10]:  # 只显示前10个
            text = elem.get_text(strip=True)
            if '.' in text and len(text) > 3:
                print(f"   可能的域名: {text}")
    
    # 查找data-qa属性为target-domains的元素
    target_domains_section = soup.find('div', {'data-qa': 'target-domains'})
    if target_domains_section:
        print("✓ 找到data-qa='target-domains'的元素")
        code_elements = target_domains_section.find_all('code')
        for code in code_elements:
            domain = code.get_text(strip=True)
            if domain and '.' in domain:
                domains.add(domain)
                print(f"   + 提取到域名: {domain}")
    else:
        print("✗ 未找到data-qa='target-domains'的元素")
    
    # 查找class为program-scope__target-domains的元素
    program_scope_section = soup.find('div', class_='program-scope__target-domains')
    if program_scope_section:
        print("✓ 找到class='program-scope__target-domains'的元素")
        code_elements = program_scope_section.find_all('code')
        for code in code_elements:
            domain = code.get_text(strip=True)
            if domain and '.' in domain:
                domains.add(domain)
                print(f"   + 提取到域名: {domain}")
    else:
        print("✗ 未找到class='program-scope__target-domains'的元素")
    
    # 保存页面内容用于调试
    filename = f'page_{url.split("/")[-1]}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html[:20000])  # 只保存前20000字符
    print(f"✓ 页面内容已保存到 {filename}")
    
    return list(domains)

# 使用crawl4ai爬取页面
def crawl_with_crawl4ai(url):
    """使用crawl4ai爬取页面"""
    if not crawl4ai_available:
        return None
    
    try:
        print(f"\n====== 开始使用crawl4ai爬取: {url} ======")
        # 创建爬虫实例
        config = {
            "verbose": True,
            "headless": True,
            "async_mode": False,
            "auto_close": False,
            "proxy": proxy['http'] if proxy else None,
        }
        
        crawler = WebCrawler(config=config)
        
        # 爬取页面
        result = crawler.crawl(
            url=url,
            wait_until="networkidle",
            timeout=60000,
            # 对于列表页面，可能需要滚动加载
            actions=[
                {"type": "scroll", "direction": "down", "times": 3}
            ] if 'opportunities' in url else None
        )
        
        # 关闭爬虫
        crawler.close()
        
        if result and hasattr(result, 'markdown'):
            print(f"✓ crawl4ai爬取成功，页面大小: {len(result.markdown)} 字符")
            return result.markdown
        else:
            print("✗ crawl4ai爬取失败或返回无效结果")
            if result and hasattr(result, 'error'):
                print(f"   错误信息: {result.error}")
            return None
    except Exception as e:
        print(f"✗ crawl4ai爬取过程中出错: {e}")
        return None

# 使用基本HTTP请求爬取页面
def crawl_with_requests(url):
    """使用基本HTTP请求爬取页面"""
    print(f"\n====== 开始使用requests爬取: {url} ======")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, proxies=proxy if proxy else None, timeout=30)
        response.raise_for_status()
        
        print(f"✓ requests爬取成功，状态码: {response.status_code}，页面大小: {len(response.text)} 字符")
        return response.text
    except requests.exceptions.Timeout:
        print("✗ 请求超时")
    except requests.exceptions.ConnectionError:
        print("✗ 连接错误")
    except Exception as e:
        print(f"✗ requests爬取过程中出错: {e}")
    return None

# 主函数
def main():
    print("====== 简单爬取测试工具 ======")
    print(f"使用代理: {proxy if proxy else '不使用代理'}")
    
    for url in test_urls:
        # 先尝试使用crawl4ai
        html = crawl_with_crawl4ai(url)
        
        # 如果crawl4ai不可用或失败，使用requests
        if not html:
            html = crawl_with_requests(url)
        
        # 解析页面中的域名
        if html:
            domains = parse_domains(html, url)
            print(f"从 {url} 提取到 {len(domains)} 个域名")
        else:
            print(f"无法获取 {url} 的页面内容")
        
        print("=" * 60)
        time.sleep(2)  # 添加延迟

if __name__ == "__main__":
    main()