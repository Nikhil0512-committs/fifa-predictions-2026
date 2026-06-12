import sqlite3

db_path = "./data/processed/fifa2026_predictions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in processed database:", tables)

# Get schema of each table
for table in tables:
    t_name = table[0]
    print(f"\nSchema for table '{t_name}':")
    cursor.execute(f"PRAGMA table_info({t_name});")
    for col in cursor.fetchall():
        print("  ", col)
        
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {t_name};")
    count = cursor.fetchone()[0]
    print(f"Row count in '{t_name}': {count}")
    
conn.close()
