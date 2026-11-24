# Changelog

Note notable changes here, newest first.

## Skills

- Agent rules: put your own rules in `agent-rules/AGENT-RULES.local.md`; they are added after the shared rules and never overwritten, so editing `AGENT-RULES.md` is no longer needed (it stops updates reaching you). `add-agent-rules.sh` now skips a file whose markers are out of order or unreadable, handles Windows line endings, and the daily maintenance tells you when a file was skipped instead of failing quietly. Rules are re-applied every day (a file already up to date is left alone, no new backup), so edits to your local file take effect overnight. Maintainers: `scripts/test-add-agent-rules.sh` tests the installer on macOS bash.
- Agent rules: your agent must now load each named skill (gstack `/review`, `/qa`, ponytail and others) rather than imitate it, and say which one it loaded; if a skill isn't available in that tool it says so and never claims it was used. ponytail is loaded at the start of every coding task: it never switched itself on, so in our own Claude Code trial it went unused for two weeks. Re-running `add-agent-rules.sh` no longer adds a blank line each time, and it refuses to touch a file whose end marker was deleted (that used to delete everything after the block). A pull request is only "reviewed" once gstack `/review` has run; a manual review in a tool without it doesn't count.
- New: `au-employment-law` (figures checked for 2026-27, including Payday Super and the draft non-compete ban), `pre-meeting-brief`, `meeting-action-items`, `email-inbox-triage`, `weekly-review-planning` (the last three by Hermes Agent, MIT licence), and `google-workspace-dwd-setup`.
- `site-analytics`: new. Plausible plus Microsoft Clarity reporting, setup guide and optional daily history.
- gbrain guide: explains it's optional, and that it shines when you use more than one AI tool on the same project.
- `karpathy-council`: new. Five advisors, anonymous peer review and a chairman's verdict for high-stakes decisions.
- `1password-secrets`: checked against 1Password's official docs and tested reading secrets with a real service account (`op read`, `op run`, `op inject`). Adds plan limits, the minimum CLI version, and which vaults service accounts can't reach.
- README and HOUSEKEEPING: use your own private copy; this starter will be made private again.
- `1password-secrets`: new. Create a vault per purpose, add credentials without exposing them, create a read-only service account, store its token in the keychain or host, and read secrets at runtime with `op read` and `op run`.
- `meta-ad-recon`: says outright to use a logged-out browser on the public Ad Library, never Apify, Foreplay or another paid scraper even when one is connected, and why a plain fetch and Meta's API don't work for Australian ads.

## Automatic maintenance

- `scripts/maintain.sh`, run daily and at login by `scripts/setup-maintenance-macos.sh`: updates gstack and gbrain (including Bun and the search index), pulls starter improvements into your copy without overwriting your edits, enforces gbrain's fully local configuration, and checks Ollama and gbrain are healthy. Notifies only when something needs you.
- `.starter-managed`: the list of starter files, so updates can tell which ones you've edited.

## Integrations

- Guides for ponytail, gstack, gbrain and REA in `integrations/`, with the versions they were tested on.
- `skills/ponytail`: the ponytail core skill (v5.3.3, MIT), copied unchanged.
- `agent-rules/` and `scripts/add-agent-rules.sh`: tells your agent when to use gstack skills, the pull request `/review` rule, ponytail, gbrain and REA limits.
- `scripts/setup-ollama-macos.sh`: runs Ollama at login for gbrain's local embeddings, unloading the model after each use.

## Starter version

- 12 ad and marketing skills: Meta (campaigns, weekly review, account health check, pixel and conversions, competitor ad research), Google Ads (campaign launch, conversion tracking), TikTok Ads, return on ad spend, cost per client, and an SEO and AI search audit.
- `write-skill` and `_template` for creating your own skills.
- `install.sh` to link skills into every AI tool on your machine, with a secret check on commits.
- Housekeeping and third-party vetting guides.
