import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")
SPORT_KEY = "soccer_fifa_world_cup"
OUTPUT_FILE = "reports/worldcup_live_scores.csv"
HISTORICAL_FILE = "reports/worldcup_historical_results.csv"

TEAM_NAME_MAP = {
    "Czech Republic": "Czechia",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "USA": "United States",
    "Curacao": "Curaçao",
}

def main():
    if not API_KEY:
        raise ValueError("Missing THE_ODDS_API_KEY in .env")

    url = f"https://api.the-odds-api.com/v4/sports/{SPORT_KEY}/scores"

    params = {
        "apiKey": API_KEY,
        "daysFrom": 3,
        "dateFormat": "iso",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    events = response.json()
    rows = []

    for event in events:

        home_team = TEAM_NAME_MAP.get(
            event.get("home_team"),
            event.get("home_team")
        )

        away_team = TEAM_NAME_MAP.get(
            event.get("away_team"),
            event.get("away_team")
        )

        completed = event.get("completed", False)
        scores = event.get("scores") or []

        home_score = None
        away_score = None

        for item in scores:
            name = TEAM_NAME_MAP.get(item.get("name"), item.get("name"))
            score = item.get("score")

            if name == home_team:
                home_score = score
            elif name == away_team:
                away_score = score

        rows.append(
            {
                "event_id": event.get("id"),
                "commence_time": event.get("commence_time"),
                "home_team": home_team,
                "away_team": away_team,
                "completed": completed,
                "home_score": home_score,
                "away_score": away_score,
                "last_update": event.get("last_update"),
            }
        )

    df = pd.DataFrame(rows)

    Path("reports").mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    historical_path = Path(HISTORICAL_FILE)

    if historical_path.exists():
        old_df = pd.read_csv(historical_path)
        combined_df = pd.concat([old_df, df], ignore_index=True)
    else:
        combined_df = df.copy()

    combined_df = combined_df.drop_duplicates(
        subset=["event_id"],
        keep="last"
    )

    combined_df = combined_df.sort_values("commence_time")

    combined_df.to_csv(HISTORICAL_FILE, index=False)
    
    print()
    print("=" * 70)
    print("WORLD CUP LIVE SCORES")
    print("=" * 70)

    if df.empty:
        print("No score data returned.")
    else:
        print(df.head(30).to_string(index=False))

    print()
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()