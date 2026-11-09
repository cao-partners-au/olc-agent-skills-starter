#!/usr/bin/env python3
"""
First-run health check of a Meta ad account with history. READ ONLY: it never changes anything.

Collects everything the meta-account-healthcheck skill scores:
  account + ownership, pixel/dataset health (browser vs server events), campaign/ad set/ad
  structure, 13 weeks of weekly results, last-30-day ad performance, placements, and a creative
  audit against the 2025+ "Andromeda" playbook (format mix, new ads per week, near-duplicate copy,
  copy length, targeting breadth, URL tracking parameters).

Setup:
  export META_AD_ACCOUNT=act_1234567890
  export META_TOKEN_FILE=~/secrets/meta_token.txt   # System User token with ads_read (+ business_management helps)
Usage:
  python3 healthcheck.py                 # last 90 days, ending yesterday
  python3 healthcheck.py --days 180
Writes /tmp/meta-healthcheck.json and prints a readable summary for the agent to score.
"""
import argparse, collections as C, datetime as D, difflib, json, os, re, statistics as S, urllib.parse, urllib.request

ap = argparse.ArgumentParser(); ap.add_argument("--days", type=int, default=90); a = ap.parse_args()
ACCOUNT = os.environ["META_AD_ACCOUNT"]
TOKEN = open(os.path.expanduser(os.environ["META_TOKEN_FILE"])).read().strip()
API = "https://graph.facebook.com/v21.0"
END = D.date.today() - D.timedelta(days=1)
START = END - D.timedelta(days=a.days - 1)
RNG = json.dumps({"since": START.isoformat(), "until": END.isoformat()})
R30 = json.dumps({"since": (END - D.timedelta(days=29)).isoformat(), "until": END.isoformat()})

def get(path, **q):
    q["access_token"] = TOKEN
    url = f"{API}/{path}?" + urllib.parse.urlencode(q)
    try: return json.load(urllib.request.urlopen(url))
    except urllib.error.HTTPError as e: return {"error": json.load(e).get("error", {}).get("message", str(e))}

def many(path, **q):
    q["access_token"] = TOKEN; q.setdefault("limit", 500)
    url, out = f"{API}/{path}?" + urllib.parse.urlencode(q), []
    while url:
        try: r = json.load(urllib.request.urlopen(url))
        except urllib.error.HTTPError as e: return {"error": json.load(e).get("error", {}).get("message", str(e))}
        out += r.get("data", []); url = r.get("paging", {}).get("next")
    return out

RESULT_TYPES = ("offsite_conversion.fb_pixel_lead", "lead", "onsite_conversion.lead_grouped",
                "offsite_conversion.fb_pixel_purchase", "purchase", "offsite_conversion.fb_pixel_complete_registration")
def results(x):  # one result is reported under several action types: max per family, never the sum
    acts = {v["action_type"]: int(float(v["value"])) for v in x.get("actions", [])}
    lead = max([acts.get(k, 0) for k in RESULT_TYPES[:3]] or [0])
    purchase = max(acts.get(RESULT_TYPES[3], 0), acts.get(RESULT_TYPES[4], 0))
    reg = acts.get(RESULT_TYPES[5], 0)
    return lead + purchase + reg, {"leads": lead, "purchases": purchase, "registrations": reg}

out = {"window": [START.isoformat(), END.isoformat()]}

# 1. Account + ownership
acc = get(ACCOUNT, fields="name,account_status,disable_reason,currency,timezone_name,amount_spent,business{id,name},owner")
out["account"] = acc

# 2. Pixel / dataset health
pixels = many(f"{ACCOUNT}/adspixels", fields="id,name,last_fired_time,owner_business{name},is_unavailable")
out["pixels"] = []
if isinstance(pixels, list):
    for p in pixels:
        src = get(f"{p['id']}/stats", aggregation="event_source", start_time=int((D.datetime.now() - D.timedelta(days=7)).timestamp()))
        ev = get(f"{p['id']}/stats", aggregation="event", start_time=int((D.datetime.now() - D.timedelta(days=7)).timestamp()))
        def tally(r):
            t = C.Counter()
            for b in (r.get("data") or []):
                for x in b.get("data", []): t[x["value"]] += x["count"]
            return dict(t)
        out["pixels"].append({"id": p["id"], "name": p.get("name"), "owner": (p.get("owner_business") or {}).get("name"),
                              "last_fired": p.get("last_fired_time"), "sources_7d": tally(src), "events_7d": tally(ev)})
else:
    out["pixels_error"] = pixels.get("error")

# 3. Structure
camps = many(f"{ACCOUNT}/campaigns", fields="id,name,objective,effective_status,special_ad_categories,daily_budget,lifetime_budget,bid_strategy,created_time")
sets = many(f"{ACCOUNT}/adsets", fields="id,name,campaign_id,effective_status,daily_budget,lifetime_budget,optimization_goal,promoted_object,targeting,learning_stage_info,created_time,updated_time")
ads = many(f"{ACCOUNT}/ads", fields="id,name,adset_id,effective_status,created_time,creative{object_type,body,title,url_tags,object_story_spec,asset_feed_spec,effective_object_story_id}")
for name, v in (("campaigns", camps), ("adsets", sets), ("ads", ads)):
    if isinstance(v, dict): out[f"{name}_error"] = v["error"]
camps = camps if isinstance(camps, list) else []; sets = sets if isinstance(sets, list) else []; ads = ads if isinstance(ads, list) else []
act_c = [c for c in camps if c["effective_status"] == "ACTIVE"]
act_s = [s for s in sets if s["effective_status"] == "ACTIVE"]
act_a = [x for x in ads if x["effective_status"] == "ACTIVE"]

def targeting_summary(t):
    g = t.get("geo_locations", {})
    return {"countries": g.get("countries"), "regions": len(g.get("regions", [])), "cities": len(g.get("cities", [])),
            "radius_km": sorted({c.get("radius") for c in g.get("cities", []) if c.get("radius")}),
            "zips": len(g.get("zips", [])), "age": [t.get("age_min"), t.get("age_max")], "genders": t.get("genders"),
            "interests": sum(len(f.get("interests", [])) + len(f.get("behaviors", [])) for f in t.get("flexible_spec", [])),
            "custom_audiences": len(t.get("custom_audiences", [])), "excluded_audiences": len(t.get("excluded_custom_audiences", [])),
            "advantage_audience": (t.get("targeting_automation") or {}).get("advantage_audience"),
            "manual_placements": t.get("publisher_platforms"), "positions": {k: t.get(k) for k in ("facebook_positions", "instagram_positions") if t.get(k)}}
out["structure"] = {
    "campaigns_active": [{"name": c["name"], "objective": c.get("objective"), "special_ad_categories": c.get("special_ad_categories"),
                          "campaign_budget": bool(c.get("daily_budget") or c.get("lifetime_budget")), "bid_strategy": c.get("bid_strategy")} for c in act_c],
    "adsets_active": [{"name": s["name"], "daily_budget": int(s.get("daily_budget", 0) or 0) / 100, "goal": s.get("optimization_goal"),
                       "event": (s.get("promoted_object") or {}).get("custom_event_type"), "learning": (s.get("learning_stage_info") or {}).get("status"),
                       "edited": s["updated_time"][:10], "ads_active": sum(1 for x in act_a if x["adset_id"] == s["id"]),
                       "targeting": targeting_summary(s.get("targeting", {}))} for s in act_s],
    "counts": {"campaigns_active": len(act_c), "adsets_active": len(act_s), "ads_active": len(act_a), "ads_total": len(ads)}}

# 4. Weekly trend
wk = many(f"{ACCOUNT}/insights", fields="spend,impressions,reach,frequency,cpm,ctr,actions", time_range=RNG, time_increment=7)
out["weekly"] = [] if isinstance(wk, dict) else [
    {"week": w["date_start"], "spend": round(float(w["spend"])), "results": results(w)[0], "cpm": round(float(w.get("cpm", 0)), 1),
     "ctr": round(float(w.get("ctr", 0)), 2), "freq": round(float(w.get("frequency", 0)), 2)} for w in wk]
for w in out["weekly"]: w["cost_per_result"] = round(w["spend"] / w["results"]) if w["results"] else None
tot = many(f"{ACCOUNT}/insights", fields="spend,actions,impressions,reach,frequency,ctr,cpm", time_range=RNG)
if isinstance(tot, list) and tot:
    r, fam = results(tot[0])
    out["totals"] = {"spend": round(float(tot[0]["spend"])), "results": r, "by_type": fam, "cost_per_result": round(float(tot[0]["spend"]) / r) if r else None,
                     "frequency": float(tot[0].get("frequency", 0)), "ctr": float(tot[0].get("ctr", 0)), "cpm": float(tot[0].get("cpm", 0))}

# 5. Placements
pl = many(f"{ACCOUNT}/insights", fields="spend,actions", time_range=RNG, breakdowns="publisher_platform,platform_position")
if isinstance(pl, list):
    rows = sorted(({"placement": f"{x['publisher_platform']}/{x['platform_position']}", "spend": round(float(x["spend"])), "results": results(x)[0]} for x in pl), key=lambda r: -r["spend"])
    for r in rows: r["cost_per_result"] = round(r["spend"] / r["results"]) if r["results"] else None
    out["placements"] = [r for r in rows if r["spend"] >= 20]

# 6. Ads, last 30 days
ai = many(f"{ACCOUNT}/insights", level="ad", fields="ad_id,ad_name,spend,ctr,frequency,cpm,actions", time_range=R30)
perf = {x["ad_id"]: x for x in (ai if isinstance(ai, list) else [])}
spend30 = sum(float(x["spend"]) for x in perf.values())

# 7. Creative audit (Andromeda alignment)
def copy_of(cr):
    oss = cr.get("object_story_spec") or {}
    body = cr.get("body") or (oss.get("link_data") or {}).get("message") or (oss.get("video_data") or {}).get("message") or ""
    feed = cr.get("asset_feed_spec") or {}
    if not body and feed.get("bodies"): body = feed["bodies"][0].get("text", "")
    return body or ""
def fmt_of(cr):
    oss = cr.get("object_story_spec") or {}
    if (oss.get("link_data") or {}).get("child_attachments"): return "carousel"
    if oss.get("video_data") or cr.get("object_type") == "VIDEO": return "video"
    if cr.get("asset_feed_spec"): return "dynamic/flexible"
    if oss.get("link_data") or cr.get("object_type") in ("SHARE", "PHOTO"): return "static"
    if cr.get("effective_object_story_id") and not oss: return "existing post"
    return (cr.get("object_type") or "unknown").lower()
active_info = []
for x in act_a:
    cr = x.get("creative") or {}
    p = perf.get(x["id"], {})
    res = results(p)[0] if p else 0
    active_info.append({"name": x["name"], "format": fmt_of(cr), "created": x["created_time"][:10],
                        "age_days": (END - D.date.fromisoformat(x["created_time"][:10])).days,
                        "copy_chars": len(copy_of(cr)), "copy_start": re.sub(r"\s+", " ", copy_of(cr))[:110],
                        "has_url_params": bool(cr.get("url_tags")) or "utm_" in json.dumps(cr),
                        "spend30": round(float(p.get("spend", 0))), "results30": res,
                        "ctr30": round(float(p.get("ctr", 0)), 2), "freq30": round(float(p.get("frequency", 0)), 2)})
created = [D.date.fromisoformat(x["created_time"][:10]) for x in ads]
weeks_new = C.Counter(((END - c).days // 7) for c in created if (END - c).days < 56)
texts = [(i["name"], i["copy_start"].lower()) for i in active_info if i["copy_start"]]
dups = [(a1, b1, round(difflib.SequenceMatcher(None, ta, tb).ratio(), 2)) for i, (a1, ta) in enumerate(texts) for (b1, tb) in texts[i + 1:]
        if difflib.SequenceMatcher(None, ta, tb).ratio() >= 0.6]
spends = sorted((i["spend30"] for i in active_info), reverse=True)
out["creative"] = {
    "active_ads": active_info,
    "format_mix_active": dict(C.Counter(i["format"] for i in active_info)),
    "new_ads_per_week_last_8w": [weeks_new.get(w, 0) for w in range(8)],  # index 0 = most recent week
    "median_active_ad_age_days": S.median([i["age_days"] for i in active_info]) if active_info else None,
    "median_copy_chars": S.median([i["copy_chars"] for i in active_info]) if active_info else None,
    "near_duplicate_pairs": dups[:20],
    "share_without_url_params": round(sum(1 for i in active_info if not i["has_url_params"]) / len(active_info), 2) if active_info else None,
    "spend_share_top_ad_30d": round(spends[0] / spend30, 2) if spends and spend30 else None,
    "ads_under_70_per_week": sum(1 for i in active_info if i["spend30"] < 300)}
json.dump(out, open("/tmp/meta-healthcheck.json", "w"), indent=1, default=str)

# Summary
p = print
p(f"ACCOUNT {acc.get('name')} | status {acc.get('account_status')} | currency {acc.get('currency')} | owner business {(acc.get('business') or {}).get('name')} | window {START}..{END}")
if "totals" in out: t = out["totals"]; p(f"TOTALS {a.days}d: spend {t['spend']:,} | results {t['results']} {t['by_type']} | cost/result {t['cost_per_result']} | freq {t['frequency']:.2f} | CTR {t['ctr']:.2f}% | CPM {t['cpm']:.1f}")
p("PIXELS:"); [p(f"  {x['name']} ({x['id']}) owner={x['owner']} last_fired={x['last_fired']} sources_7d={x['sources_7d']} events_7d={x['events_7d']}") for x in out["pixels"]]
p(f"STRUCTURE: {out['structure']['counts']}")
for c in out["structure"]["campaigns_active"]: p(f"  campaign {c['name']} | {c['objective']} | special={c['special_ad_categories']} | campaign_budget={c['campaign_budget']}")
for s in out["structure"]["adsets_active"]: p(f"  adset {s['name']} | ${s['daily_budget']:,.0f}/d | goal {s['goal']} {s['event'] or ''} | learning {s['learning']} | edited {s['edited']} | ads {s['ads_active']} | targeting {s['targeting']}")
p("WEEKLY (oldest first): " + " | ".join(f"{w['week'][5:]} ${w['spend']:,}/{w['results']}={w['cost_per_result']} f{w['freq']} ctr{w['ctr']}" for w in out["weekly"]))
p("PLACEMENTS: " + " | ".join(f"{r['placement']} ${r['spend']:,} {r['results']} ({r['cost_per_result']})" for r in out.get("placements", [])[:12]))
cr = out["creative"]
p(f"CREATIVE: formats {cr['format_mix_active']} | new ads/week last 8w (latest first) {cr['new_ads_per_week_last_8w']} | median ad age {cr['median_active_ad_age_days']}d | median copy {cr['median_copy_chars']} chars | no URL params {cr['share_without_url_params']} | top ad share of 30d spend {cr['spend_share_top_ad_30d']} | ads under ~$70/wk {cr['ads_under_70_per_week']}")
p(f"NEAR-DUPLICATE COPY PAIRS (>=60% similar): {len(cr['near_duplicate_pairs'])}")
p("ACTIVE ADS (30d): ")
for i in sorted(cr["active_ads"], key=lambda r: -r["spend30"]):
    p(f"  {i['name'][:42]:42} {i['format']:9} age {i['age_days']:>3}d ${i['spend30']:>6,} res {i['results30']:>3} ctr {i['ctr30']}% f{i['freq30']} copy {i['copy_chars']}ch params={'Y' if i['has_url_params'] else 'N'}")
