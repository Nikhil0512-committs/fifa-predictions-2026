import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT match_number, home_team, away_team, predicted_winner, predicted_score 
    FROM fixture_predictions 
    WHERE match_number=2;
""")
row = cursor.fetchone()
print("Second Match Prediction (Match 2):")
print("  ", row)

conn.close()
