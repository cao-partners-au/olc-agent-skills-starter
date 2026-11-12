---
name: site-analytics
description: >-
  On-demand website analytics that joins Plausible (traffic, sources, ads and conversions per
  landing page, any date range) with Microsoft Clarity (scroll depth, time on page, rage clicks,
  quick backs) and stored history, then diagnoses why pages convert or don't and what to fix. Also
  sets both services up from scratch with the user (guided, or by driving the browser) and stores
  daily history for long-term reporting. Use when asked "how's the website doing", "which landing
  page converts best", "why isn't this page converting", "website analytics", "traffic report",
  "where are visitors dropping off", "set up Plausible", "set up Clarity", "install website
  analytics", or "store our analytics history".
---

# Site analytics: Plausible + Clarity together

**Plausible** answers *how many*: visits, sources, ads, and how many visits reach a goal.
**Clarity** answers *why*: how far people scroll, how long they stay, where they get frustrated, and
recordings to watch. **History** answers *is it getting better*: a daily snapshot, because Clarity
forgets after 1 to 3 days. **The CRM** (optional) answers *did they become customers*.

## 0. Is it set up?
Look for a config file (`site.env`; copy `example.env`). If Plausible or Clarity isn't installed,
or there's no API key/token, **follow `references/setup-guide.md` with the user** before anything
else. It covers accounts, installing on any website platform, the strict-CSP trap, goals, keys,
privacy, verification, and history.

## 1. Run the report (read only)
```bash
python3 scripts/report.py --config site.env              # last 30 days
python3 scripts/report.py --config site.env --days 7
python3 scripts/report.py --config site.env --from 2026-10-01 --to 2026-10-31
python3 scripts/report.py --config site.env --no-clarity # keep Clarity's 10 reads/day
```
It prints totals vs the previous equal period, every landing page (visits that **started** there,
bounce, average time, goal conversions and % of visits converting), sources, Meta/Google ads
(`utm_content`), Clarity's last 3 days per page, stored weekly history, and CRM leads per landing
page if a `LEADS_CSV` is configured. Full data: `/tmp/site-analytics-report.json`.

**Clarity budget:** 10 reads a day for the whole project, shared with any dashboard or snapshot job.
Prefer stored history; only do a live read when the user wants the last few days.

## 2. Diagnose (combine both tools; never one alone)
For each landing page with meaningful traffic (roughly 50+ visits in the range):

| Plausible says | Clarity says | Likely cause | Fix |
|---|---|---|---|
| High bounce, low time | **Low scroll** (under ~25%) | The top of the page loses them: headline, hero, slow load, mismatch with the ad | Rewrite the hero to match the ad's promise; check mobile load speed |
| OK time, low conversion | **Good scroll**, form reached | The form or offer is the problem | Shorten the form, reduce steps, clarify what happens next |
| Low conversion | **Rage / dead clicks** | Something looks clickable and isn't, or is broken | Watch 5 recordings filtered by rage clicks; fix the element |
| Low conversion | **High quick backs** | Visitors expected something else | Align the ad/link text with the page |
| Good conversion, few visits | — | A winner starved of traffic | Send more ads/links to it |
| Conversions by Form: Submission but not the success-page goal | — | Spam, or a form that confirms on the page | Check the CRM for real leads |

Also check:
- **Compare like with like:** equal periods; say the dates; a week of data on one page is a hint,
  not a result.
- **Source and ad quality:** which sources and ads (`utm_content` = ad ID if ads carry
  `utm_content={{ad.id}}`) bring visits that convert, not just visits.
- **Plausible counts ≠ CRM leads.** Plausible counts visitors reaching a goal page; the CRM is the
  truth for leads and customers. When they disagree, trust the CRM and look for a tracking gap.
- **Plausible ≠ Clarity session counts.** Different methods; never add or compare them directly.

## 3. Output (short; phone-friendly)
1. One-line verdict and the biggest opportunity.
2. Traffic and conversion vs the previous period.
3. Top landing pages: visits, conversion %, and the Clarity "why" for the weak ones.
4. Up to 4 fixes, each with which page, what to change, and the expected effect.
5. What to watch in recordings (page + filter, e.g. "/pricing/, rage clicks").
6. Facts vs guesses vs missing. Never state a number not pulled this session.

## 4. History (set up once)
Schedule `scripts/snapshot.py --config site.env` daily just after midnight. It stores Plausible per
day x landing page / source / campaign / ad, and Clarity's last 24 hours per page, in SQLite or
Supabase (`references/history-tables.sql`). Re-running a day replaces it. Backfill Plausible with
`--from/--to`; Clarity cannot be backfilled, so start the snapshot as soon as Clarity is installed.
Dashboards and CRMs read these two tables for long-term reporting.

## Guardrails
- Read only. Never change site code, goals or settings without the user's approval.
- Never paste or print API keys/tokens; they live in files referenced by the config.
- Account sign-ups, logins, passwords and payment are always the user's to do.
- If your site has a strict Content Security Policy, the Plausible and Clarity scripts must be
  allowed in it (or served from your own domain), or they fail silently and record nothing.
