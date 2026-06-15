from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
TARGET = ROOT / "web_dashboard" / "public" / "data"

FILES = [
    "worldcup_adjusted_match_probabilities.csv",
    "worldcup_predictions.csv",
    "group_stage_probabilities.csv",
    "champion_probabilities.csv",
    "worldcup_live_scores.csv",
    "prediction_accuracy.csv",
    "model_vs_market.csv",
]


def main():
    TARGET.mkdir(parents=True, exist_ok=True)

    for file in FILES:
        src = REPORTS / file
        dst = TARGET / file

        if src.exists():
            shutil.copy2(src, dst)
            print(f"Copied: {file}")
        else:
            print(f"Missing: {file}")

    print("\nDashboard data sync complete.")


if __name__ == "__main__":
    main()