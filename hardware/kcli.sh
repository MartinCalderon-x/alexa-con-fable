#!/usr/bin/env bash
# kicad-cli con configuración aislada dentro de la producción (no toca la config global de KiCad).
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export KICAD_CONFIG_HOME="$here/.cache/kicad/config" KICAD_CACHE_HOME="$here/.cache/kicad/cache" XDG_CACHE_HOME="$here/.cache"
export LC_ALL=C LANG=C FONTCONFIG_FILE="$HOME/repos/physical-ai/config/fontconfig-macos.conf"
mkdir -p "$KICAD_CONFIG_HOME" "$KICAD_CACHE_HOME"
exec /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli "$@"
