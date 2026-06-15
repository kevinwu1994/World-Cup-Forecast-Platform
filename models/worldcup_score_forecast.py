import math
import pandas as pd


MAX_GOALS = 6


MATCHES = [
    {
        "home_team": "Mexico",
        "away_team": "South Africa",
        "home_odds": 1.42,
        "draw_odds": 4.33,
        "away_odds": 8.27,
        "score_odds": {
            "1-0": 5.50,
            "2-0": 4.75,
            "2-1": 6.00,
            "3-0": 8.00,
            "1-1": 7.25,
            "0-0": 9.50,
        },
    },
    {
        "home_team": "South Korea",
        "away_team": "Czechia",
        "home_odds": 2.66,
        "draw_odds": 3.09,
        "away_odds": 2.79,
        "score_odds": {
            "1-1": 4.70,
            "0-1": 7.25,
            "1-0": 7.00,
            "0-0": 8.00,
            "1-2": 8.50,
            "2-1": 8.00,
        },
    },
    {
        "home_team": "Canada",
        "away_team": "Bosnia",
        "home_odds": 1.81,
        "draw_odds": 3.51,
        "away_odds": 4.56,
        "score_odds": {
            "1-0": 5.70,
            "2-1": 7.00,
            "2-0": 6.50,
            "1-1": 6.20,
            "0-0": 9.50,
            "0-1": 10.50,
        },
    },
    {
        "home_team": "USA",
        "away_team": "Paraguay",
        "home_odds": 1.95,
        "draw_odds": 3.38,
        "away_odds": 4.00,
        "score_odds": {
            "1-0": 6.00,
            "2-1": 7.25,
            "2-0": 8.00,
            "1-1": 5.45,
            "0-0": 8.00,
            "0-1": 8.75,
        },
    },
]


def poisson_pmf(goals: int, lam: float) -> float:
    return math.exp(-lam) * lam**goals / math.factorial(goals)


def normalize_market_probs(home_odds, draw_odds, away_odds):
    raw_home = 1 / home_odds
    raw_draw = 1 / draw_odds
    raw_away = 1 / away_odds

    total = raw_home + raw_draw + raw_away

    return {
        "H": raw_home / total,
        "D": raw_draw / total,
        "A": raw_away / total,
    }


def score_result(score: str) -> str:
    home_goals, away_goals = map(int, score.split("-"))

    if home_goals > away_goals:
        return "H"

    if home_goals < away_goals:
        return "A"

    return "D"


def solve_lambdas_from_market(
    home_prob: float,
    draw_prob: float,
    away_prob: float,
):
    best = None

    for home_lambda in [x / 100 for x in range(40, 351)]:
        for away_lambda in [x / 100 for x in range(20, 301)]:
            probs = result_probs_from_lambdas(
                home_lambda,
                away_lambda,
            )

            error = (
                (probs["H"] - home_prob) ** 2
                + (probs["D"] - draw_prob) ** 2
                + (probs["A"] - away_prob) ** 2
            )

            if best is None or error < best["error"]:
                best = {
                    "home_lambda": home_lambda,
                    "away_lambda": away_lambda,
                    "error": error,
                }

    return best["home_lambda"], best["away_lambda"]


def result_probs_from_lambdas(home_lambda, away_lambda):
    home_win = 0.0
    draw = 0.0
    away_win = 0.0

    for h in range(MAX_GOALS + 1):
        for a in range(MAX_GOALS + 1):
            prob = poisson_pmf(h, home_lambda) * poisson_pmf(a, away_lambda)

            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob

    total = home_win + draw + away_win

    return {
        "H": home_win / total,
        "D": draw / total,
        "A": away_win / total,
    }


def build_score_table(match):
    market_probs = normalize_market_probs(
        match["home_odds"],
        match["draw_odds"],
        match["away_odds"],
    )

    home_lambda, away_lambda = solve_lambdas_from_market(
        home_prob=market_probs["H"],
        draw_prob=market_probs["D"],
        away_prob=market_probs["A"],
    )

    rows = []

    for h in range(MAX_GOALS + 1):
        for a in range(MAX_GOALS + 1):
            score = f"{h}-{a}"
            prob = poisson_pmf(h, home_lambda) * poisson_pmf(a, away_lambda)

            market_score_odds = match["score_odds"].get(score)

            fair_odds = 1 / prob if prob > 0 else None

            edge = None
            value = False

            if market_score_odds:
                edge = market_score_odds / fair_odds - 1
                value = edge > 0.10

            rows.append(
                {
                    "match": f"{match['home_team']} vs {match['away_team']}",
                    "score": score,
                    "result": score_result(score),
                    "model_prob": prob,
                    "fair_odds": fair_odds,
                    "market_score_odds": market_score_odds,
                    "edge": edge,
                    "value": value,
                    "home_lambda": home_lambda,
                    "away_lambda": away_lambda,
                }
            )

    df = pd.DataFrame(rows)

    return df.sort_values(
        "model_prob",
        ascending=False,
    )


def main():
    all_rows = []

    print("\n==============================")
    print("World Cup Correct Score Forecast")
    print("==============================")

    for match in MATCHES:
        table = build_score_table(match)

        print("\n------------------------------")
        print(f"{match['home_team']} vs {match['away_team']}")
        print("------------------------------")

        display_cols = [
            "score",
            "model_prob",
            "fair_odds",
            "market_score_odds",
            "edge",
            "value",
        ]

        show = table[display_cols].head(10).copy()

        show["model_prob"] = show["model_prob"].map(lambda x: f"{x:.2%}")
        show["fair_odds"] = show["fair_odds"].map(lambda x: f"{x:.2f}")
        show["edge"] = show["edge"].map(
            lambda x: "" if pd.isna(x) else f"{x:.2%}"
        )

        print(show.to_string(index=False))

        all_rows.append(table)

    output = pd.concat(
        all_rows,
        ignore_index=True,
    )

    output.to_csv(
        "reports/worldcup_score_forecast.csv",
        index=False,
    )

    print("\nSaved to: reports/worldcup_score_forecast.csv")


if __name__ == "__main__":
    main()