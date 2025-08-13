# Git Commit Script - PowerShell version with robust quotation handling
# Usage: .\git-commit.ps1 "Your commit message here"
# Usage: .\git-commit.ps1 (prompts for message)

param(
    [string]$Message = ""
)

# Function to safely execute git commands
function Invoke-GitCommand {
    param([string]$Command, [string]$Arguments)
    
    try {
        $result = & $Command $Arguments.Split(' ')
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Host "Error executing: $Command $Arguments" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
}

# Get commit message if not provided
if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host ""
    $Message = Read-Host "Enter your commit message"
}

# Validate message
if ([string]::IsNullOrWhiteSpace($Message)) {
    Write-Host "Error: Commit message cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Committing with message: $Message" -ForegroundColor Green
Write-Host ""

# Stage all changes
Write-Host "Adding all changes..." -ForegroundColor Yellow
if (-not (Invoke-GitCommand "git" "add -A")) {
    Write-Host "Error: Failed to stage changes" -ForegroundColor Red
    exit 1
}

# Show status before commit
Write-Host ""
Write-Host "Current status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Commit with proper escaping
try {
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Commit failed" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Error: Commit failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Commit successful!" -ForegroundColor Green
Write-Host ""

# Show recent commits
Write-Host "Recent commits:" -ForegroundColor Yellow
git log --oneline -3
Write-Host ""
