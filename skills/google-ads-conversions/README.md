# google-ads-conversions

Set up, audit or repair Google Ads conversion tracking, including the case where it has silently never fired.

**When in the sequence:** 1st for Google  
**Rough time:** 1-2 hours

## Before you start, you need

- Admin on the Google Ads account
- Access to the site's tag setup (GTM or hardcoded)
- Knowing who else has a tag on the site - agencies often leave one behind

## It will ask you for

- Who owns the AW- tag currently on the site
- Which page or action counts as a conversion
- Whether several form types share one thank-you page

## What it will not do

- Create campaigns. That is `google-ads-campaign-launch`.

## Worth knowing

Start with Phase 1, the audit. Conversion tracking that is configured but never fires looks identical to tracking that works, until you check.

---

Invoke it by name in your agent (`/google-ads-conversions`), or just describe the task - the
skill's description lists the phrases that should trigger it.
