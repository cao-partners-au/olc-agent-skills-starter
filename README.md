# Agent Skills Starter

Your own home for AI agent skills. One private repo that holds every skill you use, so they come with you when you change laptops or move between AI tools (Claude Code, Codex, Cursor, Gemini CLI, Hermes, OpenClaw and others).

A skill is a folder with a `SKILL.md` file: plain instructions your agent loads when a task matches. This repo uses the open Agent Skills format, so the same folder works in every tool that supports it.

> **Important: make your own copy, don't rely on this one.** The safest way to use this repo is
> to copy it into your own private repository (step 1 below) and use only your copy. This starter
> is public for a limited time and will be made private again for security. Don't link to it,
> bookmark it as your source, or build anything that depends on it staying available. Once it goes
> private, your copy keeps working exactly as it is; only the automatic starter updates stop.

## Get started (5 minutes)

1. **Make your own copy.** Click **Use this template** (top right) and choose **Create a new repository**. Set it to **Private**. This gives you a clean copy you own, with no link back to this one.
2. **Clone your copy** to your computer:
   ```bash
   git clone https://github.com/<your-account>/<your-repo>.git ~/agent-skills
   cd ~/agent-skills
   ```
3. **Install the skills into your tools:**
   ```bash
   ./install.sh --dry-run   # shows what it would do, changes nothing
   ./install.sh             # links every skill into each AI tool it finds
   ```
4. **Add the agent rules**, so your agent knows when to use the add-ons below:
   ```bash
   ./scripts/add-agent-rules.sh --dry-run
   ./scripts/add-agent-rules.sh
   ```
5. Restart your AI tool. Your skills are now available.
6. **Optional, recommended:** install the add-ons in [integrations/](integrations/README.md): gstack (review, testing, shipping) and gbrain (local memory).
7. **Switch on automatic maintenance** (macOS), so you never have to update anything by hand:
   ```bash
   ./scripts/setup-maintenance-macos.sh
   ```
   Every day it updates gstack and gbrain, pulls improvements from this starter into your copy (never overwriting files you've edited), puts gbrain's fully local settings back if anything changed them, and checks everything still works. You only hear from it, as a Mac notification, if something needs you. Log: `~/Library/Logs/agent-skills-maintain.log`.

Not comfortable with the terminal? Paste this into your agent:

> Clone my skills repo `https://github.com/<your-account>/<your-repo>` to `~/agent-skills`, then run `./install.sh --dry-run`, show me the result, and run `./install.sh` once I approve.

## How it works

`install.sh` links (it does not copy) each folder in `skills/` into the skills folder of every AI tool installed on your machine. Every tool then reads the same files:

- Edit a skill once in this repo, and every tool sees the change.
- New laptop or new tool: clone your repo and run `./install.sh` again.
- Remove the links any time with `./install.sh --remove`. Your repo is untouched.

It never overwrites a skill you already have with the same name. It tells you and skips it.

## Day to day

```bash
cd ~/agent-skills
git pull                                  # get changes from your other machines
# add or edit skills in skills/<name>/SKILL.md
./install.sh                              # link any new skills
git add -A && git commit -m "Add <skill>" && git push
```

Ask your agent to "write a new skill for X" and it will use the `write-skill` skill to create it in the right format, inside this repo.

## What's included

| Folder | What it does |
|---|---|
| `skills/write-skill` | Creates or improves a skill in this repo, in the right format |
| `skills/ponytail` | Coding rules: the smallest change that fully solves the task ([guide](integrations/ponytail/README.md)) |
| `skills/_template` | A blank skill to copy |
| `skills/site-analytics` | Website analytics: joins Plausible and Microsoft Clarity to show why pages convert or don't, and sets both up |
| `skills/karpathy-council` | Runs a big decision past five advisors with different thinking styles, then a chairman's verdict |
| `skills/1password-secrets` | Keep keys and passwords in 1Password, and give agents read-only access through a service account |
| `skills/meta-*`, `ad-pixel-funnel`, `marketing-roas`, `cac-and-conversion` | Meta ads: build, review weekly, health check, pixel and conversions setup, return on ad spend |
| `skills/google-ads-*` | Google Ads campaign launch and conversion tracking |
| `skills/tiktok-ads-mcp` | Read TikTok Ads performance |
| `skills/meta-ad-recon` | Free competitor ad research from Meta's public Ad Library |
| `skills/open-operator-audit` | SEO and AI search (GEO) audit for your website |

The ad skills need your own ad account logins. Start with [docs/ad-skills/QUICKSTART.md](docs/ad-skills/QUICKSTART.md), and see [ADAPTING-TO-YOUR-STACK.md](docs/ad-skills/ADAPTING-TO-YOUR-STACK.md) to fit them to your business.

## Add-ons (integrations)

| Add-on | What it does | Guide |
|---|---|---|
| ponytail | Smaller, safer code changes. Included in `skills/` | [integrations/ponytail](integrations/ponytail/README.md) |
| gstack | Workflow skills: `/review` before every merge, `/qa` and `/browse` for testing in a real browser, `/ship` and `/land-and-deploy` for releases, `/investigate` for debugging, `/cso` for security audits | [integrations/gstack](integrations/gstack/README.md) |
| gbrain | Long-term searchable memory, run locally with Ollama so nothing leaves your computer | [integrations/gbrain](integrations/gbrain/README.md) |
| REA | Reverse-engineering tools for software you're allowed to inspect. Per project only | [integrations/rea](integrations/rea/README.md) |

[agent-rules/](agent-rules/README.md) tells your agent when to use each one, including running `/review` on every pull request before asking you to merge.

## Rules of the house

Read [HOUSEKEEPING.md](HOUSEKEEPING.md) once. The short version:

1. **No secrets in this repo, ever.** Keys and passwords live in a password manager or environment variables. A check blocks commits that look like they contain one.
2. **One skill, one folder, one job.** A clear description of when it should be used.
3. **Vet before you install** someone else's skill: [VETTING-THIRD-PARTY-SKILLS.md](VETTING-THIRD-PARTY-SKILLS.md).
4. **Review every quarter.** Retire skills you no longer use.
