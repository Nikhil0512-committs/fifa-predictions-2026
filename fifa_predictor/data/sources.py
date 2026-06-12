from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import requests
from bs4 import BeautifulSoup
import pandas as pd

@dataclass(frozen=True)
class PublicSource:
    name: str
    url: str
    output: str
    notes: str

PUBLIC_SOURCES: tuple[PublicSource, ...] = (
    PublicSource("Football-Data fixtures/results", "https://www.football-data.co.uk/", "football_data", "CSV results history"),
    PublicSource("Club Elo", "http://api.clubelo.com/", "club_elo", "Elo-style team ratings"),
    PublicSource("FBref standard stats", "https://fbref.com/", "fbref", "Player/team performance tables"),
    PublicSource("Kaggle football datasets", "https://www.kaggle.com/datasets", "kaggle", "Historical World Cup and player data"),
)

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def parse_dob(text: str) -> str:
    text = text.strip()
    m1 = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m1:
        return f"{m1.group(1)}-{m1.group(2)}-{m1.group(3)}"
    m2 = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
    if m2:
        day = int(m2.group(1))
        month_str = m2.group(2).lower()
        year = int(m2.group(3))
        month = MONTHS.get(month_str, 1)
        return f"{year:04d}-{month:02d}-{day:02d}"
    m3 = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
    if m3:
        month_str = m3.group(1).lower()
        day = int(m3.group(2))
        year = int(m3.group(3))
        month = MONTHS.get(month_str, 1)
        return f"{year:04d}-{month:02d}-{day:02d}"
    return "1996-01-01"

def clean_player_name(name: str) -> str:
    name = re.sub(r"\s*\(captain\)\s*", "", name, flags=re.I)
    name = re.sub(r"\s*\(c\)\s*", "", name, flags=re.I)
    name = re.sub(r"\s*\(vice-captain\)\s*", "", name, flags=re.I)
    name = re.sub(r"\s*\(vc\)\s*", "", name, flags=re.I)
    return name.strip()

def clean_int(text: str) -> int:
    m = re.search(r"\d+", text)
    return int(m.group(0)) if m else 0

def scrape_wikipedia_squads() -> list[dict]:
    url = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    players = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch Wikipedia squads: Status {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        headings = soup.find_all("h3")
        
        for h in headings:
            team_name = h.text.strip().replace("[edit]", "").strip()
            
            table = None
            curr = h.parent if h.parent.name == "div" else h
            while curr:
                curr = curr.next_sibling
                if not curr:
                    break
                if curr.name in ["h2", "h3"] or (curr.name == "div" and curr.find(["h2", "h3"])):
                    break
                if curr.name == "table" and "wikitable" in curr.get("class", []):
                    table = curr
                    break
                if curr.name and curr.find:
                    t = curr.find("table", class_="wikitable")
                    if t:
                        table = t
                        break
            
            if not table:
                continue
                
            headers = [th.text.strip().lower() for th in table.find_all("th")]
            
            player_idx = -1
            pos_idx = -1
            dob_idx = -1
            caps_idx = -1
            goals_idx = -1
            club_idx = -1
            
            for idx, col_name in enumerate(headers):
                if "player" in col_name or "name" in col_name:
                    player_idx = idx
                elif "pos" in col_name:
                    pos_idx = idx
                elif "birth" in col_name or "dob" in col_name:
                    dob_idx = idx
                elif "caps" in col_name:
                    caps_idx = idx
                elif "goals" in col_name:
                    goals_idx = idx
                elif "club" in col_name:
                    club_idx = idx
            
            if player_idx == -1 or pos_idx == -1:
                continue
                
            rows = table.find_all("tr")[1:]
            for r in rows:
                cols = [td.text.strip() for td in r.find_all(["td", "th"])]
                if len(cols) <= max(player_idx, pos_idx):
                    continue
                
                name = clean_player_name(cols[player_idx])
                if not name:
                    continue
                
                pos = cols[pos_idx]
                dob = parse_dob(cols[dob_idx]) if dob_idx != -1 and dob_idx < len(cols) else "1996-01-01"
                caps = clean_int(cols[caps_idx]) if caps_idx != -1 and caps_idx < len(cols) else 0
                goals = clean_int(cols[goals_idx]) if goals_idx != -1 and goals_idx < len(cols) else 0
                club = cols[club_idx] if club_idx != -1 and club_idx < len(cols) else "Unknown"
                
                players.append({
                    "full_name": name,
                    "date_of_birth": dob,
                    "nationality": team_name,
                    "position": pos,
                    "current_club": club,
                    "international_caps": caps,
                    "international_goals": goals,
                })
        print(f"Scraped {len(players)} players from Wikipedia")
        return players
    except Exception as e:
        print(f"Error scraping Wikipedia: {e}")
        return []

def download_url(url: str, destination: Path, timeout: int = 30) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "fifa2026-predictor/0.1"})
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination

def load_optional_csvs(paths: Iterable[Path]) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for path in paths:
        if path.exists() and path.suffix.lower() == ".csv":
            frames[path.stem] = pd.read_csv(path)
    return frames
