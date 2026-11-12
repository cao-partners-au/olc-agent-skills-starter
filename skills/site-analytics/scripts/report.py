#!/usr/bin/env python3
"""
On-demand website analytics: Plausible (traffic + conversions, any date range) joined with
Microsoft Clarity (behaviour: scroll, time, frustration) and, optionally, stored history and
CRM leads. READ ONLY. Python standard library only, so it runs in Claude Code or Hermes.

Config (environment variables, or a .env-style file passed with --config):
  PLAUSIBLE_SITE            your site as added in Plausible, e.g. example.com
  PLAUSIBLE_API_KEY_FILE    file holding a Plausible Stats API key  (or PLAUSIBLE_API_KEY)
  PLAUSIBLE_GOALS           optional, comma list of goal names to report (default: every goal found)
  CLARITY_TOKEN_FILE        file holding a Clarity Data Export API token (or CLARITY_TOKEN). Optional.
  HISTORY                   optional: "supabase" (SUPABASE_URL + SUPABASE_KEY_FILE) or "sqlite:/path/file.db"
                            written by snapshot.py; used for week-on-week trends and Clarity history.
  LEADS_CSV                 optional CRM export: created_at, landing_page (or ad_id), booked, showed, won

Usage:
  python3 report.py                       # last 30 days
  python3 report.py --days 7
  python3 report.py --from 2026-10-01 --to 2026-10-31
  python3 report.py --no-clarity          # don't spend one of Clarity's 10 reads a day
Writes /tmp/site-analytics-report.json and prints a summary for the agent to diagnose.
"""
import argparse, collections as C, csv, datetime as D, json, os, re, sqlite3, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=30); ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
ap.add_argument("--no-clarity", action="store_true"); ap.add_argument("--config")
a = ap.parse_args()
if a.config:
    for line in open(os.path.expanduser(a.config)):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1); os.environ.setdefault(k, v.strip().strip('"'))

def secret(name):
    if os.environ.get(name): return os.environ[name].strip()
    f = os.environ.get(name + "_FILE")
    return open(os.path.expanduser(f)).read().strip() if f and os.path.exists(os.path.expanduser(f)) else None

SITE = os.environ.get("PLAUSIBLE_SITE")
PKEY = secret("PLAUSIBLE_API_KEY"); CTOK = secret("CLARITY_TOKEN")
today = D.date.today()
TO = D.date.fromisoformat(a.to) if a.to else today
FROM = D.date.fromisoformat(a.frm) if a.frm else TO - D.timedelta(days=a.days - 1)
out = {"site": SITE, "from": str(FROM), "to": str(TO), "notes": []}

def get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    try: return json.load(urllib.request.urlopen(req, timeout=20)), None
    except urllib.error.HTTPError as e: return None, f"{e.code} {e.read().decode()[:160]}"
    except Exception as e: return None, str(e)

def pbreak(prop, metrics, filters=None, frm=FROM, to=TO):
    q = {"site_id": SITE, "period": "custom", "date": f"{frm},{to}", "property": prop, "metrics": metrics, "limit": 1000}
    if filters: q["filters"] = filters
    r, err = get("https://plausible.io/api/v1/stats/breakdown?" + urllib.parse.urlencode(q), {"Authorization": f"Bearer {PKEY}"})
    if err: raise RuntimeError(f"Plausible {prop}: {err}")
    return r.get("results", [])

def path(v): return (v.split("?")[0] or "/").replace("/index.html", "/")

# ---------------- Plausible
if not (SITE and PKEY):
    out["notes"].append("Plausible not configured (PLAUSIBLE_SITE + PLAUSIBLE_API_KEY): see references/setup-guide.md")
else:
    try:
        goals_all = [g["goal"] for g in pbreak("event:goal", "visitors,events")]
        want = [g.strip() for g in os.environ.get("PLAUSIBLE_GOALS", "").split(",") if g.strip()] or goals_all
        out["goals_found"] = goals_all
        agg, _ = get("https://plausible.io/api/v1/stats/aggregate?" + urllib.parse.urlencode({"site_id": SITE, "period": "custom", "date": f"{FROM},{TO}", "metrics": "visitors,visits,pageviews,bounce_rate,visit_duration"}), {"Authorization": f"Bearer {PKEY}"})
        out["totals"] = (agg or {}).get("results")
        def dim(prop, field, limit=25):
            rows = {}
            for r in pbreak(prop, "visitors,visits,bounce_rate,visit_duration"):
                k = path(r[field]) if field == "entry_page" else r[field]
                if not k: continue
                x = rows.setdefault(k, {"value": k, "visits": 0, "visitors": 0, "bounce": r.get("bounce_rate"), "avg_s": r.get("visit_duration"), "goals": {}})
                x["visits"] += r.get("visits", 0); x["visitors"] += r.get("visitors", 0)
            for g in want:
                for r in pbreak(prop, "visitors", f"event:goal=={g}"):
                    k = path(r[field]) if field == "entry_page" else r[field]
                    if k in rows: rows[k]["goals"][g] = rows[k]["goals"].get(g, 0) + r.get("visitors", 0)
            return sorted(rows.values(), key=lambda x: -x["visits"])[:limit]
        out["entry_pages"] = dim("visit:entry_page", "entry_page")
        out["sources"] = dim("visit:source", "source", 12)
        out["utm_content"] = dim("visit:utm_content", "utm_content", 20)
        # previous equal period, for trend
        span = (TO - FROM).days + 1
        pf, pt = FROM - D.timedelta(days=span), FROM - D.timedelta(days=1)
        prev, _ = get("https://plausible.io/api/v1/stats/aggregate?" + urllib.parse.urlencode({"site_id": SITE, "period": "custom", "date": f"{pf},{pt}", "metrics": "visitors,visits,bounce_rate,visit_duration"}), {"Authorization": f"Bearer {PKEY}"})
        out["previous_period"] = {"from": str(pf), "to": str(pt), "totals": (prev or {}).get("results")}
    except RuntimeError as e:
        out["notes"].append(str(e))

# ---------------- Clarity (live, last 3 days; costs 1 of 10 reads/day)
def parse_clarity(raw):
    pages = C.defaultdict(lambda: {"sessions": 0, "w": C.defaultdict(lambda: [0.0, 0.0])})
    def num(v):
        try: return float(v)
        except Exception: return None
    for b in raw if isinstance(raw, list) else []:
        name = re.sub(r"[^a-z]", "", (b.get("metricName") or "").lower())
        for row in b.get("information") or []:
            url = next((row[k] for k in row if k.lower() == "url"), None)
            if not url: continue
            p = urllib.parse.urlparse(url).path or "/"
            p = p if p.endswith("/") else p + "/"
            pg = pages[p]
            if "traffic" in name:
                pg["sessions"] += num(row.get("totalSessionCount") or row.get("sessionsCount") or 0) or 0
                continue
            wgt = num(row.get("sessionsCount")) or 1
            if "scroll" in name: val, key = num(row.get("averageScrollDepth")), "scroll_pct"
            elif "engagement" in name: val, key = num(row.get("activeTime") or row.get("totalTime")), "active_s"
            else:
                key = next((k for k in ("rage", "dead", "quickback", "excessive", "scripterror") if k in name), None)
                val = num(row.get("sessionsWithMetricPercentage"))
                if not key: continue
                key += "_pct"
            if val is not None: pg["w"][key][0] += val * wgt; pg["w"][key][1] += wgt
    res = []
    for p, pg in pages.items():
        r = {"path": p, "sessions": int(pg["sessions"])}
        for k, (s, w) in pg["w"].items(): r[k] = round(s / w, 1) if w else None
        res.append(r)
    return sorted(res, key=lambda r: -r["sessions"])

if a.no_clarity or not CTOK:
    out["notes"].append("Clarity live read skipped" + ("" if CTOK else " (no CLARITY_TOKEN: see setup guide)"))
else:
    raw, err = get("https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=3&dimension1=URL", {"Authorization": f"Bearer {CTOK}", "Content-Type": "application/json"})
    if err: out["notes"].append(f"Clarity: {err} (429 = the 10 reads/day are used up)")
    else: out["clarity_3d"] = parse_clarity(raw)

# ---------------- History (written by snapshot.py)
HIST = os.environ.get("HISTORY", "")
try:
    if HIST.startswith("sqlite:"):
        db = sqlite3.connect(os.path.expanduser(HIST[7:]))
        out["history_weekly"] = [dict(zip(("week", "visits", "enquiries"), r)) for r in db.execute(
            "select strftime('%Y-%W', day) w, sum(visits), sum(goals_total) from site_analytics_daily where dimension='entry_page' group by w order by w desc limit 8")]
        out["clarity_history"] = [dict(zip(("path", "days", "sessions", "scroll", "active"), r)) for r in db.execute(
            "select path, count(*), sum(sessions), round(avg(scroll_depth),1), round(avg(active_seconds),1) from clarity_daily group by path order by 3 desc limit 15")]
    elif HIST == "supabase":
        sb, sk = os.environ.get("SUPABASE_URL", "").rstrip("/"), secret("SUPABASE_KEY")
        t1 = os.environ.get("HISTORY_TABLE_SITE", "site_analytics_daily"); t2 = os.environ.get("HISTORY_TABLE_CLARITY", "clarity_daily")
        h = {"apikey": sk, "Authorization": f"Bearer {sk}"}
        since = str(TO - D.timedelta(days=56))
        gcol = os.environ.get("HISTORY_GOAL_COLUMN", "goals_total")
        rows, err = get(f"{sb}/rest/v1/{t1}?select=day,visits,{gcol}&dimension=eq.entry_page&day=gte.{since}&limit=5000", h)
        if rows:
            wk = C.defaultdict(lambda: [0, 0])
            for r in rows:
                w = D.date.fromisoformat(r["day"]).strftime("%Y-%W"); wk[w][0] += r["visits"]; wk[w][1] += r.get(gcol) or 0
            out["history_weekly"] = [{"week": w, "visits": v[0], "enquiries": v[1]} for w, v in sorted(wk.items(), reverse=True)]
        rows, err2 = get(f"{sb}/rest/v1/{t2}?select=day,path,sessions,scroll_depth,active_seconds,rage_clicks,quick_backs&day=gte.{since}&limit=5000", h)
        if rows:
            ph = C.defaultdict(list)
            for r in rows: ph[r["path"]].append(r)
            out["clarity_history"] = sorted([{"path": p, "days": len(v), "sessions": sum(x["sessions"] or 0 for x in v),
                "scroll": round(sum(float(x["scroll_depth"] or 0) * (x["sessions"] or 0) for x in v) / max(1, sum(x["sessions"] or 0 for x in v)), 1)} for p, v in ph.items()], key=lambda r: -r["sessions"])[:15]
        if err or err2: out["notes"].append(f"history read: {err or err2}")
except Exception as e:
    out["notes"].append(f"history unavailable: {e}")

# ---------------- CRM leads (optional)
if os.environ.get("LEADS_CSV") and os.path.exists(os.path.expanduser(os.environ["LEADS_CSV"])):
    lp = C.defaultdict(C.Counter)
    for r in csv.DictReader(open(os.path.expanduser(os.environ["LEADS_CSV"]))):
        if not (str(FROM) <= (r.get("created_at") or "")[:10] <= str(TO)): continue
        key = path(r.get("landing_page") or "") if r.get("landing_page") else (r.get("ad_id") or "unknown")
        c = lp[key]; c["leads"] += 1
        for k in ("booked", "showed", "won"): c[k] += (r.get(k) or "").strip().lower() in ("1", "true", "yes")
    out["crm_by_landing"] = {k: dict(v) for k, v in lp.items()}

json.dump(out, open("/tmp/site-analytics-report.json", "w"), indent=1, default=str)

# ---------------- Summary
p = print
p(f"SITE {SITE} | {FROM} to {TO}")
for n in out["notes"]: p("NOTE:", n)
if out.get("totals"): t = out["totals"]; p("TOTALS:", {k: t[k]["value"] for k in t}, "| previous:", {k: v["value"] for k, v in ((out.get('previous_period') or {}).get('totals') or {}).items()})
if out.get("goals_found") is not None: p("GOALS with conversions in range:", out["goals_found"] or "none yet (no conversions, or goals not set up: setup guide step P5)")
def show(title, rows):
    if not rows: return
    p(f"\n{title}:")
    for r in rows:
        g = r["goals"]; conv = " ".join(f"{k}={v}" for k, v in g.items() if v)
        rate = (sum(g.values()) / r["visits"] * 100) if r["visits"] else 0
        p(f"  {r['value'][:48]:48} visits {r['visits']:>5} bounce {r['bounce'] if r['bounce'] is not None else '-':>4}% avg {r['avg_s'] or 0:>4}s goals {conv or '-'} ({rate:.1f}% of visits)")
show("LANDING PAGES (visits that started here)", out.get("entry_pages"))
show("SOURCES", out.get("sources"))
show("AD / utm_content", out.get("utm_content"))
if out.get("clarity_3d"):
    p("\nCLARITY last 3 days:"); [p(f"  {r['path'][:40]:40} sessions {r['sessions']:>4} scroll {r.get('scroll_pct','-')}% active {r.get('active_s','-')}s rage {r.get('rage_pct','-')}% dead {r.get('dead_pct','-')}% quickback {r.get('quickback_pct','-')}%") for r in out["clarity_3d"][:15]]
if out.get("history_weekly"): p("\nHISTORY weekly (latest first):", out["history_weekly"][:8])
if out.get("clarity_history"): p("CLARITY history (56d):", out["clarity_history"][:10])
if out.get("crm_by_landing"): p("\nCRM by landing page:", out["crm_by_landing"])
