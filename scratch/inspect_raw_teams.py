import sqlite3

db = "./data/raw/provided/archive_3/worldcup2026.db"
conn = sqlite3.connect(db)
cursor = conn.cursor()

# Get columns of table 'teams'
cursor.execute("PRAGMA table_info(teams);")
for col in cursor.fetchall():
    print("Column:", col)
    
# Get all teams in raw teams table
cursor.execute("SELECT * FROM teams;")
rows = cursor.fetchall()
print(f"Total teams in raw database: {len(rows)}")
for r in rows:
    print("  ", r)

conn.close()
