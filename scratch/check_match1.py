import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT match_number, home_team, away_team, predicted_winner, predicted_score, confidence 
    FROM fixture_predictions 
    WHERE match_number=1;
""")
row = cursor.fetchone()
print("First Match Prediction (Match 1):")
print("  ", row)

conn.close()
