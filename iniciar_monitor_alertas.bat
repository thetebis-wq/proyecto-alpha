@echo off
title Proyecto Alpha - Vigilante de Mercado (Telegram)
cd /d "%~dp0"
echo ===================================================
echo   INICIANDO VIGILANTE DE MERCADO PROYECTO ALPHA
echo ===================================================
echo.
echo Monitoreando Bitcoin, Ethereum y Solana...
echo Las alertas se enviaran automaticamente a tu Telegram.
echo Para detener el monitor, simplemente cierra esta ventana.
echo.
.\.venv\Scripts\python.exe -m src.alerts.market_monitor --interval 15
pause
