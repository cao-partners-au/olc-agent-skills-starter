# meta-ad-recon

Free competitor ad research on Meta, plus fatigue diagnosis on your own ads. Finds the longest-running ads in your market, writes scripts and edits for your own creative, and tells you why an ad of yours has stopped working.

**When in the sequence:** before you write creative, and weekly from then on
**Rough time:** an hour for the first pass, minutes per week after

## Before you start, you need

- A browser your agent can drive. No login, no API key, no subscription.
- The Facebook page ids of 5 to 10 competitors, or a keyword to go find them
- Somewhere to keep a JSON file per competitor, so history accumulates

## It will ask you for

- Which market or country to filter to
- Who your actual competitors are, including one or two out-of-market businesses with the same funnel shape
- Your own active ads, pulled from your ad account rather than the library, so performance sits beside the comparison

## What it will not do

- Show competitor spend. Nobody outside the EU can see it for commercial ads, and the skill refuses to estimate it.
- Copy anyone's creative. It takes the angle and the structure and rewrites in your voice with your proof.
- Bulk scrape. It works a short watchlist at human pace, because automated collection breaches Meta's terms and gets the IP blocked.

## Two jobs, two data sources

**Competitor recon** uses the free public library, no login. **Fatigue diagnosis** uses your own ad account through the Marketing API, where real frequency, CTR and CPM trends exist. You can run either half on its own.

The fatigue half separates four problems that all look like "performance is down": true creative fatigue (CTR down, frequency and CPM up), auction cost (CPM up, CTR flat), post-click breakdown (CTR fine, leads absent), and audience exhaustion (frequency above 2.5). Each has a different fix, and three of them are made worse by replacing the creative.

## Worth knowing

A logged-out library view renders about 30 ads however far you scroll, while the header tells you the true count. Get past it by partitioning: by media type, by advertiser sub-page, by active status, by keyword, then union on Library ID. Verified that one brand's ~78 ads split into ~47 video, ~6 meme and 1 image, each its own 30-row window. That is why the weekly snapshot matters: paid tools are really selling an archive they started before you cared, and four weeks of your own snapshots tells you what competitors killed quickly versus what survived a quarter. That is the part you cannot buy retroactively.

Longevity is the performance proxy. An ad still running past 60 days is working, because nobody funds a loser for two months. Variant count and relaunches are the next best signals.

Cross-checked against a paid tool on the same advertiser and the durations matched exactly.

---

Invoke it by name in your agent (`/meta-ad-recon`), or just ask what competitors are running.
