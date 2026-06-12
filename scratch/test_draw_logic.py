import sqlite3
import sys

sys.path.append('.')

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all predictions
cursor.execute("""
    SELECT match_number, home_team, away_team, home_win_probability, away_win_probability, draw_probability
    FROM fixture_predictions
    WHERE match_number <= 72;
""")
rows = cursor.fetchall()
conn.close()

thresholds = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
for t in thresholds:
    draws = []
    for r in rows:
        match_num, home, away, p_win, p_loss, p_draw = r
        if abs(p_win - p_loss) < t:
            draws.append((match_num, home, away, p_win, p_loss))
            
    print(f"Threshold {t}%: {len(draws)} draws out of 72 group stage matches.")
    if t == 8.0:
        print("Sample draws:")
        for d in draws[:10]:
            print(f"  Match {d[0]}: {d[1]} vs {d[2]} (Home Win %: {d[3]}, Away Win %: {d[4]}, diff: {abs(d[3]-d[4]):.1f}%)")
