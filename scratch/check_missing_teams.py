from app.streamlit_app import FIXTURES, ALL_TEAMS

teams_in_fixtures = set()
for f in FIXTURES:
    teams_in_fixtures.add(f["team_a"])
    teams_in_fixtures.add(f["team_b"])

missing_teams = [t for t in ALL_TEAMS if t not in teams_in_fixtures]
print("Teams with NO matches in FIXTURES:", missing_teams)
