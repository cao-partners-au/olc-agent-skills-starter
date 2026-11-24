#!/usr/bin/env bash
# Add (or update) the rules in agent-rules/AGENT-RULES.md to your AI tools' global
# instruction files, between marker lines, so running it again replaces the block
# instead of duplicating it. Your own instructions outside the markers are untouched.
#   ./scripts/add-agent-rules.sh            add or update
#   ./scripts/add-agent-rules.sh --dry-run  show which files would change
#   ./scripts/add-agent-rules.sh --remove   take the block out again
#   ./scripts/add-agent-rules.sh --if-present  update only files that already have the block (daily maintenance)
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
# refuse instead. So does a file that can't be read. A missing file is fine (it gets created).
markers_ok() {
  [ ! -e "$1" ] && return 0
  [ -r "$1" ] || return 1
  awk -v s="$START" -v e="$END" '{l=$0; sub(/\r$/,"",l)} l==s{if(o){bad=1;exit};o=1} l==e{if(!o){bad=1;exit};o=0} END{exit bad||o}' "$1"
}
SKIPPED=0; WROTE=0
tmp=""; trap 'rm -f "${tmp:-}"' EXIT   # a failed write never leaves a temp file behind
skip() { echo "$1" >&2; SKIPPED=1; rm -f "${tmp:-}"; tmp=""; }
# A marker line inside the local rules would end the block early and lock the file on the next run.
local_ok() { [ ! -e "$LOCAL_RULES" ] || { [ -r "$LOCAL_RULES" ] && ! awk -v s="$START" -v e="$END" '{l=$0; sub(/\r$/,"",l)} l==s||l==e{f=1} END{exit !f}' "$LOCAL_RULES"; }; }
# Put $tmp in place of $1: nothing written (and no backup) when the content is unchanged; a backup first
# otherwise; the file's permissions kept; a symlinked file written through, so the file it points to updates.
# Called inside an if, where set -e is off, so each step returns on failure itself.
put() {
  if [ -f "$1" ] && cmp -s "$tmp" "$1"; then rm -f "$tmp"; return 0; fi
  if [ -f "$1" ]; then
    # GNU stat first: on Linux `stat -f` means "filesystem" and prints a report instead of failing.
    mode="$(stat -c %a "$1" 2>/dev/null || stat -f %Lp "$1")" || return 1
    chmod "$mode" "$tmp" || return 1
    cp -p "$1" "$1.bak.$(date +%Y%m%d%H%M%S).$$" || return 1
  else chmod 644 "$tmp" || return 1; fi
  if [ -L "$1" ]; then cat "$tmp" > "$1" || return 1; rm -f "$tmp"; else mv "$tmp" "$1" || return 1; fi
  WROTE=1
}

IF_PRESENT=0; [ "$MODE" = --if-present ] && { MODE=add; IF_PRESENT=1; }
if [ "$MODE" = add ] && ! [ -r "$RULES" ]; then echo "$RULES is missing or can't be read; nothing was changed" >&2; exit 3; fi
if [ "$MODE" = add ] && ! local_ok; then
  echo "$LOCAL_RULES can't be read or contains a rules marker line; fix it, nothing was changed" >&2; exit 3
fi

for entry in "${TARGETS[@]}"; do
  IFS="|" read -r name home file <<< "$entry"
  [ -d "$home" ] || continue
  if { [ -e "$file" ] || [ -L "$file" ]; } && [ ! -f "$file" ]; then skip "$name: $file isn't a regular file (a folder or a broken link); skipped"; continue; fi
  if ! markers_ok "$file"; then
    skip "$name: $file can't be read, or its rules markers are missing or out of order; fix it by hand, skipped"; continue
  fi
  case "$MODE" in
    --dry-run)
      if has_block "$file"; then echo "$name: would update the rules block in $file"
      else echo "$name: would add the rules block to $file"; fi ;;
    --remove)
      has_block "$file" || continue
      tmp="$(mktemp "$file.XXXXXX")" || { skip "$name: can't write next to $file; skipped"; continue; }
      if strip_block "$file" | trim_end > "$tmp" && put "$file"; then echo "$name: removed the rules block from $file"
      else skip "$name: couldn't write $file; it is unchanged"; fi ;;
    add)
      # --if-present (the daily maintenance): only refresh a block you already have, so --remove sticks.
      [ "$IF_PRESENT" = 1 ] && ! has_block "$file" && continue
      existed=0; [ -f "$file" ] && existed=1
      tmp="$(mktemp "$file.XXXXXX")" || { skip "$name: can't write next to $file; skipped"; continue; } # its own temp file, so two runs at once can't clash
      # awk 1: each file ends in a newline, so a rules file without one can't glue itself to the end marker.
      # Chained with &&: inside an if, set -e is off and a group only reports its last command, so a failed
      # read (an unreadable rules file) would otherwise write an empty block over your rules.
      if ! { { [ ! -f "$file" ] || { strip_block "$file" | trim_end; }; } && printf '\n%s\n' "$START" && awk 1 "$RULES" &&
             { [ ! -f "$LOCAL_RULES" ] || { printf '\n' && awk 1 "$LOCAL_RULES"; }; } && printf '%s\n' "$END"; } > "$tmp"; then skip "$name: couldn't write next to $file; it is unchanged"; continue; fi
      markers_ok "$tmp" || { skip "$name: the new block came out malformed; $file is unchanged"; continue; }
      w=$WROTE; WROTE=0
      if put "$file"; then
        if [ "$WROTE" = 1 ]; then echo "$name: rules added to $file$([ "$existed" = 1 ] && echo " (backup saved next to it)")"; else echo "$name: rules already up to date in $file"; fi
      else skip "$name: couldn't write $file; it is unchanged"; fi
      [ "$w" = 1 ] && WROTE=1 ;;
    *) echo "Usage: ./scripts/add-agent-rules.sh [--dry-run|--remove|--if-present]"; exit 1 ;;
  esac
done
# Exit 3 when a file was skipped, so the daily maintenance tells you instead of failing quietly.
[ "$MODE" = "add" ] && [ "$WROTE" = 1 ] && echo "Restart your AI tools to load the rules."
[ "$SKIPPED" = 1 ] && exit 3
exit 0
