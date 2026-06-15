import math


def implied_probability(odds):
    return 1 / odds


def normalize_probs(home_odds, draw_odds, away_odds):

    home = implied_probability(home_odds)
    draw = implied_probability(draw_odds)
    away = implied_probability(away_odds)

    total = home + draw + away

    return {
        "home": home / total,
        "draw": draw / total,
        "away": away / total,
    }


def elo_adjustment(home_elo, away_elo):

    elo_diff = home_elo - away_elo

    expected_home = 1 / (1 + math.pow(10, -elo_diff / 400))

    return expected_home


def predict_match(
    home_team,
    away_team,
    home_elo,
    away_elo,
    home_odds,
    draw_odds,
    away_odds,
):

    market = normalize_probs(
        home_odds,
        draw_odds,
        away_odds,
    )

    elo_home = elo_adjustment(
        home_elo,
        away_elo,
    )

    home_prob = (
        market["home"] * 0.7
        + elo_home * 0.3
    )

    away_prob = (
        market["away"] * 0.7
        + (1 - elo_home) * 0.3
    )

    draw_prob = market["draw"]

    total = (
        home_prob
        + draw_prob
        + away_prob
    )

    home_prob /= total
    draw_prob /= total
    away_prob /= total

    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_prob": round(home_prob, 4),
        "draw_prob": round(draw_prob, 4),
        "away_prob": round(away_prob, 4),
    }