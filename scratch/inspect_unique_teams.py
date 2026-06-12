import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all unique team names from fixtures_2026
cursor.execute("SELECT DISTINCT home_team FROM fixtures_2026 UNION SELECT DISTINCT away_team FROM fixtures_2026;")
teams = [row[0] for row in cursor.fetchall()]
print("Teams in fixtures_2026:", sorted(teams))

conn.close()
