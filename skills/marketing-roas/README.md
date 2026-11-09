# marketing-roas

Join ad spend, lead attribution and invoiced revenue to work out what the advertising actually earned.

**When in the sequence:** once any channel has been running a full sales cycle  
**Rough time:** half a day to build, minutes to run after

## Before you start, you need

- API access to each ad platform you spend on
- A CRM where every lead carries the channel that created it
- An accounting system you can read paid invoices from

## It will ask you for

- When did lead-source tracking actually start
- What is the median time from lead to first payment, and to final payment
- Which channels run from ad accounts you do not own, and whether you can get read access to them
- What the business actually banked each month, so cohort revenue can be reconciled against it

## What it will not do

- Make a young channel look good. If revenue has not arrived yet it reports 0.00x and says why.

## Worth knowing

Step 0 is reconciling your revenue base against the accounting system. Skip it and every figure downstream is wrong by the difference. This has happened.

Two numbers in its reports are routinely misread, so it labels them hard. Cohort revenue is the lifetime revenue of the customers who arrived in a month, not that month's sales, and the report carries a reconciliation between the two. And a channel's cost divided by all new customers is a ceiling, not that channel's CAC; it gives the ceiling, the measured-share estimate and the proven figure separately.

If a partner runs ads from their own account, ask them for API read access before accepting their PDF as the record.

---

Invoke it by name in your agent (`/marketing-roas`), or just describe the task - the
skill's description lists the phrases that should trigger it.
