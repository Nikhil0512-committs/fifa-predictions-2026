# FIFA 2026 Match Prediction System

This project is a modular AI/ML platform for FIFA 2026 match prediction. It predicts match winner, win/draw/loss probabilities, exact scoreline, and confidence for every fixture in the provided 2026 schedule.

Football statistics are the primary predictive signal. Astrology and numerology features are generated as experimental numerical features and exposed as adjustable weights so their contribution can be validated rather than assumed.

## What Is Included

- Data ingestion for the provided ZIP datasets.
- SQLite database with fixtures, team features, predictions, update logs, and a player schema.
- Feature engineering for rankings, form, goals, tournament history, market value, astrology, and numerology.
- Model training with Random Forest and neural network by default, plus auto-detected XGBoost, LightGBM, and CatBoost when installed.
- Regression models for expected goals and exact scoreline generation.
- Ensemble-style match prediction with adjustable football, astrology, and numerology weights.
- Streamlit dashboard with fixture list, predictions, match detail pages, model metrics, and data previews.
- FastAPI endpoints for predictions.
- Public-source collector stubs for APIs and downloaded CSVs.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\initialize.py
python scripts\train.py
python scripts\predict_fixtures.py
streamlit run app\streamlit_app.py
```

The dashboard will show all FIFA 2026 fixtures, predicted winners, scorelines, confidence, team comparison, form-derived football strength, astrology analysis, numerology analysis, and model metrics.

## API

```powershell
uvicorn fifa_predictor.api:app --reload
```

- `GET /health`
- `GET /predictions`
- `GET /predictions/{match_number}`

## Data Notes

The supplied archives contain team-level historical/tournament data and FIFA 2026 fixtures. They do not contain full player-level profiles, birth times, injury feeds, live recent-form tables, or paid-source market values. The project therefore creates the database schema and source-collector interfaces for those fields, while the currently runnable model uses the provided team features.

Recommended enrichments:

- FIFA rankings and match results exports.
- World Football Elo or equivalent national-team Elo files.
- FBref/Sofascore performance exports.
- Transfermarkt market values where legally available.
- Injury reports from licensed feeds or manually curated CSVs.
- Kaggle World Cup and international-results datasets.

## Architecture

```text
fifa_predictor/
  data/
    ingest.py       Load provided data and build SQLite
    sources.py      Public-source download helpers
  features/
    build.py        Football feature engineering
    astrology.py    Experimental astrology features
    numerology.py   Experimental numerology features
  models/
    train.py        Candidate model training and metrics
    predict.py      Fixture prediction and scoreline logic
  api.py            FastAPI app
app/
  streamlit_app.py  Dashboard
scripts/
  initialize.py
  train.py
  predict_fixtures.py
```

## Production Considerations

- Schedule `scripts/initialize.py`, enrichment collectors, `scripts/train.py`, and `scripts/predict_fixtures.py` with cron, Task Scheduler, or Airflow.
- Replace SQLite with PostgreSQL by adapting the ingestion layer to SQLAlchemy.
- Track model metrics over time before increasing experimental feature weights.
- Add player records to the `players` table and extend `features/build.py` with player aggregates.
- Keep source licensing and robots.txt constraints in mind for scraped/public data.
