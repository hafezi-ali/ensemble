#!/usr/bin/env bash
# Build manuscript/document.tex -> build_pdf/document.pdf using the project-local
# tectonic toolchain in tools/tectonic. Requires no system TeX installation.
#   usage: tools/build_pdf.sh [document.tex]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TECTONIC="$ROOT/tools/tectonic/bin/tectonic"
[ -x "$TECTONIC" ] || { echo "error: $TECTONIC missing" >&2; exit 1; }
# Point tectonic at the vendored TeX resource bundle so builds work offline.
export XDG_CACHE_HOME="$ROOT/tools/tectonic/texcache_home"
mkdir -p "$XDG_CACHE_HOME"
[ -e "$XDG_CACHE_HOME/Tectonic" ] || ln -s "$ROOT/tools/tectonic/texcache" "$XDG_CACHE_HOME/Tectonic"
mkdir -p "$ROOT/build_pdf"
cd "$ROOT/manuscript"
exec "$TECTONIC" -X compile "${1:-document.tex}" \
  --outdir "$ROOT/build_pdf" --keep-intermediates --keep-logs
