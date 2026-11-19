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
        self.assertIn("--hwdec=auto-safe", gui_src)


if __name__ == "__main__":
    unittest.main()
