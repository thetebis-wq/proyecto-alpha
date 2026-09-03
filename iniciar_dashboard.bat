@echo off
title Proyecto Alpha - Terminal Cuantitativa (Streamlit)
cd /d "%~dp0"
echo ===================================================
echo   INICIANDO PROYECTO ALPHA - DASHBOARD INTERACTIVO
echo ===================================================
echo.

if not exist ".\.venv\Scripts\python.exe" (
    echo [ERROR] No se detecto el entorno virtual .venv.
    echo Por favor ejecuta: python -m venv .venv
    echo e instala las dependencias con: .\.venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Abriendo servidor local en el navegador (http://localhost:8501)...
echo.
.\.venv\Scripts\python.exe -m streamlit run app.py
pause
