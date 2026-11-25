# Script Peluncur Server Backend CekHoaks Mobile
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   MEMULAI SERVER BACKEND & MOBILE WEB CEKHOAKS AI" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$sysPython = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $sysPython) {
    Write-Host "[*] Menggunakan Python 3.12 Resmi: $sysPython" -ForegroundColor Green
    & $sysPython -u (Join-Path $PSScriptRoot "run_server.py") 8080
} elseif (Test-Path $venvPython) {
    Write-Host "[*] Menggunakan Python Virtualenv: $venvPython" -ForegroundColor Green
    & $venvPython -u (Join-Path $PSScriptRoot "run_server.py") 8080
} else {
    Write-Host "[*] Mencari uv runner..." -ForegroundColor Yellow
    & C:\Users\$env:USERNAME\.local\bin\uv.exe run python -u (Join-Path $PSScriptRoot "run_server.py") 8080
}

