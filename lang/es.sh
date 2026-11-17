# ==============================================================================
# YT-CLI: Archivo de idioma español (Spanish Language Pack)
# Código de idioma: es
# ==============================================================================

LANG_CODE="es"
LANG_NAME="Español"

# --- Banner principal y prompt ---
MSG_BANNER_CREDITS="YT-CLI v1.3 • Creado por Kenny Waddell (@KennyWaddell)"
MSG_BANNER_SUBTITLE="Cliente Multimedia: YouTube, TikTok, X, Reels y +1000 sitios"
MSG_BANNER_FEATURES="Aceleración HWDEC Auto • Cola FZF • Descargas MP4/MP3"
MSG_BANNER_SEARCHES="Búsquedas: término | @canal | @canal término | enlaces URL"
MSG_BANNER_CMD_1="Comandos:  [:help] Ayuda     [:h] Historial    [:c] Cookies"
MSG_BANNER_CMD_2="           [:lang] Idioma    [:about] Créditos [q] Salir"
MSG_SEARCH_PROMPT="Buscar, enlace o comando [:help | q]: "
MSG_GOODBYE="Hasta luego."

# --- Búsquedas ---
MSG_SEARCHING="Buscando en YouTube:"
MSG_SEARCHING_CHANNEL="Buscando en canal"
MSG_FETCHING_CHANNEL="Obteniendo videos del canal"
MSG_NO_RESULTS="No se encontraron resultados para:"
MSG_EXITING_LIST="Saliendo de la lista actual de resultados..."
MSG_SELECTED_ITEMS="Elementos seleccionados:"
MSG_FZF_PROMPT="▶ Selecciona video(s) > "
MSG_FZF_HEADER="[Enter] Ver | [Tab] Marcar varios | [ESC] Salir | [Flechas] Navegar"

# --- Portapapeles ---
MSG_CLIPBOARD_DETECTED="📋 Enlace detectado en el portapapeles:"
MSG_CLIPBOARD_CONFIRM="¿Deseas abrir este enlace? [S/n] (Enter para Sí): "

# --- Menú de acciones (Reproducir / Descargar / Volver) ---
MSG_ACTION_TITLE="¿Qué deseas hacer con"
MSG_ACTION_SINGLE="este video"
MSG_ACTION_MULTI="videos en cola"
MSG_ACTION_STREAM_HEADER="── REPRODUCIR (STREAMING AL VUELO) ─────────────────"
MSG_ACTION_1="Ver en 720p HD a 30fps  (Recomendado GPU Auto-Safe) ★ Predeterminado"
MSG_ACTION_2="Ver en 1080p Full HD     (30fps acelerado H.264)"
MSG_ACTION_3="Ver en 480p / 360p       (Ahorro de datos/CPU)"
MSG_ACTION_4="Escuchar solo audio      (Modo radio/podcast - ~25MB RAM)"
MSG_ACTION_DOWNLOAD_HEADER="── DESCARGAR Y GUARDAR EN DISCO ────────────────────"
MSG_ACTION_5="Descargar Video(s) 720p  (MP4 H.264 en disco/USB)"
MSG_ACTION_6="Descargar Video(s) 1080p (MP4 Full HD en disco/USB)"
MSG_ACTION_7="Descargar Audio(s) MP3   (Con carátula y metadatos)"
MSG_ACTION_NAV_HEADER="── NAVEGACIÓN ──────────────────────────────────────"
MSG_ACTION_0="Volver a la lista / Cancelar"
MSG_ACTION_PROMPT="Elige opción [1-7 | 0 para volver] (Enter para ver en 720p): "

# --- Reproductor MPV ---
MSG_MPV_AUDIO_START="▶ Modo Solo Audio (Reproductor compacto interactivo - ~25 MB RAM)..."
MSG_MPV_AUDIO_WAIT="⏳ Cargando audio/playlist... la ventana de controles abrirá en unos segundos."
MSG_MPV_AUDIO_TIPS="[Atajos Audio: 'Espacio' pausa | '←/→' retroceder/avanzar | 'l' bucle | '>/<' sig./ant. | '9/0' vol | 'q' salir]"
MSG_MPV_QUEUE_ACTIVE="🎶 Cola activa con"
MSG_MPV_QUEUE_TIPS="[Atajos MPV: '>' siguiente | '<' anterior | 'q' salir | 'Espacio' pausa | 'f' pantalla completa]"
MSG_MPV_SINGLE_TIPS="[Atajos MPV: 'q' cerrar y volver a lista | 'Espacio' pausa | '9/0' volumen | 'f' pantalla completa]"
MSG_MPV_PLAY_360="▶ Reproduciendo en 360p (H.264 / 30fps)..."
MSG_MPV_PLAY_480="▶ Reproduciendo en 480p (H.264 / 30fps)..."
MSG_MPV_PLAY_720="▶ Reproduciendo en 720p (H.264 / auto-safe)..."
MSG_MPV_PLAY_1080="▶ Reproduciendo en 1080p a 30fps (H.264 / auto-safe, fallback 720p)..."

# --- Descargas ---
MSG_DL_DEST_TITLE="Carpeta de destino para descarga:"
MSG_DL_DEST_DEFAULT="Predeterminada:"
MSG_DL_DEST_DRIVE="Pendrive/Disco externo:"
MSG_DL_DEST_CUSTOM="Escribir otra ruta personalizada..."
MSG_DL_DEST_PROMPT="Elige opción (Enter para predeterminada): "
MSG_DL_DEST_INPUT="Introduce la ruta de la carpeta: "
MSG_DL_VIDEO_START="⬇ Descargando Video(s) en"
MSG_DL_SAVING_IN="Guardando en:"
MSG_DL_SUCCESS_NOTIFY="Descarga Completada"
MSG_DL_SUCCESS_MSG="Video descargado correctamente en"
MSG_DL_FAILED="Falló la descarga de:"
MSG_DL_ALL_COMPLETE="✔ Descarga(s) finalizada(s)."
MSG_DL_MUSIC_QUALITY_HEADER="Selecciona calidad de audio MP3:"
MSG_DL_MUSIC_Q1="320 kbps (Máxima fidelidad de audio) ★ Recomendado"
MSG_DL_MUSIC_Q2="192 kbps (Equilibrio calidad / tamaño)"
MSG_DL_MUSIC_Q3="128 kbps (Menor peso / Descarga rápida)"
MSG_DL_MUSIC_Q_PROMPT="Elige calidad [1-3] (Enter para 320k): "
MSG_DL_EMBED_COVER_PROMPT="¿Incrustar carátula en los MP3? [S/n] (Enter para Sí): "
MSG_DL_MUSIC_START="🎵 Descargando en MP3"
MSG_DL_MUSIC_NOTIFY_TITLE="Música Descargada"
MSG_DL_MUSIC_NOTIFY_MSG="Canción guardada con metadatos en"

# --- Historial ---
MSG_HIST_EMPTY="El historial está vacío."
MSG_HIST_CLEARED="✔ Historial borrado correctamente."
MSG_HIST_CLEAR_OPTION="🗑️  Borrar todo el historial"
MSG_HIST_PROMPT="📜 Historial (máx. 50) > "
MSG_HIST_HEADER="[Enter] Ver vídeo/playlist o Borrar | [ESC] Volver"

# --- Cookies ---
MSG_COOKIE_PROMPT="Introduce navegador o ruta a cookies (ej: brave, firefox, cookies.txt): "
MSG_COOKIE_SUCCESS="✔ Cookies configuradas para:"
MSG_COOKIE_ERROR_NOT_FOUND="[ERROR] El archivo de cookies no existe:"
MSG_COOKIE_BROWSER_EMPTY="[ERROR] Debes indicar un navegador o ruta a cookies (ej: -c brave, -c firefox, -c cookies.txt)"

# --- Idioma ---
MSG_LANG_CURRENT="Idioma actual:"
MSG_LANG_CHOOSE="Selecciona idioma:"
MSG_LANG_SAVED="✔ Idioma cambiado correctamente a:"

# --- Ayuda interactiva ---
MSG_HELP_TITLE="GUÍA RÁPIDA DE COMANDOS (YT-CLI)"
MSG_HELP_SEARCH_HEADER="Búsquedas y Enlaces:"
MSG_HELP_SEARCH_KW="Búsqueda general en YouTube (ej: noticias de hoy)"
MSG_HELP_SEARCH_CH="Ver videos recientes de un canal (ej: @ElCuriosoBen)"
MSG_HELP_SEARCH_CH_TERM="Buscar dentro de un canal (ej: @DrossRotzank misterio)"
MSG_HELP_SEARCH_URL="Pega enlaces de YouTube, TikTok, X, Reels, etc."
MSG_HELP_CMD_HEADER="Comandos en la consola interactiva:"
MSG_HELP_CMD_HELP="Muestra este resumen de ayuda"
MSG_HELP_CMD_HIST="Abre el historial interactivo de reproducción"
MSG_HELP_CMD_CLEAR="Borra todo el historial local guardado"
MSG_HELP_CMD_COOKIE="Activa cookies de navegador (Brave, Firefox, etc.)"
MSG_HELP_CMD_LANG="Cambia el idioma (Español / English)"
MSG_HELP_CMD_ABOUT="Muestra los créditos y acerca de YT-CLI"
MSG_HELP_CMD_QUIT="Cierra YT-CLI"
MSG_HELP_CLI_HEADER="Opciones al arrancar desde terminal externa:"
MSG_HELP_CLI_AUDIO="Modo podcast (Solo audio, ~25 MB RAM)"
MSG_HELP_CLI_DOWN="Descargar directamente en MP4 (720p H.264)"
MSG_HELP_CLI_MUSIC="Descargar canción directamente en MP3 (320k)"
MSG_HELP_CLI_HIST="Abrir historial directamente"
MSG_HELP_CLI_HELP="Ver todos los flags de ejecución"
MSG_HELP_PRESS_ENTER="Presiona [Enter] para volver al menú principal..."
MSG_PRESS_ENTER_RETRY="¿Presione [Enter] para otra búsqueda o [q] para salir: "

# --- Créditos / Acerca de ---
MSG_ABOUT_TITLE="ACERCA DE YT-CLI / CRÉDITOS"
MSG_ABOUT_VERSION="Versión:"
MSG_ABOUT_AUTHOR="Autor:"
MSG_ABOUT_COLLAB="Colaboración:"
MSG_ABOUT_LICENSE="Licencia:"
MSG_ABOUT_REPO="Repositorio:"
MSG_ABOUT_TAGLINE="Dedicado a la comunidad de Linux y usuarios de hardware modesto."
