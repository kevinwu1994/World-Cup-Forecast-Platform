def probabilities_to_xg(
    home_prob,
    draw_prob,
    away_prob,
):
    """
    Convert 1X2 probabilities into expected goals.

    This is a simple first version:
    - Stronger favorite gets higher xG
    - Draw-heavy matches get lower total goals
    """

    strength_gap = home_prob - away_prob

    total_goals = 2.45

    if draw_prob > 0.28:
        total_goals -= 0.25

    if draw_prob < 0.20:
        total_goals += 0.15

    home_xg = total_goals / 2 + strength_gap * 1.15
    away_xg = total_goals / 2 - strength_gap * 1.15

    home_xg = max(0.25, min(home_xg, 4.50))
    away_xg = max(0.25, min(away_xg, 4.50))

    return round(home_xg, 3), round(away_xg, 3)