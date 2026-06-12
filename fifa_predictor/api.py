from __future__ import annotations

import sqlite3
import json
import pandas as pd
from fastapi import FastAPI, HTTPException

from fifa_predictor import config
from fifa_predictor.models.predict import predict_fixtures
from fifa_predictor.features.astrology import zodiac_sign
from fifa_predictor.features.numerology import destiny_number, life_path_number

app = FastAPI(title="FIFA 2026 Match Prediction API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/predictions")
def predictions() -> list[dict]:
    if not config.PREDICTIONS_CSV.exists():
        df = predict_fixtures()
    else:
        df = pd.read_csv(config.PREDICTIONS_CSV)
    return df.to_dict(orient="records")


@app.get("/predictions/{match_number}")
def prediction(match_number: int) -> dict:
    df = pd.read_csv(config.PREDICTIONS_CSV) if config.PREDICTIONS_CSV.exists() else predict_fixtures()
    row = df[df["match_number"] == match_number]
    if row.empty:
        raise HTTPException(status_code=404, detail="match_number not found")
    return row.iloc[0].to_dict()


@app.get("/players/{team_name}")
def get_team_players(team_name: str) -> list[dict]:
    if not config.SQLITE_DB.exists():
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    players = []
    try:
        with sqlite3.connect(config.SQLITE_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT full_name, date_of_birth, birth_time, birth_location, nationality,
                       position, current_club, market_value_eur, international_caps,
                       international_goals, recent_form_score, injury_status,
                       performance_metrics_json, source
                FROM players WHERE nationality = ?
                """,
                (team_name,)
            )
            rows = cursor.fetchall()
            for r in rows:
                p_dict = dict(r)
                p_dict["zodiac_sign"] = zodiac_sign(p_dict["date_of_birth"])
                p_dict["life_path_number"] = life_path_number(p_dict["date_of_birth"])
                p_dict["destiny_number"] = destiny_number(p_dict["full_name"])
                try:
                    p_dict["performance_metrics"] = json.loads(p_dict["performance_metrics_json"])
                except Exception:
                    p_dict["performance_metrics"] = {}
                players.append(p_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    if not players:
        raise HTTPException(status_code=404, detail=f"No players found for team '{team_name}'")
        
    return players
