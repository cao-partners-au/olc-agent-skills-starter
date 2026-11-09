# meta-ads-campaign

Build, read and manage Meta campaigns, either through the Marketing API or by walking through Ads Manager.

**When in the sequence:** 2nd for Meta, after the pixel  
**Rough time:** 1-2 hours to first campaign

## Before you start, you need

- A working pixel (see `meta-pixel-funnel`)
- For API mode: a System User token with ads_management, ads_read, business_management
- A funded payment method on the ad account

## It will ask you for

- Whether your ads fall under a Special Ad Category (employment, housing, credit, politics) - this legally restricts targeting
- Your daily budget, and which geography
- Whether you want API mode or to click through Ads Manager

## What it will not do

- Spend money on its own. Everything is created PAUSED and activation is a separate, explicit step.

## Worth knowing

Includes video-upload traps, Advantage+ creative opting out, and how to read cost per lead back out of the API.

---

Invoke it by name in your agent (`/meta-ads-campaign`), or just describe the task - the
skill's description lists the phrases that should trigger it.
