---
name: marketing-roas
description: >-
  Work out what advertising actually earned, by joining ad spend to lead attribution and to
  invoiced revenue. Use when asked for "ROAS", "return on ad spend", "cost per lead", "cost per
  booked call", "a marketing report", "campaign analytics", "is Meta/Google/TikTok working",
  "what did we get for the ad spend", or "revenue by channel". Covers the reconcile-first rule,
  the cohort-versus-cash distinction, the attribution start-date boundary, and the eight traps
  that produce flattering but wrong numbers.
---

# What the advertising actually earned

Three systems each hold a third of the answer, and in most businesses nothing
joins them:

| System | Holds |
|---|---|
| Ad platform API (Meta / Google / TikTok) | what was SPENT, per campaign, ad set, ad |
| CRM lead record | what ARRIVED, and which channel sent it |
| Accounting system (Xero, QuickBooks, Stripe) | what was PAID |

The arithmetic is trivial. Every mistake below was made for real on live numbers,
and each one produced a figure that looked like a result.

---

## Step 0 — reconcile revenue FIRST, always

**Never report return on ad spend without checking the revenue base.**

Pull every PAID invoice from the accounting system for the period, total it, and
compare against what the CRM believes it was paid. If those two disagree, stop:
every ROAS figure below is wrong by the difference.

This is not hypothetical. On one reconciliation the CRM held 87% of the real
figure, and a full client-facing report had already been written on the short
number. Four separate faults, all silent:

- the invoice sync read only the FIRST PAGE of results and treated it as the
  whole answer, so the newest invoices were permanently invisible
- invoice dates in the accounting API's own format could not be parsed, so
  payments were stamped with the day the sync noticed them, moving revenue
  between months
- an invoice-type filter was being ignored by the API, so supplier bills were
  being read as revenue
- there was no way to express one fee paid by two related entities, or a client
  invoiced under a different legal name

Build the reconciliation as a tool, not a one-off query, and run it monthly. A
gap means something has drifted.

---

## Step 1 — join the three systems

For a date window, produce:

- spend, impressions, clicks, per channel and per creative
- leads created in that window, grouped by the channel that created them
- how far each lead progressed (contacted, booked, completed, proposal, won)
- revenue invoiced against those leads, whenever it actually arrived

Report cost per lead and cost per booked call always. Report ROAS only when the
sales cycle has had time to complete, per the traps below.

---

## The eight traps

**1. Divide like for like.** ROAS is *that channel's* revenue over *that
channel's* spend. Dividing TOTAL revenue by ONE channel's spend produced 3.71x
for a month in which the channel's real figure was 0.00x, because the revenue had
come from a different channel and from untracked leads. A number that credits one
channel with another's revenue is worse than no number, because it reads as a
result and gets acted on.

**2. Cohort, not cash.** Revenue lags the click. Measure the lag before reporting
anything: time from lead created to first payment, median and range. Dividing
this week's revenue by this week's spend is meaningless in both directions.
Report revenue earned by the leads CREATED in the window, whenever it arrived.

**3. The attribution start-date boundary.** Find the first lead that ever carried
a source, and the coverage percentage by month after it. Revenue from leads
created before that date cannot be credited to any channel. Report it as
unattributed. Never spread it across channels that did not earn it.

**And do not call that "attribution is broken".** If the pixel fires and the
source is recorded, attribution works; the revenue is simply older than the
tracking, and that boundary closes on its own as new leads convert.

**4. A channel you cannot see is usually a channel you can ask to see.** If an
agency or partner runs ads from THEIR ad account, their spend is invisible to
you, not zero. But invisible is often just unasked: most ad platforms let an
account owner grant read access to your user or business, after which you can
pull spend, leads and creative-level performance through the API yourself. Ask on
day one, and write it into the engagement. A partner's own PDF report is their
summary of their work; the API is the record.

If they will not grant it, say the spend is unmeasurable rather than zero, and
never draw an efficiency comparison against a channel whose spend you can see.

**4b. Load the retainer into the comparison.** A managed channel costs the fee
plus the media. Comparing an agency's cost per lead on media alone against an
in-house channel with no fee makes the agency look about half its real price.
Loaded, one engagement that appeared to be half the cost of in-house was a dead
heat, $179 against $186 per lead.

**5. Say plainly when a channel is unmeasured.** If click identifiers are not
captured — `gclid` for Google, `ttclid` for TikTok, `fbclid` for Meta — leads
from that channel arrive indistinguishable from direct traffic. Do not estimate.
State it, and give the fix: whatever the site already does for one channel's
click id, do the same for the others.

**6. Check the denominator before you call anything CAC.** Dividing ONE channel's
cost by EVERY new customer is not that channel's acquisition cost, and a column
headed "new customers" beside a column headed "CAC" will be read as a channel
result no matter what the surrounding text says. It happened: an agency figure of
$3,755 per customer was really somewhere between $7,500 and $17,000, because most
of those customers came from elsewhere.

Give three readings and label them:

| Reading | How |
|---|---|
| Ceiling | channel cost over all new customers, explicitly marked as a ceiling |
| Estimate | channel cost over customers times the channel's measured share |
| Proven | channel cost over customers that actually carry that source |

The estimate needs the measured share, which you get from the attributed window
only. If 2 of 5 attributed customers carry the channel, the share is 40%, not
100%. Say how small that sample is.

**7. Cohort revenue is not monthly sales.** Cohort revenue is the lifetime
revenue of the customers who first made contact in a month. Monthly sales is what
the business banked. They are wildly different, and presenting cohort revenue in a
column next to a month invites someone to compare it against the figure they know
and conclude the whole report is wrong. One review showed $47,500 for August
against the owner's actual $170,000 month, and he was right to stop reading.

Always include the reconciliation, with the gap explained:

| Month | Sales received, cash, ex tax | Revenue from customers acquired that month |
|---|---|---|

Pull the sales column on a CASH basis, not accrual, so it matches what the owner
sees in the bank. State ex or including tax every time. The gap between the two
columns is revenue from customers won before the window, and naming that is what
makes the cohort column believable.

**8. History from before tracking may not be dateable at all.** A CRM migration or
bulk import commonly stamps every imported record with the import date, which
destroys the only field that said when the lead arrived. One import overwrote the
created date on hundreds of records, which made a whole month
unmeasurable and left ten paying customers undateable.

Before concluding a period cannot be measured, look for the system it was migrated
FROM. A legacy spreadsheet export usually still carries the true submission
timestamps, and matching it back by email restores the dating. Two cautions: that
legacy sheet probably mixes organic and paid enquiries, so use the ad platform for
lead counts and the sheet only for dating, and check whether the import date also
swallowed records from earlier months. In that case nine of the ten undateable
customers turned out to predate the advertising entirely.

---

## Judging a young channel

Revenue lags, so a new channel reads 0.00x until its first lead completes the
cycle. Use **cost per booked call** until it has had a fair run.

But "too early" expires, and it is worth naming the date it does. A month with
full spend, high attribution coverage and more than one median sales cycle behind
it is a fair test. If the channel produced leads and no revenue in that window,
say so. Compare its progression against another channel over the same period:
leads, booked, proposal, won, and the disqualification rate. A channel buying
volume that does not survive qualification is a lead-quality problem, not a
follow-up problem, and the disqualification rate is what shows it.

---

## Multi-stage funnels and long lags

**Skip this section if a customer pays once, at or soon after the enquiry** (most retail,
e-commerce, trades jobs and simple services). Standard CAC and payback in `cac-and-conversion`
cover you.

Some businesses do not have one conversion. They have a sequence, each stage with
its own price or its own drop-off: an enquiry becomes an appraisal, an appraisal
becomes a signed listing, a listing becomes a completed sale, and only the last
one pays. Professional services, recruitment, construction and property all look
like this.

Three consequences.

**There is more than one honest denominator.** Cost per signed engagement and cost
per completed, paid engagement are different numbers and both matter. Report both,
and never let the cheaper one stand alone.

**Measure the lag per stage before reporting any ratio.** Lead to first payment
may be weeks; lead to final payment may be months. Where the final payment is
months out, the recent cohorts are structurally incomplete and must be labelled as
a floor, not a verdict.

**Revenue per customer is realised, not list.** Where the fee is a percentage, or
where a later stage may never happen, the average customer is worth far less than
the headline. For example, a business priced as though every customer bought a $20,000
package; if half stop after a $5,000 first stage, realised revenue per customer is
$12,500, not $20,000. Compute realised revenue per customer from actual payments and
use that against CAC. If the number is far below list, the mid-funnel stall is the
finding, not the ad costs.

---

## Define CAC before you report it

CAC means whatever the report says it means, so say it. The two defensible
definitions:

- **advertising CAC**: media plus any management fee, divided by new customers
- **loaded CAC**: the above plus sales labour, commission and the share of
  salaries spent winning customers

They can differ by a factor of two. Pick one with whoever is making the decision,
write the definition into the report, and quote the excluded costs beside it for
reference, so nobody reads the smaller number as the full cost of winning a
customer. Advertising CAC is the better default for comparing channels. Loaded CAC
is the one for a pricing decision.

---

## Equal windows and the quality trap

Adapted from coreyhaines31/marketingskills (MIT).

- **Every rate divides matching, closed windows:** spend and the leads created in the same dates,
  and those leads' outcomes. Never full-period spend over part-period results.
- **Cohorts must be mature before they count:** older than your normal lead-to-payment lag.
  Younger cohorts are "not yet mature", not a trend.
- **Say the dates** on every figure, and compare equal-length periods (full weeks or months).
- **The quality trap:** platform-reported ROAS and cost per lead reward cheap form fills. Judge
  channels and ads on CRM outcomes and cash received; use the platform's own conversion counts for
  delivery only. When the platform and the CRM disagree, the CRM wins.
- **Payback** (how fast acquisition cost comes back, by revenue model) lives in
  `cac-and-conversion`. Use it when asked whether a channel "pays for itself", not ROAS alone.

---

## Writing the report

If it is going to a client or a board, that means:

- lead with the finding, not the spend
- period-on-period deltas with the awkward ones kept in; falling click-through
  and rising CPM while spend doubles is the expected shape, and saying so builds
  trust
- name the ads that spent and produced nothing, with the amount
- state what changed in the period, including faults found and fixed
- recommendations that are decisions, not observations
- say when a number is a snapshot of a live campaign

State the currency and whether figures include tax, every time.

---

## Do not break the accounting connection

Many accounting APIs (Xero among them) issue SINGLE-USE refresh tokens: refreshing
returns a new one and invalidates the old. If several consumers share one token,
whoever refreshes first MUST persist the replacement for everyone else.

A throwaway analysis script that refreshes and discards the new token will kill
the scheduled sync for every other consumer, and recovery usually needs a human
to re-authorise in a browser. Either reuse the sync's own read path, or copy its
token write-back into your script before running it.
