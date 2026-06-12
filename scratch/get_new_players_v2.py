import sqlite3
import json

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def fetch_players(nationality):
    cursor.execute("SELECT full_name, date_of_birth, position FROM players WHERE nationality=?;", (nationality,))
    players = []
    for row in cursor.fetchall():
        name, dob, pos = row
        # Clean positions: e.g. '1GK' -> 'GK', '2DF' -> 'DF', '3MF' -> 'MF', '4FW' -> 'FW'
        clean_pos = pos
        if len(pos) >= 3 and pos[0].isdigit():
            clean_pos = pos[1:]
        players.append((name, dob, clean_pos))
    return players

iraq_p = fetch_players("Iraq")
czech_p = fetch_players("Czech Republic")

# Write to json file
output_data = {
    "Iraq": iraq_p,
    "Czech Republic": czech_p
}

with open("./scratch/players_dump.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print("Players successfully written to ./scratch/players_dump.json")
conn.close()
