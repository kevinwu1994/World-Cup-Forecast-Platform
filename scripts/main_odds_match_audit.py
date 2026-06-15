import pandas as pd


MODEL_FILE = "reports/worldcup_match_probabilities.csv"
MARKET_FILE = "reports/worldcup_market_odds.csv"


def main():

    model_df = pd.read_csv(MODEL_FILE)
    market_df = pd.read_csv(MARKET_FILE)

    model_matches = set(
        zip(
            model_df["home_team"],
            model_df["away_team"],
        )
    )

    market_matches = set(
        zip(
            market_df["home_team"],
            market_df["away_team"],
        )
    )

    matched = model_matches & market_matches

    missing = model_matches - market_matches

    print()
    print("=" * 70)
    print("ODDS MATCH AUDIT")
    print("=" * 70)

    print()
    print(f"Model Matches : {len(model_matches)}")
    print(f"Market Matches: {len(market_matches)}")
    print(f"Matched       : {len(matched)}")
    print(f"Missing       : {len(missing)}")

    print()
    print("=" * 70)
    print("MISSING MATCHES")
    print("=" * 70)

    for home, away in sorted(missing):
        print(f"{home} vs {away}")


if __name__ == "__main__":
    main()