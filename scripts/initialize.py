from fifa_predictor.data.ingest import build_sqlite_database


if __name__ == "__main__":
    path = build_sqlite_database()
    print(f"SQLite database initialized at {path}")
