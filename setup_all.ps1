<#
.SYNOPSIS
Master setup script for the FindMy Tracker project.
#>

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "    FindMy Tracker - Dual-Network ESP32 Setup        " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check Prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$prereqsMet = $true

# Python
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Python is installed." -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python is not found." -ForegroundColor Red
    $prereqsMet = $false
}

# Docker
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Docker is installed." -ForegroundColor Green
} else {
    Write-Host "[ERROR] Docker is not found." -ForegroundColor Red
    $prereqsMet = $false
}

# Git
if (Get-Command "git" -ErrorAction SilentlyContinue) {
    Write-Host "[OK] Git is installed." -ForegroundColor Green
} else {
    Write-Host "[ERROR] Git is not found." -ForegroundColor Red
    $prereqsMet = $false
}

# VS Code
if (Get-Command "code" -ErrorAction SilentlyContinue) {
    Write-Host "[OK] VS Code is installed." -ForegroundColor Green
} else {
    Write-Host "[WARNING] VS Code is not found in PATH." -ForegroundColor Yellow
}

if (-not $prereqsMet) {
    Write-Host "Please install missing prerequisites and try again." -ForegroundColor Red
    exit 1
}

# Install Python requirements
Write-Host "`nInstalling Python requirements..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# Run Sub-project Setups
Write-Host "`nRunning sub-project setup scripts..." -ForegroundColor Yellow

if (Test-Path "apple-findmy\setup.ps1") {
    Write-Host "Running Apple track setup..." -ForegroundColor Cyan
    & .\apple-findmy\setup.ps1
} else {
    Write-Host "Apple track setup script not found. Skipping." -ForegroundColor DarkGray
}

if (Test-Path "google-findmy\setup.ps1") {
    Write-Host "Running Google track setup..." -ForegroundColor Cyan
    & .\google-findmy\setup.ps1
} else {
    Write-Host "Google track setup script not found. Skipping." -ForegroundColor DarkGray
}

# Initialize Git Repository
Write-Host "`nChecking Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    Write-Host "Initializing new Git repository..." -ForegroundColor Cyan
    git init
    Write-Host "Git repository initialized." -ForegroundColor Green
} else {
    Write-Host "Git repository already exists." -ForegroundColor Green
}

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the README.md in both apple-findmy/ and google-findmy/."
Write-Host "2. Flash your ESP32 boards using the provided tools."
Write-Host "=====================================================" -ForegroundColor Cyan
