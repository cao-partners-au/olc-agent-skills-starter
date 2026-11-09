#!/usr/bin/env bash
# Link every skill in ./skills into the skills folder of each AI tool on this machine.
#   ./install.sh            link skills (and switch on the secret check for commits)
#   ./install.sh --dry-run  show what would happen, change nothing
#   ./install.sh --remove   remove the links this script made (your repo is untouched)
# Links, never copies: edit a skill here and every tool sees it. Never overwrites a
# skill folder that isn't one of our links. Folders starting with "_" are skipped.
set -euo pipefail

MODE="install"
case "${1:-}" in
  --dry-run) MODE="dry" ;;
  --remove) MODE="remove" ;;
  "") ;;
  *) echo "Usage: ./install.sh [--dry-run|--remove]"; exit 1 ;;
esac

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$REPO/skills"

# "tool name|folder that shows the tool is installed|its skills folder"
TOOLS=(
  "Claude Code|$HOME/.claude|$HOME/.claude/skills"
  "Codex|$HOME/.codex|$HOME/.codex/skills"
  "Shared agent skills (.agents)|$HOME/.agents|$HOME/.agents/skills"
  "Gemini CLI|$HOME/.gemini|$HOME/.gemini/skills"
  "Cursor|$HOME/.cursor|$HOME/.cursor/skills"
  "Hermes|$HOME/.hermes|$HOME/.hermes/skills"
  "OpenClaw|$HOME/.openclaw|$HOME/.openclaw/skills"
)

run() { if [ "$MODE" = "dry" ]; then echo "    would run: $*"; else "$@"; fi; }

found=0
for entry in "${TOOLS[@]}"; do
  IFS="|" read -r name home target <<< "$entry"
  [ -d "$home" ] || continue
  found=1
  echo "$name -> $target"
  [ "$MODE" = "remove" ] || run mkdir -p "$target"
  for dir in "$SKILLS"/*/; do
    dir="${dir%/}"; skill="$(basename "$dir")"
    case "$skill" in _*) continue ;; esac
    [ -f "$dir/SKILL.md" ] || continue
    link="$target/$skill"
    if [ "$MODE" = "remove" ]; then
      if [ -L "$link" ] && [ "$(readlink "$link")" = "$dir" ]; then rm "$link"; echo "  removed $skill"; fi
      continue
    fi
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$dir" ]; then
      echo "  ok       $skill"
    elif [ -e "$link" ] || [ -L "$link" ]; then
      echo "  SKIPPED  $skill: a different '$skill' is already there. Rename one of them, then run again."
    else
      if [ "$MODE" = "dry" ]; then echo "  would link $skill"; else ln -s "$dir" "$link"; echo "  linked   $skill"; fi
    fi
  done
done

[ "$found" = 1 ] || echo "No supported AI tools found in your home folder. Install one, then run this again."

if [ "$MODE" = "install" ] && [ -d "$REPO/.git" ]; then
  git -C "$REPO" config core.hooksPath .githooks
  chmod +x "$REPO/.githooks/pre-commit"
  echo "Secret check switched on for commits in this repo."
fi
[ "$MODE" = "dry" ] && echo "Dry run: nothing was changed."
[ "$MODE" = "install" ] && echo "Done. Restart your AI tools to load new skills."
exit 0
