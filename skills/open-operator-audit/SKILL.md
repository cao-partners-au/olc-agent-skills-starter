---
name: open-operator-audit
description: >-
  Unified SEO + GEO (Generative Engine Optimisation) audit for websites. Use when asked to
  "audit [URL]", "run an SEO audit", "how visible is my site to AI", "check my GEO", "are we
  showing up in ChatGPT", or "compare me to [competitor URL]". Runs technical SEO, on-page SEO,
  GEO readiness checks, and live AI citation tests. Produces a prioritised fix list with
  paste-ready code. No paid SaaS required. Works for any country — AU conventions used by
  default (LocalBusiness schema, ABN), adapts to other locales when specified.
---

# Open Operator Audit

Unified audit for Google SEO and AI engine visibility (GEO). Runs the full check, produces a
short prioritised fix list with paste-ready code. No 200-item report noise.

## What to run (in order)

### Step 1 — Technical SEO

Fetch and analyse using `web_fetch`:

- `https://[domain]/robots.txt` — exists? any accidental bot blocks?
- `https://[domain]/sitemap.xml` — exists? referenced from robots.txt? URL count?
- `https://[domain]/` homepage — HTTP status, HTTPS redirect, response time, canonical tag
- A path that should 404 — confirm it returns a real 404 status

Score: X/10. List every issue with severity.

### Step 2 — On-page SEO

For homepage and any additional URLs specified:

- Title tag: present, unique, 50-60 chars
- Meta description: 120-160 chars, compelling
- Exactly one H1 per page, matches page intent
- H2/H3 hierarchy makes sense
- Image alt attributes
- Word count (flag thin pages under 300 words)
- Internal links count
- Mobile viewport meta tag
- JSON-LD structured data present and valid

Score: X/10.

### Step 3 — GEO readiness

**AI crawler blocking (highest-leverage check for small business sites):**

Fetch `robots.txt` and scan for:
`GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot, anthropic-ai, cohere-ai`

If ANY are blocked — lead with this. It's the single most common hidden issue. Provide the
exact robots.txt lines to fix it.

**Schema markup:**
- LocalBusiness (preferred for local/SMB — includes address, phone, hours, area served)
- Organization
- FAQPage
- Service/Product
- Review

Report which are present, which are missing, which are malformed. For AU: include ABN in
schema. For other locales, adapt business number + address format when told the country.

**E-E-A-T signals on About/Contact:**
Years in operation, owner/team names, certifications, physical address, contact phone,
business registration number, customer count, testimonials. Score each.

**Section self-containment:**
For each H2, check whether the content under it makes sense without the rest of the page.
Flag sections starting with "As mentioned above" or referring to prior context — AI models
cite self-contained sections and skip contextually-dependent ones.

**Content structure:** answer-first Q&A sections, section lengths (~120-180 words ideal),
FAQPage schema on Q&A blocks.

**llms.txt:** check for `https://[domain]/llms.txt`. Not a confirmed ranking factor, just a
completeness flag.

Score: X/10.

### Step 4 — Live AI visibility test

Generate 3-5 realistic buying-intent queries based on the business type and location. Examples:
- Plumber in Penrith: "best plumber in Penrith", "emergency plumber Western Sydney"
- Cafe in Fitzroy: "best cafe Fitzroy", "brunch spots Fitzroy Melbourne"

Use `web_search` to run each query and check:
- Does the business domain appear in results?
- Which competitors appear instead?
- What do cited competitors have that this site lacks?

For full AI engine tests (Claude, ChatGPT, Perplexity API calls): only run if the user has
provided API keys. If no keys provided, skip Step 4 and note it clearly — do not fake results.

Score: X/10.

### Step 5 — Prioritised fix list with draft code

Rank all issues from Steps 1-4:

**P0: do today.** High impact, low effort. Missing schema, blocked AI bots, missing meta
description, broken HTTPS redirect.

**P1: this week.** High impact, higher effort. New FAQPage sections, content rewrites, new
pages, internal linking structure.

**P2: when you have time.** Lower impact. Image alt improvements, minor internal linking.

For every P0 and P1, generate **paste-ready code** — not a description of what to do. Examples:
- Missing LocalBusiness schema → generate the JSON-LD with their actual business details
- Blocked AI bots → generate the exact robots.txt lines to change
- Missing FAQPage → draft the HTML + schema from real customer questions
- Title too long → suggest a tighter version that fits

## Output format

Always in this order:
1. One-line summary: "Audit of [domain] complete. Overall score: X/40."
2. Four sub-scores (Technical / On-page / GEO / AI Visibility) each X/10 with one-line reason
3. P0 fixes with paste-ready code under each
4. P1 fixes with paste-ready code under each
5. P2 fixes (short descriptions only, no code)
6. Offer to schedule a weekly re-audit cron

## Weekly re-audit

After the first audit, offer to schedule a weekly re-audit as an isolated OpenClaw cron:
- Schedule: Monday 8am AEST
- Mode: isolated agentTurn
- Prompt: re-run this skill on [URL], compare scores to last week, Telegram the business owner if anything
  changed or new P0 issues appeared

Use `cron(action=add)` with an isolated agentTurn payload if the business owner wants to set it up.

## Guardrails

- Never claim "you'll rank #1" or give specific traffic predictions
- Always distinguish between observed (crawled + confirmed) and estimated (inferred)
- Never modify the target site — only report and draft fixes for the user to apply
- If the site blocks web_fetch (Cloudflare, rate limits), say so. Don't fabricate results.
- For local businesses, always use LocalBusiness schema, not just Organization
- If asked "will this get me to #1", redirect to "here's what's in your control"
- Do not produce a 200-line report. The 5-10 fixes that matter beat a noise wall.
- If no AI API keys are provided, skip Step 4 and note it — don't run fake tests
