import sqlite3
from datetime import date, datetime
from fifa_predictor.models.predict import predict_match
from fifa_predictor.knowledge import KEY_PLAYERS

# Name mapping dictionary
NAME_MAPPING = {
    # Spelling corrections
    "Cabo Verde": "Cape Verde",
    "Curaao": "Curaçao",
    "Cte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran",
    "Türkiye": "Turkey",
    "USA": "United States",
    # Placeholder mappings
    "Winner UEFA Playoff A": "Bosnia and Herzegovina",
    "Winner UEFA Playoff B": "Sweden",
    "Winner UEFA Playoff C": "Turkey",
    "Winner UEFA Playoff D": "Czechia",
    "Winner FIFA Playoff 1": "DR Congo",
    "Winner FIFA Playoff 2": "Iraq",
}

def clean_team_name(name):
    return NAME_MAPPING.get(name, name)

def is_placeholder(name):
    # Knockout placeholders like '1A', 'W100', '3ABCDF'
    if name.isdigit() or (len(name) >= 2 and name[0].isdigit()) or name.startswith("W") or name.startswith("RU") or "Playoff" in name:
        return name not in NAME_MAPPING
    return False

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all matches from fixtures_2026
cursor.execute("""
    SELECT match_number, stage_name, match_label, kickoff_at, venue_name, city_name, home_team, away_team 
    FROM fixtures_2026;
""")
fixtures = cursor.fetchall()

print(f"Loaded {len(fixtures)} fixtures from database.")

# Clear existing predictions in the table to avoid stale data
cursor.execute("DELETE FROM fixture_predictions;")

inserted_count = 0
for f in fixtures:
    match_num, stage, group_or_label, kickoff_at, venue, city, home, away = f
    
    # Clean kickoff date
    try:
        # e.g., '2026-06-11 15:00:00-06' -> split at space and take date part
        date_part = kickoff_at.split()[0]
        md = date.fromisoformat(date_part)
    except Exception:
        md = date(2026, 6, 20)
        
    home_clean = clean_team_name(home)
    away_clean = clean_team_name(away)
    
    if is_placeholder(home_clean) or is_placeholder(away_clean):
        # Neutral placeholder prediction
        pred = {
            "winner": "TBD",
            "scoreline": {"team_a": 0, "team_b": 0},
            "probabilities": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
            "confidence": 50.0,
            "team_a_analysis": {"strength": 0.5, "astro_score": 0.5, "numerology_score": 0.5},
            "team_b_analysis": {"strength": 0.5, "astro_score": 0.5, "numerology_score": 0.5},
            "pillar_breakdown": {
                "football": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                "astrology": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                "numerology": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
            }
        }
    else:
        # Run prediction
        try:
            pred = predict_match(
                team_a=home_clean,
                team_b=away_clean,
                match_date=md,
                football_weight=0.3333,
                astro_weight=0.3333,
                numerology_weight=0.3333
            )
        except Exception as e:
            print(f"Error predicting {home_clean} vs {away_clean}: {e}")
            pred = {
                "winner": "TBD",
                "scoreline": {"team_a": 0, "team_b": 0},
                "probabilities": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                "confidence": 50.0,
                "team_a_analysis": {"strength": 0.5, "astro_score": 0.5, "numerology_score": 0.5},
                "team_b_analysis": {"strength": 0.5, "astro_score": 0.5, "numerology_score": 0.5},
                "pillar_breakdown": {
                    "football": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                    "astrology": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                    "numerology": {"win_a": 33.3, "draw": 33.4, "win_b": 33.3},
                }
            }
            
    # Insert prediction
    cursor.execute("""
        INSERT INTO fixture_predictions (
            match_number, stage, group_or_label, kickoff_at, venue, city, home_team, away_team,
            predicted_winner, predicted_score, home_win_probability, draw_probability, away_win_probability,
            confidence, home_football_strength, away_football_strength, home_astrology_score, away_astrology_score,
            home_numerology_score, away_numerology_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        match_num, stage, group_or_label, kickoff_at, venue, city, home, away,
        pred["winner"], f"{pred['scoreline']['team_a']}-{pred['scoreline']['team_b']}",
        pred["probabilities"]["win_a"], pred["probabilities"]["draw"], pred["probabilities"]["win_b"],
        pred["confidence"], pred["team_a_analysis"]["strength"], pred["team_b_analysis"]["strength"],
        pred["team_a_analysis"]["astro_score"], pred["team_b_analysis"]["astro_score"],
        pred["team_a_analysis"]["numerology_score"], pred["team_b_analysis"]["numerology_score"]
    ))
    inserted_count += 1

conn.commit()
conn.close()
print(f"Successfully populated {inserted_count} predictions in fixture_predictions table.")
