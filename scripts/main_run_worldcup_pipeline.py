import subprocess
import sys
from pathlib import Path

import pandas as pd


PIPELINE_STEPS = [

    "main_fetch_worldcup_scores.py",

    "main_worldcup_predict.py",

    "main_fetch_worldcup_odds.py",

    "main_market_adjusted_predictions.py",

    "main_prediction_accuracy.py",

    "main_group_montecarlo.py",

    "main_knockout_simulator.py",
]


EXPECTED_FILES = {
    "reports/worldcup_match_probabilities.csv": 72,
    "reports/worldcup_adjusted_match_probabilities.csv": 72,
    "reports/worldcup_predictions.csv": 720,
    "reports/group_stage_probabilities.csv": 48,
    "reports/champion_probabilities.csv": 48,
}


def run_script(script_name: str) -> None:
    print()
    print("=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script_name],
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Pipeline stopped. Failed at: {script_name}")

    print(f"COMPLETED: {script_name}")


def check_output_files() -> None:
    print()
    print("=" * 70)
    print("CHECKING OUTPUT FILES")
    print("=" * 70)

    all_good = True

    for file_path, expected_rows in EXPECTED_FILES.items():
        path = Path(file_path)

        if not path.exists():
            print(f"[MISSING] {file_path}")
            all_good = False
            continue

        df = pd.read_csv(path)
        actual_rows = len(df)

        if actual_rows != expected_rows:
            print(
                f"[WARNING] {file_path}: "
                f"{actual_rows} rows, expected {expected_rows}"
            )
            all_good = False
        else:
            print(f"[OK] {file_path}: {actual_rows} rows")

    if not all_good:
        raise RuntimeError("Pipeline completed, but output check failed.")

    print()
    print("ALL OUTPUT FILES PASSED.")


def main() -> None:
    print()
    print("=" * 70)
    print("WORLD CUP FULL PIPELINE START")
    print("=" * 70)

    for script in PIPELINE_STEPS:
        if not Path(script).exists():
            raise FileNotFoundError(f"Missing script: {script}")

        run_script(script)

    check_output_files()

    print()
    print("=" * 70)
    print("WORLD CUP FULL PIPELINE COMPLETE")
    print("=" * 70)
    print("Final output:")
    print("reports/champion_probabilities.csv")


if __name__ == "__main__":
    main()