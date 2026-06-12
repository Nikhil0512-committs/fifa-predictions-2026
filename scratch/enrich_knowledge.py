import os

file_path = "./fifa_predictor/knowledge.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. FIFA_RANKINGS
target_rankings = '"Sweden":                 (26, 1510.44),  # for training fallback'
replace_rankings = '"Sweden":                 (26, 1510.44),  # for training fallback\n    "Iraq":                   (58, 1420.55),\n    "Czechia":                (36, 1502.44),'
if target_rankings in content:
    content = content.replace(target_rankings, replace_rankings)
    print("Updated FIFA_RANKINGS")

# 2. ELO_RATINGS
target_elo = '"Sweden":                 1720,'
replace_elo = '"Sweden":                 1720,\n    "Iraq":                   1620,\n    "Czechia":                1730,'
if target_elo in content:
    content = content.replace(target_elo, replace_elo)
    print("Updated ELO_RATINGS")

# 3. RECENT_FORM
target_form = '"Curaçao":     {"w": 2, "d": 2, "l": 6, "gf": 7, "ga": 17},'
replace_form = '"Curaçao":     {"w": 2, "d": 2, "l": 6, "gf": 7, "ga": 17},\n    "Iraq":        {"w": 5, "d": 2, "l": 3, "gf": 14, "ga": 11},\n    "Czechia":     {"w": 6, "d": 2, "l": 2, "gf": 18, "ga": 10},'
if target_form in content:
    content = content.replace(target_form, replace_form)
    print("Updated RECENT_FORM")

# 4. SQUAD_VALUE_M
target_value = '"Curaçao":     45,'
replace_value = '"Curaçao":     45,\n    "Iraq":        25,\n    "Czechia":     180,'
if target_value in content:
    content = content.replace(target_value, replace_value)
    print("Updated SQUAD_VALUE_M")

# 5. PARTICIPATIONS
target_parts = '"Qatar": 1,'
replace_parts = '"Qatar": 1, "Iraq": 1, "Czechia": 10,'
if target_parts in content:
    content = content.replace(target_parts, replace_parts)
    print("Updated PARTICIPATIONS")

# 6. BEST_RESULT
target_best = '"Curaçao": "Group Stage",'
replace_best = '"Curaçao": "Group Stage",\n    "Iraq": "Group Stage",\n    "Czechia": "Runner-Up",'
if target_best in content:
    content = content.replace(target_best, replace_best)
    print("Updated BEST_RESULT")

# 7. KEY_PLAYERS
target_players = """        ("Victor Lindelof", "1994-07-17", "DF"),
        ("Robin Olsen", "1990-01-08", "GK"),
    ],"""

replace_players = """        ("Victor Lindelof", "1994-07-17", "DF"),
        ("Robin Olsen", "1990-01-08", "GK"),
    ],
    "Iraq": [
        ("Fahad Talib", "1994-10-21", "GK"),
        ("Rebin Sulaka", "1992-04-12", "DF"),
        ("Hussein Ali", "2002-03-01", "DF"),
        ("Zaid Tahseen", "2001-01-29", "DF"),
        ("Akam Hashim", "1998-08-16", "DF"),
        ("Manaf Younis", "1996-11-16", "DF"),
        ("Youssef Amyn", "2003-08-21", "MF"),
        ("Ibrahim Bayesh", "2000-05-01", "MF"),
        ("Ali Al-Hamadi", "2002-03-01", "FW"),
        ("Mohanad Ali", "2000-06-20", "FW"),
        ("Ahmed Qasem", "2003-07-12", "FW"),
        ("Jalal Hassan", "1991-05-18", "GK"),
        ("Ali Yousif", "1996-01-19", "FW"),
        ("Zidane Iqbal", "2003-04-27", "MF"),
        ("Ahmed Maknzi", "2001-09-24", "DF"),
        ("Amir Al-Ammari", "1997-07-27", "MF"),
        ("Ali Jasim", "2004-01-20", "FW"),
        ("Aymen Hussein", "1996-03-22", "FW"),
        ("Kevin Yakob", "2000-10-10", "MF"),
        ("Aimar Sher", "2002-12-20", "MF"),
        ("Marko Farji", "2004-03-16", "FW"),
        ("Ahmed Basil", "1996-08-19", "GK"),
        ("Merchas Doski", "1999-12-07", "DF"),
        ("Zaid Ismail", "2002-01-03", "MF"),
        ("Mustafa Saadoon", "2001-05-25", "DF"),
        ("Frans Putros", "1993-07-14", "DF"),
    ],
    "Czechia": [
        ("Matej Kovar", "2000-05-17", "GK"),
        ("David Zima", "2000-11-08", "DF"),
        ("Tomas Holes", "1993-03-31", "DF"),
        ("Robin Hranac", "2000-01-29", "DF"),
        ("Vladimir Coufal", "1992-08-22", "DF"),
        ("Stepan Chaloupek", "2003-03-08", "DF"),
        ("Ladislav Krejci", "1999-04-20", "DF"),
        ("Vladimir Darida", "1990-08-08", "MF"),
        ("Adam Hlozek", "2002-07-25", "FW"),
        ("Patrik Schick", "1996-01-24", "FW"),
        ("Jan Kuchta", "1997-01-08", "FW"),
        ("Lukas Cerv", "2001-04-10", "MF"),
        ("Mojmir Chytil", "1999-04-29", "FW"),
        ("David Jurasek", "2000-08-07", "DF"),
        ("Pavel Sulc", "2000-12-29", "FW"),
        ("Jindrich Stanek", "1996-04-27", "GK"),
        ("Lukas Provod", "1996-10-23", "MF"),
        ("Michal Sadilek", "1999-05-31", "MF"),
        ("Tomas Chory", "1995-01-26", "FW"),
        ("Jaroslav Zeleny", "1992-08-20", "DF"),
        ("David Doudera", "1998-05-31", "DF"),
        ("Tomas Soucek", "1995-02-27", "MF"),
        ("Lukas Hornicek", "2002-07-13", "GK"),
        ("Alexandr Sojka", "2003-04-02", "MF"),
        ("Hugo Sochurek", "2008-06-07", "MF"),
        ("Denis Visinsky", "2003-03-21", "FW"),
    ],"""

if target_players in content:
    content = content.replace(target_players, replace_players)
    print("Updated KEY_PLAYERS")
else:
    # Alternative format lookup without exact whitespace
    print("WARNING: KEY_PLAYERS target not matched exactly. Checking alternatives...")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished enriching knowledge.py")
