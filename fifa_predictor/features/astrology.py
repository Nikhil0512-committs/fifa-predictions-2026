from __future__ import annotations

from datetime import date, datetime
from math import sin, cos, pi

ZODIAC_SIGNS = [
    ("Capricorn", (1, 20)),
    ("Aquarius", (2, 19)),
    ("Pisces", (3, 21)),
    ("Aries", (4, 20)),
    ("Taurus", (5, 21)),
    ("Gemini", (6, 21)),
    ("Cancer", (7, 23)),
    ("Leo", (8, 23)),
    ("Virgo", (9, 23)),
    ("Libra", (10, 23)),
    ("Scorpio", (11, 22)),
    ("Sagittarius", (12, 22)),
    ("Capricorn", (12, 32)),
]

ZODIAC_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

ELEMENT_COMPATIBILITY = {
    ("Fire", "Fire"): 1.0, ("Fire", "Air"): 0.8, ("Fire", "Earth"): 0.4, ("Fire", "Water"): 0.2,
    ("Earth", "Earth"): 1.0, ("Earth", "Water"): 0.8, ("Earth", "Fire"): 0.4, ("Earth", "Air"): 0.4,
    ("Air", "Air"): 1.0, ("Air", "Fire"): 0.8, ("Air", "Earth"): 0.4, ("Air", "Water"): 0.3,
    ("Water", "Water"): 1.0, ("Water", "Earth"): 0.8, ("Water", "Fire"): 0.2, ("Water", "Air"): 0.3,
}

def zodiac_sign(birth_date: date | datetime | str | None) -> str:
    if not birth_date:
        return "Unknown"
    if isinstance(birth_date, str):
        birth_date = datetime.fromisoformat(birth_date[:10]).date()
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    month_day = (birth_date.month, birth_date.day)
    for sign, cutoff in ZODIAC_SIGNS:
        if month_day < cutoff:
            return sign
    return "Capricorn"

def approximate_planetary_positions(moment: date | datetime | str | None) -> dict[str, float]:
    if not moment:
        return {f"{body}_deg": 0.0 for body in ["sun", "moon", "mercury", "venus", "mars"]}
    if isinstance(moment, str):
        moment = datetime.fromisoformat(moment[:10]).date()
    if isinstance(moment, datetime):
        moment = moment.date()
    day = moment.toordinal()
    cycles = {"sun": 365.25, "moon": 27.32, "mercury": 88.0, "venus": 225.0, "mars": 687.0}
    return {f"{body}_deg": float((day % cycle) / cycle * 360.0) for body, cycle in cycles.items()}

def player_astrology_resonance(player_dob: str | date | datetime | None, match_date: str | date | datetime | None) -> float:
    if not player_dob or not match_date:
        return 0.5
    
    p_sign = zodiac_sign(player_dob)
    m_sign = zodiac_sign(match_date)
    
    p_elem = ZODIAC_ELEMENTS.get(p_sign, "Fire")
    m_elem = ZODIAC_ELEMENTS.get(m_sign, "Fire")
    
    elem_score = ELEMENT_COMPATIBILITY.get((p_elem, m_elem), 0.5)
    if (m_elem, p_elem) in ELEMENT_COMPATIBILITY:
        elem_score = ELEMENT_COMPATIBILITY.get((m_elem, p_elem), 0.5)
        
    p_pos = approximate_planetary_positions(player_dob)
    m_pos = approximate_planetary_positions(match_date)
    
    aspect_scores = []
    for body in ["sun", "moon", "mercury", "venus", "mars"]:
        diff = abs(p_pos[f"{body}_deg"] - m_pos[f"{body}_deg"]) % 360
        if diff > 180:
            diff = 360 - diff
            
        if diff < 10:
            aspect_scores.append(1.0)
        elif abs(diff - 120) < 10:
            aspect_scores.append(0.9)
        elif abs(diff - 60) < 10:
            aspect_scores.append(0.8)
        elif abs(diff - 180) < 10:
            aspect_scores.append(0.6)
        elif abs(diff - 90) < 10:
            aspect_scores.append(0.3)
        else:
            aspect_scores.append(0.5)
            
    avg_aspect = sum(aspect_scores) / len(aspect_scores)
    return 0.4 * elem_score + 0.6 * avg_aspect

def team_astrology_score(team_name: str, match_date: date | datetime | str | None, player_dobs: list[str] | None = None) -> float:
    if not player_dobs:
        # Fallback to name hash resonance
        positions = approximate_planetary_positions(match_date)
        name_hash = sum(ord(ch) for ch in team_name) % 360
        sun = positions["sun_deg"] * pi / 180
        moon = positions["moon_deg"] * pi / 180
        resonance = sin(sun + name_hash) + 0.5 * cos(moon - name_hash)
        return max(0.0, min(1.0, (resonance + 1.5) / 3.0))
    
    resonances = [player_astrology_resonance(dob, match_date) for dob in player_dobs if dob]
    return sum(resonances) / len(resonances) if resonances else 0.5
