---
name: meta-weekly-review
description: >-
  Weekly review of a Meta (Facebook/Instagram) ad account that ends in a decision per ad: keep,
  scale, pause, fix or hold, with the evidence behind each. Joins Meta delivery with what each ad's
  leads did next in the CRM (booked, showed, bought), anchors every call to one target number, and
  applies hold rules so nothing is judged mid-learning or on too little data. Use when asked "how are
  the ads doing", "run the ads report", "is anything fatigued", "what should we pause", "which ads
  are working", "should we scale this", "weekly ads review", or after a batch of ad changes. Read
  only until the owner approves a change.
---

# Meta weekly review

Method adapted from coreyhaines31/marketingskills (MIT): `ads/references/meta-decision-system.md`,
`operating-check.md` and `audit-guardrails.md`.

## 0. Setup (once)

- `META_AD_ACCOUNT` = your ad account ID (`act_…`), `META_TOKEN_FILE` = path to a file holding a
  System User token with `ads_read` (see `meta-ads-campaign`). Never paste the token into chat.
- For CRM outcomes, export leads to CSV with `created_at, ad_id, booked, showed, won` (and an
  optional `score`). `ad_id` comes from the ad's URL parameters: add
  `utm_content={{ad.id}}` to every ad's URL parameters and have your forms save it on the lead.
  Without it the review falls back to Meta's numbers only, which can't tell good leads from bad.

## 1. Pull the data (read only)

```bash
python3 scripts/pull.py --crm leads.csv            # weeks ending yesterday
python3 scripts/pull.py --end 2026-10-18 --crm leads.csv
```

It prints account totals this week vs last, the **target number**, active ads vs the **ad-count
ceiling**, each ad set's budget and **last edited date**, and per ad: this week, last week and 14
days, lifetime frequency, and CRM leads / booked / showed / won (and average score).

Never pause an ad on Meta's lead count alone. Meta counts form fills; the CRM shows whether they
became customers.

## 2. The target number

Use the most "real" outcome you have enough of:
- **Best:** cost per paying customer (if you win enough customers a month to measure).
- **Usually:** cost per showed call / appointment / quote, over the last 30 days (the script
  computes this from the CSV).
- **Fallback:** cost per lead, until CRM data exists. Say clearly that it's a weaker target.

Every decision below is a multiple of this one number. Review it monthly.

## 3. Hold rules first (what NOT to judge)

Mark an ad or ad set **HOLD** (no decision) when any is true, and say which:
- **Learning:** its ad set was edited (placements, location, budget, goal) or its creative/link was
  swapped in the last **7 days**. Costs run higher and jumpier for 3 to 5 days.
- **Too little spend:** under **2 × target** spent in the last 14 days.
- **Too new:** its leads are younger than your normal lead-to-outcome lag (measure it; for many
  businesses it's 3 to 14 days).
- **Small numbers:** 1 or 2 results either way is noise.

A cost spike is a question, not a verdict.

## 4. Decide per ad (last 14 days, multiples of the target)

| Call | When |
|---|---|
| **Keep** | reaches the target outcome at or under ~1.5 × target, or has produced paying customers |
| **Scale** | clearly under target, frequency under ~3, not in learning. Raise budget **≤20%**, then wait 3 to 5 days |
| **Pause** | spent **3 × target or more** with no target outcomes, and no hold rule applies. Have a replacement ready |
| **Fix, not pause** | good click rate but no enquiries: suspect the landing page or form, not the ad |
| **Watch** | in between, or outcomes pending; name the re-check date |

**Fatigue** needs all three: frequency rising (above ~3 to 4), click rate falling week on week, and
cost per result rising. High frequency with a rising click rate is not fatigue.

**Ad-count ceiling** = (daily budget × 14) ÷ (2 × target). Above it, ads starve and none gets a fair
read. Ads that Meta barely spends on (under ~$70 a week) are Meta's own verdict; pausing them is
tidying, not a finding.

## 5. Other checks every week

- **Creative volume:** count ads created in the last 7 days. Under 3 genuinely new concepts a week
  under-feeds the account (see `meta-ads-campaign/references/creative-playbook.md`).
- **Tracking coverage:** the share of CRM leads with no `ad_id`. If it rises, an ad points somewhere
  that drops the URL parameters (often a multi-page form); find and fix it.
- **Lead counts:** Meta reports one lead under several action types. Take the max, never the sum.
- **Separate budgets on purpose:** if two very different audiences or offers share one budget, Meta
  sends most of it to whichever converts cheapest. Flag before recommending a merge.
- **Special Ad Categories** (employment, housing, credit, social issues) restrict targeting; don't
  recommend age, gender or postcode targeting for those campaigns.
- Paused ads still show spend for the days before the pause.
- Weekend-heavy weeks run softer; compare full weeks.

## 6. Output (short; the owner reads it on a phone)

1. One-line verdict, then this week vs last (spend, leads, cost per lead, CRM booked/showed/won).
2. **Keep / Scale / Pause / Watch / Hold**: each ad with the one number that decides it and why.
3. Up to 4 tweaks, each with the expected effect.
4. Up to 3 trends.
5. **Facts vs guesses vs missing**: label anything not read from data. Never state a figure that
   wasn't pulled in this session.
6. End with: "Shall I pause X / change Y? I won't change anything until you say so."
