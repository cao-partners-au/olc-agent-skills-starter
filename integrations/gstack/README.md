# gstack: workflow skills for building software

**What it is.** A free pack of 40+ skills for Claude Code (also Codex and others) that turn common software jobs into checklists your agent follows: reviewing a change, testing a site in a real browser, shipping a release, debugging, security audits and more. Made by Garry Tan. Source: [garrytan/gstack](https://github.com/garrytan/gstack).

**Does it help passively?** Mostly no. gstack helps when one of its skills runs. You can type the command (`/review`), or just ask naturally ("review this PR", "test the site") and the matching skill runs. Everyday coding ("fix this bug") doesn't go through gstack. That's why we add rules telling your agent when to use it: see [agent-rules](../../agent-rules/README.md).

## The skills worth knowing

| Skill | Use it for |
|---|---|
| `/review` | Check a change (pull request) before merging, including the code around the change, not just the diff |
| `/qa`, `/browse` | Test your website, CRM or app in a real browser: click through it, check errors, take screenshots |
| `/ship`, `/land-and-deploy` | A fixed release checklist: tests, review, version, changelog, pull request, deploy |
| `/investigate` | Structured debugging when you don't yet know the cause |
| `/cso` | A security audit of your codebase |

Others you may like: `/office-hours` (think through a product idea), `/plan-eng-review` (review a technical plan before building), `/design-review` (visual polish), `/retro` (weekly look back).

## Setup (macOS or Linux)

Needs: [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Git, and [Bun](https://bun.sh) 1.4.2 or newer.

```bash
curl -fsSL https://bun.sh/install | bash        # skip if `bun --version` shows 1.4.2+
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

Restart Claude Code. `./setup` installs the skills and registers a couple of small hooks in your Claude Code settings (it backs the settings up first). Its own docs list exactly what: [docs/install.md](https://github.com/garrytan/gstack/blob/main/docs/install.md).

Then add the agent rules from [agent-rules](../../agent-rules/README.md). They include the review rule below.

## The review rule

The single highest-value habit: **every pull request gets `/review` before you merge it.** The agent rules make this automatic: your agent runs `/review`, fixes or explains each finding, and includes the result when it asks you to merge. It catches changes that went wider than you asked, missed callers, and risky edits, before they reach your live system.

## Updating

gstack checks for updates itself and offers to upgrade. To upgrade by hand:

```bash
cd ~/.claude/skills/gstack && git pull && ./setup
```

Don't upgrade in the middle of important work: big jumps can change how skills behave.

## Optional extras

- **Block pushes that contain passwords or keys** in any repo you ship from: `~/.claude/skills/gstack/bin/gstack-config set redact_prepush_hook true`.
- **gstack and gbrain work together**: gstack's `/sync-gbrain` keeps a repo indexed in gbrain. See [gbrain](../gbrain/README.md).
