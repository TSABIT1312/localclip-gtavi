@echo off
setlocal
cd /d "%~dp0"
echo ===================================================
echo   LocalClip GTA VI - Auto Clipper (Windows)
echo ===================================================
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    python -m uvicorn app:app --host 127.0.0.1 --port 8765
) else (
    echo [INFO] Menjalankan dengan Python sistem...
    python -m uvicorn app:app --host 127.0.0.1 --port 8765
)
pause
