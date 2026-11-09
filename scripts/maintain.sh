#!/usr/bin/env bash
# Keeps the setup up to date and locked to the agreed configuration. Runs daily on its own
# (see scripts/setup-maintenance-macos.sh). Safe to run by hand any time.
#
#   ./scripts/maintain.sh            update, enforce, verify
#   ./scripts/maintain.sh --dry-run  report what it would change, change nothing
#
# What it does:
#   1. Starter updates: refreshes files that came from the starter repo, only where you
#      haven't edited them (your edits are never overwritten; you're told instead).
#   2. gstack: upgrades with gstack's own unattended, fast-forward-only upgrader.
#   3. gbrain: upgrades, upgrades Bun if gbrain needs it, finishes the upgrade, rebuilds
#      the search index.
#   4. Enforces gbrain's fully local configuration (local embeddings, no cloud models,
#      no stored AI keys) and puts it back if anything changed.
#   5. Checks Ollama is running and a real gbrain search works.
# A macOS notification appears only when something needs you. Full log:
#   ~/Library/Logs/agent-skills-maintain.log
set -uo pipefail

DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
REPO="$(cd "$(dirname "$0")/.." && pwd)"
STATE="$HOME/.agent-skills"; mkdir -p "$STATE"
LOG="$HOME/Library/Logs/agent-skills-maintain.log"; mkdir -p "$(dirname "$LOG")"
UPSTREAM_URL="${AGENT_SKILLS_UPSTREAM:-https://github.com/cao-partners-au/olc-agent-skills-starter.git}"
EMBED_MODEL="ollama:nomic-embed-text"
export PATH="$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

PROBLEMS=()
# portable time limit (macOS has no `timeout`): t <seconds> <command...>
t() { local s="$1"; shift; perl -e 'alarm shift; exec @ARGV' "$s" "$@"; }
log()  { printf '%s %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }
warn() { log "NEEDS ATTENTION: $*"; PROBLEMS+=("$*"); }
do_()  { if [ "$DRY" = 1 ]; then log "  would run: $*"; return 0; fi; "$@" >>"$LOG" 2>&1; }

log "---- maintenance run (dry=$DRY) ----"

# 1. Starter updates ------------------------------------------------------------------
# .starter-managed lists "<sha> <path>" for every file as last shipped by the starter.
starter_update() {
  local manifest="$REPO/.starter-managed" tmp
  [ -f "$manifest" ] || { log "starter: no .starter-managed manifest, skipping"; return; }
  tmp="$(mktemp -d)"
  if ! git clone -q --depth 1 "$UPSTREAM_URL" "$tmp/up" 2>>"$LOG"; then
    log "starter: couldn't reach $UPSTREAM_URL, will try next run"; rm -rf "$tmp"; return
  fi
  local changed=0 skipped=() path oldsha cursha newsha
  # files the starter ships now
  while read -r newsha path; do
    [ -n "$path" ] || continue
    oldsha="$(awk -v p="$path" '$2==p{print $1}' "$manifest")"
    cursha="$( [ -f "$REPO/$path" ] && git hash-object "$REPO/$path" || echo none)"
    [ "$newsha" = "$oldsha" ] && continue                       # starter didn't change it
    if [ "$cursha" = "$oldsha" ] || { [ "$cursha" = "none" ] && [ -z "$oldsha" ]; }; then
      log "starter: updating $path"
      if [ "$DRY" = 0 ]; then mkdir -p "$(dirname "$REPO/$path")"; cp "$tmp/up/$path" "$REPO/$path"; fi
      changed=1
    elif [ "$cursha" != "$newsha" ]; then
      skipped+=("$path")
    fi
  done < <(cd "$tmp/up" && git ls-files -s | awk '$4!=".starter-managed"{print $2, $4}')
  if [ "$DRY" = 0 ]; then
    cp "$tmp/up/.starter-managed" "$manifest" 2>/dev/null || true
    [ -x "$REPO/install.sh" ] && chmod +x "$REPO"/install.sh "$REPO"/scripts/*.sh "$REPO"/.githooks/* 2>/dev/null
    if [ "$changed" = 1 ] && [ -d "$REPO/.git" ]; then
      git -C "$REPO" add -A >>"$LOG" 2>&1 && git -C "$REPO" commit -qm "Update from starter repo" >>"$LOG" 2>&1 || true
      "$REPO/install.sh" >>"$LOG" 2>&1 || true
      "$REPO/scripts/add-agent-rules.sh" >>"$LOG" 2>&1 || true
    fi
  fi
  [ "${#skipped[@]}" -gt 0 ] && warn "starter has updates to files you've edited, left as yours: ${skipped[*]}"
  rm -rf "$tmp"
}
starter_update

# 2. gstack ---------------------------------------------------------------------------
GSTACK="$HOME/.claude/skills/gstack"
if [ -x "$GSTACK/bin/gstack-upgrade" ]; then
  if "$GSTACK/bin/gstack-upgrade" --check >>"$LOG" 2>&1; then
    log "gstack: up to date"
  else
    log "gstack: update available"
    do_ "$GSTACK/bin/gstack-upgrade" || warn "gstack couldn't upgrade itself (it refuses if you've edited its files). See the log."
  fi
else
  log "gstack: not installed, skipping"
fi

# 3. gbrain ---------------------------------------------------------------------------
if ! command -v gbrain >/dev/null 2>&1; then
  log "gbrain: not installed, skipping gbrain steps"; GBRAIN=0
else
  GBRAIN=1
  if t 60 gbrain check-update --json 2>/dev/null | grep -q '"update_available": *true'; then
    log "gbrain: update available"
    if [ "$DRY" = 0 ]; then
      cp -Rp "$HOME/.gbrain" "$STATE/gbrain-backup-before-upgrade" 2>/dev/null || true
      out="$(gbrain upgrade 2>&1)"; printf '%s\n' "$out" >>"$LOG"
      if printf '%s' "$out" | grep -q "requires Bun"; then
        log "gbrain: upgrading Bun"; bun upgrade >>"$LOG" 2>&1 || warn "Bun couldn't upgrade, gbrain may not start. See the log."
      fi
      gbrain post-upgrade >>"$LOG" 2>&1 || true
      gbrain projections drain >>"$LOG" 2>&1 || true
    else
      log "  would run: gbrain upgrade, then post-upgrade and projections drain"
    fi
  else
    log "gbrain: up to date"
  fi
fi

# 4. Enforce fully local gbrain -------------------------------------------------------
enforce_local() {
  local cfg="$HOME/.gbrain/config.json" show
  [ -f "$cfg" ] || { warn "gbrain has no config at ~/.gbrain/config.json"; return; }
  # values (not keys) the agreed setup must have
  do_ gbrain config set search.expansion false
  do_ gbrain config set search.reranker.enabled false
  # model pins live in config.json and need --file to unset; keys unset plainly
  for k in chat_model expansion_model; do
    if grep -q "\"$k\"" "$cfg"; then log "gbrain: removing $k"; do_ gbrain config unset "$k" --file; fi
  done
  for k in openai_api_key anthropic_api_key voyage_api_key openrouter_api_key gemini_api_key; do
    if grep -q "\"$k\"" "$cfg"; then log "gbrain: removing $k"; do_ gbrain config unset "$k"; fi
  done
  [ "$DRY" = 1 ] && return
  # verify
  grep -q "\"embedding_model\": *\"$EMBED_MODEL\"" "$cfg" || warn "gbrain embeddings are not $EMBED_MODEL. Fix: see integrations/gbrain/README.md"
  if grep -qiE '"(openai|anthropic|voyage|openrouter|gemini)[a-z_]*_key"' "$cfg"; then warn "an AI key is still stored in gbrain's config"; fi
  show="$(t 60 gbrain config show 2>&1)"
  if printf '%s' "$show" | grep -qiE 'locked|lock is held|single-writer'; then
    echo "$(( $(cat "$STATE/lock-misses" 2>/dev/null || echo 0) + 1 ))" > "$STATE/lock-misses"
    log "gbrain: busy (another program has it open), will check again next run"
    [ "$(cat "$STATE/lock-misses")" -ge 3 ] && warn "gbrain's settings couldn't be checked for 3 runs because it's always in use. Quit your AI tools overnight once."
    return
  fi
  echo 0 > "$STATE/lock-misses"
  printf '%s' "$show" | grep -iE '(chat|expansion|rerank)[a-z_.]*.*(openai|anthropic|voyage|openrouter|gemini):' \
    && warn "gbrain still lists a cloud model: check 'gbrain config show'"
  log "gbrain: local configuration checked"
}
[ "${GBRAIN:-0}" = 1 ] && enforce_local

# 5. Health -------------------------------------------------------------------------
if [ "${GBRAIN:-0}" = 1 ] && [ "$DRY" = 0 ]; then
  if ! curl -fsS 127.0.0.1:11434/api/version >/dev/null 2>&1; then
    launchctl kickstart -k "gui/$(id -u)/local.ollama" >>"$LOG" 2>&1 || true
    sleep 5
    curl -fsS 127.0.0.1:11434/api/version >/dev/null 2>&1 || warn "Ollama isn't running, so gbrain can't search by meaning. Run scripts/setup-ollama-macos.sh"
  fi
  stats="$(t 90 gbrain stats 2>&1)"
  if printf '%s' "$stats" | grep -q "Pages:"; then log "gbrain: $(printf '%s' "$stats" | grep -E 'Pages:|Embedded:' | tr -s ' ' | tr '\n' ' ')"
  elif printf '%s' "$stats" | grep -qiE 'lock'; then log "gbrain: busy, health check skipped this run"
  else warn "gbrain's database didn't open. See integrations/gbrain/README.md, 'If it stops working'"; fi
fi

# Report ------------------------------------------------------------------------------
if [ "${#PROBLEMS[@]}" -gt 0 ]; then
  msg="$(printf '%s; ' "${PROBLEMS[@]}")"
  [ "$DRY" = 0 ] && command -v osascript >/dev/null && osascript -e "display notification \"${msg//\"/}\" with title \"Agent skills maintenance\"" >/dev/null 2>&1
  log "done with ${#PROBLEMS[@]} item(s) needing attention"
  exit 1
fi
log "done, all good"
exit 0
