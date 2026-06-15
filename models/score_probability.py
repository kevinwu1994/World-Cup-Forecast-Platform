import math
import pandas as pd


class ScoreProbability:

    def poisson_prob(
        self,
        goals,
        lam
    ):
        return (
            math.exp(-lam)
            * lam**goals
            / math.factorial(goals)
        )

    def score_matrix(
        self,
        home_xg,
        away_xg,
        max_goals=6
    ):

        rows = []

        for hg in range(max_goals + 1):

            for ag in range(max_goals + 1):

                prob = (
                    self.poisson_prob(hg, home_xg)
                    * self.poisson_prob(ag, away_xg)
                )

                rows.append(
                    {
                        "score": f"{hg}-{ag}",
                        "home_goals": hg,
                        "away_goals": ag,
                        "probability": prob
                    }
                )

        df = pd.DataFrame(rows)

        df = df.sort_values(
            "probability",
            ascending=False
        )

        return df.reset_index(drop=True)