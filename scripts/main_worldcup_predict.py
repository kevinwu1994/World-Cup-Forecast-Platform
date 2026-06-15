from pathlib import Path

import pandas as pd

from api.worldcup_client import WorldCupClient
from models.xg_engine import XGEngine
from models.score_probability import ScoreProbability


SCORE_OUTPUT_FILE = "reports/worldcup_predictions.csv"
MATCH_OUTPUT_FILE = "reports/worldcup_match_probabilities.csv"

TOP_N_SCORES = 10


def calculate_match_probs(score_df: pd.DataFrame) -> dict:
    home_prob = score_df[
        score_df["home_goals"] > score_df["away_goals"]
    ]["probability"].sum()

    draw_prob = score_df[
        score_df["home_goals"] == score_df["away_goals"]
    ]["probability"].sum()

    away_prob = score_df[
        score_df["home_goals"] < score_df["away_goals"]
    ]["probability"].sum()

    total = home_prob + draw_prob + away_prob

    return {
        "home_prob": home_prob / total,
        "draw_prob": draw_prob / total,
        "away_prob": away_prob / total,
    }


def main() -> None:
    client = WorldCupClient()
    xg_engine = XGEngine()
    score_model = ScoreProbability()

    teams = client.get_teams()
    fixtures = client.get_fixtures()

    score_rows = []
    match_rows = []

    print()
    print("=" * 60)
    print("WORLD CUP MATCH PREDICTIONS")
    print("=" * 60)

    for _, match in fixtures.iterrows():
        match_id = match["match_id"]
        date = match["date"]
        group = match["group"]
        home_team = match["home_team"]
        away_team = match["away_team"]

        home_row = teams[teams["team"] == home_team].iloc[0]
        away_row = teams[teams["team"] == away_team].iloc[0]

        home_elo = home_row["elo_rating"]
        away_elo = away_row["elo_rating"]

        home_xg, away_xg = xg_engine.elo_to_xg(
            home_elo,
            away_elo,
        )

        score_df = score_model.score_matrix(
            home_xg=home_xg,
            away_xg=away_xg,
            max_goals=6,
        )

        probs = calculate_match_probs(score_df)

        match_rows.append(
            {
                "match_id": match_id,
                "date": date,
                "group": group,
                "home_team": home_team,
                "away_team": away_team,
                "home_elo": home_elo,
                "away_elo": away_elo,
                "home_xg": home_xg,
                "away_xg": away_xg,
                "home_prob": probs["home_prob"],
                "draw_prob": probs["draw_prob"],
                "away_prob": probs["away_prob"],
                "home_odds": match.get("home_odds", None),
                "draw_odds": match.get("draw_odds", None),
                "away_odds": match.get("away_odds", None),
            }
        )

        print()
        print("-" * 60)
        print(f"{home_team} vs {away_team}")
        print("-" * 60)
        print(f"xG       : {home_xg:.3f} - {away_xg:.3f}")
        print(f"Home Win : {probs['home_prob']:.2%}")
        print(f"Draw     : {probs['draw_prob']:.2%}")
        print(f"Away Win : {probs['away_prob']:.2%}")

        print()
        print("Top 5 Scores:")

        for _, row in score_df.head(5).iterrows():
            print(
                f"{row['score']:<5} "
                f"{row['probability']:.2%}"
            )

        for rank, row in enumerate(
            score_df.head(TOP_N_SCORES).itertuples(index=False),
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
                    "score": row.score,
                    "home_goals": row.home_goals,
                    "away_goals": row.away_goals,
                    "score_probability": row.probability,
                    "home_xg": home_xg,
                    "away_xg": away_xg,
                    "home_prob": probs["home_prob"],
                    "draw_prob": probs["draw_prob"],
                    "away_prob": probs["away_prob"],
                }
            )

    Path("reports").mkdir(
        parents=True,
        exist_ok=True,
    )

    score_report = pd.DataFrame(score_rows)
    match_report = pd.DataFrame(match_rows)

    score_report.to_csv(
        SCORE_OUTPUT_FILE,
        index=False,
    )

    match_report.to_csv(
        MATCH_OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 60)
    print("REPORTS SAVED")
    print("=" * 60)
    print(f"Score predictions saved to: {SCORE_OUTPUT_FILE}")
    print(f"Match probabilities saved to: {MATCH_OUTPUT_FILE}")


if __name__ == "__main__":
    main()