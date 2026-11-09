# meta-account-healthcheck

**Start here if you already run Meta ads.** A one-off, read-only audit of your Meta ad account that
scores eight areas green / amber / red (ownership, tracking, structure, performance, fatigue,
placements, creative alignment with Meta's current algorithm, and compliance), then gives you the
top 5 fixes in order of money saved and a 30-day plan.

**What it needs from you:**
1. A Meta System User token with `ads_read`, saved to a file on your computer (the
   `meta-ads-campaign` skill walks you through it). Set `META_AD_ACCOUNT` and `META_TOKEN_FILE`.
2. Three answers: what a paying customer is worth, what counts as a good result, and whether you
   track which leads become customers.

**Then ask:** "Run a health check on my Meta account." It changes nothing; you decide what to fix.
After the fixes, run `meta-weekly-review` every Monday.
