==============================================================================
               YT-CLI: Ultralight Multimedia Client (Windows)
==============================================================================
Author: Kenny Waddell (@KennyWaddell)
License: GNU General Public License v3.0 (GPLv3)
Repository: https://github.com/KennyWaddell/yt-cli

DESCRIPTION
-----------
YT-CLI for Windows is a modern, native, and ultralight graphical interface
designed to search, stream, and download multimedia from YouTube and hundreds
of platforms with hardware acceleration (GPU).

REQUIREMENTS
------------
1. Windows 7 SP1, 8.1, 10, or 11 (64-bit).
2. Fully portable: does NOT require Python or external dependencies installed.

QUICK START
-----------
1. Double-click "YT-CLI.exe" to launch the application.
2. (Optional) To create a desktop shortcut: right-click "YT-CLI.exe",
   select "Send to" -> "Desktop (create shortcut)".

INCLUDED COMPONENTS
-------------------
All multimedia engines are pre-packaged inside the "bin/" folder:
  - yt-dlp.exe        (Search and download engine)
  - mpv.exe           (High-performance GPU video/audio player)
  - ffmpeg.exe        (Audio/video conversion and stream merger)
  - ffprobe.exe       (Media stream analyzer)
  - vulkan-1.dll      (Graphics compatibility runtime)
  - d3dcompiler_43.dll

FEATURES (v1.4)
---------------
* Smooth video streaming in 360p, 480p, 720p, 1080p, and 60 FPS (GPU Auto-Safe).
* MP4 video downloads with automatic chapter splitting and time trimming.
* Modern native audio formats: MP3 (320k/192k/128k), M4A, Opus, and FLAC with cover art.
* Subtitle and plain-text transcript extractor (.txt and .srt).
* Safe download archive: prevents duplicate downloads automatically.
* Private local watch history with auto-resume where you left off.
* Session cookie support for Brave, Chrome, Firefox, and Edge.
* Dynamic Dark and Light themes.
* Ultralow memory footprint (~22 MB RAM).

FREQUENTLY ASKED QUESTIONS (FAQ)
--------------------------------
Q: Why does Windows SmartScreen or antivirus show a warning?
A: This is a classic heuristic false positive common to PyInstaller executables
   that do not possess an expensive commercial code-signing certificate (which cost
   hundreds of dollars per year). The software is 100% open source under the GPLv3
   license and every line of code can be audited on GitHub. Click "More info" and
   then "Run anyway".

Q: How do I update yt-dlp if YouTube makes internal changes?
A: Simply replace "yt-dlp.exe" inside the "bin/" folder with the latest release:
   https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
   No recompilation or setup needed!


==============================================================================
               YT-CLI: Cliente Multimedia Ultraligero (Windows)
==============================================================================
Autor: Kenny Waddell (@KennyWaddell)
Licencia: GNU General Public License v3.0 (GPLv3)
Repositorio: https://github.com/KennyWaddell/yt-cli

DESCRIPCION
-----------
YT-CLI para Windows es una interfaz grafica moderna, nativa y ultraligera
disenada para buscar, reproducir y descargar contenido de YouTube y cientos
de plataformas con aceleracion por hardware (GPU).

REQUISITOS
----------
1. Windows 7 SP1, 8.1, 10 u 11 (64-bit).
2. Completamente portable: NO requiere instalar Python ni dependencias en el sistema.

INSTRUCCIONES DE USO
--------------------
1. Haz doble clic sobre "YT-CLI.exe" para iniciar la aplicacion.
2. (Opcional) Si deseas tener un acceso directo en tu Escritorio, haz clic
   derecho sobre "YT-CLI.exe", selecciona "Enviar a" y luego "Escritorio
   (crear acceso directo)".

COMPONENTES INCLUIDOS
---------------------
Todos los motores multimedia ya vienen incluidos dentro de la carpeta "bin/":
  - yt-dlp.exe        (Motor de busqueda y descarga)
  - mpv.exe           (Reproductor multimedia de alto rendimiento)
  - ffmpeg.exe        (Conversor y unificador de audio/video)
  - ffprobe.exe       (Analizador de flujos multimedia)
  - vulkan-1.dll      (Libreria de compatibilidad grafica)
  - d3dcompiler_43.dll

CARACTERISTICAS (v1.4)
----------------------
* Streaming fluido en 360p, 480p, 720p, 1080p y 60 FPS (GPU Auto-Safe).
* Descargas MP4 (con division en capitulos y recorte por tiempo).
* Audio multiformato nativo: MP3 (320k/192k/128k), M4A, Opus y FLAC con caratula.
* Extraccion de subtitulos y transcripciones limpias en texto plano (.txt y .srt).
* Historial seguro de descargas previas (evita duplicar descargas ya realizadas).
* Historial local con reanudacion automatica donde lo dejaste.
* Soporte para cookies de sesion de Brave, Chrome, Firefox y Edge.
* Modos visuales Tema Oscuro y Tema Claro.
* Consumo ultrabajo de memoria RAM (~22 MB).

PREGUNTAS FRECUENTES (FAQ)
--------------------------
P: ¿Por qué Windows SmartScreen o mi antivirus muestra una alerta al abrirlo?
R: Es un falso positivo muy comun en ejecutables empaquetados con PyInstaller
   que no cuentan con un certificado de firma digital de pago (cuestan cientos
   de dolares al ano). El proyecto es 100% de codigo abierto bajo licencia GPLv3
   y puedes auditar cada linea de codigo en GitHub. Haz clic en "Mas informacion"
   y luego "Ejecutar de todas formas".

P: ¿Que hago si YouTube cambia su sistema y los videos dejan de cargar?
R: Solo debes actualizar el motor yt-dlp.exe:
   1. Descarga el ejecutable mas reciente desde:
      https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
   2. Reemplaza el archivo "yt-dlp.exe" dentro de la subcarpeta "bin/".
   Listo! No necesitas volver a compilar nada.
