import sqlite3
import sys
import hashlib
from datetime import date

sys.path.append('.')

from fifa_predictor.knowledge import get_team_strength, RECENT_FORM, ELO_RATINGS
from fifa_predictor.models.predict import predict_match

NAME_MAPPING = {
    "Cabo Verde": "Cape Verde", "Curaao": "Curaçao", "Cte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran", "Türkiye": "Turkey", "USA": "United States",
    "Winner UEFA Playoff A": "Bosnia and Herzegovina", "Winner UEFA Playoff B": "Sweden",
    "Winner UEFA Playoff C": "Turkey", "Winner UEFA Playoff D": "Czechia",
    "Winner FIFA Playoff 1": "DR Congo", "Winner FIFA Playoff 2": "Iraq",
}

def clean_team_name(name):
    return NAME_MAPPING.get(name, name)

def is_placeholder(name):
    if name.isdigit() or (len(name) >= 2 and name[0].isdigit()) or name.startswith("W") or name.startswith("RU") or "Playoff" in name:
        return name not in NAME_MAPPING
    return False

def get_outcome_and_score(team_a, team_b, md, p_win, p_draw, p_loss, match_num):
    # If the user explicitly requested, use overrides
    if match_num == 1:
        return "win", "Mexico", (2, 0)
    if match_num == 2:
        return "win", "South Korea", (2, 1)
        
    pw = p_win / 100.0
    pd = p_draw / 100.0
    pl = p_loss / 100.0
    
    # Draw threshold of 5.5% for group stage
    is_group = match_num <= 72
    if is_group and abs(pw - pl) < 0.055:
        outcome = "draw"
        winner = "Draw"
    elif pw >= pl:
        outcome = "win"
        winner = team_a
    else:
        outcome = "loss"
        winner = team_b
        
    # Scoreline logic
    sa = get_team_strength(team_a)
    sb = get_team_strength(team_b)
    
    form_a = RECENT_FORM.get(team_a, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    form_b = RECENT_FORM.get(team_b, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    
    moon_clean_sheet = False
    if md is not None:
        cycle_day = (md.toordinal() % 29)
        if cycle_day <= 3 or 18 <= cycle_day <= 28:
            moon_clean_sheet = True
            
    date_str = md.isoformat() if md else "2026-06-20"
    match_key = f"{team_a}:{team_b}:{date_str}"
    hash_val = int(hashlib.md5(match_key.encode()).hexdigest(), 16) % 100
    
    strong_defense_a = form_a["ga"] < 10
    strong_defense_b = form_b["ga"] < 10
    weak_attack_a = form_a["gf"] < 11
    weak_attack_b = form_b["gf"] < 11
    
    clean_sheet_bias = 0
    if strong_defense_a or weak_attack_b:
        clean_sheet_bias += 1
    if moon_clean_sheet:
        clean_sheet_bias += 1
        
    if outcome == "draw":
        avg_strength = (sa + sb) / 2
        if avg_strength > 0.65:
            choices = [(2, 2)] * 70 + [(3, 3)] * 10 + [(1, 1)] * 20
        elif avg_strength < 0.45:
            choices = [(0, 0)] * 60 + [(1, 1)] * 40
        else:
            choices = [(1, 1)] * 65 + [(0, 0)] * 20 + [(2, 2)] * 15
        score = choices[hash_val % len(choices)]
    elif outcome == "win":
        diff = pw - pl
        if diff >= 0.45:
            if clean_sheet_bias >= 1:
                choices = [(3, 0)] * 45 + [(2, 0)] * 35 + [(4, 0)] * 20
            else:
                choices = [(3, 1)] * 35 + [(3, 0)] * 30 + [(4, 1)] * 20 + [(2, 0)] * 15
        elif diff >= 0.25:
            if clean_sheet_bias >= 2:
                choices = [(2, 0)] * 60 + [(1, 0)] * 40
            elif clean_sheet_bias == 1:
                choices = [(2, 0)] * 45 + [(1, 0)] * 25 + [(3, 0)] * 15 + [(2, 1)] * 15
            else:
                choices = [(2, 1)] * 40 + [(3, 1)] * 25 + [(2, 0)] * 20 + [(1, 0)] * 15
        else:
            if clean_sheet_bias >= 2:
                choices = [(1, 0)] * 80 + [(2, 0)] * 20
            elif clean_sheet_bias == 1:
                choices = [(1, 0)] * 60 + [(2, 1)] * 40
            else:
                choices = [(2, 1)] * 55 + [(1, 0)] * 30 + [(3, 2)] * 15
        score = choices[hash_val % len(choices)]
    else:
        diff = pl - pw
        if diff >= 0.45:
            if clean_sheet_bias >= 1:
                choices = [(0, 3)] * 45 + [(0, 2)] * 35 + [(0, 4)] * 20
            else:
                choices = [(1, 3)] * 35 + [(0, 3)] * 30 + [(1, 4)] * 20 + [(0, 2)] * 15
        elif diff >= 0.25:
            if clean_sheet_bias >= 2:
                choices = [(0, 2)] * 60 + [(0, 1)] * 40
            elif clean_sheet_bias == 1:
                choices = [(0, 2)] * 45 + [(0, 1)] * 25 + [(0, 3)] * 15 + [(1, 2)] * 15
            else:
                choices = [(1, 2)] * 40 + [(1, 3)] * 25 + [(0, 2)] * 20 + [(0, 1)] * 15
        else:
            if clean_sheet_bias >= 2:
                choices = [(0, 1)] * 80 + [(0, 2)] * 20
            elif clean_sheet_bias == 1:
                choices = [(0, 1)] * 60 + [(1, 2)] * 40
            else:
                choices = [(1, 2)] * 55 + [(0, 1)] * 30 + [(2, 3)] * 15
        score = choices[hash_val % len(choices)]
        
    return outcome, winner, score

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("""
    SELECT match_number, kickoff_at, home_team, away_team, home_win_probability, draw_probability, away_win_probability
    FROM fixture_predictions;
""")
rows = cur.fetchall()
conn.close()

score_counts = {}
outcome_counts = {"win": 0, "draw": 0, "loss": 0}
sample_preds = []

for r in rows:
    num, kickoff, home, away, p_win, p_draw, p_loss = r
    home_clean = clean_team_name(home)
    away_clean = clean_team_name(away)
    
    try:
        md = date.fromisoformat(kickoff.split()[0])
    except Exception:
        md = date(2026, 6, 20)
        
    if is_placeholder(home_clean) or is_placeholder(away_clean):
        outcome = "draw"
        winner = "TBD"
        score = (0, 0)
    else:
        outcome, winner, score = get_outcome_and_score(home_clean, away_clean, md, p_win, p_draw, p_loss, num)
        
    score_str = f"{score[0]}-{score[1]}"
    score_counts[score_str] = score_counts.get(score_str, 0) + 1
    if num <= 72:
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        
    if num <= 40:
        sample_preds.append((num, home_clean, away_clean, winner, score_str))

print("\n--- Outcome Counts (Group Stage only) ---")
for k, v in outcome_counts.items():
    print(f"  {k}: {v}")

print("\n--- Scoreline Distribution ---")
for k, v in sorted(score_counts.items()):
    print(f"  {k}: {v}")

print("\n--- Sample of first 40 matches ---")
for s in sample_preds:
    print(f"Match {s[0]}: {s[1]} vs {s[2]} -> Winner: {s[3]} | Score: {s[4]}")
