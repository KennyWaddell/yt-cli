#!/usr/bin/env python3
"""
Descargador automático de binarios portables para YT-CLI (Windows).
Descarga yt-dlp.exe, ffmpeg.exe y mpv.exe dentro de windows/bin/ sin tocar el PATH.
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
TEMP_DIR = os.path.join(BASE_DIR, "_tmp_dl")

URL_YTDLP = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
URL_FFMPEG_ZIP = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
URL_MPV_API = "https://api.github.com/repos/shinchiro/mpv-winbuild-cmake/releases/latest"
URL_7ZR = "https://www.7-zip.org/a/7zr.exe"


def download_file(url, dest_path, label):
    print(f"  -> Descargando {label}...")
    req = urllib.request.Request(url, headers={"User-Agent": "YT-CLI-Setup/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest_path, "wb") as out:
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


def setup_ytdlp():
    dest = os.path.join(BIN_DIR, "yt-dlp.exe")
    print("\n[1/3] yt-dlp.exe")
    download_file(URL_YTDLP, dest, "yt-dlp.exe")
    print("  [OK] yt-dlp.exe listo.")


def setup_ffmpeg():
    dest = os.path.join(BIN_DIR, "ffmpeg.exe")
    print("\n[2/3] ffmpeg.exe")
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


def get_mpv_asset_url():
    req = urllib.request.Request(URL_MPV_API, headers={"User-Agent": "YT-CLI-Setup/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Preferir compilación estándar x86_64 (sin -v3) para compatibilidad con CPUs modestas/antiguas
    fallback_url = None
    for asset in data.get("assets", []):
        name = asset.get("name", "")
        if name.startswith("mpv-x86_64-") and name.endswith(".7z"):
            if "-v3-" not in name and "dev" not in name:
                return asset["browser_download_url"], name
            if fallback_url is None and "dev" not in name:
                fallback_url = (asset["browser_download_url"], name)
    if fallback_url:
        return fallback_url
    raise RuntimeError("No se encontró el paquete mpv-x86_64-*.7z en GitHub Releases.")


def find_7z_command():
    for cmd in ("7z", "7za", "7zr"):
        found = shutil.which(cmd)
        if found:
            return found
    if sys.platform.startswith("win"):
        seven_zr = os.path.join(TEMP_DIR, "7zr.exe")
        download_file(URL_7ZR, seven_zr, "7zr.exe (descompresor temporal)")
        return seven_zr
    raise RuntimeError("No se encontró 7z/7za en el sistema para extraer el paquete .7z.")


def setup_mpv():
    print("\n[3/3] mpv.exe")
    mpv_url, mpv_name = get_mpv_asset_url()
    archive_path = os.path.join(TEMP_DIR, mpv_name)
    extract_dir = os.path.join(TEMP_DIR, "mpv_extract")
    os.makedirs(extract_dir, exist_ok=True)

    download_file(mpv_url, archive_path, mpv_name)
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


def main():
    print("========================================================")
    print("       YT-CLI: Descarga Automatica de Binarios")
    print("========================================================")
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    try:
        setup_ytdlp()
        setup_ffmpeg()
        setup_mpv()
        print("\n========================================================")
        print(" [COMPLETADO] Todos los binarios estan listos en bin/")
        print(" Ya puedes ejecutar YT-CLI.bat sin instalar nada mas.")
        print("========================================================")
    except Exception as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
