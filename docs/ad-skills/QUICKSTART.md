# Paid Acquisition Skills: Quick Start

**What this is:** twelve Claude skills that take a business from "we boost posts by hand and nothing is
connected" to "we know what each channel earned and whether our price covers it". They cover paid
ads (Google, Meta, TikTok), tracking that proves where every lead came from, competitor ad research,
SEO and AI-search visibility, and the reporting that ties ad spend to revenue.

**You don't code and you don't run scripts.** You talk to Claude Code, Claude does the technical
work, and you click the buttons inside your own accounts.

## Start in 3 steps

1. **Install once.** Unzip this bundle, then run
   `cp -R claude-code-ad-skills/*/ ~/.claude/skills/`
   or just tell Claude *"install these ad skills for me."*
2. **Tell Claude your website platform** (WordPress, Shopify, Webflow, GoHighLevel, Squarespace, Wix
   or a custom-coded site) so it picks the click-through or the code path. See
   `ADAPTING-TO-YOUR-STACK.md`.
3. **Work through the stages in `README.md`, in order.** In plain English:
   - *"Run a health check on my Meta account"* (`meta-account-healthcheck`, start here if you already run Meta ads)
   - *"Audit my site, and are we showing up in ChatGPT?"* (`open-operator-audit`, free, any time)
   - *"Set up my Google Ads conversion tracking"* (`google-ads-conversions`) **before spending anything**
   - *"Set up my Meta pixel and Conversions API"* (`meta-pixel-funnel`)
   - *"Give TikTok its own tracked landing page and form"* (`ad-pixel-funnel`, for any channel after the first)
   - *"What have our competitors been running longest?"* (`meta-ad-recon`, free, from Meta's Ad Library)
   - *"Launch a Google Search campaign"* (`google-ads-campaign-launch`) / *"Build a Meta campaign"* (`meta-ads-campaign`)
   - *"Run the weekly Meta review"* (`meta-weekly-review`, every Monday: keep, scale or pause each ad)
   - *"How's my TikTok campaign doing?"* (`tiktok-ads-mcp`, once TikTok is running)
   - *"What did each channel earn us?"* (`marketing-roas`) and *"What does a customer cost us, and does our price cover it?"* (`cac-and-conversion`, including how fast a customer pays back)

   Claude walks you through each step and pauses whenever it needs you to click something or approve spend.

## Who does what

**Claude** follows the skill, runs any commands, adds the tracking code or tells you the exact button.
**You** log into your ad accounts, generate tokens, paste them into *your platform* (never into a
chat), approve budgets and press Activate.

## 5 safety rules

1. **Own your accounts.** Never build on an agency's pixel or ad account; you can't take the data with you.
2. **Track before you spend.** Broken tracking can't be backfilled.
3. **Never paste a secret token into a chat.** Only into your platform's secure field.
4. **Everything that spends starts paused.** Going live is always your deliberate click.
5. **Your CRM is the source of truth.** Every platform over-claims; don't add up their dashboards.

## What you'll need (Claude shows you where)

- **Meta:** a Business portfolio you own, an ad account, a pixel, a Conversions API token.
- **Google:** a Google Ads account and a conversion action.
- **TikTok:** a Business Center, ad account and pixel, plus the TikTok Ads MCP connector for reporting.
- **Your CRM:** one field on each lead for its source. If you don't have it, that is the first build.
- **Your accounting system:** read access to paid invoices, for the revenue side of `marketing-roas`
  and `cac-and-conversion`.

## Stuck?

Tell Claude exactly what you see. If a step seems to want *you* to run a script, say your website
platform's name and Claude switches to the no-code, click-through version.

*Skeletons only. You fill in your own accounts and credentials. Nothing here is connected to any live account.*
