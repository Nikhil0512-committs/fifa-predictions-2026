import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check some rows from fixtures_2026
cursor.execute("SELECT DISTINCT home_team, away_team FROM fixtures_2026 LIMIT 15;")
print("fixtures_2026 teams:")
for row in cursor.fetchall():
    print("  ", row)

# Check some rows from fixture_predictions
cursor.execute("SELECT DISTINCT home_team, away_team, predicted_winner FROM fixture_predictions LIMIT 15;")
print("\nfixture_predictions teams:")
for row in cursor.fetchall():
    print("  ", row)

# Search specifically for Argentina, Portugal, etc. in fixture_predictions
print("\nPredictions for Argentina, Portugal, DR Congo, Colombia, Uzbekistan:")
teams = ["Argentina", "Portugal", "DR Congo", "Colombia", "Uzbekistan"]
for t in teams:
    cursor.execute("SELECT COUNT(*) FROM fixture_predictions WHERE home_team=? OR away_team=?;", (t, t))
    count = cursor.fetchone()[0]
    print(f"  {t} predictions count: {count}")
    
conn.close()
