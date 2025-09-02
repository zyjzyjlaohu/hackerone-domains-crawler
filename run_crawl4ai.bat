@echo off
chcp 65001 >nul

:: 设置环境变量，确保中文正常显示
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

:: 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo 已在虚拟环境中运行: %VIRTUAL_ENV%
) else (
    echo 未在虚拟环境中运行，尝试查找并激活虚拟环境...
    
    :: 检查常见的虚拟环境目录
    if exist "%~dp0.venv\Scripts\activate" (
        call "%~dp0.venv\Scripts\activate"
        echo 已激活虚拟环境: %~dp0.venv
    ) else (
        echo 警告: 未找到虚拟环境，将使用当前Python环境。
        echo 建议: 创建虚拟环境以避免依赖冲突。
        echo 命令: python -m venv .venv && .venv\Scripts\activate
    )
)

:: 安装或升级必要的依赖
:INSTALL_DEPENDENCIES
echo ============================================================================
echo                      安装/升级必要的依赖包
echo ============================================================================
echo 安装pip最新版本...
pip install --upgrade pip

echo 安装基础依赖...
pip install --upgrade beautifulsoup4 requests

echo 尝试安装crawl4ai...
pip install --upgrade crawl4ai

:: 检查crawl4ai是否安装成功
python -c "import crawl4ai; print('crawl4ai安装成功')" 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo crawl4ai安装成功，将使用crawl4ai模式运行。
) else (
    echo 警告: crawl4ai安装失败或无法导入。
    echo 将再次尝试安装crawl4ai...
    pip install --upgrade crawl4ai
    python -c "import crawl4ai; print('crawl4ai安装成功')" 2>NUL
    if %ERRORLEVEL% NEQ 0 (
        echo 错误: crawl4ai仍然无法导入。
        echo 将使用基本HTTP请求模式运行。
    )
)

:: 测试网络连接状态
cls
echo ============================================================================
echo                   HackerOne众测域名爬虫 - 网络诊断
echo ============================================================================
echo 正在测试网络连接...
python -c "import requests; print('\n网络连接测试结果:'); try: r = requests.get('https://www.example.com', timeout=5); print(f'直接连接 - 状态码: {r.status_code}'); except Exception as e: print(f'直接连接失败: {e}')"
echo 

:: 询问用户是否使用代理
if exist "%~dp0proxies.txt" (
    echo 检测到代理文件: proxies.txt
    set /p USE_PROXY_INPUT=是否使用代理？(y/n，默认为n): 
    if /i "%USE_PROXY_INPUT%"=="y" (
        set USE_PROXY=--use-proxy --proxy-file proxies.txt
        echo 将使用代理进行爬取
    ) else (
        set USE_PROXY=
        echo 将不使用代理进行爬取
    )
) else (
    echo 未检测到代理文件，将不使用代理爬取
    set USE_PROXY=
)
echo 
echo 正在启动爬虫...
echo 使用参数: %USE_PROXY% --use-crawl4ai --log-level DEBUG
echo ============================================================================

:: 运行更新后的脚本，强制使用crawl4ai模式并显示详细日志
python crawl_hackerone_domains_updated.py %USE_PROXY% --use-crawl4ai --log-level DEBUG

:: 脚本执行完成后的处理
if %ERRORLEVEL% EQU 0 (
    echo ============================================================================
    echo 爬虫已成功完成！
    echo 结果已保存到 hackerone_domains.csv
    echo ============================================================================
) else (
    echo ============================================================================
    echo 爬虫执行出错！
    echo 请查看上面的错误信息进行排查。
    echo 可能的解决方案:
    echo 1. 检查网络连接是否正常（防火墙、网络限制等）
    echo 2. 如果使用代理，请确保代理服务器配置正确且正在运行
    echo 3. 尝试不使用代理运行（重新运行脚本并选择'n'）
    echo 4. 确保crawl4ai已正确安装: pip install crawl4ai
    echo 5. 检查是否有安全软件阻止连接
    echo ============================================================================
)

:: 暂停以查看结果
echo.
echo 按任意键退出...
pause >nul