Write-Host "=== MEMASANG FLUTTER SDK OTOMATIS ===" -ForegroundColor Cyan

if (-not (Test-Path "C:\src")) {
    New-Item -ItemType Directory -Path "C:\src" -Force | Out-Null
}

$gitPath = "C:\Program Files\Git\cmd\git.exe"
if (-not (Test-Path $gitPath)) {
    Write-Host "Git belum ditemukan di C:\Program Files\Git\cmd\git.exe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "C:\src\flutter\bin\flutter.bat")) {
    Write-Host "[1/3] Sedang mengunduh Flutter SDK stable (shallow clone ~200MB)..." -ForegroundColor Yellow
    & $gitPath clone https://github.com/flutter/flutter.git -b stable C:\src\flutter --depth 1
} else {
    Write-Host "[1/3] Folder C:\src\flutter sudah ada." -ForegroundColor Green
}

Write-Host "[2/3] Mendaftarkan C:\src\flutter\bin ke PATH sistem..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike '*C:\src\flutter\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $userPath + ';C:\src\flutter\bin', 'User')
    Write-Host "PATH Flutter berhasil didaftarkan!" -ForegroundColor Green
} else {
    Write-Host "PATH Flutter sudah terdaftar sebelumnya." -ForegroundColor Green
}

Write-Host "[3/3] Menjalankan inisialisasi awal Flutter..." -ForegroundColor Yellow
$env:PATH = "$env:PATH;C:\src\flutter\bin;C:\Program Files\Git\cmd"
& "C:\src\flutter\bin\flutter.bat" --version

Write-Host ""
Write-Host "=== INSTALASI FLUTTER SELESAI ===" -ForegroundColor Cyan

