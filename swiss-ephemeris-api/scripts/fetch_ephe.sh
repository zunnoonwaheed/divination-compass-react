#!/usr/bin/env sh
set -eu

# Minimal Swiss Ephemeris files to support planets, Moon, and Chiron on Railway.
# Source: Swiss Ephemeris public FTP mirror hosted by astro.com.
BASE_URL="https://www.astro.com/ftp/swisseph/ephe"
OUT_DIR="${1:-/app/ephe}"

mkdir -p "$OUT_DIR"

fetch() {
  file="$1"
  if [ -f "$OUT_DIR/$file" ]; then
    echo "✓ ephe already present: $file"
    return 0
  fi
  echo "↓ downloading ephe: $file"
  curl -fsSL "$BASE_URL/$file" -o "$OUT_DIR/$file"
}

# Planet ephemeris (major planets)
fetch "sepl_18.se1"
# Moon ephemeris (required for accurate Moon)
fetch "semo_18.se1"
# Asteroids ephemeris (required for Chiron)
fetch "seas_18.se1"

echo "✓ ephe ready in: $OUT_DIR"
