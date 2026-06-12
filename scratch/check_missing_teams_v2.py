from fifa_predictor.knowledge import KEY_PLAYERS
from app.streamlit_app import FIXTURES

teams_in_fixtures = set()
for f in FIXTURES:
    teams_in_fixtures.add(f["team_a"])
    teams_in_fixtures.add(f["team_b"])

all_teams = list(KEY_PLAYERS.keys())
missing_teams = [t for t in all_teams if t not in teams_in_fixtures]
print("Missing teams:", missing_teams)
