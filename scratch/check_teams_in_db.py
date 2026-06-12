import sqlite3
import os

dbs = [
    "./data/processed/fifa2026_predictions.db",
    "./data/raw/provided/archive_3/worldcup2026.db"
]

for db in dbs:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Select all teams
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        for t in ["teams", "players"]:
            if t in tables:
                cursor.execute(f"SELECT DISTINCT name FROM {t} ORDER BY name LIMIT 50;" if t == "teams" else f"SELECT DISTINCT nationality FROM {t} ORDER BY nationality LIMIT 50;")
                rows = cursor.fetchall()
                print(f"\nDB: {db}, table: {t}, count: {len(rows)}")
                for r in rows[:15]:
                    print("  ", r)
        conn.close()
