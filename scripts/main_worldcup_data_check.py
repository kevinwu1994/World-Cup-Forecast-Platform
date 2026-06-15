from pathlib import Path

import pandas as pd


TEAMS_FILE = "data/manual/teams.csv"
GROUPS_FILE = "data/manual/worldcup_groups.csv"
FIXTURES_FILE = "data/manual/worldcup_fixtures.csv"


def read_csv_checked(path: str) -> pd.DataFrame:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    return pd.read_csv(file_path)


def main() -> None:
    teams = read_csv_checked(TEAMS_FILE)
    groups = read_csv_checked(GROUPS_FILE)
    fixtures = read_csv_checked(FIXTURES_FILE)

    print("\n======================")
    print("World Cup V2 Data Check")
    print("======================")

    print("\nTeams:")
    print(teams.head(20).to_string(index=False))
    print(f"Total teams: {len(teams)}")

    print("\nGroups:")
    print(groups.to_string(index=False))
    print(f"Total group rows: {len(groups)}")

    print("\nFixtures:")
    print(fixtures.to_string(index=False))
    print(f"Total fixtures: {len(fixtures)}")

    missing_teams = []

    known_teams = set(teams["team"])

    for team in groups["team"]:
        if team not in known_teams:
            missing_teams.append(team)

    for _, row in fixtures.iterrows():
        if row["home_team"] not in known_teams:
            missing_teams.append(row["home_team"])
        if row["away_team"] not in known_teams:
            missing_teams.append(row["away_team"])

    missing_teams = sorted(set(missing_teams))

    if missing_teams:
        print("\nMissing teams in teams.csv:")
        for team in missing_teams:
            print(f"- {team}")
        raise ValueError("Some teams are missing from teams.csv")

    print("\nData check passed.")


if __name__ == "__main__":
    main()