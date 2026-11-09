# Adapting these skills to YOUR website / stack

**You do not need to be technical, and you do not run any scripts yourself.** These skills are
written for **Claude Code** to follow — Claude does the technical work; you do the point-and-click
parts inside your ad accounts that only you can do (logging in, approving, generating tokens).

The skills were originally built on one common stack (a **static website on Netlify + a small
serverless form handler + a database CRM**). That's just *one* way to do it. The **principles are
universal** and work on any platform:

- **Own your pixel/ad account** (never build on an agency's).
- **Track each conversion twice** — in the browser *and* server-side — deduplicated.
- **Only count real leads** (fire the conversion after a genuine submission, never on spam).
- **One sealed funnel per channel** so datasets never mix.
- **Your CRM is the source of truth** — never sum ad-platform dashboards.

What changes between stacks is only *how* the pixel and Conversions API get added. Here's the map.

---

## First: which kind of site do you have?

**A. No-code / hosted platform** — WordPress, Shopify, Webflow, Squarespace, Wix, GoHighLevel,
Kajabi, ClickFunnels, Systeme.io, Framer, etc.
→ You almost never need a serverless function or a code repo. These platforms add the browser
pixel through a settings field, and most offer a **native Conversions API** integration (or a
one-click connector). **Just tell Claude which platform you're on** and it will guide you through
that platform's own screens. Skip the parts of the skills that edit HTML files or a
`form-submit.js` — Claude will translate them to your platform's equivalent.

**B. Custom-coded site** (static HTML, React/Next, a repo that deploys to Netlify/Vercel, etc.)
→ The skills apply almost as written; Claude edits the code for you.

If you're not sure, tell Claude the name of the tool you built your website in — it'll figure out
which path you're on.

---

## No-code platform cheat-sheet

For each platform: (1) where the **browser pixel** goes, and (2) how to get the **server-side
Conversions API** (the part that survives ad-blockers and lifts match quality). Claude walks you
through whichever applies — you just click.

| Platform | Browser pixel goes… | Server-side Conversions API |
|---|---|---|
| **WordPress** | A pixel plugin (e.g. PixelYourSite) or Theme → custom head code | Same plugin's CAPI add-on, or a server-side GTM connector (Stape) |
| **Shopify** | Settings → Customer events (custom pixel), or the Meta/TikTok sales-channel app | **Native** — the official Meta & TikTok apps include Conversions API; turn it on |
| **GoHighLevel (GHL)** | Sites/Funnels → Settings → **Tracking Code** (head), or the native pixel field | Native Meta pixel + CAPI in newer GHL; otherwise via a connector (Make/Zapier → CAPI) |
| **Webflow** | Project Settings → Custom Code → Head | Server-side GTM (Stape) or a connector; no native CAPI |
| **Squarespace / Wix** | Settings → custom code / header injection | Via a connector (Stape / Zapier / Make) — no native CAPI |
| **Kajabi / ClickFunnels / Systeme** | Site/funnel settings → tracking / head code | Native pixel field for browser; CAPI via connector if offered |
| **Framer** | Site Settings → Custom Code → Head | Server-side GTM / connector |

**Notes that save you time:**
- The **browser pixel ID is not secret** — it's fine to paste into a settings field.
- The **Conversions API token IS secret** — paste it only into the platform's secure integration
  field, **never into a chat**. Only *you* generate it (in the ad platform) and paste it.
- If your platform has a **native Conversions API** (Shopify, newer GHL, some WordPress plugins),
  use it — you get browser + server tracking with no custom code at all. That's the easiest path.
- If it doesn't, the simplest server-side option is a **connector**: **Stape.io** (server-side
  GTM), or **Zapier/Make** sending a Lead event to the platform's Conversions API when a form is
  submitted. Claude can set the mapping up with you.
- **"Sealing the funnel"** (one channel's pixel only on that channel's pages) still matters. On
  no-code platforms you do it by only adding a channel's pixel to that channel's landing
  page/funnel, not site-wide. Claude will show you exactly where.

---

## What each skill means on a no-code stack

- **google-ads-conversions** → the ideas are identical; you add the Google tag + conversion via
  your platform's tracking-code field or Google Tag Manager, and fire the conversion on your
  thank-you page. Claude adapts the "fire on redirect parameter" pattern to your platform.
- **ad-pixel-funnel / meta-pixel-funnel** → use your platform's native pixel + Conversions API (or
  a connector) instead of the serverless function. Same principles: browser + server, deduped,
  sealed, attributed.
- **meta-ads-campaign** → the campaign *settings and guardrails* (objective, budget, Special Ad
  Category limits, video-not-carousel, paused-first) apply exactly the same whether you build the
  campaign in **Ads Manager (the normal GUI)** or via the API. Non-technical users just use Ads
  Manager and follow the skill's settings guidance — **no CLI or scripts needed.**
- **google-ads-campaign-launch** → pure Ads Manager GUI walkthrough; no stack dependency at all.
- **tiktok-ads-mcp** → this is *reporting* — it reads your live numbers. Works regardless of your
  website stack once your TikTok ad account exists.

---

## The one rule that never changes

Whatever your stack: **you never paste a secret token into a chat, and you never run a command you
don't understand.** Claude tells you exactly which button to click in your own ad account, and
handles everything technical on its side. If a step ever asks *you* to run a script, that's a sign
you're on the custom-code path by mistake — tell Claude your platform name and it'll switch to the
click-through version.
