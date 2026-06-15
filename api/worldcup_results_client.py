import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()


class FootballResultsClient:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self):
        self.api_key = os.getenv("API_FOOTBALL_KEY")

        if not self.api_key:
            raise ValueError("Missing API_FOOTBALL_KEY in .env")

        self.headers = {
            "x-apisports-key": self.api_key,
        }

    def get_fixtures(
        self,
        league_id: int,
        season: int,
    ) -> pd.DataFrame:
        url = f"{self.BASE_URL}/fixtures"

        params = {
            "league": league_id,
            "season": season,
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        rows = []

        for item in data.get("response", []):
            fixture = item.get("fixture", {})
            league = item.get("league", {})
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            score = item.get("score", {})

            home = teams.get("home", {})
            away = teams.get("away", {})
            status = fixture.get("status", {})

            rows.append({
                "api_fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "league_id": league.get("id"),
                "league_name": league.get("name"),
                "season": league.get("season"),
                "round": league.get("round"),
                "status_long": status.get("long"),
                "status_short": status.get("short"),
                "elapsed": status.get("elapsed"),

                "home_team": home.get("name"),
                "away_team": away.get("name"),
                "home_team_id": home.get("id"),
                "away_team_id": away.get("id"),

                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),

                "home_halftime": score.get("halftime", {}).get("home"),
                "away_halftime": score.get("halftime", {}).get("away"),
                "home_fulltime": score.get("fulltime", {}).get("home"),
                "away_fulltime": score.get("fulltime", {}).get("away"),
                "home_extratime": score.get("extratime", {}).get("home"),
                "away_extratime": score.get("extratime", {}).get("away"),
                "home_penalty": score.get("penalty", {}).get("home"),
                "away_penalty": score.get("penalty", {}).get("away"),
            })

        return pd.DataFrame(rows)

    def get_leagues_by_search(
        self,
        search: str,
    ) -> pd.DataFrame:
        url = f"{self.BASE_URL}/leagues"

        params = {
            "search": search,
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        rows = []

        for item in data.get("response", []):
            league = item.get("league", {})
            country = item.get("country", {})

            seasons = item.get("seasons", [])

            for season in seasons:
                rows.append({
                    "league_id": league.get("id"),
                    "league_name": league.get("name"),
                    "type": league.get("type"),
                    "country_name": country.get("name"),
                    "season": season.get("year"),
                    "season_start": season.get("start"),
                    "season_end": season.get("end"),
                    "current": season.get("current"),
                })

        return pd.DataFrame(rows)


def main():
    client = FootballResultsClient()

    Path("reports").mkdir(parents=True, exist_ok=True)

    leagues_df = client.get_leagues_by_search("World Cup")
    leagues_df.to_csv(
        "reports/api_football_worldcup_leagues.csv",
        index=False,
    )

    print()
    print("=" * 70)
    print("API-FOOTBALL WORLD CUP LEAGUES")
    print("=" * 70)

    if leagues_df.empty:
        print("No World Cup leagues found.")
    else:
        print(
            leagues_df[
                [
                    "league_id",
                    "league_name",
                    "country_name",
                    "season",
                    "current",
                ]
            ]
            .drop_duplicates()
            .to_string(index=False)
        )

    print()
    print("Saved: reports/api_football_worldcup_leagues.csv")


if __name__ == "__main__":
    main()