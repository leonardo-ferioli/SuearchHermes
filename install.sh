#!/usr/bin/env bash
set -euo pipefail

# SuearchHermes — Install script
# Installs the agy web search plugin into Hermes Agent
#
# Works on Linux, macOS and Windows (Git Bash / MSYS2). On Windows the agy
# binary is fetched as agy.exe from Google's release manifest, because
# antigravity.google/cli/install.sh is a Unix-only bootstrapper.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

is_windows() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) return 0 ;;
        *) return 1 ;;
    esac
}

# Hermes home: explicit override > platform default (Windows uses LOCALAPPDATA)
default_hermes_home() {
    if is_windows; then
        echo "${LOCALAPPDATA:-$HOME/AppData/Local}/hermes"
    else
        echo "$HOME/.hermes"
    fi
}

HERMES_HOME="${HERMES_HOME:-$(default_hermes_home)}"
HERMES_SRC="${HERMES_SRC:-$HERMES_HOME/hermes-agent}"
PLUGIN_DEST="$HERMES_SRC/plugins/web/agy"
CONFIG_FILE="$HERMES_HOME/config.yaml"
AGY_URL_BASE="https://antigravity-cli-auto-updater-974169037036.us-central1.run.app"

# Run a command with a time limit where coreutils' timeout exists
# (macOS ships it only with coreutils installed).
run_t() {
    local secs="$1"; shift
    if command -v timeout >/dev/null 2>&1; then
        timeout "$secs" "$@"
    else
        "$@"
    fi
}

echo "SuearchHermes — Google Search via Antigravity (agy) for Hermes"
echo "=================================================================="
echo ""

# 1. Check Hermes is installed
if [ ! -d "$HERMES_SRC" ]; then
    echo "ERROR: Hermes agent not found at $HERMES_SRC"
    echo "Set HERMES_HOME if your Hermes directory lives elsewhere, e.g."
    is_windows && echo "    HERMES_HOME=\"\$LOCALAPPDATA/hermes\" ./install.sh"
    is_windows || echo "    HERMES_HOME=\"\$HOME/.hermes\" ./install.sh"
    exit 1
fi

# 2. Install plugin files — every file in the plugin dir, not a hardcoded list.
#    A missing module (e.g. oauth_provider.py) breaks plugin discovery, and
#    plugin.yaml is what makes Hermes list the plugin at all.
echo "[1/4] Installing plugin to $PLUGIN_DEST ..."
mkdir -p "$PLUGIN_DEST"
for f in "$SCRIPT_DIR/plugins/web/agy/"*.py "$SCRIPT_DIR/plugins/web/agy/plugin.yaml"; do
    [ -e "$f" ] || continue
    cp "$f" "$PLUGIN_DEST/$(basename "$f")"
done
echo "      Done."
echo ""

# 3. Make sure the agy binary exists
echo "[2/4] Checking Antigravity CLI (agy) ..."
AGY_BIN="$HOME/.local/bin/agy"
if command -v agy >/dev/null 2>&1 || [ -f "$AGY_BIN" ] || [ -f "$AGY_BIN.exe" ]; then
    echo "      agy found."
elif is_windows; then
    echo "      agy not found — downloading it from Google's release manifest ..."
    mkdir -p "$HOME/.local/bin"
    manifest="$(curl -fsSL "$AGY_URL_BASE/manifests/windows_amd64.json")" || {
        echo "ERROR: could not reach the Antigravity release server."; exit 1; }
    url="$(echo "$manifest" | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
    sha="$(echo "$manifest" | sed -n 's/.*"sha512"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
    if [ -z "$url" ] || [ -z "$sha" ]; then
        echo "ERROR: malformed release manifest."; exit 1
    fi
    curl -fsSL -o "$AGY_BIN.exe" "$url"
    actual="$(sha512sum "$AGY_BIN.exe" | cut -d' ' -f1)"
    if [ "$actual" != "$sha" ]; then
        echo "ERROR: checksum mismatch (expected $sha, got $actual)"
        rm -f "$AGY_BIN.exe"; exit 1
    fi
    # provider.py looks for ~/.local/bin/agy first; CreateProcess appends .exe
    cp "$AGY_BIN.exe" "$AGY_BIN"
    echo "      Installed to $AGY_BIN.exe (checksum verified)."
    case ":$PATH:" in
        *":$HOME/.local/bin:"*) ;;
        *) echo "      NOTE: add $HOME/.local/bin to PATH so 'agy' resolves in new shells." ;;
    esac
else
    echo "      WARNING: agy not found — install it, then re-run this script:"
    echo "      curl -fsSL https://antigravity.google/cli/install.sh | bash"
    echo ""
fi
echo ""

# 4. Point Hermes at the backend. Prefer the CLI (it validates and keeps the
#    file consistent); fall back to a targeted edit that does not clobber an
#    existing backend and does not create a second top-level 'web:' key.
echo "[3/4] Configuring Hermes ($CONFIG_FILE) ..."

set_via_cli() {
    command -v hermes >/dev/null 2>&1 || return 1
    run_t 30 hermes config set web.search_backend agy >/dev/null 2>&1
}

if [ -f "$CONFIG_FILE" ] && grep -qE '^[[:space:]]+search_backend:[[:space:]]*"?agy"?[[:space:]]*$' "$CONFIG_FILE"; then
    echo "      Already configured."
elif set_via_cli; then
    echo "      Set web.search_backend: agy via 'hermes config'."
elif [ -f "$CONFIG_FILE" ]; then
    if grep -qE '^[[:space:]]+search_backend:' "$CONFIG_FILE"; then
        echo "      Another backend is already set. Change it by hand:"
        echo "        web:"
        echo "          search_backend: agy"
    elif grep -qE '^web:[[:space:]]*$' "$CONFIG_FILE"; then
        awk '/^web:[[:space:]]*$/ && !done {print; print "  search_backend: agy"; done=1; next}
             {print}' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        echo "      Added web.search_backend: agy to the existing 'web:' block."
    else
        printf 'web:\n  search_backend: agy\n\n' | cat - "$CONFIG_FILE" > "$CONFIG_FILE.tmp" \
            && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        echo "      Added web.search_backend: agy."
    fi
else
    echo "      WARNING: config.yaml not found at $CONFIG_FILE"
    echo "      Add this to it yourself:"
    echo "        web:"
    echo "          search_backend: agy"
fi
echo ""

# 5. Verify discovery (capture first: grep -q + pipefail trips over the SIGPIPE)
echo "[4/4] Verifying ..."
if command -v hermes >/dev/null 2>&1; then
    plugins_list="$(run_t 60 hermes plugins list 2>/dev/null || true)"
    case "$plugins_list" in
        *web-agy*) echo "      web-agy is registered." ;;
        *) echo "      WARNING: web-agy not listed — restart Hermes and run 'hermes plugins list'." ;;
    esac
else
    echo "      Skipped (hermes CLI not on PATH). Check with: hermes plugins list"
fi

echo ""
echo "Installation complete. Restart Hermes so it loads the plugin."
echo ""
echo "Next steps:"
echo "  1. Authenticate agy once (browser login): agy"
echo "  2. Restart Hermes"
echo "  3. Ask Hermes to search something — it will use Google via Gemini"
