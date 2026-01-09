from __future__ import annotations

import argparse
from pathlib import Path

from parser import parse_google_takeout
from parser.anomalies import detect_anomalies
from parser.reporting import (
    export_anomalies_json,
    export_events_csv,
    export_events_json,
    generate_report,
    generate_timeline,
)


def main() -> None:
    args = _parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    events = parse_google_takeout(args.google_takeout)
    anomalies = detect_anomalies(events)

    timeline_lines = generate_timeline(events)
    report_lines = generate_report(events, anomalies)

    (output_dir / "timeline.txt").write_text("\n".join(timeline_lines), encoding="utf-8")
    (output_dir / "report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    export_events_csv(events, output_dir / "events.csv")
    export_events_json(events, output_dir / "events.json")
    export_anomalies_json(anomalies, output_dir / "anomalies.json")

    print(f"Wrote timeline, report, and exports to {output_dir}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autopsy MVP CLI")
    parser.add_argument(
        "--google-takeout",
        required=True,
        help="Path to the root folder containing the Takeout directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="autopsy-output",
        help="Directory to write timeline, report, and exports.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
