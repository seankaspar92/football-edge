from __future__ import annotations
from datetime import datetime, timezone
import requests
from .config import ODDS_API_KEY, ODDS_MARKETS, ODDS_REGIONS, ODDS_SPORT
from .db import connect

API = "https://api.the-odds-api.com/v4"

def run() -> int:
    if not ODDS_API_KEY:
        print("[warn] ODDS_API_KEY not set; skipping odds ingestion")
        return 0

    response = requests.get(
        f"{API}/sports/{ODDS_SPORT}/odds",
        params={
            "apiKey": ODDS_API_KEY,
            "regions": ODDS_REGIONS,
            "markets": ODDS_MARKETS,
            "oddsFormat": "american",
            "dateFormat": "iso",
        },
        timeout=45,
    )
    response.raise_for_status()
    events = response.json()
    snapshot_ts = datetime.now(timezone.utc).isoformat()

    written = 0
    with connect() as con:
        for event in events:
            for book in event.get("bookmakers", []):
                for market in book.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        con.execute(
                            '''
                            INSERT OR IGNORE INTO odds_snapshots(
                              snapshot_ts,event_id,commence_time,home_team,away_team,
                              bookmaker_key,bookmaker_title,market_key,outcome_name,
                              price,point,last_update
                            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                            ''',
                            (
                                snapshot_ts, event.get("id"), event.get("commence_time"),
                                event.get("home_team"), event.get("away_team"),
                                book.get("key"), book.get("title"), market.get("key"),
                                outcome.get("name"), outcome.get("price"),
                                outcome.get("point"), book.get("last_update"),
                            ),
                        )
                        written += 1

    print(
        "[odds] rows=", written,
        " used=", response.headers.get("x-requests-used"),
        " remaining=", response.headers.get("x-requests-remaining"),
    )
    return written

if __name__ == "__main__":
    run()
