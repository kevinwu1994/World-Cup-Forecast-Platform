import math


def poisson_probability(k, lam):
    """
    Poisson PMF
    """
    return (
        math.exp(-lam)
        * (lam ** k)
        / math.factorial(k)
    )


def score_matrix(
    home_xg,
    away_xg,
    max_goals=6,
):
    """
    Generate score probability matrix
    """

    results = []

    for home_goals in range(max_goals + 1):

        home_prob = poisson_probability(
            home_goals,
            home_xg,
        )

        for away_goals in range(max_goals + 1):

            away_prob = poisson_probability(
                away_goals,
                away_xg,
            )

            prob = home_prob * away_prob

            results.append(
                {
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "probability": prob,
                }
            )

    return results