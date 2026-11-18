#!/usr/bin/env python3
"""
Descargador automático de binarios portables para YT-CLI (Windows).
Descarga yt-dlp.exe, ffmpeg.exe y mpv.exe dentro de windows/bin/ sin tocar el PATH.
"""

import json
import os
import shutil
import ssl
import subprocess
import sys
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
TEMP_DIR = os.path.join(BASE_DIR, "_tmp_dl")

URL_YTDLP = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
URL_FFMPEG_ZIP = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
# Compilación universal de mpv compatible con Windows 7 SP1, 8.1, 10 y 11
# (v0.37.0 sin dependencia estricta de AdjustWindowRectExForDpi de Windows 10)
URL_MPV_7Z = "https://sourceforge.net/projects/mpv-player-windows/files/64bit/mpv-x86_64-20231126-git-6898d57.7z/download"
URL_VULKAN_ZIP = "https://sdk.lunarg.com/sdk/download/1.3.296.0/windows/VulkanRT-1.3.296.0-Components.zip"
URL_7ZR = "https://www.7-zip.org/a/7zr.exe"


def download_file(url, dest_path, label):
    print(f"  -> Descargando {label}...")
    curl_bin = shutil.which("curl") or shutil.which("curl.exe")
    if curl_bin:
        res = subprocess.run([curl_bin, "-fSL", "--retry", "3", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "-o", dest_path, url])
        if res.returncode == 0 and os.path.isfile(dest_path) and os.path.getsize(dest_path) > 0:
            print(f"  [OK] {label} descargado con curl.")
            return

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    req = urllib.request.Request(url, headers=headers)
    ctx = getattr(ssl, "_create_unverified_context", None)
    context_arg = {"context": ctx()} if ctx else {}
    with urllib.request.urlopen(req, timeout=120, **context_arg) as resp, open(dest_path, "wb") as out:
        total = int(resp.headers.get("Content-Length") or 0)
        downloaded = 0
        chunk_size = 65536
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = int(downloaded * 100 / total)
                mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                print(f"\r     Progreso: {pct}% ({mb:.1f} / {total_mb:.1f} MB)", end="", flush=True)
    if total > 0:
        print()


def setup_ytdlp(force=False):
    dest = os.path.join(BIN_DIR, "yt-dlp.exe")
    print("\n[1/4] yt-dlp.exe")
    if not force and os.path.isfile(dest):
        print("  [OK] yt-dlp.exe ya existe en bin/ (omitido).")
        return
    download_file(URL_YTDLP, dest, "yt-dlp.exe")
    print("  [OK] yt-dlp.exe listo.")


def setup_ffmpeg(force=False):
    dest = os.path.join(BIN_DIR, "ffmpeg.exe")
    print("\n[2/4] ffmpeg.exe")
    if not force and os.path.isfile(dest):
        print("  [OK] ffmpeg.exe ya existe en bin/ (omitido).")
        return
    zip_path = os.path.join(TEMP_DIR, "ffmpeg.zip")
    download_file(URL_FFMPEG_ZIP, zip_path, "FFmpeg (paquete oficial .zip)")

    print("  -> Extrayendo ffmpeg.exe...")
    found = False
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("/bin/ffmpeg.exe") or member == "ffmpeg.exe":
                with zf.open(member) as src, open(dest, "wb") as out:
                    shutil.copyfileobj(src, out)
                found = True
                break
    if not found:
        raise RuntimeError("No se encontró ffmpeg.exe dentro del archivo .zip.")
    print("  [OK] ffmpeg.exe listo.")


def find_7z_command():
    candidates = [
        "7z", "7za", "7zr",
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
        r"C:\ProgramData\chocolatey\bin\7z.exe"
    ]
    for cmd in candidates:
        if os.path.isabs(cmd):
            if os.path.isfile(cmd):
                return cmd
        else:
            found = shutil.which(cmd)
            if found:
                return found
    if sys.platform.startswith("win"):
        seven_zr = os.path.join(TEMP_DIR, "7zr.exe")
        download_file(URL_7ZR, seven_zr, "7zr.exe (descompresor temporal)")
        return seven_zr
    raise RuntimeError("No se encontró 7z/7za en el sistema para extraer el paquete .7z.")


def setup_mpv(force=False):
    print("\n[3/4] mpv.exe (Universal Win 7/8.1/10/11)")
    dest = os.path.join(BIN_DIR, "mpv.exe")
    if not force and os.path.isfile(dest):
        print("  [OK] mpv.exe ya existe en bin/ (omitido).")
        return
    mpv_name = "mpv-x86_64-20231126-git-6898d57.7z"
    archive_path = os.path.join(TEMP_DIR, mpv_name)
    extract_dir = os.path.join(TEMP_DIR, "mpv_extract")
    os.makedirs(extract_dir, exist_ok=True)

    download_file(URL_MPV_7Z, archive_path, mpv_name)
    extractor = find_7z_command()

    print("  -> Extrayendo mpv.exe y librerías...")
    res = subprocess.run(
        [extractor, "x", archive_path, f"-o{extract_dir}", "-y"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Error al extraer {mpv_name}: {res.stderr}")

    copied = 0
    for root_dir, _, files in os.walk(extract_dir):
        for fname in files:
            low = fname.lower()
            if low in ("mpv.exe", "mpv.com") or low.endswith(".dll"):
                shutil.copy2(os.path.join(root_dir, fname), os.path.join(BIN_DIR, fname))
                copied += 1

    if not os.path.isfile(os.path.join(BIN_DIR, "mpv.exe")):
        raise RuntimeError("No se encontró mpv.exe después de extraer el paquete.")
    print(f"  [OK] mpv.exe listo ({copied} archivo(s) copiado(s) a bin/).")


def setup_vulkan(force=False):
    dest = os.path.join(BIN_DIR, "vulkan-1.dll")
    print("\n[4/4] vulkan-1.dll (Compatibilidad universal)")
    if not force and os.path.isfile(dest):
        print("  [OK] vulkan-1.dll ya existe en bin/ (omitido).")
        return
    zip_path = os.path.join(TEMP_DIR, "vulkan.zip")
    download_file(URL_VULKAN_ZIP, zip_path, "Vulkan Runtime Components (.zip)")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("x64/vulkan-1.dll"):
                with zf.open(member) as src, open(dest, "wb") as out:
                    shutil.copyfileobj(src, out)
                break
    if not os.path.isfile(dest):
        raise RuntimeError("No se encontró vulkan-1.dll dentro de VulkanRT-Components.zip.")
    print("  [OK] vulkan-1.dll listo.")


def main():
    force = "--force" in sys.argv or "-f" in sys.argv
    print("========================================================")
    print("       YT-CLI: Descarga Automatica de Binarios")
    print("========================================================")
    if force:
        print(" [MODO FORZADO] Se re-descargaran todos los binarios.")
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    try:
        setup_ytdlp(force=force)
        setup_ffmpeg(force=force)
        setup_mpv(force=force)
        try:
            setup_vulkan(force=force)
        except Exception as v_err:
            print(f"  [AVISO] vulkan-1.dll no pudo descargarse (opcional): {v_err}")
        print("\n========================================================")
        print(" [COMPLETADO] Todos los binarios estan listos en bin/")
        print(" Ya puedes ejecutar YT-CLI.bat sin instalar nada mas.")
        print("========================================================")
    except Exception as exc:
        import traceback
        print(f"\n[ERROR CRITICO] {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
