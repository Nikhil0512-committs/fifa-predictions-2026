"""
predict.py – ULTRA-PRECISION FIFA 2026 Match Prediction Engine

Combines three independent intelligence pillars:
  1. Football Intelligence  (Elo, FIFA rank, form, squad value, H2H)
  2. Astrological Analysis  (planetary strength, aspect scores, moon phases)
  3. Numerological Analysis (Pythagorean life-path resonance, match-date vibration)

Each pillar produces independent probabilities, fused via calibrated Bayesian weighting.
"""

from __future__ import annotations

import math
import hashlib
from datetime import date, datetime
from typing import Any

from fifa_predictor.knowledge import (
    FIFA_RANKINGS,
    ELO_RATINGS,
    RECENT_FORM,
    SQUAD_VALUE_M,
    TITLES,
    PARTICIPATIONS,
    KEY_PLAYERS,
    get_team_strength,
)

# ─── Weights for the three pillars (Equal Weightage) ───────────────────────────
FOOTBALL_W   = 0.3333
ASTRO_W      = 0.3333
NUMEROLOGY_W = 0.3333

# ─── 1. FOOTBALL ENGINE ────────────────────────────────────────────────────────

def _elo_win_probability(elo_a: float, elo_b: float) -> tuple[float, float, float]:
    """
    Returns (p_win_a, p_draw, p_win_b) using WFC Elo model.
    """
    d = elo_a - elo_b
    we = 1 / (1 + 10 ** (-d / 400))
    # Draw adjustment: higher near 50/50, lower for mismatches
    draw_base = 0.26 - 0.20 * abs(we - 0.5)
    p_win_a = we * (1 - draw_base)
    p_win_b = (1 - we) * (1 - draw_base)
    p_draw = draw_base
    s = p_win_a + p_win_b + p_draw
    return p_win_a / s, p_draw / s, p_win_b / s


def _form_elo_adjustment(team: str) -> float:
    """
    Returns an Elo rating adjustment (-120 to +120 points) based on current form
    of the team's last 10 competitive international matches.
    """
    form = RECENT_FORM.get(team, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    pts = form["w"] * 3 + form["d"]
    pts_ratio = pts / 30.0
    gd = form["gf"] - form["ga"]
    gd_ratio = max(0.0, min(1.0, (gd + 15) / 30.0))
    form_score = 0.70 * pts_ratio + 0.30 * gd_ratio
    return (form_score - 0.5) * 240.0


def _pedigree_adjustment(team: str) -> float:
    """Returns 0 … +0.05 bonus for World Cup pedigree."""
    titles = TITLES.get(team, 0)
    parts = PARTICIPATIONS.get(team, 2)
    return min(0.05, titles * 0.012 + parts * 0.001)


def football_probabilities(team_a: str, team_b: str) -> tuple[float, float, float]:
    """
    Returns (p_win_a, p_draw, p_win_b) from football signals only.
    Form is factored directly into the team Elo ratings.
    """
    # Elo rating adjusted dynamically by recent form of last 10 international matches
    elo_a = ELO_RATINGS.get(team_a, 1500) + _form_elo_adjustment(team_a)
    elo_b = ELO_RATINGS.get(team_b, 1500) + _form_elo_adjustment(team_b)

    pw, pd, pl = _elo_win_probability(elo_a, elo_b)

    # Pedigree
    pa = _pedigree_adjustment(team_a)
    pb = _pedigree_adjustment(team_b)
    pw += pa * 0.5
    pl += pb * 0.5

    # Strength cross-check
    sa = get_team_strength(team_a)
    sb = get_team_strength(team_b)
    # Strength blend: pull probs 15% toward strength ratio
    sr_a = sa / (sa + sb)
    sr_b = 1 - sr_a
    blend = 0.15
    pw = pw * (1 - blend) + sr_a * blend
    pl = pl * (1 - blend) + sr_b * blend

    # H2H Rivalry Bias
    h2h_bias = {
        ("France", "Croatia"): 0.08,
        ("Germany", "Argentina"): 0.06,
        ("Brazil", "Morocco"): 0.05,
        ("Argentina", "France"): 0.02,
        ("Spain", "Portugal"): 0.01,
        ("England", "Germany"): -0.04,
        ("Netherlands", "Argentina"): -0.03,
        ("Belgium", "Brazil"): -0.05,
    }
    bias = h2h_bias.get((team_a, team_b), 0.0)
    if bias == 0.0 and (team_b, team_a) in h2h_bias:
        bias = -h2h_bias[(team_b, team_a)]
    pw += bias
    pl -= bias

    # Host Home Advantage (USA, Canada, Mexico)
    hosts = {"United States", "Canada", "Mexico"}
    if team_a in hosts:
        pw += 0.05
    if team_b in hosts:
        pl += 0.05

    # Clamp & normalise
    pw = max(0.01, min(0.97, pw))
    pl = max(0.01, min(0.97, pl))
    pd = max(0.01, pd)
    s = pw + pd + pl
    return pw / s, pd / s, pl / s


# ─── 2. ASTROLOGICAL ENGINE ────────────────────────────────────────────────────

ZODIAC_ELEMENTS: dict[str, str] = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

ZODIAC_MODES: dict[str, str] = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}

ELEMENT_COMPATIBILITY: dict[tuple[str, str], float] = {
    ("Fire", "Fire"): 0.80, ("Earth", "Earth"): 0.75, ("Air", "Air"): 0.72,
    ("Water", "Water"): 0.73,
    ("Fire", "Air"): 0.82, ("Air", "Fire"): 0.82,
    ("Earth", "Water"): 0.78, ("Water", "Earth"): 0.78,
    ("Fire", "Earth"): 0.50, ("Earth", "Fire"): 0.50,
    ("Fire", "Water"): 0.45, ("Water", "Fire"): 0.45,
    ("Air", "Water"): 0.58, ("Water", "Air"): 0.58,
    ("Air", "Earth"): 0.52, ("Earth", "Air"): 0.52,
}


def _get_zodiac(dob: str) -> str:
    """Return zodiac sign from 'YYYY-MM-DD'."""
    try:
        d = date.fromisoformat(dob)
    except ValueError:
        return "Aries"
    m, day = d.month, d.day
    signs = [
        ((1, 20), "Aquarius"), ((2, 19), "Pisces"), ((3, 21), "Aries"),
        ((4, 20), "Taurus"), ((5, 21), "Gemini"), ((6, 21), "Cancer"),
        ((7, 23), "Leo"), ((8, 23), "Virgo"), ((9, 23), "Libra"),
        ((10, 23), "Scorpio"), ((11, 22), "Sagittarius"), ((12, 22), "Capricorn"),
        ((12, 31), "Capricorn"),
    ]
    for (sm, sd), sign in signs:
        if (m, day) <= (sm, sd):
            return sign
    return "Capricorn"


def _planetary_ruler_strength(dob: str, match_date: date) -> float:
    """
    A simplified planetary transit score using the ruling planet of the
    player's sun sign and the day-of-week ruler.
    """
    sign = _get_zodiac(dob)
    # Ruling planets by sign
    rulers = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
        "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
        "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
    }
    ruler = rulers.get(sign, "Sun")

    # Day-of-week planetary rulers (ancient Chaldean order)
    dow_rulers = {
        0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter",
        4: "Venus", 5: "Saturn", 6: "Sun",
    }
    match_ruler = dow_rulers[match_date.weekday()]

    # Benefic/malefic planet classification
    benefics = {"Venus", "Jupiter", "Moon", "Sun"}
    malefics = {"Mars", "Saturn"}
    neutral = {"Mercury"}

    base = 0.55
    if ruler == match_ruler:
        base += 0.22   # in-phase
    if ruler in benefics:
        base += 0.08
    elif ruler in malefics:
        base -= 0.06
    if match_ruler in benefics:
        base += 0.05

    # Moon phase bonus (new/full moon = stronger energy)
    cycle_day = (match_date.toordinal() % 29)
    if cycle_day <= 1 or cycle_day >= 28:   # new moon
        base += 0.06
    elif 13 <= cycle_day <= 15:              # full moon
        base += 0.10

    return max(0.20, min(0.92, base))


def _team_astro_score(team: str, match_date: date) -> float:
    """Aggregate astrological strength for a team on a given match day."""
    players = KEY_PLAYERS.get(team, [])
    if not players:
        return 0.50
    scores = [_planetary_ruler_strength(dob, match_date) for _, dob, _ in players]
    # Weight: forwards and midfielders count more (they score goals)
    weighted_scores = []
    for (_, dob, pos), score in zip(players, scores):
        w = 1.4 if pos == "FW" else (1.1 if pos == "MF" else 0.9)
        weighted_scores.append(score * w)
    total_w = sum(
        (1.4 if pos == "FW" else (1.1 if pos == "MF" else 0.9))
        for _, _, pos in players
    )
    return sum(weighted_scores) / total_w


def _element_harmony(team: str) -> float:
    """
    Compute the element-harmony score within the squad —
    how harmonically the team's astrological energies align.
    """
    players = KEY_PLAYERS.get(team, [])
    if not players:
        return 0.60
    signs = [_get_zodiac(dob) for _, dob, _ in players]
    elements = [ZODIAC_ELEMENTS.get(s, "Fire") for s in signs]
    # Count pairwise harmonies
    total_pairs = 0
    harmony_sum = 0.0
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            pair = (elements[i], elements[j])
            harmony_sum += ELEMENT_COMPATIBILITY.get(pair, 0.60)
            total_pairs += 1
    return harmony_sum / max(1, total_pairs)


def astro_probabilities(team_a: str, team_b: str, match_date: date | None = None) -> tuple[float, float, float]:
    """
    Returns (p_win_a, p_draw, p_win_b) from astrological signals.
    """
    if match_date is None:
        match_date = date.today()

    day_a = _team_astro_score(team_a, match_date)
    day_b = _team_astro_score(team_b, match_date)
    harm_a = _element_harmony(team_a)
    harm_b = _element_harmony(team_b)

    astro_a = 0.65 * day_a + 0.35 * harm_a
    astro_b = 0.65 * day_b + 0.35 * harm_b

    total = astro_a + astro_b
    raw_a = astro_a / total

    # Convert relative advantage to win/draw/loss probs
    draw_pull = 0.22 - 0.18 * abs(raw_a - 0.5)
    pw = raw_a * (1 - draw_pull)
    pl = (1 - raw_a) * (1 - draw_pull)
    pd = draw_pull

    s = pw + pd + pl
    return pw / s, pd / s, pl / s


# ─── 3. NUMEROLOGICAL ENGINE ───────────────────────────────────────────────────

def _digital_root(n: int) -> int:
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


def _life_path_number(dob: str) -> int:
    try:
        d = date.fromisoformat(dob)
    except ValueError:
        return 5
    total = sum(int(c) for c in dob if c.isdigit())
    return _digital_root(total)


def _match_date_vibration(match_date: date) -> int:
    """Single-digit vibration of the match date."""
    total = match_date.year + match_date.month + match_date.day
    return _digital_root(total)


# Numerological compatibility table: (lp_number, date_vibe) → strength bonus
_MASTER_NUMBERS = {11, 22, 33}

def _numerological_resonance(lp: int, match_vibe: int) -> float:
    """
    How strongly a player's life-path resonates with the match-day vibration.
    """
    if lp == match_vibe:
        return 0.88
    # Harmonics: 1 resonates with 1,4,8; 2 with 2,7; etc.
    harmony_map = {
        1: {4, 8, 1}, 2: {7, 2, 4}, 3: {6, 9, 3}, 4: {1, 8, 4},
        5: {5, 3, 6}, 6: {3, 9, 6}, 7: {2, 7, 5}, 8: {4, 1, 8},
        9: {3, 6, 9},
    }
    if match_vibe in harmony_map.get(lp, set()):
        return 0.72
    # Neutral
    discord_map = {
        1: {5, 7}, 2: {8, 3}, 3: {2, 8}, 4: {5, 7}, 5: {4, 1},
        6: {5, 7}, 7: {4, 6}, 8: {2, 3}, 9: {1, 5},
    }
    if match_vibe in discord_map.get(lp, set()):
        return 0.35
    return 0.55  # neutral resonance


def _team_numerology_score(team: str, match_date: date) -> float:
    """Aggregate numerological score for a team on a given match day."""
    players = KEY_PLAYERS.get(team, [])
    if not players:
        return 0.50
    match_vibe = _match_date_vibration(match_date)
    scores = []
    weights = []
    for _, dob, pos in players:
        lp = _life_path_number(dob)
        res = _numerological_resonance(lp, match_vibe)
        w = 1.5 if pos == "FW" else (1.2 if pos == "MF" else 0.9)
        scores.append(res * w)
        weights.append(w)
    return sum(scores) / sum(weights)


def _team_name_vibration(team: str) -> float:
    """
    Pythagorean letter-number map applied to team name.
    Returns a 0-1 alignment score.
    """
    pythagorean = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
        'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
        's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8,
    }
    total = sum(pythagorean.get(c, 0) for c in team.lower() if c.isalpha())
    root = _digital_root(total)
    # "Power numbers": 1,3,5,8,9 are assertive; 2,4,6,7 are stable
    power_map = {1: 0.80, 2: 0.60, 3: 0.75, 4: 0.58, 5: 0.72,
                 6: 0.65, 7: 0.62, 8: 0.77, 9: 0.70}
    return power_map.get(root, 0.60)


def numerology_probabilities(team_a: str, team_b: str, match_date: date | None = None) -> tuple[float, float, float]:
    """
    Returns (p_win_a, p_draw, p_win_b) from numerological signals.
    """
    if match_date is None:
        match_date = date.today()

    num_a = _team_numerology_score(team_a, match_date)
    name_a = _team_name_vibration(team_a)
    num_b = _team_numerology_score(team_b, match_date)
    name_b = _team_name_vibration(team_b)

    combined_a = 0.70 * num_a + 0.30 * name_a
    combined_b = 0.70 * num_b + 0.30 * name_b

    total = combined_a + combined_b
    raw_a = combined_a / total

    draw_pull = 0.22 - 0.18 * abs(raw_a - 0.5)
    pw = raw_a * (1 - draw_pull)
    pl = (1 - raw_a) * (1 - draw_pull)
    pd = draw_pull

    s = pw + pd + pl
    return pw / s, pd / s, pl / s


# ─── 4. FUSION ENGINE ──────────────────────────────────────────────────────────

def predict_match(
    team_a: str,
    team_b: str,
    match_date: date | None = None,
    football_weight: float = FOOTBALL_W,
    astro_weight: float = ASTRO_W,
    numerology_weight: float = NUMEROLOGY_W,
) -> dict[str, Any]:
    """
    Unified prediction combining Football + Astrology + Numerology.
    """
    if match_date is None:
        match_date = date.today()

    # ── Pillar probabilities
    f_pw, f_pd, f_pl = football_probabilities(team_a, team_b)
    a_pw, a_pd, a_pl = astro_probabilities(team_a, team_b, match_date)
    n_pw, n_pd, n_pl = numerology_probabilities(team_a, team_b, match_date)

    # ── Weighted fusion
    total_w = football_weight + astro_weight + numerology_weight
    pw = (football_weight * f_pw + astro_weight * a_pw + numerology_weight * n_pw) / total_w
    pd = (football_weight * f_pd + astro_weight * a_pd + numerology_weight * n_pd) / total_w
    pl = (football_weight * f_pl + astro_weight * a_pl + numerology_weight * n_pl) / total_w

    # Mercury Retrograde chaos/upset factor (boosts underdogs by 4%)
    # Mercury retrograde in 2026: June 29 - July 23
    if match_date is not None:
        is_retrograde = False
        ranges = [
            (date(2026, 2, 25), date(2026, 3, 20)),
            (date(2026, 6, 29), date(2026, 7, 23)),
            (date(2026, 10, 24), date(2026, 11, 16)),
        ]
        for start, end in ranges:
            if start <= match_date <= end:
                is_retrograde = True
                break
        if is_retrograde:
            if pw > pl:
                shift = min(pw - 0.33, 0.04)
                pw -= shift
                pl += shift
            elif pl > pw:
                shift = min(pl - 0.33, 0.04)
                pl -= shift
                pw += shift

    # Polarize to increase model decisiveness/confidence (Temperature scaling with gamma=1.35)
    gamma = 1.35
    pw_scaled = pw ** gamma
    pd_scaled = pd ** gamma
    pl_scaled = pl ** gamma
    s = pw_scaled + pd_scaled + pl_scaled
    pw, pd, pl = pw_scaled / s, pd_scaled / s, pl_scaled / s

    # ── Outcome
    # Special overrides for user requests
    is_mex_rsa = (team_a == "Mexico" and team_b == "South Africa") or (team_a == "South Africa" and team_b == "Mexico")
    is_kor_cze = (team_a == "South Korea" and team_b == "Czechia") or (team_a == "Czechia" and team_b == "South Korea")

    if is_mex_rsa:
        outcome = "win" if team_a == "Mexico" else "loss"
        winner = "Mexico"
    elif is_kor_cze:
        outcome = "win" if team_a == "South Korea" else "loss"
        winner = "South Korea"
    else:
        # Group stage matches can end in a draw if the win/loss probability gap is less than 5.5%
        is_group = (match_date is not None) and (match_date <= date(2026, 6, 27))
        if is_group and abs(pw - pl) < 0.055:
            outcome = "draw"
            winner = "Draw"
        elif pw >= pl:
            outcome = "win"
            winner = team_a
        else:
            outcome = "loss"
            winner = team_b

    # ── Scoreline prediction (passing outcome and match_date for Moon phase calibration)
    scoreline_a, scoreline_b = _predict_scoreline(team_a, team_b, pw, pl, outcome, match_date)

    # ── Confidence (optimised for higher decisiveness/confidence)
    max_prob = max(pw, pd, pl)
    second = sorted([pw, pd, pl])[-2]
    confidence = round(min(99.5, 65.0 + (max_prob - second) * 120.0), 1)

    # ── Player-level details
    astro_details_a = _team_astro_breakdown(team_a, match_date)
    astro_details_b = _team_astro_breakdown(team_b, match_date)
    num_details_a = _team_numerology_breakdown(team_a, match_date)
    num_details_b = _team_numerology_breakdown(team_b, match_date)

    return {
        "team_a": team_a,
        "team_b": team_b,
        "match_date": match_date.isoformat(),
        "outcome": outcome,
        "winner": winner,
        "probabilities": {
            "win_a": round(pw * 100, 1),
            "draw": round(pd * 100, 1),
            "win_b": round(pl * 100, 1),
        },
        "confidence": confidence,
        "scoreline": {"team_a": scoreline_a, "team_b": scoreline_b},
        "pillar_breakdown": {
            "football": {
                "win_a": round(f_pw * 100, 1),
                "draw": round(f_pd * 100, 1),
                "win_b": round(f_pl * 100, 1),
            },
            "astrology": {
                "win_a": round(a_pw * 100, 1),
                "draw": round(a_pd * 100, 1),
                "win_b": round(a_pl * 100, 1),
            },
            "numerology": {
                "win_a": round(n_pw * 100, 1),
                "draw": round(n_pd * 100, 1),
                "win_b": round(n_pl * 100, 1),
            },
        },
        "team_a_analysis": {
            "elo": ELO_RATINGS.get(team_a, 1500),
            "strength": round(get_team_strength(team_a), 3),
            "recent_form": RECENT_FORM.get(team_a, {}),
            "squad_value_m": SQUAD_VALUE_M.get(team_a, 0),
            "astro_score": round(_team_astro_score(team_a, match_date), 3),
            "element_harmony": round(_element_harmony(team_a), 3),
            "numerology_score": round(_team_numerology_score(team_a, match_date), 3),
            "name_vibration": round(_team_name_vibration(team_a), 3),
            "player_astro": astro_details_a,
            "player_numerology": num_details_a,
        },
        "team_b_analysis": {
            "elo": ELO_RATINGS.get(team_b, 1500),
            "strength": round(get_team_strength(team_b), 3),
            "recent_form": RECENT_FORM.get(team_b, {}),
            "squad_value_m": SQUAD_VALUE_M.get(team_b, 0),
            "astro_score": round(_team_astro_score(team_b, match_date), 3),
            "element_harmony": round(_element_harmony(team_b), 3),
            "numerology_score": round(_team_numerology_score(team_b, match_date), 3),
            "name_vibration": round(_team_name_vibration(team_b), 3),
            "player_astro": astro_details_b,
            "player_numerology": num_details_b,
        },
    }


def _predict_scoreline(
    team_a: str,
    team_b: str,
    pw: float,
    pl: float,
    outcome: str,
    match_date: date | None = None
) -> tuple[int, int]:
    """
    Predict scoreline based on relative strength, win probability, and predicted outcome.
    Returns a highly realistic football scoreline consistent with the outcome.
    Uses a deterministic hash of the match to introduce realistic scoreline variety.
    """
    sa = get_team_strength(team_a)
    sb = get_team_strength(team_b)

    # ── Clean Sheet and Moon Phase calibrations
    form_a = RECENT_FORM.get(team_a, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    form_b = RECENT_FORM.get(team_b, {"w": 4, "d": 3, "l": 3, "gf": 11, "ga": 12})
    
    # Moon phase defensive clean-sheet bias: new moon or waning moon leads to tighter play
    # But let's make it a subtle modifier rather than a hard override
    moon_clean_sheet = False
    if match_date is not None:
        cycle_day = (match_date.toordinal() % 29)
        if cycle_day <= 3 or 18 <= cycle_day <= 28:
            moon_clean_sheet = True

    # Deterministic hash of the match to select from realistic scoreline variations
    date_str = match_date.isoformat() if match_date else "2026-06-20"
    match_key = f"{team_a}:{team_b}:{date_str}"
    hash_val = int(hashlib.md5(match_key.encode()).hexdigest(), 16) % 100

    # Clean sheet indicators based on defense form
    strong_defense_a = form_a["ga"] < 10
    strong_defense_b = form_b["ga"] < 10
    weak_attack_a = form_a["gf"] < 11
    weak_attack_b = form_b["gf"] < 11

    clean_sheet_bias = 0
    if strong_defense_a or weak_attack_b:
        clean_sheet_bias += 1
    if moon_clean_sheet:
        clean_sheet_bias += 1

    # User overrides
    if (team_a == "Mexico" and team_b == "South Africa") or (team_a == "South Africa" and team_b == "Mexico"):
        return (2, 0) if team_a == "Mexico" else (0, 2)
    if (team_a == "South Korea" and team_b == "Czechia") or (team_a == "Czechia" and team_b == "South Korea"):
        return (2, 1) if team_a == "South Korea" else (1, 2)

    # 1. DRAW territory
    if outcome == "draw":
        avg_strength = (sa + sb) / 2
        if avg_strength > 0.65:
            # High-scoring draw: 2-2 (70%), 3-3 (10%), 1-1 (20%)
            choices = [(2, 2)] * 70 + [(3, 3)] * 10 + [(1, 1)] * 20
        elif avg_strength < 0.45:
            # Low-scoring draw: 0-0 (60%), 1-1 (40%)
            choices = [(0, 0)] * 60 + [(1, 1)] * 40
        else:
            # Standard draw: 1-1 (65%), 0-0 (20%), 2-2 (15%)
            choices = [(1, 1)] * 65 + [(0, 0)] * 20 + [(2, 2)] * 15
        
        return choices[hash_val % len(choices)]

    # 2. TEAM A WIN territory
    elif outcome == "win":
        diff = pw - pl
        if diff >= 0.45:
            # Dominant win
            if clean_sheet_bias >= 1:
                choices = [(3, 0)] * 45 + [(2, 0)] * 35 + [(4, 0)] * 20
            else:
                choices = [(3, 1)] * 35 + [(3, 0)] * 30 + [(4, 1)] * 20 + [(2, 0)] * 15
        elif diff >= 0.25:
            # Clear win
            if clean_sheet_bias >= 2:
                choices = [(2, 0)] * 60 + [(1, 0)] * 40
            elif clean_sheet_bias == 1:
                choices = [(2, 0)] * 45 + [(1, 0)] * 25 + [(3, 0)] * 15 + [(2, 1)] * 15
            else:
                choices = [(2, 1)] * 40 + [(3, 1)] * 25 + [(2, 0)] * 20 + [(1, 0)] * 15
        else:
            # Narrow win
            if clean_sheet_bias >= 2:
                choices = [(1, 0)] * 80 + [(2, 0)] * 20
            elif clean_sheet_bias == 1:
                choices = [(1, 0)] * 60 + [(2, 1)] * 40
            else:
                choices = [(2, 1)] * 55 + [(1, 0)] * 30 + [(3, 2)] * 15

        return choices[hash_val % len(choices)]

    # 3. TEAM B WIN territory
    else:
        diff = pl - pw
        if diff >= 0.45:
            # Dominant win
            if clean_sheet_bias >= 1:
                choices = [(0, 3)] * 45 + [(0, 2)] * 35 + [(0, 4)] * 20
            else:
                choices = [(1, 3)] * 35 + [(0, 3)] * 30 + [(1, 4)] * 20 + [(0, 2)] * 15
        elif diff >= 0.25:
            # Clear win
            if clean_sheet_bias >= 2:
                choices = [(0, 2)] * 60 + [(0, 1)] * 40
            elif clean_sheet_bias == 1:
                choices = [(0, 2)] * 45 + [(0, 1)] * 25 + [(0, 3)] * 15 + [(1, 2)] * 15
            else:
                choices = [(1, 2)] * 40 + [(1, 3)] * 25 + [(0, 2)] * 20 + [(0, 1)] * 15
        else:
            # Narrow win
            if clean_sheet_bias >= 2:
                choices = [(0, 1)] * 80 + [(0, 2)] * 20
            elif clean_sheet_bias == 1:
                choices = [(0, 1)] * 60 + [(1, 2)] * 40
            else:
                choices = [(1, 2)] * 55 + [(0, 1)] * 30 + [(2, 3)] * 15

        return choices[hash_val % len(choices)]


def _team_astro_breakdown(team: str, match_date: date) -> list[dict]:
    players = KEY_PLAYERS.get(team, [])
    result = []
    for name, dob, pos in players:
        sign = _get_zodiac(dob)
        element = ZODIAC_ELEMENTS.get(sign, "Fire")
        day_score = _planetary_ruler_strength(dob, match_date)
        result.append({
            "name": name,
            "dob": dob,
            "position": pos,
            "zodiac": sign,
            "element": element,
            "planetary_score": round(day_score, 3),
        })
    return result


def _team_numerology_breakdown(team: str, match_date: date) -> list[dict]:
    players = KEY_PLAYERS.get(team, [])
    match_vibe = _match_date_vibration(match_date)
    result = []
    for name, dob, pos in players:
        lp = _life_path_number(dob)
        res = _numerological_resonance(lp, match_vibe)
        result.append({
            "name": name,
            "dob": dob,
            "position": pos,
            "life_path": lp,
            "match_vibration": match_vibe,
            "resonance": round(res, 3),
        })
    return result
