import requests
import time
import sys
import os

# 配置日志
def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

# 从文件加载代理
def load_proxies(file_path):
    proxies = []
    try:
        if not os.path.exists(file_path):
            log(f"错误: 代理文件 {file_path} 不存在")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # 确保代理有正确的协议前缀
                    if not line.startswith('http://') and not line.startswith('https://'):
                        proxy = f'http://{line}'
                    else:
                        proxy = line
                    proxies.append((line_num, proxy))
        
        log(f"从文件加载了 {len(proxies)} 个代理")
        return proxies
    except Exception as e:
        log(f"加载代理文件时出错: {e}")
        return []

# 测试单个代理
def test_proxy(proxy_info):
    line_num, proxy = proxy_info
    log(f"测试第 {line_num} 行的代理: {proxy}")
    
    proxy_dict = {
        'http': proxy,
        'https': proxy
    }
    
    try:
        # 测试连接到HackerOne
        start_time = time.time()
        response = requests.get('https://www.hackerone.com', proxies=proxy_dict, timeout=15)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            log(f"✓ 代理 {proxy} 测试成功 (状态码: {response.status_code}, 响应时间: {elapsed_time:.2f}秒)")
            log(f"   页面大小: {len(response.content)/1024:.2f} KB")
            return True
        else:
            log(f"✗ 代理 {proxy} 测试失败: 状态码 {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        log(f"✗ 代理 {proxy} 测试失败: 连接超时")
        return False
    except requests.exceptions.ConnectionError:
        log(f"✗ 代理 {proxy} 测试失败: 连接错误")
        return False
    except Exception as e:
        log(f"✗ 代理 {proxy} 测试失败: {e}")
        return False

# 主函数
def main():
    proxy_file = "proxies.txt"
    
    log("====== 代理测试工具 ======")
    log(f"测试文件: {proxy_file}")
    
    # 加载代理
    proxies = load_proxies(proxy_file)
    
    if not proxies:
        log("没有可测试的代理")
        sys.exit(1)
    
    # 测试所有代理
    successful_proxies = 0
    for proxy_info in proxies:
        if test_proxy(proxy_info):
            successful_proxies += 1
        log("------------------------")
        time.sleep(1)  # 添加延迟，避免过快测试
    
    # 显示结果摘要
    log("====== 测试结果摘要 ======")
    log(f"总共测试: {len(proxies)} 个代理")
    log(f"成功: {successful_proxies} 个代理")
    log(f"失败: {len(proxies) - successful_proxies} 个代理")
    
    if successful_proxies == 0:
        log("⚠️  警告: 所有代理都测试失败")
        log("请检查以下几点:")
        log("1. 代理服务器是否正在运行")
        log("2. 代理格式是否正确")
        log("3. 网络连接是否正常")
        log("4. 是否有防火墙或安全软件阻止连接")
        sys.exit(1)

if __name__ == "__main__":
    main()