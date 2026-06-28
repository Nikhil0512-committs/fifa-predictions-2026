"""
FIFA 2026 Prediction System – Ultra-Premium Streamlit Dashboard (Equal Weightage Mode)
"""

import streamlit as st
import sqlite3
from datetime import date, datetime
import os

# ── Page config MUST be first ────────────────────────────────────────────────
st.set_page_config(
    page_title="FIFA 2026 AI Oracle — Predictions Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fifa_predictor.models.predict import (
    predict_match,
    _team_astro_score,
    _element_harmony,
    _team_numerology_score,
    _team_name_vibration,
    _get_zodiac,
    _team_astro_breakdown,
    _team_numerology_breakdown,
    ZODIAC_ELEMENTS,
    _get_combined_form,
)
from fifa_predictor.knowledge import (
    FIFA_RANKINGS, ELO_RATINGS, RECENT_FORM,
    SQUAD_VALUE_M, get_team_strength, KEY_PLAYERS,
)

# ─── Name mapping dictionary ──────────────────────────────────────────────────
NAME_MAPPING = {
    # Spelling corrections
    "Cabo Verde": "Cape Verde",
    "Curaao": "Curaçao",
    "Cte d'Ivoire": "Ivory Coast",
    "IR Iran": "Iran",
    "Türkiye": "Turkey",
    "USA": "United States",
    # Placeholder mappings
    "Winner UEFA Playoff A": "Bosnia and Herzegovina",
    "Winner UEFA Playoff B": "Sweden",
    "Winner UEFA Playoff C": "Turkey",
    "Winner UEFA Playoff D": "Czechia",
    "Winner FIFA Playoff 1": "DR Congo",
    "Winner FIFA Playoff 2": "Iraq",
}

def clean_team_name(name):
    return NAME_MAPPING.get(name, name)

# ─── Load predictions from SQLite database ───────────────────────────────────
def load_predictions_from_db():
    db_path = "./data/processed/fifa2026_predictions.db"
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT match_number, stage, group_or_label, kickoff_at, venue, city, home_team, away_team,
               predicted_winner, predicted_score, home_win_probability, draw_probability, away_win_probability,
               confidence, home_football_strength, away_football_strength, home_astrology_score, away_astrology_score,
               home_numerology_score, away_numerology_score, predicted_qualifier
        FROM fixture_predictions
        ORDER BY kickoff_at, match_number;
    """)
    rows = cursor.fetchall()
    conn.close()
    
    preds = []
    for r in rows:
        match_num, stage, group, kickoff_at, venue, city, home, away, winner, score, p_win_a, p_draw, p_win_b, conf, str_a, str_b, ast_a, ast_b, num_a, num_b, qualifier = r
        
        home_clean = clean_team_name(home)
        away_clean = clean_team_name(away)
        winner_clean = clean_team_name(winner)
        qualifier_clean = clean_team_name(qualifier) if qualifier else None
        
        # Parse score
        try:
            score_parts = score.split("-")
            score_a = int(score_parts[0])
            score_b = int(score_parts[1])
        except Exception:
            score_a = 0
            score_b = 0
        
        # Parse kickoff date
        date_str = kickoff_at.split()[0]
        
        preds.append({
            "match_number": match_num,
            "stage": stage,
            "group": group,
            "date": date_str,
            "kickoff_at": kickoff_at,
            "venue": f"{venue}, {city}" if city else venue,
            "team_a": home_clean,
            "team_b": away_clean,
            "raw_team_a": home,
            "raw_team_b": away,
            "winner": winner_clean,
            "predicted_qualifier": qualifier_clean,
            "scoreline": {"team_a": score_a, "team_b": score_b},
            "probabilities": {
                "win_a": p_win_a,
                "draw": p_draw,
                "win_b": p_win_b,
            },
            "confidence": conf,
            "team_a_analysis": {
                "elo": ELO_RATINGS.get(home_clean, 1500),
                "strength": str_a,
                "recent_form": _get_combined_form(home_clean),
                "squad_value_m": SQUAD_VALUE_M.get(home_clean, 0),
                "astro_score": ast_a,
                "element_harmony": _element_harmony(home_clean) if home_clean in KEY_PLAYERS else 0.5,
                "numerology_score": num_a,
                "name_vibration": _team_name_vibration(home_clean) if home_clean in KEY_PLAYERS else 0.5,
            },
            "team_b_analysis": {
                "elo": ELO_RATINGS.get(away_clean, 1500),
                "strength": str_b,
                "recent_form": _get_combined_form(away_clean),
                "squad_value_m": SQUAD_VALUE_M.get(away_clean, 0),
                "astro_score": ast_b,
                "element_harmony": _element_harmony(away_clean) if away_clean in KEY_PLAYERS else 0.5,
                "numerology_score": num_b,
                "name_vibration": _team_name_vibration(away_clean) if away_clean in KEY_PLAYERS else 0.5,
            }
        })
    return preds

all_preds = load_predictions_from_db()

# Initialize session state for selected match index
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Outfit', sans-serif !important; }

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.01);
}
::-webkit-scrollbar-thumb {
    background: rgba(0,212,255,0.2);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0,212,255,0.4);
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #030712 0%, #081125 40%, #0d1e3a 75%, #050b18 100%);
    min-height: 100vh;
}

/* Hero Header styling */
.hero-header {
    text-align: center;
    padding: 1.8rem 1rem 1rem;
    background: linear-gradient(180deg, rgba(13,30,58,0.3) 0%, rgba(3,7,18,0) 100%);
    border-bottom: 1px solid rgba(0,212,255,0.08);
    margin-bottom: 1.5rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00d4ff, #a855f7, #00ff94);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.hero-subtitle {
    color: rgba(180,210,255,0.7);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.weight-badge-container {
    margin-top: 0.8rem;
}
.weight-badge {
    display: inline-block;
    background: rgba(168,85,247,0.12);
    border: 1px solid rgba(168,85,247,0.3);
    color: #c084fc;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    letter-spacing: 0.05em;
}

/* Match Schedule Feed (Left Pane) */
.schedule-container {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 0.5rem;
}
.date-header {
    font-size: 0.95rem;
    font-weight: 700;
    color: #a855f7;
    margin: 1.2rem 0 0.6rem;
    padding-bottom: 0.2rem;
    border-bottom: 1px solid rgba(168,85,247,0.2);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Match Cards */
.match-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(0,212,255,0.12);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: all 0.25s ease;
    cursor: pointer;
    position: relative;
}
.match-card:hover {
    border-color: rgba(0,212,255,0.35);
    background: rgba(255,255,255,0.04);
    box-shadow: 0 4px 15px rgba(0,212,255,0.08);
}
.match-card-selected {
    background: rgba(168,85,247,0.07) !important;
    border: 1px solid rgba(168,85,247,0.5) !important;
    box-shadow: 0 4px 20px rgba(168,85,247,0.15) !important;
}
.match-card-selected::after {
    content: 'SELECTED';
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 0.65rem;
    font-weight: 800;
    background: #a855f7;
    color: white;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
}
.match-card-meta {
    font-size: 0.75rem;
    color: rgba(180,210,255,0.5);
    margin-bottom: 0.4rem;
}
.match-card-teams {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.5rem;
}
.match-card-score {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00ff94;
}
.match-card-result {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.85);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.4rem;
    padding-top: 0.4rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.outcome-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.45rem;
    border-radius: 4px;
}
.outcome-win { background: rgba(0,255,148,0.15); color: #00ff94; border: 1px solid rgba(0,255,148,0.25); }
.outcome-draw { background: rgba(255,200,0,0.12); color: #ffc800; border: 1px solid rgba(255,200,0,0.25); }

/* Right Panel Sticky Column Wrapper */
div[data-testid="column"]:has(.detail-container) {
    position: -webkit-sticky;
    position: sticky;
    top: 1.5rem;
    align-self: start;
}

/* Right Panel View */
.detail-container {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 75vh;
    backdrop-filter: blur(20px);
}
.main-winner-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.05), rgba(168,85,247,0.08), rgba(0,255,148,0.04));
    border: 1px solid rgba(168,85,247,0.25);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.main-winner-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #00ff94);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}
.main-scoreline {
    font-size: 3.2rem;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace !important;
    color: #ffffff;
    letter-spacing: -1px;
}

/* Pillar Progress bars */
.prob-bar-container { margin: 0.75rem 0; }
.prob-bar-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
    font-size: 0.85rem;
    color: rgba(180,210,255,0.7);
}
.prob-bar-track {
    height: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 5px;
    overflow: hidden;
}
.prob-bar-fill {
    height: 100%;
    border-radius: 5px;
    transition: width 0.5s ease;
}

/* Squad details table */
.player-row {
    display: flex;
    align-items: center;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.3rem;
    font-size: 0.85rem;
    background: rgba(255,255,255,0.015);
    border: 1px solid rgba(255,255,255,0.03);
}
.player-pos {
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    margin-right: 0.6rem;
    min-width: 2.2rem;
    text-align: center;
}
.pos-fw { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.pos-mf { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }
.pos-df { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.pos-gk { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }

.stat-badge {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.8);
    border: 1px solid rgba(255,255,255,0.08);
}
.elem-fire { background: rgba(239,68,68,0.1); color:#f87171; border-color:rgba(239,68,68,0.2); }
.elem-water { background: rgba(59,130,246,0.1); color:#60a5fa; border-color:rgba(59,130,246,0.2); }
.elem-earth { background: rgba(16,185,129,0.1); color:#34d399; border-color:rgba(16,185,129,0.2); }
.elem-air  { background: rgba(139,92,246,0.1); color:#a78bfa; border-color:rgba(139,92,246,0.2); }

/* Quick info badges */
.info-badge-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.5rem;
}

/* Tab labels */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.02);
    border-radius: 6px 6px 0 0;
    color: rgba(180,210,255,0.6);
    font-weight: 600;
    padding: 0.5rem 1rem;
    border: 1px solid rgba(255,255,255,0.04);
}
.stTabs [aria-selected="true"] {
    background: rgba(168,85,247,0.12) !important;
    color: #c084fc !important;
    border-color: rgba(168,85,247,0.3) !important;
}

/* Filter Search Input */
.stTextInput > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Helper functions ─────────────────────────────────────────────────────────

def color_gradient(value: float, low: str = "#f87171", high: str = "#34d399") -> str:
    """Interpolate hex color based on 0-1 value."""
    r1, g1, b1 = int(low[1:3], 16), int(low[3:5], 16), int(low[5:7], 16)
    r2, g2, b2 = int(high[1:3], 16), int(high[3:5], 16), int(high[5:7], 16)
    r = int(r1 + (r2 - r1) * value)
    g = int(g1 + (g2 - g1) * value)
    b = int(b1 + (b2 - b1) * value)
    return f"#{r:02x}{g:02x}{b:02x}"

def prob_bar(label: str, pct: float, color: str = "#00d4ff"):
    st.markdown(f"""
    <div class="prob-bar-container">
        <div class="prob-bar-label">
            <span>{label}</span>
            <span style="font-weight:700; color:white;">{pct:.1f}%</span>
        </div>
        <div class="prob-bar-track">
            <div class="prob-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def pos_class(pos: str) -> str:
    return {"FW": "pos-fw", "MF": "pos-mf", "DF": "pos-df", "GK": "pos-gk"}.get(pos, "pos-mf")

def element_class(elem: str) -> str:
    return {"Fire": "elem-fire", "Water": "elem-water", "Earth": "elem-earth", "Air": "elem-air"}.get(elem, "")

# ─── Hero Header ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">🔮 FIFA 2026 AI ORACLE</div>
    <div class="hero-subtitle">Official Fixtures & Cosmic Forecasts (Knockout Stage)</div>
    <div class="weight-badge-container">
        <span class="weight-badge">⚖️ EQUAL WEIGHTAGE MODE (33.3% Football · 33.3% Astrology · 33.3% Numerology)</span>
        <span class="weight-badge" style="background:rgba(52,211,153,0.12); border-color:rgba(52,211,153,0.3); color:#34d399;">⚡ HIGH-DECISIVENESS TEMPERATURE SCALING ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── SPLIT LAYOUT ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([5, 8])

# ─── LEFT COLUMN: Matches Feed ───────────────────────────────────────────────
with col_left:
    st.markdown("<h3 style='margin:0 0 0.5rem; font-size:1.3rem; font-weight:700;'>📅 Match Fixtures</h3>", unsafe_allow_html=True)
    
    # Simple Search Filter
    filter_query = st.text_input("🔍 Search matches by team name:", placeholder="e.g. Argentina, Portugal, Colombia, DR Congo...", key="team_filter")
    
    # Filter matches
    filtered_indices = []
    for idx, f in enumerate(all_preds):
        if not filter_query or filter_query.lower() in f["team_a"].lower() or filter_query.lower() in f["team_b"].lower() or filter_query.lower() in f["raw_team_a"].lower() or filter_query.lower() in f["raw_team_b"].lower():
            filtered_indices.append(idx)
            
    # Keep selected index valid
    if filtered_indices and st.session_state.selected_idx not in filtered_indices:
        st.session_state.selected_idx = filtered_indices[0]
        
    st.markdown('<div class="schedule-container">', unsafe_allow_html=True)
    
    if not filtered_indices:
        st.info("No matches found in the prediction model database for this team name.")
    else:
        current_date = ""
        for idx in filtered_indices:
            f = all_preds[idx]
            
            # Group by date header
            date_str = datetime.strptime(f["date"], "%Y-%m-%d").strftime("%A, %B %d, %Y")
            if date_str != current_date:
                current_date = date_str
                st.markdown(f"<div class='date-header'>📅 {current_date}</div>", unsafe_allow_html=True)
            
            is_selected = (idx == st.session_state.selected_idx)
            card_class = "match-card match-card-selected" if is_selected else "match-card"
            
            outcome_label = "Draw"
            outcome_badge_class = "outcome-badge outcome-draw"
            if f["winner"] == f["team_a"]:
                outcome_label = f"{f['team_a']} Win"
                outcome_badge_class = "outcome-badge outcome-win"
            elif f["winner"] == f["team_b"]:
                outcome_label = f"{f['team_b']} Win"
                outcome_badge_class = "outcome-badge outcome-win"
                
            qualifier_html = ""
            if f.get("predicted_qualifier"):
                qualifier_html = f"""<div style="font-size:0.8rem; color:#34d399; margin-top:0.3rem; font-weight:600; display:flex; align-items:center; gap:4px;">🔮 <span style="text-transform:uppercase; font-size:0.7rem; color:rgba(255,255,255,0.4); font-weight:normal;">To Qualify:</span> {f['predicted_qualifier']}</div>"""

            # Draw the custom card
            st.markdown(f"""
            <div class="{card_class}">
                <div class="match-card-meta">{f['stage']} &nbsp;·&nbsp; {f['venue']}</div>
                <div class="match-card-teams">
                    <span>{f['team_a']}</span>
                    <span class="match-card-score">{f['scoreline']['team_a']} - {f['scoreline']['team_b']}</span>
                    <span>{f['team_b']}</span>
                </div>
                <div class="match-card-result">
                    <span>Forecast: <span class="{outcome_badge_class}">{outcome_label}</span></span>
                    <span style="font-family:'JetBrains Mono'; font-weight:600; color:rgba(255,255,255,0.7);">{f['confidence']}% conf</span>
                </div>
                {qualifier_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Clickable overlay button to select
            if st.button(f"Analyze: {f['team_a']} vs {f['team_b']}", key=f"btn_{idx}", use_container_width=True):
                st.session_state.selected_idx = idx
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

# ─── RIGHT COLUMN: Detailed Breakdown ────────────────────────────────────────
with col_right:
    # Get active selection
    if filtered_indices:
        sel_idx = st.session_state.selected_idx
        R = all_preds[sel_idx]
        
        ta = R["team_a"]
        tb = R["team_b"]
        probs = R["probabilities"]
        score = R["scoreline"]
        conf = R["confidence"]
        winner = R["winner"]
        ana_a = R["team_a_analysis"]
        ana_b = R["team_b_analysis"]
        
        # Calculate dynamic pillar win/draw/loss for detailed tab (unpolarized for absolute breakdown)
        # Using equal weights
        f_pw, f_pd, f_pl = predict_match(ta, tb, date.fromisoformat(R["date"]), 1.0, 0.0, 0.0)["probabilities"].values()
        a_pw, a_pd, a_pl = predict_match(ta, tb, date.fromisoformat(R["date"]), 0.0, 1.0, 0.0)["probabilities"].values()
        n_pw, n_pd, n_pl = predict_match(ta, tb, date.fromisoformat(R["date"]), 0.0, 0.0, 1.0)["probabilities"].values()
        
        winner_text = winner
        winner_label = "🏆 Predicted Winner" if winner != "Draw" else "🤝 Predicted Outcome"
        winner_emoji = "🏆" if winner != "Draw" else "🤝"
        conf_color = color_gradient(conf / 100)
        
        st.markdown(f"<h3 style='margin:0 0 1rem; font-size:1.3rem; font-weight:700;'>🔍 Match Breakdown: {ta} vs {tb}</h3>", unsafe_allow_html=True)
        
        # Outer Detail Container
        st.markdown('<div class="detail-container">', unsafe_allow_html=True)
        
        qualifier_detail = ""
        if R.get("predicted_qualifier"):
            qualifier_detail = f"""
            <div style="margin-top:0.6rem; font-size:0.95rem; font-weight:700; color:#34d399; border-top:1px solid rgba(52,211,153,0.18); padding-top:0.5rem; display:flex; align-items:center; justify-content:center; gap:6px;">
                🔮 <span style="text-transform:uppercase; font-size:0.75rem; color:rgba(255,255,255,0.4); font-weight:normal;">Predicted to Qualify:</span> {R['predicted_qualifier']}
            </div>
            """

        # Outcome Card
        st.markdown(f"""
        <div class="main-winner-card">
            <div style="font-size:0.85rem; color:rgba(180,210,255,0.6); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.3rem;">{winner_label}</div>
            <div class="main-winner-title">{winner_emoji} {winner_text}</div>
            <div class="main-scoreline">{score['team_a']} — {score['team_b']}</div>
            {qualifier_detail}
            <div style="font-size:0.8rem; color:rgba(180,210,255,0.45); margin-top:0.4rem;">{R['venue']} &nbsp;·&nbsp; {R['group']}</div>
            <div style="margin-top:0.8rem; font-size:0.85rem; color:white;">
                Composite Oracle Confidence: <span style="font-weight:700; color:{conf_color}; font-family:'JetBrains Mono'; font-size:1.1rem;">{conf:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Forecast",
            "⚽ Football",
            "🔮 Astrology",
            "🔢 Numerology",
            "👥 Squads"
        ])
        
        # TAB 1: Forecast Overview
        with tab1:
            col_pa, col_pb = st.columns(2)
            with col_pa:
                st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>Unified Outcome Probs</h4>", unsafe_allow_html=True)
                prob_bar(f"🔵 {ta} Win", probs["win_a"], "#00d4ff")
                prob_bar("🟡 Draw", probs["draw"], "#ffc800")
                prob_bar(f"🔴 {tb} Win", probs["win_b"], "#ff6060")
            
            with col_pb:
                st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>Comparative Metrics</h4>", unsafe_allow_html=True)
                metrics = [
                    ("FIFA Rank", f"#{FIFA_RANKINGS.get(ta, (0,0))[0]}" if ta in FIFA_RANKINGS else "N/A", f"#{FIFA_RANKINGS.get(tb, (0,0))[0]}" if tb in FIFA_RANKINGS else "N/A"),
                    ("Elo Rating", ana_a["elo"] if ta in ELO_RATINGS else "N/A", ana_b["elo"] if tb in ELO_RATINGS else "N/A"),
                    ("Astro Strength", f"{round(ana_a['astro_score']*100, 1)}%" if ta in KEY_PLAYERS else "N/A", f"{round(ana_b['astro_score']*100, 1)}%" if tb in KEY_PLAYERS else "N/A"),
                    ("Name Vibration", f"{round(ana_a['name_vibration']*100, 1)}%" if ta in KEY_PLAYERS else "N/A", f"{round(ana_b['name_vibration']*100, 1)}%" if tb in KEY_PLAYERS else "N/A"),
                ]
                for label, val_a, val_b in metrics:
                    col_m_l, col_m_c, col_m_r = st.columns([2, 3, 2])
                    with col_m_l:
                        st.markdown(f"<div style='text-align:right; font-weight:700; font-size:0.85rem; color:#00d4ff;'>{val_a}</div>", unsafe_allow_html=True)
                    with col_m_c:
                        st.markdown(f"<div style='text-align:center; font-size:0.75rem; color:rgba(180,210,255,0.65); text-transform:uppercase; letter-spacing:0.05em;'>{label}</div>", unsafe_allow_html=True)
                    with col_m_r:
                        st.markdown(f"<div style='text-align:left; font-weight:700; font-size:0.85rem; color:#ff6060;'>{val_b}</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:1.2rem 0; opacity:0.1;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='font-size:1rem; margin-bottom:0.8rem;'>Equal-Weight Pillars Comparison</h4>", unsafe_allow_html=True)
            
            cols_pillars = st.columns(3)
            with cols_pillars[0]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.015); border:1px solid rgba(255,255,255,0.05); padding:0.8rem; border-radius:10px; text-align:center;">
                    <div style="color:#00d4ff; font-size:0.8rem; font-weight:700; text-transform:uppercase; margin-bottom:0.5rem;">⚽ Football</div>
                    <div style="font-size:0.75rem; color:rgba(180,210,255,0.65); line-height:1.5; text-align:left;">
                        {ta} Win: <b>{f_pw:.1f}%</b><br>
                        Draw: <b>{f_pd:.1f}%</b><br>
                        {tb} Win: <b>{f_pl:.1f}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cols_pillars[1]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.015); border:1px solid rgba(255,255,255,0.05); padding:0.8rem; border-radius:10px; text-align:center;">
                    <div style="color:#a855f7; font-size:0.8rem; font-weight:700; text-transform:uppercase; margin-bottom:0.5rem;">🔮 Astrology</div>
                    <div style="font-size:0.75rem; color:rgba(180,210,255,0.65); line-height:1.5; text-align:left;">
                        {ta} Win: <b>{a_pw:.1f}%</b><br>
                        Draw: <b>{a_pd:.1f}%</b><br>
                        {tb} Win: <b>{a_pl:.1f}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with cols_pillars[2]:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.015); border:1px solid rgba(255,255,255,0.05); padding:0.8rem; border-radius:10px; text-align:center;">
                    <div style="color:#00ff94; font-size:0.8rem; font-weight:700; text-transform:uppercase; margin-bottom:0.5rem;">🔢 Numerology</div>
                    <div style="font-size:0.75rem; color:rgba(180,210,255,0.65); line-height:1.5; text-align:left;">
                        {ta} Win: <b>{n_pw:.1f}%</b><br>
                        Draw: <b>{n_pd:.1f}%</b><br>
                        {tb} Win: <b>{n_pl:.1f}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        # TAB 2: Football details
        with tab2:
            st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>⚽ Football Analytics</h4>", unsafe_allow_html=True)
            if ta not in KEY_PLAYERS or tb not in KEY_PLAYERS:
                st.info("Tactical data not available for knockout placeholders.")
            else:
                col_fa, col_fb = st.columns(2)
                for col, team, ana in [(col_fa, ta, ana_a), (col_fb, tb, ana_b)]:
                    with col:
                        st.markdown(f"<div style='font-weight:700; color:white; font-size:0.95rem; margin-bottom:0.5rem;'>{team} Strength Details</div>", unsafe_allow_html=True)
                        mv = ana["squad_value_m"]
                        form = ana["recent_form"]
                        st.markdown(f"""
                        <div class="info-badge-grid">
                            <span class="stat-badge">Elo: {ana['elo']}</span>
                            <span class="stat-badge">Squad value: €{mv}M</span>
                            <span class="stat-badge">Weight score: {round(ana['strength']*100, 1)}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if form:
                            st.markdown(f"<div style='font-size:0.8rem; margin-top:0.8rem;'>Form (last 10 matches): <b>W{form['w']} D{form['d']} L{form['l']}</b></div>", unsafe_allow_html=True)
                            prob_bar("Win Probability (Football)", form.get("w", 0) / 10 * 100, "#00ff94")
                            st.markdown(f"<div style='font-size:0.75rem; color:rgba(180,210,255,0.5);'>GF: {form['gf']} &nbsp;·&nbsp; GA: {form['ga']}</div>", unsafe_allow_html=True)

        # TAB 3: Astrology details
        with tab3:
            st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>🔮 Celestial Alignments</h4>", unsafe_allow_html=True)
            if ta not in KEY_PLAYERS or tb not in KEY_PLAYERS:
                st.info("Astrological data not available for knockout placeholders.")
            else:
                col_aa, col_ab = st.columns(2)
                md = date.fromisoformat(R["date"])
                for col, team, ana in [(col_aa, ta, ana_a), (col_ab, tb, ana_b)]:
                    with col:
                        st.markdown(f"<div style='font-weight:700; color:white; font-size:0.95rem; margin-bottom:0.5rem;'>{team} Cosmic Energy</div>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="info-badge-grid" style="margin-bottom:0.8rem;">
                            <span class="stat-badge">Day energy: {round(ana['astro_score']*100, 1)}%</span>
                            <span class="stat-badge">Element harmony: {round(ana['element_harmony']*100, 1)}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        players_astro = _team_astro_breakdown(team, md)
                        if players_astro:
                            for p in players_astro[:4]: # Show top 4 key players
                                elem = p["element"]
                                ec = element_class(elem)
                                score_color = color_gradient(p["planetary_score"])
                                st.markdown(f"""
                                <div class="player-row">
                                    <span class="player-pos {pos_class(p['position'])}">{p['position']}</span>
                                    <span style="flex:1; color:rgba(255,255,255,0.85); font-size:0.8rem;">{p['name']}</span>
                                    <span class="stat-badge {ec}" style="margin-right:0.3rem; font-size:0.7rem;">{p['zodiac']}</span>
                                    <span style="font-family:'JetBrains Mono'; color:{score_color}; font-weight:700; font-size:0.8rem;">{p['planetary_score']:.2f}</span>
                                </div>
                                """, unsafe_allow_html=True)

        # TAB 4: Numerology details
        with tab4:
            st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>🔢 Numerology & Vibrations</h4>", unsafe_allow_html=True)
            if ta not in KEY_PLAYERS or tb not in KEY_PLAYERS:
                st.info("Numerological data not available for knockout placeholders.")
            else:
                md = date.fromisoformat(R["date"])
                from fifa_predictor.models.predict import _match_date_vibration
                match_vibe = _match_date_vibration(md)
                st.markdown(f"<div style='font-size:0.85rem; color:#a855f7; margin-bottom:0.8rem; font-weight:600;'>📅 Match Date Vibration Root: {match_vibe}</div>", unsafe_allow_html=True)
                
                col_na, col_nb = st.columns(2)
                for col, team, ana in [(col_na, ta, ana_a), (col_nb, tb, ana_b)]:
                    with col:
                        st.markdown(f"<div style='font-weight:700; color:white; font-size:0.95rem; margin-bottom:0.5rem;'>{team} Numerology Resonance</div>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="info-badge-grid" style="margin-bottom:0.8rem;">
                            <span class="stat-badge">Squad resonance: {round(ana['numerology_score']*100, 1)}%</span>
                            <span class="stat-badge">Name vibration: {round(ana['name_vibration']*100, 1)}%</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        players_num = _team_numerology_breakdown(team, md)
                        if players_num:
                            for p in players_num[:4]: # Show top 4 key players
                                res_color = color_gradient(p["resonance"])
                                res_label = "In-Phase" if p["resonance"] >= 0.80 else (
                                    "Harmonic" if p["resonance"] >= 0.65 else (
                                    "Neutral" if p["resonance"] >= 0.50 else "Discord"))
                                st.markdown(f"""
                                <div class="player-row">
                                    <span class="player-pos {pos_class(p['position'])}">{p['position']}</span>
                                    <span style="flex:1; color:rgba(255,255,255,0.85); font-size:0.8rem;">{p['name']}</span>
                                    <span class="stat-badge" style="margin-right:0.3rem; font-size:0.7rem;">LP {p['life_path']}</span>
                                    <span style="font-size:0.75rem; color:rgba(180,210,255,0.5); margin-right:0.4rem;">{res_label}</span>
                                    <span style="font-family:'JetBrains Mono'; color:{res_color}; font-weight:700; font-size:0.8rem;">{p['resonance']:.2f}</span>
                                </div>
                                """, unsafe_allow_html=True)

        # TAB 5: Full squad details
        with tab5:
            st.markdown("<h4 style='font-size:1rem; margin-top:0.5rem;'>👥 Full Roster Details</h4>", unsafe_allow_html=True)
            if ta not in KEY_PLAYERS or tb not in KEY_PLAYERS:
                st.info("Squad rosters not available for knockout placeholders.")
            else:
                col_sa, col_sb = st.columns(2)
                for col, team in [(col_sa, ta), (col_sb, tb)]:
                    with col:
                        st.markdown(f"<div style='font-weight:700; color:white; font-size:0.95rem; margin-bottom:0.5rem;'>{team} Key Squad</div>", unsafe_allow_html=True)
                        players = KEY_PLAYERS.get(team, [])
                        if players:
                            for name, dob, pos in players:
                                sign = _get_zodiac(dob)
                                elem = ZODIAC_ELEMENTS.get(sign, "Fire")
                                ec = element_class(elem)
                                from fifa_predictor.models.predict import _life_path_number
                                lp = _life_path_number(dob)
                                st.markdown(f"""
                                <div class="player-row" style="background:rgba(255,255,255,0.01); border-color:rgba(255,255,255,0.03);">
                                    <span class="player-pos {pos_class(pos)}">{pos}</span>
                                    <div style="flex:1;">
                                        <div style="color:white; font-weight:600; font-size:0.8rem;">{name}</div>
                                        <div style="color:rgba(180,210,255,0.45); font-size:0.7rem;">Born: {dob}</div>
                                    </div>
                                    <span class="stat-badge {ec}" style="margin-right:0.25rem; font-size:0.7rem;">{sign}</span>
                                    <span class="stat-badge" style="background:rgba(245,158,11,0.08); color:#fbbf24; border-color:rgba(245,158,11,0.18); font-size:0.7rem;">LP{lp}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No squad data available.")
                            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No search results to display.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding:1.5rem; border-top:1px solid rgba(255,255,255,0.06);">
    <div style="font-size:0.75rem; color:rgba(180,210,255,0.3); letter-spacing:0.1em; text-transform:uppercase;">
        FIFA 2026 AI Oracle &nbsp;·&nbsp; Powered by Football Statistics, Celestial Alignment, and Pythagorean Numerology
    </div>
</div>
""", unsafe_allow_html=True)
