import sys
from datetime import date
from fifa_predictor.models.predict import predict_match
from app.streamlit_app import FIXTURES

print("Testing all fixtures predictions...")
success_count = 0
failed_count = 0

for idx, f in enumerate(FIXTURES):
    try:
        md = date.fromisoformat(f["date"])
        res = predict_match(
            team_a=f["team_a"],
            team_b=f["team_b"],
            match_date=md,
            football_weight=0.3333,
            astro_weight=0.3333,
            numerology_weight=0.3333
        )
        success_count += 1
    except Exception as e:
        print(f"FAILED on fixture index {idx}: {f['team_a']} vs {f['team_b']} on {f['date']}. Error: {e}")
        failed_count += 1

print(f"Total Success: {success_count}, Total Failed: {failed_count}")
