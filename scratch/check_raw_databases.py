import sqlite3
import os

db_paths = [
    "./data/raw/provided/archive_3/worldcup2026.db",
    "./data/raw/provided/archive_4/worldcup2026.db",
    "./data/raw/provided/archive_5/worldcup2026.db"
]

for db in db_paths:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"\nDB: {db}, tables: {tables}")
        
        # Search for Iraq
        for table in tables:
            try:
                cursor.execute(f"PRAGMA table_info({table});")
                cols = [c[1] for c in cursor.fetchall()]
                
                # Check text columns
                text_cols = []
                for c in cols:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE [{c}] LIKE '%Iraq%' OR [{c}] LIKE '%Iraq%';")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"  Found Iraq in table {table}, column {c}: {count} times")
            except Exception as e:
                pass
        conn.close()
