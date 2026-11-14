#!/usr/bin/env bash
# ==============================================================================
# Uninstaller for YT-CLI
# ==============================================================================

set -euo pipefail

C_GREEN="\033[1;32m"
C_YELLOW="\033[1;33m"
C_BOLD="\033[1m"
C_RESET="\033[0m"

echo -e "${C_YELLOW}Desinstalando YT-CLI...${C_RESET}"

rm -f "${HOME}/.local/bin/yt-cli"
rm -f "${HOME}/.local/share/applications/yt-cli.desktop"
rm -f "${HOME}/.local/share/icons/hicolor/48x48/apps/yt-cli.png"
rm -f "${HOME}/Desktop/yt-cli.desktop" 2>/dev/null || true
rm -f "${HOME}/Escritorio/yt-cli.desktop" 2>/dev/null || true

echo -e "${C_GREEN}✔ YT-CLI ha sido desinstalado por completo de tu sistema.${C_RESET}"
