from __future__ import annotations
import sqlite3
from .config import DB_PATH

DDL = '''
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_ts TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    season INTEGER,
    week INTEGER,
    game_type TEXT,
    gameday TEXT,
    gametime TEXT,
    away_team TEXT,
    home_team TEXT,
    away_score REAL,
    home_score REAL,
    stadium TEXT,
    roof TEXT,
    surface TEXT,
    temp REAL,
    wind REAL,
    spread_line REAL,
    total_line REAL,
    home_moneyline REAL,
    away_moneyline REAL,
    raw_json TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS injuries (
    season INTEGER,
    week INTEGER,
    team TEXT,
    player_name TEXT,
    position TEXT,
    report_status TEXT,
    practice_status TEXT,
    raw_json TEXT,
    snapshot_ts TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
    snapshot_ts TEXT NOT NULL,
    event_id TEXT NOT NULL,
    commence_time TEXT,
    home_team TEXT,
    away_team TEXT,
    bookmaker_key TEXT NOT NULL,
    bookmaker_title TEXT,
    market_key TEXT NOT NULL,
    outcome_name TEXT NOT NULL,
    price REAL,
    point REAL,
    last_update TEXT,
    PRIMARY KEY (
      snapshot_ts,event_id,bookmaker_key,market_key,outcome_name,price,point
    )
);

CREATE INDEX IF NOT EXISTS idx_odds_event
ON odds_snapshots(event_id, snapshot_ts);

CREATE INDEX IF NOT EXISTS idx_odds_matchup
ON odds_snapshots(home_team, away_team, snapshot_ts);
'''

def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(DDL)
    return con
