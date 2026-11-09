---
name: google-ads-campaign-launch
description: >-
  Build and launch a Google Search campaign end to end in the current (2026) UI. Use when asked
  to "set up a Google Ads campaign", "launch Google Search ads", "my Google ads get no
  impressions", "eligible (limited)", "missing enough relevant keywords", or "what keywords
  should I bid on". Covers demand validation (before spending), campaign structure, the settings
  that silently waste budget, negative keywords, ad groups + assets, and paid-vs-organic
  attribution. Fix conversion tracking first (google-ads-conversions skill) — a campaign without
  working tracking spends blind and data cannot be backfilled.
---

# Google Ads Search Campaign Launch

**Read google-ads-conversions skill first.** A campaign without working conversion tracking is
wasted spend. Fix measurement before building the campaign.

## Phase 0 — validate demand BEFORE building (everyone skips this)

Tools → Planning → Keyword Planner → Get search volume and forecasts. Paste every keyword.

Two columns to read:
- **Avg. monthly searches.** "10-100" is Google's LOWEST bucket and often means single digits.
  A dash means too low to report at all.
- **Top of page bid (low range).** This is the real entry price. Google's in-wizard forecast is
  optimistic — in one case it estimated $2.90 avg CPC while the Planner showed $5.82-$6.34 for
  the same terms. Trust the Planner.

**If your bid cap is below the top-of-page low range, you will get ~zero impressions.**
That is the #1 cause of "my campaign isn't spending" and it looks identical to "no demand".

**The strategic call:** Google Search only HARVESTS existing demand. If the Planner shows almost
no volume, you're creating a category, not competing in one. Demand CREATION (paid social,
content, outbound) has to come first. A small always-on campaign can still catch high-intent
searchers cheaply — just don't build a pipeline forecast on it.

## Phase 1 — the campaign wizard (2026 UI)

Screens in order: Objective → Bidding → Campaign settings → AI Max → Keyword and asset generation
→ Keywords and ads → Budget → Review.

- **Objective:** Leads. Type: Search.
- **Bidding:** "Clicks" + tick **Set a maximum CPC bid limit**. Do NOT accept Smart Bidding/tCPA
  with zero conversion history — switch after 15-30 conversions. Set cap from Planner's
  top-of-page bid, not from feel.
- **Customer acquisition / "Only bid for new customers":** leave OFF. Needs 100+ active audience
  members to identify existing customers.
- **Networks: untick Search partners AND Display.** Both default ON, both dilute intent.
- **Locations:** your country → open Location options → **"Presence: people in or regularly in
  your targeted locations."** The default "presence OR interest" shows ads to people overseas
  merely browsing about your country. Silent, expensive.
- **Audience segments:** none, leave "Observation" selected. Targeting narrows reach on a campaign
  already buying only a few clicks a day.
- **AI Max: SKIP.** Expands matching beyond your keywords, rewrites ad text, auto-selects landing
  pages, and strips attribution parameters.
- **Keyword and asset generation: SKIP.** Pre-fills the Final URL with your homepage (no
  attribution params) and generates broad off-brand keywords.
- **Campaign URL options: leave blank.** A tracking template applies ONE value across all ads,
  destroying per-ad-group attribution. A malformed one silently 404s every click while spend
  continues.
- **EU political ads:** No. Tick the account-wide box.
- **More settings:** Ad rotation = Optimise. Ad schedule = all hours initially. **Set a start date,
  leave end date EMPTY** — an end date is how campaigns silently stop.

## Phase 2 — keywords

**Match types are punctuation:** bare words are BROAD. Never paste an unquoted list.
Google pre-fills the keyword box with broad suggestions — **clear it entirely** before pasting yours.

Pair phrase + exact for your best terms — they're separate keywords, both belong in the same ad group:
- `"phrase match"` — catches longer real-world queries
- `[exact match]` — fires only on that phrase

**One ad group per landing page.** Keyword → ad → page relevance is what earns Quality Score and
cheaper clicks.

**Ad group type: Standard, not Dynamic.** Dynamic Search Ads crawl your site and pick landing pages
and headlines themselves — undoing attribution, positioning, and keyword control.

**Watch for keyword/negative collisions.** A negative always wins. Adding `"ai consultant for hire"`
while `consultant` is a campaign negative means it can never serve.

## Phase 3 — negatives (do immediately after publishing)

**Campaign level**, so it covers ad groups you haven't built yet. Tick "Save to new or existing
list" to make it reusable. Broad match type is correct for negatives — blocks any query containing
the word.

Find the ambiguity in your category first. Example, a commercial cleaning company:
`jobs job hiring salary vacancies careers course training certificate diy recipe homemade
products supplies equipment wholesale free template`

Build the equivalent list for your category: what word does a shopper for a totally different
thing type that contains your keyword?

## Phase 4 — ad groups 2+ and assets

The wizard creates only ONE ad group. Add the rest after via Campaigns → Ad groups → ⊕. Add each
ad separately under Ads (select the correct ad group in the top filter first — or the ad lands in
the wrong group).

**Assets (campaign level):**
- **Sitelinks:** full absolute URLs (`https://…`), not relative paths. Give each its own
  attribution slug (`?src=gads-sl-how`) to learn which sitelink converts. Min 2, 6 recommended.
  Leave Sitelink URL options blank — same tracking-template trap.
- **Callouts:** 6 max, 25 chars each, no links.
- **Display path:** 2 fields, 15 chars each — 19-char strings are rejected.
- **Call asset:** check whether an account-level one already exists before creating a duplicate.

**Call reporting on a call asset** = Google forwarding number IN THE AD ONLY. Does NOT touch
your website. Leave it ON — this is how calls from ads get counted as conversions.

**"Conversions from phone calls"** = injects a dynamic number INTO your site's HTML. Breaks NAP
consistency. Skip it.

Schedule the call asset to business hours — an unanswered ad-driven call is a wasted click.

## Phase 5 — attribution on shared landing pages

If SEO pages also serve paid traffic, paid leads report as organic without distinction.

Pattern:
- Ad final URLs carry `?src=gads-[theme]`; organic CTAs carry `?src=[page-slug]`
- Form JS maps `gads-` prefix → `lead_source="Google-Ads"`, everything else → `"Organic"`

**PAID MUST WIN ON COLLISION.** A paid visitor lands on `?src=gads-…`, then clicks the page CTA
to `/form?src=[page-slug]`. Without a guard, the second hop overwrites the paid slug and every
paid lead reports as organic. Refuse to downgrade a `gads-` cookie.

Google's `gclid` (auto-tagging in Admin → Account settings) and your `?src=` are complementary:
`gclid` tells Google which click converted; `?src=` tells your CRM which channel produced the lead.

## Phase 6 — after launch

- **"Eligible (Limited)" + "Missing enough relevant keywords"** = narrow reach. Do NOT click
  "Add keywords / Apply all" — it's a broad-match upsell. Fix with MORE VOCABULARY (synonyms as
  phrase match), not looser match types.
- **Zero impressions day one is normal.** Ads sit "Pending – under review" ~1 business day.
  "Bid strategy learning" lasts 1-2 weeks.
- **Search terms report daily for the first week** (Keywords → Search terms). This is where the
  waste is — pruning it is the highest-value 10 min/day.
- Don't judge anything before ~100 clicks.

## What to ask the business owner before starting

- What's the campaign goal (what conversion are we buying)?
- What's the daily budget?
- What landing pages exist (one ad group per page)?
- What's the top-of-page bid from the Planner? (Run Phase 0 first)
- Does the site already carry a Google AW- tag?
