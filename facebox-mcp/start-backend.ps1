# FaceBox 後端啟動腳本
# 使用方式: .\start-backend.ps1

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$BackendDir = Join-Path $ProjectRoot "facebox"

Write-Host "=== FaceBox 後端啟動 ===" -ForegroundColor Cyan
Write-Host "專案目錄: $BackendDir"
Write-Host "API 位置: http://127.0.0.1:17494"
Write-Host ""

# 檢查 Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "錯誤: 找不到 Python，請先安裝 Python 3.10+" -ForegroundColor Red
    exit 1
}

# 檢查/建立虛擬環境
$VenvDir = Join-Path $BackendDir "venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "建立虛擬環境..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

# 啟動虛擬環境並安裝依賴
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript

Write-Host "安裝依賴..." -ForegroundColor Yellow
pip install -r (Join-Path $BackendDir "backend\requirements.txt") -q

# 啟動後端
Write-Host ""
Write-Host "啟動 FaceBox 後端..." -ForegroundColor Green
Write-Host "請確保 SD WebUI (A1111) 已在 http://127.0.0.1:7860 運行" -ForegroundColor Yellow
Write-Host ""

Set-Location $BackendDir
python -m backend.main
