#!/usr/bin/env bash
# Builds dist/SoilClassPro.app on macOS. Run from Terminal: ./build_mac.sh
set -euo pipefail
cd "$(dirname "$0")"

if [ -x .venv/bin/python ]; then
    PY=.venv/bin/python
else
    PY=python3
fi

echo "Using: $PY ($("$PY" --version))"

echo "Installing/updating PyInstaller and project requirements..."
"$PY" -m pip install --upgrade pip pyinstaller
"$PY" -m pip install --upgrade -r requirements.txt

# Build the macOS icon from the PNG logo (sips and iconutil ship with macOS).
ICONSET=build/SoilClassPro.iconset
rm -rf "$ICONSET"
mkdir -p "$ICONSET"
for size in 16 32 128 256 512; do
    sips -z "$size" "$size" soilclass/assets/logo.png \
        --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    sips -z $((size * 2)) $((size * 2)) soilclass/assets/logo.png \
        --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o build/SoilClassPro.icns

echo "Building SoilClassPro.app..."
"$PY" -m PyInstaller --noconfirm --clean SoilClassPro.spec

echo "Done! Your app bundle is at: dist/SoilClassPro.app"
