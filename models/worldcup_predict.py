from pathlib import Path

import pandas as pd

from models.worldcup_match_predictor import predict_match
from models.xg_converter import probabilities_to_xg
from models.score_model import score_matrix


TEAMS_FILE = "data/manual/teams.csv"
FIXTURES_FILE = "data/manual/worldcup_fixtures.csv"

MATCH_OUTPUT_FILE = "reports/worldcup_match_predictions.csv"
SCORE_OUTPUT_FILE = "reports/worldcup_score_predictions.csv"
TOP_SCORE_REPORT = "reports/top_score_predictions.csv"

TOP_N_SCORES = 10


def main() -> None:
    teams = pd.read_csv(TEAMS_FILE)
    fixtures = pd.read_csv(FIXTURES_FILE)

    match_rows = []
    score_rows = []

    print()
    print("=" * 40)
    print("World Cup Match + Score Predictions")
    print("=" * 40)

    for _, match in fixtures.iterrows():
        match_id = match["match_id"]
        date = match["date"]
        group = match["group"]
        home_team = match["home_team"]
        away_team = match["away_team"]

        home_info = teams[teams["team"] == home_team].iloc[0]
        away_info = teams[teams["team"] == away_team].iloc[0]

        result = predict_match(
            home_team=home_team,
            away_team=away_team,
            home_elo=home_info["elo_rating"],
            away_elo=away_info["elo_rating"],
            home_odds=match["home_odds"],
            draw_odds=match["draw_odds"],
            away_odds=match["away_odds"],
        )

        home_xg, away_xg = probabilities_to_xg(
            home_prob=result["home_prob"],
            draw_prob=result["draw_prob"],
            away_prob=result["away_prob"],
        )

        scores = score_matrix(
            home_xg=home_xg,
            away_xg=away_xg,
            max_goals=6,
        )

        scores = sorted(
            scores,
            key=lambda x: x["probability"],
            reverse=True,
        )

        match_rows.append(
            {
                "match_id": match_id,
                "date": date,
                "group": group,
                "home_team": home_team,
                "away_team": away_team,
                "home_prob": result["home_prob"],
                "draw_prob": result["draw_prob"],
                "away_prob": result["away_prob"],
                "home_xg": home_xg,
                "away_xg": away_xg,
                "home_odds": match["home_odds"],
                "draw_odds": match["draw_odds"],
                "away_odds": match["away_odds"],
            }
        )

        for rank, row in enumerate(
            scores[:TOP_N_SCORES],
            start=1,
        ):
            score_rows.append(
                {
                    "match_id": match_id,
                    "date": date,
                    "group": group,
                    "home_team": home_team,
                    "away_team": away_team,
                    "rank": rank,
                    "score": f"{row['home_goals']}-{row['away_goals']}",
                    "home_goals": row["home_goals"],
                    "away_goals": row["away_goals"],
                    "score_probability": row["probability"],
                    "home_xg": home_xg,
                    "away_xg": away_xg,
                }
            )

        print()
        print(f"{home_team} vs {away_team}")
        print("-" * 40)
        print(f"Home Win : {result['home_prob']:.2%}")
        print(f"Draw     : {result['draw_prob']:.2%}")
        print(f"Away Win : {result['away_prob']:.2%}")
        print(f"xG       : {home_team} {home_xg} - {away_xg} {away_team}")

        print("\nTop Scores:")
        for row in scores[:5]:
            score = f"{row['home_goals']}-{row['away_goals']}"
            prob = row["probability"]
            print(f"{score:<5} {prob:.2%}")

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    match_df = pd.DataFrame(match_rows)
    score_df = pd.DataFrame(score_rows)

    match_df.to_csv(
        MATCH_OUTPUT_FILE,
        index=False,
    )

    score_df.to_csv(
        SCORE_OUTPUT_FILE,
        index=False,
    )

    score_df.to_csv(
        TOP_SCORE_REPORT,
        index=False,
    )

    print()
    print("=" * 40)
    print("Saved Reports")
    print("=" * 40)
    print(f"Saved match report to: {MATCH_OUTPUT_FILE}")
    print(f"Saved score report to: {SCORE_OUTPUT_FILE}")
    print(f"Saved top score report to: {TOP_SCORE_REPORT}")


if __name__ == "__main__":
    main()