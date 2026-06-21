from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.data_processing import process_tickets
from app.metrics import build_summary_metrics

INPUT_PATH = ROOT_DIR / "tickets.csv"
OUTPUT_PATH = ROOT_DIR / "processed_tickets.csv"


def main() -> None:
    df = process_tickets(INPUT_PATH)
    df.to_csv(OUTPUT_PATH, index=False)

    metrics = build_summary_metrics(df)
    print(f"Processed tickets: {metrics['total_tickets']}")
    print(f"Open tickets: {metrics['open_tickets']}")
    print(f"High/Critical tickets: {metrics['high_critical_tickets']}")
    print(f"Invalid resolution times: {metrics['invalid_resolution_time_tickets']}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
