#!/bin/bash
# Tests add-agent-rules.sh against throwaway HOMEs, on macOS's own /bin/bash 3.2 (what the daily maintenance runs).
# Run before pushing a change to the installer: /bin/bash scripts/test-add-agent-rules.sh
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"; R="$(mktemp -d)"; trap 'rm -rf "$R"' EXIT
cp -R "$REPO/." "$R/repo"; rm -f "$R/repo/agent-rules/AGENT-RULES.local.md"
S="<!-- agent-skills-repo rules: start (managed by add-agent-rules.sh) -->"; E="<!-- agent-skills-repo rules: end -->"
fail() { echo "FAIL: $*"; exit 1; }
home() { H="$(mktemp -d "$R/h.XXXX")"; mkdir -p "$H/.claude"; F="$H/.claude/CLAUDE.md"; }
run() { set +e; HOME="$H" /bin/bash "$R/repo/scripts/add-agent-rules.sh" "$@" >/dev/null 2>&1; rc=$?; set -e; }
starts() { grep -c "rules: start" "$F" || true; }

home; printf 'a\n\t\nb\n' > "$F"; run; run; [ "$rc" = 0 ] && [ "$(starts)" = 1 ] || fail "re-run"
head -3 "$F" | od -c | grep -q '\\t' || fail "whitespace-only line changed"
n="$(ls "$H/.claude" | grep -c bak)"; run; [ "$(ls "$H/.claude" | grep -c bak)" = "$n" ] || fail "unchanged re-run made a backup"

home; printf 'top\n%s\nkeep1\n%s\nkeep2\n' "$E" "$S" > "$F"; run
[ "$rc" = 3 ] && grep -q keep2 "$F" || fail "out-of-order markers"

home; printf 'mine\r\n%s\r\nold\r\n%s\r\n' "$S" "$E" > "$F"; run
[ "$(starts)" = 1 ] && ! grep -q '^old' "$F" || fail "CRLF block not replaced"

printf -- '- local rule' > "$R/repo/agent-rules/AGENT-RULES.local.md"   # no final newline, on purpose
home; run; run; [ "$rc" = 0 ] || fail "local file without newline locked the file"
grep -qx -- '- local rule' "$F" || fail "local rules missing"
printf '\n%s\n%s\n' "$E" "$S" >> "$R/repo/agent-rules/AGENT-RULES.local.md"; run; [ "$rc" = 3 ] || fail "marker lines in local rules accepted"
chmod 000 "$R/repo/agent-rules/AGENT-RULES.local.md"; home; printf 'x\n' > "$F"; run
[ "$rc" = 3 ] && ! grep -q "rules: start" "$F" || fail "unreadable local rules not refused"
chmod 644 "$R/repo/agent-rules/AGENT-RULES.local.md"
rm "$R/repo/agent-rules/AGENT-RULES.local.md"

home; printf 'x\n' > "$F"; chmod 640 "$F"; run
[ "$(stat -f %Lp "$F" 2>/dev/null || stat -c %a "$F")" = 640 ] || fail "permissions not kept"
home; printf 'real\n' > "$H/real.md"; rm -f "$F"; ln -s "$H/real.md" "$F"; run
[ -L "$F" ] && grep -q "rules: start" "$H/real.md" || fail "symlink replaced instead of written through"
home; mkdir "$F.dir" && rm -f "$F" && mkdir "$F"; mkdir -p "$H/.codex"; run
[ "$rc" = 3 ] && grep -q "rules: start" "$H/.codex/AGENTS.md" || fail "a bad target stopped the others"

home; printf 'x\n' > "$F"; run; run --remove; [ "$rc" = 0 ] && [ "$(starts)" = 0 ] || fail "remove"
[ -z "$(ls "$H/.claude" | grep -v -e bak -e CLAUDE.md || true)" ] || fail "temp file left behind"
# An unreadable shared rules file must never write an empty block over the rules.
home; printf 'x\n' > "$F"; run; chmod 000 "$R/repo/agent-rules/AGENT-RULES.md"; run; chmod 644 "$R/repo/agent-rules/AGENT-RULES.md"
[ "$rc" = 3 ] && grep -q "Load the skill" "$F" || fail "unreadable rules file emptied the block"
# A skip leaves no temp file behind, for any target.
home; printf '%s\nx\n' "$E" > "$F"; mkdir -p "$H/.codex"; printf '%s\nx\n' "$E" > "$H/.codex/AGENTS.md"; run
[ "$rc" = 3 ] && [ -z "$(ls "$H/.claude" "$H/.codex" | grep -E '\.(md)\.[A-Za-z0-9]{6}$' || true)" ] || fail "temp file left after a skip"
# --if-present (daily maintenance) refreshes an existing block, never re-adds one that was removed.
home; printf 'x\n' > "$F"; run; run --remove; run --if-present; [ "$(starts)" = 0 ] || fail "--if-present re-added removed rules"
home; printf 'x\n' > "$F"; run; printf -- '- new\n' > "$R/repo/agent-rules/AGENT-RULES.local.md"; run --if-present
grep -qx -- '- new' "$F" || fail "--if-present didn't refresh"; rm "$R/repo/agent-rules/AGENT-RULES.local.md"
# The restart reminder prints when one file was written, even if another was skipped.
home; printf 'x\n' > "$F"; mkdir -p "$H/.codex"; printf '%s\nx\n' "$E" > "$H/.codex/AGENTS.md"
out="$(HOME="$H" /bin/bash "$R/repo/scripts/add-agent-rules.sh" 2>/dev/null || true)"; echo "$out" | grep -q Restart || fail "restart line missing"
# GNU stat (Linux): -f means "filesystem" there. Tested when coreutils' gstat is installed.
if command -v gstat >/dev/null; then
  mkdir -p "$R/gnu"; ln -sf "$(command -v gstat)" "$R/gnu/stat"
  home; printf 'x\n' > "$F"; chmod 640 "$F"; set +e; PATH="$R/gnu:$PATH" HOME="$H" /bin/bash "$R/repo/scripts/add-agent-rules.sh" >/dev/null 2>&1; rc=$?; set -e
  [ "$rc" = 0 ] && grep -q "rules: start" "$F" && [ "$(gstat -c %a "$F")" = 640 ] || fail "GNU stat"
fi
echo "PASS"
