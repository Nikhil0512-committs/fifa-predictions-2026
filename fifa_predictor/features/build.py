from __future__ import annotations

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

from fifa_predictor import config
from fifa_predictor.features.astrology import team_astrology_score
from fifa_predictor.features.numerology import team_numerology_score

TARGET_COLUMNS = ["winner", "finalist", "semi_finalist", "quarter_finalist"]

def get_team_player_features(team_name: str, match_date: str) -> dict[str, float]:
    out = {
        "avg_player_form": 7.0,
        "injured_doubtful_count": 0.0,
        "total_caps": 300.0,
        "total_goals": 40.0,
        "team_astrology_score": 0.5,
        "team_numerology_score": 0.5,
    }
    
    if not Path(config.SQLITE_DB).exists():
        # Fallback to name-hash calculations
        out["team_astrology_score"] = team_astrology_score(team_name, match_date)
        out["team_numerology_score"] = team_numerology_score(team_name, match_date)
        return out
        
    try:
        with sqlite3.connect(config.SQLITE_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT full_name, date_of_birth, position, market_value_eur, 
                       international_caps, international_goals, recent_form_score, injury_status 
                FROM players WHERE nationality = ?
                """,
                (team_name,)
            )
            rows = cursor.fetchall()
            if not rows:
                # Fallback to name-hash calculations if no players found for this team
                out["team_astrology_score"] = team_astrology_score(team_name, match_date)
                out["team_numerology_score"] = team_numerology_score(team_name, match_date)
                return out
                
            dobs = [r[1] for r in rows if r[1]]
            names_dobs = [(r[0], r[1]) for r in rows if r[0] and r[1]]
            
            valid_forms = [r[6] for r in rows if r[6] is not None]
            out["avg_player_form"] = sum(valid_forms) / len(valid_forms) if valid_forms else 7.0
            out["injured_doubtful_count"] = float(sum(1 for r in rows if r[7] in ["Injured", "Doubtful"]))
            out["total_caps"] = float(sum(r[4] for r in rows if r[4] is not None))
            out["total_goals"] = float(sum(r[5] for r in rows if r[5] is not None))
            
            # Astrology and Numerology aggregated from players
            out["team_astrology_score"] = team_astrology_score(team_name, match_date, dobs)
            out["team_numerology_score"] = team_numerology_score(team_name, match_date, names_dobs)
            
    except Exception as e:
        print(f"Error loading player features for {team_name}: {e}")
        
    return out

def add_derived_team_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    matches = out["wins_last_4y"] + out["losses_last_4y"] + out["draws_last_4y"]
    out["points_per_match_last_4y"] = (out["wins_last_4y"] * 3 + out["draws_last_4y"]) / matches.clip(lower=1)
    out["goal_difference_last_4y"] = out["goals_scored_last_4y"] - out["goals_received_last_4y"]
    out["goals_for_per_match"] = out["goals_scored_last_4y"] / matches.clip(lower=1)
    out["goals_against_per_match"] = out["goals_received_last_4y"] / matches.clip(lower=1)
    out["market_value_log"] = np.log(out["squad_total_market_value_eur"].clip(lower=0) + 1)
    out["ranking_strength"] = 1 / out["fifa_rank_pre_tournament"].clip(lower=1)
    out["tournament_depth"] = (
        out["groups_passed_before"]
        + 1.5 * out["round16_before"]
        + 2.0 * out["quarterfinals_before"]
        + 2.5 * out["semifinals_before"]
        + 3.0 * out["finals_before"]
    )
    return out

def add_experimental_features(df: pd.DataFrame, match_date: str = "2026-06-11") -> pd.DataFrame:
    out = df.copy()
    
    # Pre-allocate feature columns
    avg_form_list = []
    injured_list = []
    caps_list = []
    goals_list = []
    astro_list = []
    num_list = []
    
    for _, row in out.iterrows():
        team_name = str(row["team"])
        feats = get_team_player_features(team_name, match_date)
        avg_form_list.append(feats["avg_player_form"])
        injured_list.append(feats["injured_doubtful_count"])
        caps_list.append(feats["total_caps"])
        goals_list.append(feats["total_goals"])
        astro_list.append(feats["team_astrology_score"])
        num_list.append(feats["team_numerology_score"])
        
    out["avg_player_form"] = avg_form_list
    out["injured_doubtful_count"] = injured_list
    out["total_caps"] = caps_list
    out["total_goals"] = goals_list
    out["team_astrology_score"] = astro_list
    out["team_numerology_score"] = num_list
    
    return out

def model_feature_columns(df: pd.DataFrame) -> list[str]:
    excluded = {"team", "version", *TARGET_COLUMNS}
    return [col for col in df.columns if col not in excluded]
