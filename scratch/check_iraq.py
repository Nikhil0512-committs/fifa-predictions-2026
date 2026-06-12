import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for Iraq in fixtures_2026
cursor.execute("SELECT COUNT(*) FROM fixtures_2026 WHERE home_team LIKE '%Iraq%' OR away_team LIKE '%Iraq%';")
count = cursor.fetchone()[0]
print("Iraq matches count in fixtures_2026:", count)

# Print any Iraq matches
if count > 0:
    cursor.execute("SELECT match_number, home_team, away_team, kickoff_at FROM fixtures_2026 WHERE home_team LIKE '%Iraq%' OR away_team LIKE '%Iraq%';")
    for row in cursor.fetchall():
        print("  ", row)

conn.close()
