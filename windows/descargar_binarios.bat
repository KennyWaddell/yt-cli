@echo off
setlocal
cd /d "%~dp0"
title Descargador de Binarios Portables - YT-CLI

where python >nul 2>&1
if %errorlevel% equ 0 (
    python setup_binaries.py
    echo.
    pause
    exit /b %errorlevel%
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    py setup_binaries.py
    echo.
    pause
    exit /b %errorlevel%
)

echo [ERROR] No se encontro Python 3 en el sistema.
echo Instala Python desde https://www.python.org/ marcando "Add python.exe to PATH".
pause
exit /b 1
