---
name: tiktok-ads-mcp
description: >-
  Query a TikTok Ads account live via the official TikTok for Business MCP server, connected
  as an MCP connector in Claude Code. Use when asked "how's the TikTok campaign doing", "cost per
  lead", "which creative is winning", "pull the pixel stats", "what's spend today", or any
  request for live TikTok Ads numbers. Read-only by default — write tools (budget changes,
  campaign updates) require explicit approval each time. The funnel build half of this is the
  ad-pixel-funnel skill.
---

# TikTok Ads MCP — Live Ad Account Access

## Connection

Add the official TikTok Ads MCP as a **custom connector in the Claude desktop app** (Settings ›
Connectors › Add custom connector, using the server URL from TikTok for Business). It then appears
in Claude Code sessions. It authenticates via TikTok's own OAuth (in-browser flow; the account owner
approves with their TikTok Business account).

If the session says "connector requires authentication", the OAuth lapsed — the account owner
re-approves via the Connectors panel. A non-interactive session can't do OAuth.

Tools surface under the connector's UUID prefix. Load their schemas before calling:
`ToolSearch` query `select:mcp__<uuid>__auth_advertiser_get,mcp__<uuid>__report_integrated_get,...`

## Key account info

| Field | Value |
|---|---|
| Advertiser ID | (fill in after `auth_advertiser_get`) |
| Pixel ID | (fill in after `pixel_list_get`) |
| Pixel Code | (fill in from Events Manager) |
| Business Center ID | (fill in from TikTok Business Center) |
| Optimization event | `FORM` (browser `Lead` maps to it) |

Confirm anytime with `auth_advertiser_get` (no args → lists authorized accounts).

## Read recipes (safe — use freely)

**Campaign performance:**
```
report_integrated_get:
  report_type: "BASIC"
  data_level: "AUCTION_CAMPAIGN"
  advertiser_id: "[ID]"
  dimensions: ["campaign_id"]
  metrics: ["campaign_name","spend","impressions","clicks","ctr","cpc","cpm",
            "conversion","cost_per_conversion","conversion_rate"]
  start_date: "YYYY-MM-DD"
  end_date: "YYYY-MM-DD"
  page_size: 50
```

**Per-creative breakdown** (find which creative wins):
```
data_level: "AUCTION_AD"
dimensions: ["ad_id"]
metrics: [...above + "adgroup_name","ad_name"]
```

**Daily time series:** add `stat_time_day` to `dimensions`. Keep range ≤ 30 days.
Dates use the ad account's timezone. Currency = account currency.

**Pixel config:** `pixel_list_get` (advertiser_id) → returns configuration, not fired-event counts.
For actual fired Lead counts, use TikTok Events Manager or an events report.

**Other reads:** `advertiser_info_get`, `dmp_custom_audience_list_get`,
`dmp_saved_audience_list_get`, `custom_conversion_list_get`, `creative_portfolio_list_get`,
`identity_get`. Use `tool_list → tool_get → tool_execute` to reach tools not surfaced by default.

## Write tools — approval-gated, never autonomous

The MCP also exposes Smart+ WRITE tools: `smart_plus_campaign_create/update/status_update`,
`smart_plus_adgroup_create/update/status_update/budget_update`, `smart_plus_ad_create/update/
status_update`. These can create campaigns, change budgets, pause/activate ads.

**Rules:**
- Default to READ tools only (`*_get`, `*_list_get`, `report_integrated_get`)
- NEVER call a create/update/status/budget tool without **explicit approval from the business owner in the
  current conversation**. Draft the exact change, show it, wait for a clear yes, then do ONE
  change at a time and read back the result
- Treat like DRY_RUN discipline — this account spends real money

## Interpreting the numbers

- TikTok traffic is cheap (~$0.20-0.36/click, ~$2 CPM)
- **CTR benchmark ~1%.** Sub-0.4% ads are laggards. 0% after 1k+ impressions = dud.
- **Vertical-specific, benefit-led creatives beat generic FOMO.** Concrete named-audience
  benefit → >1% CTR. "Evolve or die / breaking news" generics → sub-0.4%.
- **0 conversions on a ~1-day / <100-click campaign is noise, not a broken pixel.** At 1-2%
  landing CR, ~71 clicks predicts ~1 lead. Chase an attribution gap only after 200+ clicks
  still at 0.
- Let a new campaign run at least 2 days before moving budget — video views also build followers
  + a retargetable engaged audience that CPL alone misses.
- `ViewContent` is worth adding as a campaign event (mid-funnel signal). Events like
  `Contact`/`Search` that don't map to your funnel — ignore them.

## Roadmap (future TikTok workstreams)

1. CRM-events postback — POST outcome events to TikTok Events API (`event_source: "crm"`) so
   campaigns optimise for real outcomes, not just form fills. Pure API + existing
   `TIKTOK_EVENTS_API_TOKEN`; no MCP OAuth needed.
2. Reporting → warehouse — scheduled pull of `report_integrated_get` into database for dashboards.
3. Audience sync — push CRM segments as Custom/Lookalike audiences.
