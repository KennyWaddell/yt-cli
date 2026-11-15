@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Descargador de Binarios Portables - YT-CLI

echo ========================================================
echo        YT-CLI: Configuracion de Binarios Portables
echo ========================================================
echo.
echo Este asistente descargara los binarios necesarios para que
echo YT-CLI funcione de forma 100%% autonoma sin tocar el PATH:
echo   - yt-dlp.exe (Motor de extraccion)
echo   - ffmpeg.exe (Procesador de audio MP3 y video MP4)
echo.

if not exist "bin" mkdir bin

echo [1/2] Descargando yt-dlp.exe oficial...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $wc = New-Object System.Net.WebClient; $wc.DownloadFile('https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe', 'bin\yt-dlp.exe')"

if exist "bin\yt-dlp.exe" (
    echo       [OK] yt-dlp.exe descargado con exito.
) else (
    echo       [AVISO] No se pudo descargar yt-dlp.exe automaticamente.
)

echo.
echo [2/2] MPV Player y FFmpeg:
echo Para el reproductor MPV y FFmpeg:
echo   1. Descarga MPV desde: https://mpv.io/installation/ o https://sourceforge.net/projects/mpv-player-windows/files/
echo   2. Copia 'mpv.exe' dentro de la carpeta 'bin\'
echo   3. Copia 'ffmpeg.exe' dentro de la carpeta 'bin\'
echo.
echo Si ya tienes MPV o FFmpeg instalados en tu sistema (PATH),
echo YT-CLI los detectara automaticamente sin necesidad de copiarlos.
echo.
echo ========================================================
echo Proceso finalizado. Ahora puedes ejecutar: YT-CLI.bat
echo ========================================================
echo.
pause
