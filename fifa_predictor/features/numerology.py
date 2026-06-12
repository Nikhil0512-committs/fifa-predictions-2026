from __future__ import annotations

from datetime import date, datetime

LETTER_VALUES = {chr(ord("A") + i): (i % 9) + 1 for i in range(26)}

def reduce_number(value: int) -> int:
    """Reduce to a numerology number while preserving master numbers."""
    while value > 9 and value not in {11, 22, 33}:
        value = sum(int(ch) for ch in str(value))
    return value

def life_path_number(birth_date: date | datetime | str | None) -> int:
    if not birth_date:
        return 0
    if isinstance(birth_date, str):
        birth_date = datetime.fromisoformat(birth_date[:10]).date()
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    raw = int(birth_date.strftime("%Y%m%d"))
    return reduce_number(sum(int(ch) for ch in str(raw)))

def destiny_number(name: str | None) -> int:
    if not name:
        return 0
    total = sum(LETTER_VALUES.get(ch, 0) for ch in name.upper() if ch.isalpha())
    return reduce_number(total)

def player_numerology_resonance(player_name: str, player_dob: str | date | datetime | None, match_date: str | date | datetime | None) -> float:
    destiny = destiny_number(player_name)
    lp = life_path_number(player_dob) if player_dob else 0
    match_lp = life_path_number(match_date) if match_date else 0
    
    if not destiny or not lp or not match_lp:
        return 0.5
        
    diff_destiny = abs(destiny - match_lp)
    diff_lp = abs(lp - match_lp)
    
    score_destiny = 1.0 - (diff_destiny / 9.0)
    score_lp = 1.0 - (diff_lp / 9.0)
    
    return 0.5 * score_destiny + 0.5 * score_lp

def team_numerology_score(team_name: str, match_date: date | datetime | str | None, player_names_dobs: list[tuple[str, str]] | None = None) -> float:
    if not player_names_dobs:
        destiny = destiny_number(team_name)
        if isinstance(match_date, str):
            match_date = datetime.fromisoformat(match_date[:10]).date()
        if isinstance(match_date, datetime):
            match_date = match_date.date()
        day_number = life_path_number(match_date.isoformat()) if match_date else 0
        if not destiny or not day_number:
            return 0.5
        distance = abs(destiny - day_number)
        return max(0.0, 1.0 - distance / 9.0)
        
    resonances = [player_numerology_resonance(name, dob, match_date) for name, dob in player_names_dobs if name and dob]
    return sum(resonances) / len(resonances) if resonances else 0.5
