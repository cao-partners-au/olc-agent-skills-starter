#!/usr/bin/env bash
# Run scripts/maintain.sh automatically: daily at 3:15am, and once when you log in.
# If the Mac is asleep at 3:15, macOS runs it when it wakes.
#   ./scripts/setup-maintenance-macos.sh            switch on
#   ./scripts/setup-maintenance-macos.sh --remove   switch off
set -euo pipefail

LABEL="local.agent-skills.maintain"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

if [ "${1:-}" = "--remove" ]; then
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"; echo "Automatic maintenance switched off."; exit 0
fi
[ "$(uname)" = "Darwin" ] || { echo "macOS only. On Linux, add a daily cron entry: 15 3 * * * $REPO/scripts/maintain.sh"; exit 1; }
chmod +x "$REPO/scripts/maintain.sh"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$REPO/scripts/maintain.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>15</integer></dict>
  <key>RunAtLoad</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>LowPriorityIO</key><true/>
  <key>Nice</key><integer>10</integer>
  <key>StandardOutPath</key><string>/dev/null</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/agent-skills-maintain.err.log</string>
</dict>
</plist>
EOF
plutil -lint "$PLIST" >/dev/null
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"
echo "Automatic maintenance is on: daily at 3:15am and at login."
echo "Log: ~/Library/Logs/agent-skills-maintain.log (a notification appears only if something needs you)."
