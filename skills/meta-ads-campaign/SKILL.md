---
name: meta-ads-campaign
description: >-
  Build, read, and manage in-house Meta (Facebook/Instagram) ad campaigns via the Marketing API
  or walk through Ads Manager. Use when asked to "run a Meta ad campaign", "create a Facebook
  ad via API", "set up a Meta system user token", "activate the Meta campaign", "Meta ad won't
  deliver", or "pull Meta ad spend / CPL". Covers System User token setup (including the
  chicken-and-egg traps), campaign/adset/ad creation with PAUSED-by-default guardrails,
  Special Ad Category targeting limits, the creative playbook, carousel-vs-video gotcha, reading
  creative and destination URLs back for QA, and activation.
---

# Meta Ad Campaigns via the Marketing API

## Two modes — pick one before starting

**API/CLI mode:** `scripts/meta-ads.ts` — thin wrapper over Graph v21.0. Every CREATE is dry-run
(prints payload) unless `--commit`. Activation is the only command that spends. Local dev only,
never a deployed service. The token can SPEND MONEY.

**GUI mode:** the operator clicks through Ads Manager. Ask Claude to walk through the settings using
this skill. No scripts, no token. All the same guardrails apply.

---

## Phase 0 — System User token (required for API mode; skip for GUI mode)

A specific chain — each step blocks the next:

1. Business Settings → Users → System Users → Add → role: Admin
2. Create a Marketing API app: developers.facebook.com → Create App → use case
   **"Create & manage ads with Marketing API"** → App type: Business → **select your Business
   portfolio** (critical — this ties the app to the portfolio)
3. Assign assets to the system user (Add Assets, Full control): the App, Facebook Page, Ad
   account, Dataset/Pixel. The pixel is under **"Datasets"** not "Pixels" (Meta renamed them).
   Search by numeric ID, not name.
4. **CHICKEN-AND-EGG:** you cannot generate a token until the app is assigned to the system user.
   Assign the app FIRST, then Generate token.
5. Generate token → select the app → tick scopes: `ads_management, ads_read, business_management`
6. **Saving the token:** Meta tokens can contain shell-special chars (`|`). Never `echo "$TOK" > file`
   — it silently truncates. Create the file and paste via editor: `open -e <path>`. Never inline
   the token in a shell command.

---

## Phase 1 — campaign settings (non-negotiable)

- **Objective:** `OUTCOME_LEADS`, `status: PAUSED`
- **Special Ad Category:** if the ads are about jobs, housing, credit/finance or social issues, set
  `special_ad_categories: ['EMPLOYMENT']` — legally required. This bans age/gender/
  detailed-interest targeting. Location only.
- **`is_adset_budget_sharing_enabled: false`** — required when budget lives on the ad set
  (omit → 400 error)
- **Ad set budget:** `daily_budget` in cents. `billing_event: IMPRESSIONS`.
  `optimization_goal: OFFSITE_CONVERSIONS`. `bid_strategy: LOWEST_COST_WITHOUT_CAP`.
- **Targeting under Employment Special Ad Category:** no age/gender/interests. Use capital-city
  metros. `targeting_automation.advantage_audience: 1`.
- **Budget:** Meta needs ~50 conversions/week to exit learning — don't go below ~$25/day. Scale
  after initial test read.

---

## Phase 2 — creative: use VIDEO/REEL, not carousel

Promoting an existing CAROUSEL Instagram post throws a hard **"WhatsApp number required (#2446880)"**
blocker. It's baked into the carousel post and cannot be fixed from ad settings.

VIDEO/REEL posts:
- Don't trigger the blocker
- Deliver to more placements
- Set Website URL / CTA link to the landing page made for this channel (e.g. `/offer/meta`)
- CTA: `LEARN_MORE`

**Ads per ad set at low budget:** ~3. More fragments learning; fewer gives nothing to optimise.

**Primary text for cold audience:** first ~125 chars are all that show before "…See more". Hook
lives there. Name the shift, the role, what you do, a clear CTA. Specific > punchy for unfamiliar
offers (nobody searches a job title or product that is new to the market, so explain it).

---

## Phase 3 — what the API can read (no App Review needed for your OWN assets)

Older advice said reading Page posts or Instagram media needed Meta App Review. **It doesn't for
your own business's Page and Instagram account.** Standard Access is enough once the token has the
right scopes (`pages_read_engagement`, `pages_show_list`, `instagram_basic`,
`instagram_manage_insights`, `read_insights`) and the Page and Instagram account are assigned to the
System User.

With that you can:
- ✅ list Page posts and Instagram media, and read Reel/post insights (reach, views, saves, shares)
  to pick organic winners to boost
- ✅ read campaign, ad set and ad status, budgets, optimisation goal, pixel, and each ad's creative,
  **including its destination URL and URL parameters** (`creative{object_story_spec,url_tags}`)
- ✅ build an ad from an existing post ID

**QA consequence:** after building or editing ads, read every live ad's destination URL back via
the API and confirm each points at the intended landing page. A wrong path fires the wrong pixel or
loses attribution, and nothing in Ads Manager will warn you.

**Meta's AI text lock:** when promoting an existing Instagram post, "Advantage+ creative" text
generation is often switched on by default and pins the caption read-only. Turn the text variations
toggle off, or build the creative via the API with your own `object_story_spec` copy.

---

## Phase 4 — verify + activate

- Draft ads (built in GUI but not published) are invisible to the API until published. Publishing
  with paused parents does NOT spend.
- Ready state per ad: `effective_status: ADSET_PAUSED`, `configured_status: ACTIVE`, no
  `ad_review_feedback`. `ADSET_PAUSED` = passed review, held by paused ad set. Rejection =
  `DISAPPROVED` / `WITH_ISSUES`.
- **Activation needs BOTH campaign AND ad set set to ACTIVE.** One alone won't deliver.
- Activation SPENDS MONEY — get the business owner's explicit go before every activate command.
  `activate --id <campaign> --commit` then `activate --id <adset> --commit`, then read back
  `effective_status: ACTIVE`.
- Learning phase is real: early CPL is noisy. Don't judge before ~50 clicks / a few days.

---

## What to ask the business owner before starting

- GUI or API/CLI mode?
- Which Facebook Page + Instagram account?
- Landing page URL for this channel (e.g. `/offer/meta`)?
- Daily budget?
- Does a Special Ad Category apply (jobs, housing, credit/finance, social issues)?
- Which existing Instagram post to promote (for creative)?

---

## Video ads from local files (added Sep 2026)

Boosting an existing Reel and uploading your own file are two different paths, and
the second has traps the first does not.

**A file on disk must be posted as multipart `source`, not as a base64 `bytes`
field.** Ad creatives routinely run 40MB or more; base64 inflates that by a third
into a single form value and Meta rejects it. (The `bytes` field is fine for
IMAGES, which is why the mistake is easy to make.)

**Meta transcodes asynchronously, so a fresh `video_id` is not usable yet.**
Build a creative against one still processing and it gets no thumbnail, and the
ad renders a black frame in the feed. Poll
`GET /{video_id}?fields=status,thumbnails` until `status.video_status == "ready"`
AND at least one thumbnail exists. On a batch of five 40MB files, two were still
processing after the other three finished, so check each one rather than
assuming a fixed wait.

**Always set the thumbnail explicitly.** Take the `is_preferred` entry from
`GET /{video_id}/thumbnails` and pass it as `image_url`. Reels in particular fail
outright without one (`error_subcode 1443226`).

**Opt out of Advantage+ creative on video creatives too.** Set
`degrees_of_freedom_spec.creative_features_spec.advantage_plus_creative.enroll_status = "OPT_OUT"`.
Enrolled, Meta rewrites your primary text on delivery. This is documented for
existing-post ads and is easy to assume does not apply to a plain video creative.
It does. If your ads carry industry-specific or offer-specific copy, that copy is
silently replaced without it.

**Keep budget changes away from targeting changes.** Meta MERGES a budget update
but REPLACES the whole targeting object. Sharing one code path means a partial
targeting write silently discards placements and any Special Ad Category
settings. Write `daily_budget` on its own.

---

## Reading the numbers back

**Cost per lead is not a field.** Meta reports the conversion inside `actions`
and `cost_per_action_type`, under `lead` or `offsite_conversion.fb_pixel_lead`,
so CPL has to be read out of those arrays. An ad with spend and NO lead action
has no CPL at all, and that absence is the finding, not a gap to fill.

**Low spend is not evidence an ad is bad.** Meta concentrates budget on two or
three winners rather than testing evenly, so in an ad set carrying a dozen ads
most will show near-zero spend. Recommending a pause on that basis is reading the
mechanism as a verdict. Judge an ad Meta actually FUNDED and that produced
nothing; leave the starved ones alone, or split them into their own ad set so
they get a fair test.

**Adding creatives re-enters the learning phase for the whole ad set**, not just
the new ads. Any report covering that period should say so, or the reader will
draw a trend out of noise.

**The pixel count will not match your CRM, and that is correct.** If the pixel
fires when a booking calendar OPENS while the CRM row is written when a form is
SUBMITTED, the pixel reads slightly high. Reconcile the two and explain the
difference. Do not treat it as leads lost, and do not quietly report whichever
number flatters.

**Spend is a different question from revenue.** For what the advertising actually
EARNED, see the `marketing-roas` skill in this bundle: it joins ad spend to lead
attribution and to invoiced revenue, and carries the traps that make a naive
return-on-ad-spend figure wrong.
