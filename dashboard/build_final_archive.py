"""Build fixed post-tournament dashboard archives from committed forecast snapshots."""

from __future__ import annotations

import io
import subprocess
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ARCHIVE = ROOT / "dashboard" / "archive_data"


def git_versions(path: str):
    log = subprocess.check_output(
        ["git", "log", "--all", "--reverse", "--format=%H|%cI", "--", path],
        cwd=ROOT,
        text=True,
    ).splitlines()
    if not log:
        return

    specs = [f"{line.split('|', 1)[0]}:{path}" for line in log]
    output = subprocess.check_output(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=("\n".join(specs) + "\n").encode(),
    )
    stream = io.BytesIO(output)

    for metadata in log:
        header = stream.readline().decode().strip().split()
        size = int(header[2])
        raw = stream.read(size)
        stream.read(1)
        try:
            frame = pd.read_csv(io.BytesIO(raw))
        except Exception:
            continue
        yield metadata.split("|", 1)[1], frame


def normalize_team(value) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def matchup_key(home, away) -> str:
    return "||".join(sorted((normalize_team(home), normalize_team(away))))


def historical_frames(path: str) -> pd.DataFrame:
    frames = []
    for timestamp, frame in git_versions(path):
        copy = frame.copy()
        copy["forecast_as_of"] = timestamp
        frames.append(copy)
    return pd.concat(frames, ignore_index=True)


def tournament_stage(index: int) -> str:
    if index < 72:
        return "Group Stage"
    if index < 88:
        return "Round of 32"
    if index < 96:
        return "Round of 16"
    if index < 100:
        return "Quarterfinal"
    if index < 102:
        return "Semifinal"
    if index == 102:
        return "Third Place"
    return "Final"


def build_archive() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    forecast_history = historical_frames(
        "reports/worldcup_adjusted_match_probabilities.csv"
    )
    forecast_history["matchup_key"] = [
        matchup_key(home, away)
        for home, away in zip(forecast_history.home_team, forecast_history.away_team)
    ]
    forecasts = (
        forecast_history.sort_values("forecast_as_of")
        .drop_duplicates("matchup_key", keep="first")
        .reset_index(drop=True)
    )

    score_history = historical_frames("reports/worldcup_predictions.csv")
    score_history["matchup_key"] = [
        matchup_key(home, away)
        for home, away in zip(score_history.home_team, score_history.away_team)
    ]
    first_score_snapshot = (
        score_history.groupby("matchup_key", as_index=False)["forecast_as_of"].min()
    )
    scores = score_history.merge(
        first_score_snapshot,
        on=["matchup_key", "forecast_as_of"],
        how="inner",
    ).drop_duplicates(["matchup_key", "rank"], keep="first")

    results = pd.read_csv(REPORTS / "worldcup_historical_results.csv")
    # The retired score API stopped updating before the final completed. FIFA's
    # official match report records Spain 1-0 Argentina after extra time.
    final_mask = (
        results["home_team"].map(normalize_team).eq("spain")
        & results["away_team"].map(normalize_team).eq("argentina")
    )
    results.loc[final_mask, ["completed", "home_score", "away_score"]] = [
        True,
        1,
        0,
    ]
    results["commence_dt"] = pd.to_datetime(results["commence_time"], utc=True)
    results = results.sort_values("commence_dt").reset_index(drop=True)
    results["matchup_key"] = [
        matchup_key(home, away) for home, away in zip(results.home_team, results.away_team)
    ]
    results["stage"] = [tournament_stage(index) for index in range(len(results))]

    archive = results.merge(
        forecasts.drop(columns=["home_team", "away_team"], errors="ignore"),
        on="matchup_key",
        how="left",
        suffixes=("_result", "_forecast"),
    )

    def align_forecast(row):
        original = forecasts.loc[forecasts.matchup_key == row.matchup_key].iloc[0]
        same_order = normalize_team(original.home_team) == normalize_team(row.home_team)
        row["forecast_home_team"] = original.home_team
        row["forecast_away_team"] = original.away_team
        row["home_prob"] = original.home_prob if same_order else original.away_prob
        row["draw_prob"] = original.draw_prob
        row["away_prob"] = original.away_prob if same_order else original.home_prob
        row["home_xg"] = original.home_xg if same_order else original.away_xg
        row["away_xg"] = original.away_xg if same_order else original.home_xg
        return row

    archive = archive.apply(align_forecast, axis=1)
    probability_columns = ["home_prob", "draw_prob", "away_prob"]
    labels = {"home_prob": "HOME", "draw_prob": "DRAW", "away_prob": "AWAY"}
    archive["predicted_result"] = archive[probability_columns].idxmax(axis=1).map(labels)
    archive["actual_result"] = archive.apply(
        lambda row: (
            "HOME"
            if row.home_score > row.away_score
            else "AWAY"
            if row.away_score > row.home_score
            else "DRAW"
        )
        if bool(row.completed)
        else "",
        axis=1,
    )
    archive["result_hit"] = (
        archive["completed"].astype(bool)
        & (archive["predicted_result"] == archive["actual_result"])
    )
    archive["actual_score"] = archive.apply(
        lambda row: f"{int(row.home_score)}-{int(row.away_score)}"
        if bool(row.completed)
        else "",
        axis=1,
    )

    score_map = {}
    for key, group in scores.groupby("matchup_key"):
        forecast = forecasts.loc[forecasts.matchup_key == key].iloc[0]
        result = results.loc[results.matchup_key == key].iloc[0]
        same_order = normalize_team(forecast.home_team) == normalize_team(result.home_team)
        ranked = group.sort_values("rank").copy()
        if not same_order:
            ranked["score"] = ranked.apply(
                lambda row: f"{int(row.away_goals)}-{int(row.home_goals)}", axis=1
            )
            ranked[["home_goals", "away_goals"]] = ranked[
                ["away_goals", "home_goals"]
            ].to_numpy()
            ranked[["home_xg", "away_xg"]] = ranked[
                ["away_xg", "home_xg"]
            ].to_numpy()
        score_map[key] = ranked

    aligned_scores = pd.concat(score_map.values(), ignore_index=True)
    aligned_scores = aligned_scores.merge(
        results[["matchup_key", "home_team", "away_team", "stage", "commence_time"]],
        on="matchup_key",
        how="left",
        suffixes=("_forecast", ""),
    )

    for rank_limit in (1, 3, 5, 8):
        top_scores = (
            aligned_scores[aligned_scores["rank"] <= rank_limit]
            .groupby("matchup_key")["score"]
            .apply(set)
            .to_dict()
        )
        archive[f"top{rank_limit}_hit"] = archive.apply(
            lambda row: bool(row.completed)
            and row.actual_score in top_scores.get(row.matchup_key, set()),
            axis=1,
        )

    group_history = historical_frames("reports/group_stage_probabilities.csv")
    initial_group_snapshot = group_history["forecast_as_of"].min()
    group_archive = group_history[
        group_history["forecast_as_of"] == initial_group_snapshot
    ].drop_duplicates(["group", "team"])

    forecasts.to_csv(ARCHIVE / "match_forecasts.csv", index=False)
    aligned_scores.to_csv(ARCHIVE / "score_forecasts.csv", index=False)
    archive.to_csv(ARCHIVE / "tournament_matches.csv", index=False)
    group_archive.to_csv(ARCHIVE / "group_stage_probabilities.csv", index=False)
    pd.read_csv(REPORTS / "champion_probabilities.csv").to_csv(
        ARCHIVE / "champion_probabilities.csv", index=False
    )
    pd.read_csv(REPORTS / "model_vs_market.csv").to_csv(
        ARCHIVE / "model_vs_market.csv", index=False
    )

    completed = archive[archive["completed"].astype(bool)]
    print(f"Archived forecasts: {len(forecasts)}")
    print(f"Archived score rows: {len(aligned_scores)}")
    print(f"Tournament matches: {len(archive)} ({len(completed)} completed)")
    print(f"Winner accuracy: {completed.result_hit.mean():.1%}")
    print(f"Top-3 score hit rate: {completed.top3_hit.mean():.1%}")
    print(f"Group-stage teams: {len(group_archive)}")


if __name__ == "__main__":
    build_archive()
