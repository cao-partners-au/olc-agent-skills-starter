# meta-weekly-review

A Monday-morning review of your Meta ads that ends in a decision for every ad, keep, scale, pause,
fix or hold, based on what each ad's leads actually did, not just how cheap they were.

**What it needs from you (once):**
1. A Meta System User token with `ads_read`, saved to a file on your computer (see `meta-ads-campaign`).
   Set `META_AD_ACCOUNT` and `META_TOKEN_FILE`.
2. Ideally, a CSV export from your CRM: one row per lead with `created_at, ad_id, booked, showed, won`.
   For `ad_id` to exist, add `utm_content={{ad.id}}` to your ads' URL parameters and make your forms
   save it. Without this the review still runs, but only on Meta's numbers.

**Then ask:** "Run the weekly Meta review." It changes nothing; you approve every pause or budget move.

Tip: schedule it for every Monday morning.
