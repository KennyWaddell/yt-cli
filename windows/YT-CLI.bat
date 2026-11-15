@echo off
setlocal
cd /d "%~dp0"
title YT-CLI

:: 1. Verificar si existen los binarios en bin/
if not exist "bin\yt-dlp.exe" (
    echo ========================================================
    echo             YT-CLI - Version Portable Windows
    echo ========================================================
    echo.
    echo [AVISO] No se encontraron los binarios en la carpeta bin\
    echo Para que YT-CLI pueda reproducir y descargar videos,
    echo ejecuta primero el archivo:
    echo.
    echo       descargar_binarios.bat
    echo.
    echo Presiona cualquier tecla para continuar de todos modos...
    pause >nul
)

:: 2. Buscar ejecutor de Python (priorizar pythonw para evitar ventana de consola negra)
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw yt_cli_gui.py
    exit /b 0
)

where pyw >nul 2>&1
if %errorlevel% equ 0 (
    start "" pyw yt_cli_gui.py
    exit /b 0
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    start "" python yt_cli_gui.py
    exit /b 0
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    start "" py yt_cli_gui.py
    exit /b 0
)

echo.
echo [ERROR] No se encontro Python 3 instalado en este equipo.
echo Instala Python desde https://www.python.org/
echo (Recuerda marcar la casilla: "Add python.exe to PATH")
echo.
pause
exit /b 1
