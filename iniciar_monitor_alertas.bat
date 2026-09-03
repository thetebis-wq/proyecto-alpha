@echo off
title Proyecto Alpha - Vigilante de Mercado (Telegram 24/7)
cd /d "%~dp0"
echo ===================================================
echo   INICIANDO VIGILANTE DE MERCADO PROYECTO ALPHA
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

echo Monitoreando Bitcoin, Ethereum y Solana...
echo Las alertas se enviaran automaticamente a tu Telegram.
echo Los eventos se registraran en data/monitor.log
echo Para detener el monitor, simplemente presiona Ctrl+C o cierra esta ventana.
echo.
.\.venv\Scripts\python.exe -m src.alerts.market_monitor --interval 15
pause
