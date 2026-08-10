from __future__ import annotations
import json
from .config import SITE_DIR
from .db import connect

def latest_events():
    with connect() as con:
        row = con.execute("SELECT MAX(snapshot_ts) AS ts FROM odds_snapshots").fetchone()
        ts = row["ts"] if row else None
        if not ts:
            return None, []

        rows = con.execute(
            """
            SELECT *
            FROM odds_snapshots
            WHERE snapshot_ts=?
            ORDER BY commence_time,event_id,bookmaker_key,market_key
            """,
            (ts,),
        ).fetchall()

    by_event = {}
    for row in rows:
        r = dict(row)
        event = by_event.setdefault(
            r["event_id"],
            {
                "event_id": r["event_id"],
                "commence_time": r["commence_time"],
                "home_team": r["home_team"],
                "away_team": r["away_team"],
                "spreads": [], "totals": [], "h2h": [],
            },
        )
        event[r["market_key"]].append(r)
    return ts, list(by_event.values())

def average(values):
    values = [float(v) for v in values if v is not None]
    return round(sum(values) / len(values), 2) if values else None

def build():
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    ts, events = latest_events()
    cards = []

    for e in events:
        cards.append({
            "matchup": f'{e["away_team"]} @ {e["home_team"]}',
            "start": e["commence_time"],
            "home_spread": average([
                x["point"] for x in e["spreads"]
                if x["outcome_name"] == e["home_team"]
            ]),
            "total": average([x["point"] for x in e["totals"]]),
            "home_ml": average([
                x["price"] for x in e["h2h"]
                if x["outcome_name"] == e["home_team"]
            ]),
            "away_ml": average([
                x["price"] for x in e["h2h"]
                if x["outcome_name"] == e["away_team"]
            ]),
        })

    cards_json = json.dumps(cards)
    snapshot = ts or "No odds snapshot yet"

    page = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NFL EDGE</title>
<style>
body{margin:0;background:#08111f;color:#f4f7fb;font-family:Inter,system-ui,Segoe UI,Arial,sans-serif}
.wrap{max-width:1160px;margin:auto;padding:28px 18px 50px}
h1{font-size:42px;margin:5px 0} p{color:#9fb0c7;line-height:1.5}
.eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;color:#4ca7ff;text-transform:uppercase}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}
.card{background:#101d30;border:1px solid #28415e;border-radius:16px;padding:17px}
.v{font-size:21px;font-weight:800}.muted{font-size:12px;color:#99abc1}
.market{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #233a56}
.alert{background:#3a3015;border:1px solid #6d5720;color:#ffe384;border-radius:12px;padding:12px 14px;margin-top:18px}
@media(max-width:850px){.grid{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<div class="eyebrow">Continuous market monitor</div>
<h1>NFL EDGE</h1>
<p>Latest odds snapshot: __SNAPSHOT__. Consensus values are simple averages across returned bookmakers.</p>
<div class="alert"><strong>Model probabilities are intentionally disabled in this starter.</strong> Add the validated model artifact before producing BET / LEAN / PASS recommendations.</div>
<div id="grid" class="grid"></div>
</div>
<script>
const games=__DATA__;
const grid=document.getElementById("grid");
const fmt=x=>x===null?"—":x;
games.forEach(g=>{
  const div=document.createElement("div");
  div.className="card";
  div.innerHTML=`<div class="muted">${g.start||""}</div>
  <div class="v">${g.matchup}</div>
  <div class="market"><span>Home spread</span><strong>${fmt(g.home_spread)}</strong></div>
  <div class="market"><span>Total</span><strong>${fmt(g.total)}</strong></div>
  <div class="market"><span>Away ML</span><strong>${fmt(g.away_ml)}</strong></div>
  <div class="market"><span>Home ML</span><strong>${fmt(g.home_ml)}</strong></div>`;
  grid.appendChild(div);
});
</script>
</body>
</html>"""
    page = page.replace("__SNAPSHOT__", str(snapshot)).replace("__DATA__", cards_json)
    out = SITE_DIR / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"[site] events={len(cards)} -> {out}")

if __name__ == "__main__":
    build()
