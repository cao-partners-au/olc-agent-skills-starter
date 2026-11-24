#!/usr/bin/env bash
# Add (or update) the rules in agent-rules/AGENT-RULES.md to your AI tools' global
# instruction files, between marker lines, so running it again replaces the block
# instead of duplicating it. Your own instructions outside the markers are untouched.
#   ./scripts/add-agent-rules.sh            add or update
#   ./scripts/add-agent-rules.sh --dry-run  show which files would change
#   ./scripts/add-agent-rules.sh --remove   take the block out again
set -euo pipefail

MODE="${1:-add}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
RULES="$REPO/agent-rules/AGENT-RULES.md"
# Your own additions: kept in a separate file so starter updates to AGENT-RULES.md still reach you.
LOCAL_RULES="$REPO/agent-rules/AGENT-RULES.local.md"
START="<!-- agent-skills-repo rules: start (managed by add-agent-rules.sh) -->"
END="<!-- agent-skills-repo rules: end -->"

# "tool|folder showing it's installed|its global instructions file"
TARGETS=(
  "Claude Code|$HOME/.claude|$HOME/.claude/CLAUDE.md"
  "Codex|$HOME/.codex|$HOME/.codex/AGENTS.md"
  "Gemini CLI|$HOME/.gemini|$HOME/.gemini/GEMINI.md"
)

# Markers are matched as whole lines; a Windows line ending (\r) is ignored, so such files aren't given a second block.
strip_block() { awk -v s="$START" -v e="$END" '{l=$0; sub(/\r$/,"",l)} l==s{skip=1;next} l==e{skip=0;next} !skip' "$1"; }
has_block() { [ -f "$1" ] && awk -v s="$START" '{l=$0; sub(/\r$/,"",l)} l==s{f=1;exit} END{exit !f}' "$1"; }
# Trailing blank lines dropped (kept exactly as written anywhere else), so re-runs don't add one each time.
trim_end() { awk 'NF{for(i=1;i<=n;i++)print b[i];n=0;print;next}{b[++n]=$0}'; }
# Markers out of step (one deleted, or an end above its start) would make strip_block delete the text after them:
# refuse instead. So does a file that can't be read.
markers_ok() {
  [ ! -e "$1" ] && return 0
  [ -r "$1" ] || return 1
  awk -v s="$START" -v e="$END" '{l=$0; sub(/\r$/,"",l)} l==s{if(o){bad=1;exit};o=1} l==e{if(!o){bad=1;exit};o=0} END{exit bad||o}' "$1"
}
SKIPPED=0

for entry in "${TARGETS[@]}"; do
  IFS="|" read -r name home file <<< "$entry"
  [ -d "$home" ] || continue
  if ! markers_ok "$file"; then
    echo "$name: $file can't be read, or its rules markers are missing or out of order; fix it by hand, skipped" >&2
    SKIPPED=1; continue
  fi
  case "$MODE" in
    --dry-run)
      if has_block "$file"; then echo "$name: would update the rules block in $file"
      else echo "$name: would add the rules block to $file"; fi ;;
    --remove)
      has_block "$file" || continue
      cp "$file" "$file.bak.$(date +%Y%m%d%H%M%S).$$"
      tmp="$(mktemp "$file.XXXXXX")"
      strip_block "$file" | trim_end > "$tmp" && mv "$tmp" "$file"
      echo "$name: removed the rules block from $file" ;;
    add)
      touch "$file"
      cp "$file" "$file.bak.$(date +%Y%m%d%H%M%S).$$"
      tmp="$(mktemp "$file.XXXXXX")" # its own temp file, so two runs at once can't overwrite each other's
      { strip_block "$file" | trim_end; printf '\n%s\n' "$START"; cat "$RULES"
        if [ -f "$LOCAL_RULES" ]; then printf '\n'; cat "$LOCAL_RULES"; fi
        printf '%s\n' "$END"; } > "$tmp"
      mv "$tmp" "$file"
      echo "$name: rules added to $file (backup saved next to it)" ;;
    *) echo "Usage: ./scripts/add-agent-rules.sh [--dry-run|--remove]"; exit 1 ;;
  esac
done
# Exit 3 when a file was skipped, so the daily maintenance tells you instead of failing quietly.
[ "$SKIPPED" = 1 ] && exit 3
[ "$MODE" = "add" ] && echo "Restart your AI tools to load the rules."
exit 0
