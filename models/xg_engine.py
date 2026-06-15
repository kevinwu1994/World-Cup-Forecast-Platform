class XGEngine:

    def __init__(self):
        pass

    def elo_to_xg(
        self,
        home_elo,
        away_elo
    ):

        elo_diff = home_elo - away_elo

        home_xg = 1.35 + elo_diff / 350

        away_xg = 1.35 - elo_diff / 350

        home_xg = max(0.40, min(3.50, home_xg))
        away_xg = max(0.40, min(3.50, away_xg))

        return round(home_xg, 3), round(away_xg, 3)