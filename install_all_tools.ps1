# Script Installer Otomatis Kebutuhan Pengembangan via PowerShell
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  INSTALLER OTOMATIS DEPENDENSI PENGEMBANGAN CEKHOAKS MOBILE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pastikan laptop terhubung ke internet." -ForegroundColor Yellow
Write-Host ""

$tools = @(
    @{ Name = "Git for Windows"; Id = "Git.Git" },
    @{ Name = "Python 3.12 Resmi"; Id = "Python.Python.3.12" },
    @{ Name = "Microsoft OpenJDK 17 (Java)"; Id = "Microsoft.OpenJDK.17" },
    @{ Name = "Flutter SDK"; Id = "Google.Flutter" },
    @{ Name = "Android Studio"; Id = "Google.AndroidStudio" }
)

$i = 1
foreach ($tool in $tools) {
    Write-Host "[$i/5] Sedang mengunduh dan memasang $($tool.Name)..." -ForegroundColor Green
    winget install --id $tool.Id -e --source winget --accept-source-agreements --accept-package-agreements
    $i++
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  SEMUA ALAT BERHASIL DIPASANG!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Silakan buka terminal baru atau restart laptop agar PATH sistem aktif." -ForegroundColor Yellow

