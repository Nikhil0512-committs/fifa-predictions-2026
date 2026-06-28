import sqlite3
import pandas as pd

if __name__ == "__main__":
    db_path = "./data/processed/fifa2026_predictions.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT match_number, home_team, away_team, predicted_winner, predicted_score, confidence FROM fixture_predictions ORDER BY match_number;", conn)
    print(df.head(12).to_string(index=False))
    conn.close()
