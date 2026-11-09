# Agent rules

Installing a skill makes it available. These rules tell your agent **when** to use the integrations instead of improvising: gstack's `/review` on every pull request, `/qa` for testing, `/investigate` for debugging, ponytail for coding, gbrain for memory, and the limits on REA.

The rules are in [AGENT-RULES.md](AGENT-RULES.md). Edit them to suit you before adding them.

## Add them to your AI tools

```bash
./scripts/add-agent-rules.sh --dry-run   # shows which files it would change
./scripts/add-agent-rules.sh             # adds the rules
```

It adds the rules to the global instruction file of each tool it finds:

| Tool | File |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |

The rules sit between two marker lines, so:
- your own instructions in those files are never touched,
- running it again after editing `AGENT-RULES.md` replaces the old block rather than adding a second copy,
- `./scripts/add-agent-rules.sh --remove` takes them out again.

A backup of each file is saved next to it every time.

Restart your AI tools afterwards.
