---
name: google-ads-conversions
description: >-
  Set up, audit, or repair Google Ads conversion tracking end to end. Use when asked to "set
  up Google Ads conversion tracking", "Google Ads isn't tracking conversions", "no recent
  conversions", "AW- tag not firing", "enhanced conversions", or "conversion action needs
  attention". Fix this BEFORE any ad spend — a campaign with broken tracking spends blind and
  the data cannot be backfilled. Covers: proving tag ownership, finding conversions that are
  configured but never fire, the redirect-parameter pattern for multi-form thank-you pages,
  primary vs secondary action setup, Enhanced Conversions, and tag diagnostics.
---

# Google Ads Conversion Tracking

**Do this BEFORE any spend.** Broken tracking means real money spent with zero optimisation signal,
and the data cannot be backfilled.

## Phase 0 — who owns the tag?

Find the tag on the site: `grep -rhoE "AW-[0-9]{9,}" *.html | sort -u`

Prove ownership: Google Ads → Goals → Conversions → action → Manage → See event snippet.
The snippet shows `AW-XXXXXXXXX/LABEL`. If that AW- matches the site AND you can see it in an
account you control — you own it.

Do not assume. The site can carry an agency's Google tag while the Meta pixel is yours (or vice versa).
Verify each independently.

## Phase 1 — the audit that finds the real bug

A conversion action existing in the UI proves nothing. Verify the code path separately:

**Is the label ever CALLED, or only DEFINED?**
```bash
grep -rn "AW-XXXXXXXXX/" --include=*.html .     # where the label appears
grep -rn "gtag_report_conversion" --include=*.html .   # defined vs invoked
```
Google's snippet often ships as a `gtag_report_conversion()` function. A page can define it and
never call it.

**Is the label VALID?** Real labels are ~20 chars of mixed case (e.g. `uunuCK-l2YkcEOfs1pBD`).
A human-readable string like `AW-123/application_submitted` is NOT a real label — it silently
fires into nothing.

**Where does the form ACTUALLY redirect?** Read the form handler's redirect, don't assume. A
site can have a fully-wired `application-submitted.html` that nothing ever redirects to, while
the real landing page (`success.html`) has no Google tag at all.

**Does the landing page have the gtag BASE?** The conversion snippet does nothing without
`gtag/js?id=AW-…` on the same page.

Symptom of all this: the action shows **"Needs attention / No recent conversions"** since
creation. It has never once fired and, as wired, never could.

## Phase 2 — implementation: redirect-parameter pattern

One thank-you page, multiple form types — don't clone the page, tag the redirect:

```js
// netlify/functions/form-submit.js
const redirectTo = (t) => ({ statusCode: 302, headers: { Location: `/success.html?t=${t}` }, body: "" });
// ONLY on a real, successful insert:
return ok ? redirectTo("enquire") : REDIRECT_UNTAGGED;
```

Only the success path gets the `?t=` parameter. Spam blocks, dedup skips, failures stay untagged
and can never be counted as conversions. This is what keeps the numbers honest.

```html
<!-- success.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date()); gtag('config', 'AW-XXXXXXXXX');

  var LABELS = { enquire: 'uunuCK-l2YkcEOfs1pBD', talent: 'qnhhCO78wNQcEOfs1pBD' };
  try {
    var t = new URLSearchParams(window.location.search).get('t');
    var label = t && LABELS[t];
    if (label) gtag('event', 'conversion', { send_to: 'AW-XXXXXXXXX/' + label, value: 1.0, currency: 'AUD' });
  } catch(e) {}
</script>
```

**Never fire a placeholder label.** If an action doesn't exist yet, leave the entry `null` with
a TODO.

**Watch the meta refresh.** Thank-you pages with `<meta http-equiv="refresh" content="3;url=/">`
are fine — gtag uses `navigator.sendBeacon` which survives navigation.

## Phase 3 — creating the conversion action

Goals → Conversions → + New conversion action:

- **Data sources:** tick "Conversions on a website" ONLY. Do NOT tick "Conversions from phone
  calls" unless you want a dynamic forwarding number injected into your site (breaks NAP
  consistency across site / GBP / socials).
- **Category:** "Submit lead form" — for ANY form submission (enquiry, quote request, booking).
- **Create manually with code** (not "automatically without code"). Automatic misfires on
  redirect-based flows.
- **Page load, not Click.** Click fires before the insert — it counts spam, dedup-skips, and
  failed writes. Page load on the thank-you page = write succeeded.
- **Name it distinctly.** Default names collide with existing actions.
- **Primary vs Secondary:** only the action you want to BUY should be primary. If a cheap
  secondary action (newsletter signups, job applications) is primary alongside real enquiries, Smart Bidding drifts spend
  toward the cheap traffic while reporting looks fine.
- **Count: One** (not Every — Every is for purchases).
- **Click-through window: 30 days** (90 over-credits ads for conversions they didn't drive).
- **Attribution: Data-driven.**

Demote or remove leftovers (e.g. a "Google hosted" lead-form action). Prefer demoting to
Secondary over deleting — **deleting discards conversion history permanently.**

## Phase 4 — Enhanced Conversions

Goals → Conversions → Settings → Enhanced Conversions → on, method "Google tag".

Google's equivalent of Meta's Automatic Advanced Matching. Hashes email/phone from form fields
to recover cross-device conversions. Requires the Google tag on the page collecting the data.

## Phase 5 — verification

**Tag coverage check:**
```bash
for f in $(find . -name "*.html" -not -path "./node_modules/*"); do
  grep -q "AW-XXXXXXXXX" "$f" && echo "TAGGED   $f" || echo "UNTAGGED $f"
done
```

**"Additional domains detected"** — usually build preview URLs (`<hash>--site.netlify.app`).
Do NOT accept suggestions to add preview URLs (cross-domain linking adds `_gl=` params to links
to listed domains; throwaway URLs regenerate endlessly). DO fix a real `www`/apex split.

**Does firing on every submission inflate Google's numbers?** No. Google only counts a conversion
it can tie to an ad click via the `_gcl_aw` GCLID cookie. Organic/TikTok/Meta leads fire the
beacon and are discarded, not counted. Do NOT gate the conversion on a cookie or `lead_source`.

**Status notes:**
- Brand-new action shows "Inactive" until its first conversion — not broken
- Repaired action keeps "No recent conversions" until the first real one lands — not broken
- Diagnostics lag 24-48h after a fix

**Live verify:**
```bash
curl -s https://site/success.html | grep -cE "gtag/js\?id=AW-|<LABEL>"
```

An end-to-end test submit writes a real CRM row and can trigger outreach — get approval, then
delete the test row.

## What to ask the business owner before starting

- What's the Google Ads account number?
- What AW- tag is currently on the site (run the grep)?
- What forms need to be tracked, and which one should be Primary?
- What's the thank-you page path and the form handler file?
