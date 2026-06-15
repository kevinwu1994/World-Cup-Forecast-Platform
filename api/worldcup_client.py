from pathlib import Path

import pandas as pd


class WorldCupClient:
    """
    World Cup data client.

    Current version:
    - Reads manual CSV files.

    Future version:
    - Can be upgraded to fetch live fixtures, results, odds, standings.
    """

    def __init__(
        self,
        teams_file: str = "data/manual/teams.csv",
        groups_file: str = "data/manual/worldcup_groups.csv",
        fixtures_file: str = "data/manual/worldcup_fixtures.csv",
    ):
        self.teams_file = teams_file
        self.groups_file = groups_file
        self.fixtures_file = fixtures_file

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