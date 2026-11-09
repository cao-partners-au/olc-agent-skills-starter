---
name: ad-pixel-funnel
description: >-
  Set up a new ad-channel lead funnel for any channel — TikTok, Meta in-house, LinkedIn, or
  other. Creates a sealed, channel-separated landing funnel with a browser pixel + server-side
  Conversions/Events API, deduplicated by a shared event_id, with CRM lead attribution. Use
  when asked to "set up the [channel] pixel", "new [channel] ad funnel", "clone the hire funnel
  for [channel]", or "add [channel] conversions API". This is the generalised playbook — see
  meta-pixel-funnel for Meta-specific setup and tiktok-ads-mcp for TikTok campaign analysis.
---

# Ad-Channel Pixel Funnel (Generalised)

Builds a sealed, attributed ad funnel for any channel. Built end-to-end for TikTok. Reusable
for Meta in-house, LinkedIn, or any other channel with a pixel + server-side API.

## Core principles (non-negotiable)

1. **One sealed funnel per channel.** Each channel gets its own cloned pages under a path suffix
   (e.g. `/offer/tt` for TikTok, `/offer/mt` for Meta). A channel's pixel goes ONLY on
   its own pages — never shared/base pages, never site-wide.
2. **Seal the funnel.** In the cloned hub, repoint ALL internal CTAs to the channel form. In the
   cloned form, repoint the back-link + logo to the channel hub. A visitor must be unable to
   navigate from the channel funnel back to another channel's form.
3. **Pixel + server API with a SHARED event_id.** Browser fires the conversion with a generated
   event_id AND stamps it into a hidden field; the server sends the SAME event_id to the channel's
   API → the platform dedups. Better match quality, ITP/ad-block resilience, lower CPA.
4. **Channels are mutually exclusive server-side.** In `form-submit.js`, gate on `lead_source` —
   this channel fires ONLY this channel's server event. Everything else keeps firing unchanged.
5. **Clone = verbatim.** Channel pages are byte-for-byte clones except the named changes (pixel
   swap, lead_source, relinked paths). Diff to prove it. Note the drift risk.
6. **Backup before touching the live site.** `git tag`/branch the pre-change HEAD and push to origin.

## What to gather before starting

- Domain and base funnel path (e.g. `example.com`, `/offer`)
- Channel name and path suffix (e.g. `tt` for TikTok, `mt` for Meta in-house)
- lead_source value for CRM attribution (e.g. `TikTok`, `Meta`)
- Channel pixel/dataset ID (non-secret — goes in client HTML)
- Channel Events API access token (secret — goes in Netlify env var, never in chat or git)
- Server-side API endpoint and auth pattern (see reference table below)

## Phase 0 — recon + backup

Check the base hub is self-contained:
```bash
grep -oE 'href="/[^"]*"' [FUNNEL_PATH]/index.html | sort -u
```
Only exits should be the form CTA + a mailto + assets/anchors. If it links to the root site or
blog, the seal will leak — flag it before proceeding.

```bash
git tag -a backup-pre-[channel]-[stamp] -m "pre-[channel] funnel" && git push --tags
```

## Phase 1 — clone the funnel (no pixel yet)

**Form page** `[FUNNEL_PATH]/form/[sfx]/index.html` = verbatim copy of base form, then:
- Add `<input type="hidden" name="lead_source" value="[Channel]" />`
- Strip the OTHER channel's pixel block + its hidden fields (leave a comment placeholder)
- Repoint back-link + logo `href="[FUNNEL_PATH]"` → `[FUNNEL_PATH]/[sfx]`

**Hub page** `[FUNNEL_PATH]/[sfx]/index.html` = verbatim copy of base hub, then:
- Strip the other channel's pixel block
- Repoint ALL `href="[FUNNEL_PATH]/form"` → `[FUNNEL_PATH]/form/[sfx]`

**Verify the seal:**
```bash
diff [FUNNEL_PATH]/[sfx]/index.html [FUNNEL_PATH]/index.html  # only intended lines differ
grep -c 'href="[FUNNEL_PATH]/form"' [FUNNEL_PATH]/[sfx]/index.html  # must be 0
git status  # base pages must be unmodified
```

**Server** (`form-submit.js`): add `lead_source`/`lead_source_detail` to the insert, make the
existing server conversion event mutually exclusive:
```js
if (ok && fields.lead_source === '[Channel]') await send[Channel]LeadEvent(event, fields);
else if (ok) await sendMetaLeadEvent(event, fields);  // unchanged
```

Commit, push, verify live with curl (routes 200, channel pixel absent for now, base pages still
carry their own pixel).

## Phase 2 — pixel base code (browser)

Get the pixel base snippet + ID from the channel's Events Manager. Put the snippet in the `<head>`
of BOTH channel pages (hub + form). NOT the base pages, NOT site-wide.

Verify live: pixel present on both channel pages, absent on base pages; base pages still fire their
own pixel.

## Phase 3 — browser conversion event + click-id capture

Add a small `[channel]-lead.js`, loaded on BOTH channel pages:
- On load: capture the channel click-id from the URL (`ttclid` for TikTok, `fbclid` for Meta)
  into a first-party cookie so it survives hub→form navigation (the URL param is lost on click-through)
- On enquire submit: generate one `event_id`, stamp it + click-id + first-party cookie into hidden
  fields, then fire the browser conversion with that `event_id`

**Do NOT put Cloudflare Turnstile on ad-funnel forms.** In-app browsers (especially TikTok)
frequently fail it and you silently lose every paid lead.

Commit, push, verify: `node --check` the JS; live-curl confirms JS is served and form has hidden fields.

## Phase 4 — server Conversions/Events API

Add `send[Channel]LeadEvent(event, fields)` in `form-submit.js`:
- Reuse `hashPii` (email, lowercased + SHA-256) and `sha256(normalisePhone(phone))` (E.164)
- `event_id = fields.[ch]_event_id || randomUUID()` (never empty)
- Include click-id/cookie/ip/user_agent RAW
- Read the token from env: `process.env.[CH]_EVENTS_API_TOKEN`
- Best-effort + isolated in try/catch — must never block the redirect
- Optional `[CH]_TEST_EVENT_CODE` env → routes to Test Events

**Token handling:** the access token is a SECRET. Have the owner paste it into the host's env vars
(Netlify: Site config → Environment variables), marked "Contains secret values". NEVER in chat or git.

After setting any env var, **push an empty commit to force a redeploy** — env vars are read at
deploy time, not runtime.

## RULE: never fire real conversion events to test page behaviour

Testing a form or thank-you page on the LIVE site sends real Lead events to the ad platforms. They
count as genuine conversions, pollute optimisation and can't be deleted. Test on a preview/staging
URL where the server suppresses platform events, or use the platform's Test Events code (and check
the response says the test code is active: a stale code makes the platform process the event as
REAL). Delete any test leads from the CRM afterwards.

## Phase 5 — verify + flip to live

1. Set `[CH]_TEST_EVENT_CODE` in env → push empty commit to redeploy
2. Submit the channel form → confirm BOTH Browser and Server conversions appear with the SAME event_id
3. Confirm event_id placement via channel's Payload Helper (UI quirk: event_id may show BLANK in
   the Test Events panel but still be present — verify via Payload Helper and function logs)
4. Delete `[CH]_TEST_EVENT_CODE` → push another empty commit to redeploy
5. Do ONE clean LIVE submission (Test Events debugger closed) → allow ~30 min for Overview to update

Clean up the test lead row from the CRM (real row, can trigger outreach).

## Channel reference

| | TikTok | Meta (in-house) |
|---|---|---|
| Path suffix | `/tt` | `/mt` (or choose another) |
| lead_source | `TikTok` | e.g. `Meta` |
| Endpoint | `POST business-api.tiktok.com/open_api/v1.3/event/track/` | `POST graph.facebook.com/v21.0/{pixel}/events?access_token=` |
| Auth | Header `Access-Token: <token>` | `access_token` query param |
| Click-id URL param | `ttclid` | `fbclid` |
| First-party cookie | `_ttp` → `ttp` | `_fbp` → `fbp` (Meta auto-captures, no custom script needed) |
| Token env | `TIKTOK_EVENTS_API_TOKEN` | `META_CAPI_ACCESS_TOKEN` |
| Test code env | `TIKTOK_TEST_EVENT_CODE` | `META_TEST_EVENT_CODE` |

## Gotchas

- **Env vars need a REDEPLOY.** After setting or clearing, push an empty commit.
- **Marking env var "secret" triggers secrets-scanning** — build fails if the value appears in
  any published file. Safe for server-only creds. Pre-grep published files before marking anything
  that could also appear client-side.
- **Test events do NOT count toward "ready for campaign."** Only LIVE events flip the status.
- **The Test Events debugger MIRRORS browser events** — close it before the live check.
- **event_id can show BLANK in Test Events UI** even when present — use the Payload Helper.
- **Clones are point-in-time mirrors.** Always diff against the base before editing again.
- **Capture click-id to a cookie**, not just the URL — lost on hub→form navigation otherwise.

## Verification checklist

- [ ] `diff` clone vs base: only intended lines differ; base pages unmodified
- [ ] No bare `href="[FUNNEL_PATH]/form"` reachable from either channel page
- [ ] Channel pixel present on both channel pages, ABSENT on base pages; base pages still carry their own pixel
- [ ] `node --check` the JS and the function
- [ ] Host deploy published (function endpoint returns 405 to GET) = secrets scan passed
- [ ] Test Events: Browser + Server conversion with the SAME event_id
- [ ] event_id confirmed via Payload Helper
- [ ] After clean live submit: Overview shows conversion Active, Server source, status flips to ready (~30 min)
- [ ] Test lead cleaned from CRM
- [ ] Campaign set to optimise for the conversion event
