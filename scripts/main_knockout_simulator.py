from pathlib import Path
import math
import numpy as np
import pandas as pd


MATCH_PROB_FILE = "reports/worldcup_adjusted_match_probabilities.csv"
OUTPUT_FILE = "reports/champion_probabilities.csv"

N_SIMULATIONS = 10000
RANDOM_SEED = 42


def elo_to_xg(team_elo: float, opponent_elo: float) -> tuple[float, float]:
    """
    Neutral-field Elo to expected goals.
    Used for knockout matchups that did not appear in group fixtures.
    """
    base_total_xg = 2.70
    elo_diff = team_elo - opponent_elo

    strength_ratio = 10 ** (elo_diff / 400)

    team_xg = base_total_xg * strength_ratio / (1 + strength_ratio)
    opponent_xg = base_total_xg / (1 + strength_ratio)

    return round(team_xg, 3), round(opponent_xg, 3)


def build_elo_map(match_df: pd.DataFrame) -> dict:
    elo_map = {}

    for _, row in match_df.iterrows():
        elo_map[row["home_team"]] = row["home_elo"]
        elo_map[row["away_team"]] = row["away_elo"]

    return elo_map


def simulate_group_match(row, rng):
    home_goals = rng.poisson(row["home_xg"])
    away_goals = rng.poisson(row["away_xg"])

    return home_goals, away_goals


def simulate_group_stage(match_df: pd.DataFrame, rng) -> pd.DataFrame:
    teams = sorted(set(match_df["home_team"]) | set(match_df["away_team"]))

    standings = {
        team: {
            "team": team,
            "group": None,
            "points": 0,
            "gf": 0,
            "ga": 0,
            "gd": 0,
        }
        for team in teams
    }

    for _, row in match_df.iterrows():
        group = row["group"]
        home = row["home_team"]
        away = row["away_team"]

        standings[home]["group"] = group
        standings[away]["group"] = group

        home_goals, away_goals = simulate_group_match(row, rng)

        standings[home]["gf"] += home_goals
        standings[home]["ga"] += away_goals
        standings[away]["gf"] += away_goals
        standings[away]["ga"] += home_goals

        if home_goals > away_goals:
            standings[home]["points"] += 3
        elif home_goals < away_goals:
            standings[away]["points"] += 3
        else:
            standings[home]["points"] += 1
            standings[away]["points"] += 1

    rows = []

    for team, data in standings.items():
        data["gd"] = data["gf"] - data["ga"]
        rows.append(data)

    table = pd.DataFrame(rows)

    ranked_groups = []

    for group, group_df in table.groupby("group"):
        group_df = group_df.copy()
        group_df["random_tiebreaker"] = rng.random(len(group_df))

        group_df = group_df.sort_values(
            by=["points", "gd", "gf", "random_tiebreaker"],
            ascending=[False, False, False, False],
        ).reset_index(drop=True)

        group_df["group_rank"] = group_df.index + 1
        ranked_groups.append(group_df)

    ranked_table = pd.concat(ranked_groups, ignore_index=True)

    return ranked_table


def select_round_of_32_teams(ranked_table: pd.DataFrame, rng) -> list[str]:
    """
    2026 format approximation:
    - 12 group winners
    - 12 group runners-up
    - 8 best third-place teams

    Then seed all 32 teams by group-stage performance.
    This is not the official FIFA bracket mapping yet.
    """
    top_two = ranked_table[ranked_table["group_rank"] <= 2].copy()
    third_place = ranked_table[ranked_table["group_rank"] == 3].copy()

    third_place["random_tiebreaker"] = rng.random(len(third_place))

    best_thirds = third_place.sort_values(
        by=["points", "gd", "gf", "random_tiebreaker"],
        ascending=[False, False, False, False],
    ).head(8)

    qualified = pd.concat([top_two, best_thirds], ignore_index=True)

    qualified["random_tiebreaker"] = rng.random(len(qualified))

    qualified = qualified.sort_values(
        by=["points", "gd", "gf", "random_tiebreaker"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    return qualified["team"].tolist()


def simulate_knockout_match(team_a: str, team_b: str, elo_map: dict, rng) -> str:
    elo_a = elo_map[team_a]
    elo_b = elo_map[team_b]

    xg_a, xg_b = elo_to_xg(elo_a, elo_b)

    goals_a = rng.poisson(xg_a)
    goals_b = rng.poisson(xg_b)

    if goals_a > goals_b:
        return team_a

    if goals_b > goals_a:
        return team_b

    # Extra time / penalties approximation
    strength_a = 10 ** (elo_a / 400)
    strength_b = 10 ** (elo_b / 400)

    prob_a = strength_a / (strength_a + strength_b)

    return team_a if rng.random() < prob_a else team_b


def play_round(teams: list[str], elo_map: dict, rng) -> list[str]:
    winners = []

    for i in range(0, len(teams), 2):
        team_a = teams[i]
        team_b = teams[i + 1]

        winner = simulate_knockout_match(
            team_a=team_a,
            team_b=team_b,
            elo_map=elo_map,
            rng=rng,
        )

        winners.append(winner)

    return winners


def build_seeded_bracket(qualified_teams: list[str]) -> list[str]:
    """
    Seeded bracket:
    1 vs 32
    16 vs 17
    8 vs 25
    9 vs 24
    4 vs 29
    13 vs 20
    5 vs 28
    12 vs 21
    2 vs 31
    15 vs 18
    7 vs 26
    10 vs 23
    3 vs 30
    14 vs 19
    6 vs 27
    11 vs 22
    """
    seed_pairs = [
        (1, 32),
        (16, 17),
        (8, 25),
        (9, 24),
        (4, 29),
        (13, 20),
        (5, 28),
        (12, 21),
        (2, 31),
        (15, 18),
        (7, 26),
        (10, 23),
        (3, 30),
        (14, 19),
        (6, 27),
        (11, 22),
    ]

    bracket = []

    for left_seed, right_seed in seed_pairs:
        bracket.append(qualified_teams[left_seed - 1])
        bracket.append(qualified_teams[right_seed - 1])

    return bracket


def main():
    rng = np.random.default_rng(RANDOM_SEED)

    match_df = pd.read_csv(MATCH_PROB_FILE)

    required_cols = {
        "group",
        "home_team",
        "away_team",
        "home_elo",
        "away_elo",
        "home_xg",
        "away_xg",
    }

    missing_cols = required_cols - set(match_df.columns)

    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    elo_map = build_elo_map(match_df)

    teams = sorted(elo_map.keys())

    result_counter = {
        team: {
            "round_of_32": 0,
            "round_of_16": 0,
            "quarterfinal": 0,
            "semifinal": 0,
            "final": 0,
            "champion": 0,
        }
        for team in teams
    }

    for _ in range(N_SIMULATIONS):
        ranked_table = simulate_group_stage(match_df, rng)

        qualified_teams = select_round_of_32_teams(ranked_table, rng)

        for team in qualified_teams:
            result_counter[team]["round_of_32"] += 1

        bracket = build_seeded_bracket(qualified_teams)

        round_of_16 = play_round(bracket, elo_map, rng)
        for team in round_of_16:
            result_counter[team]["round_of_16"] += 1

        quarterfinal = play_round(round_of_16, elo_map, rng)
        for team in quarterfinal:
            result_counter[team]["quarterfinal"] += 1

        semifinal = play_round(quarterfinal, elo_map, rng)
        for team in semifinal:
            result_counter[team]["semifinal"] += 1

        final = play_round(semifinal, elo_map, rng)
        for team in final:
            result_counter[team]["final"] += 1

        champion = play_round(final, elo_map, rng)[0]
        result_counter[champion]["champion"] += 1

    rows = []

    for team, counts in result_counter.items():
        rows.append({
            "team": team,
            "simulations": N_SIMULATIONS,
            "round_of_32_prob": counts["round_of_32"] / N_SIMULATIONS,
            "round_of_16_prob": counts["round_of_16"] / N_SIMULATIONS,
            "quarterfinal_prob": counts["quarterfinal"] / N_SIMULATIONS,
            "semifinal_prob": counts["semifinal"] / N_SIMULATIONS,
            "final_prob": counts["final"] / N_SIMULATIONS,
            "champion_prob": counts["champion"] / N_SIMULATIONS,
        })

    result_df = pd.DataFrame(rows)

    result_df = result_df.sort_values(
        by="champion_prob",
        ascending=False,
    ).reset_index(drop=True)

    Path("reports").mkdir(parents=True, exist_ok=True)

    result_df.to_csv(OUTPUT_FILE, index=False)

    print()
    print("=" * 70)
    print("WORLD CUP CHAMPION MONTE CARLO")
    print("=" * 70)
    print(f"Input file : {MATCH_PROB_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Simulations: {N_SIMULATIONS}")
    print()
    print(result_df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()