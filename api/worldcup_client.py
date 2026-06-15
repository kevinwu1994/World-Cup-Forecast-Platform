from pathlib import Path
import pandas as pd


class WorldCupClient:
    """
    World Cup data client.

    Priority:
    1. Use live API scores/fixtures from reports/worldcup_live_scores.csv
    2. Filter live fixtures to teams that exist in data/manual/teams.csv
    3. Fall back to manual fixtures if live file is missing or unusable
    """

    def __init__(
        self,
        teams_file: str = "data/manual/teams.csv",
        groups_file: str = "data/manual/worldcup_groups.csv",
        fixtures_file: str = "data/manual/worldcup_fixtures.csv",
        live_scores_file: str = "reports/worldcup_live_scores.csv",
    ):
        self.teams_file = teams_file
        self.groups_file = groups_file
        self.fixtures_file = fixtures_file
        self.live_scores_file = live_scores_file

    def _read_csv_checked(self, path: str) -> pd.DataFrame:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        return pd.read_csv(file_path)

    def get_teams(self) -> pd.DataFrame:
        return self._read_csv_checked(self.teams_file)

    def get_groups(self) -> pd.DataFrame:
        return self._read_csv_checked(self.groups_file)

    def get_fixtures(self) -> pd.DataFrame:
        live_path = Path(self.live_scores_file)

        if live_path.exists():
            live_df = pd.read_csv(live_path)

            if not live_df.empty:
                live_df = live_df.copy()

                if "completed" in live_df.columns:
                    live_df = live_df[live_df["completed"] != True]

                required_cols = {
                    "event_id",
                    "commence_time",
                    "home_team",
                    "away_team",
                }

                if required_cols.issubset(set(live_df.columns)):
                    teams_df = self.get_teams()
                    valid_teams = set(teams_df["team"].astype(str))

                    live_df = live_df[
                        live_df["home_team"].astype(str).isin(valid_teams)
                        & live_df["away_team"].astype(str).isin(valid_teams)
                    ]

                    if not live_df.empty:
                        fixtures = live_df[
                            [
                                "event_id",
                                "commence_time",
                                "home_team",
                                "away_team",
                            ]
                        ].copy()

                        fixtures = fixtures.rename(
                            columns={
                                "event_id": "match_id",
                                "commence_time": "date",
                            }
                        )

                        fixtures["group"] = "-"

                        fixtures = fixtures.drop_duplicates(
                            subset=["home_team", "away_team"],
                            keep="last",
                        )

                        fixtures = fixtures.sort_values("date")

                        if not fixtures.empty:
                            return fixtures

        return self._read_csv_checked(self.fixtures_file)

    def get_team_info(self, team_name: str) -> pd.Series:
        teams = self.get_teams()

        matched = teams[teams["team"] == team_name]

        if matched.empty:
            raise ValueError(f"Team not found in teams.csv: {team_name}")

        return matched.iloc[0]


if __name__ == "__main__":
    client = WorldCupClient()

    print("\nTeams")
    print(client.get_teams().head().to_string(index=False))

    print("\nGroups")
    print(client.get_groups().head().to_string(index=False))

    print("\nFixtures")
    print(client.get_fixtures().head().to_string(index=False))

    print("\nWorldCupClient check completed.")