from __future__ import annotations
import json
from datetime import datetime, timezone
import nflreadpy as nfl
from .db import connect

def _records(frame):
    if frame is None:
        return []
    if hasattr(frame, "to_dicts"):
        return frame.to_dicts()
    if hasattr(frame, "to_pandas"):
        return frame.to_pandas().to_dict("records")
    return frame.to_dict("records")

def ingest_schedules() -> int:
    rows = _records(nfl.load_schedules())
    now = datetime.now(timezone.utc).isoformat()
    fields = [
        "game_id","season","week","game_type","gameday","gametime",
        "away_team","home_team","away_score","home_score","stadium","roof",
        "surface","temp","wind","spread_line","total_line",
        "home_moneyline","away_moneyline"
    ]
    with connect() as con:
        for row in rows:
            if not row.get("game_id"):
                continue
            data = {k: row.get(k) for k in fields}
            data["raw_json"] = json.dumps(row, default=str)
            data["updated_at"] = now
            con.execute(
                '''
                INSERT INTO games(
                  game_id,season,week,game_type,gameday,gametime,away_team,home_team,
                  away_score,home_score,stadium,roof,surface,temp,wind,spread_line,
                  total_line,home_moneyline,away_moneyline,raw_json,updated_at
                ) VALUES(
                  :game_id,:season,:week,:game_type,:gameday,:gametime,:away_team,:home_team,
                  :away_score,:home_score,:stadium,:roof,:surface,:temp,:wind,:spread_line,
                  :total_line,:home_moneyline,:away_moneyline,:raw_json,:updated_at
                )
                ON CONFLICT(game_id) DO UPDATE SET
                  season=excluded.season, week=excluded.week, game_type=excluded.game_type,
                  gameday=excluded.gameday, gametime=excluded.gametime,
                  away_team=excluded.away_team, home_team=excluded.home_team,
                  away_score=excluded.away_score, home_score=excluded.home_score,
                  stadium=excluded.stadium, roof=excluded.roof, surface=excluded.surface,
                  temp=excluded.temp, wind=excluded.wind, spread_line=excluded.spread_line,
                  total_line=excluded.total_line, home_moneyline=excluded.home_moneyline,
                  away_moneyline=excluded.away_moneyline, raw_json=excluded.raw_json,
                  updated_at=excluded.updated_at
                ''',
                data,
            )
    return len(rows)

def ingest_injuries() -> int:
    try:
        rows = _records(nfl.load_injuries())
    except Exception as exc:
        print(f"[warn] injuries unavailable: {exc}")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    with connect() as con:
        for row in rows:
            con.execute(
                '''
                INSERT INTO injuries(
                  season,week,team,player_name,position,report_status,
                  practice_status,raw_json,snapshot_ts
                ) VALUES(?,?,?,?,?,?,?,?,?)
                ''',
                (
                    row.get("season"), row.get("week"), row.get("team"),
                    row.get("full_name") or row.get("player_name") or row.get("name"),
                    row.get("position"),
                    row.get("report_status") or row.get("game_status"),
                    row.get("practice_status") or row.get("practice_participation"),
                    json.dumps(row, default=str), now,
                ),
            )
    return len(rows)

def run():
    print(f"[nfl] schedules={ingest_schedules()} injuries={ingest_injuries()}")

if __name__ == "__main__":
    run()
