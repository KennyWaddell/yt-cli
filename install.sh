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
echo -e "${C_YELLOW}[1/5] Verificando dependencias del sistema...${C_RESET}"
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
echo -e "${C_YELLOW}[2/5] Instalando ejecutable en ~/.local/bin/yt-cli...${C_RESET}"
INSTALL_BIN_DIR="${HOME}/.local/bin"
mkdir -p "$INSTALL_BIN_DIR"
cp "${PROJECT_DIR}/bin/yt-cli" "${INSTALL_BIN_DIR}/yt-cli"
chmod +x "${INSTALL_BIN_DIR}/yt-cli"
echo -e "${C_GREEN}✔ Ejecutable instalado correctamente.${C_RESET}\n"

# 3. Instalación de paquetes de idioma (i18n)
echo -e "${C_YELLOW}[3/5] Instalando paquetes de idiomas en ~/.local/share/yt-cli/lang...${C_RESET}"
LANG_INSTALL_DIR="${HOME}/.local/share/yt-cli/lang"
mkdir -p "$LANG_INSTALL_DIR"
cp "${PROJECT_DIR}/lang/"*.sh "$LANG_INSTALL_DIR/"
echo -e "${C_GREEN}✔ Idiomas instalados (Español / English).${C_RESET}\n"

# 4. Instalación de iconos y acceso directo
echo -e "${C_YELLOW}[4/5] Instalando iconos y menús del sistema...${C_RESET}"
ICON_DIR="${HOME}/.local/share/icons/hicolor/48x48/apps"
mkdir -p "$ICON_DIR"
cp "${PROJECT_DIR}/assets/yt-cli.png" "${ICON_DIR}/yt-cli.png"

APP_DIR="${HOME}/.local/share/applications"
mkdir -p "$APP_DIR"
cp "${PROJECT_DIR}/yt-cli.desktop" "${APP_DIR}/yt-cli.desktop"
chmod +x "${APP_DIR}/yt-cli.desktop"
echo -e "${C_GREEN}✔ Acceso en menú de aplicaciones (${APP_DIR}/yt-cli.desktop).${C_RESET}"

# Preguntar respetuosamente antes de crear icono en ~/Desktop o ~/Escritorio
CREATE_DESKTOP="n"
if [[ " $* " == *" --desktop "* ]]; then
    CREATE_DESKTOP="s"
elif [ -t 0 ]; then
    echo -ne "${C_YELLOW}¿Deseas crear también un acceso directo en tu Escritorio? [s/N]: ${C_RESET}"
    read -r ans || ans="n"
    [[ "$ans" =~ ^[sSyY]$ ]] && CREATE_DESKTOP="s"
fi

if [ "$CREATE_DESKTOP" = "s" ]; then
    DESKTOP_PATH=""
    if [ -d "${HOME}/Desktop" ]; then
        DESKTOP_PATH="${HOME}/Desktop"
    elif [ -d "${HOME}/Escritorio" ]; then
        DESKTOP_PATH="${HOME}/Escritorio"
    fi
    if [ -n "$DESKTOP_PATH" ]; then
        cp "${PROJECT_DIR}/yt-cli.desktop" "${DESKTOP_PATH}/yt-cli.desktop"
        chmod +x "${DESKTOP_PATH}/yt-cli.desktop"
        echo -e "${C_GREEN}✔ Acceso directo creado en ${DESKTOP_PATH}/yt-cli.desktop.${C_RESET}\n"
    fi
else
    echo -e "${C_GRAY}ℹ Escritorio no modificado (manteniendo tu entorno limpio).${C_RESET}\n"
fi

# 5. Configuración aislada de YT-CLI (Sin contaminar dotfiles globales)
echo -e "${C_YELLOW}[5/5] Verificando entorno aislado en ~/.config/yt-cli...${C_RESET}"
YT_CLI_CONF_DIR="${HOME}/.config/yt-cli"
mkdir -p "$YT_CLI_CONF_DIR"
echo -e "${C_GREEN}✔ Directorio de configuración aislado listo (tus dotfiles de ~/.config/yt-dlp no han sido tocados).${C_RESET}\n"

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
