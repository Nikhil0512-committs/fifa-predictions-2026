import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check unique nationalities in players table
cursor.execute("SELECT DISTINCT nationality FROM players ORDER BY nationality;")
nationalities = [row[0] for row in cursor.fetchall()]
print("Nationalities in players table:", nationalities)

# Search specifically for Iraq and Czechia/Czech Republic
for nat in ["Iraq", "Czechia", "Czech Republic"]:
    cursor.execute("SELECT COUNT(*) FROM players WHERE nationality=?;", (nat,))
    print(f"Count for '{nat}':", cursor.fetchone()[0])
    
conn.close()
