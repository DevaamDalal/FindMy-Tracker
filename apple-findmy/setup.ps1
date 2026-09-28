Write-Host "Setting up Apple Find My (Macless-Haystack) Environment..." -ForegroundColor Cyan

# Check Python 3
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pyVersion = python --version
    Write-Host "Found Python: $pyVersion" -ForegroundColor Green
} else {
    Write-Host "WARNING: Python 3 is not installed or not in PATH." -ForegroundColor Yellow
}

# Check Docker
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "Found Docker." -ForegroundColor Green
} else {
    Write-Host "WARNING: Docker is not installed or not in PATH." -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host "Installing Python dependencies (cryptography, esptool)..." -ForegroundColor Cyan
pip install cryptography esptool

# Create keys directory
$keysDir = "keys"
if (-Not (Test-Path $keysDir)) {
    New-Item -ItemType Directory -Force -Path $keysDir | Out-Null
    Write-Host "Created $keysDir directory." -ForegroundColor Green
} else {
    Write-Host "$keysDir directory already exists." -ForegroundColor Green
}

Write-Host "`nSetup complete! Next steps:" -ForegroundColor Cyan
Write-Host "1. Run 'python generate_keys.py' to generate your keys."
Write-Host "2. Run 'docker-compose up -d' to start the servers."
