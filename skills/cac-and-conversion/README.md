# cac-and-conversion

Work out what a customer costs to acquire, what they are actually worth, and whether your price covers it.

**When in the sequence:** after `marketing-roas`, once at least one cohort has reached the paying stage
**Rough time:** a few hours, mostly spent agreeing definitions

## Before you start, you need

- The output of `marketing-roas`: spend per channel, leads with their source, revenue reconciled against the accounting system
- A list of your funnel stages in your own words, with the paying stage marked
- Payments received per customer, not invoices raised

## It will ask you for

- Which stage is the one that pays, and whether there is more than one
- Whether CAC should be advertising only, or loaded with sales labour and commission
- How long a customer takes to reach the final payment, so incomplete cohorts can be labelled

## What it will not do

- Report one CAC figure. It gives cost per signed customer and cost per completed customer, because where those diverge the gap is the story.
- Use your list price. It computes realised revenue per customer from actual payments, including the customers who bought the first stage and stopped.

## Worth knowing

The most common finding is not that the ads are too expensive. It is that a large share of customers buy the first stage and never reach the one that pays the real fee, so realised revenue per customer is nothing like the list price. Fixing that stage is usually cheaper than buying more customers, and this skill quantifies which.

---

Invoke it by name in your agent (`/cac-and-conversion`), or just describe the task - the
skill's description lists the phrases that should trigger it.
