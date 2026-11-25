@echo off
title CekHoaks Mobile Server
cls
echo ======================================================================
echo    MEMULAI SERVER BACKEND & MOBILE WEB CEKHOAKS AI
echo ======================================================================
echo.

echo [*] Membuka browser otomatis ke http://localhost:8080...
start http://localhost:8080

set "SYS_PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if exist "%SYS_PYTHON%" (
    echo [*] Menggunakan Python 3.12 Resmi: %SYS_PYTHON%
    "%SYS_PYTHON%" -u run_server.py 8080
) else if exist ".venv\Scripts\python.exe" (
    echo [*] Menggunakan lingkungan Python Virtualenv (.venv)...
    .venv\Scripts\python.exe -u run_server.py 8080
) else if exist "C:\Users\%USERNAME%\.local\bin\uv.exe" (
    echo [*] Menggunakan UV Python Runner...
    C:\Users\%USERNAME%\.local\bin\uv.exe run python -u run_server.py 8080
) else (
    echo [*] Menjalankan python sistem...
    python -u run_server.py 8080
)

pause

