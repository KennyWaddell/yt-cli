#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de tests automatizados para YT-CLI (Linux CLI + Windows GUI).
Valida sintaxis, lógica de formatos, paridad de idiomas (i18n) y reglas de seguridad.
"""

import io
import os
import py_compile
import queue
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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
        self.assertIn("def clear_downloads_from_view", gui_src)
        self.assertIn('s["dl_clear_all"]', gui_src)
        self.assertNotIn("dialog.grab_set()", gui_src)
        self.assertIn("--dither=no", gui_src)
        self.assertIn("--log-file=", gui_src)
        self.assertIn("override_urls", gui_src)
        self.assertIn("timeout=3", gui_src)
        self.assertNotIn('self.current_lang == "en"', gui_src)

        with open(os.path.join(WINDOWS_DIR, "setup_binaries.py"), "r", encoding="utf-8") as f:
            setup_src = f.read()
        self.assertNotIn("_create_unverified_context", setup_src)
        self.assertIn("create_default_context", setup_src)

    def test_terminate_process_tree_fallback(self):
        """terminate_process_tree intenta matar el proceso y usa terminate() si sigue vivo."""
        proc = mock.MagicMock()
        proc.pid = 4242
        proc.poll.return_value = None
        with mock.patch.object(yt_cli_gui.subprocess, "run", side_effect=subprocess.TimeoutExpired("taskkill", 3)):
            yt_cli_gui.terminate_process_tree(proc)
        proc.terminate.assert_called_once()

    def test_format_ytdlp_error(self):
        """format_ytdlp_error traduce bloqueos DPAPI de Chromium y HTTP 429 con guía clara."""
        dpapi = yt_cli_gui.format_ytdlp_error(
            "ERROR: Failed to decrypt with DPAPI. See https://github.com/yt-dlp/yt-dlp/issues/10927",
            is_en=False,
        )
        self.assertIn("Firefox", dpapi)
        self.assertIn("App-Bound Encryption", dpapi)
        err429 = yt_cli_gui.format_ytdlp_error("ERROR: HTTP Error 429: Too Many Requests", is_en=True)
        self.assertIn("429", err429)
        self.assertEqual(yt_cli_gui.format_ytdlp_error("plain error", is_en=False), "plain error")

    def test_is_playlist_url(self):
        """is_playlist_url distingue URLs de playlist de vídeos individuales o enlaces ajenos."""
        self.assertTrue(yt_cli_gui.is_playlist_url("https://www.youtube.com/playlist?list=PL12345"))
        self.assertTrue(yt_cli_gui.is_playlist_url("https://youtube.com/watch?list=PL12345"))
        self.assertTrue(yt_cli_gui.is_playlist_url("https://music.youtube.com/playlist?list=PL12345"))
        self.assertFalse(yt_cli_gui.is_playlist_url("https://youtu.be/dQw4w9WgXcQ?list=PL12345"))
        self.assertFalse(yt_cli_gui.is_playlist_url("https://www.youtube.com/playlist?list="))
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

    def _make_worker_stub(self, dl_dir):
        stub = yt_cli_gui.YtCliGUI.__new__(yt_cli_gui.YtCliGUI)
        stub.current_lang = "es"
        stub.msg_queue = queue.Queue()
        stub.active_process = "dl-sentinel"
        stub.search_process = None
        stub.is_cancelled = False
        stub._is_searching = False
        stub._is_downloading = False
        stub.download_dir = dl_dir
        stub.get_selected_cookie_browser = lambda: None
        return stub

    def test_search_worker_error_preserves_download_process_and_parses_na(self):
        """_search_worker aísla search_process, emite search_error en fallo y normaliza canales NA."""
        stub = self._make_worker_stub(tempfile.gettempdir())
        fake_err_proc = mock.MagicMock(returncode=1)
        fake_err_proc.communicate.return_value = ("", "ERROR: Private playlist")
        with mock.patch.object(yt_cli_gui.subprocess, "Popen", return_value=fake_err_proc):
            stub._search_worker("https://www.youtube.com/playlist?list=PLprivate", "25")
        self.assertEqual(stub.active_process, "dl-sentinel")
        self.assertIsNone(stub.search_process)
        msgs = [stub.msg_queue.get_nowait() for _ in range(stub.msg_queue.qsize())]
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0][0], "search_error")
        self.assertIn("Private playlist", msgs[0][1])

        fake_ok_proc = mock.MagicMock(returncode=0)
        fake_ok_proc.communicate.return_value = ("Video Demo\tNA\t03:20\tabc12345678\n", "")
        with mock.patch.object(yt_cli_gui.subprocess, "Popen", return_value=fake_ok_proc):
            stub._search_worker("demo", "15")
        kind, items = stub.msg_queue.get_nowait()
        self.assertEqual(kind, "search_done")
        self.assertEqual(items, [("Video Demo", "—", "03:20", "abc12345678")])

    def test_subtitles_worker_429_and_empty_srt(self):
        """_subtitles_worker detecta HTTP 429 y falla explícitamente si no se generó ningún .srt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stub = self._make_worker_stub(tmpdir)
            proc_429 = mock.MagicMock(returncode=1)
            proc_429.stdout = io.StringIO("ERROR: Unable to download video subtitles for 'es': HTTP Error 429: Too Many Requests\n")
            with mock.patch.object(yt_cli_gui.subprocess, "Popen", return_value=proc_429):
                stub._subtitles_worker(["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])
            msgs = [stub.msg_queue.get_nowait() for _ in range(stub.msg_queue.qsize())]
            err_msgs = [m for m in msgs if m[0] == "error"]
            self.assertTrue(err_msgs and "429" in err_msgs[0][1])
            self.assertEqual(msgs[-1][0], "download_error")

            stub_empty = self._make_worker_stub(tmpdir)
            proc_empty = mock.MagicMock(returncode=0)
            proc_empty.stdout = io.StringIO("[info] There are no subtitles for the requested languages\n")
            with mock.patch.object(yt_cli_gui.subprocess, "Popen", return_value=proc_empty):
                stub_empty._subtitles_worker(["https://www.youtube.com/watch?v=UbC7iRA_O3g"])
            msgs_empty = [stub_empty.msg_queue.get_nowait() for _ in range(stub_empty.msg_queue.qsize())]
            self.assertTrue(any(m[0] == "error" and "No hay subtítulos disponibles" in m[1] for m in msgs_empty))
            self.assertEqual(msgs_empty[-1][0], "download_error")

    def test_download_concurrency_guard(self):
        """start_download y start_subtitles_download bloquean lanzamientos simultáneos."""
        stub = self._make_worker_stub(tempfile.gettempdir())
        stub._is_downloading = True
        with mock.patch.object(yt_cli_gui.messagebox, "showinfo") as mock_info, \
                mock.patch.object(yt_cli_gui.threading, "Thread") as mock_thread:
            stub.start_download(override_items=[("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Test")])
            stub.start_subtitles_download()
        self.assertEqual(mock_info.call_count, 2)
        mock_thread.assert_not_called()


if __name__ == "__main__":
    unittest.main()
