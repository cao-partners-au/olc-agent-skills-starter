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
START="<!-- agent-skills-repo rules: start (managed by add-agent-rules.sh) -->"
END="<!-- agent-skills-repo rules: end -->"

# "tool|folder showing it's installed|its global instructions file"
TARGETS=(
  "Claude Code|$HOME/.claude|$HOME/.claude/CLAUDE.md"
  "Codex|$HOME/.codex|$HOME/.codex/AGENTS.md"
  "Gemini CLI|$HOME/.gemini|$HOME/.gemini/GEMINI.md"
)

strip_block() { awk -v s="$START" -v e="$END" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$1"; }
# Trailing blank lines dropped (kept exactly as written anywhere else), so re-runs don't add one each time.
trim_end() { awk 'NF{for(i=1;i<=n;i++)print b[i];n=0;print;next}{b[++n]=$0}'; }
# A start marker without its end marker would make strip_block delete everything after it: refuse instead.
markers_ok() { [ ! -f "$1" ] || [ "$(grep -cxF "$START" "$1")" = "$(grep -cxF "$END" "$1")" ]; }

for entry in "${TARGETS[@]}"; do
  IFS="|" read -r name home file <<< "$entry"
  [ -d "$home" ] || continue
  if ! markers_ok "$file"; then echo "$name: $file has a start marker without its end marker (or the reverse); fix it by hand, skipped" >&2; continue; fi
  case "$MODE" in
    --dry-run)
      if [ -f "$file" ] && grep -qF "$START" "$file"; then echo "$name: would update the rules block in $file"
      else echo "$name: would add the rules block to $file"; fi ;;
    --remove)
      [ -f "$file" ] && grep -qF "$START" "$file" || continue
      cp "$file" "$file.bak.$(date +%Y%m%d%H%M%S).$$"
      strip_block "$file" > "$file.tmp" && mv "$file.tmp" "$file"
      echo "$name: removed the rules block from $file" ;;
    add)
      touch "$file"
      cp "$file" "$file.bak.$(date +%Y%m%d%H%M%S).$$"
      { strip_block "$file" | trim_end; printf '\n%s\n' "$START"; cat "$RULES"; printf '%s\n' "$END"; } > "$file.tmp"
      mv "$file.tmp" "$file"
      echo "$name: rules added to $file (backup saved next to it)" ;;
    *) echo "Usage: ./scripts/add-agent-rules.sh [--dry-run|--remove]"; exit 1 ;;
  esac
done
[ "$MODE" = "add" ] && echo "Restart your AI tools to load the rules."
exit 0
