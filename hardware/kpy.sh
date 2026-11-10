#!/usr/bin/env bash
# Python incluido en KiCad (trae pcbnew), con configuración aislada.
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export KICAD_CONFIG_HOME="$here/.cache/kicad/config" KICAD_CACHE_HOME="$here/.cache/kicad/cache" LC_ALL=C LANG=C
exec /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 "$@"
