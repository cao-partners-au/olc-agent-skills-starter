#!/usr/bin/env bash
# Start Ollama at login (macOS), listening only on this computer, with models unloaded
# straight after each request (OLLAMA_KEEP_ALIVE=0) so nothing stays in memory.
#   ./scripts/setup-ollama-macos.sh            set up and start
#   ./scripts/setup-ollama-macos.sh --remove   stop it starting at login
set -euo pipefail

LABEL="local.ollama"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

if [ "${1:-}" = "--remove" ]; then
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Removed. Ollama will no longer start at login."
  exit 0
fi

[ "$(uname)" = "Darwin" ] || { echo "This script is for macOS. See integrations/gbrain/README.md for Linux."; exit 1; }
OLLAMA="$(command -v ollama || true)"
[ -n "$OLLAMA" ] || { echo "Ollama isn't installed. Run: brew install ollama"; exit 1; }

if command -v brew >/dev/null 2>&1 && brew services list 2>/dev/null | grep -qE '^ollama +started'; then
  echo "Stopping Homebrew's own Ollama service so only this one runs."
  brew services stop ollama >/dev/null
fi

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$OLLAMA</string><string>serve</string></array>
  <key>EnvironmentVariables</key><dict>
    <key>OLLAMA_KEEP_ALIVE</key><string>0</string>
    <key>OLLAMA_HOST</key><string>127.0.0.1:11434</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>/tmp/ollama.log</string>
  <key>StandardErrorPath</key><string>/tmp/ollama.log</string>
</dict>
</plist>
EOF
plutil -lint "$PLIST" >/dev/null
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"

for _ in 1 2 3 4 5 6 7 8 9 10; do
  curl -fsS 127.0.0.1:11434/api/version >/dev/null 2>&1 && break
  sleep 1
done
if curl -fsS 127.0.0.1:11434/api/version >/dev/null 2>&1; then
  echo "Ollama is running and will start at login (models unload after each use)."
else
  echo "Ollama didn't respond yet. Check /tmp/ollama.log"
  exit 1
fi
