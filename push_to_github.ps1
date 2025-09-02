# This script is used to upload hackerone directory to GitHub repository

# Set variables
$REPO_URL = "https://github.com/zyjzyjlaohu/hackerone-domains-crawler"
$BRANCH_NAME = "main"
$COMMIT_MESSAGE = "Upload HackerOne crawl scripts"

# Check if Git is installed
try {
    Get-Command git -ErrorAction Stop
} catch {
    Write-Host "Git is not installed. Please install Git first." -ForegroundColor Red
    Pause
    exit 1
}

# Change to current directory
Set-Location $PSScriptRoot

# Check if it's already a git repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
}

# Add all files (excluding files specified in .gitignore)
Write-Host "Adding files to staging area..."
git add .

# Commit changes
Write-Host "Committing changes..."
git commit -m $COMMIT_MESSAGE

# Add remote repository
Write-Host "Adding remote repository..."
git remote add origin $REPO_URL

# Push code to GitHub
Write-Host "Pushing to GitHub repository..."
git push -u origin $BRANCH_NAME

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully uploaded to GitHub repository!" -ForegroundColor Green
} else {
    Write-Host "Upload failed. Please check the following:" -ForegroundColor Red
    Write-Host "1. Make sure GitHub username and repository name are correct"
    Write-Host "2. Make sure you have write permission to the repository"
    Write-Host "3. Make sure network connection is normal"
    Write-Host "4. You may need to set git user information first:"
    Write-Host "   git config --global user.name \"Your Name\""
    Write-Host "   git config --global user.email \"your.email@example.com\""
}

Pause