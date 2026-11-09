# ad-pixel-funnel

The general version of the above: a sealed, channel-separated landing funnel with a browser pixel plus a server-side conversions API, for ANY channel (TikTok, LinkedIn, Meta, Pinterest).

**When in the sequence:** when adding a 2nd or 3rd channel  
**Rough time:** 2-3 hours per channel

## Before you start, you need

- The same website access as above
- A pixel/dataset id and a server access token for the new channel
- An existing funnel page to clone

## It will ask you for

- Which channel, and whether its leads must stay separate from your other channels
- The click-id parameter that channel uses (fbclid, ttclid, gclid, li_fat_id)

## What it will not do

- Merge channels into one funnel. Keeping them sealed is the point: it is what makes attribution possible later.

## Worth knowing

Read `meta-pixel-funnel` first even if you are not using Meta. It explains the pattern in full; this one generalises it.

---

Invoke it by name in your agent (`/ad-pixel-funnel`), or just describe the task - the
skill's description lists the phrases that should trigger it.
