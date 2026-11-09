# Paid acquisition skills

Twelve agent skills that take a business from "we have a website, we boost posts by
hand, and nothing is connected" to "we can say what each channel earned and
whether our price covers it". They are written to be handed to someone else: no
accounts, no keys, no company names, nothing pre-wired.

Each skill is a `SKILL.md` your agent reads plus a `README.md` for you, the human,
saying what it needs from you before it can start.

## Already running Meta ads? Start with the health check

Run `meta-account-healthcheck` first. It reads your account's history (read only) and scores eight
areas green / amber / red: ownership, tracking, structure, performance, fatigue, placements, how
well your ads follow Meta's current creative-led algorithm, and compliance. You get the top 5 fixes
in order of money saved and a 30-day plan. Then follow the stages below for whatever scored red.

## Start here if nothing is integrated yet

If ads are currently placed by hand, leads arrive by phone and email, and the CRM
does not record where anyone came from, do the stages in this order. Each one is
usable on its own, and each is a prerequisite for the next. The temptation is to
start at stage 4 because that is the part that feels like marketing. Starting
there is why most businesses cannot answer what a customer costs two years later.

### Stage 0. Find out what you already own (half a day)

Before building anything, establish:

- **Who owns the pixel on your site.** If there is a tracking pixel already, whose
  business portfolio is it in? If it is an agency's, your data leaves when they
  do, and your own ad account cannot optimise against it.
- **Who owns the ad accounts.** Same question. An account in a partner's business
  is theirs, not yours.
- **Whether any conversion tracking fires at all.** Usually a tag exists and has
  never recorded anything.
- **What your CRM can record about a lead's origin.** You need one field. If there
  isn't one, that is the first build.
- **Where the money is recorded**, and whether you can read paid invoices or
  settlements from it programmatically.

`open-operator-audit` covers the site and visibility side of this. The ownership
questions you ask people.

**Gate: do not spend on ads until you know who owns the pixel and the ad account.**

### Stage 1. Make leads identifiable (a few days)

One field on the lead record for the channel, written at the moment the lead is
created, never edited by hand afterwards. Then capture the click identifiers that
let you prove it: `fbclid` and the `fbc`/`fbp` cookies for Meta, `gclid` for
Google, `ttclid` for TikTok.

This is the single highest-value thing in the whole bundle, and it is worth
nothing retrospectively. Every day it is not done is a day you will never be able
to attribute. Covered in `meta-pixel-funnel` and `ad-pixel-funnel`.

**Also handle the leads that never touch a form.** In many industries most
enquiries arrive by phone, or through a third-party marketplace or portal that
hands you a name and nothing else. Those will never carry a click id. Decide now
how they get a source: a tracking number per channel, an agreed value for portal
leads, and a rule that a blank source means "unknown", never the name of whichever
channel you happen to be running. A blank is not your agency's lead.

### Stage 2. Server-side events (a day, alongside stage 1)

Browser pixels lose roughly a third of conversions to iOS restrictions and ad
blockers. Send the same event from your server with a shared `event_id` so the
platform deduplicates it. Doing the browser half and skipping this is the most
common half-finished setup there is. Covered in `meta-pixel-funnel`, step by step.

**Gate: verify in the platform's test tool that browser and server events arrive
and are marked deduplicated.** If it does not say deduplicated, your ids do not
match and you are double-counting.

### Stage 3. Seal each channel's path (a day per channel)

Give every channel its own landing URL, its own form endpoint and its own lead
source value. If Meta, Google and portal traffic all land on the same page with
the same form, no reporting will ever separate them. It feels redundant. It is
what makes stage 6 possible. `ad-pixel-funnel` does this for any channel after the
first.

### Stage 3b. Look at what already works in the market (an hour)

Before writing creative, see what competitors have been running longest.
`meta-ad-recon` does this free from Meta's public Ad Library: no subscription, no
login. Longevity is the proxy, since nobody outside the EU can see competitor
spend.

Start the weekly snapshot now even if you do not act on it yet. The paid tools in
this space are really selling an archive they began collecting before you cared,
and four weeks of your own snapshots tells you what the market killed quickly
versus what survived a quarter.

### Stage 4. Move the ads off manual (a week)

Only now bring the campaigns into something auditable: `meta-ads-campaign` for
Meta, `google-ads-conversions` then `google-ads-campaign-launch` for Google,
`tiktok-ads-mcp` if TikTok is in play. Build one channel properly before adding a
second.

Everything these skills create is **paused by default**. Activation is always a
separate, explicit step.

### Stage 5. Let it run (one full sales cycle)

Resist reporting a return before a cohort has had time to pay. Measure the lag
first: lead created to first payment, and lead created to final payment, median
and range. In a business where the real fee arrives at completion or settlement,
that can be months, and anything reported before then is a floor, not a result.

Report cost per lead and cost per booked appointment in the meantime. They move
early and they are honest.

**Every Monday, run `meta-weekly-review`.** It gives a keep / scale / pause / fix /
hold call on every ad, judged on what each ad's leads actually did in your CRM, with
hold rules so nothing is judged while Meta is still learning. Before making new ads,
follow the creative playbook in `meta-ads-campaign` (3 to 5 new static concepts a
week, broad targeting, identity keywords).

### Stage 6. Measure it (half a day to build)

`marketing-roas` joins spend, attribution and revenue. Reconcile the revenue base
against the accounting system first, to a gap of zero. Expect the first honest
number to be worse than the ad platform's dashboard.

### Stage 7. Answer the business question (a few hours)

`cac-and-conversion` turns cost per lead into cost per customer (standard paid and
blended CAC), shows how fast that cost comes back (payback, for one-off sales,
subscriptions, deposits/milestones or commission), and tells you whether the price
covers acquisition and where deals stall. This is the stage an owner actually wants, and it is unanswerable
without stages 1 and 2.

```
Stage 0  meta-account-healthcheck   if you already run Meta ads: scored audit + fix list
         open-operator-audit        what exists, who owns it
Stage 1  meta-pixel-funnel         lead source + click ids
Stage 2  meta-pixel-funnel         server-side events, deduplicated
Stage 3  ad-pixel-funnel           one sealed path per channel
Stage 3b meta-ad-recon            what competitors run longest, free, weekly
Stage 4  meta-ads-campaign         campaigns + creative playbook, paused by default
         google-ads-conversions    audit the tag, then conversion actions
         google-ads-campaign-launch
         tiktok-ads-mcp            live reads on a TikTok account
Stage 5  meta-weekly-review        weekly keep/scale/pause per ad (run every Monday)
Stage 6  marketing-roas            spend + leads + revenue, joined
Stage 7  cac-and-conversion        CAC, payback, and whether the price covers it
```

## The six things that go wrong

**1. Someone else owns your pixel.** Agencies commonly install their own pixel
under their own business portfolio. Your ad account then cannot optimise against
it, and when the relationship ends the data leaves with them. If a pixel on your
site belongs to a portfolio you are not an admin of, you are building on rented
ground.

**2. Browser-only tracking loses a third of your conversions.** The Conversions
API sends the same event from your server, matched by a shared `event_id` you
generate. Skipping the server side is the most common half-finished setup.

**3. Channels bleed into each other.** Shared landing pages and shared forms
cannot be separated later by any amount of reporting.

**4. Nobody checks the revenue base.** Reconcile against the accounting system
until the gap is zero before reporting any ratio. Split payments, credit notes and
invoices raised under a different entity all understate it silently, and a
shortfall in the base understates every channel at once.

**5. The denominator is wrong.** Dividing one channel's cost by every new customer
is not that channel's acquisition cost, and it will be read as one. Label it as a
ceiling, give the measured share of customers that channel can actually be shown
to have produced, and give the proven figure beside it. The gap between those
three is routinely a factor of four.

**6. Cohort revenue gets mistaken for monthly sales.** The lifetime revenue of
customers acquired in a month is not what the business banked that month. Present
both, in a reconciliation, with the difference explained. Someone who knows the
real monthly figure will check, and if the two cannot be reconciled on the page
they will reasonably distrust the entire report.

## A note on partner-run advertising

If an agency or partner runs the ads from their own account, ask for API read
access on day one and write it into the engagement. Most platforms allow it, and
it takes them minutes. Their own report is their summary of their work; the API is
the record, and it answers questions a summary cannot, such as which individual
ad produced the leads in the month that worked.

Also load the retainer into every comparison. A managed channel costs the fee plus
the media, and comparing their media-only cost per lead against an in-house
channel with no fee makes them look about half their real price.

Where some of the "ad spend" is actually funded by your customers, as with
vendor-paid campaign contributions, separate it from the money the business spends
on acquiring customers. It is marketing spend, but it is not your CAC.

## Using them

Drop each skill folder where your agent looks for skills (`~/.claude/skills/` for
Claude Code, or import the `.skill` file in a client that supports it), then invoke
by name or just describe the task.

Nothing here spends money on its own. Campaign skills create everything paused;
activation is always a separate, explicit step.
