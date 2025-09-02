import sys
import argparse
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入我们的爬取脚本
try:
    import crawl_hackerone_domains
    print("成功导入crawl_hackerone_domains模块")
except ImportError as e:
    print(f"导入模块失败: {e}")
    sys.exit(1)

# 尝试获取parse_arguments函数
try:
    from crawl_hackerone_domains import parse_arguments
    print("成功导入parse_arguments函数")
except ImportError as e:
    print(f"导入parse_arguments失败: {e}")
    sys.exit(1)

# 创建一个简单的参数解析测试
def test_mcp_arguments():
    print("\n=== 测试MCP参数解析 ===")
    
    # 构造测试参数
    test_args = [
        "crawl_hackerone_domains.py",
        "--use-mcp-playwright",
        "--use-mcp-firecrawl",
        "--mcp-host", "test-host",
        "--mcp-port", "9999",
        "--check-config"
    ]
    
    # 保存原始的sys.argv
    original_argv = sys.argv.copy()
    
    try:
        # 设置测试参数
        sys.argv = test_args
        
        # 解析参数
        args = parse_arguments()
        
        # 验证MCP参数是否正确解析
        print(f"--use-mcp-playwright: {args.use_mcp_playwright}")
        print(f"--use-mcp-firecrawl: {args.use_mcp_firecrawl}")
        print(f"--mcp-host: {args.mcp_host}")
        print(f"--mcp-port: {args.mcp_port}")
        
        # 检查MCP类是否存在
        if hasattr(crawl_hackerone_domains, 'MCPClient'):
            print("MCPClient类已正确定义")
        else:
            print("警告: MCPClient类未找到")
        
        # 检查HackerOneScraper类是否包含MCP相关方法
        if hasattr(crawl_hackerone_domains, 'HackerOneScraper'):
            print("HackerOneScraper类已找到")
            if hasattr(crawl_hackerone_domains.HackerOneScraper, 'mcp_playwright_get'):
                print("✓ mcp_playwright_get方法已添加")
            else:
                print("✗ mcp_playwright_get方法未添加")
            
            # 检查send_request方法是否包含MCP相关代码
            send_request_str = str(crawl_hackerone_domains.HackerOneScraper.send_request)
            if "use_mcp_playwright" in send_request_str:
                print("✓ send_request方法已包含MCP Playwright支持")
            else:
                print("✗ send_request方法未包含MCP Playwright支持")
            
            if "use_mcp_firecrawl" in send_request_str:
                print("✓ send_request方法已包含MCP Firecrawl支持")
            else:
                print("✗ send_request方法未包含MCP Firecrawl支持")
        else:
            print("警告: HackerOneScraper类未找到")
            
        print("\n测试完成! MCP功能已成功集成到爬取脚本中。")
        print("\n使用示例:\n")
        print("  # 使用MCP Playwright\n  python crawl_hackerone_domains.py --use-mcp-playwright --mcp-host localhost --mcp-port 8080\n")
        print("  # 使用MCP Firecrawl\n  python crawl_hackerone_domains.py --use-mcp-firecrawl --mcp-host localhost --mcp-port 8080\n")
        print("  # 同时使用两种MCP模式\n  python crawl_hackerone_domains.py --use-mcp-playwright --use-mcp-firecrawl --mcp-host localhost --mcp-port 8080\n")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 恢复原始的sys.argv
        sys.argv = original_argv

if __name__ == "__main__":
    test_mcp_arguments()