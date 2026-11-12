# Setting up Plausible + Microsoft Clarity (agent-guided)

Follow this with the user when either service isn't set up yet. Work through it **one step at a
time**, confirm each step worked before moving on, and verify on the live site at the end.

## Rules for the agent
- **The user owns the accounts.** They sign up, log in, enter passwords, verify email and enter
  payment details. Never type a password, card number or one-time code for them, and never create an
  account on their behalf.
- **Driving a browser is fine for everything else** (Claude Code's browser, or Claude in Chrome):
  navigating to the right page, reading settings, clicking through menus, copying a snippet, and
  checking the live site. Pause and hand over whenever a login, payment or approval appears.
- **Never paste API keys or tokens into chat.** Ask the user to save each one into a file (e.g.
  `~/secrets/plausible_key.txt`) and point the config at the file. Never print them.
- Check for an existing account or tag first (step 0) before creating anything.

---

## Step 0: what already exists?
1. View the live homepage source (or fetch it) and search for `plausible.io` and `clarity.ms`.
2. Look for a **Content-Security-Policy** (a `<meta http-equiv="Content-Security-Policy">` tag, or
   the hosting's headers config). If one exists, both tools will be **silently blocked** until it
   allows them (P3 / C3).
3. Ask: which website platform? (WordPress, Shopify, Webflow, Squarespace, Wix, GoHighLevel, or
   custom code / Netlify / Vercel.) Most steps differ only in *where the snippet goes*.

---

## Plausible (traffic and conversions, cookieless)

**P1. Account and site.** User signs up at plausible.io (30-day free trial), then **Add website**
with the bare domain (`example.com`). Timezone = the business's local timezone. *Note:* the Stats
API (which this skill uses) needs the **Business** plan after the trial. Check Plausible's pricing
page with the user.

**P2. Install the snippet.** Plausible shows a site-specific snippet (`plausible.io/js/pa-….js` plus
a small init script). Put it in the `<head>` of **every page**:
- WordPress: the official Plausible plugin, or a header-scripts plugin
- Shopify: Online Store › Themes › Edit code › `theme.liquid`, before `</head>`
- Webflow / Squarespace / Wix / GoHighLevel: site-wide custom code › Head
- Custom code: the shared layout/head template. **Static sites with no shared template need every
  HTML file edited**: write a small idempotent script that inserts it before `</head>`.

**P3. Strict CSP? Use a same-origin loader.** If step 0 found a CSP, the inline init script is
blocked. Host the init code as a file on your own domain (e.g. `/plausible.js`: the init stub plus
code that appends the `pa-….js` script) and load that instead, then add `https://plausible.io` to
`script-src` and `connect-src`. Missing this silently loses data on exactly the pages that matter.

**P4. Verify (don't skip).** Open a live page in a browser and check that requests to
`plausible.io/js/pa-…js` and `plausible.io/api/event` happen (the event should answer 202). In the
browser console: `performance.getEntriesByType('resource').filter(e => /plausible/.test(e.name))`.
Preview/staging domains are not counted; test on the real domain.

**P5. Goals.** Site settings › Goals › Add goal:
- a **pageview** goal for each thank-you / success page (e.g. `/thank-you*`, `/success*`). Use a
  trailing `*`: many sites serve `/success` and `/success.html` for the same page.
- keep Plausible's automatic **Form: Submission** goal, which also catches forms that confirm on the same
  page. It counts attempts, including spam.
- Check the actual redirect URL each form uses before naming a goal (look at the form's code or
  submit a test).

**P6. Stats API key.** Account settings › API keys › New key › **Stats API**. The user saves it to
a file; set `PLAUSIBLE_API_KEY_FILE`. Test: `python3 scripts/report.py --days 1 --no-clarity`.

**P7. Privacy.** Plausible uses no cookies and stores no personal data, so it needs no consent
banner on its own. Add a line to the privacy policy that the site uses Plausible for anonymous
statistics. (Other tools on the site, like Clarity or ad pixels, may still need disclosure or
consent depending on the country: not legal advice.)

---

## Microsoft Clarity (heatmaps, recordings, frustration signals; free)

**C1. Project.** User signs in at clarity.microsoft.com (Microsoft, Google or Facebook login) ›
**Add new project** › name + site URL. Note the project ID (letters/numbers in the tag).

**C2. Install.** Settings › Setup › install manually: a small script in `<head>` of the pages you
want recorded (all pages, or just landing/funnel pages). Platform plugins exist for WordPress,
Shopify, Wix. Only run it on the live domain if previews would pollute the data.

**C3. Strict CSP? Same pattern.** Host the loader on your own domain (e.g. `/clarity.js`) and add
`https://www.clarity.ms https://scripts.clarity.ms` to `script-src`, and `https://*.clarity.ms
https://c.bing.com` to `connect-src` and `img-src`.

**C4. Privacy settings (important).** Settings › Masking: choose **Strict** (masks all text and
form input in recordings). Booking calendars or forms embedded in iframes can carry names and emails
in their address; strict masking blanks them. Clarity uses cookies and records sessions, so disclose
it in the privacy policy, and use a consent banner where the law requires (EU/UK, some US states).

**C5. Verify.** On the live site, requests to `www.clarity.ms/tag/<id>` and `j.clarity.ms/collect`
appear. The Clarity dashboard shows the first recordings within about 2 hours.

**C6. Data Export API token.** Settings › Data Export › Generate new API token. The user saves it to
a file; set `CLARITY_TOKEN_FILE`. **Limits:** 10 reads per day for the whole project, and only the
last 1 to 3 days are returned. That's why history is stored daily (`snapshot.py`) and the on-demand
report can skip the live read (`--no-clarity`).

---

## H. History (so reporting works over months)
1. Choose a store: `sqlite:/path/analytics.db` (no setup) or Supabase/Postgres (run
   `references/history-tables.sql` first).
2. Schedule `python3 scripts/snapshot.py --config site.env` daily just after midnight (cron, Hermes
   schedule, Railway, GitHub Actions). Clarity uses one of its 10 daily reads.
3. Backfill Plausible from the day it was installed: `--from YYYY-MM-DD --to YYYY-MM-DD`. Clarity
   can't be backfilled.

## Done when
- Both tools fire on the live site (P4, C5), goals exist (P5), keys are saved as files (P6, C6),
- `report.py` runs clean, and the snapshot is scheduled (H).
