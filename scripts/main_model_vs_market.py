from pathlib import Path

import pandas as pd


MODEL_FILE = "reports/worldcup_match_probabilities.csv"
MARKET_FILE = "reports/worldcup_market_odds.csv"
OUTPUT_FILE = "reports/model_vs_market.csv"


def implied_probability(home_odds, draw_odds, away_odds):
    home = 1 / home_odds
    draw = 1 / draw_odds
    away = 1 / away_odds

    total = home + draw + away

    return home / total, draw / total, away / total


def main():
    model_df = pd.read_csv(MODEL_FILE)
    market_df = pd.read_csv(MARKET_FILE)

    model_df = model_df.drop(
        columns=["home_odds", "draw_odds", "away_odds"],
        errors="ignore",
    )

    merged = pd.merge(
        model_df,
        market_df,
        on=["home_team", "away_team"],
        how="inner",
    )

    rows = []

    for _, row in merged.iterrows():
        market_home, market_draw, market_away = implied_probability(
            row["home_odds"],
            row["draw_odds"],
            row["away_odds"],
        )

        model_home = row["home_prob"]
        model_draw = row["draw_prob"]
        model_away = row["away_prob"]

        rows.append({
            "home_team": row["home_team"],
            "away_team": row["away_team"],

            "model_home_prob": model_home,
            "market_home_prob": market_home,
            "home_diff": model_home - market_home,

            "model_draw_prob": model_draw,
            "market_draw_prob": market_draw,
            "draw_diff": model_draw - market_draw,

            "model_away_prob": model_away,
            "market_away_prob": market_away,
            "away_diff": model_away - market_away,

            "abs_diff": (
                abs(model_home - market_home)
                + abs(model_draw - market_draw)
                + abs(model_away - market_away)
            ),
        })

    result_df = pd.DataFrame(rows)

    result_df = result_df.sort_values(
        "abs_diff",
        ascending=False,
    ).reset_index(drop=True)

    Path("reports").mkdir(parents=True, exist_ok=True)

    result_df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 70)
    print("MODEL VS MARKET")
    print("=" * 70)

    print()
    print("Matched matches:", len(result_df))
    print()

    print("TOP 20 BIGGEST DIFFERENCES")
    print()

    display_cols = [
        "home_team",
        "away_team",
        "model_home_prob",
        "market_home_prob",
        "home_diff",
        "model_draw_prob",
        "market_draw_prob",
        "draw_diff",
        "model_away_prob",
        "market_away_prob",
        "away_diff",
        "abs_diff",
    ]

    print(
        result_df[display_cols]
        .head(20)
        .to_string(index=False)
    )

    print()
    print(f"Saved: {OUTPUT_FILE}")

    print()
    print(f"Average Difference: {result_df['abs_diff'].mean():.4f}")
    print(f"Median Difference : {result_df['abs_diff'].median():.4f}")
    print(f"Max Difference    : {result_df['abs_diff'].max():.4f}")


if __name__ == "__main__":
    main()