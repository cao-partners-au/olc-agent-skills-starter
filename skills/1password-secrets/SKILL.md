---
name: 1password-secrets
description: Keep API keys, passwords and tokens in 1Password and give AI agents safe, read-only access to them through a service account. Covers creating vaults, adding credentials from the command line without them touching files or chat, creating and storing a service account token, and having scripts and agents read secrets at runtime. Use when asked to "set up 1Password for my agents", "store this API key", "where should I keep this token", "create a vault", "make a service account", "give the agent access to the credentials", "op read", "op run", or when a skill or script needs a secret.
---

# 1Password for agents

The outcome: every secret lives in one 1Password vault per purpose, and agents and scripts read
it at runtime through a service account that can only see that vault. No key is ever pasted into
a chat, a file, a skill or a git repo. When a key changes, you change it once in 1Password.

## Before you start

- **Any 1Password account.** Service accounts work on Individual, Families, Teams and Business
  plans; Business gets much higher usage limits (see Gotchas).
- **1Password CLI (`op`) version 2.18.0 or later** (service accounts need it):
  `brew install 1password-cli` on a Mac, then check `op --version`.
- **The desktop app's CLI integration** switched on (Settings > Developer > "Integrate with
  1Password CLI"), so `op` signs in with Touch ID as the person. Check with `op whoami`.
- Creating service accounts needs permission to manage them in your account (normally the owner
  or an administrator). If `op` says you don't have permission, stop and ask the account owner.

## The model

| Piece | What it is | Who uses it |
|---|---|---|
| Vault | A folder of items, e.g. `Agents - Marketing`. One per purpose or team, never one giant vault | Set up by a person |
| Item | One credential: an API key, a login, a token | Added by a person |
| Secret reference | The address of one field: `op://Vault/Item/field`. Safe to put in files and skills; it is not the secret | Scripts and agents |
| Service account | A robot login that can only read the vaults you name | Agents and scheduled jobs |
| `OP_SERVICE_ACCOUNT_TOKEN` | The service account's key. Unlocks only its vaults | Kept in the computer's keychain or the host's secret store, never in a file |

Service accounts can never see your built-in Personal, Private or Employee vault, or the default
Shared vault. That is the point: an agent only ever sees what you deliberately put in a vault you
created for it. You can have up to 100 service accounts.

## How to do it

### 1. Create a vault per purpose (as a person)

```bash
op vault create "Agents - Marketing" --description "Read by marketing agents only"
```

Name vaults so it's obvious who reads them. Keep personal logins out of agent vaults.

### 2. Add a credential without exposing it

Never put the value on the command line (it lands in shell history) or in a chat with the agent.
Use one of these:

- **The 1Password app** (simplest): New Item, API Credential, paste the key, save it in the vault.
- **A template, from the command line:**
  ```bash
  op item template get "API Credential" --out-file /tmp/item.json
  # edit /tmp/item.json: set "title", and the "value" of the field with "id": "credential"
  op item create --vault "Agents - Marketing" --template /tmp/item.json
  rm -P /tmp/item.json   # delete the filled-in template straight away (rm -P overwrites first on macOS)
  ```
- **Let 1Password generate it** when you're setting a new password:
  `op item create --category login --vault "Agents - Marketing" --title "Supplier portal" --generate-password username=agent@yourco.com.au`

Then note the reference, e.g. `op://Agents - Marketing/Meta Ads token/credential`. Confirm it
resolves without printing it: `op read "op://Agents - Marketing/Meta Ads token/credential" >/dev/null && echo ok`.

### 3. Create a service account with the least access (as an admin)

```bash
op service-account create "marketing-agents" \
  --vault "Agents - Marketing:read_items" \
  --expires-in 90d
```

- Give `read_items` only. Add `write_items` only if the agent must save new credentials, and say why.
- One service account per job or agent group, so you can switch one off without breaking the rest.
- The token is shown **once**. Save it straight into 1Password, in a vault the agents can't read
  (e.g. your own admin vault), as an API Credential called `Service account: marketing-agents`.
- Set a reminder to rotate it before it expires.

### 4. Put the token where agents can use it

**On a Mac** (an agent or scheduled job on this computer), store it in the macOS keychain:
```bash
security add-generic-password -a "$USER" -s op-sa-marketing-agents -w
# paste the token when asked; it is not echoed or saved in history
```
and load it only for the command that needs it:
```bash
export OP_SERVICE_ACCOUNT_TOKEN="$(security find-generic-password -a "$USER" -s op-sa-marketing-agents -w)"
```

Check it works: `op user get --me` should show `Type: SERVICE_ACCOUNT`.

**On a hosting platform** (Railway, Render, GitHub Actions and similar): add
`OP_SERVICE_ACCOUNT_TOKEN` as a secret variable in that platform's settings. It is the only
secret the platform needs to hold.

### 5. Read secrets at runtime

- **One value:** `op read "op://Agents - Marketing/Meta Ads token/credential"`
- **A whole app or script:** keep a `.env` file of references, not values (safe to commit):
  ```
  META_ACCESS_TOKEN=op://Agents - Marketing/Meta Ads token/credential
  XERO_CLIENT_SECRET=op://Agents - Marketing/Xero app/client secret
  ```
  then run `op run --env-file=.env -- python3 report.py`. The secrets exist only inside that
  process, and `op run` masks them if they're printed (they show as `<concealed by 1Password>`).
  To use one in a shell command, wrap it so your shell doesn't expand it first:
  `op run --env-file=.env -- sh -c 'curl -H "Authorization: Bearer $META_ACCESS_TOKEN" ...'`
- **A config file that needs real values:** `op inject -i config.tpl -o config.yml`, and keep
  `config.yml` out of git.

In skills, always name the reference or the environment variable, never the value:
"uses `META_ACCESS_TOKEN` (from `op://Agents - Marketing/Meta Ads token/credential`)".

## Rules

- The agent never asks the user to paste a secret into chat. If a secret is missing, it tells the
  user which item to create in which vault, and waits.
- Never print, log or echo a secret. Check a value exists with `>/dev/null && echo ok`.
- Never write a secret to a file in a repo, a skill, a notebook or a `.env` with real values.
- Read-only by default. Never give a service account access to a vault it doesn't need.
- Never turn off two-factor or weaken a login to make automation easier.
- If a secret is ever exposed (pasted in chat, committed, shown in a log), treat it as leaked:
  rotate it at the provider, update the item in 1Password, and nothing else needs to change.

## Gotchas

- **"No accounts configured" or a sign-in prompt in a script:** `OP_SERVICE_ACCOUNT_TOKEN` isn't
  set in that shell. Scheduled jobs and new terminals don't inherit it; load it in the job itself.
- **"isn't a vault in this account" or "item not found":** the service account wasn't granted that
  vault, or the vault or item was renamed. References use names, so renaming breaks them. Prefer
  stable names, or use IDs in the reference (`op://<vault-id>/<item-id>/<field>`).
- **Names in references:** letters, numbers, `-`, `_`, `.` and spaces are fine (quote the whole
  reference if there's a space). Anything else, such as `&` or `/` in a name, must be referenced by
  ID instead. References are not case-sensitive.
- **Field names differ by item type:** an API Credential's value is `credential`, a Login's is
  `password`. Check with `op item get "<item>" --vault "<vault>" --format json` (as a person) and
  read the field labels, not the values.
- **Service account access is fixed at creation** (1Password calls it immutable). To add a vault
  later, create a new service account with the extra vault, swap the token, then delete the old one.
- **More than one vault:** if a service account can see several vaults, `op item` commands need
  `--vault`.
- **Usage limits** (per service account per hour, and per account per day):
  | Plan | Reads per hour | Writes per hour | Per day, whole account |
  |---|---|---|---|
  | Business | 10,000 | 1,000 | 50,000 |
  | Teams | 1,000 | 100 | 5,000 |
  | Individual, Families | 1,000 | 100 | 1,000 |

  Read each secret once per run, never inside a loop. Using IDs instead of names in references also
  cuts the number of requests.
- **Expired token:** everything fails at once on the expiry date. Rotate early and keep the expiry
  date in your calendar.
