@echo off
setlocal
cd /d "%~dp0"
title Compilar YT-CLI a EXE Nativo - Windows

echo ========================================================
echo       YT-CLI: Generador de Ejecutable Unico (.exe)
echo ========================================================
echo.

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] PyInstaller no esta instalado o no se encuentra en PATH.
    echo Instalando PyInstaller mediante pip...
    pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo instalar PyInstaller.
        pause
        exit /b 1
    )
)

echo Compilando yt_cli_gui.py con icono oficial app.ico...
pyinstaller --noconsole --onefile --icon=app.ico --add-data "app.ico;." --name=YT-CLI yt_cli_gui.py

if %errorlevel% equ 0 (
    echo.
    echo Copiando YT-CLI.exe a la carpeta principal...
    copy /y "dist\YT-CLI.exe" "%~dp0YT-CLI.exe" >nul
    echo.
    echo ========================================================
    echo  [OK] Compilacion finalizada con exito!
    echo  Ya tienes "YT-CLI.exe" listo en esta carpeta.
    echo ========================================================
) else (
    echo.
    echo [ERROR] Ocurrio un fallo durante la compilacion.
)
echo.
pause
