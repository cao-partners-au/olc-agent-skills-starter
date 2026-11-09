---
name: meta-pixel-funnel
description: >-
  Set up or repair an IN-HOUSE Meta (Facebook/Instagram) pixel + Conversions API lead funnel.
  Use when asked to "set up the Meta pixel", "wire up Meta CAPI", "Facebook pixel not tracking",
  "why is my Lead event not showing in Events Manager", or "set up in-house Meta ads separate
  from my agency". Covers pixel creation, CAPI token setup, sealed landing funnel clone,
  server-side Lead events with event_id dedup, CRM attribution, and verification. Examples assume a
  static host plus a hosted Postgres; adapt file paths for other stacks.
---

# Meta Pixel + Conversions API Funnel

## Before you start — check who owns the existing pixel

Run this first: `grep -rhoE "fbq\('init', *'[0-9]+'\)" *.html | sort -u`

If it's an agency's pixel, keep theirs on the base pages and build a SEPARATE in-house funnel
on a sealed clone path. Never mix pixels on shared pages.

## Phase 0 — ad account ownership

- Create the ad account INSIDE your Business portfolio: Business Settings → Accounts → Ad
  Accounts → Add → **Create a new ad account**. Do NOT add an existing account — moving
  ad accounts between businesses is restricted and sometimes irreversible.
- Currency and timezone are PERMANENT. Set them right.
- Confirm you hold **Full control** (People tab on the ad account).

## Phase 1 — create the pixel (Meta calls it a "dataset")

Meta renamed pixels to datasets. Dataset ID = Pixel ID.

1. Events Manager → Connect data sources → Web → Meta Pixel → name it → Create
2. Grab the Dataset/Pixel ID (~15 digits). It is non-secret — it goes in client HTML.
3. Setup method → **"Install code manually"**. Skip the code screen; you only need the ID.
4. Turn ON **Automatic Advanced Matching** — hashes form fields client-side, lifts match rate.

## Phase 2 — Conversions API token (the maze)

Dataset → Settings → Conversions API → **Set up direct integration** → "Set up with Dataset
Quality API (recommended)".

**Tick ONLY your own dataset.** Ticking an agency's pixel grants write access to their data.

Generate access token → store as a server-side env var or in a secret manager (on hosts like Netlify or Vercel, mark it as a secret so it is never exposed to the browser bundle). Never
paste it in chat. It only appears in the serverless function so the secret scanner won't reject it.

**Dead ends to skip (each wastes an hour):**
- "Set up with Google Tag Manager" — only if you use GTM
- "Set up with Meta (one-click)" — doubles up with your server events, sends weaker data
- "Send integration instructions to a developer" — just emails boilerplate; the token is in
  Settings, not that wizard

## Phase 3 — sealed funnel + code

Clone the base hub + form to `[FUNNEL_PATH]/[SUFFIX]` and `[FUNNEL_PATH]/form/[SUFFIX]`, then:

- Swap `fbq('init','AGENCY_PIXEL_ID')` → `fbq('init','YOUR_PIXEL_ID')` — leave a comment naming both
- Add hidden `lead_source="[YOUR_LEAD_SOURCE]"` to the form
- Keep existing `fb_event_id`, `fb_fbp`, `fb_fbc`, `fb_source_url` hidden fields
- Repoint all CTAs to the channel form; repoint form's logo/back-link to channel hub
- **No Cloudflare Turnstile on ad-funnel forms** — in-app browsers (especially TikTok) frequently
  fail it and you silently lose every paid lead

**Meta needs LESS code than TikTok:** the shared `lead-form.js` already handles Meta browser
Lead events with event_id. The pixel auto-captures `fbclid → _fbc` cookie. No extra JS needed.

**Server (form-submit.js):** clone `sendMetaLeadEvent` into `sendYourMetaLeadEvent` with your
pixel + token, then make routing mutually exclusive:

```js
if (ok && lead_source === "TikTok")           await sendTikTokLeadEvent(...);
else if (ok && lead_source === "[YOURS]")      await sendYourMetaLeadEvent(...);
else if (ok)                                  await sendMetaLeadEvent(...); // agency, unchanged
```

Key payload: `event_id = fields.fb_event_id || randomUUID()`, `action_source: "website"`,
hashed `em/ph` + raw `fbp/fbc/client_ip_address/client_user_agent`.

Exclude the sealed ad pages from `sitemap.xml` — they'd compete with the public page in search.

## RULE: never fire real conversion events to test page behaviour

Testing a form or thank-you page on the LIVE site sends real Lead events to the ad platforms. They
count as genuine conversions, pollute optimisation and can't be deleted. Test on a preview/staging
URL where the server suppresses platform events, or use the platform's Test Events code (and check
the response says the test code is active: a stale code makes the platform process the event as
REAL). Delete any test leads from the CRM afterwards.

## Phase 4 — verification

1. On most static hosts, env vars only take effect on the next deploy — push an empty commit after setting the token
2. **Server CAPI events do NOT appear in the Test Events tab by default** — they go straight to
   the live dataset. Their absence from Test Events is correct, not a failure.
3. Test Events works for proving the browser pixel (PageView appears in seconds)
4. Only a real LIVE event (Test Events tab closed) flips the pixel to "ready" — allow ~30 min
5. Success looks like: `Meta pixel ✅ + Conversions API ✅` in Integrations, `Lead` with an Event
   Match Quality score (8.0+ is strong)

After verifying: delete the test lead row from the CRM so it doesn't trigger outreach.

## Gotchas

- `Low coverage of fbc through Conversions API` — benign. Real ad clicks populate it automatically.
- `Missing commerce events (Add to cart / Purchase)` — irrelevant for lead-gen funnels. Ignore.
- Ads about jobs, housing, credit/finance or social issues fall under a Meta **Special Ad Category** — restricts
  age/gender/interest targeting. Plan creative and audience accordingly.
- Always `diff` sealed pages against the base before editing again — concurrent restyling causes drift.

## What to ask the business owner before starting

- What's the domain and funnel path?
- Is there an existing agency Meta pixel on the site?
- What should the `lead_source` value be (e.g. "Meta", "Meta-Inhouse")?
- Which host serves the site, and where do leads get written?
