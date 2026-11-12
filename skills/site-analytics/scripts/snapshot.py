#!/usr/bin/env python3
"""
Daily history for Plausible + Clarity (Clarity forgets after 1-3 days, so this is its only history).
Run once a day just after midnight (cron, Hermes schedule, Railway, GitHub Action...). READ ONLY towards
both services; writes to your store. Python standard library only.

Store (HISTORY):
  sqlite:/path/analytics.db   simplest; tables are created automatically
  supabase                    SUPABASE_URL + SUPABASE_KEY(_FILE); create the tables first with
                              references/history-tables.sql (tables: site_analytics_daily, clarity_daily)
Same config as report.py (PLAUSIBLE_SITE, PLAUSIBLE_API_KEY(_FILE), PLAUSIBLE_GOALS, CLARITY_TOKEN(_FILE)).

  python3 snapshot.py --config site.env                 # yesterday
  python3 snapshot.py --config site.env --from 2026-10-01 --to 2026-10-19   # backfill Plausible
  python3 snapshot.py --config site.env --dry-run
Re-running a day replaces it (upsert on day+dimension+value / day+path).
"""
import argparse, datetime as D, json, os, re, sqlite3, urllib.parse, urllib.request

ap = argparse.ArgumentParser(); ap.add_argument("--config"); ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--no-clarity", action="store_true")
a = ap.parse_args()
if a.config:
    for line in open(os.path.expanduser(a.config)):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1); os.environ.setdefault(k, v.strip().strip('"'))
def secret(n):
    if os.environ.get(n): return os.environ[n].strip()
    f = os.environ.get(n + "_FILE"); return open(os.path.expanduser(f)).read().strip() if f else None
SITE, PKEY, CTOK = os.environ.get("PLAUSIBLE_SITE"), secret("PLAUSIBLE_API_KEY"), secret("CLARITY_TOKEN")
GOALS = [g.strip() for g in os.environ.get("PLAUSIBLE_GOALS", "").split(",") if g.strip()][:4]
STORE = os.environ.get("HISTORY", "sqlite:~/site-analytics.db")
DIMS = {"entry_page": "visit:entry_page", "source": "visit:source", "utm_campaign": "visit:utm_campaign", "utm_content": "visit:utm_content"}
yesterday = D.date.today() - D.timedelta(days=1)

def get(url, h):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30)), None
    except urllib.error.HTTPError as e: return None, f"{e.code} {e.read().decode()[:150]}"
def pb(day, prop, metrics, filt=None):
    q = {"site_id": SITE, "period": "day", "date": day, "property": prop, "metrics": metrics, "limit": 1000}
    if filt: q["filters"] = filt
    r, err = get("https://plausible.io/api/v1/stats/breakdown?" + urllib.parse.urlencode(q), {"Authorization": f"Bearer {PKEY}"})
    if err: raise SystemExit(f"Plausible: {err}")
    return r.get("results", [])
norm = lambda v: (v.split("?")[0] or "/").replace("/index.html", "/")

def plausible_day(day):
    rows = []
    for dim, prop in DIMS.items():
        field = prop.split(":")[1]; acc = {}
        for r in pb(day, prop, "visitors,visits,bounce_rate,visit_duration"):
            k = norm(r[field]) if dim == "entry_page" else r[field]
            if not k: continue
            x = acc.setdefault(k, {"day": day, "dimension": dim, "value": k, "visits": 0, "visitors": 0, "bounce_rate": r.get("bounce_rate"), "avg_seconds": r.get("visit_duration"), "goal_1": 0, "goal_2": 0, "goal_3": 0, "goal_4": 0})
            x["visits"] += r.get("visits", 0); x["visitors"] += r.get("visitors", 0)
        for i, g in enumerate(GOALS, 1):
            for r in pb(day, prop, "visitors", f"event:goal=={g}"):
                k = norm(r[field]) if dim == "entry_page" else r[field]
                if k in acc: acc[k][f"goal_{i}"] += r.get("visitors", 0)
        rows += list(acc.values())
    for r in rows: r["goals_total"] = r["goal_1"] + r["goal_2"] + r["goal_3"] + r["goal_4"]
    return rows

def clarity_last_day(day):
    raw, err = get("https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=1&dimension1=URL", {"Authorization": f"Bearer {CTOK}", "Content-Type": "application/json"})
    if err: print("Clarity:", err); return []
    pages = {}
    for b in raw if isinstance(raw, list) else []:
        name = re.sub(r"[^a-z]", "", (b.get("metricName") or "").lower())
        for row in b.get("information") or []:
            url = next((row[k] for k in row if k.lower() == "url"), None)
            if not url: continue
            p = urllib.parse.urlparse(url).path or "/"; p = p if p.endswith("/") else p + "/"
            x = pages.setdefault(p, {"day": day, "path": p, "sessions": 0, "scroll_depth": None, "active_seconds": None, "rage_clicks": None, "dead_clicks": None, "quick_backs": None})
            f = lambda k: float(row[k]) if row.get(k) not in (None, "") else None
            if "traffic" in name: x["sessions"] += int(f("totalSessionCount") or 0)
            elif "scroll" in name: x["scroll_depth"] = f("averageScrollDepth")
            elif "engagement" in name: x["active_seconds"] = f("activeTime")
            elif "rage" in name: x["rage_clicks"] = f("sessionsWithMetricPercentage")
            elif "dead" in name: x["dead_clicks"] = f("sessionsWithMetricPercentage")
            elif "quickback" in name: x["quick_backs"] = f("sessionsWithMetricPercentage")
    return list(pages.values())

def store(table, key, rows):
    if not rows or a.dry_run: return
    if STORE.startswith("sqlite:"):
        db = sqlite3.connect(os.path.expanduser(STORE[7:]))
        db.execute("create table if not exists site_analytics_daily(day,dimension,value,visits,visitors,bounce_rate,avg_seconds,goal_1,goal_2,goal_3,goal_4,goals_total, primary key(day,dimension,value))")
        db.execute("create table if not exists clarity_daily(day,path,sessions,scroll_depth,active_seconds,rage_clicks,dead_clicks,quick_backs, primary key(day,path))")
        cols = list(rows[0].keys())
        db.executemany(f"insert or replace into {table}({','.join(cols)}) values({','.join('?' * len(cols))})", [tuple(r[c] for c in cols) for r in rows]); db.commit()
    else:
        sb, sk = os.environ["SUPABASE_URL"].rstrip("/"), secret("SUPABASE_KEY")
        req = urllib.request.Request(f"{sb}/rest/v1/{table}?on_conflict={key}", data=json.dumps(rows).encode(), method="POST",
              headers={"apikey": sk, "Authorization": f"Bearer {sk}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"})
        urllib.request.urlopen(req, timeout=30)

frm = D.date.fromisoformat(a.frm) if a.frm else yesterday
to = D.date.fromisoformat(a.to) if a.to else (yesterday if a.frm else frm)
if SITE and PKEY:
    d = frm
    while d <= to:
        rows = plausible_day(str(d)); store("site_analytics_daily", "day,dimension,value", rows)
        print(f"Plausible {d}: {len(rows)} rows, {sum(r['visits'] for r in rows if r['dimension']=='entry_page')} visits{' (dry run)' if a.dry_run else ''}")
        d += D.timedelta(days=1)
else: print("Plausible not configured: skipped")
if CTOK and not a.no_clarity and not a.frm:
    rows = clarity_last_day(str(yesterday)); store("clarity_daily", "day,path", rows)
    print(f"Clarity last 24h -> {yesterday}: {len(rows)} pages{' (dry run)' if a.dry_run else ''} (uses 1 of Clarity's 10 reads/day)")
