import requests
import time
from bs4 import BeautifulSoup
import re
import json
import csv
import os

# 配置日志
def log(message, level='INFO'):
    print(f"[{time.strftime('%H:%M:%S')}] [{level}] {message}")

# 目标URL
base_url = 'https://www.hackerone.com'
opportunities_url = f'{base_url}/opportunities/all'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': base_url,
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def save_to_csv(domains, filename='hackerone_domains_direct.csv'):
    """将域名列表保存到CSV文件"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['domain', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for domain, url in domains.items():
                writer.writerow({'domain': domain, 'url': url})
        log(f"成功保存 {len(domains)} 个域名到 {filename}")
    except Exception as e:
        log(f"保存CSV文件失败: {e}", 'ERROR')

def extract_domains_from_html(html, url):
    """从HTML中提取域名信息"""
    if not html:
        log("HTML内容为空，无法提取域名", 'ERROR')
        return {}
    
    domains = {}
    soup = BeautifulSoup(html, 'html.parser')
    
    # 检查是否需要JavaScript
    if 'js-disabled' in html and 'It looks like your JavaScript is disabled' in html:
        log("警告: 页面需要JavaScript才能正常显示内容", 'WARNING')
    
    # 方法1: 查找JSON数据
    script_tags = soup.find_all('script', type='application/json')
    for script in script_tags:
        try:
            script_content = script.string
            if script_content and ('opportunities' in script_content or 'programs' in script_content):
                # 尝试解析JSON
                try:
                    data = json.loads(script_content)
                    # 搜索可能包含域名的部分
                    log("找到包含项目数据的JSON脚本")
                    # 这里简化处理，实际需要根据JSON结构调整
                except json.JSONDecodeError:
                    # 可能不是完整的JSON，尝试其他方法
                    pass
        except Exception as e:
            log(f"解析script标签时出错: {e}", 'ERROR')
    
    # 方法2: 查找链接和域名模式
    # 查找所有可能的项目链接
    program_links = soup.find_all('a', href=re.compile(r'/programs/'))
    log(f"找到 {len(program_links)} 个可能的项目链接")
    
    # 提取域名模式
    domain_pattern = r'[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    potential_domains = set(re.findall(domain_pattern, html))
    
    # 过滤掉HackerOne自己的域名和无效域名
    filtered_domains = {}
    for domain in potential_domains:
        # 排除HackerOne域名和常见服务域名
        if ('hackerone.com' not in domain and 
            'cloudflare.com' not in domain and 
            'google.com' not in domain and 
            'github.com' not in domain and 
            '.' in domain and 
            len(domain) > 3):
            # 添加到结果中，URL设为推测的项目页面
            filtered_domains[domain] = f"{base_url}/programs/{domain.split('.')[0]}"
            
    log(f"过滤后得到 {len(filtered_domains)} 个可能的第三方域名")
    
    # 保存页面内容用于调试
    with open('hackerone_direct_crawl.html', 'w', encoding='utf-8') as f:
        f.write(html[:50000])  # 只保存前50000字符
    log("页面内容已保存到 hackerone_direct_crawl.html")
    
    return filtered_domains

def crawl_hackerone():
    """直接爬取HackerOne众测页面"""
    log("开始直接爬取HackerOne众测页面")
    
    try:
        # 发送请求
        log(f"正在请求: {opportunities_url}")
        response = requests.get(opportunities_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        log(f"请求成功，状态码: {response.status_code}")
        log(f"页面大小: {len(response.text)/1024:.2f} KB")
        
        # 提取域名
        domains = extract_domains_from_html(response.text, opportunities_url)
        
        # 保存结果
        if domains:
            save_to_csv(domains)
        else:
            log("未找到任何众测域名", 'WARNING')
            # 创建空的CSV文件，避免用户困惑
            save_to_csv({'no-domains-found': 'https://www.hackerone.com/opportunities/all'})
        
    except requests.exceptions.Timeout:
        log("请求超时", 'ERROR')
    except requests.exceptions.ConnectionError:
        log("连接错误，请检查网络连接或代理设置", 'ERROR')
        log("提示: 可能需要使用VPN或代理服务器访问HackerOne", 'WARNING')
    except requests.exceptions.HTTPError as e:
        log(f"HTTP错误: {e}", 'ERROR')
    except Exception as e:
        log(f"爬取过程中出错: {e}", 'ERROR')
    
    log("直接爬取完成")

def main():
    print("====== HackerOne直接爬取工具 ======")
    print("此工具尝试直接爬取HackerOne的众测页面并提取域名")
    print(f"目标URL: {opportunities_url}")
    print("=" * 60)
    
    # 运行爬取
    crawl_hackerone()
    
    print("=" * 60)
    print("爬取完成，请查看结果文件: hackerone_domains_direct.csv")
    print("如果未找到域名，请检查网络连接或尝试使用代理")

if __name__ == "__main__":
    main()