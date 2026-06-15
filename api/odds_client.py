import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()


class OddsClient:

    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):
        self.api_key = os.getenv("THE_ODDS_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Missing THE_ODDS_API_KEY in .env"
            )

    def get_sports(self) -> pd.DataFrame:

        url = f"{self.BASE_URL}/sports"

        response = requests.get(
            url,
            params={
                "apiKey": self.api_key,
            },
            timeout=30,
        )

        response.raise_for_status()

        return pd.DataFrame(response.json())


def main():

    client = OddsClient()

    sports_df = client.get_sports()

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    sports_df.to_csv(
        "reports/available_sports.csv",
        index=False,
    )

    print()
    print("=" * 70)
    print("ODDS API CHECK")
    print("=" * 70)
    print()

    soccer_df = sports_df[
        sports_df["key"].str.contains(
            "soccer",
            case=False,
            na=False,
        )
    ]

    print(
        soccer_df[
            ["key", "title"]
        ].to_string(index=False)
    )

    print()
    print("Saved:")
    print("reports/available_sports.csv")


if __name__ == "__main__":
    main()