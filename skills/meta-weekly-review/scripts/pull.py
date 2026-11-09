#!/usr/bin/env python3
"""
Weekly Meta review data pull. READ ONLY: it never changes anything in Meta.

Per ad: this week vs last week vs last 14 days (spend, leads, CTR), lifetime frequency, ad set
edit dates (for learning holds), and, if you give it a CRM export, what each ad's leads did next.

Setup (once):
  export META_AD_ACCOUNT=act_1234567890                 # your ad account ID
  export META_TOKEN_FILE=~/secrets/meta_token.txt       # file holding a System User token (ads_read)
Optional CRM outcomes: a CSV with one row per lead and these columns (header names exactly):
  created_at  (YYYY-MM-DD or ISO date)
  ad_id       (the Meta ad ID the lead came from; usually from utm_content={{ad.id}})
  booked      (1/0: booked a call/quote/appointment)
  showed      (1/0: the call/quote/appointment happened)
  won         (1/0: became a paying customer)
  score       (optional: your 0-100 lead quality score)

Usage:
  python3 pull.py                         # weeks ending yesterday, Meta only
  python3 pull.py --crm leads.csv         # with CRM outcomes
  python3 pull.py --end 2026-10-18 --crm leads.csv
Writes /tmp/meta-weekly-review.json and prints a summary.
"""
import argparse, collections as C, csv, datetime as D, json, os, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--end"); ap.add_argument("--crm")
a = ap.parse_args()
ACCOUNT = os.environ["META_AD_ACCOUNT"]
TOKEN = open(os.path.expanduser(os.environ["META_TOKEN_FILE"])).read().strip()
API = "https://graph.facebook.com/v21.0"
end = D.date.fromisoformat(a.end) if a.end else D.date.today() - D.timedelta(days=1)
d = lambda n: (end - D.timedelta(days=n)).isoformat()
W1, W0, W14, W30 = (d(6), end.isoformat()), (d(13), d(7)), (d(13), end.isoformat()), (d(29), end.isoformat())

def meta(path, **q):
    q["access_token"] = TOKEN
    url, out = f"{API}/{path}?" + urllib.parse.urlencode(q), []
    while url:
        r = json.load(urllib.request.urlopen(url)); out += r.get("data", []); url = r.get("paging", {}).get("next")
    return out

def leads_of(x):  # Meta reports one lead under several action types: take the max, never the sum
    return max([int(v["value"]) for v in x.get("actions", []) if v["action_type"] in ("offsite_conversion.fb_pixel_lead", "lead", "onsite_conversion.lead_grouped")] or [0])

def insights(rng):
    rows = meta(f"{ACCOUNT}/insights", level="ad", fields="ad_id,spend,frequency,ctr,actions",
                time_range=json.dumps({"since": rng[0], "until": rng[1]}), limit=500)
    return {r["ad_id"]: {"spend": float(r["spend"]), "leads": leads_of(r), "ctr": float(r.get("ctr", 0)), "freq": float(r.get("frequency", 0))} for r in rows}

ads = {x["id"]: x for x in meta(f"{ACCOUNT}/ads", fields="id,name,effective_status,adset{name},created_time", limit=500)}
adsets = [s for s in meta(f"{ACCOUNT}/adsets", fields="name,effective_status,daily_budget,updated_time,optimization_goal", limit=200) if s["effective_status"] == "ACTIVE"]
w1, w0, w14, w30, life = insights(W1), insights(W0), insights(W14), insights(W30), insights((d(364), end.isoformat()))

crm, untraced, rows = C.defaultdict(lambda: C.Counter()), 0, []
if a.crm:
    rows = list(csv.DictReader(open(a.crm)))
    for r in rows:
        aid = (r.get("ad_id") or "").strip()
        if not aid: untraced += 1; continue
        c = crm[aid]; c["leads"] += 1
        for k in ("booked", "showed", "won"): c[k] += int((r.get(k) or "0").strip() in ("1", "true", "TRUE", "yes"))
        if (r.get("score") or "").strip(): c["score_n"] += 1; c["score_sum"] += float(r["score"])

spend30 = sum(v["spend"] for v in w30.values())
showed30 = sum(1 for r in rows if W30[0] <= r["created_at"][:10] <= W30[1] and (r.get("showed") or "0").strip() in ("1", "true", "TRUE", "yes"))
leads30 = sum(v["leads"] for v in w30.values())
target = (spend30 / showed30) if showed30 else (spend30 / leads30 if leads30 else None)
target_label = "cost per showed call/appointment (CRM)" if showed30 else "cost per lead (Meta only: add --crm for a better target)"
budget = sum(int(s.get("daily_budget", 0)) / 100 for s in adsets)
active = [x for x in ads.values() if x["effective_status"] == "ACTIVE"]
ceiling = int(budget * 14 / (2 * target)) if target and budget else None

out = {"week": W1, "prev_week": W0, "target": round(target) if target else None, "target_label": target_label,
       "active_ads": len(active), "ad_count_ceiling": ceiling, "daily_budget": budget, "crm_untraced": untraced,
       "adsets": [{"name": s["name"], "budget": int(s.get("daily_budget", 0)) / 100, "goal": s.get("optimization_goal"), "edited": s["updated_time"][:10]} for s in adsets],
       "ads": []}
for i, x in ads.items():
    if x["effective_status"] != "ACTIVE" and not w1.get(i, {}).get("spend"): continue
    c = crm.get(i)
    out["ads"].append({"id": i, "name": x["name"], "status": x["effective_status"], "adset": x.get("adset", {}).get("name"),
                       "created": x["created_time"][:10], "week": w1.get(i), "prev_week": w0.get(i), "last14": w14.get(i),
                       "lifetime_freq": (life.get(i) or {}).get("freq"),
                       "crm": ({k: c[k] for k in ("leads", "booked", "showed", "won")} | ({"avg_score": round(c["score_sum"] / c["score_n"])} if c["score_n"] else {})) if c else None})
out["ads"].sort(key=lambda r: -((r["week"] or {}).get("spend", 0)))
json.dump(out, open("/tmp/meta-weekly-review.json", "w"), indent=1)

t1 = (sum(v["spend"] for v in w1.values()), sum(v["leads"] for v in w1.values()))
t0 = (sum(v["spend"] for v in w0.values()), sum(v["leads"] for v in w0.values()))
cpl = lambda s, l: f"${s/l:,.0f}" if l else "-"
print(f"Week {W1[0]}..{W1[1]}: ${t1[0]:,.0f}, {t1[1]} leads, {cpl(*t1)}/lead | previous week ${t0[0]:,.0f}, {t0[1]} leads, {cpl(*t0)}/lead")
print(f"Target ({target_label}, last 30 days): {('$%s' % format(round(target), ',')) if target else 'n/a'}")
print(f"Active ads {len(active)} vs ad-count ceiling {ceiling} (daily budget ${budget:,.0f})" + (f" | CRM leads with no ad ID: {untraced}/{len(rows)}" if a.crm else ""))
for s in out["adsets"]: print(f"  ad set: {s['name']} ${s['budget']:,.0f}/day, goal {s['goal']}, last edited {s['edited']}")
print("\nad | week $,leads,ctr | prev $,leads | 14d $,leads | freq | CRM leads/booked/showed/won (score)")
for r in out["ads"]:
    w, p, f, c = r["week"] or {}, r["prev_week"] or {}, r["last14"] or {}, r["crm"] or {}
    print(f"{r['name'][:44]:44} | ${w.get('spend',0):.0f},{w.get('leads',0)},{w.get('ctr',0):.1f}% | ${p.get('spend',0):.0f},{p.get('leads',0)}"
          f" | ${f.get('spend',0):.0f},{f.get('leads',0)} | {r['lifetime_freq'] or 0:.1f} | "
          f"{c.get('leads','-')}/{c.get('booked','-')}/{c.get('showed','-')}/{c.get('won','-')} ({c.get('avg_score','-')})"
          + ("" if r["status"] == "ACTIVE" else f"  [{r['status']}]"))
