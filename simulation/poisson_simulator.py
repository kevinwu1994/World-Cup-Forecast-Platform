import numpy as np


class PoissonSimulator:

    def __init__(self, random_seed=42):

        np.random.seed(random_seed)

    def simulate_match(
        self,
        home_xg,
        away_xg
    ):

        home_goals = np.random.poisson(home_xg)

        away_goals = np.random.poisson(away_xg)

        return home_goals, away_goals