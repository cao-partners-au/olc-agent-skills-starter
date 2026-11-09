# tiktok-ads-mcp

Query a TikTok Ads account live through the official TikTok for Business MCP server.

**When in the sequence:** after TikTok funnel is live  
**Rough time:** 30 minutes to connect

## Before you start, you need

- A TikTok for Business advertiser account
- An MCP-capable client (Claude Desktop, OpenClaw, or similar)

## It will ask you for

- Your advertiser id
- Whether write tools should be enabled at all

## What it will not do

- Build the funnel. Use `ad-pixel-funnel` for that.

## Worth knowing

The server exposes WRITE tools alongside reads. Treat it read-only unless a human has explicitly approved a specific write.

---

Invoke it by name in your agent (`/tiktok-ads-mcp`), or just describe the task - the
skill's description lists the phrases that should trigger it.
