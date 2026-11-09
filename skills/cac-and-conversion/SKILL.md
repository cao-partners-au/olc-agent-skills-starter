---
name: cac-and-conversion
description: >-
  Work out what it costs to acquire a paying customer (CAC), how fast that cost comes back
  (payback), what a customer is actually worth, and whether the price covers it. Works for any
  revenue model: one-off sales, subscriptions and memberships, retainers, deposit-then-balance or
  milestone billing, and commission or percentage fees. Use when asked "what is our CAC", "how much
  does a customer cost us", "how long until a customer pays back", "is this channel paying for
  itself", "should we raise prices", "what is a lead worth", "what can we afford to pay per lead",
  or "where do deals stall".
---

# What a customer costs, how fast it comes back, and whether the price covers it

Cost per lead is a marketing number. **Cost per customer, and how quickly that customer pays it
back, is a business number.** It decides pricing, budget, and whether a channel is worth running.

Run this after `marketing-roas`, which produces the spend and attribution inputs and reconciles
revenue against the accounting system.

---

## Step 1: standard CAC first

Most businesses should start here, and many never need more.

**CAC = acquisition cost in a period ÷ new paying customers acquired from that spend.**

- **Paid CAC (per channel):** that channel's ad spend ÷ new customers that channel produced.
  Never divide one channel's spend by all new customers (see `marketing-roas`).
- **Blended CAC:** all marketing spend ÷ all new customers, including organic and referral. It
  looks better than paid CAC; report both and label which is which.
- **Fully loaded CAC (for pricing decisions):** add agency/freelancer fees, tools, creative
  production and the sales time spent closing. State what is and isn't included.

A "customer" is someone who **paid**, not a lead, a booking or a signed quote.

---

## Step 2: compare equal, mature windows

Most CAC errors are window errors, not maths errors.

- **Match the windows.** Spend from 1 to 30 September goes with the customers who came from leads
  created 1 to 30 September. Never divide a full month's spend by a partial month's sales, or this
  month's spend by customers who came from last month's leads.
- **Only judge mature cohorts.** Measure the time from lead to first payment (median and slowest).
  A cohort only counts once its leads are older than that lag. Report younger cohorts as "not yet
  mature", never as a trend in either direction.
- **Say the dates** on every figure and compare equal-length periods (full weeks or months).

Example of the trap: dividing three months of spend by the customers won so far, when the newest
leads haven't had time to buy, overstates CAC. Matching each month's spend to its own cohort and
dropping the immature weeks can move CAC by 10 to 20%.

---

## Step 3: payback, which depends on how you get paid

CAC says what a customer costs; **payback says how long that cash is tied up.** Two businesses
with the same CAC can be in completely different positions.

Use **cash received** (payments that landed), not invoices raised, and **gross margin** where
delivery has real costs.

| Revenue model | How to read payback |
|---|---|
| **One-off sale** (product, job, project paid on completion) | Payback is immediate if first-order gross profit ≥ CAC. If not, payback only comes from repeat purchases: measure the repeat rate and time to second order before assuming it. |
| **Subscription / membership / retainer** | Payback months = CAC ÷ (monthly revenue × gross margin). Check with real cohort retention: find the month cumulative gross profit per original customer first covers CAC. Early churn makes this much longer than the simple ratio. |
| **Deposit then balance, or milestone billing** | Count each payment when it lands. Payback is reached at the first payment whose cumulative cash covers CAC. Track how many customers stop after the first payment; their revenue is the deposit only. |
| **Commission / percentage fee** (agents, brokers, finance) | Use the achieved fee, not an assumed average sale. Allow for long settlement lags; recent cohorts are a floor, not a result. |
| **High-ticket with a sales process** | Same as the model it bills under, but measure the lead-to-paid lag first; it sets how long you wait before judging a cohort. |

Report payback **per product or tier**, never blended. A cheap entry product and a premium one
can share a CAC and have opposite payback.

Planning reference: payback inside 3 to 12 months is comfortable for most small businesses, but
the real limit is your cash runway. If a cohort hasn't paid back yet, say so; don't project a date.

---

## Step 4: what you can afford per lead

**Breakeven cost per lead = average revenue per customer × lead-to-customer rate.**
Example: $2,000 average first-year revenue × 1 in 20 leads becoming customers = $100 per lead
breaks even on revenue. Use gross profit instead of revenue for the true ceiling, then set the
target below it by the margin you need.

**Breakeven cost per click = target cost per lead × landing page conversion rate.**

These come from your own deal maths, not platform benchmarks, and every pause or scale decision
should key off them.

---

## Step 5: the funnel, and where it stalls

Write the actual sequence with the money marked, in the business's own words, e.g.

```
enquiry -> call/quote booked -> call/quote held -> proposal accepted -> PAID (-> repeat / renewal)
```

Count how many of a matched cohort reach each stage. **The biggest drop is usually worth more than
any advertising change.** Work out what one percentage point at that stage is worth and compare it
with the cost of buying more leads. Common winners: show-up rate for booked calls (reminders and
confirmations), quote follow-up speed, and first-payment collection.

If payment happens in stages, treat each payment as its own event and report how many customers
only ever trigger the first one.

---

## Step 6: realised revenue per customer, never list price

Average **actual payments received** over every customer acquired, including the ones who
cancelled early, stopped after a deposit, or bought the entry product only. The gap between list
price and realised revenue per customer is usually the most useful number this skill produces.

Report the distribution, not just the mean (completed at full price, entry tier, part-paid,
refunded), so a cheaper tier or high drop-off doesn't hide inside an average.

---

## Step 7: the pricing read

1. **Does the first payment cover CAC?** If a customer who only ever makes the first purchase or
   payment returns less than CAC plus delivery cost, they are unprofitable. Know what share of
   customers look like that.
2. **Is a cheaper offer carrying the same CAC?** A lower price doesn't halve the cost to win the
   customer. If the mix shifts toward the cheaper offer, revenue per customer falls while CAC
   holds.
3. **Is the stall cheaper to fix than the lead?** Usually yes (Step 5).

---

## The quality trap

Ad platforms optimise toward whatever you tell them a conversion is. Fed form fills, they buy
cheap form fills: cost per lead falls while customers don't. Fix, in order:

1. **Judge ads and channels on CRM outcomes** (held calls, quotes accepted, payments), not on the
   platform's lead count.
2. **Send later stages back to the platforms** (Meta Conversions API lifecycle events, Google
   offline conversion import) so they learn which leads become customers. Optimise for a later
   stage only once an ad set reaches roughly 50 of that event a week.
3. When the platform and the CRM disagree, **the CRM wins**.

---

## Reporting it honestly

- State the CAC definition and what's excluded.
- Give paid and blended CAC side by side, with dates and cohort maturity.
- Give payback per product/tier and say which revenue model it assumes.
- Separate cohort revenue from monthly sales.
- Count referrals and repeat business separately; they cost nothing to acquire and flatter any
  blended figure.
- End with a decision: raise this price, fix this stage, hold or move this budget.

## What makes this wrong

- **Invoices raised instead of cash received.**
- **Unmatched or immature windows** (Step 2).
- **One customer billed under several names or entities**, reading as several customers or a
  missing one. Reconcile per customer, not per invoice.
- **Blending tiers or products** in payback.
- **Ignoring labour** in a pricing decision. Advertising CAC excludes the people who sell and
  deliver; say so, or the price gets set against half the truth.

Method notes on windows, payback and the quality trap adapted from coreyhaines31/marketingskills (MIT).
