<#
.SYNOPSIS
Sets up the environment for the Google Find My ESP32 tracker project.

.DESCRIPTION
Checks for required tools (Python, Git), clones the GoogleFindMyTools repository,
installs Python dependencies, and provides instructions for VS Code and ESP-IDF.
#>

$ErrorActionPreference = "Stop"

Write-Host "Starting setup for Google Find My ESP32 Tracker..." -ForegroundColor Cyan

# 1. Check Python
Write-Host "Checking for Python 3..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "Found $pythonVersion" -ForegroundColor Green
    } else {
        Write-Warning "Python 3 is required but found: $pythonVersion"
        Write-Host "Please install Python 3 from https://www.python.org/downloads/"
        exit 1
    }
} catch {
    Write-Warning "Python is not installed or not in PATH."
    Write-Host "Please install Python 3 from https://www.python.org/downloads/ and ensure 'Add Python to PATH' is checked."
    exit 1
}

# 2. Check Git
Write-Host "Checking for Git..."
try {
    $gitVersion = git --version 2>&1
    Write-Host "Found $gitVersion" -ForegroundColor Green
} catch {
    Write-Warning "Git is not installed or not in PATH."
    Write-Host "Please install Git from https://git-scm.com/downloads"
    exit 1
}

# 3. Clone Repository
$repoUrl = "https://github.com/leonboe1/GoogleFindMyTools.git"
$targetDir = "GoogleFindMyTools"

if (Test-Path $targetDir) {
    Write-Host "Directory '$targetDir' already exists. Skipping clone." -ForegroundColor Yellow
} else {
    Write-Host "Cloning GoogleFindMyTools repository..."
    git clone $repoUrl $targetDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository."
        exit 1
    }
    Write-Host "Successfully cloned repository." -ForegroundColor Green
}

# 4. Install Python Dependencies
Write-Host "Installing Python dependencies..."
Push-Location $targetDir
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install Python dependencies."
        Pop-Location
        exit 1
    }
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
} finally {
    Pop-Location
}

# 5. Check VS Code
Write-Host "Checking for Visual Studio Code..."
try {
    $codeVersion = code --version 2>&1
    Write-Host "Found VS Code." -ForegroundColor Green
} catch {
    Write-Warning "VS Code is not installed or not in PATH."
    Write-Host "It is recommended to install VS Code from https://code.visualstudio.com/"
}

# 6. Next Steps
Write-Host "`nSetup complete!" -ForegroundColor Cyan
Write-Host "----------------------------------------"
Write-Host "Next Steps:"
Write-Host "1. Ensure you have the ESP-IDF Extension installed in VS Code."
Write-Host "2. Run '.\register_tracker.ps1' to generate your advertisement key."
Write-Host "3. Follow instructions in 'firmware/README.md' to build and flash your ESP32."
Write-Host "----------------------------------------"
