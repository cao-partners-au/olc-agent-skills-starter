---
name: write-skill
description: Create a new agent skill, or improve an existing one, inside this skills repo, following its housekeeping rules. Use when asked to "write a skill", "make this a skill", "save this as a skill", "turn what we just did into a skill", or "improve the X skill".
---

# Write a skill

Skills live in the user's skills repo (usually `~/agent-skills`), one folder per skill: `skills/<name>/SKILL.md`. Follow `HOUSEKEEPING.md` in that repo.

## Steps

1. **Find the repo.** Look for `~/agent-skills`, or ask the user where their skills repo is. Never create skills outside it.
2. **Check for an existing skill** that already covers the job (`skills/*/SKILL.md`). Improve that one rather than adding a near-duplicate.
3. **Agree the job in one sentence** with the user: what outcome, and when it should trigger. If it covers two unrelated jobs, make two skills.
4. **Copy `skills/_template/SKILL.md`** to `skills/<name>/SKILL.md`. Name: lowercase words joined by hyphens.
5. **Write the description first.** It decides when the skill loads: say what it does and list the phrases the user would actually use.
6. **Fill in the body**, briefly:
   - the outcome, and what to check before starting
   - only the steps and rules that matter, not general knowledge
   - business facts in one place
   - gotchas: what went wrong before and the fix. When turning a just-finished task into a skill, capture the mistakes and corrections from that task here.
7. **No secrets.** Refer to keys and logins by environment variable or password-manager item name only. Never paste a value.
8. **Test it** on a real task, or walk the user through a dry run, and fix what's unclear.
9. **Install and save:** run `./install.sh` from the repo, tell the user to restart their AI tool, then commit and push:
   ```bash
   git add skills/<name> && git commit -m "Add <name> skill" && git push
   ```
   Add a line to `CHANGELOG.md` for anything notable.

## Improving an existing skill

- Read the whole skill first. Change the smallest part that fixes the problem.
- Add the new gotcha or rule; don't rewrite what already works.
- Commit with a message that says what changed and why.
