from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .export_schemas import apple_schema, google_voice_schema
from .models import ValidationError
from .specs import APPLE_EXPORT_FILES, GOOGLE_TAKEOUT_FILES
from .telecom_schemas import CsvSchema


def validate_google_takeout(root_dir: Path) -> None:
    missing = _missing_export_files(root_dir, GOOGLE_TAKEOUT_FILES)
    if missing:
        raise ValidationError("Missing Google Takeout files", missing)

    for spec in GOOGLE_TAKEOUT_FILES:
        schema = google_voice_schema(spec.label)
        _validate_csv_header(root_dir / spec.relative_path, schema.required_columns)


def validate_apple_export(root_dir: Path) -> None:
    missing = _missing_export_files(root_dir, APPLE_EXPORT_FILES)
    if missing:
        raise ValidationError("Missing Apple export files", missing)

    for spec in APPLE_EXPORT_FILES:
        schema = apple_schema(spec.label)
        _validate_csv_header(root_dir / spec.relative_path, schema.required_columns)


def validate_telecom_csv(file_path: Path, schema: CsvSchema) -> None:
    if not file_path.exists():
        raise ValidationError(f"Telecom CSV not found: {file_path}")

    header = _read_header(file_path)
    missing_columns = [column for column in schema.required_columns if column not in header]
    if missing_columns:
        raise ValidationError(
            f"Missing required columns for {schema.key}",
            [f"Missing column: {column}" for column in missing_columns],
        )


def _missing_export_files(root_dir: Path, specs: Iterable) -> List[str]:
    missing = []
    for spec in specs:
        file_path = root_dir / spec.relative_path
        if not file_path.exists():
            missing.append(spec.relative_path)
    return missing


def _validate_csv_header(file_path: Path, required_columns: List[str]) -> None:
    if not file_path.exists():
        raise ValidationError(f"Missing file: {file_path}")
    header = _read_header(file_path)
    missing_columns = [column for column in required_columns if column not in header]
    if missing_columns:
        raise ValidationError(
            f"Missing required columns for {file_path.name}",
            [f"Missing column: {column}" for column in missing_columns],
        )


def _read_header(file_path: Path) -> List[str]:
    with file_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return next(reader)
        except StopIteration as exc:
            raise ValidationError(f"Empty CSV file: {file_path}") from exc
