from pathlib import Path
import pandas as pd


OUTPUT_DIR = Path("data/manual")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}


ELO_RATINGS = {
    "Argentina": 1885,
    "France": 1865,
    "Spain": 1845,
    "England": 1835,
    "Brazil": 1825,
    "Portugal": 1815,
    "Netherlands": 1795,
    "Belgium": 1780,
    "Germany": 1775,
    "Uruguay": 1765,
    "Croatia": 1745,
    "Colombia": 1735,
    "Morocco": 1715,
    "Japan": 1705,
    "United States": 1695,
    "Switzerland": 1685,
    "Mexico": 1675,
    "Senegal": 1665,
    "Austria": 1655,
    "Sweden": 1645,
    "Turkey": 1635,
    "Ecuador": 1625,
    "South Korea": 1615,
    "Australia": 1595,
    "Ivory Coast": 1585,
    "Paraguay": 1575,
    "Norway": 1565,
    "Egypt": 1555,
    "Tunisia": 1545,
    "Czechia": 1535,
    "Algeria": 1525,
    "Canada": 1515,
    "Iran": 1505,
    "Scotland": 1495,
    "Saudi Arabia": 1485,
    "Qatar": 1465,
    "South Africa": 1455,
    "Bosnia and Herzegovina": 1445,
    "Ghana": 1435,
    "Panama": 1425,
    "New Zealand": 1415,
    "Uzbekistan": 1405,
    "DR Congo": 1395,
    "Iraq": 1385,
    "Jordan": 1375,
    "Cape Verde": 1365,
    "Haiti": 1355,
    "Curacao": 1345,
}


def make_teams_csv():
    rows = []

    for group, teams in GROUPS.items():
        for team in teams:
            rows.append({
                "team": team,
                "group": group,
                "elo_rating": ELO_RATINGS[team],
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "teams.csv", index=False)


def make_groups_csv():
    rows = []

    for group, teams in GROUPS.items():
        for team in teams:
            rows.append({
                "group": group,
                "team": team,
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "worldcup_groups.csv", index=False)


def make_fixtures_csv():
    rows = []
    match_id = 1

    fixture_dates = {
        "A": ["2026-06-11", "2026-06-11", "2026-06-18", "2026-06-18", "2026-06-24", "2026-06-24"],
        "B": ["2026-06-12", "2026-06-13", "2026-06-18", "2026-06-18", "2026-06-24", "2026-06-24"],
        "C": ["2026-06-13", "2026-06-13", "2026-06-19", "2026-06-19", "2026-06-24", "2026-06-24"],
        "D": ["2026-06-12", "2026-06-14", "2026-06-19", "2026-06-19", "2026-06-25", "2026-06-25"],
        "E": ["2026-06-14", "2026-06-14", "2026-06-20", "2026-06-20", "2026-06-25", "2026-06-25"],
        "F": ["2026-06-14", "2026-06-14", "2026-06-20", "2026-06-21", "2026-06-25", "2026-06-25"],
        "G": ["2026-06-15", "2026-06-15", "2026-06-21", "2026-06-21", "2026-06-26", "2026-06-26"],
        "H": ["2026-06-15", "2026-06-15", "2026-06-21", "2026-06-21", "2026-06-26", "2026-06-26"],
        "I": ["2026-06-16", "2026-06-16", "2026-06-22", "2026-06-22", "2026-06-26", "2026-06-26"],
        "J": ["2026-06-16", "2026-06-17", "2026-06-22", "2026-06-22", "2026-06-27", "2026-06-27"],
        "K": ["2026-06-17", "2026-06-17", "2026-06-23", "2026-06-23", "2026-06-27", "2026-06-27"],
        "L": ["2026-06-17", "2026-06-17", "2026-06-23", "2026-06-23", "2026-06-27", "2026-06-27"],
    }

    for group, teams in GROUPS.items():
        fixtures = [
            (teams[0], teams[1]),
            (teams[2], teams[3]),
            (teams[0], teams[2]),
            (teams[3], teams[1]),
            (teams[2], teams[1]),
            (teams[3], teams[0]),
        ]

        for date, (home_team, away_team) in zip(fixture_dates[group], fixtures):
            rows.append({
                "match_id": match_id,
                "date": date,
                "group": group,
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": "",
                "draw_odds": "",
                "away_odds": "",
            })
            match_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "worldcup_fixtures.csv", index=False)


def main():
    make_teams_csv()
    make_groups_csv()
    make_fixtures_csv()

    print("Manual World Cup files created:")
    print(OUTPUT_DIR / "teams.csv")
    print(OUTPUT_DIR / "worldcup_groups.csv")
    print(OUTPUT_DIR / "worldcup_fixtures.csv")


if __name__ == "__main__":
    main()