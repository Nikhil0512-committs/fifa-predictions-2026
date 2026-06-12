import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT match_number, home_team, away_team, predicted_winner, predicted_score 
    FROM fixture_predictions 
    WHERE match_number=25 OR kickoff_at LIKE '%2026-06-18%';
""")
rows = cursor.fetchall()
print("Matches on 18th June:")
for r in rows:
    print("  ", r)

conn.close()
