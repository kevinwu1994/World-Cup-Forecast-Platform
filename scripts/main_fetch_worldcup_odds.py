import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")

SPORT_KEY = "soccer_fifa_world_cup"

OUTPUT_FILE = "reports/worldcup_market_odds.csv"


def main():

    url = (
        f"https://api.the-odds-api.com/v4/sports/"
        f"{SPORT_KEY}/odds"
    )

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    events = response.json()

    rows = []

    for event in events:

        home_team = event["home_team"]
        away_team = event["away_team"]

        bookmakers = event.get(
            "bookmakers",
            []
        )

        if not bookmakers:
            continue

        bookmaker = bookmakers[0]

        market = bookmaker["markets"][0]

        outcomes = market["outcomes"]

        home_odds = None
        draw_odds = None
        away_odds = None

        for outcome in outcomes:

            name = outcome["name"]
            price = outcome["price"]

            if name == home_team:
                home_odds = price

            elif name == away_team:
                away_odds = price

            elif name.lower() == "draw":
                draw_odds = price

        rows.append(
            {
                "home_team": home_team,
                "away_team": away_team,
                "home_odds": home_odds,
                "draw_odds": draw_odds,
                "away_odds": away_odds,
            }
        )

    df = pd.DataFrame(rows)

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 70)
    print("WORLD CUP MARKET ODDS")
    print("=" * 70)
    print(df.head(20).to_string(index=False))
    print()
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()