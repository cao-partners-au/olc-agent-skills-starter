# gbrain: long-term memory for your agent, kept local

**What it is.** A searchable memory your AI agent can read and write. It stores pages (notes, decisions, documents and, optionally, your code), splits them into chunks, and indexes them by **meaning**, so your agent can ask "what did we decide about refunds?" and find the right note even when the wording differs. Your agent reaches it through tools (`search`, `query`, and saving new pages). Made by Garry Tan. Source: [garrytan/gbrain](https://github.com/garrytan/gbrain).

**What it's good for**
- Remembering decisions, fixes and "gotchas" across sessions and AI tools.
- Searching your notes and documents by meaning, not exact words.
- Optionally, indexing a codebase so your agent can ask "where is the invoice logic?" without hunting through files. Plain text search (`grep`) is still better for exact checks like "every place that uses this table".

## Why local embeddings (Ollama)

Searching by meaning needs **embeddings**: each chunk of text is turned into a list of numbers that captures its meaning. By default gbrain uses a paid cloud service for this, which means **your notes and code are sent to that company**.

This setup uses **Ollama** instead: a free app that runs a small embedding model on your own computer.
- Costs nothing, and nothing leaves your machine.
- The model only loads while it's being used, for a second or two per search, then unloads. The background service uses about 30 MB of memory when idle.
- Quality is a little below the paid models, and plenty for notes and code.

Claude can't do this part for you: Anthropic doesn't offer an embeddings service, and your Claude plan only covers chat.

## Setup (macOS)

Needs [Bun](https://bun.sh) 1.4.4+ and [Homebrew](https://brew.sh).

**1. Install Ollama and the embedding model**
```bash
brew install ollama
```
Then start it at login with the model unloading after every use (run from this repo):
```bash
./scripts/setup-ollama-macos.sh
ollama pull nomic-embed-text
```

**2. Install gbrain** (only from the official source; a package called `gbrain` on npm is not it)
```bash
curl -fsSL https://bun.sh/install | bash             # skip if `bun --version` shows 1.4.4+
bun install -g github:garrytan/gbrain#stable
```

**3. Create your brain with local embeddings**
```bash
gbrain init --pglite --embedding-model ollama:nomic-embed-text --embedding-dimensions 768
```
`--pglite` keeps the database as a folder in `~/.gbrain` on your computer. No server, no account.

**4. Connect it to Claude Code** (or `codex` instead of `claude-code`)
```bash
gbrain setup claude-code --dry-run   # shows what it will change
gbrain setup claude-code
```
This registers gbrain with Claude Code and adds a short "check the brain first" note to your agent instructions. Restart Claude Code.

**5. Check it really works**
```bash
gbrain stats                       # shows pages and chunks
gbrain search "a phrase from one of your notes"
```
Don't rely on `gbrain doctor` alone: it can report healthy while the database won't start. A real search is the test.

## Keep it fully local

- Don't add an OpenAI, Voyage or other AI key to gbrain unless you decide to. Without one, nothing is sent out.
- If you later set a chat or "expansion" model (used for written answers and smarter queries), choose a local one (`ollama:...`), or accept that those queries go to that provider.

## Getting your knowledge in

Add each folder or repo as a **source**, then sync it:

```bash
gbrain sources add notes --path ~/notes --force       # a plain folder of markdown notes
gbrain sources add skills --path ~/agent-skills       # this skills repo
gbrain sources federate notes && gbrain sources federate skills   # include them in normal searches
gbrain sync --source notes
gbrain sync --source skills
```

For a code repo: `gbrain sources add my-app --path ~/code/my-app`, then `gbrain sync --source my-app --strategy code` (a big repo takes 20 to 30 minutes the first time). If you use gstack, `/sync-gbrain` does this for you.

### Before syncing anything: secrets

A sync reads every file in the source and stores it in your brain. One real-world leak came from a sync that read a keys file sitting inside a synced folder.
- For a **git repo**, gbrain reads only files git tracks; files listed in `.gitignore` are skipped. Never use `--include-gitignored`.
- For a **plain folder** (`--force`), it reads everything in it. Make sure no keys, passwords or `.env` files are in that folder.
- Check first: look through the folder, or ask your agent to "scan this folder for keys and passwords before I sync it".

## Upgrading

```bash
gbrain check-update
gbrain upgrade
```
If it says it needs a newer Bun: run `bun upgrade`, then `gbrain post-upgrade`.
If searches then say `projection_pending` or return nothing: run `gbrain projections drain`.

## If it stops working

1. Is Ollama running? `curl 127.0.0.1:11434/api/version` should print a version. If not: `launchctl kickstart -k gui/$(id -u)/local.ollama`.
2. Does the database open? `gbrain stats`. If it errors, upgrade gbrain (above): an old version failed to start on newer macOS.
3. Back up first if you're unsure: `cp -Rp ~/.gbrain ~/.gbrain.bak-$(date +%F)`.

Linux: install Ollama from [ollama.com](https://ollama.com) (it sets up its own service), set `OLLAMA_KEEP_ALIVE=0` in that service, and skip `setup-ollama-macos.sh`.
