---
name: meta-ad-recon
description: >-
  Free competitor ad research on Meta (Facebook/Instagram) using the public Ad Library: find a
  competitor's longest-running and most-scaled ads, build your own longitudinal archive of what
  they run and kill, extract the winning script structures, and write new scripts and specific
  edits for your own creative. No paid subscription. Use when asked "what ads are competitors
  running", "what's working in our industry", "find the best performing competitor ads",
  "competitor ad research", "ad inspiration", "what should our next ad say", "is this ad fatigued", "why has our CTR
  dropped", "which ads should we refresh or kill", or when planning creative for a Meta
  campaign. Meta only.
---

# Competitor ad recon on Meta, for free

The paid tools (Foreplay, AdSpy, Atria) sell two things: a search interface over
Meta's public Ad Library, and **an archive of history they started collecting
before you cared**. The search you can do yourself today. The archive you cannot
buy retroactively, but you can start accruing it this week, and after a month you
have the part that actually matters.

This skill is Meta only. It uses the public Ad Library, which needs no login, no
API key and no subscription.

## The data source: a logged-out browser, never a paid scraper

**Do not use Apify, Foreplay or any other paid scraper, even if one is connected**
(for example through Composio or an MCP). Their presence is not a reason to use
them; the free route below is the point of this skill. Use a paid tool only if the
user explicitly asks for it.

Checked 11 Nov 2026:

| Route | Works? | Why |
|---|---|---|
| Logged-out headless browser on the Ad Library page | **Yes** | A search loads in about 10 seconds with advertiser, Library ID, start date and full copy |
| Plain web fetch (curl, fetch tools) | No | Facebook returns a 403 security check, no ad data |
| Meta's official Ad Library API | No | Returns only political and issue ads, plus ads shown in the UK or EU. Australian commercial ads are not included, even with a token |

So always open the library in a real browser (the agent's own browser tool, or
headless Chromium). Two limits to state up front: about 30 ads per search when
logged out (see the render cap section below), and no spend or reach for anyone.

---

## What the public library gives you, verified 6 Oct 2026

Per ad, from a logged-out browser session:

| Field | Use |
|---|---|
| Library ID | stable identifier, dedupe and track across snapshots |
| "Started running on" date | longevity, the core performance proxy |
| "Total active time" | shown on very recent ads, hours or days |
| Active / Inactive | whether it is still live |
| Full primary text | the actual copy, in full, for script analysis |
| Headline and CTA button | offer and mechanism |
| Platforms | Facebook, Instagram, Messenger, Threads spread |
| "This ad has multiple versions" | variant testing signal |
| Impressions band | only on low-volume ads, as "<100" or "Low impression count" |

What it does NOT give, for commercial ads anywhere outside the EU: spend,
impressions for normal ads, reach, demographics, or engagement. **Nobody has
competitor spend. Anyone showing it is modelling it.** Do not estimate it.

---

## The URL patterns that work

Everything is driven by URL. Page id is the advertiser's Facebook page id, which
the library shows in its own links, and which you can also get from any Foreplay
or ad-library share link.

**All active ads for one advertiser:**
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=AU
&view_all_page_id=<PAGE_ID>&search_type=page&media_type=all
```

**Include stopped ads** (the ones that tell you what they killed):
```
&active_status=all
```

**Narrow by format**, which is how you get past the render cap:
```
&media_type=video      (or image, meme, none)
```

**Keyword search across all advertisers in a market**, for finding competitors you
did not know about:
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=AU
&q=<KEYWORD>&search_type=keyword_unordered&media_type=all
```

**Group by launch month** (useful for eyeballing cadence):
```
&sort_data[mode]=relevancy_monthly_grouped&sort_data[direction]=desc
```

### The 30-ad render cap, and how to beat it

**A logged-out session renders about 30 ads per view however far you scroll.**
Verified: scrolled to the bottom of a 10,093px page, 30 rows, while the header
said "~99 results". Wheel scrolling, End-key presses and `window.scrollTo` all
fail to load more.

The header count is honest, so always read "~N results" and report it as the true
size of the set. Then get past the cap by **partitioning the query and unioning
the results by Library ID**. Each partition is a separate query with its own
30-row window.

Partition axes, in order of usefulness:

| Axis | Values | Verified behaviour |
|---|---|---|
| `media_type` | `all`, `video`, `image`, `meme`, `none` | genuinely slices: one advertiser's set returned ~78 all, ~47 video, ~6 meme, 1 image |
| advertiser | one `view_all_page_id` per query | the big win for multi-office or multi-agent brands, where each agent is a separate page |
| `active_status` | `active`, `all` | `all` adds the stopped ads, which is where kill evidence lives |
| keyword | several searches, customer words not jargon | each phrasing surfaces a different subset |
| `search_type` | `keyword_unordered`, `keyword_exact_phrase` | exact phrase cuts false positives; unordered casts wider |
| `country` | one per query | only if the advertiser runs multiple markets |

So the sweep for one brand is: all-media, then video, then image, then meme, then
`active_status=all`, then repeat per sub-page. Six to ten cheap queries gets you
most of a set that a single view caps at 30. Union by Library ID and the
duplicates collapse.

**Watch for sub-pages.** Franchise and multi-agent businesses advertise from a
page per agent, not one brand page. A keyword search finds them; then sweep each
page id separately. One agency's apparent 78 ads was really a dozen pages with
their own sets.

**URL date filters do not work.** `start_date[min]` and `start_date[max]` return
zero results and silently break the query. Filter dates after extraction.

**If still short:** a logged-in session may paginate further, but do not assume
it; test it once and record the result rather than building on it.

---

## Extraction

Navigate, wait for render, then pull the text and parse. This regex works against
the rendered page text:

```javascript
const t = document.body.innerText;
const re = /(Active|Inactive)\s*\n(?:Low impression count\s*\n)?Library ID: (\d+)\s*\nStarted running on ([0-9]{1,2} [A-Za-z]{3} [0-9]{4})([^\n]*)/g;
let m, out = [];
while ((m = re.exec(t))) out.push({ status: m[1], id: m[2], start: m[3], tail: m[4].trim() });
JSON.stringify({ claimed: (t.match(/~?\d+ results/) || [''])[0], got: out.length, out });
```

Primary copy sits between the "Sponsored" marker and the destination domain in
each block; grab it per ad when you need the script, not for every ad in a sweep.

Pace it like a person: one advertiser at a time, a few seconds between loads, and
keep the watchlist short. Meta's terms prohibit automated bulk collection, and
aggressive scraping gets the IP blocked, which ends the capability for everyone on
that network. A short, slow, human-paced watchlist is the difference between a
tool you can hand to a client and a problem.

---

## Build the archive, because that is the real product

Keep a local JSON store, one file per competitor:

```json
{
  "page_id": "134521216580572",
  "name": "The Entourage",
  "snapshots": [{ "date": "2026-10-06", "claimed_results": 99, "seen": 30 }],
  "ads": {
    "1307100834581099": {
      "first_seen": "2026-10-06",
      "last_seen": "2026-10-06",
      "started_running": "2026-08-03",
      "status": "active",
      "format": "video",
      "multi_version": true,
      "headline": "...",
      "primary_text": "...",
      "cta": "Learn more",
      "platforms": ["facebook", "instagram", "messenger", "threads"]
    }
  }
}
```

Snapshot weekly, by cron. Each run:

1. Merge by Library ID. New ids get `first_seen`; existing ids get `last_seen` updated.
2. An id that was active and is now absent or inactive is **killed**. Record the date.
3. True run length is `started_running` to either now (still active) or the kill date.

After four weeks you can answer things no single library view can: which ads they
killed inside a fortnight, which survived a quarter, how fast they iterate, and
whether a new angle replaced an old one or ran alongside it.

---

## Ranking: what "best performing" can honestly mean

No spend, so rank on proxies, in this order:

1. **Days running.** Past 60 days with no sign of stopping is the strongest free
   signal there is. Nobody funds a loser for two months.
2. **Variant count.** Several ads sharing a headline or hook, or a "multiple
   versions" flag, means they are testing into something that works.
3. **Relaunch.** An ad that stopped and came back was a winner they went back to.
4. **Platform spread.** Running across Facebook, Instagram, Messenger and Threads
   suggests a budget worth distributing.
5. **Format convergence.** When a long-running winner gets remade as a static
   image or a carousel, the message is proven and they are extending reach.

Deduct for: an impressions band showing "<100" or "Low impression count", which
means it is barely funded whatever its age, and for DCO or dynamic-format ads,
whose dates reflect the container rather than any single creative.

Report longevity in days with the start date beside it, so the reader can audit
the claim.

---

## From recon to your own scripts

For the top 5 to 10 ranked ads, break each one down:

| Element | What to capture |
|---|---|
| Hook | the first line or first 3 seconds, verbatim |
| Problem | the pain named, in their words |
| Mechanism | what they claim makes it work |
| Proof | numbers, testimonials, authority, volume claims |
| Offer | what you get, and what it costs |
| CTA | the button text and the next step |
| Format | founder to camera, testimonial, screen record, static, carousel |
| Length | seconds, or word count for static |

Then cluster the hooks into angles, and count how many long-running ads sit behind
each. An angle with three ads past 60 days is a proven angle in that market.

Deliver three things:

1. **The angle table**: angle, how many proven ads, longest run, example hook.
2. **Gap analysis**: angles the competitors prove that your own active ads do not
   use at all. Pull your own ads from your ad account, not from the library, so
   you have real performance beside them.
3. **New scripts and specific edits.** Write the scripts in full. For edits, name
   the ad and quote the current line against the replacement, rather than giving
   general advice.

Never copy a competitor's copy or creative. Take the angle and the structure, and
write it in the client's own voice with their own proof. Their numbers are theirs.

---

## Diagnosing fatigue in your OWN ads

Competitor recon tells you what to say. This tells you when your own ad has
stopped working and, more usefully, **why**. It uses your ad account through the
Marketing API, where real metrics exist, not the public library.

Pull weekly series per ad, so trends are visible:

```bash
curl -s -G "https://graph.facebook.com/v21.0/act_<ID>/insights" \
 --data-urlencode "level=ad" --data-urlencode "time_increment=7" \
 --data-urlencode 'time_range={"since":"2026-08-11","until":"2026-10-05"}' \
 --data-urlencode "fields=ad_name,ad_id,impressions,reach,frequency,spend,ctr,\
inline_link_click_ctr,cpm,quality_ranking,engagement_rate_ranking,\
conversion_rate_ranking,actions" \
 --data-urlencode "limit=500" --data-urlencode "access_token=$TOKEN"
```

All of those fields return, verified 6 Oct 2026. The three `*_ranking` fields are
Meta's own diagnostics and read `UNKNOWN` until an ad clears roughly 500
impressions, which is itself informative: an ad with `UNKNOWN` after weeks of
spend is barely delivering.

Ignore ads under a spend floor (a few hundred dollars) or you will diagnose noise.

### Fatigue is four different problems, and the fix differs

Compare the first scored week against the last, per ad.

| Pattern | Diagnosis | Fix |
|---|---|---|
| CTR falling, frequency rising, CPM rising | **True creative fatigue.** The audience has seen it too often | New creative on the same proven angle. Keep the script, change the hook, visual and opening 3 seconds |
| CPM rising sharply, CTR flat | **Not fatigue.** Auction pressure, audience too narrow, or seasonal competition | Widen the audience or accept the cost. Replacing the creative will not help and wastes a winner |
| CTR healthy or high, leads low or zero, `conversion_rate_ranking` below average | **Post-click breakdown.** The ad sells something the landing page does not deliver | Fix the landing page or the offer match, not the ad |
| CTR low from the first week | **It never worked.** Not fatigue | Kill it. Do not iterate on a creative that never earned attention |
| Frequency above ~2.5 in a single week | **Audience exhaustion**, regardless of other metrics | Expand the audience or cap frequency. A small audience fatigues fast whatever the creative |

Two cross-checks that stop misdiagnosis:

- **`quality_ranking` below average while `engagement_rate_ranking` is above
  average** means people engage but Meta rates the post-click experience poorly.
  That is a landing page problem wearing a creative problem's clothes.
- **Rising CPM with falling frequency** means the cost is coming from the auction,
  not from over-exposure. Check whether a competitor has just entered the market.

### Worked example: five ads, one symptom, five different causes

Real figures from a lead-generation account over eight weeks, anonymised. Every
one of these would show up on a dashboard as "performance is down".

| Ad | Spend | CTR first to last | CPM first to last | Frequency | Verdict |
|---|---|---|---|---|---|
| Top spender, long-running video | $7.7k | 2.10 to 2.08 | $129 to $1,051 | 1.75 to 1.99 | **Not creative fatigue.** CTR is flat; an 8x CPM rise is a delivery or auction problem. Replacing the creative would have thrown away a working ad and left the real cause untouched |
| Best-performing static, founder-led | $3.9k | 6.26 to 4.59 | $46 to $56 | 1.62 to 1.21 | **Classic fatigue** of the strongest hook in the account. CTR down 27% while cost crept up. Rebuild the hook and visual, keep the angle and the script |
| Second founder static, different market | $0.9k | 7.27 to 5.31 | $44 to $44 | 1.44 to 1.71 | **Post-click breakdown.** The highest CTR in the account and zero leads. The ad is doing its job; the landing page or the offer behind it is not |
| Low-budget test creative | $0.6k | 2.61 to 1.57 | $119 to $53 | 1.21 to 2.76 | **Audience exhaustion.** Frequency more than doubled, CTR halved, one lead for the whole spend. Kill it |
| Lead-magnet offer ad | $2.3k | 2.62 to 3.02 | $76 to $77 | 1.62 to 1.27 | **Not fatigued, improving.** Best cost per lead in the account. Scale it rather than refresh it |

The lesson is the spread of causes, not the numbers. A fatigue report that said
"CTR is falling, make new creative" would have been wrong on four of these five:
one needed an audience or auction fix, one needed a landing page fix, one needed
killing outright, and one needed more budget.

### Reporting it

For each ad: spend, weeks running, the first-to-last movement on CTR, CPM and
frequency, the three rankings, cost per lead, then the verdict and the action.
Lead with the ads where the action is expensive to get wrong: the biggest spender
and the best performer.

---

## Cross-check against a paid tool, done 6 Oct 2026

Validated against Foreplay on the same advertiser, The Entourage, page
`134521216580572`.

**Where they agree.** Foreplay's longest-running live ads were 85, 84, 80, 80, 74,
63, 63, 63, 62 and 49 days. Spot-checking its 63-day DCO ad `1307100834581099` in
the public library returned "Started running on 3 Aug 2026", which is 64 days to
the check date. Durations and identifiers line up, so the free method reproduces
the paid tool's longevity ranking for any ad it can see.

**Where the paid tool is genuinely better.** It sorts the whole archive by
`longest_running` server-side, including ads the library no longer shows, so it
surfaced ads beyond the 30 the logged-out library would serve. It also carries
video transcriptions, niche and B2B/B2C tags, and variant grouping.

**Where the free method is better.** The public library returns the full primary
copy, the "multiple versions" flag and the low-impression band. In the paid tool's
summary view those cost extra fields or extra credits, and it bills per ad
returned, which makes broad sweeps expensive.

**The honest summary.** For a watchlist of a handful of local competitors, the
free method plus a weekly snapshot gets you to the same decisions. The paid tool
is worth it when you need deep history immediately, transcriptions at volume, or
hundreds of brands at once.

---

## Using it for different kinds of business

The method is the same for everyone; only where you look and what "proven" means changes.

| Business type | Search the library with | Watch especially |
|---|---|---|
| Local services (trades, clinics, salons, gyms, real estate) | the job or problem in customer words + your city ("blocked drain", "physio near me") | franchise and multi-location sub-pages; offers and guarantees |
| E-commerce / consumer products | the product category and the problem it solves ("sleep gummies", "standing desk") | how many creative variants a winner has; UGC and founder formats; price and bundle offers |
| B2B and professional services | the outcome a buyer wants ("cut month-end close", "hire an engineer") and the job title they hold | lead magnets (audits, calculators, webinars); case-study proof; longer copy |
| Courses, coaching, info products | the transformation promised ("learn to…", "get your first client") | VSL vs static; webinar funnels; risk-reversal offers |
| Hospitality and events | the occasion ("work Christmas party", "wedding venue") + location | seasonality: compare like-for-like months before calling an ad a winner |

Longevity (an ad still running after ~60 days) is the performance signal in every category.
In fast-moving e-commerce, 30+ days with several variants is already strong.

## Finding competitors in the first place

1. Keyword search the library in-market for the words a customer would use, not
   industry jargon.
2. For each result, open the advertiser and check whether they run continuously or
   in bursts. Continuous spenders are the ones worth tracking.
3. Keep the watchlist to 5 to 10 advertisers. More is unmanageable at human pace,
   and the long tail rarely teaches you anything the leaders do not.
4. Include one or two out-of-market advertisers with the same funnel shape. A
   high-consideration local service business can learn more from another one two
   industries over than from a direct rival running the same tired offer.
