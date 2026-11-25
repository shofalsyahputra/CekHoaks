@echo off
title Kompilasi APK CekHoaks Mobile
cls
echo ======================================================================
echo          PROSES KOMPILASI APK MOBILE - CEKHOAKS AI
echo ======================================================================
echo.

cd /d "%~dp0mobile_app"

where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Flutter SDK belum terdeteksi di variabel sistem PATH komputer Anda.
    echo.
    echo ----------------------------------------------------------------------
    echo OPSI CARA MEMBUAT / MEMASANG APK:
    echo ----------------------------------------------------------------------
    echo 1. OPSI A (Paling Mudah - Melalui Browser HP Anda):
    echo    - Buka Google Chrome di HP Android Anda.
    echo    - Buka alamat IP laptop Anda (misal: http://192.168.1.xxx:8080).
    echo    - Klik menu titik tiga (titik 3 di kanan atas Chrome).
    echo    - Pilih "Tambahkan ke Layar Utama" / "Install Aplikasi".
    echo    - Android akan otomatis membuat WebAPK resmi yang terpasang di HP!
    echo.
    echo 2. OPSI B (Buka Proyek di Android Studio / VS Code):
    echo    - Buka Android Studio atau VS Code.
    echo    - Pilih "Open Folder" dan arahkan ke folder "mobile_app".
    echo    - Jalankan build APK melalui menu: Build ^> Flutter ^> Build APK.
    echo.
    echo 3. OPSI C (Instal Flutter SDK via Command Line):
    echo    - Jalankan: winget install -e --id Google.Flutter
    echo    - Restart terminal, lalu jalankan kembali skrip build_apk.bat ini.
    echo ----------------------------------------------------------------------
    echo.
    pause
    exit /b 1
)

echo [*] Mengunduh dependensi Flutter (flutter pub get)...
call flutter pub get

echo.
echo [*] Memulai proses kompilasi APK Release (flutter build apk --release)...
echo [*] Harap tunggu, proses ini membutuhkan waktu beberapa menit...
call flutter build apk --release

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo [v] SUKSES! File APK telah berhasil dibuat di:
    echo     mobile_app\build\app\outputs\flutter-apk\app-release.apk
    echo ======================================================================
    echo.
    explorer.exe "build\app\outputs\flutter-apk"
) else (
    echo.
    echo [X] Gagal melakukan kompilasi APK. Silakan periksa pesan error di atas.
)

pause

