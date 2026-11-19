#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YT-CLI - Cliente multimedia ultraligero y portable
Diseño moderno y minimalista para Linux y Windows (7 SP1, 8.1, 10)
"""

import os
import sys
import subprocess
import threading
import queue
import json
import time
import glob
import re
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from locales_data import LANG_OPTIONS, GUI_STRINGS

IS_WINDOWS = sys.platform.startswith("win")

if IS_WINDOWS:
    try:
        import ctypes
        # SEM_FAILCRITICALERRORS (0x0001) | SEM_NOOPENFILEERRORBOX (0x8000)
        # Suprime ventanas de error críticas del sistema operativo como "No hay disco en la unidad",
        # heredándose automáticamente a subprocesos hijos (ffmpeg.exe, yt-dlp.exe).
        ctypes.windll.kernel32.SetErrorMode(0x0001 | 0x8000)
    except Exception:
        pass

def is_browser_installed(browser_name):
    """Comprueba si el navegador seleccionado existe realmente en el sistema antes de pedirle cookies."""
    b = str(browser_name).lower().strip()
    if b in ("ninguna", "", "none"):
        return True
    user_home = os.path.expanduser("~")
    if IS_WINDOWS:
        appdata = os.environ.get("APPDATA", "")
        localappdata = os.environ.get("LOCALAPPDATA", "")
        checks = {
            "firefox": [os.path.join(appdata, "Mozilla", "Firefox")],
            "chrome": [os.path.join(localappdata, "Google", "Chrome")],
            "edge": [os.path.join(localappdata, "Microsoft", "Edge")],
            "brave": [os.path.join(localappdata, "BraveSoftware", "Brave-Browser")],
            "chromium": [os.path.join(localappdata, "Chromium")]
        }
    else:
        checks = {
            "firefox": [os.path.join(user_home, ".mozilla", "firefox")],
            "chrome": [os.path.join(user_home, ".config", "google-chrome")],
            "edge": [os.path.join(user_home, ".config", "microsoft-edge")],
            "brave": [os.path.join(user_home, ".config", "BraveSoftware", "Brave-Browser")],
            "chromium": [os.path.join(user_home, ".config", "chromium")]
        }
    paths = checks.get(b, [])
    return any(os.path.exists(p) for p in paths)

def get_base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_config_dir():
    if IS_WINDOWS:
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.path.join(os.path.expanduser("~"), ".config")
    cfg = os.path.join(base, "yt-cli")
    os.makedirs(cfg, exist_ok=True)
    return cfg

def get_history_file():
    return os.path.join(get_config_dir(), "history.json")

def load_history_data():
    path = get_history_file()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"enabled": True, "max_items": 50, "history": []}

def save_history_data(data):
    path = get_history_file()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def record_history_item(title, channel, duration, video_id):
    data = load_history_data()
    if not data.get("enabled", True):
        return
    history = data.get("history", [])
    history = [item for item in history if item.get("id") != video_id]
    item = {
        "title": title,
        "channel": channel,
        "duration": duration,
        "id": video_id,
        "date": time.strftime("%d/%m/%Y %H:%M")
    }
    history.insert(0, item)
    max_items = data.get("max_items", 50)
    data["history"] = history[:max_items]
    save_history_data(data)

def remove_history_ids(video_ids):
    """Elimina uno o más IDs específicos del historial local."""
    if not video_ids:
        return
    data = load_history_data()
    targets = set(video_ids)
    data["history"] = [item for item in data.get("history", []) if item.get("id") not in targets]
    save_history_data(data)

def get_settings_file():
    return os.path.join(get_config_dir(), "settings.json")

def load_settings():
    path = get_settings_file()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    supported_codes = {code for code, _ in LANG_OPTIONS}
    default_lang = "en"
    try:
        import locale
        sys_loc = (locale.getdefaultlocale()[0] or "").lower().split("_")[0].split("-")[0]
        if sys_loc in supported_codes:
            default_lang = sys_loc
    except Exception:
        pass
    return {"lang": default_lang, "theme": "dark", "sponsorblock": False}

def save_settings(settings):
    path = get_settings_file()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

def get_binary_path(name):
    if IS_WINDOWS:
        exe_name = f"{name}.exe"
        app_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
        candidates = [
            os.path.join(app_dir, "bin", exe_name),
            os.path.join(app_dir, exe_name),
            os.path.join(app_dir, "..", "bin", exe_name),
            os.path.join(get_base_dir(), "bin", exe_name),
            os.path.join(get_base_dir(), exe_name)
        ]
        for c in candidates:
            if os.path.isfile(c):
                return os.path.abspath(c)
        return exe_name
    # En Linux: priorizar ~/.local/bin y luego /usr/bin (para evitar el sandbox de Firejail en /usr/local/bin)
    local_user_bin = os.path.join(os.path.expanduser("~"), ".local", "bin", name)
    if os.path.isfile(local_user_bin) and os.access(local_user_bin, os.X_OK):
        return local_user_bin
    usr_bin = f"/usr/bin/{name}"
    if os.path.isfile(usr_bin) and os.access(usr_bin, os.X_OK):
        return usr_bin
    return name

SUBPROCESS_FLAGS = {}
if IS_WINDOWS:
    SUBPROCESS_FLAGS["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

# Paletas de diseño moderno (Flat & Sleek)
THEMES = {
    "dark": {
        "bg": "#13141c",
        "header_bg": "#1a1b26",
        "card_bg": "#1f202e",
        "card_border": "#2b2d42",
        "fg": "#e2e8f0",
        "fg_muted": "#8892b0",
        "entry_bg": "#161722",
        "entry_fg": "#ffffff",
        "btn_primary_bg": "#e53e3e",       # Rojo estilo YouTube
        "btn_primary_fg": "#ffffff",
        "btn_secondary_bg": "#2a2b3d",
        "btn_secondary_fg": "#e2e8f0",
        "btn_hover": "#3a3c54",
        "tree_bg": "#161722",
        "tree_alt": "#1a1b28",
        "tree_fg": "#e2e8f0",
        "tree_select": "#314368",
        "accent_green": "#10b981",          # Verde esmeralda vivo
        "progress_trough": "#161722"
    },
    "light": {
        "bg": "#f4f5f8",
        "header_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "fg": "#1a202c",
        "fg_muted": "#64748b",
        "entry_bg": "#f8fafc",
        "entry_fg": "#0f172a",
        "btn_primary_bg": "#dc2626",
        "btn_primary_fg": "#ffffff",
        "btn_secondary_bg": "#e2e8f0",
        "btn_secondary_fg": "#1e293b",
        "btn_hover": "#cbd5e1",
        "tree_bg": "#ffffff",
        "tree_alt": "#f8fafc",
        "tree_fg": "#0f172a",
        "tree_select": "#93c5fd",
        "accent_green": "#059669",
        "progress_trough": "#e2e8f0"
    }
}

def parse_duration_to_seconds(dur_str):
    """Convierte '03:45' o '1:20:00' a segundos para ordenamiento numérico."""
    if not dur_str or dur_str in ("--:--", "NA"):
        return 0
    parts = dur_str.strip().split(":")
    try:
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
    except Exception:
        return 0
    return 0

class YtCliGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-CLI")
        self.root.geometry("880x620")
        self.root.minsize(760, 520)

        settings = load_settings()
        self.current_theme = settings.get("theme", "dark")
        self.current_lang = settings.get("lang", "es")
        self.sponsorblock_enabled = settings.get("sponsorblock", False)

        self.msg_queue = queue.Queue()
        self.active_process = None
        self.mpv_process = None
        self.sort_directions = {}
        self.last_search_results = []
        self.is_viewing_history = False
        self.is_cancelled = False
        self._placeholder_active = False

        user_home = os.path.expanduser("~")
        if IS_WINDOWS:
            self.download_dir = os.path.join(user_home, "Downloads")
        else:
            self.download_dir = os.path.join(user_home, "Descargas")
        if not os.path.exists(self.download_dir):
            self.download_dir = user_home

        self.setup_ui()
        self.apply_theme(self.current_theme)
        self.update_ui_language()
        
        # Asignar icono oficial tanto en script Python como en binario compilado (.exe)
        app_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
        ico_candidates = [
            os.path.join(app_dir, "app.ico"),
            os.path.join(app_dir, "..", "app.ico"),
            os.path.join(get_base_dir(), "app.ico")
        ]
        ico_applied = False
        for ico_file in ico_candidates:
            if os.path.isfile(ico_file):
                try:
                    self.root.iconbitmap(ico_file)
                    ico_applied = True
                    break
                except Exception:
                    pass
        if not ico_applied and IS_WINDOWS and getattr(sys, "frozen", False):
            try:
                self.root.iconbitmap(default=sys.executable)
            except Exception:
                pass

        self.check_clipboard_on_start()
        self.process_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Contenedor raíz
        self.main_container = tk.Frame(self.root, bd=0, highlightthickness=0)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # --- CABECERA SUPERIOR ---
        self.header_frame = tk.Frame(self.main_container, bd=0, highlightthickness=0)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))

        self.brand_frame = tk.Frame(self.header_frame, bd=0)
        self.brand_frame.pack(side=tk.LEFT)

        self.logo_lbl = tk.Label(self.brand_frame, text=" YT-CLI ", font=("sans-serif", 13, "bold"), padx=6, pady=2)
        self.logo_lbl.pack(side=tk.LEFT, padx=(0, 8))

        self.subtitle_lbl = tk.Label(self.brand_frame, text="Cliente Multimedia Ultraligero", font=("sans-serif", 9))
        self.subtitle_lbl.pack(side=tk.LEFT)

        self.btn_theme_toggle = tk.Button(
            self.header_frame,
            text="☀ Modo Claro",
            font=("sans-serif", 8, "bold"),
            command=self.toggle_theme,
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_theme_toggle.pack(side=tk.RIGHT)

        self.btn_about = tk.Button(
            self.header_frame,
            text="Créditos",
            font=("sans-serif", 8, "bold"),
            command=self.open_about_dialog,
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_about.pack(side=tk.RIGHT, padx=(0, 6))

        self.var_lang_display = tk.StringVar()
        lang_names = [name for _, name in LANG_OPTIONS]
        self.cb_lang = ttk.Combobox(
            self.header_frame,
            textvariable=self.var_lang_display,
            values=lang_names,
            width=11,
            state="readonly",
            font=("sans-serif", 8)
        )
        self.cb_lang.bind("<<ComboboxSelected>>", self.on_lang_selected)
        self.cb_lang.pack(side=tk.RIGHT, padx=(0, 6))

        # --- TARJETA DE BÚSQUEDA ---
        self.card_search = tk.Frame(self.main_container, bd=1, relief="solid")
        self.card_search.pack(fill=tk.X, pady=(0, 10), ipady=6)

        search_inner = tk.Frame(self.card_search, bd=0)
        search_inner.pack(fill=tk.X, padx=10, pady=(6, 4))

        self.entry_query = tk.Entry(search_inner, font=("sans-serif", 10), bd=1, relief="solid")
        self.entry_query.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=5)
        self.entry_query.bind("<Return>", lambda e: self.start_search())
        self.entry_query.bind("<FocusIn>", self._on_query_focus_in)
        self.entry_query.bind("<FocusOut>", self._on_query_focus_out)

        self.btn_paste = tk.Button(
            search_inner,
            text="Pegar",
            command=self.paste_clipboard,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_paste.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_clear = tk.Button(
            search_inner,
            text="Limpiar",
            command=self.clear_all,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_clear.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_search = tk.Button(
            search_inner,
            text="Buscar",
            command=self.start_search,
            font=("sans-serif", 9, "bold"),
            relief="flat",
            bd=0,
            padx=14,
            pady=4,
            cursor="hand2"
        )
        self.btn_search.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_history = tk.Button(
            search_inner,
            text="Historial",
            command=self.toggle_history_view,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2"
        )
        self.btn_history.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_hist_opts = tk.Button(
            search_inner,
            text="Opciones",
            command=self.open_history_settings,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.btn_hist_opts.pack(side=tk.LEFT)

        # Parámetros (Resultados, Calidad, FPS y Destino)
        params_row = tk.Frame(self.card_search, bd=0)
        params_row.pack(fill=tk.X, padx=10, pady=(6, 4))

        self.lbl_limit = tk.Label(params_row, text="Resultados:", font=("sans-serif", 8))
        self.lbl_limit.pack(side=tk.LEFT, padx=(0, 4))
        self.var_limit = tk.StringVar(value="25")
        self.cb_limit = ttk.Combobox(params_row, textvariable=self.var_limit, values=["15", "25", "50"], width=4, state="readonly")
        self.cb_limit.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_qual = tk.Label(params_row, text="Calidad:", font=("sans-serif", 8))
        self.lbl_qual.pack(side=tk.LEFT, padx=(0, 4))
        self.var_quality = tk.StringVar(value="720")
        self.quality_cb = ttk.Combobox(params_row, textvariable=self.var_quality, values=["360", "480", "720", "1080"], width=5, state="readonly")
        self.quality_cb.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_fps = tk.Label(params_row, text="FPS:", font=("sans-serif", 8))
        self.lbl_fps.pack(side=tk.LEFT, padx=(0, 4))
        self.var_fps = tk.StringVar(value="30")
        self.fps_cb = ttk.Combobox(params_row, textvariable=self.var_fps, values=["30", "60", "Auto"], width=5, state="readonly")
        self.fps_cb.pack(side=tk.LEFT, padx=(0, 12))

        self.lbl_cookies = tk.Label(params_row, text="Cookies:", font=("sans-serif", 8))
        self.lbl_cookies.pack(side=tk.LEFT, padx=(0, 4))
        self.var_cookies = tk.StringVar(value="Ninguna")
        self.cb_cookies = ttk.Combobox(params_row, textvariable=self.var_cookies, values=["Ninguna", "Firefox", "Chrome", "Edge", "Brave"], width=10, state="readonly")
        self.cb_cookies.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_dest_tag = tk.Label(params_row, text="Destino:", font=("sans-serif", 8))
        self.lbl_dest_tag.pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_dest_path = tk.Label(params_row, text=self.download_dir, anchor="w", font=("sans-serif", 8))
        self.lbl_dest_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_browse = tk.Button(
            params_row,
            text="Examinar",
            command=self.browse_folder,
            font=("sans-serif", 8),
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        self.btn_browse.pack(side=tk.RIGHT)

        # --- SECCIÓN CENTRAL: TABLA ---
        self.card_table = tk.Frame(self.main_container, bd=1, relief="solid")
        self.card_table.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        table_header_bar = tk.Frame(self.card_table, bd=0)
        table_header_bar.pack(fill=tk.X, padx=10, pady=(6, 2))

        self.lbl_table_info = tk.Label(table_header_bar, text="Resultados (haz clic en las columnas para ordenar • doble clic para ver)", font=("sans-serif", 8, "italic"))
        self.lbl_table_info.pack(side=tk.LEFT)

        self.btn_hist_clear = tk.Button(
            table_header_bar,
            text="Limpiar Historial",
            command=self.clear_history_from_view,
            font=("sans-serif", 8, "bold"),
            relief="flat",
            bd=0,
            padx=8,
            pady=1,
            cursor="hand2"
        )

        tree_wrapper = tk.Frame(self.card_table, bd=0)
        tree_wrapper.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        columns = ("title", "channel", "duration", "id")
        self.tree = ttk.Treeview(tree_wrapper, columns=columns, show="headings", selectmode="extended")

        self.tree.heading("title", text="Título ↕", command=lambda: self.sort_tree("title"))
        self.tree.heading("channel", text="Canal ↕", command=lambda: self.sort_tree("channel"))
        self.tree.heading("duration", text="Duración ↕", command=lambda: self.sort_tree("duration"))
        self.tree.heading("id", text="ID / Enlace", command=lambda: self.sort_tree("id"))

        self.tree.column("title", width=450, anchor="w")
        self.tree.column("channel", width=160, anchor="w")
        self.tree.column("duration", width=85, anchor="center")
        self.tree.column("id", width=110, anchor="center")

        tree_scroll_y = ttk.Scrollbar(tree_wrapper, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self.play_selected(audio_only=False))
        self.tree.bind("<Button-3>", self.on_tree_right_click)
        self.tree.bind("<Delete>", self.on_tree_delete_key)

        # --- BARRA DE ACCIONES (Corregida con self.action_bar para tema limpio) ---
        self.action_bar = tk.Frame(self.main_container, bd=0, highlightthickness=0)
        self.action_bar.pack(fill=tk.X, pady=(0, 8))

        self.btn_play_vid = tk.Button(
            self.action_bar,
            text="▶ Ver Vídeo",
            command=lambda: self.play_selected(audio_only=False),
            font=("sans-serif", 9, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_play_vid.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_play_aud = tk.Button(
            self.action_bar,
            text="♫ Escuchar Audio",
            command=lambda: self.play_selected(audio_only=True),
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_play_aud.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_dl_video = tk.Button(
            self.action_bar,
            text="↓ Descargar MP4",
            command=self.prompt_video_download,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_dl_video.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_dl_audio = tk.Button(
            self.action_bar,
            text="♪ Descargar Audio",
            command=self.prompt_audio_download,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_dl_audio.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_extract_subs = tk.Button(
            self.action_bar,
            text="📝 Subtítulos",
            command=self.start_subtitles_download,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.btn_extract_subs.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_cancel = tk.Button(
            self.action_bar,
            text="■ Detener",
            command=self.cancel_process,
            font=("sans-serif", 9),
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            state=tk.DISABLED
        )
        self.btn_cancel.pack(side=tk.RIGHT)

        # --- PIE DE PÁGINA: ESTADO Y PROGRESO ---
        self.status_bar = tk.Frame(self.main_container, bd=0, highlightthickness=0)
        self.status_bar.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Listo.")
        self.lbl_status = tk.Label(self.status_bar, textvariable=self.status_var, anchor="w", font=("sans-serif", 8))
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.prog_bar = ttk.Progressbar(self.status_bar, style="Green.Horizontal.TProgressbar", mode="indeterminate", length=150)
        self.prog_bar.pack(side=tk.RIGHT)

    def apply_theme(self, theme_key):
        pal = THEMES[theme_key]
        self.current_theme = theme_key

        # Fondo principal y marcos contenedores
        self.root.configure(bg=pal["bg"])
        self.main_container.configure(bg=pal["bg"])
        self.header_frame.configure(bg=pal["bg"])
        self.brand_frame.configure(bg=pal["bg"])
        self.action_bar.configure(bg=pal["bg"])
        self.status_bar.configure(bg=pal["bg"])

        # Logo y cabecera
        s = self.get_strings()
        self.logo_lbl.configure(bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"])
        self.subtitle_lbl.configure(bg=pal["bg"], fg=pal["fg_muted"])
        self.btn_theme_toggle.configure(
            text=s["theme_light"] if theme_key == "dark" else s["theme_dark"],
            bg=pal["btn_secondary_bg"],
            fg=pal["btn_secondary_fg"]
        )
        self.btn_about.configure(
            bg=pal["btn_secondary_bg"],
            fg=pal["btn_secondary_fg"]
        )

        # Tarjetas de búsqueda y tabla
        for card in [self.card_search, self.card_table]:
            card.configure(bg=pal["card_bg"], highlightbackground=pal["card_border"], highlightcolor=pal["card_border"])
            for child in card.winfo_children():
                try:
                    child.configure(bg=pal["card_bg"])
                    for sub in child.winfo_children():
                        if isinstance(sub, tk.Label):
                            sub.configure(bg=pal["card_bg"], fg=pal["fg"])
                        elif isinstance(sub, tk.Frame):
                            sub.configure(bg=pal["card_bg"])
                except Exception:
                    pass

        self.lbl_table_info.configure(bg=pal["card_bg"], fg=pal["fg_muted"])
        self.lbl_dest_path.configure(bg=pal["card_bg"], fg=pal["accent_green"])
        self.lbl_limit.configure(fg=pal["fg_muted"])
        self.lbl_qual.configure(fg=pal["fg_muted"])
        self.lbl_fps.configure(fg=pal["fg_muted"])
        self.lbl_cookies.configure(fg=pal["fg_muted"])
        self.lbl_dest_tag.configure(fg=pal["fg_muted"])

        # Entrada de texto
        entry_fg_col = pal["fg_muted"] if self._placeholder_active else pal["entry_fg"]
        self.entry_query.configure(bg=pal["entry_bg"], fg=entry_fg_col, insertbackground=pal["entry_fg"], highlightbackground=pal["card_border"])

        # Botones secundarios
        for btn in [self.btn_paste, self.btn_clear, self.btn_history, self.btn_hist_opts, self.btn_browse, self.btn_play_aud, self.btn_dl_video, self.btn_dl_audio, self.btn_extract_subs, self.btn_cancel]:
            btn.configure(bg=pal["btn_secondary_bg"], fg=pal["btn_secondary_fg"], activebackground=pal["btn_hover"], activeforeground="#ffffff")
        self.btn_hist_clear.configure(bg="#7f1d1d", fg="#ffffff", activebackground="#991b1b", activeforeground="#ffffff")

        # Botones primarios
        self.btn_search.configure(bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"], activebackground="#b91c1c", activeforeground="#ffffff")
        self.btn_play_vid.configure(bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"], activebackground="#b91c1c", activeforeground="#ffffff")

        # Barra de estado
        self.lbl_status.configure(bg=pal["bg"], fg=pal["fg"])

        # Estilo de tabla (Treeview)
        self.style.configure(
            "Treeview",
            background=pal["tree_bg"],
            foreground=pal["tree_fg"],
            fieldbackground=pal["tree_bg"],
            rowheight=26,
            borderwidth=0
        )
        self.style.map("Treeview", background=[("selected", pal["tree_select"])], foreground=[("selected", "#ffffff")])
        self.style.configure(
            "Treeview.Heading",
            background=pal["btn_secondary_bg"],
            foreground=pal["btn_secondary_fg"],
            font=("sans-serif", 9, "bold"),
            relief="flat"
        )
        self.tree.tag_configure("evenrow", background=pal["tree_bg"])
        self.tree.tag_configure("oddrow", background=pal["tree_alt"])

        # Barra de progreso verde
        self.style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=pal["progress_trough"],
            background=pal["accent_green"],
            darkcolor=pal["accent_green"],
            lightcolor=pal["accent_green"],
            bordercolor=pal["card_border"]
        )

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        self._refresh_row_tags()
        settings = load_settings()
        settings["theme"] = new_theme
        save_settings(settings)

    def get_strings(self):
        base = GUI_STRINGS["en"]
        lang_dict = GUI_STRINGS.get(self.current_lang, base)
        merged = dict(base)
        merged.update(lang_dict)
        return merged

    def _show_placeholder(self):
        if self._placeholder_active:
            return
        s = self.get_strings()
        pal = THEMES[self.current_theme]
        self._placeholder_active = True
        self.entry_query.delete(0, tk.END)
        self.entry_query.insert(0, s["search_placeholder"])
        self.entry_query.configure(fg=pal["fg_muted"])

    def _hide_placeholder(self):
        if not self._placeholder_active:
            return
        pal = THEMES[self.current_theme]
        self._placeholder_active = False
        self.entry_query.delete(0, tk.END)
        self.entry_query.configure(fg=pal["entry_fg"])

    def _on_query_focus_in(self, event=None):
        self._hide_placeholder()

    def _on_query_focus_out(self, event=None):
        if not self.entry_query.get().strip():
            self._show_placeholder()

    def _get_query_text(self):
        if self._placeholder_active:
            return ""
        return self.entry_query.get().strip()

    def _set_query_text(self, text):
        self._hide_placeholder()
        self.entry_query.delete(0, tk.END)
        self.entry_query.insert(0, text)

    def update_ui_language(self):
        s = self.get_strings()
        all_ready = {d.get("ready", "") for d in GUI_STRINGS.values()}
        all_none = {d.get("cookie_none", "") for d in GUI_STRINGS.values()} | {"Ninguna", "None"}

        self.subtitle_lbl.config(text=s["subtitle"])
        for code, name in LANG_OPTIONS:
            if code == self.current_lang:
                self.var_lang_display.set(name)
                break
        self.btn_theme_toggle.config(text=s["theme_light"] if self.current_theme == "dark" else s["theme_dark"])
        self.btn_about.config(text=s["credits"])
        self.btn_paste.config(text=s["paste"])
        self.btn_clear.config(text=s["clear"])
        self.btn_search.config(text=s["search"])
        self.btn_history.config(text=s["history_back"] if self.is_viewing_history else s["history"])
        self.btn_hist_opts.config(text=s["history_opts"])
        self.btn_hist_clear.config(text=s["hist_clear_all"])
        self.lbl_limit.config(text=s["results_label"])
        self.lbl_qual.config(text=s["quality_label"])
        self.lbl_fps.config(text=s["fps_label"])
        self.lbl_cookies.config(text=s["cookies_label"])
        self.lbl_dest_tag.config(text=s["dest_label"])
        self.btn_browse.config(text=s["change_folder"])
        self.lbl_table_info.config(text=s["table_hint"])
        self.tree.heading("title", text=s["col_title"])
        self.tree.heading("channel", text=s["col_channel"])
        self.tree.heading("duration", text=s["col_duration"])
        self.tree.heading("id", text=s["col_id"])
        self.btn_play_vid.config(text=s["play_video"])
        self.btn_play_aud.config(text=s["play_audio"])
        self.btn_dl_video.config(text=s["download_video"])
        self.btn_dl_audio.config(text=s["download_audio"])
        self.btn_extract_subs.config(text=s["extract_subs"])
        self.btn_cancel.config(text=s["stop"])

        none_label = s["cookie_none"]
        current_cookie = self.var_cookies.get()
        if current_cookie in all_none or not current_cookie:
            self.var_cookies.set(none_label)
        self.cb_cookies.config(values=[none_label, "Firefox", "Chrome", "Edge", "Brave"])

        if self._placeholder_active or not self.entry_query.get().strip():
            self._placeholder_active = False
            self._show_placeholder()

        if self.status_var.get() in all_ready or self.status_var.get() in ("Listo.", "Ready."):
            self.status_var.set(s["ready"])

    def on_lang_selected(self, event=None):
        chosen_name = self.var_lang_display.get()
        for code, name in LANG_OPTIONS:
            if name == chosen_name:
                self.current_lang = code
                break
        self.update_ui_language()
        settings = load_settings()
        settings["lang"] = self.current_lang
        save_settings(settings)

    def _refresh_row_tags(self):
        for idx, item in enumerate(self.tree.get_children()):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.item(item, tags=(tag,))

    def get_selected_cookie_browser(self):
        choice = self.var_cookies.get().strip()
        if choice in ("Firefox", "Chrome", "Edge", "Brave"):
            return choice
        return None

    def check_clipboard_on_start(self):
        try:
            clip = self.root.clipboard_get().strip()
            if clip.startswith("http://") or clip.startswith("https://") or "youtube.com" in clip or "youtu.be" in clip:
                self._set_query_text(clip)
                item_id = self.tree.insert("", tk.END, values=("Enlace multimedia detectado", "Enlace Web", "--:--", clip), tags=("evenrow",))
                self.tree.selection_set(item_id)
                self.status_var.set("Enlace detectado del portapapeles. Listo para Ver Vídeo, Escuchar Audio o Descargar.")
        except Exception:
            pass

    def paste_clipboard(self):
        try:
            clip = self.root.clipboard_get().strip()
            if not clip:
                messagebox.showwarning("Portapapeles", "El portapapeles está vacío.")
                return
            self._set_query_text(clip)
            if clip.startswith("http://") or clip.startswith("https://"):
                for item in self.tree.get_children():
                    self.tree.delete(item)
                item_id = self.tree.insert("", tk.END, values=("Enlace pegado", "Enlace Web", "--:--", clip), tags=("evenrow",))
                self.tree.selection_set(item_id)
                self.status_var.set("Enlace pegado y seleccionado. Elige Ver Vídeo, Escuchar Audio o Descargar.")
            else:
                self.status_var.set(f"Texto pegado: '{clip}'. Pulsa Buscar para ver resultados.")
        except Exception:
            messagebox.showwarning("Portapapeles", "No se pudo leer el portapapeles.")

    def clear_all(self):
        """Limpia el campo de entrada, la tabla de resultados y el estado."""
        self._hide_placeholder()
        self.entry_query.delete(0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.last_search_results = []
        self.is_viewing_history = False
        self.btn_hist_clear.pack_forget()
        s = self.get_strings()
        self.btn_history.config(text=s["history"])
        self.prog_bar.stop()
        self.status_var.set(s["ready"])
        self._show_placeholder()

    def browse_folder(self):
        chosen = filedialog.askdirectory(initialdir=self.download_dir, title="Seleccionar Carpeta")
        if chosen:
            self.download_dir = chosen
            self.lbl_dest_path.config(text=chosen)

    def sort_tree(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        reverse = self.sort_directions.get(col, False)
        self.sort_directions[col] = not reverse

        if col == "duration":
            items.sort(key=lambda t: parse_duration_to_seconds(t[0]), reverse=reverse)
        else:
            items.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

        self._refresh_row_tags()
        order_txt = "descendente ↓" if reverse else "ascendente ↑"
        self.status_var.set(f"Tabla ordenada por '{col}' ({order_txt}).")

    def start_search(self):
        query = self._get_query_text()
        if not query:
            messagebox.showinfo("Búsqueda" if self.current_lang == "es" else "Search", "Escribe un término de búsqueda, @canal o pega un enlace." if self.current_lang == "es" else "Enter a search term, @channel, or paste a link.")
            return

        if query.startswith("http://") or query.startswith("https://"):
            for item in self.tree.get_children():
                self.tree.delete(item)
            item_id = self.tree.insert("", tk.END, values=("Enlace directo cargado", "Enlace Web", "--:--", query), tags=("evenrow",))
            self.tree.selection_set(item_id)
            self.status_var.set("Enlace cargado y seleccionado. Listo para Ver o Descargar.")
            return

        limit = self.var_limit.get()
        self.btn_search.config(state=tk.DISABLED)
        self.prog_bar.start(10)
        self.status_var.set(f"Buscando '{query}' ({limit} resultados)...")
        for item in self.tree.get_children():
            self.tree.delete(item)

        thread = threading.Thread(target=self._search_worker, args=(query, limit), daemon=True)
        thread.start()

    def _search_worker(self, query, limit):
        ytdlp_cmd = get_binary_path("yt-dlp")
        bin_dir = os.path.dirname(os.path.abspath(ytdlp_cmd))
        env = os.environ.copy()
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        search_target = f"ytsearch{limit}:{query}"
        extra_args = []
        if query.startswith("@"):
            parts = query.split(None, 1)
            ch = parts[0][1:]
            if len(parts) > 1:
                search_target = f"https://www.youtube.com/@{ch}/search?query={parts[1]}"
                extra_args = ["--playlist-end", str(limit)]
            else:
                search_target = f"https://www.youtube.com/@{ch}/videos"
                extra_args = ["--playlist-end", str(limit)]

        cmd = [
            ytdlp_cmd,
            "--encoding", "utf-8",
            "--flat-playlist",
            "--extractor-args", f"youtube:lang={self.current_lang}",
            "--print", "%(title)s\t%(uploader)s\t%(duration_string)s\t%(id)s",
        ] + extra_args + [search_target]
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                **SUBPROCESS_FLAGS
            )
            self.active_process = proc
            out, err = proc.communicate()
            items = []
            for line in out.splitlines():
                parts = line.strip().split("\t")
                if len(parts) >= 4:
                    items.append((parts[0], parts[1], parts[2], parts[3]))
            self.msg_queue.put(("search_done", items))
        except Exception as e:
            self.msg_queue.put(("error", f"Error en búsqueda: {str(e)}"))
        finally:
            self.active_process = None

    def get_selected_urls(self):
        selected = self.tree.selection()
        if selected:
            urls = []
            for item_id in selected:
                val = self.tree.item(item_id, "values")
                video_ref = val[3]
                if video_ref.startswith("http"):
                    urls.append(video_ref)
                else:
                    urls.append(f"https://www.youtube.com/watch?v={video_ref}")
            return urls

        # Si no hay selección en la tabla, tomar directamente la URL de la caja de entrada
        query = self.entry_query.get().strip()
        if query:
            if query.startswith("http://") or query.startswith("https://"):
                return [query]
            elif len(query) == 11 and " " not in query:
                return [f"https://www.youtube.com/watch?v={query}"]
        return []

    def get_format_string(self):
        quality = self.var_quality.get()
        fps_choice = self.var_fps.get()

        fps_filter = ""
        if fps_choice == "30":
            fps_filter = "[fps<=30]"
        elif fps_choice == "60":
            fps_filter = "[fps<=60]"

        fmt = (
            f"bestvideo[height<={quality}]{fps_filter}[vcodec^=avc1]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={quality}]{fps_filter}+bestaudio/"
            f"bestvideo[height<={quality}]+bestaudio/"
            f"best[height<={quality}]{fps_filter}/"
            f"best[height<={quality}]/best"
        )
        return fmt

    def toggle_history_view(self):
        if not self.is_viewing_history:
            self.show_history()
        else:
            self.show_last_search()

    def show_history(self):
        data = load_history_data()
        hist = data.get("history", [])
        if not hist:
            messagebox.showinfo("Historial" if self.current_lang == "es" else "History", "El historial de reproducción está vacío." if self.current_lang == "es" else "Watch history is empty.")
            return

        self.is_viewing_history = True
        s = self.get_strings()
        self.btn_history.config(text=s["history_back"])
        self.btn_hist_clear.pack(side=tk.RIGHT)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, entry in enumerate(hist):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=(entry.get("title", ""), entry.get("channel", ""), entry.get("duration", ""), entry.get("id", "")), tags=(tag,))

        self.status_var.set(f"Mostrando historial ({len(hist)} vídeos). Clic derecho o Supr para eliminar." if self.current_lang == "es" else f"Showing history ({len(hist)} items). Right-click or Del to remove.")

    def show_last_search(self):
        self.is_viewing_history = False
        s = self.get_strings()
        self.btn_history.config(text=s["history"])
        self.btn_hist_clear.pack_forget()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.last_search_results:
            self.status_var.set(s["ready"])
            return

        for idx, item in enumerate(self.last_search_results):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=item, tags=(tag,))

        self.status_var.set(f"Volviste a tu búsqueda ({len(self.last_search_results)} resultados)." if self.current_lang == "es" else f"Returned to search ({len(self.last_search_results)} results).")

    def clear_history_from_view(self):
        is_es = self.current_lang == "es"
        if messagebox.askyesno("Historial" if is_es else "History", "¿Borrar todo el historial local?" if is_es else "Clear all local watch history?"):
            data = load_history_data()
            data["history"] = []
            save_history_data(data)
            self.show_last_search()

    def remove_selected_from_history(self):
        if not self.is_viewing_history:
            return
        selected = self.tree.selection()
        if not selected:
            return
        ids_to_remove = []
        for item_id in selected:
            vals = self.tree.item(item_id, "values")
            if vals and len(vals) >= 4:
                ids_to_remove.append(vals[3])
            self.tree.delete(item_id)
        remove_history_ids(ids_to_remove)
        self._refresh_row_tags()
        if not self.tree.get_children():
            self.show_last_search()

    def on_tree_right_click(self, event):
        if not self.is_viewing_history:
            return
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        if row_id not in self.tree.selection():
            self.tree.selection_set(row_id)
        s = self.get_strings()
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=s["hist_remove_item"], command=self.remove_selected_from_history)
        menu.add_separator()
        menu.add_command(label=s["hist_clear_all"], command=self.clear_history_from_view)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def on_tree_delete_key(self, event=None):
        if self.is_viewing_history:
            self.remove_selected_from_history()

    def open_about_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Acerca de YT-CLI")
        dialog.geometry("440x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        pal = THEMES[self.current_theme]
        dialog.configure(bg=pal["card_bg"])

        lbl_title = tk.Label(dialog, text="YT-CLI v1.5", font=("sans-serif", 13, "bold"), bg=pal["card_bg"], fg=pal["fg"])
        lbl_title.pack(pady=(14, 2))

        is_en = self.current_lang == "en"
        desc_txt = (
            "Ultralight high-performance multimedia client\nfor resource-constrained and modern systems."
            if is_en else
            "Cliente multimedia ultraligero y de alto rendimiento\npara equipos de bajos recursos y sistemas modernos."
        )
        lbl_desc = tk.Label(
            dialog,
            text=desc_txt,
            font=("sans-serif", 8),
            bg=pal["card_bg"],
            fg=pal["fg_muted"],
            justify="center"
        )
        lbl_desc.pack(pady=(0, 10))

        box = tk.Frame(dialog, bg=pal["entry_bg"], bd=1, relief="solid", padx=12, pady=10)
        box.pack(fill=tk.X, padx=20, pady=(0, 12))

        tk.Label(box, text="Author:" if is_en else "Autor:", font=("sans-serif", 8, "bold"), bg=pal["entry_bg"], fg=pal["fg"]).grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(box, text="Kenny Waddell (@KennyWaddell)", font=("sans-serif", 8), bg=pal["entry_bg"], fg=pal["accent_green"]).grid(row=0, column=1, sticky="w", padx=8, pady=2)

        tk.Label(box, text="Collaboration:" if is_en else "Colaboración:", font=("sans-serif", 8, "bold"), bg=pal["entry_bg"], fg=pal["fg"]).grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(box, text="Google DeepMind / Antigravity", font=("sans-serif", 8), bg=pal["entry_bg"], fg=pal["fg"]).grid(row=1, column=1, sticky="w", padx=8, pady=2)

        tk.Label(box, text="License:" if is_en else "Licencia:", font=("sans-serif", 8, "bold"), bg=pal["entry_bg"], fg=pal["fg"]).grid(row=2, column=0, sticky="w", pady=2)
        tk.Label(box, text="GNU General Public License v3 (GPLv3)", font=("sans-serif", 8), bg=pal["entry_bg"], fg=pal["fg"]).grid(row=2, column=1, sticky="w", padx=8, pady=2)

        def open_repo():
            webbrowser.open_new_tab("https://github.com/KennyWaddell/yt-cli")

        btn_repo = tk.Button(
            dialog,
            text="View Repository on GitHub" if is_en else "Ver Repositorio en GitHub",
            command=open_repo,
            font=("sans-serif", 8, "bold"),
            bg=pal["btn_primary_bg"],
            fg=pal["btn_primary_fg"],
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2"
        )
        btn_repo.pack(pady=(0, 8))

        btn_close = tk.Button(
            dialog,
            text="Cerrar",
            command=dialog.destroy,
            font=("sans-serif", 8),
            bg=pal["btn_secondary_bg"],
            fg=pal["btn_secondary_fg"],
            relief="flat",
            bd=0,
            padx=14,
            pady=3,
            cursor="hand2"
        )
        btn_close.pack()

    def open_history_settings(self):
        data = load_history_data()

        dialog = tk.Toplevel(self.root)
        dialog.title("Ajustes de Historial")
        dialog.geometry("380x210")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        pal = THEMES[self.current_theme]
        dialog.configure(bg=pal["card_bg"])

        lbl = tk.Label(dialog, text="Historial de Reproducción", font=("sans-serif", 10, "bold"), bg=pal["card_bg"], fg=pal["fg"])
        lbl.pack(pady=(14, 8))

        var_enabled = tk.BooleanVar(value=data.get("enabled", True))
        cb = tk.Checkbutton(
            dialog,
            text="¿Desea recordar el historial de vídeos vistos?",
            variable=var_enabled,
            font=("sans-serif", 9),
            bg=pal["card_bg"],
            fg=pal["fg"],
            selectcolor=pal["entry_bg"],
            activebackground=pal["card_bg"]
        )
        cb.pack(pady=(0, 6), padx=20, anchor="w")

        lbl_limit = tk.Label(dialog, text="Límite: hasta 50 vídeos recientes (rotación automática)", font=("sans-serif", 8), bg=pal["card_bg"], fg=pal["fg_muted"])
        lbl_limit.pack(pady=(0, 14), padx=22, anchor="w")

        def clear_all():
            if messagebox.askyesno("Borrar Historial", "¿Estás seguro de que deseas borrar todo el historial?"):
                data["history"] = []
                save_history_data(data)
                dialog.destroy()
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self.status_var.set("Historial eliminado por completo.")

        def save_and_close():
            data["enabled"] = var_enabled.get()
            save_history_data(data)
            dialog.destroy()
            state_str = "activado" if data["enabled"] else "desactivado"
            self.status_var.set(f"Historial {state_str}.")

        btn_box = tk.Frame(dialog, bg=pal["card_bg"])
        btn_box.pack(fill=tk.X, padx=20, pady=(6, 0))

        is_en = self.current_lang == "en"
        btn_clear = tk.Button(btn_box, text="Clear History" if is_en else "Borrar Historial", command=clear_all, font=("sans-serif", 8), bg="#7f1d1d", fg="#ffffff", relief="flat", padx=10, pady=3, cursor="hand2")
        btn_clear.pack(side=tk.LEFT)

        btn_ok = tk.Button(btn_box, text="Save and Close" if is_en else "Guardar y Cerrar", command=save_and_close, font=("sans-serif", 8, "bold"), bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"], relief="flat", padx=10, pady=3, cursor="hand2")
        btn_ok.pack(side=tk.RIGHT)

    def play_selected(self, audio_only=False):
        urls = self.get_selected_urls()
        is_en = self.current_lang == "en"
        if not urls:
            msg = "Select at least one video from the list." if is_en else "Selecciona al menos un vídeo de la lista."
            title = "Play" if is_en else "Reproducir"
            messagebox.showinfo(title, msg)
            return

        mpv_cmd = get_binary_path("mpv")
        ytdlp_cmd = get_binary_path("yt-dlp")
        bin_dir = os.path.dirname(os.path.abspath(ytdlp_cmd))
        clean_ytdlp = os.path.abspath(ytdlp_cmd).replace("\\", "/")

        env = os.environ.copy()
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # Registrar en historial
        selected_ids = self.tree.selection()
        for item_id in selected_ids:
            vals = self.tree.item(item_id, "values")
            if vals and len(vals) >= 4:
                record_history_item(vals[0], vals[1], vals[2], vals[3])

        # Detener cualquier reproducción previa de mpv antes de iniciar una nueva
        if self.mpv_process and self.mpv_process.poll() is None:
            try:
                self.mpv_process.terminate()
            except Exception:
                pass

        # Notificación visual y activación de la barra de progreso
        self.prog_bar.start(10)
        self.btn_cancel.config(state=tk.NORMAL)
        if is_en:
            self.status_var.set("⏳ Loading YouTube buffer... player will launch in ~10-15s")
        else:
            self.status_var.set("⏳ Cargando buffer de YouTube... el reproductor abrirá automáticamente en ~10-15s")

        # Base de comando con reanudación automática (save-position-on-quit) y buffer optimizado
        cmd = [
            mpv_cmd,
            "--save-position-on-quit",
            "--watch-later-options=start",
            f"--script-opts=ytdl_hook-ytdl_path={clean_ytdlp}",
            f"--ytdl-raw-options=extractor-args=youtube:lang={self.current_lang}",
            "--demuxer-readahead-secs=5",
            "--demuxer-max-bytes=32M"
        ]

        # Soporte seguro de Cookies de navegadores (con verificación previa de instalación)
        cookie_choice = self.get_selected_cookie_browser()
        if cookie_choice:
            if is_browser_installed(cookie_choice):
                cmd.append(f'--ytdl-raw-options-append=cookies-from-browser={cookie_choice.lower()}')
            else:
                warn_msg = f"Notice: Browser {cookie_choice} not detected. Continuing without cookies..." if is_en else f"Aviso: Navegador {cookie_choice} no detectado. Continuando sin cookies..."
                self.status_var.set(warn_msg)

        if audio_only:
            # Ventana interactiva de audio con barra de tiempo, volumen, pausa y bucle
            title_text = "YT-CLI - Audio Player" if is_en else "YT-CLI - Reproductor de Audio"
            cmd += [
                f"--title={title_text}",
                "--vid=no",
                "--force-window=yes",
                "--geometry=560x220",
                "--player-operation-mode=pseudo-gui",
                "--ytdl-format=bestaudio[ext=m4a]/bestaudio/best"
            ]
        else:
            fmt = self.get_format_string()
            title_text = "YT-CLI - Video Player" if is_en else "YT-CLI - Reproductor de Vídeo"
            cmd += [
                f"--title={title_text}",
                "--vo=gpu",
                "--hwdec=auto-safe",
                f"--ytdl-format={fmt}"
            ]

        cmd += urls

        try:
            self.mpv_process = subprocess.Popen(cmd, env=env)

            # Monitoreo de arranque activo: detectar cierre o fallo prematuro de mpv
            def check_mpv_startup(elapsed=0):
                if not self.mpv_process:
                    return
                poll_code = self.mpv_process.poll()
                if poll_code is not None:
                    # mpv terminó prematuramente (cierre o fallo)
                    self.prog_bar.stop()
                    self.btn_cancel.config(state=tk.DISABLED)
                    if poll_code != 0:
                        err_text = f"Player closed unexpectedly (exit code {poll_code})." if is_en else f"El reproductor se cerró inesperadamente (código {poll_code})."
                        self.status_var.set(err_text)
                    else:
                        ready_text = "Ready." if is_en else "Listo."
                        self.status_var.set(ready_text)
                    return

                if elapsed >= 8:
                    # Tras 8 segundos sigue en ejecución
                    self.prog_bar.stop()
                    if audio_only:
                        self.status_var.set(
                            "♫ Playing. Controls: Space (Pause), Arrows (Seek), 9/0 (Volume), L (Loop)" if is_en
                            else "♫ En reproducción. Controles: Espacio (Pausa), Flechas (Avanzar/Retroceder), 9/0 (Volumen), L (Bucle)"
                        )
                    else:
                        self.status_var.set(
                            "▶ Playing. Controls: Space (Pause), Arrows (Seek), F (Fullscreen)" if is_en
                            else "▶ En reproducción. Controles: Espacio (Pausa), Flechas (Avanzar/Retroceder), F (Pantalla completa)"
                        )
                else:
                    self.root.after(1000, lambda: check_mpv_startup(elapsed + 1))

            self.root.after(1000, lambda: check_mpv_startup(1))
        except FileNotFoundError:
            self.prog_bar.stop()
            self.btn_cancel.config(state=tk.DISABLED)
            self.status_var.set("Ready." if is_en else "Listo.")
            err_msg = f"Executable '{mpv_cmd}' not found." if is_en else f"No se encontró el ejecutable '{mpv_cmd}'."
            messagebox.showerror("Error", err_msg)

    def prompt_video_download(self):
        urls = self.get_selected_urls()
        if not urls:
            is_en = self.current_lang == "en"
            msg = "Select at least one video from the list." if is_en else "Selecciona al menos un vídeo de la lista."
            title = "Download Video" if is_en else "Descargar Vídeo"
            messagebox.showinfo(title, msg)
            return

        is_en = self.current_lang != "es"
        s = self.get_strings()
        dialog = tk.Toplevel(self.root)
        dialog.title("Video Download Options (MP4)" if is_en else "Opciones de Descarga de Vídeo (MP4)")
        dialog.geometry("420x440")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        pal = THEMES[self.current_theme]
        dialog.configure(bg=pal["card_bg"])

        lbl = tk.Label(dialog, text="Video Download Options (MP4)" if is_en else "Opciones de Descarga MP4", font=("sans-serif", 10, "bold"), bg=pal["card_bg"], fg=pal["fg"])
        lbl.pack(pady=(12, 6))

        row_q = tk.Frame(dialog, bg=pal["card_bg"])
        row_q.pack(fill=tk.X, padx=24, pady=3)
        tk.Label(row_q, text="Resolution:" if is_en else "Resolución:", font=("sans-serif", 9), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        var_q = tk.StringVar(value=self.var_quality.get())
        cb_q = ttk.Combobox(row_q, textvariable=var_q, values=["360", "480", "720", "1080"], width=8, state="readonly")
        cb_q.pack(side=tk.RIGHT)

        row_fps = tk.Frame(dialog, bg=pal["card_bg"])
        row_fps.pack(fill=tk.X, padx=24, pady=3)
        tk.Label(row_fps, text="Frame rate (FPS):" if is_en else "Tasa de cuadros (FPS):", font=("sans-serif", 9), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        var_f = tk.StringVar(value=self.var_fps.get())
        cb_f = ttk.Combobox(row_fps, textvariable=var_f, values=["30", "60", "Auto"], width=8, state="readonly")
        cb_f.pack(side=tk.RIGHT)

        var_thumb = tk.BooleanVar(value=True)
        cb_th = tk.Checkbutton(dialog, text="Embed thumbnail in MP4" if is_en else "Incrustar carátula en el MP4", variable=var_thumb, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_th.pack(pady=(6, 2), padx=22, anchor="w")

        var_split = tk.BooleanVar(value=False)
        cb_split = tk.Checkbutton(dialog, text="Split by chapters (--split-chapters)" if is_en else "Dividir en capítulos automáticos", variable=var_split, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_split.pack(pady=2, padx=22, anchor="w")

        var_sb = tk.BooleanVar(value=self.sponsorblock_enabled)
        cb_sb = tk.Checkbutton(dialog, text=s["sponsorblock"], variable=var_sb, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_sb.pack(pady=2, padx=22, anchor="w")

        trim_frame = tk.LabelFrame(dialog, text="Trim Time Section" if is_en else "Recortar fragmento de tiempo", font=("sans-serif", 8, "bold"), bg=pal["card_bg"], fg=pal["fg_muted"], bd=1, padx=8, pady=4)
        trim_frame.pack(fill=tk.X, padx=22, pady=(6, 10))

        var_trim = tk.BooleanVar(value=False)
        cb_trim = tk.Checkbutton(trim_frame, text="Enable time trimming" if is_en else "Activar recorte por tiempo", variable=var_trim, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_trim.pack(anchor="w", pady=(0, 4))

        trim_inputs = tk.Frame(trim_frame, bg=pal["card_bg"])
        trim_inputs.pack(fill=tk.X)

        tk.Label(trim_inputs, text="From (MM:SS):" if is_en else "Desde (MM:SS):", font=("sans-serif", 8), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        ent_start = tk.Entry(trim_inputs, width=7, font=("sans-serif", 9), bd=1)
        ent_start.insert(0, "00:00")
        ent_start.pack(side=tk.LEFT, padx=(4, 12))

        tk.Label(trim_inputs, text="To (MM:SS):" if is_en else "Hasta (MM:SS):", font=("sans-serif", 8), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        ent_end = tk.Entry(trim_inputs, width=7, font=("sans-serif", 9), bd=1)
        ent_end.insert(0, "00:00")
        ent_end.pack(side=tk.LEFT, padx=4)

        def confirm():
            q = var_q.get()
            fps = var_f.get()
            thumb = var_thumb.get()
            split = var_split.get()
            sb = var_sb.get()
            self.sponsorblock_enabled = sb
            settings = load_settings()
            settings["sponsorblock"] = sb
            save_settings(settings)
            trim_spec = ""
            if var_trim.get():
                s_val = ent_start.get().strip()
                e_val = ent_end.get().strip()
                if s_val and e_val and (s_val != "00:00" or e_val != "00:00"):
                    trim_spec = f"{s_val}-{e_val}"
            dialog.destroy()
            self.start_download(mode="video", quality=q, fps=fps, embed_thumb=thumb, split_chapters=split, trim_section=trim_spec, sponsorblock=sb)

        btn = tk.Button(dialog, text="Start Download" if is_en else "Iniciar Descarga", command=confirm, bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"], font=("sans-serif", 9, "bold"), relief="flat", bd=0, padx=14, pady=5, cursor="hand2")
        btn.pack(pady=(4, 0))

    def prompt_audio_download(self):
        urls = self.get_selected_urls()
        if not urls:
            is_en = self.current_lang == "en"
            msg = "Select at least one video from the list." if is_en else "Selecciona al menos un vídeo de la lista."
            title = "Download Audio" if is_en else "Descarga de Audio"
            messagebox.showinfo(title, msg)
            return

        is_en = self.current_lang != "es"
        s = self.get_strings()
        dialog = tk.Toplevel(self.root)
        dialog.title("Audio Download Options" if is_en else "Opciones de Descarga de Audio")
        dialog.geometry("420x490")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        pal = THEMES[self.current_theme]
        dialog.configure(bg=pal["card_bg"])

        lbl = tk.Label(dialog, text="Audio Download Options" if is_en else "Opciones de Descarga de Audio", font=("sans-serif", 10, "bold"), bg=pal["card_bg"], fg=pal["fg"])
        lbl.pack(pady=(12, 6))

        row_fmt = tk.Frame(dialog, bg=pal["card_bg"])
        row_fmt.pack(fill=tk.X, padx=24, pady=3)
        tk.Label(row_fmt, text="Audio Format:" if is_en else "Formato de audio:", font=("sans-serif", 9), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        var_afmt = tk.StringVar(value="MP3")
        cb_afmt = ttk.Combobox(row_fmt, textvariable=var_afmt, values=["MP3", "M4A", "Opus", "FLAC"], width=8, state="readonly")
        cb_afmt.pack(side=tk.RIGHT)

        frame_mp3 = tk.Frame(dialog, bg=pal["card_bg"])
        frame_mp3.pack(fill=tk.X, padx=24, pady=4)
        tk.Label(frame_mp3, text="MP3 Bitrate:" if is_en else "Calidad MP3:", font=("sans-serif", 8, "bold"), bg=pal["card_bg"], fg=pal["fg_muted"]).pack(anchor="w", pady=(0, 2))
        var_bitrate = tk.StringVar(value="320k")
        for br, label in [("320k", "320 kbps (Máxima fidelidad)" if not is_en else "320 kbps (Max quality)"),
                          ("192k", "192 kbps (Recomendado)" if not is_en else "192 kbps (Standard)"),
                          ("128k", "128 kbps (Ahorro de espacio)" if not is_en else "128 kbps (Lightweight)")]:
            rb = tk.Radiobutton(frame_mp3, text=label, variable=var_bitrate, value=br, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
            rb.pack(anchor="w", padx=10)

        def on_fmt_change(event=None):
            fmt_val = var_afmt.get().upper()
            state = tk.NORMAL if fmt_val == "MP3" else tk.DISABLED
            for child in frame_mp3.winfo_children():
                if isinstance(child, tk.Radiobutton):
                    child.configure(state=state)

        cb_afmt.bind("<<ComboboxSelected>>", on_fmt_change)

        var_thumb = tk.BooleanVar(value=True)
        cb_th = tk.Checkbutton(dialog, text="Embed official cover art" if is_en else "Incrustar carátula oficial en el archivo", variable=var_thumb, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_th.pack(pady=(4, 2), padx=22, anchor="w")

        var_split = tk.BooleanVar(value=False)
        cb_split = tk.Checkbutton(dialog, text="Split tracks/chapters (--split-chapters)" if is_en else "Dividir en pistas/capítulos automáticos", variable=var_split, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_split.pack(pady=2, padx=22, anchor="w")

        var_sb = tk.BooleanVar(value=self.sponsorblock_enabled)
        cb_sb = tk.Checkbutton(dialog, text=s["sponsorblock"], variable=var_sb, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_sb.pack(pady=2, padx=22, anchor="w")

        trim_frame = tk.LabelFrame(dialog, text="Trim Time Section" if is_en else "Recortar fragmento de tiempo", font=("sans-serif", 8, "bold"), bg=pal["card_bg"], fg=pal["fg_muted"], bd=1, padx=8, pady=4)
        trim_frame.pack(fill=tk.X, padx=22, pady=(6, 10))

        var_trim = tk.BooleanVar(value=False)
        cb_trim = tk.Checkbutton(trim_frame, text="Enable time trimming" if is_en else "Activar recorte por tiempo", variable=var_trim, bg=pal["card_bg"], fg=pal["fg"], selectcolor=pal["entry_bg"], activebackground=pal["card_bg"])
        cb_trim.pack(anchor="w", pady=(0, 4))

        trim_inputs = tk.Frame(trim_frame, bg=pal["card_bg"])
        trim_inputs.pack(fill=tk.X)

        tk.Label(trim_inputs, text="From (MM:SS):" if is_en else "Desde (MM:SS):", font=("sans-serif", 8), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        ent_start = tk.Entry(trim_inputs, width=7, font=("sans-serif", 9), bd=1)
        ent_start.insert(0, "00:00")
        ent_start.pack(side=tk.LEFT, padx=(4, 12))

        tk.Label(trim_inputs, text="To (MM:SS):" if is_en else "Hasta (MM:SS):", font=("sans-serif", 8), bg=pal["card_bg"], fg=pal["fg"]).pack(side=tk.LEFT)
        ent_end = tk.Entry(trim_inputs, width=7, font=("sans-serif", 9), bd=1)
        ent_end.insert(0, "00:00")
        ent_end.pack(side=tk.LEFT, padx=4)

        def confirm():
            fmt = var_afmt.get().lower()
            br = var_bitrate.get()
            thumb = var_thumb.get()
            split = var_split.get()
            sb = var_sb.get()
            self.sponsorblock_enabled = sb
            settings = load_settings()
            settings["sponsorblock"] = sb
            save_settings(settings)
            trim_spec = ""
            if var_trim.get():
                s_val = ent_start.get().strip()
                e_val = ent_end.get().strip()
                if s_val and e_val and (s_val != "00:00" or e_val != "00:00"):
                    trim_spec = f"{s_val}-{e_val}"
            dialog.destroy()
            self.start_download(mode="audio", audio_format=fmt, bitrate=br, embed_thumb=thumb, split_chapters=split, trim_section=trim_spec, sponsorblock=sb)

        btn = tk.Button(dialog, text="Start Download" if is_en else "Iniciar Descarga", command=confirm, bg=pal["btn_primary_bg"], fg=pal["btn_primary_fg"], font=("sans-serif", 9, "bold"), relief="flat", bd=0, padx=14, pady=5, cursor="hand2")
        btn.pack(pady=(4, 0))

    def start_download(self, mode="video", quality="720", fps="30", audio_format="mp3", bitrate="320k", embed_thumb=True, split_chapters=False, trim_section="", sponsorblock=False):
        urls = self.get_selected_urls()
        if not urls:
            is_en = self.current_lang != "es"
            msg = "Select at least one video from the list." if is_en else "Selecciona al menos un vídeo de la lista."
            title = "Download" if is_en else "Descargar"
            messagebox.showinfo(title, msg)
            return

        self.is_cancelled = False
        self.btn_dl_video.config(state=tk.DISABLED)
        self.btn_dl_audio.config(state=tk.DISABLED)
        self.btn_extract_subs.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        self.prog_bar.start(10)
        is_en = self.current_lang != "es"
        msg = f"Starting download ({len(urls)} items)..." if is_en else f"Iniciando descarga ({len(urls)} elemento(s))..."
        self.status_var.set(msg)

        thread = threading.Thread(
            target=self._download_worker,
            args=(urls, mode, quality, fps, audio_format, bitrate, embed_thumb, split_chapters, trim_section, sponsorblock),
            daemon=True
        )
        thread.start()

    def _ask_yesno_from_worker(self, title, message):
        """Solicita confirmación al usuario en el hilo principal de Tkinter."""
        evt = threading.Event()
        result_box = [False]
        self.msg_queue.put(("ask_yesno", (title, message, evt, result_box)))
        evt.wait()
        return result_box[0]

    def _has_recent_download_file(self, since_ts):
        """Comprueba si existe al menos un archivo creado o actualizado en download_dir."""
        try:
            for root_dir, _, files in os.walk(self.download_dir):
                for fname in files:
                    if fname.endswith((".part", ".ytdl", ".tmp")):
                        continue
                    fpath = os.path.join(root_dir, fname)
                    try:
                        st = os.stat(fpath)
                        if st.st_size > 0 and st.st_mtime >= since_ts - 2.0:
                            return True
                    except OSError:
                        pass
        except OSError:
            pass
        return False

    def _write_download_log(self, lines):
        log_path = os.path.join(get_config_dir(), "last_download.log")
        try:
            with open(log_path, "w", encoding="utf-8", errors="replace") as f:
                f.writelines(lines)
        except Exception:
            pass
        return log_path

    def _download_worker(self, urls, mode, quality, fps, audio_format, bitrate, embed_thumb, split_chapters, trim_section, sponsorblock=False):
        ytdlp_cmd = get_binary_path("yt-dlp")
        ffmpeg_cmd = get_binary_path("ffmpeg")
        bin_dir = os.path.dirname(os.path.abspath(ffmpeg_cmd))
        is_en = self.current_lang != "es"
        has_error = False
        last_error_msg = ""

        env = os.environ.copy()
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        for idx, url in enumerate(urls, start=1):
            if self.is_cancelled:
                break

            status_text = f"Downloading [{idx}/{len(urls)}]: connecting..." if is_en else f"Descargando [{idx}/{len(urls)}]: conectando..."
            self.msg_queue.put(("status", status_text))

            base_cmd = [
                ytdlp_cmd,
                "--encoding", "utf-8",
                "-c",
                "--no-mtime",
                "--no-download-archive",
                "--no-simulate",
                "--print", "after_move:__YTCLI_FILE__:%(filepath)s",
                "--extractor-args", f"youtube:lang={self.current_lang}",
                "-P", self.download_dir
            ]

            if split_chapters:
                base_cmd += [
                    "--split-chapters",
                    "-o", "%(title)s/%(section_number)02d - %(section_title)s.%(ext)s"
                ]
            elif trim_section:
                clean_s = trim_section.split("-")[0].replace(":", "")
                clean_e = trim_section.split("-")[1].replace(":", "") if "-" in trim_section else "end"
                base_cmd += [
                    "--download-sections", f"*{trim_section}",
                    "--force-keyframes-at-cuts",
                    "-o", f"%(title)s [{clean_s}_{clean_e}].%(ext)s"
                ]
            else:
                base_cmd += ["-o", "%(title)s.%(ext)s"]

            cookie_choice = self.get_selected_cookie_browser()
            if cookie_choice and is_browser_installed(cookie_choice):
                base_cmd += ["--cookies-from-browser", cookie_choice.lower()]

            if sponsorblock:
                base_cmd += ["--sponsorblock-remove", "sponsor,selfpromo"]

            if mode == "video":
                fps_filter = ""
                if fps == "30":
                    fps_filter = "[fps<=30]"
                elif fps == "60":
                    fps_filter = "[fps<=60]"

                fmt = (
                    f"bestvideo[height<={quality}]{fps_filter}[vcodec^=avc1]+bestaudio[ext=m4a]/"
                    f"bestvideo[height<={quality}]{fps_filter}+bestaudio/"
                    f"best[height<={quality}]{fps_filter}/best"
                )
                base_cmd += [
                    "-f", fmt,
                    "--merge-output-format", "mp4",
                    "--ffmpeg-location", ffmpeg_cmd
                ]
                if embed_thumb:
                    base_cmd += ["--embed-thumbnail"]
            else:
                if audio_format == "m4a":
                    base_cmd += [
                        "-f", "ba[ext=m4a]/ba/b",
                        "-x",
                        "--audio-format", "m4a",
                        "--ffmpeg-location", ffmpeg_cmd
                    ]
                elif audio_format == "opus":
                    base_cmd += [
                        "-f", "ba[ext=opus]/ba[ext=webm]/ba/b",
                        "-x",
                        "--audio-format", "opus",
                        "--ffmpeg-location", ffmpeg_cmd
                    ]
                elif audio_format == "flac":
                    base_cmd += [
                        "-x",
                        "--audio-format", "flac",
                        "--ffmpeg-location", ffmpeg_cmd
                    ]
                else:  # mp3
                    base_cmd += [
                        "-x",
                        "--audio-format", "mp3",
                        "--audio-quality", bitrate,
                        "--ffmpeg-location", ffmpeg_cmd
                    ]
                if embed_thumb:
                    base_cmd += ["--embed-thumbnail"]

            force_overwrite = False
            while True:
                cmd = list(base_cmd)
                if force_overwrite:
                    cmd.append("--force-overwrites")
                cmd.append(url)

                dl_start_time = time.time()
                try:
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        env=env,
                        **SUBPROCESS_FLAGS
                    )
                    self.active_process = proc

                    merge_failed = False
                    already_exists = False
                    reported_files = []
                    all_output_lines = []

                    for line in proc.stdout:
                        all_output_lines.append(line)
                        line_clean = line.strip()
                        if line_clean.startswith("__YTCLI_FILE__:"):
                            fpath = line_clean.split("__YTCLI_FILE__:", 1)[1].strip()
                            if fpath:
                                reported_files.append(fpath)
                        elif "[download]" in line and "%" in line:
                            pct_text = line_clean.replace("[download]", "").strip()
                            self.msg_queue.put(("status", f"[{idx}/{len(urls)}] {pct_text}"))
                        elif "has already been downloaded" in line:
                            already_exists = True
                        elif "ffmpeg is not installed" in line or "won't be merged" in line:
                            merge_failed = True
                        elif "ERROR:" in line:
                            last_error_msg = line_clean

                    proc.wait()
                    if self.is_cancelled:
                        break

                    if proc.returncode != 0:
                        has_error = True
                        log_path = self._write_download_log(all_output_lines)
                        if not last_error_msg:
                            last_error_msg = f"Item {idx} failed (exit code {proc.returncode}). Log: {log_path}" if is_en else f"Error en elemento {idx}. Código: {proc.returncode}. Log: {log_path}"
                        self.msg_queue.put(("error", last_error_msg))
                        break

                    if merge_failed:
                        has_error = True
                        log_path = self._write_download_log(all_output_lines)
                        last_error_msg = (
                            f"FFmpeg was not detected or failed to merge audio and video.\nLog: {log_path}"
                            if is_en else
                            f"FFmpeg no fue detectado o falló al unir el audio y vídeo.\nLog: {log_path}"
                        )
                        self.msg_queue.put(("error", last_error_msg))
                        break

                    verified_files = [
                        p for p in reported_files
                        if os.path.isfile(p) and os.path.getsize(p) > 0
                    ]
                    if not verified_files and not self._has_recent_download_file(dl_start_time):
                        if already_exists and not force_overwrite:
                            title_ask = "File Already Exists" if is_en else "Archivo Existente"
                            msg_ask = (
                                "This file already exists in the destination folder.\nDo you want to download it again?"
                                if is_en else
                                "Este archivo ya existe en la carpeta de destino.\n¿Quieres descargarlo de nuevo?"
                            )
                            if self._ask_yesno_from_worker(title_ask, msg_ask):
                                force_overwrite = True
                                continue
                            break

                        has_error = True
                        log_path = self._write_download_log(all_output_lines)
                        tail = "".join(all_output_lines[-6:]).strip()
                        last_error_msg = (
                            f"Download finished but no file was found in:\n{self.download_dir}\n\nDetails:\n{tail}\n\nLog: {log_path}"
                            if is_en else
                            f"El proceso terminó pero no se generó ningún archivo en:\n{self.download_dir}\n\nDetalle:\n{tail}\n\nLog: {log_path}"
                        )
                        self.msg_queue.put(("error", last_error_msg))
                        break

                    break
                except Exception as e:
                    if not self.is_cancelled:
                        has_error = True
                        last_error_msg = f"Download error: {str(e)}" if is_en else f"Error en descarga: {str(e)}"
                        self.msg_queue.put(("error", last_error_msg))
                    break
                finally:
                    self.active_process = None

            if has_error or self.is_cancelled:
                break

        if self.is_cancelled:
            self.msg_queue.put(("download_cancelled", None))
        elif has_error:
            self.msg_queue.put(("download_error", last_error_msg))
        else:
            self.msg_queue.put(("download_done", None))

    def start_subtitles_download(self):
        urls = self.get_selected_urls()
        if not urls:
            is_en = self.current_lang == "en"
            msg = "Select at least one video from the list." if is_en else "Selecciona al menos un vídeo de la lista."
            title = "Subtitles" if is_en else "Subtítulos"
            messagebox.showinfo(title, msg)
            return

        self.is_cancelled = False
        self.btn_dl_video.config(state=tk.DISABLED)
        self.btn_dl_audio.config(state=tk.DISABLED)
        self.btn_extract_subs.config(state=tk.DISABLED)
        self.btn_cancel.config(state=tk.NORMAL)
        self.prog_bar.start(10)
        is_en = self.current_lang == "en"
        msg = f"Extracting subtitles/transcripts ({len(urls)} items)..." if is_en else f"Extrayendo subtítulos y transcripción ({len(urls)} elemento(s))..."
        self.status_var.set(msg)

        thread = threading.Thread(
            target=self._subtitles_worker,
            args=(urls,),
            daemon=True
        )
        thread.start()

    def _subtitles_worker(self, urls):
        ytdlp_cmd = get_binary_path("yt-dlp")
        ffmpeg_cmd = get_binary_path("ffmpeg")
        bin_dir = os.path.dirname(os.path.abspath(ffmpeg_cmd))
        is_en = self.current_lang == "en"
        has_error = False
        last_error_msg = ""

        env = os.environ.copy()
        env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        for idx, url in enumerate(urls, start=1):
            if self.is_cancelled:
                break
            status_text = f"Extracting subtitles [{idx}/{len(urls)}]..." if is_en else f"Extrayendo subtítulos [{idx}/{len(urls)}]..."
            self.msg_queue.put(("status", status_text))

            cmd = [
                ytdlp_cmd,
                "--encoding", "utf-8",
                "-c",
                "--no-mtime",
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-lang", f"{self.current_lang},es,en",
                "--extractor-args", f"youtube:lang={self.current_lang}",
                "--ffmpeg-location", ffmpeg_cmd,
                "--sub-format", "srt/vtt/best",
                "--convert-subs", "srt",
                "--no-warnings",
                "-P", self.download_dir,
                "-o", "%(title)s.%(ext)s"
            ]

            cookie_choice = self.get_selected_cookie_browser()
            if cookie_choice and is_browser_installed(cookie_choice):
                cmd += ["--cookies-from-browser", cookie_choice.lower()]

            cmd.append(url)

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                    **SUBPROCESS_FLAGS
                )
                self.active_process = proc

                for line in proc.stdout:
                    if "[info]" in line or "[download]" in line:
                        clean_line = line.strip().replace("[download]", "").strip()
                        self.msg_queue.put(("status", f"[{idx}/{len(urls)}] {clean_line}"))

                proc.wait()
                if self.is_cancelled:
                    break
                if proc.returncode != 0:
                    has_error = True
                    last_error_msg = f"Subtitle extraction item {idx} failed (code {proc.returncode})" if is_en else f"Error en elemento {idx} al extraer subtítulos (código {proc.returncode})"
                    self.msg_queue.put(("error", last_error_msg))
                    break

                # Convertir SRTs descargados a texto limpio (.txt)
                srt_files = glob.glob(os.path.join(self.download_dir, "*.srt"))
                for srt_path in srt_files:
                    txt_path = os.path.splitext(srt_path)[0] + ".txt"
                    if os.path.exists(txt_path):
                        continue
                    try:
                        with open(srt_path, "r", encoding="utf-8", errors="replace") as f:
                            lines = f.readlines()
                        clean_text = []
                        last_line = ""
                        for line in lines:
                            l = line.strip()
                            if not l or l.isdigit() or "-->" in l:
                                continue
                            l = re.sub(r"<[^>]+>", "", l).strip()
                            if l and l != last_line:
                                clean_text.append(l)
                                last_line = l
                        if clean_text:
                            with open(txt_path, "w", encoding="utf-8") as out:
                                out.write("\n".join(clean_text) + "\n")
                    except Exception:
                        pass
            except Exception as e:
                if not self.is_cancelled:
                    has_error = True
                    last_error_msg = f"Extraction error: {str(e)}" if is_en else f"Error en extracción: {str(e)}"
                    self.msg_queue.put(("error", last_error_msg))
                break
            finally:
                self.active_process = None

        if self.is_cancelled:
            self.msg_queue.put(("download_cancelled", None))
        elif has_error:
            self.msg_queue.put(("download_error", last_error_msg))
        else:
            self.msg_queue.put(("download_done", None))

    def cancel_process(self):
        self.is_cancelled = True
        if self.mpv_process and self.mpv_process.poll() is None:
            try:
                self.mpv_process.terminate()
            except Exception:
                pass
            self.mpv_process = None
            self.status_var.set("Reproducción detenida.")

        if self.active_process and self.active_process.poll() is None:
            try:
                self.active_process.terminate()
            except Exception:
                pass
            self.active_process = None
            self.status_var.set("Descarga cancelada.")

        self.btn_cancel.config(state=tk.DISABLED)
        self.btn_dl_video.config(state=tk.NORMAL)
        self.btn_dl_audio.config(state=tk.NORMAL)
        self.btn_extract_subs.config(state=tk.NORMAL)
        self.prog_bar.stop()

    def on_close(self):
        """Mata limpiamente todos los subprocesos al cerrar la ventana."""
        self.is_cancelled = True
        if self.mpv_process and self.mpv_process.poll() is None:
            try:
                self.mpv_process.terminate()
            except Exception:
                pass
        if self.active_process and self.active_process.poll() is None:
            try:
                self.active_process.terminate()
            except Exception:
                pass
        self.root.destroy()

    def process_queue(self):
        try:
            while True:
                msg, data = self.msg_queue.get_nowait()
                if msg == "search_done":
                    self.prog_bar.stop()
                    self.btn_search.config(state=tk.NORMAL)
                    self.last_search_results = data
                    self.is_viewing_history = False
                    self.btn_hist_clear.pack_forget()
                    s = self.get_strings()
                    self.btn_history.config(text=s["history"])
                    for idx, item in enumerate(data):
                        tag = "evenrow" if idx % 2 == 0 else "oddrow"
                        self.tree.insert("", tk.END, values=item, tags=(tag,))
                    self.status_var.set(f"{s['ready']} ({len(data)})")
                elif msg == "status":
                    self.status_var.set(data)
                elif msg == "ask_yesno":
                    title_ask, msg_ask, evt, result_box = data
                    try:
                        result_box[0] = messagebox.askyesno(title_ask, msg_ask)
                    finally:
                        evt.set()
                elif msg == "error":
                    self.status_var.set(data)
                    messagebox.showerror("Aviso", data)
                elif msg == "download_cancelled":
                    self.prog_bar.stop()
                    self.btn_dl_video.config(state=tk.NORMAL)
                    self.btn_dl_audio.config(state=tk.NORMAL)
                    self.btn_extract_subs.config(state=tk.NORMAL)
                    self.btn_cancel.config(state=tk.DISABLED)
                    is_en = self.current_lang == "en"
                    self.status_var.set("Download cancelled by user." if is_en else "Descarga cancelada por el usuario.")
                elif msg == "download_error":
                    self.prog_bar.stop()
                    self.btn_dl_video.config(state=tk.NORMAL)
                    self.btn_dl_audio.config(state=tk.NORMAL)
                    self.btn_extract_subs.config(state=tk.NORMAL)
                    self.btn_cancel.config(state=tk.DISABLED)
                    is_en = self.current_lang == "en"
                    self.status_var.set("Operation finished with errors." if is_en else "Operación finalizada con errores.")
                elif msg == "download_done":
                    self.prog_bar.stop()
                    self.btn_dl_video.config(state=tk.NORMAL)
                    self.btn_dl_audio.config(state=tk.NORMAL)
                    self.btn_extract_subs.config(state=tk.NORMAL)
                    self.btn_cancel.config(state=tk.DISABLED)
                    is_en = self.current_lang == "en"
                    self.status_var.set("Downloads finished!" if is_en else "¡Descargas finalizadas!")
                    title_done = "Completed" if is_en else "Completado"
                    msg_done = f"Downloads saved to:\n{self.download_dir}" if is_en else f"Descargas guardadas en:\n{self.download_dir}"
                    messagebox.showinfo(title_done, msg_done)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

def main():
    root = tk.Tk()
    app = YtCliGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
