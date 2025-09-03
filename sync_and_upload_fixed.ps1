# GitHub 同步与上传脚本 - 修复版

Write-Host "=== GitHub 同步与上传脚本 ===" -ForegroundColor Green

# 配置变量
$REPO_URL = "https://github.com/zyjzyjlaohu/hackerone-domains-crawler"
$BRANCH_NAME = "main"
$COMMIT_MESSAGE = "Upload HackerOne crawl scripts"

# 检查 Git 是否已安装
try {
    git --version | Out-Null
    Write-Host "Git 已安装。"
} catch {
    Write-Host "错误：未找到 Git。请先安装 Git 后再运行此脚本。" -ForegroundColor Red
    Write-Host "Git 下载地址：https://git-scm.com/download/win"
    Read-Host -Prompt "按 Enter 键退出..."
    exit 1
}

# 设置 Git 用户信息（如果尚未设置）
$gitConfigUser = git config user.name
$gitConfigEmail = git config user.email

if (-not $gitConfigUser -or -not $gitConfigEmail) {
    Write-Host "Git 用户信息未设置，建议先设置："
    Write-Host "git config --global user.name ""你的用户名"""
    Write-Host "git config --global user.email ""你的邮箱"""
}

# 检查当前目录是否已初始化 Git 仓库
if (-not (Test-Path -Path ".git" -PathType Container)) {
    Write-Host "当前目录未初始化 Git 仓库，正在初始化..."
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Git 仓库初始化失败。" -ForegroundColor Red
        Read-Host -Prompt "按 Enter 键退出..."
        exit 1
    }
}

# 检查是否已存在远程仓库 origin
$remoteOrigin = git remote get-url origin 2>$null
if ($remoteOrigin) {
    Write-Host "远程仓库 origin 已存在：$remoteOrigin"
    Write-Host "正在移除旧的远程仓库..."
    git remote remove origin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "移除旧的远程仓库失败，但将继续执行。" -ForegroundColor Yellow
    }
}

# 添加远程仓库
Write-Host "正在添加远程仓库：$REPO_URL"
if ($LASTEXITCODE -eq 0) {
    git remote add origin $REPO_URL
    if ($LASTEXITCODE -ne 0) {
        Write-Host "添加远程仓库失败。" -ForegroundColor Red
        Read-Host -Prompt "按 Enter 键退出..."
        exit 1
    }
}

# 拉取远程仓库的最新内容（解决冲突）
Write-Host "正在拉取远程仓库 $BRANCH_NAME 分支的最新内容..."
try {
    git pull --rebase origin $BRANCH_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Host "拉取失败，尝试使用不同的方法..." -ForegroundColor Yellow
        git fetch origin
        if ($LASTEXITCODE -ne 0) {
            Write-Host "获取远程更新失败，可能是网络问题。" -ForegroundColor Red
            Read-Host -Prompt "按 Enter 键退出..."
            exit 1
        }
    }
} catch {
    Write-Host "拉取过程中出现异常：$_" -ForegroundColor Red
    Read-Host -Prompt "按 Enter 键退出..."
    exit 1
}

# 添加文件到暂存区
Write-Host "正在将文件添加到暂存区..."
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "添加文件失败。" -ForegroundColor Red
    Read-Host -Prompt "按 Enter 键退出..."
    exit 1
}

# 提交更改
Write-Host "正在提交更改..."
git commit -m $COMMIT_MESSAGE 2>$null
if ($LASTEXITCODE -ne 0) {
    # 如果没有可提交的更改，忽略错误
    if ($LASTEXITCODE -eq 1) {
        Write-Host "没有新的更改需要提交。" -ForegroundColor Yellow
    } else {
        Write-Host "提交失败。" -ForegroundColor Red
        Read-Host -Prompt "按 Enter 键退出..."
        exit 1
    }
}

# 推送更改
Write-Host "正在推送更改到远程仓库 $BRANCH_NAME 分支..."
git push origin $BRANCH_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "推送失败，尝试使用强制推送（谨慎使用）..." -ForegroundColor Yellow
    git push origin $BRANCH_NAME --force
    if ($LASTEXITCODE -ne 0) {
        Write-Host "强制推送也失败了。可能的问题："
        Write-Host "1. 网络连接问题"
        Write-Host "2. GitHub 仓库权限不足"
        Write-Host "3. 个人访问令牌 (PAT) 无效或权限不够"
        Write-Host "\n建议手动尝试以下命令："
        Write-Host "cd \"$PWD\""
        Write-Host "git push -u origin $BRANCH_NAME"
        Read-Host -Prompt "按 Enter 键退出..."
        exit 1
    }
}

# 成功完成
Write-Host "\n=== 上传成功！===" -ForegroundColor Green
Write-Host "你的代码已成功上传到 GitHub 仓库："
Write-Host "$REPO_URL"
Read-Host -Prompt "按 Enter 键退出..."