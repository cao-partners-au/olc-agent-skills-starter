# Vetting third-party skills and tools

Skills and agent add-ons from the internet run with your agent's access: your files, your logins, your email. Check before you install.

## Before installing, check

1. **Read it.** Open every file, not just the README. A skill should be plain instructions plus any scripts it needs. If you can't follow what it does, ask your agent to explain it line by line before installing.
2. **What does it run?** Look for scripts, "hooks" that run automatically, and anything that downloads more code (`curl`, `npx …@latest`, "update itself"). These are the risky parts.
3. **What does it send out?** Look for web addresses, webhooks, "telemetry" or "analytics". Know where your data goes.
4. **What can it reach?** Be wary of anything that reads your whole disk, your browser cookies or saved passwords, or asks for broad account access.
5. **Who made it?** Check the author, how long it has existed, and whether the history looks real. A brand-new repo with one squashed commit and big claims deserves extra care.
6. **Is the benefit real?** Author benchmarks are marketing until you've tested it on your own work.

## When you do install

- **Take only the part you need.** Often that's one `SKILL.md`, not the whole plugin with its background scripts.
- **Copy it into this repo** so you control the version, rather than installing a live link that updates itself.
- **Pin versions** of any tools it needs.
- **Keep it in one project** if it's only needed for one job, and remove it afterwards.
- **Note the source** in the skill folder (where it came from, which version, the date), and the licence.

## Red flags: don't install

- It asks for passwords or keys to be pasted into it.
- It disables safety checks or asks for "full permissions".
- It's obfuscated or minified code you can't read.
- It promises to bypass logins, bot protection or a platform's terms of service.
