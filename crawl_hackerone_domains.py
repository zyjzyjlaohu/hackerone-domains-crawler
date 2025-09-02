from bs4 import BeautifulSoup
import time
import random
import csv
import argparse
import os
from urllib.parse import urljoin
import logging
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import http.client

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入Playwright
playwright_available = False
try:
    from playwright.sync_api import sync_playwright
    playwright_available = True
except ImportError:
    logger.warning("未安装Playwright，无法使用Playwright模拟登录功能。请运行 'pip install playwright' 安装")

# 设置请求头，模拟浏览器
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36'
]

# 设置请求延迟范围
REQUEST_DELAY = (1, 3)  # 随机延迟范围（秒）

# 代理列表格式: [{'http': 'http://proxy:port', 'https': 'https://proxy:port'}, ...]
PROXIES = [
    # 添加你的代理服务器，例如:
    # {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080'},
]

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
class HackerOneScraper:
    def __init__(self, output_file='hackerone_domains.csv', use_proxy=False, proxy_list=None, request_delay=(1, 3), max_retries=3, backoff_factor=0.3,
                 progress_interval=10, log_level=logging.INFO, driver_path=None, chrome_path=None,
                 use_firecrawl=False, firecrawl_api_key=None, use_playwright=False,
                 playwright_login=False, username=None, password=None, use_mcp_playwright=False,
                 use_mcp_firecrawl=False, mcp_host='localhost', mcp_port=8000):
        self.base_url = 'https://hackerone.com'
        # 更改为正确的众测项目URL
        self.programs_url = f'{self.base_url}/opportunities/all'
        self.output_file = output_file
        self.domains = set()  # 使用集合避免重复
        self.domain_url_map = {}  # 存储域名和URL的对应关系
        # 添加一个测试条目以验证功能
        self.domain_url_map['example.com'] = 'https://www.example.com'
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list if proxy_list else PROXIES
        self.proxy_lock = threading.Lock()  # 用于保护代理列表的线程锁
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.progress_interval = progress_interval
        self.log_level = log_level
        self.driver_path = driver_path
        self.chrome_path = chrome_path
        self.use_firecrawl = use_firecrawl
        self.firecrawl_api_key = firecrawl_api_key
        # 新增Playwright相关参数
        self.use_playwright = use_playwright and playwright_available
        self.playwright_login = playwright_login and self.use_playwright
        self.username = username
        self.password = password
        # Playwright实例
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        self.cookies = None

        # 检查Firecrawl配置
        if self.use_firecrawl:
            self.logger.info("Firecrawl模式已启用")
            if self.firecrawl_api_key:
                self.logger.info("Firecrawl API密钥已提供")
            else:
                self.logger.warning("未提供Firecrawl API密钥，将使用基本的HTTP请求作为替代")
        # 检查Playwright配置
        if self.use_playwright:
            self.logger.info("Playwright模式已启用")
            if self.playwright_login:
                self.logger.info("将使用Playwright进行模拟登录")
        # 尝试从环境变量获取ChromeDriver路径
        if not self.driver_path:
            import os
            self.driver_path = os.environ.get('CHROMEDRIVER_PATH')
        # 尝试从环境变量获取Chrome路径
        if not self.chrome_path:
            import os
            self.chrome_path = os.environ.get('CHROME_PATH')
        self.driver = None  # WebDriver实例
        # 更新日志级别
        self.logger = logger  # 先将全局logger赋值给实例属性
        self.logger.setLevel(self.log_level)  # 然后使用实例属性设置日志级别
        self.logger.info("初始化HackerOneScraper")
        # 优先使用ChromeDriver，因为它能处理JavaScript渲染
        self.logger.info("提示：HackerOne是一个需要JavaScript的单页应用，建议使用ChromeDriver或Playwright模式")
        
        # 初始化MCP客户端
        self.use_mcp_playwright = use_mcp_playwright
        self.use_mcp_firecrawl = use_mcp_firecrawl
        self.mcp_host = mcp_host
        self.mcp_port = mcp_port
        
        if self.use_mcp_playwright:
            self.logger.info("MCP Playwright模式已启用")
            self.mcp_playwright = MCPClient('mcp.config.usrlocalmcp.Playwright', self.mcp_host, self.mcp_port)
        else:
            self.mcp_playwright = None
            
        if self.use_mcp_firecrawl:
            self.logger.info("MCP Firecrawl模式已启用")
            self.mcp_firecrawl = MCPClient('mcp.config.usrlocalmcp.Firecrawl', self.mcp_host, self.mcp_port)
        else:
            self.mcp_firecrawl = None
        
        # 设置Playwright（如果启用）
        if self.use_playwright:
            self.setup_playwright()
        # 设置Selenium WebDriver（如果未启用Playwright）
        elif not self.use_firecrawl:
            try:
                self.driver = self.setup_driver()
                self.logger.info("WebDriver初始化成功")
            except Exception as e:
                self.logger.error(f"WebDriver初始化失败: {e}")
                raise

    def get_random_headers(self):
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.base_url,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def setup_playwright(self):
        """设置Playwright浏览器"""
        if not playwright_available:
            self.logger.error("Playwright不可用，请先安装Playwright")
            return
        
        try:
            self.logger.info("初始化Playwright...")
            self.playwright = sync_playwright().start()
            
            # 创建浏览器实例
            # 可以根据需要选择不同的浏览器：chromium, firefox, webkit
            self.browser = self.playwright.chromium.launch(
                headless=False,  # 非无头模式，方便查看登录过程
                args=[
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    f'--user-agent={random.choice(USER_AGENTS)}',
                    '--ignore-certificate-errors',  # 忽略SSL证书错误
                    '--ignore-urlfetcher-cert-requests'  # 忽略URL请求的证书验证
                ]
            )
            
            # 创建新的浏览器上下文
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # 创建新的页面
            self.page = self.context.new_page()
            
            # 如果需要登录
            if self.playwright_login and self.username and self.password:
                self.playwright_login_hackerone()
            
            self.logger.info("Playwright初始化成功")
        except Exception as e:
            self.logger.error(f"Playwright初始化失败: {e}")
            self.close_playwright()
            raise

    def playwright_login_hackerone(self):
        """使用Playwright登录HackerOne"""
        if not self.page:
            self.logger.error("Playwright页面未初始化")
            return
        
        try:
            self.logger.info("准备登录HackerOne...")
            
            # 导航到登录页面
            self.page.goto(f"{self.base_url}/login", wait_until="networkidle")
            self.logger.info("已加载登录页面")
            
            # 等待登录表单加载
            self.page.wait_for_selector("input[name='username']", timeout=10000)
            self.logger.info("登录表单已加载")
            
            # 输入用户名和密码
            self.page.fill("input[name='username']", self.username)
            self.page.fill("input[name='password']", self.password)
            self.logger.info("已输入用户名和密码")
            
            # 点击登录按钮
            self.page.click("button[type='submit']")
            self.logger.info("已点击登录按钮")
            
            # 等待登录成功并验证
            try:
                # 等待登录成功的指示
                self.page.wait_for_selector("[data-ember-action][data-ember-action-12]", timeout=15000)  # 这个选择器可能需要根据实际情况调整
                self.logger.info("登录成功")
                
                # 保存Cookie，以便后续请求使用
                self.cookies = self.context.cookies()
                self.logger.info(f"已保存{len(self.cookies)}个Cookie")
                
                # 如果启用了Firecrawl，可以使用这些Cookie
                if self.use_firecrawl:
                    self.logger.info("将Playwright登录的Cookie提供给Firecrawl使用")
                    # 在send_request方法中会使用这些Cookie
            except Exception as e:
                self.logger.error(f"登录验证失败: {e}")
                # 保存页面内容以便调试
                debug_file = 'login_debug.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.page.content())
                self.logger.info(f"登录页面内容已保存到 {debug_file}")
                raise
            
        except Exception as e:
            self.logger.error(f"登录过程出错: {e}")
            # 保存页面内容以便调试
            debug_file = 'login_error.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                if self.page:
                    f.write(self.page.content())
            self.logger.info(f"错误页面内容已保存到 {debug_file}")
            raise

    def mcp_playwright_get(self, url, max_retries=3):
        """使用MCP Playwright获取页面内容"""
        if not self.use_mcp_playwright or not hasattr(self, 'mcp_playwright') or not self.mcp_playwright:
            self.logger.error("MCP Playwright未启用或未初始化")
            return None
        
        retries = 0
        while retries < max_retries:
            try:
                self.logger.info(f"使用MCP Playwright访问: {url}")
                
                # 使用MCP调用Playwright
                result = self.mcp_playwright.call(
                    "navigate_and_get_content",
                    {
                        "url": url,
                        "wait_until": "networkidle",
                        "timeout": 60000
                    }
                )
                
                if result and "content" in result:
                    self.logger.info(f"MCP Playwright获取页面成功: {url}")
                    
                    # 保存页面内容用于调试
                    if '/opportunities/all' in url or '/bug-bounty-programs' in url:
                        debug_file = 'hackerone_mcp_playwright.html'
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(result["content"])
                        self.logger.info(f"页面内容已保存到 {debug_file}")
                    
                    # 添加随机延迟
                    delay = random.uniform(*self.request_delay)
                    self.logger.info(f"添加随机延迟: {delay:.2f}秒")
                    time.sleep(delay)
                    
                    return result["content"]
                else:
                        self.logger.error(f"MCP Playwright返回无效结果: {url}")
            except Exception as e:
                retries += 1
                self.logger.error(f"MCP Playwright请求出错 (第 {retries}/{max_retries} 次尝试): {url}, 错误: {e}")
                
                # 如果达到最大重试次数，返回None
                if retries >= max_retries:
                    self.logger.error(f"达到最大重试次数，请求失败: {url}")
                    return None
                
                # 等待一段时间后重试
                wait_time = random.uniform(2, 5) * retries  # 指数退避
                self.logger.info(f"{wait_time:.2f}秒后重试...")
                time.sleep(wait_time)
        
        return None
        
    def playwright_get(self, url, max_retries=3):
        """使用Playwright获取页面内容"""
        if not self.page:
            self.logger.error("Playwright页面未初始化")
            return None
        
        retries = 0
        while retries < max_retries:
            try:
                self.logger.info(f"使用Playwright访问: {url}")
                
                # 导航到URL
                self.page.goto(url, wait_until="networkidle")
                
                # 等待页面加载完成
                wait_time = random.uniform(3, 8)
                self.logger.info(f"等待{wait_time:.2f}秒确保内容加载完成")
                time.sleep(wait_time)
                
                # 如果是opportunities页面，确保内容加载
                if '/opportunities/all' in url:
                    # 滚动页面以加载更多内容
                    self.logger.info("滚动页面以加载更多众测项目...")
                    # 尝试滚动几次
                    for _ in range(3):
                        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)
                
                # 保存页面内容用于调试
                if '/opportunities/all' in url or '/bug-bounty-programs' in url:
                    debug_file = 'hackerone_opportunities.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(self.page.content())
                    self.logger.info(f"页面内容已保存到 {debug_file}")
                    # 检查保存的文件大小
                    file_size = os.path.getsize(debug_file) / 1024
                    self.logger.info(f"保存的页面大小: {file_size:.2f} KB")
                
                # 添加随机延迟
                delay = random.uniform(*self.request_delay)
                self.logger.info(f"添加随机延迟: {delay:.2f}秒")
                time.sleep(delay)
                
                return self.page.content()
            except Exception as e:
                    retries += 1
                    self.logger.error(f"Playwright请求出错 (第 {retries}/{max_retries} 次尝试): {url}, 错误: {e}")
                    
                    # 如果达到最大重试次数，返回None
                    if retries >= max_retries:
                        self.logger.error(f"达到最大重试次数，请求失败: {url}")
                        return None
                    
                    # 等待一段时间后重试
                    wait_time = random.uniform(2, 5) * retries  # 指数退避
                    self.logger.info(f"{wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
        
        return None

    def close_playwright(self):
        """关闭Playwright资源"""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'context') and self.context:
                self.context.close()
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
            self.logger.info("Playwright资源已释放")
        except Exception as e:
            self.logger.error(f"关闭Playwright资源时出错: {e}")

    def get_random_proxy(self):
        """获取随机代理"""
        if not self.use_proxy or not self.proxy_list:
            return None
        with self.proxy_lock:
            return random.choice(self.proxy_list)

    def setup_driver(self):
        """设置Selenium WebDriver"""
        try:
            # 如果使用Firecrawl，则跳过WebDriver初始化
            if hasattr(self, 'use_firecrawl') and self.use_firecrawl:
                self.logger.info("Firecrawl模式已启用，跳过WebDriver初始化")
                return None
                
            import sys
            chrome_options = Options()
            # 启用headless模式
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            user_agent = random.choice(USER_AGENTS)
            chrome_options.add_argument(f'--user-agent={user_agent}')
            self.logger.info(f"设置User-Agent: {user_agent}")

            # 添加额外配置以提高兼容性
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-extensions')
            # 添加忽略SSL证书错误的配置
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
            chrome_options.add_argument('--allow-insecure-localhost')

            # 如果提供了Chrome路径，设置二进制位置
            if self.chrome_path:
                if os.path.exists(self.chrome_path):
                    chrome_options.binary_location = self.chrome_path
                    self.logger.info(f"使用指定路径的Chrome浏览器: {self.chrome_path}")
                else:
                    self.logger.warning(f"指定的Chrome路径不存在: {self.chrome_path}")
                    # 尝试常见的Chrome安装路径
                    common_chrome_paths = [
                        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                        os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe')
                    ]
                    for path in common_chrome_paths:
                        if os.path.exists(path):
                            chrome_options.binary_location = path
                            self.logger.info(f"找到Chrome浏览器路径: {path}")
                            break

            # 如果有代理，配置代理
            if self.use_proxy and self.proxy_list:
                proxy = self.get_random_proxy()
                if proxy:
                    # 代理格式: --proxy-server=http://ip:port
                    proxy_url = proxy['http'].replace('http://', '')
                    chrome_options.add_argument(f'--proxy-server={proxy_url}')
                    self.logger.info(f"使用代理: {proxy_url}")
            else:
                self.logger.info("未使用代理")

            self.logger.info("正在初始化Chrome WebDriver...")

            # 尝试使用webdriver_manager自动下载和管理ChromeDriver
            try:
                self.logger.info("尝试使用webdriver_manager自动下载和管理ChromeDriver...")
                # 获取ChromeDriver路径
                driver_path = ChromeDriverManager().install()
                self.logger.info(f"webdriver_manager成功下载ChromeDriver到: {driver_path}")
                
                # 使用下载的ChromeDriver初始化WebDriver
                service = Service(executable_path=driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info("WebDriver初始化成功，使用webdriver_manager自动管理的ChromeDriver")
                # 增加页面加载超时设置
                driver.set_page_load_timeout(60)
                return driver
            except Exception as webdriver_manager_e:
                self.logger.warning(f"使用webdriver_manager失败: {str(webdriver_manager_e)}")
                self.logger.info("尝试手动查找ChromeDriver...")
                
            # 确定ChromeDriver路径
            driver_path = self.driver_path

            # 如果未提供路径，尝试从环境变量获取
            if not driver_path:
                driver_path = os.environ.get('CHROMEDRIVER_PATH')

            # 如果仍未找到，尝试常见安装位置
            if not driver_path or not os.path.exists(driver_path):
                self.logger.warning("未找到有效的ChromeDriver路径，尝试从常见位置查找...")
                common_driver_paths = [
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver.exe'),
                    os.path.expanduser('~\\Downloads\\chromedriver.exe'),
                    os.path.expanduser('~\\Downloads\\chromedriver-win64\\chromedriver.exe'),
                    'C:\\Program Files\\ChromeDriver\\chromedriver.exe',
                    'C:\\chromedriver\\chromedriver.exe'
                ]
                for path in common_driver_paths:
                    if os.path.exists(path):
                        driver_path = path
                        self.logger.info(f"找到ChromeDriver路径: {driver_path}")
                        break

            # 验证驱动路径
            if not driver_path or not os.path.exists(driver_path):
                self.logger.error("无法找到ChromeDriver。请确保已下载ChromeDriver并通过--driver-path参数指定路径，或放置在脚本目录下。")
                self.logger.error("ChromeDriver下载地址: https://sites.google.com/chromium.org/driver/")
                # 提供使用Firecrawl替代的建议
                self.logger.error("提示: 如果您无法设置ChromeDriver，可以尝试使用Firecrawl API替代。使用 --use-firecrawl 参数并提供 --firecrawl-api-key。")
                raise FileNotFoundError("ChromeDriver路径未找到")

            # 检查文件是否可执行
            if not os.access(driver_path, os.X_OK):
                self.logger.warning(f"ChromeDriver文件可能不可执行: {driver_path}")
                # 在Windows上通常不需要设置可执行权限
                if sys.platform != 'win32':
                    try:
                        os.chmod(driver_path, 0o755)
                        self.logger.info(f"已修改ChromeDriver文件权限")
                    except:
                        self.logger.warning(f"无法修改ChromeDriver文件权限")

            # 初始化WebDriver
            try:
                service = Service(executable_path=driver_path)
                # 增加服务日志级别
                service.log_path = 'chromedriver.log'
                service.verbose = True

                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.logger.info(f"WebDriver初始化成功，使用路径: {driver_path}")
                # 增加页面加载超时设置
                driver.set_page_load_timeout(60)
                return driver
            except Exception as inner_e:
                self.logger.error(f"使用提供的ChromeDriver路径初始化失败: {str(inner_e)}")
                self.logger.error(f"请确保ChromeDriver版本与您的Chrome浏览器版本匹配")
                self.logger.error(f"当前ChromeDriver路径: {driver_path}")
                # 提供使用Firecrawl替代的建议
                self.logger.error("提示: 如果您无法设置ChromeDriver，可以尝试使用Firecrawl API替代。使用 --use-firecrawl 参数并提供 --firecrawl-api-key。")
                raise
        except Exception as e:
            self.logger.error(f"设置WebDriver失败: {e}")
            raise

    def send_request(self, url, max_retries=3):
        """发送请求，支持MCP Playwright、Playwright、Selenium和Firecrawl三种模式"""
        # 优先使用MCP Playwright
        if self.use_mcp_playwright and hasattr(self, 'mcp_playwright') and self.mcp_playwright:
                content = self.mcp_playwright_get(url, max_retries)
                if content:
                    return content
                self.logger.warning("MCP Playwright请求失败，尝试其他模式")
            
        # 其次使用Playwright
        if self.use_playwright and hasattr(self, 'page') and self.page:
                content = self.playwright_get(url, max_retries)
                if content:
                    return content
                self.logger.warning("Playwright请求失败，尝试其他模式")
        
        # 检查是否使用MCP Firecrawl
        if self.use_mcp_firecrawl and hasattr(self, 'mcp_firecrawl') and self.mcp_firecrawl:
            self.logger.info(f"使用MCP Firecrawl获取: {url}")
            try:
                # 使用MCP调用Firecrawl
                result = self.mcp_firecrawl_client.call(
                    "firecrawl_scrape",
                    {
                        "url": url,
                        "formats": ["markdown"],
                        "onlyMainContent": True
                    }
                )
                
                if result and "markdown" in result:
                    self.logger.info(f"MCP Firecrawl获取页面成功: {url}")
                    return result["markdown"]
                else:
                    self.logger.error(f"MCP Firecrawl返回无效结果: {url}")
            except Exception as e:
                self.logger.error(f"MCP Firecrawl请求失败: {e}")
            
        # 其次检查是否使用Firecrawl
            if self.use_firecrawl:
                self.logger.info(f"使用Firecrawl获取: {url}")
                # 简单的Firecrawl模式替代实现
                # 注意：完整的Firecrawl功能需要API密钥
                # 这里只是提供一个临时替代方案
            try:
                import requests
                headers = {
                    'User-Agent': random.choice(USER_AGENTS),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': self.base_url,
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # 如果有Cookie，添加到请求头
                cookies_dict = {}
                if hasattr(self, 'cookies') and self.cookies:
                    for cookie in self.cookies:
                        cookies_dict[cookie['name']] = cookie['value']
                    self.logger.info("Firecrawl模式使用登录Cookie")
                
                # 如果有代理，使用代理发送请求
                proxies = None
                if self.use_proxy and self.proxy_list:
                    proxy = self.get_random_proxy()
                    if proxy:
                        proxies = proxy
                        self.logger.info(f"Firecrawl模式使用代理: {proxy}")
                
                # 发送请求，增加超时时间到60秒
                response = requests.get(url, headers=headers, cookies=cookies_dict, proxies=proxies, timeout=60)
                response.raise_for_status()
                
                self.logger.info(f"Firecrawl模式获取页面成功: {url}")
                
                # 保存页面内容用于调试
                if 'bug-bounty-programs' in url or 'opportunities/all' in url:
                    debug_file = 'hackerone_page.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    self.logger.info(f"页面内容已保存到 {debug_file}")
                    
                    # 提示用户这个模式的局限性
                    self.logger.warning("注意：HackerOne是一个需要JavaScript的单页应用，Firecrawl模式（简单HTTP请求）可能无法获取完整内容")
                    self.logger.warning("建议：使用ChromeDriver或Playwright模式来确保能够执行JavaScript并获取完整的众测项目列表")
                
                # 添加随机延迟
                    delay = random.uniform(*self.request_delay)
                    self.logger.info(f"添加随机延迟: {delay:.2f}秒")
                    time.sleep(delay)
                
                return response.text
            except requests.exceptions.Timeout:
                self.logger.error(f"Firecrawl模式请求超时: {url}")
                self.logger.error("可能是网络连接问题或HackerOne网站限制。请检查您的网络连接。")
                # 尝试增加重试次数，这次使用不同的代理
                self.logger.info("尝试再次发送请求，使用不同的代理...")
                try:
                    # 使用不同的代理
                    retry_proxies = None
                    if self.use_proxy and self.proxy_list:
                        retry_proxy = self.get_random_proxy()
                        if retry_proxy:
                            retry_proxies = retry_proxy
                            self.logger.info(f"Firecrawl模式重试使用代理: {retry_proxy}")
                    
                    response = requests.get(url, headers=headers, cookies=cookies_dict, proxies=retry_proxies, timeout=90)
                    response.raise_for_status()
                    self.logger.info(f"重试成功: {url}")
                    return response.text
                except Exception as retry_e:
                    self.logger.error(f"重试也失败了: {retry_e}")
                    return None
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Firecrawl模式连接错误: {url}")
                self.logger.error("可能是网络连接问题或代理配置错误。")
                return None
            except Exception as e:
                self.logger.error(f"Firecrawl模式请求失败: {e}")
                # 如果有Firecrawl API密钥，提示正确的使用方法
                if hasattr(self, 'firecrawl_api_key') and self.firecrawl_api_key:
                    self.logger.error("提示: 如需使用完整的Firecrawl功能，请配置API密钥并使用官方API。")
                return None
        
        # 最后使用Selenium
        if hasattr(self, 'driver') and self.driver:
            retries = 0
            while retries < max_retries:
                try:
                    self.logger.info(f"使用Selenium访问: {url}")
                    # 记录页面加载开始时间
                    start_time = time.time()
                    self.driver.get(url)
                    # 等待页面加载完成
                    self.logger.info(f"等待页面加载完成: {url}")
                    # 等待body元素出现
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    self.logger.info(f"body元素已加载: {url}")
                    
                    # 尝试等待特定元素出现（对于众测项目页面）
                    if 'bug-bounty-programs' in url or 'opportunities/all' in url:
                        try:
                            # 等待项目卡片元素出现 (适配SPA)
                            try:
                                # 等待应用根容器加载
                                WebDriverWait(self.driver, 30).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'js-application-root'))
                                )
                                self.logger.info(f"应用根容器已加载: {url}")
                                
                                # 执行JavaScript以触发内容加载
                                self.logger.info("执行JavaScript以触发内容加载...")
                                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                
                                # 等待网络请求完成
                                self.logger.info("等待网络请求完成...")
                                WebDriverWait(self.driver, 30).until(
                                    lambda d: d.execute_script('return window.performance.getEntriesByType("resource").filter(e => e.initiatorType === "xmlhttprequest" || e.initiatorType === "fetch").length > 0')
                                )
                                
                                # 等待动态内容加载
                                WebDriverWait(self.driver, 60).until(
                                    lambda d: d.execute_script('return document.querySelector(\'.js-application-root\').children.length > 0')
                                )
                                self.logger.info(f"动态内容已加载: {url}")
                                
                                # 再次滚动页面以确保所有内容加载
                                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(5)
                                
                                # 尝试使用更通用的选择器
                                selectors = [
                                    (By.CSS_SELECTOR, '.js-application-root div'),
                                    (By.CSS_SELECTOR, '[data-testid="program-card"]'),
                                    (By.CSS_SELECTOR, '.application-card'),
                                    (By.CSS_SELECTOR, '.program-card'),
                                    (By.CLASS_NAME, 'sc-18f276c0-0')
                                ]
                                
                                for by, selector in selectors:
                                    try:
                                        elements = self.driver.find_elements(by, selector)
                                        if len(elements) > 0:
                                            self.logger.info(f"使用选择器 {by}:{selector} 找到 {len(elements)} 个元素: {url}")
                                            break
                                    except:
                                        continue
                                else:
                                    self.logger.warning(f"所有选择器都未能找到元素: {url}")
                            except Exception as e:
                                self.logger.warning(f"等待页面内容加载超时: {e}")
                        except Exception as e:
                            self.logger.warning(f"等待项目卡片元素超时: {e}")
                            # 尝试等待另一种可能的项目卡片类名
                            try:
                                WebDriverWait(self.driver, 15).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, 'program-card'))
                                )
                                self.logger.info(f"备选项目卡片元素已加载: {url}")
                            except Exception as e2:
                                self.logger.warning(f"等待备选项目卡片元素也超时: {e2}")

                    # 等待额外时间确保内容加载完成
                    wait_time = random.uniform(3, 8)
                    self.logger.info(f"等待{wait_time:.2f}秒确保内容加载完成")
                    time.sleep(wait_time)
                    
                    # 记录页面加载完成时间
                    load_time = time.time() - start_time
                    self.logger.info(f"页面加载完成，耗时: {load_time:.2f}秒: {url}")
                    
                    # 保存页面内容用于调试
                    if 'bug-bounty-programs' in url or 'opportunities/all' in url:
                        debug_file = 'hackerone_page.html'
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(self.driver.page_source)
                    self.logger.info(f"页面内容已保存到 {debug_file}")
                    # 检查保存的文件大小
                    file_size = os.path.getsize(debug_file) / 1024
                    self.logger.info(f"保存的页面大小: {file_size:.2f} KB")
                    
                    # 添加随机延迟
                    delay = random.uniform(*self.request_delay)
                    self.logger.info(f"添加随机延迟: {delay:.2f}秒")
                    time.sleep(delay)
                    
                    return self.driver.page_source
                except WebDriverException as e:
                    retries += 1
                    self.logger.error(f"WebDriver异常 (第 {retries}/{max_retries} 次尝试): {url}, 错误: {e}")
                    # 如果是驱动问题，尝试重新初始化WebDriver
                    try:
                        if 'session not created' in str(e) or 'chrome not reachable' in str(e):
                            self.logger.info("尝试重新初始化WebDriver...")
                            self.driver.quit()
                            self.driver = self.setup_driver()
                    except:
                        pass
                except Exception as e:
                    retries += 1
                    self.logger.error(f"请求出错 (第 {retries}/{max_retries} 次尝试): {url}, 错误: {e}")
                # 如果还没达到最大重试次数，等待一段时间后重试
                if retries < max_retries:
                    wait_time = random.uniform(2, 5) * retries  # 指数退避
                    self.logger.info(f"{wait_time:.2f}秒后重试...")
                    time.sleep(wait_time)
            self.logger.error(f"达到最大重试次数，请求失败: {url}")
            return None
        
        # 所有模式都不可用
        self.logger.error("没有可用的请求模式。请确保至少启用了Playwright、Selenium或Firecrawl中的一种。")
        return None

    def __del__(self):
        """析构函数，关闭浏览器"""
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                self.logger.info("浏览器已关闭")
            except:
                pass

    def validate_proxy(self, proxy):
        """验证代理是否有效"""
        try:
            test_url = 'https://www.hackerone.com'
            response = requests.get(test_url, proxies=proxy, timeout=10)
            return response.status_code == 200
        except:
            return False

    def load_proxies_from_file(self, file_path):
        """从文件加载代理"""
        try:
            with open(file_path, 'r') as f:
                proxies = []
                for line in f.readlines():
                    line = line.strip()
                    if line:
                        proxies.append({'http': line, 'https': line})
                # 验证代理并过滤无效的
                valid_proxies = [p for p in proxies if self.validate_proxy(p)]
                self.logger.info(f"从文件加载了 {len(valid_proxies)}/{len(proxies)} 个有效代理")
                with self.proxy_lock:
                    self.proxy_list = valid_proxies
                return True
        except Exception as e:
            self.logger.error(f"从文件加载代理失败: {e}")
            return False

    def parse_programs_page(self, html):
        """解析众测项目页面，提取域名"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        
        # 首先检查页面是否需要JavaScript
        if 'js-disabled' in html and 'It looks like your JavaScript is disabled' in html:
            self.logger.warning("检测到页面需要JavaScript才能正常显示内容")
            self.logger.warning("当前模式可能无法获取完整的众测项目列表")
            self.logger.warning("建议：请使用ChromeDriver模式来确保能够执行JavaScript")
            
        # 方法1: 尝试从script标签中提取JSON数据
        script_tags = soup.find_all('script', type='application/json')
        for script in script_tags:
            try:
                json_data = json.loads(script.string)
                # 尝试从JSON数据中提取项目信息
                if 'props' in json_data and 'pageProps' in json_data['props']:
                    page_props = json_data['props']['pageProps']
                    if 'programs' in page_props:
                        programs = page_props['programs']
                        self.logger.info(f"从JSON数据中找到 {len(programs)} 个众测项目")
                        program_links = []
                        for program in programs:
                            if 'url' in program:
                                program_links.append(program['url'])
                            elif 'slug' in program:
                                program_links.append(f"https://hackerone.com/{program['slug']}")
                        return program_links
                # 尝试其他可能的JSON结构
                if 'programs' in json_data:
                        programs = json_data['programs']
                        self.logger.info(f"从JSON数据中找到 {len(programs)} 个众测项目")
                        program_links = []
                        for program in programs:
                            if 'url' in program:
                                program_links.append(program['url'])
                            elif 'slug' in program:
                                program_links.append(f"https://hackerone.com/{program['slug']}")
                        return program_links
            except:
                continue

        # 方法2: 尝试提取所有链接并筛选
        all_links = soup.find_all('a', href=True)
        program_links = []
        for link in all_links:
            href = link['href']
            # 众测项目链接通常包含组织名称，如 /company-name
            if href.startswith('/') and len(href) > 1 and '?' not in href and '#' not in href:
                # 排除导航链接
                if href not in ['/login', '/signup', '/programs', '/about', '/blog', '/contact']:
                    full_url = urljoin(self.base_url, href)
                    program_links.append(full_url)

        if program_links:
            self.logger.info(f"通过链接筛选找到 {len(program_links)} 个可能的众测项目")
        else:
            self.logger.warning(f"未能找到任何众测项目链接")

        return program_links

    def parse_program_details(self, html, program_url):
        """解析项目详情页面，提取域名和对应的URL"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        domain_list = []
        
        # 首先检查页面是否需要JavaScript
        if 'js-disabled' in html and 'It looks like your JavaScript is disabled' in html:
            self.logger.warning("检测到页面需要JavaScript才能正常显示内容")
            self.logger.warning("当前模式可能无法获取完整的域名信息")
            self.logger.warning("建议：请使用ChromeDriver模式来确保能够执行JavaScript")

        # 尝试找到域名部分 - 方法1
        target_domains_section = soup.find('div', {'data-qa': 'target-domains'})
        if target_domains_section:
            domain_elements = target_domains_section.find_all('code')
            for domain in domain_elements:
                domain_text = domain.get_text(strip=True)
                if domain_text:
                    domain_list.append(domain_text)
                    self.domains.add(domain_text)
                    self.domain_url_map[domain_text] = program_url

        # 尝试找到域名部分 - 方法2 (备用选择器)
        if not domain_list:
            target_domains_section = soup.find('div', class_='program-scope__target-domains')
            if target_domains_section:
                domain_elements = target_domains_section.find_all('code')
                for domain in domain_elements:
                    domain_text = domain.get_text(strip=True)
                    if domain_text:
                        domain_list.append(domain_text)
                        self.domains.add(domain_text)
                        self.domain_url_map[domain_text] = program_url

        # 尝试找到域名部分 - 方法3 (直接搜索所有code标签)
        if not domain_list:
            all_code_tags = soup.find_all('code')
            for code in all_code_tags:
                code_text = code.get_text(strip=True)
                # 简单判断是否为域名
                if '.' in code_text and len(code_text) > 3 and not code_text.startswith('<') and not code_text.endswith('>'):
                    domain_list.append(code_text)
                    self.domains.add(domain_text)
                    self.domain_url_map[code_text] = program_url
        
        # 尝试找到域名部分 - 方法4 (从script标签中提取JSON数据)
        if not domain_list:
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    # 尝试从JSON数据中提取域名信息
                    if 'props' in json_data and 'pageProps' in json_data['props']:
                        page_props = json_data['props']['pageProps']
                        if 'program' in page_props and 'targets' in page_props['program']:
                            targets = page_props['program']['targets']
                            if 'in_scope' in targets:
                                for target in targets['in_scope']:
                                    if 'asset_identifier' in target:
                                        domain = target['asset_identifier']
                                        if '.' in domain:
                                            domain_list.append(domain)
                                            self.domains.add(domain)
                                            self.domain_url_map[domain] = program_url
                except:
                    continue

        return domain_list

    def get_all_programs(self):
        """获取所有众测项目链接"""
        all_program_links = []
        current_page = 1

        while True:
            self.logger.info(f"正在获取第 {current_page} 页的众测项目")
            page_url = f'{self.programs_url}?page={current_page}'
            html = self.send_request(page_url)

            if not html:
                self.logger.warning("无法获取页面内容，停止爬取")
                break

            program_links = self.parse_programs_page(html)
            if not program_links:
                self.logger.info("没有找到更多众测项目，停止爬取")
                break

            all_program_links.extend(program_links)
            current_page += 1

        self.logger.info(f"总共找到 {len(all_program_links)} 个众测项目链接")
        return all_program_links

    def save_progress(self):
        """保存当前进度"""
        temp_file = f"{self.output_file}.tmp"
        try:
            with open(temp_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['domain', 'url'])
                for domain, url in sorted(self.domain_url_map.items()):
                    writer.writerow([domain, url])
            self.logger.info(f"进度已保存到临时文件: {temp_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存进度失败: {e}")
            return False

    def load_progress(self):
        """加载之前保存的进度"""
        temp_file = f"{self.output_file}.tmp"
        try:
            with open(temp_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # 跳过标题行
                for row in reader:
                    if row and len(row) >= 2:
                        domain = row[0]
                        url = row[1]
                        self.domains.add(domain)
                        self.domain_url_map[domain] = url
            self.logger.info(f"从临时文件加载进度: {temp_file}, 已加载 {len(self.domains)} 个域名和URL")
            return True
        except Exception as e:
            self.logger.error(f"加载进度失败: {e}")
            return False

    def crawl_domains(self, progress_interval=10):
        """爬取所有众测项目的域名和URL，定期保存进度"""
        # 尝试加载之前的进度
        self.load_progress()

        program_links = self.get_all_programs()
        processed_count = 0

        for i, program_url in enumerate(program_links, 1):
            # 检查是否已经处理过该项目（可以根据需要实现）
            self.logger.info(f"正在爬取第 {i}/{len(program_links)} 个项目: {program_url}")
            html = self.send_request(program_url)
            domains = self.parse_program_details(html, program_url)
            self.logger.info(f"从该项目获取了 {len(domains)} 个域名和URL")

            processed_count += 1
            # 定期保存进度
            if processed_count % progress_interval == 0:
                self.save_progress()

        # 爬取完成后保存最终结果
        self.save_progress()
        self.logger.info(f"总共获取了 {len(self.domains)} 个唯一域名和URL")
        return self.domains

    def save_domains(self):
        """保存域名和URL到CSV文件"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['domain', 'url'])
            for domain, url in sorted(self.domain_url_map.items()):
                writer.writerow([domain, url])
        self.logger.info(f"域名和URL已保存到 {self.output_file}")

    def run(self):
        """运行爬虫"""
        self.logger.info("开始爬取HackerOne众测域名")
        start_time = time.time()

        try:
            self.crawl_domains()
            self.save_domains()
        except Exception as e:
            self.logger.error(f"爬虫运行出错: {e}")
        finally:
            end_time = time.time()
            self.logger.info(f"爬虫运行完成，耗时: {end_time - start_time:.2f} 秒")

def check_chrome_config(driver_path=None, chrome_path=None):
    """检查Chrome和ChromeDriver配置"""
    import os
    import subprocess
    import sys

    print("=== Chrome配置检查 ===")

    # 检查Chrome浏览器
    chrome_found = False
    if chrome_path and os.path.exists(chrome_path):
        print(f"✓ 找到Chrome浏览器: {chrome_path}")
        chrome_found = True
    else:
        # 尝试常见的Chrome安装路径
        common_chrome_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe')
        ]
        for path in common_chrome_paths:
            if os.path.exists(path):
                print(f"✓ 找到Chrome浏览器: {path}")
                chrome_found = True
                chrome_path = path
                break
        if not chrome_found:
            print("✗ 未找到Chrome浏览器。请安装Chrome或通过--chrome-path参数指定路径。")
            print("Chrome下载地址: https://www.google.com/chrome/")

    # 检查ChromeDriver
    driver_found = False
    if driver_path and os.path.exists(driver_path):
        print(f"✓ 找到ChromeDriver: {driver_path}")
        driver_found = True
    else:
        # 尝试常见的ChromeDriver路径
        common_driver_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chromedriver.exe'),
            os.path.expanduser('~\\Downloads\\chromedriver.exe'),
            os.path.expanduser('~\\Downloads\\chromedriver-win64\\chromedriver.exe'),
            'C:\\Program Files\\ChromeDriver\\chromedriver.exe',
            'C:\\chromedriver\\chromedriver.exe'
        ]
        for path in common_driver_paths:
            if os.path.exists(path):
                print(f"✓ 找到ChromeDriver: {path}")
                driver_found = True
                driver_path = path
                break
        if not driver_found:
            print("✗ 未找到ChromeDriver。请下载ChromeDriver并通过--driver-path参数指定路径。")
            print("ChromeDriver下载地址: https://sites.google.com/chromium.org/driver/")

    # 检查版本兼容性（如果都找到了）
    if chrome_found and driver_found:
        try:
            # 获取Chrome版本
            if sys.platform == 'win32':
                chrome_version = subprocess.check_output([chrome_path, '--version']).decode('utf-8').strip()
            else:
                chrome_version = subprocess.check_output([chrome_path, '--version']).decode('utf-8').strip()
            print(f"Chrome版本: {chrome_version}")

            # 获取ChromeDriver版本
            driver_version = subprocess.check_output([driver_path, '--version']).decode('utf-8').strip()
            print(f"ChromeDriver版本: {driver_version}")

            # 简单比较主版本号
            chrome_major = chrome_version.split(' ')[-1].split('.')[0]
            driver_major = driver_version.split(' ')[1].split('.')[0]

            if chrome_major == driver_major:
                print("✓ Chrome和ChromeDriver版本兼容")
            else:
                print(f"✗ Chrome和ChromeDriver版本不兼容: Chrome {chrome_major}, ChromeDriver {driver_major}")
                print("请确保下载与您Chrome版本匹配的ChromeDriver")
        except Exception as e:
            print(f"检查版本兼容性时出错: {str(e)}")

    print("====================")
    return chrome_found and driver_found

def parse_arguments():
    parser = argparse.ArgumentParser(description='HackerOne众测域名爬虫')
    parser.add_argument('-o', '--output', default='hackerone_domains.csv', help='输出文件路径 (默认: hackerone_domains.csv)')
    parser.add_argument('-p', '--use-proxy', action='store_true', help='使用代理服务器')
    parser.add_argument('-f', '--proxy-file', help='包含代理列表的文件路径')
    parser.add_argument('-d', '--delay', nargs=2, type=int, default=[1, 3], help='请求延迟范围 (默认: 1 3)')
    parser.add_argument('-r', '--max-retries', type=int, default=3, help='最大重试次数 (默认: 3)')
    parser.add_argument('-b', '--backoff-factor', type=float, default=0.3, help='退避因子 (默认: 0.3)')
    parser.add_argument('-i', '--progress-interval', type=int, default=10, help='进度保存间隔 (默认: 10)')
    parser.add_argument('-l', '--log-level', choices=LOG_LEVELS.keys(), default='INFO', help='日志级别 (默认: INFO)')
    parser.add_argument('--driver-path', help='ChromeDriver可执行文件路径', default=None)
    parser.add_argument('--chrome-path', help='Chrome浏览器可执行文件路径', default=None)
    parser.add_argument('--check-config', action='store_true', help='检查Chrome和ChromeDriver配置')
    parser.add_argument('--use-firecrawl', action='store_true', help='使用Firecrawl API替代Selenium进行爬取')
    parser.add_argument('--firecrawl-api-key', help='Firecrawl API密钥')
    
    # Playwright相关参数
    parser.add_argument('--playwright', action='store_true', help='使用Playwright进行爬取')
    parser.add_argument('--playwright-login', action='store_true', help='使用Playwright模拟登录HackerOne')
    parser.add_argument('-u', '--username', help='HackerOne用户名 (用于Playwright登录)')
    parser.add_argument('--password', help='HackerOne密码 (用于Playwright登录)')
    
    # MCP相关参数
    parser.add_argument('--use-mcp-playwright', action='store_true', help='使用MCP服务器调用Playwright')
    parser.add_argument('--use-mcp-firecrawl', action='store_true', help='使用MCP服务器调用Firecrawl')
    parser.add_argument('--mcp-host', default='localhost', help='MCP服务器主机地址 (默认: localhost)')
    parser.add_argument('--mcp-port', type=int, default=8000, help='MCP服务器端口 (默认: 8000)')
    
    args = parser.parse_args()
    
    # 验证Playwright登录参数
    if args.playwright_login:
        if not args.username or not args.password:
            parser.error('使用--playwright-login时，必须同时提供--username和--password参数')
    
    return args

def load_proxies_from_file(file_path):
    """从文件加载代理列表"""
    proxies = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxies.append({
                        'http': f'http://{line}',
                        'https': f'https://{line}'
                    })
        logger.info(f"从文件加载了 {len(proxies)} 个代理")
        return proxies
    except Exception as e:
        logger.error(f"加载代理文件失败: {e}")
        return []

class MCPClient:
    """MCP服务器客户端，用于调用MCP服务"""
    def __init__(self, server_name, host='localhost', port=8000):
        self.server_name = server_name
        self.host = host
        self.port = port
        self.logger = logging.getLogger(f"MCP_{server_name}")
        self.logger.setLevel(logging.INFO)
    
    def call(self, tool_name, args):
        """调用MCP服务器的工具"""
        try:
            conn = http.client.HTTPConnection(self.host, self.port)
            headers = {'Content-Type': 'application/json'}
            
            # 构建请求体
            payload = json.dumps({
                "name": "run_mcp",
                "arguments": {
                    "server_name": self.server_name,
                    "tool_name": tool_name,
                    "args": args
                }
            })
            
            self.logger.info(f"调用MCP {self.server_name}.{tool_name}")
            conn.request("POST", "/execute", payload, headers)
            
            response = conn.getresponse()
            data = response.read().decode()
            conn.close()
            
            if response.status == 200:
                return json.loads(data)
            else:
                self.logger.error(f"MCP调用失败，状态码: {response.status}, 响应: {data}")
                return None
        except Exception as e:
            self.logger.error(f"MCP调用异常: {e}")
            return None

if __name__ == '__main__':
    import sys
    args = parse_arguments()

    # 如果只是检查配置
    if args.check_config:
        success = check_chrome_config(args.driver_path, args.chrome_path)
        sys.exit(0 if success else 1)

    # 检查配置
    check_chrome_config(args.driver_path, args.chrome_path)

    # 加载代理列表
    proxy_list = None
    if args.use_proxy:
        if args.proxy_file:
            proxy_list = load_proxies_from_file(args.proxy_file)
        else:
            proxy_list = PROXIES
            if not proxy_list:
                logger.warning('未指定代理文件且默认代理列表为空')
    
    # 创建爬虫实例
    scraper = HackerOneScraper(
        output_file=args.output,
        use_proxy=args.use_proxy,
        proxy_list=proxy_list,
        request_delay=tuple(args.delay),
        max_retries=args.max_retries,
        backoff_factor=args.backoff_factor,
        progress_interval=args.progress_interval,
        log_level=LOG_LEVELS[args.log_level],
        driver_path=args.driver_path,
        chrome_path=args.chrome_path,
        use_firecrawl=args.use_firecrawl,
        firecrawl_api_key=args.firecrawl_api_key,
        use_playwright=args.playwright,
        playwright_login=args.playwright_login,
        username=args.username,
        password=args.password,
        use_mcp_playwright=args.use_mcp_playwright,
        use_mcp_firecrawl=args.use_mcp_firecrawl,
        mcp_host=args.mcp_host,
        mcp_port=args.mcp_port
    )
    
    # 运行爬虫
    scraper.run()