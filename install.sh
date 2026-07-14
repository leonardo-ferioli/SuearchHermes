#!/usr/bin/env bash
set -euo pipefail

# SuearchHermes — Install script
# Installs the agy web search plugin into Hermes Agent

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
HERMES_SRC="${HERMES_SRC:-$HERMES_HOME/hermes-agent}"
PLUGIN_DEST="$HERMES_SRC/plugins/web/agy"
CONFIG_FILE="$HERMES_HOME/config.yaml"

echo "SuearchHermes — Google Search via Antigravity (agy) for Hermes"
echo "================================================================"
echo ""

# 1. Check Hermes is installed
if [ ! -d "$HERMES_SRC" ]; then
    echo "ERROR: Hermes agent not found at $HERMES_SRC"
    echo "Install Hermes first: https://github.com/NousResearch/hermes-agent"
    exit 1
fi

# 2. Install plugin files
echo "[1/3] Installing plugin to $PLUGIN_DEST ..."
mkdir -p "$PLUGIN_DEST"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/plugins/web/agy/__init__.py" "$PLUGIN_DEST/__init__.py"
cp "$SCRIPT_DIR/plugins/web/agy/provider.py" "$PLUGIN_DEST/provider.py"
echo "      Done."
echo ""

# 3. Check agy is installed
echo "[2/3] Checking Antigravity CLI (agy) ..."
if command -v agy &>/dev/null || [ -x "$HOME/.local/bin/agy" ]; then
    echo "      agy found."
else
    echo "      WARNING: agy not found."
    echo "      Install it: curl -fsSL https://antigravity.google/cli/install.sh | bash"
    echo "      Then run: agy  (to authenticate with your Google account)"
    echo ""
fi

# 4. Configure Hermes to use agy as search backend
echo "[3/3] Configuring Hermes config.yaml ..."
if [ -f "$CONFIG_FILE" ]; then
    if grep -q "search_backend:" "$CONFIG_FILE"; then
        if grep -q "search_backend: agy" "$CONFIG_FILE"; then
            echo "      Already configured."
        else
            echo "      WARNING: a different search_backend is already set in config.yaml"
            echo "      Manually add or change these lines in $CONFIG_FILE:"
            echo ""
            echo "        web:"
            echo "          search_backend: agy"
            echo ""
        fi
    else
        # Add web section at the top of the file
        TEMP=$(mktemp)
        printf "web:\n  search_backend: agy\n\n" > "$TEMP"
        cat "$CONFIG_FILE" >> "$TEMP"
        mv "$TEMP" "$CONFIG_FILE"
        echo "      Added web.search_backend: agy to config.yaml"
    fi
else
    echo "      WARNING: config.yaml not found at $CONFIG_FILE"
    echo "      Create it with:"
    echo ""
    echo "        web:"
    echo "          search_backend: agy"
    echo ""
fi

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Make sure agy is authenticated: run 'agy' once to log in"
echo "  2. Restart Hermes"
echo "  3. Ask Hermes to search something — it will use Google via agy"
echo ""
echo "To verify the plugin is loaded:"
echo "  cd $HERMES_SRC && ./venv/bin/python -c \"from plugins.web.agy.provider import AgYWebSearchProvider; p = AgYWebSearchProvider(); print(p.name, p.is_available())\""
