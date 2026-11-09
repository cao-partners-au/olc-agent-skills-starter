# Integrations

Four add-ons that make an AI coding setup safer and more useful. Each has its own guide in this folder.

| Add-on | What it is | Install it? |
|---|---|---|
| [ponytail](ponytail/README.md) | Coding rules: the smallest change that fully solves the task | Yes. Already in `skills/ponytail`, installed by `install.sh` |
| [gstack](gstack/README.md) | A pack of workflow skills: review, QA, ship, debug, security audit | Yes, if you write or change code with Claude Code |
| [gbrain](gbrain/README.md) | Long-term searchable memory for your agent, kept on your own computer | Yes, with local embeddings (Ollama) so nothing leaves your machine |
| [REA](rea/README.md) | Reverse-engineering tools for software you're allowed to inspect | Only for a specific project that needs it. Never install it globally |

After installing, add the agent rules so your AI tools know when to use them: see [agent-rules/README.md](../agent-rules/README.md).

## Versions this was tested with (9 Nov 2026)

| Tool | Version |
|---|---|
| ponytail | 5.3.3 (core skill only) |
| gstack | 1.98.0.0 |
| gbrain | 0.60.619.0 |
| Bun | 1.4.4 |
| Ollama | 0.40.15 with `nomic-embed-text` |
| REA (`rea-agents`) | 6.8.0 |

gstack and gbrain update themselves through the daily maintenance (`scripts/setup-maintenance-macos.sh`), which then re-checks the agreed configuration. ponytail updates reach you through the starter: new versions are vetted before they're added here, then the daily maintenance pulls them into your copy. REA is never auto-updated, because it's pinned per project.

All four tools are made by other people. Read [VETTING-THIRD-PARTY-SKILLS.md](../VETTING-THIRD-PARTY-SKILLS.md) before installing, and keep their versions noted here up to date.
