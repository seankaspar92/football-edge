from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / os.getenv("NFL_EDGE_DB", "data/nfl_edge.db")
SITE_DIR = ROOT / "site"

ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
ODDS_REGIONS = os.getenv("ODDS_REGIONS", "us")
ODDS_MARKETS = os.getenv("ODDS_MARKETS", "h2h,spreads,totals")
ODDS_SPORT = "americanfootball_nfl"
