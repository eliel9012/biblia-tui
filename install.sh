#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SHARE_ROOT=${XDG_DATA_HOME:-"$HOME/.local/share"}
INSTALL_ROOT="$SHARE_ROOT/biblia-tui"
APP_DIR="$INSTALL_ROOT/app"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$APP_DIR" "$BIN_DIR"
cp -R "$PROJECT_DIR/biblia_tui" "$APP_DIR/"
cp "$PROJECT_DIR/biblia.py" "$APP_DIR/biblia.py"

if [ -f "$PROJECT_DIR/data/acf.json" ]; then
    cp "$PROJECT_DIR/data/acf.json" "$INSTALL_ROOT/acf.json"
elif [ -f "$HOME/acf.json" ]; then
    cp "$HOME/acf.json" "$INSTALL_ROOT/acf.json"
else
    python3 "$PROJECT_DIR/scripts/download_data.py" "$INSTALL_ROOT/acf.json"
fi

sed "s|__APP_DIR__|$APP_DIR|g" "$PROJECT_DIR/scripts/biblia-launcher" > "$BIN_DIR/biblia"
chmod 755 "$BIN_DIR/biblia"

echo "Instalado: $BIN_DIR/biblia"
echo "Execute: biblia"
