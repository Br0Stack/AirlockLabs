from __future__ import annotations

import argparse
import tempfile
import zipfile
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

    takeout_path = Path(args.google_takeout)
    with _prepare_takeout_root(takeout_path) as root_dir:
        events = parse_google_takeout(root_dir)
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
        help="Path to the root folder containing the Takeout directory, or a Takeout .zip file.",
    )
    parser.add_argument(
        "--output-dir",
        default="autopsy-output",
        help="Directory to write timeline, report, and exports.",
    )
    return parser.parse_args()


class _TakeoutRoot:
    def __init__(self, path: Path, temp_dir: tempfile.TemporaryDirectory[str] | None) -> None:
        self.path = path
        self._temp_dir = temp_dir

    def __enter__(self) -> Path:
        return self.path

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self._temp_dir is not None:
            self._temp_dir.cleanup()


def _prepare_takeout_root(takeout_path: Path) -> _TakeoutRoot:
    if takeout_path.is_dir():
        return _TakeoutRoot(takeout_path, None)
    if takeout_path.is_file() and takeout_path.suffix.lower() == ".zip":
        temp_dir = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(takeout_path, "r") as zip_handle:
            zip_handle.extractall(temp_dir.name)
        return _TakeoutRoot(Path(temp_dir.name), temp_dir)
    raise ValueError(
        "Google Takeout path must be a directory or a .zip file."
    )


if __name__ == "__main__":
    main()
