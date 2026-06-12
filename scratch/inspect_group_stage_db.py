import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get group stage matches only (stage_id/stage_name = 'Group Stage' or stage_order = 1)
cursor.execute("""
    SELECT id, match_label, home_team, away_team, home_group_letter, kickoff_at 
    FROM fixtures_2026 
    WHERE stage_name='Group Stage' OR stage_order=1
    ORDER BY kickoff_at;
""")
matches = cursor.fetchall()
print(f"Total Group Stage matches in DB: {len(matches)}")
for m in matches[:25]:
    print("  ", m)

conn.close()
