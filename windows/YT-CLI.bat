@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title YT-CLI

:: 1. Buscar Python instalado (PATH o ruta local de usuario Python 3.8)
call :find_python
if defined PY_CMD goto :check_bins

echo ========================================================
echo             YT-CLI - Asistente Inicial
echo ========================================================
echo.
echo [AVISO] No se encontro Python 3 instalado en este equipo.
echo.
set /p "INST_PY=Deseas descargar e instalar Python 3.8.10 (64-bit, compatible W7/8.1/10/11) ahora? [S/N]: "
if /i not "%INST_PY%"=="S" (
    echo.
    echo Instala Python manualmente desde https://www.python.org/downloads/release/python-3810/
    echo ^(Recuerda marcar "Add Python 3.8 to PATH"^)
    pause
    exit /b 1
)

echo.
echo Descargando Python 3.8.10 ^(64-bit^) desde python.org...
set "PY_INST=%TEMP%\python-3.8.10-amd64.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe', '%PY_INST%')"

if not exist "%PY_INST%" (
    echo [ERROR] No se pudo descargar el instalador de Python.
    pause
    exit /b 1
)

echo Instalando Python 3.8.10 en tu usuario ^(sin permisos de administrador^)...
"%PY_INST%" /passive InstallAllUsers=0 PrependPath=1 Include_test=0
del /f /q "%PY_INST%" >nul 2>&1

call :find_python
if not defined PY_CMD (
    echo [ERROR] La instalacion no se completo o Python no esta disponible aun.
    pause
    exit /b 1
)

:check_bins
if not exist "bin\yt-dlp.exe" (
    echo [AVISO] Faltan binarios en bin\. Ejecutando descargador automatico...
    call descargar_binarios.bat
)

:launch
start "" "%PY_CMD%" yt_cli_gui.py
exit /b 0

:find_python
set "PY_CMD="
for %%P in (pythonw pyw python py) do (
    where %%P >nul 2>&1 && (
        set "PY_CMD=%%P"
        goto :eof
    )
)
if exist "%LOCALAPPDATA%\Programs\Python\Python38\pythonw.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python38\pythonw.exe"
    goto :eof
)
if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    goto :eof
)
goto :eof
