# 简单的GitHub上传脚本

Write-Host "=== 简单GitHub上传脚本 ===" -ForegroundColor Green

# 配置变量 - 这些已经设置好了，无需修改
$REPO_URL = "https://github.com/zyjzyjlaohu/hackerone-domains-crawler"
$BRANCH_NAME = "main"

# 检查Git是否安装
try {
    git --version | Out-Null
    Write-Host "✓ Git已安装"
} catch {
    Write-Host "✗ 未找到Git！请先安装Git。" -ForegroundColor Red
    Write-Host "下载地址：https://git-scm.com/download/win"
    Read-Host -Prompt "按Enter键退出..."
    exit 1
}

# 初始化Git仓库（如果尚未初始化）
if (-not (Test-Path -Path ".git")) {
    Write-Host "初始化Git仓库..."
    git init
}

# 添加所有文件
Write-Host "添加所有文件到暂存区..."
git add .

# 提交更改
Write-Host "提交更改..."
git commit -m "Upload HackerOne crawl scripts" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "没有新的更改需要提交。" -ForegroundColor Yellow
}

# 添加远程仓库（移除旧的如果存在）
Write-Host "配置远程仓库..."
git remote remove origin 2>$null
git remote add origin $REPO_URL

# 强制推送（解决冲突）
Write-Host "\n正在推送代码到GitHub仓库..."
Write-Host "注意：这将使用--force参数覆盖远程仓库内容！"
Write-Host "请确保你有这个仓库的写入权限！"
Write-Host "\n准备推送，请输入你的GitHub凭据..."
git push --force origin $BRANCH_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "\n✓ 上传成功！" -ForegroundColor Green
    Write-Host "你的代码已成功上传到："
    Write-Host $REPO_URL
} else {
    Write-Host "\n✗ 上传失败！" -ForegroundColor Red
    Write-Host "可能的解决方法："
    Write-Host "1. 确保你的GitHub个人访问令牌有效且有写入权限"
    Write-Host "2. 检查你的网络连接"
    Write-Host "3. 尝试手动运行这些命令："
    Write-Host "   cd \"$PWD\""
    Write-Host "   git push --force origin main"
}

Read-Host -Prompt "按Enter键退出..."