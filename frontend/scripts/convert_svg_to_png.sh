#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SVG_DIR="$ROOT_DIR/frontend/src/assets"
PNG_OUT_DIR="$SVG_DIR/pngs"

mkdir -p "$PNG_OUT_DIR"

shopt -s nullglob
for svg in "$SVG_DIR"/tiles/*.svg "$SVG_DIR"/sprites/*.svg "$SVG_DIR"/ui/*.svg "$SVG_DIR"/portraits/*.svg "$SVG_DIR"/environment/*.svg; do
  base="$(basename "$svg" .svg)"
  out="$PNG_OUT_DIR/$(echo "$base" | tr '[:upper:]' '[:lower:]').png"
  echo "Converting $svg -> $out"
  if command -v inkscape >/dev/null 2>&1; then
    inkscape "$svg" --export-type=png --export-filename="$out" --export-width=32 --export-height=32 >/dev/null 2>&1 || true
  elif command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert "$svg" -w 32 -h 32 > "$out" 2>/dev/null
  else
    echo "Warning: No SVG to PNG converter found (inkscape or rsvg-convert). Skipping $svg" >&2
  fi
done

echo "PNG conversion complete. PNGs in $PNG_OUT_DIR"
