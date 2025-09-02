import csv
import os
from mcp.config.usrlocalmcp.Firecrawl import firecrawl_map

"""使用MCP的Firecrawl工具直接抓取hackerone众测平台域名"""

# 输出文件路径
output_file = "hackerone_domains_mcp.csv"

print("开始使用MCP的Firecrawl工具抓取hackerone众测平台域名...")

try:
    # 调用Firecrawl的map功能获取网站的所有链接
    print("调用Firecrawl map功能...")
    result = firecrawl_map(
        url="https://hackerone.com/opportunities/all",
        search="bug bounty",  # 添加搜索关键词以过滤相关内容
        includeSubdomains=False,  # 不包括子域名
        ignoreQueryParameters=True  # 忽略查询参数
    )
    
    # 检查结果
    if hasattr(result, 'links') and result.links:
        print(f"成功获取到 {len(result.links)} 个链接")
        
        # 提取域名
        domains = set()
        
        for link in result.links:
            if hasattr(link, 'url') and link.url:
                url = link.url
                # 简单的域名提取逻辑
                if url.startswith('http'):
                    domain_parts = url.split('/')[2]
                    # 过滤掉hackerone自身的域名
                    if 'hackerone.com' not in domain_parts:
                        domains.add(domain_parts)
        
        print(f"成功提取到 {len(domains)} 个第三方域名")
        
        # 检查输出文件是否存在，如果不存在则创建并写入表头
        file_exists = os.path.isfile(output_file)
        
        # 写入CSV文件
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 如果文件不存在，写入表头
            if not file_exists:
                writer.writerow(['domain'])
            # 写入域名
            for domain in sorted(domains):
                writer.writerow([domain])
        
        print(f"域名已成功保存到 {output_file}")
        
    else:
        print("未能获取到任何链接")
        
        # 作为备选，创建一个包含示例域名的文件
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['domain'])
            # 添加一些示例域名
            example_domains = [
                "example.com",
                "test.com",
                "target.example.org",
                "vulnerable-app.test"
            ]
            for domain in example_domains:
                writer.writerow([domain])
        
        print(f"已创建包含示例域名的文件: {output_file}")
        print("注意：这是一个示例文件，实际使用时需要正确配置MCP的Firecrawl功能")
        
except Exception as e:
    print(f"使用Firecrawl过程中发生错误: {str(e)}")
    
    # 如果出错，创建一个包含错误信息的文件
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['domain'])
        writer.writerow([f"Error: {str(e)}"])
    
    print(f"已创建错误日志文件: {output_file}")

print("任务完成")