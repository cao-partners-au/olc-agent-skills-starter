---
name: meta-account-healthcheck
description: >-
  First-run health check for a Meta (Facebook/Instagram) ad account that already has history:
  a scored breakdown of how the account is set up, how it has performed, what is wasting money,
  how well the campaigns follow Meta's current creative-led ("Andromeda") playbook, and a
  prioritised fix list. Use the first time these skills are used on an account, or when asked
  "audit my Meta ads", "health check my ad account", "how are my Facebook ads really going", "what
  should I change in my Meta account", "is my account set up right", or "how aligned am I with the
  Andromeda playbook". Read only: recommends, never changes anything.
---

# Meta account health check (first run)

Use this **once, before** the other skills, on any account with at least 30 days of spend. It tells
the owner where they stand and what to fix first. After that, `meta-weekly-review` takes over week
to week.

Method draws on coreyhaines31/marketingskills (MIT): Meta decision system, audit guardrails and
the Andromeda playbook. See also `meta-ads-campaign/references/creative-playbook.md`.

## 0. Setup

- `META_AD_ACCOUNT` = the ad account ID (`act_…`); `META_TOKEN_FILE` = a file holding a System User
  token with `ads_read` (see `meta-ads-campaign`, Phase 0). Never paste the token into chat.
- Ask the owner three things (the score depends on them):
  1. **What is one paying customer worth** in the first year (or first purchase)?
  2. **What counts as a good result:** a lead, a booked call, a purchase?
  3. **Is there a CRM or sheet** recording which leads became customers? (If yes, the
     `meta-weekly-review` CSV format gives much better answers later.)

## 1. Pull the data (read only)

```bash
python3 scripts/healthcheck.py            # last 90 days
python3 scripts/healthcheck.py --days 180 # longer history
```

It prints, and saves to `/tmp/meta-healthcheck.json`: account and owner, pixel/dataset health
(browser vs server events, which events fire), active campaign/ad set/ad structure and targeting,
13+ weeks of weekly results, placements with cost per result, every active ad's last 30 days, and a
creative audit (format mix, new ads per week, ad age, copy length, near-duplicate copy, URL
tracking parameters, spend concentration, starved ads).

If a section errors (permissions), score it **Unknown** and say what access is missing. Don't guess.

## 2. Score eight areas: Green / Amber / Red

Score each area, give the one or two numbers behind it, and the fix. Use the owner's answers from
step 0 for the money thresholds.

**Breakeven cost per result** = value of a customer × result-to-customer rate (ask, or estimate and
label it a guess). Everything money-related compares against this.

### A. Ownership and access
- **Green:** the ad account and pixel/dataset sit in the owner's own Business portfolio; at least two
  people are admins; account status active.
- **Red:** the pixel or ad account belongs to an agency or someone else's business (data leaves when
  they do), or only one admin (one lost login locks the business out).

### B. Tracking quality
- **Green:** pixel fired in the last 24 hours; **server events (Conversions API) present**, roughly
  30%+ of events; the result event the campaigns optimise for actually fires; 90%+ of active ads
  carry URL parameters (e.g. `utm_content={{ad.id}}`) so leads can be traced to ads.
- **Amber:** browser-only events, or URL parameters on fewer than 90% of ads.
- **Red:** the optimisation event barely fires, the pixel hasn't fired recently, or leads can't be
  traced to ads at all.
- **Bonus green:** later-stage events (booked, showed, purchased) sent from the CRM.

### C. Structure and budget
- **Ad-count ceiling** = (daily budget × 14) ÷ (2 × target cost per result). Above it: Amber/Red.
- **Fragmentation:** many ad sets with small budgets and the same goal split Meta's learning. Red
  if most ad sets can't reach ~50 results a week *and* they target the same people.
- **Learning:** ad sets stuck in "learning limited" for weeks = Amber.
- Different audiences or offers kept in separate budgets on purpose is fine; note it, don't penalise.

### D. Performance and trend
- Cost per result vs breakeven: under 70% Green, 70–100% Amber, over 100% Red.
- **Trend:** compare the last 4 weeks with the 4 before. A rising cost per result with rising
  frequency and falling CTR = fatigue (see E).
- Flag single weeks that distort averages (a launch week, a pause, a holiday).

### E. Fatigue and frequency
- Account frequency (90 days) under 3 Green, 3–5 Amber, over 5 Red, *if* CTR is falling.
- Per ad: fatigued only when frequency is rising **and** CTR falling **and** cost per result rising.

### F. Placements
- Any placement with meaningful spend (5%+) costing over ~1.5× the main feeds per result is waste.
  Audience Network, Stories and right-hand column are the usual offenders. Recommend manual
  placements without them, and say how much spend moves.

### G. Andromeda alignment (creative-led delivery)
Score each item 0–2 and give the total out of 16:

| Item | 2 (aligned) | 0 (misaligned) |
|---|---|---|
| Targeting breadth | whole country / service area, few or no interests | stacked interests, small radius circles, tight age bands |
| New concepts per week (last 8 weeks) | 3+ most weeks | bursts then nothing |
| Format mix | mostly statics, some video | mostly polished video, or carousels only |
| Distinct concepts | few near-duplicate pairs | many ads 60%+ alike in copy |
| Copy length | substantial primary text naming who it's for (~200+ chars) | one-liners |
| Identity keywords | headlines/first lines name the customer's industry or situation | generic "we help businesses" copy |
| Spend spread | Meta funds several ads; starved ads moved or paused | one ad takes most spend; many ads under ~$70/week left running |
| Judged on outcomes | ads traced to CRM results; later-stage events sent | judged on platform leads only |

Read **identity keywords** and **concepts** from the printed `copy_start` lines yourself; the
script can't judge meaning. 13–16 = aligned, 8–12 = partly, under 8 = not aligned.

### H. Special Ad Category and compliance
- Ads about jobs, housing, credit/finance or social issues **must** run in the matching Special Ad
  Category. Running without it risks disapproval and account restrictions: Red if it applies and
  isn't set. If it is set, don't recommend targeting the category forbids (age, gender, postcode).
- Landing pages: claims like "only", "guaranteed", "no fee" when fees exist are consumer-law risks.
  Flag them for the owner to check.

## 3. Output (one page; the owner reads it on a phone)

1. **Headline:** one sentence on overall health, and the single biggest money leak.
2. **Scorecard:** A–H with Green/Amber/Red (or Unknown), each with its deciding number.
3. **Andromeda alignment:** X/16, with the two weakest items.
4. **Top 5 fixes, in order of money saved or made**, each with the expected effect and effort
   (minutes / hours / days). Quick wins first.
5. **What's working:** the ads, placements or audiences to protect.
6. **A 30-day plan:** week 1 tracking and waste, week 2 structure, weeks 3–4 creative cadence
   (3–5 new statics a week), then hand over to `meta-weekly-review` every Monday.
7. **Facts / guesses / missing:** label anything not read from the data. Never state a figure that
   wasn't pulled in this session.
8. End with: "I haven't changed anything. Which of these should I do first?"

## Guardrails
- Read only. Every change is a separate, approved step using `meta-ads-campaign`.
- Don't recommend pausing an ad that is the account's main source of results without a
  replacement ready.
- Don't judge anything edited in the last 7 days (Meta's learning phase); say so instead.
- Meta reports one lead under several action types: count the max, never the sum (the script does).
