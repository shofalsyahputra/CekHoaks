@echo off
title Installer Otomatis Kebutuhan Pengembangan CekHoaks Mobile
color 0B
echo ======================================================================
echo   INSTALLER OTOMATIS: GIT, PYTHON, JDK, FLUTTER, & ANDROID STUDIO
echo ======================================================================
echo.
echo Pastikan Anda terhubung ke internet.
echo Proses ini akan mengunduh dan memasang aplikasi pengembangan resmi
echo secara otomatis menggunakan Windows Package Manager (winget).
echo.
pause

echo.
echo [1/5] Menginstal Git for Windows...
winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements

echo.
echo [2/5] Menginstal Python 3.12 resmi...
winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements

echo.
echo [3/5] Menginstal Java Development Kit (Microsoft OpenJDK 17)...
winget install --id Microsoft.OpenJDK.17 -e --source winget --accept-source-agreements --accept-package-agreements

echo.
echo [4/5] Menginstal Flutter SDK...
winget install --id Google.Flutter -e --source winget --accept-source-agreements --accept-package-agreements

echo.
echo [5/5] Menginstal Android Studio...
winget install --id Google.AndroidStudio -e --source winget --accept-source-agreements --accept-package-agreements

echo.
echo ======================================================================
echo   PROSES INSTALASI SELESAI!
echo ======================================================================
echo Silakan tutup jendela ini dan RESTART LAPTOP / Buka terminal baru
echo agar seluruh System Environment PATH diperbarui.
echo.
pause

