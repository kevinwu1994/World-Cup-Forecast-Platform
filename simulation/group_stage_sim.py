import pandas as pd


class GroupStageSimulator:

    def __init__(self):

        self.table = {}

    def initialize_group(self, teams):

        standings = {}

        for team in teams:

            standings[team] = {
                "pts": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0
            }

        return standings

    def update_result(
        self,
        standings,
        home_team,
        away_team,
        home_goals,
        away_goals
    ):

        standings[home_team]["gf"] += home_goals
        standings[home_team]["ga"] += away_goals

        standings[away_team]["gf"] += away_goals
        standings[away_team]["ga"] += home_goals

        standings[home_team]["gd"] = (
            standings[home_team]["gf"]
            - standings[home_team]["ga"]
        )

        standings[away_team]["gd"] = (
            standings[away_team]["gf"]
            - standings[away_team]["ga"]
        )

        if home_goals > away_goals:

            standings[home_team]["pts"] += 3

        elif home_goals < away_goals:

            standings[away_team]["pts"] += 3

        else:

            standings[home_team]["pts"] += 1
            standings[away_team]["pts"] += 1

    def get_rankings(self, standings):

        rows = []

        for team, stats in standings.items():

            rows.append(
                {
                    "team": team,
                    **stats
                }
            )

        df = pd.DataFrame(rows)

        df = df.sort_values(
            by=["pts", "gd", "gf"],
            ascending=False
        )

        return df.reset_index(drop=True)