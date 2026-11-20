#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de tests automatizados para YT-CLI (Linux CLI + Windows GUI).
Valida sintaxis, lógica de formatos, paridad de idiomas (i18n) y reglas de seguridad.
"""

import os
import py_compile
import re
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINDOWS_DIR = os.path.join(REPO_ROOT, "windows")
LANG_DIR = os.path.join(REPO_ROOT, "lang")
BIN_CLI = os.path.join(REPO_ROOT, "bin", "yt-cli")
INSTALL_SH = os.path.join(REPO_ROOT, "install.sh")
UNINSTALL_SH = os.path.join(REPO_ROOT, "uninstall.sh")

if WINDOWS_DIR not in sys.path:
    sys.path.insert(0, WINDOWS_DIR)

import locales_data  # noqa: E402
import yt_cli_gui  # noqa: E402


class DummyVar:
    def __init__(self, val):
        self._val = val

    def get(self):
        return self._val


class TestYtCliSuite(unittest.TestCase):
    def test_python_compile(self):
        """Todos los módulos Python de windows/ compilan sin errores de sintaxis."""
        for fname in ("yt_cli_gui.py", "locales_data.py", "setup_binaries.py"):
            fpath = os.path.join(WINDOWS_DIR, fname)
            py_compile.compile(fpath, doraise=True)

    def test_bash_syntax(self):
        """Los scripts shell y paquetes de idioma pasan bash -n."""
        targets = [BIN_CLI, INSTALL_SH, UNINSTALL_SH]
        for fname in sorted(os.listdir(LANG_DIR)):
            if fname.endswith(".sh"):
                targets.append(os.path.join(LANG_DIR, fname))
        for path in targets:
            res = subprocess.run(["bash", "-n", path], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Error de sintaxis en {path}: {res.stderr}")

    def test_windows_locales_completeness(self):
        """LANG_OPTIONS coincide con GUI_STRINGS y ningún idioma tiene claves faltantes o vacías."""
        option_codes = [code for code, _ in locales_data.LANG_OPTIONS]
        self.assertEqual(set(option_codes), set(locales_data.GUI_STRINGS.keys()))

        base_keys = set(locales_data.GUI_STRINGS["en"].keys())
        for code, strings in locales_data.GUI_STRINGS.items():
            missing = base_keys - set(strings.keys())
            self.assertFalse(missing, f"Faltan claves en locales_data[{code}]: {missing}")
            for k, v in strings.items():
                self.assertTrue(isinstance(v, str) and v.strip(), f"Valor vacío en {code}.{k}")

    def test_linux_lang_packs_structure(self):
        """Cada archivo lang/*.sh define LANG_CODE y LANG_NAME válidos, y en/es tienen paridad."""
        lang_keys = {}
        for fname in sorted(os.listdir(LANG_DIR)):
            if not fname.endswith(".sh"):
                continue
            code = fname[:-3]
            path = os.path.join(LANG_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(f'LANG_CODE="{code}"', content, f"Falta LANG_CODE en {fname}")
            self.assertRegex(content, r'LANG_NAME="[^"]+"', f"Falta LANG_NAME en {fname}")
            keys = set(re.findall(r"^(MSG_[A-Z0-9_]+)=", content, flags=re.MULTILINE))
            lang_keys[code] = keys

        self.assertIn("en", lang_keys)
        self.assertIn("es", lang_keys)
        self.assertEqual(
            lang_keys["en"],
            lang_keys["es"],
            f"Desfase de claves entre en.sh y es.sh: {lang_keys['en'] ^ lang_keys['es']}",
        )

    def test_parse_duration_to_seconds(self):
        """parse_duration_to_seconds convierte correctamente formatos HH:MM:SS y MM:SS."""
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds("03:45"), 225)
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds("1:20:00"), 4800)
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds("42"), 42)
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds("--:--"), 0)
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds("NA"), 0)
        self.assertEqual(yt_cli_gui.parse_duration_to_seconds(""), 0)

    def test_format_string_h264_and_fallback(self):
        """get_format_string prioriza H.264 (avc1) y mantiene fallback /best para otros sitios."""
        gui_stub = yt_cli_gui.YtCliGUI.__new__(yt_cli_gui.YtCliGUI)
        gui_stub.var_quality = DummyVar("720")
        gui_stub.var_fps = DummyVar("30")
        fmt = gui_stub.get_format_string()
        self.assertIn("[vcodec^=avc1]", fmt)
        self.assertIn("[height<=720]", fmt)
        self.assertIn("[fps<=30]", fmt)
        self.assertTrue(fmt.endswith("/best"))

        gui_stub.var_quality = DummyVar("1080")
        gui_stub.var_fps = DummyVar("Auto")
        fmt_auto = gui_stub.get_format_string()
        self.assertIn("[height<=1080]", fmt_auto)
        self.assertNotIn("[fps<=", fmt_auto)
        self.assertTrue(fmt_auto.endswith("/best"))

    def test_cli_and_gui_cookie_handling(self):
        """Las cookies se delegan a yt-dlp (--cookies-from-browser) sin persistirlas en texto plano."""
        with open(BIN_CLI, "r", encoding="utf-8") as f:
            cli_src = f.read()
        with open(os.path.join(WINDOWS_DIR, "yt_cli_gui.py"), "r", encoding="utf-8") as f:
            gui_src = f.read()

        self.assertIn("--cookies-from-browser", cli_src)
        self.assertIn("--cookies-from-browser", gui_src)
        self.assertIn("--hwdec=auto-safe", cli_src)
        self.assertIn("--hwdec=d3d11va,dxva2,no", gui_src)
        self.assertIn("--hwdec=no", gui_src)
        self.assertIn("--vo=gpu,direct3d,sdl", gui_src)
        self.assertIn("--fps", cli_src)
        self.assertIn("MAX_FPS", cli_src)
        self.assertIn("best[height<=${target_h}]", cli_src)
        self.assertIn("sponsorblock-mark=", cli_src)
        self.assertIn("sponsorblock-mark=", gui_src)

    def test_sponsorblock_profiles(self):
        """Los perfiles de SponsorBlock mapean correctamente a categorías yt-dlp."""
        gui_stub = yt_cli_gui.YtCliGUI.__new__(yt_cli_gui.YtCliGUI)
        gui_stub.sponsorblock_profile = "basic"
        self.assertEqual(gui_stub.get_sponsorblock_cats(), "sponsor,selfpromo")
        self.assertEqual(gui_stub.get_sponsorblock_cats("standard"), "sponsor,selfpromo,interaction,intro,outro")
        self.assertEqual(gui_stub.get_sponsorblock_cats("all"), "all")

    def test_build_trim_section(self):
        """build_trim_section valida rangos MM:SS y HH:MM:SS incluyendo duraciones largas."""
        self.assertEqual(yt_cli_gui.build_trim_section("00:00:00", "00:00:00"), "")
        self.assertEqual(yt_cli_gui.build_trim_section("00:00", "00:00"), "")
        self.assertEqual(yt_cli_gui.build_trim_section("01:15", "02:30"), "01:15-02:30")
        self.assertEqual(yt_cli_gui.build_trim_section("00:00:00", "12:00:00"), "00:00:00-12:00:00")
        with self.assertRaises(ValueError):
            yt_cli_gui.build_trim_section("02:00", "01:00")
        with self.assertRaises(ValueError):
            yt_cli_gui.build_trim_section("abc", "01:00")

    def test_gui_download_and_ux_fixes(self):
        """La GUI incluye Enter en tabla, conversión de carátula JPG para FLAC y sort por resolución."""
        with open(os.path.join(WINDOWS_DIR, "yt_cli_gui.py"), "r", encoding="utf-8") as f:
            gui_src = f.read()
        self.assertIn('self.tree.bind("<Return>"', gui_src)
        self.assertIn("--convert-thumbnails", gui_src)
        self.assertIn("res:{quality},fps:{fps},vcodec:h264", gui_src)
        self.assertIn("def open_help_dialog", gui_src)
        self.assertIn("--progress", gui_src)
        self.assertIn("--no-quiet", gui_src)
        self.assertIn("def toggle_downloads_view", gui_src)
        self.assertIn("def open_download_dir", gui_src)
        self.assertIn("def start_ytdlp_update", gui_src)
        self.assertIn('s["update_ytdlp"]', gui_src)

    def test_is_playlist_url(self):
        """is_playlist_url distingue URLs de playlist de vídeos individuales o enlaces ajenos."""
        self.assertTrue(yt_cli_gui.is_playlist_url("https://www.youtube.com/playlist?list=PL12345"))
        self.assertTrue(yt_cli_gui.is_playlist_url("https://youtube.com/watch?list=PL12345"))
        self.assertFalse(yt_cli_gui.is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL12345"))
        self.assertFalse(yt_cli_gui.is_playlist_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertFalse(yt_cli_gui.is_playlist_url("https://example.com/playlist?list=123"))

    def test_build_ffmpeg_local_trim_cmd(self):
        """build_ffmpeg_local_trim_cmd genera argumentos seguros para recorte local sin TLS."""
        cmd = yt_cli_gui.build_ffmpeg_local_trim_cmd("ffmpeg.exe", "in.mp4", "out.mp4", "00:01:00-00:02:30")
        self.assertEqual(
            cmd,
            [
                "ffmpeg.exe", "-y", "-ss", "60", "-t", "90",
                "-i", "in.mp4", "-map", "0", "-c", "copy",
                "-avoid_negative_ts", "make_zero", "out.mp4",
            ],
        )
        with self.assertRaises(ValueError):
            yt_cli_gui.build_ffmpeg_local_trim_cmd("ffmpeg.exe", "in.mp4", "out.mp4", "invalid")


if __name__ == "__main__":
    unittest.main()
