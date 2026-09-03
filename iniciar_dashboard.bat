@echo off
title Proyecto Alpha - Terminal de Mercado
cd /d "%~dp0"
echo ===================================================
echo   INICIANDO PROYECTO ALPHA - DASHBOARD INTERACTIVO
echo ===================================================
echo.
echo Abriendo servidor local en el navegador...
.\.venv\Scripts\streamlit.exe run app.py
pause
