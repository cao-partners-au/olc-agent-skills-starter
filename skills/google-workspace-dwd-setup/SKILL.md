---
name: google-workspace-dwd-setup
description: "Set up Google Workspace and Domain-Wide Delegation (DWD) from scratch for a business migrating off Microsoft 365 / Exchange. Covers domain verification, admin console setup, creating a GCP service account, authorising DWD scopes, and the working auth/scope patterns for Calendar, Gmail, Sheets, and Drive that avoid the common unauthorized_client traps. Use when standing up GWS for the first time, migrating mailboxes/calendars from Microsoft, or building any script/agent that needs to act on behalf of Workspace users via a service account."
tags: [google-workspace, dwd, migration, microsoft-365, service-account, gmail, calendar, drive]
related_skills: [native-mcp]
---

# Google Workspace + Domain-Wide Delegation Setup (Microsoft 365 Migration)

A from-scratch guide for standing up Google Workspace for a business that's currently on Microsoft 365 / Exchange, and configuring Domain-Wide Delegation (DWD) so a service account (or an AI agent) can act on behalf of Workspace users, sending email, managing calendars, reading Drive files, editing Sheets, all under proper authorisation, not personal OAuth per user.

*Skeleton - no credentials or company-specific values are included. Replace every `{{PLACEHOLDER}}` with your own.*

---

## Part 1: Setting Up Google Workspace (first time)

### Step 1 - Sign up and verify your domain

1. Go to `workspace.google.com` and start a trial with your existing domain (e.g. `{{YOUR_DOMAIN}}`).
2. **Domain verification** is required before you get full admin control. Google gives you a TXT or CNAME record to add at your domain registrar (GoDaddy, Namecheap, Cloudflare, whoever hosts your DNS today).
   - If you're migrating from Microsoft 365, your MX records currently point to Microsoft (`*.mail.protection.outlook.com`). You will change these to Google's MX records **only once mail migration is complete and tested** - don't cut over on day one.
3. Once verified, you're the Super Admin of a real Google Workspace organisation at `admin.google.com`.

### Step 2 - Create user accounts

- **Admin console -> Directory -> Users -> Add new user.** Create one account per person, matching their existing `{{name}}@{{YOUR_DOMAIN}}` addresses from Microsoft 365 so email addresses don't change for external contacts.
- Assign licenses (Business Starter/Standard/Plus, or Enterprise) per user under **Billing**.
- Set temporary passwords and require a reset on first login, or push SSO if you already run a separate identity provider.

### Step 3 - Migrate mail, calendar, and contacts from Microsoft 365

Google's own tool for this is **Google Workspace Migration for Microsoft Exchange (GWMME)** or, for larger/more complex migrations, **Data Migration Service** built into the Admin console (**Admin console -> Data migration**).

- **Data Migration Service (recommended for most SMB migrations):** Admin console -> Data migration -> Email/Calendar/Contacts -> connect via Microsoft 365 admin credentials (needs an app-only Azure AD app registration with `Mail.Read`, `Calendars.Read`, `Contacts.Read` delegated or application permissions, similar concept to DWD on the Google side, just the Microsoft equivalent). Google migrates historical mail into each user's Gmail inbox.
- **What does NOT migrate automatically:** Outlook rules/filters, Teams chat history, SharePoint document libraries (migrate those separately via **Drive migration tooling** or a third-party tool if you have a lot of SharePoint content), and any custom mail flow rules on the Exchange side.
- **Sequence that avoids mail loss:** (1) verify domain, (2) create users, (3) run Data Migration Service for mail/calendar/contacts while MX still points to Microsoft, (4) let it run and re-sync close to cutover, (5) switch MX records to Google, (6) do a final short re-sync to catch anything sent during the cutover window, (7) decommission the Microsoft 365 tenant once everyone has confirmed their data is present.

### Step 4 - Decide on the service account / DWD approach early

If you (or an agent, or an internal tool) need to act on behalf of users programmatically, this is the point to plan for it, not an afterthought. See Part 2.

---

## Part 2: Setting Up a Service Account + Domain-Wide Delegation

DWD lets a single service account **impersonate** any user in your Workspace domain for specific, admin-approved API scopes, without that service account needing its own mailbox or the user needing to individually grant OAuth consent every time. This is the correct pattern for an AI agent, an internal automation, or any script that needs to send email as a real person, read/write their calendar, or touch their Drive files.

### Step 1 - Create a Google Cloud project

1. Go to `console.cloud.google.com` -> create a new project (e.g. `{{YOUR_COMPANY}}-automation`).
2. Note the **Project ID** (e.g. `{{YOUR_COMPANY}}-123456`, Google appends a random suffix) - you'll need it later.

### Step 2 - Enable the APIs you need

**APIs & Services -> Library**, enable each API your automation will touch:
- Gmail API
- Google Calendar API
- Google Sheets API
- Google Drive API
- Google Docs API (if editing Docs)

This step is genuinely required once, up front. It is **not** a recurring troubleshooting step - if a script fails later with an auth error, the API being disabled is rarely the actual cause once you've done this properly the first time (see Part 3's debugging checklist).

### Step 3 - Create the service account

1. **IAM & Admin -> Service Accounts -> Create Service Account.**
2. Name it something identifiable (e.g. `{{YOUR_COMPANY}}-automation-api`).
3. Skip granting it project-level IAM roles unless you specifically need them - DWD authorisation (next step) is what actually grants it access to user data, not IAM roles.
4. **Create a key** (JSON format) for this service account and download it. This JSON file is a genuine secret - treat it like a password. Store it outside any public repo, and reference it by absolute file path in scripts, never paste its contents into chat, a ticket, or a shared doc.
5. Note the **Client ID** (a long numeric string, e.g. `123456789012345678901`) - this is what you'll authorise for DWD, not the service account email.

### Step 4 - Authorise Domain-Wide Delegation in the Admin console

This is the step that actually grants power, and it must be done by a Google Workspace **Super Admin**, not just anyone with GCP access.

1. **admin.google.com -> Security -> Access and data control -> API controls -> Domain-wide delegation.**
2. **Add new** -> paste the **Client ID** from Step 3 (numeric, not the service account email).
3. Add the **OAuth scopes** you'll need, comma-separated, as full scope URLs. A reasonable starting set for a general-purpose automation:

```
https://www.googleapis.com/auth/gmail.modify,
https://www.googleapis.com/auth/gmail.settings.basic,
https://www.googleapis.com/auth/calendar,
https://www.googleapis.com/auth/drive,
https://www.googleapis.com/auth/spreadsheets
```

4. **Authorise.** This takes effect within a few minutes, sometimes up to a few hours per Google's own documentation, but in practice it's almost always immediate.

**This is a one-time setup step per scope set.** Once done, it does not need to be revisited every time a script has an auth error, see the debugging checklist in Part 3 before assuming DWD configuration is the problem.

---

## Part 3: Working Auth Patterns (the part everyone gets wrong)

These are the actual working scope/auth patterns, hard-won from real DWD debugging. **The single biggest time-sink in DWD work is assuming a readonly scope will work when it silently doesn't.**

### The core rule: use full scopes, not readonly, for DWD impersonation

For Calendar, Drive, and Gmail specifically, the `.readonly` variant of a scope frequently fails with `unauthorized_client` under DWD impersonation, even when the DWD authorisation is correctly configured. This is a real, repeatedly-confirmed pattern, not a one-off bug:

| Service | Use this scope | NOT this |
|---|---|---|
| Calendar | `https://www.googleapis.com/auth/calendar` | ~~`calendar.readonly`~~ |
| Drive | `https://www.googleapis.com/auth/drive` | ~~`drive.readonly`~~ |
| Gmail (general access) | `https://www.googleapis.com/auth/gmail.modify` | ~~`gmail.readonly`~~ for most use cases |
| Sheets | `https://www.googleapis.com/auth/spreadsheets` | (readonly is fine here if you genuinely only need to read) |

**Exception:** Sheets read-only genuinely works fine as `spreadsheets.readonly` in most cases - this specific failure pattern is most consistently seen on Calendar, Drive, and Gmail.

### Python auth pattern (Calendar, via DWD impersonation)

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY_FILE = '/absolute/path/to/your-service-account-key.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']  # full scope, not .readonly

creds = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES, subject='{{user}}@{{YOUR_DOMAIN}}'
)
cal = build('calendar', 'v3', credentials=creds)
```

### Python auth pattern (Sheets - no impersonation needed)

```python
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
sheets = build('sheets', 'v4', credentials=creds).spreadsheets()
```

**Important: do NOT add `.with_subject(...)` for Sheets.** Sheets access works via the service account being a direct collaborator on the sheet (share the sheet with the service account's email address, found in the JSON key file as `client_email`), not via DWD impersonation. Adding a subject causes `unauthorized_client` on Sheets specifically.

### Python auth pattern (Gmail, via DWD impersonation)

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES, subject='{{user}}@{{YOUR_DOMAIN}}'
)
gmail = build('gmail', 'v1', credentials=creds)
```

### Python auth pattern (Drive, via DWD impersonation)

```python
SCOPES = ['https://www.googleapis.com/auth/drive']  # NOT drive.readonly
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES, subject='{{user}}@{{YOUR_DOMAIN}}'
)
drive = build('drive', 'v3', credentials=creds)
```

### Setting a Gmail signature via the API (a genuinely separate scope)

Writing a Gmail signature via `sendAs().patch()` requires its own scope, and `gmail.modify` alone will NOT cover it:

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.settings.basic']
creds = service_account.Credentials.from_service_account_file(
    KEY_FILE, scopes=SCOPES, subject='{{user}}@{{YOUR_DOMAIN}}')
gmail = build('gmail', 'v1', credentials=creds)

gmail.users().settings().sendAs().patch(
    userId='me',
    sendAsEmail='{{user}}@{{YOUR_DOMAIN}}',
    body={'signature': signature_html}
).execute()
```

`gmail.modify` returns a 403 `insufficientPermissions` on this specific call - it's a genuinely separate scope from general mail read/send/modify access.

### Signatures are not auto-appended on API-sent mail

If you send or draft mail via the Gmail API (rather than a human typing in the Gmail web UI), **the user's configured signature is not automatically appended.** You must fetch it and append it yourself:

```python
send_as = gmail.users().settings().sendAs().list(userId='me').execute()
signature_html = ''
for entry in send_as.get('sendAs', []):
    if entry.get('isDefault'):
        signature_html = entry.get('signature', '')
        break

body_html = f"<div dir='ltr'>{your_html_body}<br><br>{signature_html}</div>"
```

Use `MIMEMultipart('alternative')` with both a plain-text and an HTML part when constructing the message, and attach the combined HTML body (with signature) as the HTML part.

### Signature images: use a hosted URL, not inline `cid:` attachments

If a signature includes a logo, host the image (Google Drive with public link-sharing, or any public URL) and reference it with a plain `<img src="https://...">` tag. Inline `cid:` image references are frequently blocked or rendered as a phantom attachment on the recipient's side - hosted URLs render cleanly everywhere, in both API-sent mail and the Gmail web UI's own signature editor (**Insert image -> By URL**, never upload directly into the signature editor field).

---

## Debugging Auth Errors - the correct order of operations

When you hit `unauthorized_client` or any 401/403:

1. **Check the scope string is the full URI**, not a shorthand (`https://www.googleapis.com/auth/calendar`, not `calendar`).
2. **Check the subject email is a real, correctly-spelled user** in your domain. A typo fails silently with the same generic error.
3. **Check the key file path** actually resolves and is readable.
4. **Try the broader (non-readonly) scope** if a `.readonly` variant is failing - this fixes it more often than any other single change.
5. **Test the base service account without a subject** (drop `.with_subject()` entirely) - if even that fails, the key file itself is wrong or corrupted, not a scope/DWD issue.
6. **Only after all of the above fails**, revisit the actual DWD authorisation in `admin.google.com` to confirm the Client ID and scope list match exactly what your script is requesting - a scope typo in the DWD console entry (missing a comma, wrong casing) is a real, if less common, root cause.

**Do not treat "check Google Admin" as the default first response to an auth error.** In the overwhelming majority of real cases, once DWD has been correctly authorised per Part 2, subsequent auth failures are a script-side scope or subject mismatch, not a Workspace configuration regression. Debug the script first.

---

## Common Pitfalls Worth Knowing Before You Start

- **DWD authorisation changes can take a few minutes to propagate.** If you authorise a new scope and immediately test, a failure could just be propagation delay - wait a couple of minutes and retry before assuming it's broken.
- **Adding a new API scope later requires re-authorising DWD with the updated, full scope list** - the Admin console DWD entry holds one scope list per Client ID; you can't incrementally add a scope without re-pasting the entire list including the ones you already had.
- **Service account keys have no expiry by default** but can be revoked/rotated at any time from IAM & Admin -> Service Accounts -> Keys. If a script starts failing across the board with no other explanation, check whether the key was rotated or deleted.
- **One service account can serve your whole domain** - you don't need a separate service account per user or per API. Scope it broadly at setup and reuse it.
- **Calendar "other people's calendars" cannot be added via the UI '+' button for users other than yourself in some Workspace configurations** - use the `calendarList().insert()` API call (impersonating the target user) to programmatically add a colleague's calendar to someone's view if the UI path doesn't expose it.

## Your setup - fill this in

| Placeholder | What it is | Where to find/set it |
|---|---|---|
| `{{YOUR_DOMAIN}}` | Your company's domain (e.g. `example.com`) | Your DNS registrar / existing email domain |
| `{{YOUR_COMPANY}}` | Your company/project name, used for naming the GCP project and service account | Your own |
| Service account key file | The downloaded JSON credentials file | GCP Console -> IAM & Admin -> Service Accounts -> Keys |
| Client ID | Numeric ID of the service account, used for DWD authorisation | GCP Console -> Service Accounts -> click the account -> Details |
| `{{user}}@{{YOUR_DOMAIN}}` | The real Workspace user being impersonated for a given script | Your own user directory |

Related: `native-mcp` (for connecting Google Workspace access via MCP servers instead of hand-rolled service account scripts, if you'd prefer that architecture).
