# ponytail: smallest-complete-change coding

**What it is.** A short set of coding instructions ("lazy senior developer") that makes your agent find the smallest change that fully solves a task. Before writing code it works down a ladder: does this need to exist, is it already in the codebase, does the standard library or platform do it, can an installed package do it, and only then writes the minimum new code. It never cuts validation, error handling, security or accessibility, adds a small test for new non-trivial logic, checks every caller before fixing a bug, and ends each reply with what it skipped or didn't check.

**Why it helps.** AI agents tend to over-build: new files, wrappers and options nobody asked for. Smaller changes are easier to review and less likely to break things.

Source: [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail), MIT licence.

## Setup

It's already in this repo at `skills/ponytail`, copied unchanged from version 5.3.3. `./install.sh` links it into your AI tools like any other skill.

We deliberately took **only the core skill file**, not the full plugin. The plugin also adds background scripts that run on every session and message, a cost-tracking panel and extra review commands. They aren't needed, and the review commands overlap with gstack's `/review`.

## Using it

- It switches on for coding tasks, or when you say "ponytail", "be lazy" or "simplest solution".
- Change the level with `/ponytail lite`, `/ponytail full` (default) or `/ponytail off`.
- **Avoid `ultra`.** It pushes back on what you asked for before building it. If you want your agent to do exactly what you say, that gets in the way.

## What to expect

In our own side-by-side test on a real bug fix (one task, judged blind), ponytail produced about 10% less code and used about 5% fewer tokens, with equal correctness. The author's headline numbers are bigger. Treat it as a trial: compare a few of your own tasks with and without it before deciding.

## Updating

Check the source repo for a newer version, read the changes, then replace `skills/ponytail/SKILL.md`, update `skills/ponytail/SOURCE.md`, and commit.
