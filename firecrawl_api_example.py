import os
import requests

"""
Firecrawl API 使用示例

此脚本展示了如何在 Python 代码中正确设置和使用 Firecrawl API 密钥

使用步骤：
1. 将你的 Firecrawl API 密钥设置到环境变量中，或者直接在此脚本中配置
2. 运行脚本：python firecrawl_api_example.py

注意：请保护好你的 API 密钥，不要将其泄露在公开代码或版本控制系统中
"""

# 方法 1: 通过环境变量设置 API 密钥（推荐）
# 你可以在系统环境变量中设置，或者在脚本中临时设置
# os.environ['FIRECRAWL_API_KEY'] = '你的 API 密钥'

# 方法 2: 直接在代码中设置 API 密钥（仅用于测试，生产环境不推荐）
# 已设置为你提供的 API 密钥
FIRECRAWL_API_KEY = 'fc-7821b71947ab4c61ace3d4a1513b30ab'

# Firecrawl API 基础 URL
BASE_URL = 'https://api.firecrawl.dev'

# 创建请求头
headers = {
    'Authorization': f'Bearer {FIRECRAWL_API_KEY}',
    'Content-Type': 'application/json'
}

def scrape_url(url):
    """使用 Firecrawl API 爬取单个网页"""
    print(f"\n正在爬取网页: {url}")
    try:
        # 根据最新文档，使用正确的端点版本和参数格式
        endpoint = f'{BASE_URL}/v0/scrape'
        payload = {
            'url': url,
            'params': {
                'formats': ['markdown']
            }
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # 如果请求失败，抛出异常
        
        result = response.json()
        
        # 保存爬取结果到文件
        output_file = f"scraped_{url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            # 检查响应格式并提取内容
            if 'data' in result and 'markdown' in result['data']:
                f.write(result['data']['markdown'])
            elif 'markdown' in result:
                f.write(result['markdown'])
            else:
                f.write(f"# 爬取结果\n\n无法从响应中提取markdown内容。原始响应: {result}")
        
        print(f"✅ 爬取成功!")
        print(f"📝 结果已保存到: {output_file}")
        
        # 打印内容摘要
        if 'data' in result and 'markdown' in result['data']:
            print("\n内容摘要:")
            summary = result['data']['markdown'][:300].strip() + ("..." if len(result['data']['markdown']) > 300 else "")
            print(summary)
        elif 'markdown' in result:
            print("\n内容摘要:")
            summary = result['markdown'][:300].strip() + ("..." if len(result['markdown']) > 300 else "")
            print(summary)
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if response.status_code == 401:
            print("   请检查你的 API 密钥是否正确")
        elif response.status_code == 402:
            print("   余额不足，需要支付")
        elif response.status_code == 429:
            print("   请求过于频繁，请稍后再试")
        elif response.status_code == 500:
            print("   Firecrawl 服务器错误")
    except Exception as e:
        print(f"❌ 爬取失败: {e}")
        print(f"   错误详情: {str(e)}")

def search_web(query, limit=5):
    """使用 Firecrawl API 搜索网页"""
    print(f"\n正在搜索: '{query}' (限制 {limit} 个结果)")
    try:
        # 使用正确的搜索端点
        endpoint = f'{BASE_URL}/v0/search'
        payload = {
            'query': query,
            'limit': limit
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        results = response.json()
        
        # 保存搜索结果到文件
        output_file = f"search_results_{query.replace(' ', '_')[:50]}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"搜索查询: {query}\n")
            
            # 检查结果格式
            if 'results' in results:
                result_list = results['results']
                f.write(f"找到 {len(result_list)} 个结果\n\n")
                
                for i, result in enumerate(result_list, 1):
                    title = result.get('title', '无标题')
                    url = result.get('url', '无URL')
                    snippet = result.get('snippet', '无摘要')
                    
                    # 打印到控制台
                    print(f"{i}. {title} - {url}")
                    print(f"   摘要: {snippet[:100]}...")
                    
                    # 保存到文件
                    f.write(f"{i}. 标题: {title}\n")
                    f.write(f"   URL: {url}\n")
                    f.write(f"   摘要: {snippet}\n\n")
            else:
                f.write(f"无法从响应中提取搜索结果。原始响应: {results}")
                print("⚠️ 无法从响应中提取搜索结果")
        
        print(f"✅ 搜索成功!")
        print(f"📝 结果已保存到: {output_file}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP 错误: {e}")
        if response.status_code == 401:
            print("   请检查你的 API 密钥是否正确")
        elif response.status_code == 402:
            print("   余额不足，需要支付")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        print(f"   错误详情: {str(e)}")

if __name__ == "__main__":
    print("🔥 Firecrawl API 使用示例")
    print("====================")
    
    # 检查 API 密钥是否已设置
    if not FIRECRAWL_API_KEY or FIRECRAWL_API_KEY == '你的 API 密钥':
        print("\n⚠️ 警告: API 密钥未设置!")
        print("请在代码中设置你的 Firecrawl API 密钥，格式应该是 'fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'")
        print("你可以在 https://firecrawl.dev 获取 API 密钥")
        exit(1)
    
    # 示例用法
    print("\n🚀 开始演示 Firecrawl API 功能...")
    
    # 爬取单个网页示例
    scrape_url("https://example.com")
    
    # 搜索网页示例
    search_web("最新AI研究进展 2025", limit=5)
    
    print("\n🎉 演示完成!")
    print("📚 你可以查看生成的文件获取完整结果")
    print("💡 提示: 在实际应用中，建议将 API 密钥存储在环境变量或配置文件中，而不是直接硬编码在代码里")