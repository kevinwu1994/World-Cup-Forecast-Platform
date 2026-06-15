from pathlib import Path

import pandas as pd


PREDICTIONS_FILE = "reports/worldcup_predictions.csv"
RESULTS_FILE = "reports/worldcup_historical_results.csv"
OUTPUT_FILE = "reports/prediction_accuracy.csv"


TEAM_MAP = {
    "Czech Republic": "Czechia",
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "USA": "United States",
    "Curaçao": "Curacao",
}


def normalize_team(team):
    if pd.isna(team):
        return team
    return TEAM_MAP.get(str(team).strip(), str(team).strip())


def get_result(home_score, away_score):
    if home_score > away_score:
        return "HOME"
    if home_score < away_score:
        return "AWAY"
    return "DRAW"


def main():
    pred_df = pd.read_csv(PREDICTIONS_FILE)
    result_df = pd.read_csv(RESULTS_FILE)

    result_df = result_df[result_df["completed"] == True].copy()

    result_df["home_team"] = result_df["home_team"].apply(normalize_team)
    result_df["away_team"] = result_df["away_team"].apply(normalize_team)

    pred_df["home_team"] = pred_df["home_team"].apply(normalize_team)
    pred_df["away_team"] = pred_df["away_team"].apply(normalize_team)

    records = []

    for _, actual_row in result_df.iterrows():
        home = actual_row["home_team"]
        away = actual_row["away_team"]

        if pd.isna(actual_row["home_score"]) or pd.isna(actual_row["away_score"]):
            continue

        actual_home = int(actual_row["home_score"])
        actual_away = int(actual_row["away_score"])

        actual_score = f"{actual_home}-{actual_away}"
        actual_result = get_result(actual_home, actual_away)

        match_preds = pred_df[
            (pred_df["home_team"] == home)
            & (pred_df["away_team"] == away)
        ].copy()

        if match_preds.empty:
            match_preds = pred_df[
                (pred_df["home_team"] == away)
                & (pred_df["away_team"] == home)
            ].copy()

            if not match_preds.empty:
                actual_score = f"{actual_away}-{actual_home}"
                actual_result = get_result(actual_away, actual_home)
                home, away = away, home

        if match_preds.empty:
            records.append({
                "home_team": home,
                "away_team": away,
                "actual_score": actual_score,
                "actual_result": actual_result,
                "matched": False,
                "predicted_result": "",
                "result_hit": False,
                "top1_score": "",
                "top2_score": "",
                "top3_score": "",
                "top4_score": "",
                "top5_score": "",
                "top6_score": "",
                "top7_score": "",
                "top8_score": "",
                "top1_hit": False,
                "top3_hit": False,
                "top5_hit": False,
                "top8_hit": False,
            })
            continue

        match_preds = match_preds.sort_values(
            "score_probability",
            ascending=False,
        )

        top_scores = match_preds["score"].head(8).tolist()
        first_row = match_preds.iloc[0]

        probs = {
            "HOME": first_row["home_prob"],
            "DRAW": first_row["draw_prob"],
            "AWAY": first_row["away_prob"],
        }

        predicted_result = max(probs, key=probs.get)

        records.append({
            "home_team": home,
            "away_team": away,
            "actual_score": actual_score,
            "actual_result": actual_result,
            "matched": True,
            "predicted_result": predicted_result,
            "result_hit": predicted_result == actual_result,
            "top1_score": top_scores[0] if len(top_scores) > 0 else "",
            "top2_score": top_scores[1] if len(top_scores) > 1 else "",
            "top3_score": top_scores[2] if len(top_scores) > 2 else "",
            "top4_score": top_scores[3] if len(top_scores) > 3 else "",
            "top5_score": top_scores[4] if len(top_scores) > 4 else "",
            "top6_score": top_scores[5] if len(top_scores) > 5 else "",
            "top7_score": top_scores[6] if len(top_scores) > 6 else "",
            "top8_score": top_scores[7] if len(top_scores) > 7 else "",
            "top1_hit": actual_score in top_scores[:1],
            "top3_hit": actual_score in top_scores[:3],
            "top5_hit": actual_score in top_scores[:5],
            "top8_hit": actual_score in top_scores[:8],
        })

    accuracy_df = pd.DataFrame(records)

    Path("reports").mkdir(parents=True, exist_ok=True)
    accuracy_df.to_csv(OUTPUT_FILE, index=False)

    matched_df = accuracy_df[accuracy_df["matched"] == True]

    print()
    print("=" * 70)
    print("PREDICTION ACCURACY")
    print("=" * 70)

    print(f"Completed matches: {len(accuracy_df)}")
    print(f"Matched matches  : {len(matched_df)}")

    if len(matched_df) > 0:
        print(f"Result Accuracy  : {matched_df['result_hit'].mean():.2%}")
        print(f"Top1 Score Hit   : {matched_df['top1_hit'].mean():.2%}")
        print(f"Top3 Score Hit   : {matched_df['top3_hit'].mean():.2%}")
        print(f"Top5 Score Hit   : {matched_df['top5_hit'].mean():.2%}")
        print(f"Top8 Score Hit   : {matched_df['top8_hit'].mean():.2%}")

    print()
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()