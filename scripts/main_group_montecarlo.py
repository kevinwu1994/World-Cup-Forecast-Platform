from pathlib import Path

import numpy as np
import pandas as pd


INPUT_FILE = "reports/worldcup_adjusted_match_probabilities.csv"
OUTPUT_FILE = "reports/group_stage_probabilities.csv"

N_SIMULATIONS = 10000
RANDOM_SEED = 42


def simulate_match(row, rng):
    probs = [
        row["home_prob"],
        row["draw_prob"],
        row["away_prob"],
    ]

    result = rng.choice(
        ["home", "draw", "away"],
        p=probs,
    )

    home_xg = row["home_xg"]
    away_xg = row["away_xg"]

    for _ in range(100):
        home_goals = rng.poisson(home_xg)
        away_goals = rng.poisson(away_xg)

        if result == "home" and home_goals > away_goals:
            return home_goals, away_goals

        if result == "draw" and home_goals == away_goals:
            return home_goals, away_goals

        if result == "away" and home_goals < away_goals:
            return home_goals, away_goals

    if result == "home":
        return 1, 0

    if result == "draw":
        return 1, 1

    return 0, 1


def initialize_table(teams):
    return {
        team: {
            "team": team,
            "points": 0,
            "gf": 0,
            "ga": 0,
            "gd": 0,
        }
        for team in teams
    }


def update_table(table, home, away, home_goals, away_goals):
    table[home]["gf"] += home_goals
    table[home]["ga"] += away_goals
    table[away]["gf"] += away_goals
    table[away]["ga"] += home_goals

    if home_goals > away_goals:
        table[home]["points"] += 3
    elif home_goals < away_goals:
        table[away]["points"] += 3
    else:
        table[home]["points"] += 1
        table[away]["points"] += 1


def rank_group(table, rng):
    rows = []

    for data in table.values():
        data = data.copy()
        data["gd"] = data["gf"] - data["ga"]
        data["random_tiebreaker"] = rng.random()
        rows.append(data)

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by=[
            "points",
            "gd",
            "gf",
            "random_tiebreaker",
        ],
        ascending=[
            False,
            False,
            False,
            False,
        ],
    ).reset_index(drop=True)

    df["rank"] = df.index + 1

    return df


def main():
    rng = np.random.default_rng(RANDOM_SEED)

    match_df = pd.read_csv(INPUT_FILE)

    required_cols = {
        "group",
        "home_team",
        "away_team",
        "home_prob",
        "draw_prob",
        "away_prob",
        "home_xg",
        "away_xg",
    }

    missing = required_cols - set(match_df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    groups = sorted(match_df["group"].unique())

    teams_by_group = {}

    for group in groups:
        group_matches = match_df[match_df["group"] == group]
        teams = sorted(
            set(group_matches["home_team"])
            | set(group_matches["away_team"])
        )
        teams_by_group[group] = teams

    counters = {}

    for group, teams in teams_by_group.items():
        for team in teams:
            counters[team] = {
                "group": group,
                "team": team,
                "first_place": 0,
                "second_place": 0,
                "qualified": 0,
                "third_place": 0,
                "last_place": 0,
                "total_points": 0,
                "total_gd": 0,
            }

    for _ in range(N_SIMULATIONS):
        for group in groups:
            group_matches = match_df[match_df["group"] == group]
            teams = teams_by_group[group]

            table = initialize_table(teams)

            for _, row in group_matches.iterrows():
                home = row["home_team"]
                away = row["away_team"]

                home_goals, away_goals = simulate_match(row, rng)

                update_table(
                    table,
                    home,
                    away,
                    home_goals,
                    away_goals,
                )

            ranked = rank_group(table, rng)

            for _, row in ranked.iterrows():
                team = row["team"]
                rank = row["rank"]

                counters[team]["total_points"] += row["points"]
                counters[team]["total_gd"] += row["gd"]

                if rank == 1:
                    counters[team]["first_place"] += 1
                    counters[team]["qualified"] += 1
                elif rank == 2:
                    counters[team]["second_place"] += 1
                    counters[team]["qualified"] += 1
                elif rank == 3:
                    counters[team]["third_place"] += 1
                elif rank == 4:
                    counters[team]["last_place"] += 1

    rows = []

    for team, data in counters.items():
        rows.append({
            "group": data["group"],
            "team": team,
            "first_place_prob": data["first_place"] / N_SIMULATIONS,
            "second_place_prob": data["second_place"] / N_SIMULATIONS,
            "qualified_prob": data["qualified"] / N_SIMULATIONS,
            "third_place_prob": data["third_place"] / N_SIMULATIONS,
            "last_place_prob": data["last_place"] / N_SIMULATIONS,
            "avg_points": data["total_points"] / N_SIMULATIONS,
            "avg_goal_diff": data["total_gd"] / N_SIMULATIONS,
        })

    result_df = pd.DataFrame(rows)

    result_df = result_df.sort_values(
        by=[
            "group",
            "qualified_prob",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)

    Path("reports").mkdir(parents=True, exist_ok=True)

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 70)
    print("GROUP STAGE MONTE CARLO V2 COMPLETE")
    print("=" * 70)
    print(f"Input file : {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Simulations: {N_SIMULATIONS}")
    print()

    for group in groups:
        print("-" * 70)
        print(f"Group {group}")
        print("-" * 70)

        display_df = result_df[result_df["group"] == group][
            [
                "team",
                "first_place_prob",
                "second_place_prob",
                "qualified_prob",
                "last_place_prob",
                "avg_points",
                "avg_goal_diff",
            ]
        ]

        print(display_df.to_string(index=False))
        print()


if __name__ == "__main__":
    main()