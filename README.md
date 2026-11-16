# 🎬 YT-CLI

> **Cliente y Gestor Multimedia Ultraligero para Terminal en Linux y GUI Portable en Windows**  
> Diseñado específicamente para equipos de recursos limitados (Intel Celeron, Atom, ThinkPads clásicas y PCs con 2 GB de RAM). Compatible con Linux y Windows 7, 8.1, 10 y 11.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform: Linux & Windows](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue.svg)](#requisitos-del-sistema)
[![Shell: Bash](https://img.shields.io/badge/Shell-Bash-green.svg)](#instalación-rápida-en-linux)
[![GUI: Python Tkinter](https://img.shields.io/badge/GUI-Tkinter%20(Windows)-orange.svg)](#uso-en-windows-portable)
[![Backend: MPV & yt--dlp](https://img.shields.io/badge/Backend-MPV%20%2B%20yt--dlp-red.svg)](#características-principales)

---

## ⚡ El Problema que Resuelve

En navegadores web modernos (Brave, Chrome, Firefox), abrir YouTube consume entre **900 MB y 1.4 GB de RAM**, además de disparar la CPU al **100%** debido a cientos de scripts JavaScript, telemetría y renderizado pesado del DOM. En procesadores modestos de 2 núcleos, esto provoca congelamientos, ventiladores al máximo y videos con tirones.

**YT-CLI** elimina por completo el navegador de la ecuación:
* Realiza búsquedas instantáneas en texto plano con **FZF**.
* Transmite el flujo de video directamente a **MPV**.
* Fuerza decodificación por hardware **Intel VA-API** en códec **H.264 (AVC) a un máximo de 30 fps**.

| Métrica | YouTube en Navegador Web | YT-CLI + MPV |
| :--- | :--- | :--- |
| **Consumo de Memoria RAM** | ~1.100 MB (1.1 GB) | **~75 MB - 110 MB** (Ahorro del 90%) |
| **Carga de CPU en Reproducción** | 80% - 100% (Lags y calor) | **15% - 25%** (Fluido a 60/30fps) |
| **Modo Solo Audio (Música/Podcast)** | 600 MB - 800 MB | **~25 MB** |
| **Privacidad** | Rastreadores y cookies | **100% Anónimo (Sin historial)** |

---

## ✨ Características Principales

* 🔍 **Buscador interactivo ultrarrápido:** Filtra en tiempo real por título, duración y canal mediante el teclado con `fzf`.
* 🎶 **Cola de reproducción y selección múltiple:** Marca varios videos o canciones con la tecla `Tab` en `fzf` para reproducirlos en cola continua en MPV (`>` siguiente / `<` anterior) o descargarlos en lote.
* 📋 **Detección mágica del portapapeles:** Al arrancar, si tienes copiado un enlace de YouTube, TikTok, X (Twitter), etc., `yt-cli` lo detecta automáticamente y te ofrece abrirlo o descargarlo al instante.
* 🔄 **Lista de resultados persistente:** Cuando un video termina (o pulsas `q` para cerrarlo), la lista de búsqueda anterior **reaparece al instante** sin tener que volver a escribir ni recargar.
* 📺 **Selector de resoluciones inteligente:**
  * **720p HD a 30fps:** El equilibrio perfecto para pantallas de portátiles y bajo consumo de CPU.
  * **1080p Full HD:** Forzando códec H.264 acelerado por GPU (con fallback suave a 720p si el video no dispone de H.264 para proteger tu CPU de códecs pesados como AV1 o VP9).
  * **480p / 360p:** Para conexiones lentas o ahorro extremo de energía.
  * **Solo Audio:** Ideal para podcasts, conferencias o música de fondo consumiendo apenas 25 MB de RAM.
* ⬇️ **Descargas completas y reanudables:**
  * **Reanudación automática:** Si se interrumpe la conexión, retoma la descarga en el mismo punto sin perder datos (`--continue`).
  * **Selector de carpetas:** Permite guardar en tus carpetas del sistema, pendrives USB montados o rutas personalizadas.
  * **Videos en MP4:** Compatibles con cualquier reproductor, TV o móvil (con miniatura incrustada).
  * **Música en MP3:** Calidades a 320 kbps, 192 kbps o 128 kbps con carátula oficial y etiquetas ID3.
  * **Soporte para Playlists:** Descarga listas completas en lote sin interrupciones.
* 📜 **Historial local y reanudación automática:** Recuerda tus últimos videos vistos (`yt-cli -H` o `:h`) y retoma la reproducción exactamente en el segundo donde lo dejaste (`--save-position-on-quit`). Totalmente privado, local y configurable.
* 🍪 **Soporte de cookies de navegador:** Supera restricciones de edad o avisos de bot pasando cookies de Brave, Chrome, Firefox o Edge (`-c brave` / desplegable en GUI).
* 🪟 **Cliente Gráfico Portable para Windows (Windows 7 / 8.1 / 10 / 11):** Interfaz moderna y ligera sin instalaciones complejas, con tema oscuro/claro, descargas interactivas, barra de progreso y reproductor de audio dedicado.
* 🌐 **Soporte Multiplataforma:** No solo funciona con YouTube; puedes pegar enlaces directos de **TikTok, Twitter/X, Instagram Reels, Twitch, Reddit, SoundCloud y más de 1.000 sitios soportados**.
* 🔔 **Notificaciones de escritorio:** Alerta nativa no bloqueante al finalizar descargas en segundo plano.
* 🛡️ **Privacidad y Control:** Sin telemetría ni rastreadores. Historial local opcional y posibilidad de eliminarlo con un solo comando o clic.

---

## 📋 Requisitos del Sistema

Requiere las siguientes herramientas estándar de Linux:
* `bash` (v4.0+)
* `yt-dlp` (Motor de extracción multimedia)
* `fzf` (Buscador interactivo en terminal)
* `mpv` (Reproductor de video y audio)
* `ffmpeg` (Para empaquetado y conversión a MP3)

### Instalación de dependencias:

* **Debian / Ubuntu / antiX / Linux Mint:**
  ```bash
  sudo apt update && sudo apt install yt-dlp fzf mpv ffmpeg
  ```
* **Arch Linux / Manjaro:**
  ```bash
  sudo pacman -S yt-dlp fzf mpv ffmpeg
  ```
* **Fedora:**
  ```bash
  sudo dnf install yt-dlp fzf mpv ffmpeg
  ```

---

## 🚀 Instalación Rápida

1. Clona el repositorio:
   ```bash
   git clone https://github.com/KennyWaddell/yt-cli.git
   cd yt-cli
   ```

2. Ejecuta el instalador:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

El instalador:
1. Copiará el ejecutable a `~/.local/bin/yt-cli`.
2. Instalará el acceso directo con su icono oficial en tu menú de aplicaciones y en el Escritorio.
3. Configurará automáticamente los extractores optimizados en `~/.config/yt-dlp/config`.

---

## 💻 Modo de Uso

### 1. Interfaz interactiva completa (Recomendado)
Escribe en cualquier terminal:
```bash
yt-cli
```
*(O dale doble clic al icono **YT-CLI** en tu Escritorio).*

1. Escribe tu búsqueda o pega cualquier enlace.
2. Selecciona con las flechas y presiona `Enter`.
3. Elige la calidad de reproducción o descarga en el menú rápido.

### 2. Búsqueda directa desde terminal
```bash
yt-cli "noticias de tecnologia"
```

### 3. Modo Podcast / Solo Audio
```bash
yt-cli -a "musica lofi hip hop"
```

### 4. Descarga directa de enlaces
```bash
# Descargar video en MP4 (720p H.264):
yt-cli -d "https://www.youtube.com/watch?v=..."

# Descargar canción en MP3 (320 kbps):
yt-cli -m "https://www.youtube.com/watch?v=..."

# Funciona con enlaces de TikTok, X (Twitter), etc.:
yt-cli -d "https://www.tiktok.com/@usuario/video/..."
```

---

## 🪟 Uso en Windows (Versión Portable Standalone)

YT-CLI incluye una versión oficial con interfaz gráfica moderna y ligera para **Windows 7 SP1, 8.1, 10 y 11 (64-bit)**. No requiere instalar Python, ni configurar dependencias, ni tocar el `PATH` del sistema.

### Pasos rápidos:
1. Ve a la sección de [**Releases**](https://github.com/KennyWaddell/yt-cli/releases) y descarga **`YT-CLI-Windows-Portable.zip`**.
2. Descomprime el archivo `.zip` en la carpeta que prefieras.
3. Haz doble clic en **`YT-CLI.exe`** para iniciar la aplicación de inmediato.
4. *(Opcional)*: Haz clic derecho en `YT-CLI.exe` -> *Enviar a* -> *Escritorio (crear acceso directo)* para tenerlo a mano con su icono oficial.

---

## ⌨️ Atajos de Teclado en MPV

| Tecla | Acción |
| :--- | :--- |
| `q` | Cerrar el video y volver instantáneamente a la lista de búsqueda |
| `Espacio` | Pausar / Reanudar |
| `f` | Alternar pantalla completa |
| `9` / `0` | Bajar / Subir volumen |
| `←` / `→` | Retroceder / Avanzar 5 segundos |
| `>` / `<` | Siguiente / Anterior en cola de reproducción |
| `i` | Mostrar resolución actual, fps y códec en pantalla |
| `Shift + i` | Mostrar panel técnico completo (GPU VA-API/DXVA2, dropped frames, caché) |

---

## 🗺️ Roadmap

- [x] Soporte para reanudación de descargas interrumpidas (`-c` / `--continue`).
- [x] Selector interactivo de carpetas de destino (disco local, pendrives USB y rutas personalizadas).
- [x] Cola de reproducción múltiple en FZF (marcar con tecla `Tab`).
- [x] Detección mágica del portapapeles y notificaciones de escritorio.
- [x] Historial local con reanudación automática de posición (`--save-position-on-quit`).
- [x] Soporte para cookies de sesión de navegadores (Brave, Firefox, Chrome, Edge).
- [x] Versión multiplataforma con GUI nativa minimalista para **Windows 7 / 8.1 / 10 / 11**.
- [x] Compilación standalone de `YT-CLI.exe` con PyInstaller y empaquetado portable para la sección de Releases.
- [ ] Filtro y buscador directo por canal / creador de contenido específico (previsto para v1.2).
- [ ] Previsualización con miniaturas compactas en búsquedas mediante carga asíncrona en segundo plano (previsto para v1.2).

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **GNU General Public License v3.0 (GPLv3)**. Consulta el archivo [LICENSE](LICENSE) para más información.  
El conocimiento y el software pertenecen a la comunidad.

---

## 👤 Autor

Desarrollado y mantenido por **Kenny Waddell**  
* GitHub: [@KennyWaddell](https://github.com/KennyWaddell)  
* *Desarrollado en colaboración y optimización con Antigravity (Google DeepMind).*
