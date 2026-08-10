# NFL EDGE Starter

Deployable MVP for continuously collecting NFL data and sportsbook odds, storing timestamped snapshots, building a live market board, and publishing it through GitHub Actions + GitHub Pages.

## What this starter does

- Loads NFL schedules/results and injury data through `nflreadpy`.
- Pulls NFL moneyline, spread, and total prices from The Odds API.
- Stores timestamped odds snapshots in SQLite.
- Builds a simple consensus board from the latest bookmaker snapshot.
- Runs automatically with GitHub Actions.
- Publishes a static dashboard through GitHub Pages.
- Leaves a clean integration hook in `src/predict.py` for validated NFL EDGE models.

## Important

This starter deliberately does not invent model probabilities. Until a validated model artifact is installed, the dashboard displays market information only.

## Setup

1. Create a GitHub repository named `nfl-edge`.
2. Upload the contents of this folder.
3. Create an API key with The Odds API.
4. In GitHub: `Settings -> Secrets and variables -> Actions -> New repository secret`
5. Add secret `ODDS_API_KEY`.
6. In GitHub: `Settings -> Pages -> Source -> GitHub Actions`.
7. Open `Actions -> NFL EDGE Refresh -> Run workflow`.

## Automatic schedule

Configured in `America/Chicago`:

- Daily: 6:17 AM CT
- Thursday: 5:17 PM CT
- Sunday: 8:17 AM, 10:17 AM, 11:17 AM, 2:17 PM, 5:17 PM CT
- Monday: 5:17 PM CT

## Local run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

python -m src.pipeline
```

Open `site/index.html`.

## Next production upgrades

1. Add the validated totals model to `models/`.
2. Add model-version metadata and walk-forward validation checks.
3. Add weather by stadium coordinates.
4. Add projected starters and stronger injury weighting.
5. Backfill timestamped historical odds for CLV training.
6. Capture closing lines automatically.
7. Add bet grading, bankroll, CLV, Brier score, and kill switches.
8. Move SQLite to Postgres when the data volume warrants it.
