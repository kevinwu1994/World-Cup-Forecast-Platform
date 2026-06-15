from pathlib import Path

import pandas as pd


MODEL_FILE = "reports/worldcup_match_probabilities.csv"
MARKET_FILE = "reports/worldcup_market_odds.csv"

OUTPUT_FILE = (
    "reports/worldcup_adjusted_match_probabilities.csv"
)

MODEL_WEIGHT = 0.80
MARKET_WEIGHT = 0.20


def implied_probability(
    home_odds,
    draw_odds,
    away_odds,
):
    home = 1 / home_odds
    draw = 1 / draw_odds
    away = 1 / away_odds

    total = home + draw + away

    return (
        home / total,
        draw / total,
        away / total,
    )


def main():

    model_df = pd.read_csv(MODEL_FILE)
    market_df = pd.read_csv(MARKET_FILE)

    model_df = model_df.drop(
        columns=[
            "home_odds",
            "draw_odds",
            "away_odds",
        ],
        errors="ignore",
    )

    merged = pd.merge(
        model_df,
        market_df,
        on=["home_team", "away_team"],
        how="left",
    )

    adjusted_rows = []

    for _, row in merged.iterrows():

        if pd.isna(row["home_odds"]):

            adjusted_rows.append(row.to_dict())
            continue

        market_home, market_draw, market_away = (
            implied_probability(
                row["home_odds"],
                row["draw_odds"],
                row["away_odds"],
            )
        )

        adjusted_home = (
            MODEL_WEIGHT * row["home_prob"]
            + MARKET_WEIGHT * market_home
        )

        adjusted_draw = (
            MODEL_WEIGHT * row["draw_prob"]
            + MARKET_WEIGHT * market_draw
        )

        adjusted_away = (
            MODEL_WEIGHT * row["away_prob"]
            + MARKET_WEIGHT * market_away
        )

        total = (
            adjusted_home
            + adjusted_draw
            + adjusted_away
        )

        adjusted_home /= total
        adjusted_draw /= total
        adjusted_away /= total

        row_dict = row.to_dict()

        row_dict["model_home_prob"] = row["home_prob"]
        row_dict["model_draw_prob"] = row["draw_prob"]
        row_dict["model_away_prob"] = row["away_prob"]

        row_dict["market_home_prob"] = market_home
        row_dict["market_draw_prob"] = market_draw
        row_dict["market_away_prob"] = market_away

        row_dict["home_prob"] = adjusted_home
        row_dict["draw_prob"] = adjusted_draw
        row_dict["away_prob"] = adjusted_away

        adjusted_rows.append(row_dict)

    result_df = pd.DataFrame(adjusted_rows)

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 70)
    print("MARKET ADJUSTED PROBABILITIES")
    print("=" * 70)
    print()

    print(
        result_df[
            [
                "home_team",
                "away_team",
                "home_prob",
                "draw_prob",
                "away_prob",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print()
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()