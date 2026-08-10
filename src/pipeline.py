from __future__ import annotations
from datetime import datetime, timezone
import traceback
from .db import connect
from . import ingest_nfl, ingest_odds
from .build_site import build

def main():
    started = datetime.now(timezone.utc).isoformat()
    status = "ok"
    notes = None
    try:
        ingest_nfl.run()
        ingest_odds.run()
        build()
    except Exception:
        status = "failed"
        notes = traceback.format_exc()
        raise
    finally:
        with connect() as con:
            con.execute(
                "INSERT INTO pipeline_runs(run_ts,status,notes) VALUES(?,?,?)",
                (started,status,notes),
            )

if __name__ == "__main__":
    main()
