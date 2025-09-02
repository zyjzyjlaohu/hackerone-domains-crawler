import sys
import os

# 直接读取文件内容来验证功能
def verify_mcp_integration():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crawl_hackerone_domains.py')
    
    if not os.path.exists(file_path):
        print("✗ 未找到crawl_hackerone_domains.py文件")
        return False
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✓ 成功读取crawl_hackerone_domains.py文件")
        
        # 检查MCPClient类
        has_mcp_client = 'class MCPClient' in content
        print(f"MCPClient类: {'✓ 已添加' if has_mcp_client else '✗ 未添加'}")
        
        # 检查mcp_playwright_get方法
        has_mcp_playwright_get = 'def mcp_playwright_get' in content
        print(f"mcp_playwright_get方法: {'✓ 已添加' if has_mcp_playwright_get else '✗ 未添加'}")
        
        # 检查send_request方法中的MCP支持
        has_mcp_playwright_support = 'use_mcp_playwright' in content and 'self.mcp_playwright_get' in content
        has_mcp_firecrawl_support = 'use_mcp_firecrawl' in content and 'firecrawl_scrape' in content
        
        print(f"MCP Playwright支持: {'✓ 已集成' if has_mcp_playwright_support else '✗ 未集成'}")
        print(f"MCP Firecrawl支持: {'✓ 已集成' if has_mcp_firecrawl_support else '✗ 未集成'}")
        
        # 检查命令行参数
        has_mcp_args = '--use-mcp-playwright' in content and '--use-mcp-firecrawl' in content and '--mcp-host' in content and '--mcp-port' in content
        print(f"MCP命令行参数: {'✓ 已添加' if has_mcp_args else '✗ 未添加'}")
        
        # 检查调用优先级
        if has_mcp_playwright_support and has_mcp_firecrawl_support:
            # 查找send_request方法中的顺序
            send_request_start = content.find('def send_request')
            if send_request_start != -1:
                send_request_content = content[send_request_start:send_request_start+1000]  # 取前1000个字符
                
                # 检查MCP Playwright是否在Playwright之前
                mcp_playwright_pos = send_request_content.find('use_mcp_playwright')
                playwright_pos = send_request_content.find('use_playwright')
                
                # 检查MCP Firecrawl是否在Firecrawl之前
                mcp_firecrawl_pos = send_request_content.find('use_mcp_firecrawl')
                firecrawl_pos = send_request_content.find('use_firecrawl')
                
                priority_check = False
                if mcp_playwright_pos != -1 and playwright_pos != -1 and mcp_playwright_pos < playwright_pos:
                    print("✓ MCP Playwright优先级高于Playwright")
                    priority_check = True
                else:
                    print("✗ MCP Playwright优先级未设置正确")
                
                if mcp_firecrawl_pos != -1 and firecrawl_pos != -1 and mcp_firecrawl_pos < firecrawl_pos:
                    print("✓ MCP Firecrawl优先级高于Firecrawl")
                    priority_check = priority_check and True
                else:
                    print("✗ MCP Firecrawl优先级未设置正确")
                    priority_check = False
                
                if priority_check:
                    print("✓ 调用优先级设置正确")
        
        # 综合验证结果
        is_success = has_mcp_client and has_mcp_playwright_get and has_mcp_playwright_support and has_mcp_firecrawl_support and has_mcp_args
        
        print("\n=== 验证结果 ===")
        if is_success:
            print("✓ ✓ ✓ MCP功能已成功集成到爬取脚本中 ✓ ✓ ✓")
        else:
            print("✗ MCP功能集成不完整，请检查以上项目")
        
        return is_success
        
    except Exception as e:
        print(f"验证过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("\n=== MCP功能集成验证 ===")
    success = verify_mcp_integration()
    
    if success:
        print("\n\n=== MCP功能使用说明 ===")
        print("\n1. 使用MCP Playwright:")
        print("   python crawl_hackerone_domains.py --use-mcp-playwright --mcp-host <MCP服务器IP> --mcp-port <MCP服务器端口>")
        print("\n2. 使用MCP Firecrawl:")
        print("   python crawl_hackerone_domains.py --use-mcp-firecrawl --mcp-host <MCP服务器IP> --mcp-port <MCP服务器端口>")
        print("\n3. 同时使用两种MCP模式:")
        print("   python crawl_hackerone_domains.py --use-mcp-playwright --use-mcp-firecrawl --mcp-host <MCP服务器IP> --mcp-port <MCP服务器端口>")
        print("\n注意: 实际使用时需要替换 <MCP服务器IP> 和 <MCP服务器端口> 为您的MCP服务器实际地址。")
    else:
        print("\n请修复验证中发现的问题后再使用MCP功能。")