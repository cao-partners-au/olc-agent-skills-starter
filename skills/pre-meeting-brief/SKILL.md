---
name: pre-meeting-brief
description: Fast business brief on a company before a meeting or call, from just a name or website. Researches the site, the ABN register, reviews and LinkedIn, then produces a one-glance brief of what they do, where the opportunities are, and the angle for your conversation. Use when asked "meeting in 10 minutes with these guys", "quick brief on [company]", "look up [company] before I jump on a call", "prep me for this meeting", or "board presentation prep for [company]".
---

# Pre-meeting brief

The outcome: a brief you can glance at and talk from, ready in a couple of minutes. Time pressure
is always implied, so speed matters more than depth unless the user asks for a full workup.

## Before you start

- Check what you already know: your CRM, inbox or meeting notes for the company and the person
  (past calls, emails, deal stage). Thirty seconds here often tells you who you're meeting and
  what has already happened.
- If the company name could be more than one business, confirm which one first (see Gotchas).

## How to do it

1. **The website:** home, about, and one or two operational pages (services, products, ordering,
   catering, bookings). Extract the business model, locations, team-size signals, how they make
   money, and where customers touch the business.
2. **ABN Lookup** (Australian businesses): search
   `https://abr.business.gov.au/Search/ResultsActive?SearchText=<company+name>`. It shows the legal
   entity name (often different from the trading name), registration date (age and maturity),
   GST status, and how many entities are registered. The results list only shows ABN, name and
   postcode; open the ABN's own page for the full record. Always do this before an ABN goes into
   anything contractual.
3. **Google reviews:** star rating, review count and price range. A high review count signals real
   customer volume.
4. **LinkedIn:** the founder or the person you're meeting, and the company page.
5. **Stop at 4 to 5 lookups** for a quick brief. ABN Lookup is fast and high-signal; do it before
   LinkedIn if time is short.

## Output (fixed format, bullet points only)

**[Company name]: quick brief**

- **What they are:** business type, locations, product or service, price point, positioning.
  Concrete specifics only.
- **Opportunities:** three or four groups, each with a bold heading and two or three specific
  points tied to what you actually found (not generic "AI can help with X").
- **The angle for your conversation:** one or two lines on what will land with this person and
  how to frame it. This is the most valuable line; never skip it.

If the user asks for it "briefer", drop all prose: one line per point, grouped tightly by topic.

Prompts for the opportunities section (use what fits, not as a checklist):
**Operations** (forecasting, scheduling, inventory, supplier communication, rostering),
**Customers and revenue** (reorders, upsells, loyalty, follow-up, bookings),
**Sales** (quotes, follow-up sequences, lead qualification),
**Marketing** (content, social, campaigns, seasonal promotions),
**Admin** (payroll prep, compliance documents, onboarding, reporting).

## Board or investor meeting (extended format)

When it's a board-level presentation rather than a first call, go further:
1. Research the likely attendees by name. Founders and professional directors object differently.
2. Map their tech stack to your specific use cases.
3. Identify their competitive pressure points, and frame your offer as defence, not an optional
   upgrade.
4. Prepare short, word-for-word answers to the CFO and COO questions (return on investment, risk,
   cost, build versus buy).
5. Use real proof points with real numbers, not hypotheticals.
6. Open with a frame that creates urgency without hype.

## Signals worth calling out

- **Two or more entities at the same postcode, registered years apart:** usually a deliberate
  restructure (for example, separating retail from events). The newer entity is often the growth
  arm. More entities means more operational surface area. Name both in the brief.
- **A broken website** (pages returning 404, a dead social feed, missing service pages): their
  digital side is neglected or outgrown and there's likely no dedicated tech person. Use it as a
  gentle opener ("your events page isn't loading; are enquiries coming in by phone?"), not a
  criticism.
- **Self-reported company size:** treat a form's "500+ staff" for a small business as unverified.
  Ask on the call whether that includes casuals and contractors.

## Rules

- Never pad with background the user doesn't need. Bullet points, not paragraphs.
- Never invent facts, figures or names. If the website is thin, say the brief is limited.
- Note anything you couldn't see (collapsed FAQs, pages that wouldn't load) rather than presenting
  a partial crawl as complete.

## Gotchas

- **Ambiguous names:** search the name alone first. If two unrelated businesses share it, ask the
  user which one before researching. Guessing wastes the whole pass.
- **Guessed URLs:** a guessed page path can return a 404 that still shows the site's normal header
  and footer, which looks like a real but thin page. Take links from the site's own navigation, and
  check the page heading isn't "404".
- **For "look at everything" requests:** use a real browser tool rather than a single-page fetch,
  and expect five to eight page loads. Content inside collapsed sections or loaded by scripts often
  won't appear in the page text; say so in the brief.
