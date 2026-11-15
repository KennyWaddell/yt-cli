@echo off
setlocal
cd /d "%~dp0"
title Crear Acceso Directo - YT-CLI

echo Creando acceso directo de YT-CLI en tu Escritorio...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'YT-CLI.lnk')); $s.TargetPath = '%~dp0YT-CLI.bat'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = '%SystemRoot%\System32\shell32.dll,220'; $s.Save()"

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  [OK] Acceso directo 'YT-CLI' creado en tu Escritorio.
    echo ========================================================
) else (
    echo.
    echo [AVISO] No se pudo crear el acceso directo de forma automatica.
)
echo.
pause
