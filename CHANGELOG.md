# Changelog

Note notable changes here, newest first.

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
