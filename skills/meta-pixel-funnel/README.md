# meta-pixel-funnel

Stand up (or repair) a Meta pixel and Conversions API on your own ad account.

**When in the sequence:** 1st for Meta  
**Rough time:** 2-4 hours, plus waiting on Meta review

## Before you start, you need

- A Meta Business portfolio you control (not an agency's)
- Admin on the Facebook Page and the ad account
- Ability to edit your website's HTML, or a developer who can
- Somewhere to store a server-side access token (env var, secret manager)

## It will ask you for

- Who currently owns any existing pixel on the site
- Your domain, and the exact URL of the page that should count as a conversion
- Whether leads land in a CRM, a spreadsheet, or an inbox

## What it will not do

- Create ads. That is `meta-ads-campaign`.
- Fix attribution for leads that arrived before the pixel existed.

## Worth knowing

Do this BEFORE spending anything. An ad account optimising against a pixel that is not firing will spend the budget and learn nothing.

---

Invoke it by name in your agent (`/meta-pixel-funnel`), or just describe the task - the
skill's description lists the phrases that should trigger it.
