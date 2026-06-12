import sqlite3
import sys
import hashlib
from datetime import date

sys.path.append('.')

from fifa_predictor.knowledge import get_team_strength, RECENT_FORM, ELO_RATINGS
from fifa_predictor.models.predict import football_probabilities, astro_probabilities, numerology_probabilities

def test_prediction(team_a, team_b, match_date, draw_coef=0.35, draw_slope=0.30):
    # Re-implement fusion with custom draw_base parameters
    # 1. Football
    elo_a = ELO_RATINGS.get(team_a, 1500)
    # Form adjustment
    form_a = RECENT_FORM.get(team_a, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    pts_a = form_a["w"] * 3 + form_a["d"]
    form_score_a = 0.70 * (pts_a / 30.0) + 0.30 * max(0.0, min(1.0, ((form_a["gf"] - form_a["ga"]) + 15) / 30.0))
    elo_a += (form_score_a - 0.5) * 240.0
    
    elo_b = ELO_RATINGS.get(team_b, 1500)
    form_b = RECENT_FORM.get(team_b, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    pts_b = form_b["w"] * 3 + form_b["d"]
    form_score_b = 0.70 * (pts_b / 30.0) + 0.30 * max(0.0, min(1.0, ((form_b["gf"] - form_b["ga"]) + 15) / 30.0))
    elo_b += (form_score_b - 0.5) * 240.0
    
    d = elo_a - elo_b
    we = 1 / (1 + 10 ** (-d / 400))
    draw_base = draw_coef - draw_slope * abs(we - 0.5)
    f_pw = we * (1 - draw_base)
    f_pl = (1 - we) * (1 - draw_base)
    f_pd = draw_base
    s = f_pw + f_pl + f_pd
    f_pw, f_pd, f_pl = f_pw / s, f_pd / s, f_pl / s
    
    # Rest of football probabilities
    titles_a = {"Brazil": 5, "Germany": 4, "Italy": 4, "Argentina": 3, "France": 2, "Uruguay": 2, "England": 1, "Spain": 1}.get(team_a, 0)
    parts_a = {"Brazil": 22, "Germany": 20, "Italy": 18, "Argentina": 18, "France": 16, "England": 16, "Spain": 16, "Mexico": 17, "South Korea": 10}.get(team_a, 2)
    pa = min(0.05, titles_a * 0.012 + parts_a * 0.001)
    
    titles_b = {"Brazil": 5, "Germany": 4, "Italy": 4, "Argentina": 3, "France": 2, "Uruguay": 2, "England": 1, "Spain": 1}.get(team_b, 0)
    parts_b = {"Brazil": 22, "Germany": 20, "Italy": 18, "Argentina": 18, "France": 16, "England": 16, "Spain": 16, "Mexico": 17, "South Korea": 10}.get(team_b, 2)
    pb = min(0.05, titles_b * 0.012 + parts_b * 0.001)
    
    f_pw += pa * 0.5
    f_pl += pb * 0.5
    
    sa = get_team_strength(team_a)
    sb = get_team_strength(team_b)
    sr_a = sa / (sa + sb)
    blend = 0.15
    f_pw = f_pw * (1 - blend) + sr_a * blend
    f_pl = f_pl * (1 - blend) + (1 - sr_a) * blend
    
    # H2H and host biases
    hosts = {"United States", "Canada", "Mexico"}
    if team_a in hosts: f_pw += 0.05
    if team_b in hosts: f_pl += 0.05
    
    f_pw = max(0.01, min(0.97, f_pw))
    f_pl = max(0.01, min(0.97, f_pl))
    s = f_pw + f_pd + f_pl
    f_pw, f_pd, f_pl = f_pw / s, f_pd / s, f_pl / s
    
    # Astro
    a_pw, a_pd, a_pl = astro_probabilities(team_a, team_b, match_date)
    # Numerology
    n_pw, n_pd, n_pl = numerology_probabilities(team_a, team_b, match_date)
    
    # Fuse
    pw = (0.3333 * f_pw + 0.3333 * a_pw + 0.3333 * n_pw)
    pd = (0.3333 * f_pd + 0.3333 * a_pd + 0.3333 * n_pd)
    pl = (0.3333 * f_pl + 0.3333 * a_pl + 0.3333 * n_pl)
    
    # MR
    is_retrograde = False
    ranges = [
        (date(2026, 2, 25), date(2026, 3, 20)),
        (date(2026, 6, 29), date(2026, 7, 23)),
        (date(2026, 10, 24), date(2026, 11, 16)),
    ]
    for start, end in ranges:
        if start <= match_date <= end:
            is_retrograde = True
            break
    if is_retrograde:
        if pw > pl:
            shift = min(pw - 0.33, 0.04)
            pw -= shift; pl += shift
        elif pl > pw:
            shift = min(pl - 0.33, 0.04)
            pl -= shift; pw += shift
            
    # Temp scaling
    gamma = 1.35
    pw_scaled = pw ** gamma
    pd_scaled = pd ** gamma
    pl_scaled = pl ** gamma
    s = pw_scaled + pd_scaled + pl_scaled
    pw, pd, pl = pw_scaled / s, pd_scaled / s, pl_scaled / s
    
    if pw >= pl and pw >= pd:
        outcome = "win"
    elif pd >= pw and pd >= pl:
        outcome = "draw"
    else:
        outcome = "loss"
        
    return outcome, pw, pd, pl

# Load group fixtures
db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT match_number, home_team, away_team, kickoff_at FROM fixtures_2026 WHERE match_number <= 72")
fixtures = cur.fetchall()
conn.close()

NAME_MAPPING = {
    "Cabo Verde": "Cape Verde", "Curaao": "Curaçao", "Cte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran", "Türkiye": "Turkey", "USA": "United States",
    "Winner UEFA Playoff A": "Bosnia and Herzegovina", "Winner UEFA Playoff B": "Sweden",
    "Winner UEFA Playoff C": "Turkey", "Winner UEFA Playoff D": "Czechia",
    "Winner FIFA Playoff 1": "DR Congo", "Winner FIFA Playoff 2": "Iraq",
}

for coef, slope in [(0.33, 0.25), (0.34, 0.25), (0.35, 0.30), (0.36, 0.30)]:
    draw_matches = []
    for f in fixtures:
        num, home, away, kickoff = f
        home_clean = NAME_MAPPING.get(home, home)
        away_clean = NAME_MAPPING.get(away, away)
        try:
            md = date.fromisoformat(kickoff.split()[0])
        except Exception:
            md = date(2026, 6, 20)
            
        outcome, pw, pd, pl = test_prediction(home_clean, away_clean, md, coef, slope)
        if outcome == "draw":
            draw_matches.append((num, home_clean, away_clean, pw, pd, pl))
            
        if num == 2:
            match2_info = (home_clean, away_clean, outcome, pw, pd, pl)
            
    print(f"\nParameters: draw_base = {coef} - {slope} * |we - 0.5|")
    print(f"  Total predicted draws in group stage: {len(draw_matches)}")
    print(f"  Match 2 (South Korea vs Czechia) outcome: {match2_info[2]} (p_win: {match2_info[3]*100:.1f}%, p_draw: {match2_info[4]*100:.1f}%, p_loss: {match2_info[5]*100:.1f}%)")
    if len(draw_matches) > 0:
        print("  Sample draws:")
        for dm in draw_matches[:8]:
            print(f"    Match {dm[0]}: {dm[1]} vs {dm[2]} ({dm[3]*100:.1f}% / {dm[4]*100:.1f}% / {dm[5]*100:.1f}%)")
