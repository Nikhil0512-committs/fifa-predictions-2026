import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get players of Iraq
cursor.execute("SELECT full_name, date_of_birth, position FROM players WHERE nationality='Iraq';")
iraq_players = cursor.fetchall()
print("Iraq players:")
for p in iraq_players[:12]:
    print(f"    {p}")

# Get players of Czech Republic
cursor.execute("SELECT full_name, date_of_birth, position FROM players WHERE nationality='Czech Republic';")
czech_players = cursor.fetchall()
print("\nCzech Republic players:")
for p in czech_players[:12]:
    print(f"    {p}")
    
conn.close()
