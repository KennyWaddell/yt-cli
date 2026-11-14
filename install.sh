#!/usr/bin/env bash
# ==============================================================================
# Installer for YT-CLI
# Compatible with: Debian, Ubuntu, antiX, Arch, Fedora, openSUSE, Alpine, etc.
# ==============================================================================

set -euo pipefail

C_GREEN="\033[1;32m"
C_CYAN="\033[1;36m"
C_YELLOW="\033[1;33m"
C_RED="\033[1;31m"
C_BOLD="\033[1m"
C_RESET="\033[0m"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${C_CYAN}====================================================${C_RESET}"
echo -e "${C_BOLD} Instalador de YT-CLI (Cliente Multimedia Ligero)${C_RESET}"
echo -e "${C_CYAN}====================================================${C_RESET}\n"

# 1. Comprobación de dependencias
echo -e "${C_YELLOW}[1/4] Verificando dependencias del sistema...${C_RESET}"
MISSING_DEPS=()
for dep in yt-dlp fzf mpv ffmpeg; do
    if ! command -v "$dep" >/dev/null 2>&1; then
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${C_RED}Advertencia: Faltan las siguientes dependencias: ${MISSING_DEPS[*]}${C_RESET}"
    echo -e "Puedes instalarlas con tu gestor de paquetes:"
    echo -e "  Debian/Ubuntu/antiX:  ${C_BOLD}sudo apt install ${MISSING_DEPS[*]}${C_RESET}"
    echo -e "  Arch Linux:           ${C_BOLD}sudo pacman -S ${MISSING_DEPS[*]}${C_RESET}"
    echo -e "  Fedora:               ${C_BOLD}sudo dnf install ${MISSING_DEPS[*]}${C_RESET}\n"
else
    echo -e "${C_GREEN}✔ Todas las dependencias (yt-dlp, fzf, mpv, ffmpeg) están instaladas.${C_RESET}\n"
fi

# 2. Instalación del ejecutable
echo -e "${C_YELLOW}[2/4] Instalando ejecutable en ~/.local/bin/yt-cli...${C_RESET}"
INSTALL_BIN_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_BIN_DIR"
cp "${PROJECT_DIR}/bin/yt-cli" "${INSTALL_BIN_DIR}/yt-cli"
chmod +x "${INSTALL_BIN_DIR}/yt-cli"
echo -e "${C_GREEN}✔ Ejecutable instalado correctamente.${C_RESET}\n"

# 3. Instalación de iconos y acceso directo
echo -e "${C_YELLOW}[3/4] Instalando iconos y accesos directos...${C_RESET}"
ICON_DIR="${HOME}/.local/share/icons/hicolor/48x48/apps"
mkdir -p "$ICON_DIR"
cp "${PROJECT_DIR}/assets/yt-cli.png" "${ICON_DIR}/yt-cli.png"

APP_DIR="${HOME}/.local/share/applications"
mkdir -p "$APP_DIR"
cp "${PROJECT_DIR}/yt-cli.desktop" "${APP_DIR}/yt-cli.desktop"
chmod +x "${APP_DIR}/yt-cli.desktop"

# Copiar al Escritorio si la carpeta existe
if [ -d "${HOME}/Desktop" ]; then
    cp "${PROJECT_DIR}/yt-cli.desktop" "${HOME}/Desktop/yt-cli.desktop"
    chmod +x "${HOME}/Desktop/yt-cli.desktop"
elif [ -d "${HOME}/Escritorio" ]; then
    cp "${PROJECT_DIR}/yt-cli.desktop" "${HOME}/Escritorio/yt-cli.desktop"
    chmod +x "${HOME}/Escritorio/yt-cli.desktop"
fi
echo -e "${C_GREEN}✔ Acceso directo e icono instalados.${C_RESET}\n"

# 4. Configuración optimizada de yt-dlp
echo -e "${C_YELLOW}[4/4] Verificando configuración de yt-dlp...${C_RESET}"
YTDLP_CONF_DIR="${HOME}/.config/yt-dlp"
YTDLP_CONF_FILE="${YTDLP_CONF_DIR}/config"
mkdir -p "$YTDLP_CONF_DIR"

if [ ! -f "$YTDLP_CONF_FILE" ]; then
    cat << 'EOF' > "$YTDLP_CONF_FILE"
# yt-dlp configuration for antiX / Low-resource Linux
# Use android_creator client to get all resolutions (360p, 480p, 720p, 1080p) in H.264
--extractor-args "youtube:player_client=android_creator;lang=es"
--no-warnings
EOF
    echo -e "${C_GREEN}✔ Archivo de configuración generado en ~/.config/yt-dlp/config.${C_RESET}\n"
else
    echo -e "${C_GREEN}✔ Ya existe configuración previa en ~/.config/yt-dlp/config (no modificada).${C_RESET}\n"
fi

# 5. Comprobación del PATH
if [[ ":$PATH:" != *":${INSTALL_BIN_DIR}:"* ]]; then
    echo -e "${C_YELLOW}Aviso: ${INSTALL_BIN_DIR} no está actualmente en tu variable \$PATH.${C_RESET}"
    echo -e "Añade esta línea a tu archivo ~/.bashrc o ~/.profile si aún no la tienes:"
    echo -e "  ${C_BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${C_RESET}\n"
fi

echo -e "${C_GREEN}====================================================${C_RESET}"
echo -e "${C_BOLD} ¡Instalación completada con éxito!${C_RESET}"
echo -e " Ya puedes ejecutar ${C_CYAN}yt-cli${C_RESET} en tu terminal o desde tu menú."
echo -e "${C_GREEN}====================================================${C_RESET}"
