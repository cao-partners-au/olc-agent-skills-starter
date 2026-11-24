## Agent skills repo rules

My skills live in my skills repo (usually `~/agent-skills`). Create and edit skills there with the `write-skill` skill, never directly in a tool's skills folder.

### Load the skill, don't imitate it

When a rule below names a skill, load that skill before you start (with your skill tool, or by opening and following its SKILL.md), and say which skill you loaded. Doing similar steps from memory does not count: a skill only works when it is loaded, and you can't rely on it loading by itself.

In some tools gstack's skills have a `gstack-` prefix (`gstack-review`, `gstack-qa`): use whichever name exists, and never substitute the tool's own built-in review command.

If a named skill isn't available in this tool, say so in one line, do the task without it, and never claim it was used.

### Use gstack skills instead of improvising

When the task matches, load the gstack skill rather than doing it ad hoc:

- **Reviewing a change or pull request:** `/review`. It checks the code around the change, not just the diff.
- **Testing a website, CRM or app:** `/qa` (test and fix) or `/qa-only` (report only), and `/browse` for any other web browsing.
- **Releasing:** `/ship` to prepare and open the pull request, `/land-and-deploy` to merge and deploy.
- **Debugging a problem whose cause isn't known yet:** `/investigate`.
- **Security questions or audits:** `/cso`.

### Pull request review rule

Before asking me to merge any pull request, in any repo, load and run the `/review` skill on it, fix or explain every finding, and include the review result when you ask me to merge. Never ask me to merge an unreviewed pull request.

### Coding

- At the start of every coding task, load the `ponytail` skill (default level, never `ultra`): the smallest change that fully does what I asked, without cutting validation, error handling or security.
- Do what I asked, literally. If you think something else is needed, ask before doing it.

### Memory (gbrain)

- Search gbrain before external lookups when the question might be about my own business, decisions or past work.
- Before changing code, search gbrain for gotchas, past incidents and rules about the files and systems involved, and say what you found. If gbrain isn't connected, say so rather than skipping it.
- Save decisions, fixes and gotchas I ask you to remember to gbrain.
- Never sync a folder into gbrain without checking it for keys, passwords and `.env` files first.

### REA

Use REA only in a project where I've installed it for a stated purpose, and only on software I own or am allowed to analyse. Never install it globally.

### Secrets

Never put API keys, tokens or passwords in skills, code, commits or chat. Refer to them by environment variable or password-manager item name.
