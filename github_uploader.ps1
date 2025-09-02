# GitHub Uploader - A more robust script to upload files to GitHub

# Set variables
$REPO_URL = "https://github.com/zyjzyjlaohu/hackerone-domains-crawler"
$BRANCH_NAME = "main"
$COMMIT_MESSAGE = "Upload HackerOne crawl scripts"

# Function to check and set git user info
function Check-GitUserInfo {
    $gitUser = git config user.name
    $gitEmail = git config user.email
    
    if (-not $gitUser -or -not $gitEmail) {
        Write-Host "Git user information is not set." -ForegroundColor Yellow
        Write-Host "Please configure your git user information first:"
        Write-Host "git config --global user.name \"Your Name\""
        Write-Host "git config --global user.email \"your.email@example.com\""
        Pause
        exit 1
    }
    
    Write-Host "Git user information is set correctly." -ForegroundColor Green
}

# Function to handle remote repository
function Setup-RemoteRepository {
    # Check if remote origin exists and remove it if necessary
    $remoteExists = git remote | Where-Object { $_ -eq "origin" }
    if ($remoteExists) {
        Write-Host "Remote origin already exists. Removing it..."
        git remote remove origin
    }
    
    # Add new remote repository
    Write-Host "Adding remote repository: $REPO_URL"
    git remote add origin $REPO_URL
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to add remote repository. Please check the URL." -ForegroundColor Red
        Pause
        exit 1
    }
}

# Function to try pushing with retry
function Push-WithRetry {
    $maxRetries = 3
    $retryCount = 0
    $success = $false
    
    while ($retryCount -lt $maxRetries -and -not $success) {
        Write-Host "Push attempt $($retryCount + 1)/$maxRetries..."
        git push -u origin $BRANCH_NAME
        
        if ($LASTEXITCODE -eq 0) {
            $success = $true
            Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
        } else {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "Push failed. Retrying in 5 seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 5
            } else {
                Write-Host "Failed to push after $maxRetries attempts." -ForegroundColor Red
                Write-Host "Possible issues:" -ForegroundColor Red
                Write-Host "1. Network connection problems"
                Write-Host "2. Incorrect repository URL or permissions"
                Write-Host "3. Firewall or proxy restrictions"
                Write-Host "\nTroubleshooting tips:" -ForegroundColor Yellow
                Write-Host "- Check your internet connection"
                Write-Host "- Verify you have write access to the repository"
                Write-Host "- Try generating a new personal access token (PAT) with sufficient permissions"
                Write-Host "- If using a proxy, configure git with: git config --global http.proxy http://proxy:port"
            }
        }
    }
    
    return $success
}

# Main script
Write-Host "=== GitHub Uploader ===" -ForegroundColor Cyan

# Check if Git is installed
try {
    Get-Command git -ErrorAction Stop
    Write-Host "Git is installed." -ForegroundColor Green
} catch {
    Write-Host "Git is not installed. Please install Git first." -ForegroundColor Red
    Pause
    exit 1
}

# Check git user info
Check-GitUserInfo

# Change to current directory
Set-Location $PSScriptRoot
Write-Host "Current directory: $PSScriptRoot"

# Check if it's already a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to initialize git repository." -ForegroundColor Red
        Pause
        exit 1
    }
} else {
    Write-Host "Git repository already exists." -ForegroundColor Green
}

# Add all files (excluding files specified in .gitignore)
Write-Host "Adding files to staging area..."
git add .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to add files to staging area." -ForegroundColor Red
    Pause
    exit 1
}

# Commit changes
Write-Host "Committing changes..."
git commit -m $COMMIT_MESSAGE

if ($LASTEXITCODE -ne 0) {
    Write-Host "No changes to commit or failed to commit." -ForegroundColor Yellow
    # Check if there's anything to commit
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "Working directory is clean. No changes to commit." -ForegroundColor Green
    }
}

# Setup remote repository
Setup-RemoteRepository

# Push with retry
$pushSuccess = Push-WithRetry

if ($pushSuccess) {
    Write-Host "\n=== Upload Complete ===" -ForegroundColor Green
    Write-Host "Your files have been successfully uploaded to $REPO_URL"
} else {
    Write-Host "\n=== Upload Failed ===" -ForegroundColor Red
    Write-Host "Please try to manually push using the following commands:"
    Write-Host "cd \"$PSScriptRoot\""
    Write-Host "git push -u origin $BRANCH_NAME"
}

Write-Host "\nScript completed." -ForegroundColor Cyan
Pause