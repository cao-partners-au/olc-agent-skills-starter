# Housekeeping

A skills repo stays useful only if it stays tidy. These rules keep it that way.

## 1. No secrets, ever

- API keys, tokens, passwords and private links never go in a skill or anywhere in this repo.
- Keep them in a password manager (1Password, Bitwarden) or in environment variables, and have the skill read them from there. The `1password-secrets` skill sets this up for you.
- In a skill, name the variable, never the value: "uses `META_ACCESS_TOKEN`", not the token itself.
- This repo blocks commits that look like they contain a secret (see `.githooks/pre-commit`, switched on by `install.sh`). It is a safety net, not a guarantee. If a secret is ever committed, treat it as leaked: change the key straight away, then remove it from the repo.
- Keep your copy of this repo **private**.

## 2. One skill, one folder, one job

- `skills/<skill-name>/SKILL.md`, with the name in lowercase and hyphens: `weekly-sales-report`, not `Report Stuff v2`.
- The `description` at the top says **what it does and when to use it**, with the words you'd actually say ("use when I ask for the weekly sales numbers"). Your agent decides whether to load a skill from this line alone.
- If a skill does two unrelated jobs, split it.
- Supporting files (scripts, examples, reference notes) go inside the skill's own folder.

## 3. Write skills that age well

- State the outcome and the rules, not a long script of steps the agent already knows.
- Put business facts that change (prices, staff, account IDs) in one place in the skill, so they're easy to update.
- Record what went wrong and the fix ("the export misses refunds, so add them from X"). That is the most valuable part of a skill.
- Test a skill on a real task before you rely on it.

## 4. Vet anything you didn't write

Read [VETTING-THIRD-PARTY-SKILLS.md](VETTING-THIRD-PARTY-SKILLS.md) before adding a skill or tool from the internet.

## 5. Keep a record

- Commit with a clear message: "Add weekly-sales-report", "Fix GST in invoice-check".
- Note notable changes in `CHANGELOG.md`.
- Pull before you start and push when you finish, so all your machines stay in step.

## 6. Review every quarter

- Delete or archive skills you haven't used in three months.
- Check skills that touch money, customers or sending messages still match how the business works today.
- Re-run `./install.sh` after removing a skill, then restart your AI tools.
