from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .export_schemas import apple_schema, google_voice_schema
from .models import NormalizedEvent, RawReference, ValidationError
from .specs import APPLE_EXPORT_FILES, GOOGLE_TAKEOUT_FILES
from .telecom_schemas import CsvSchema, TELECOM_CSV_SCHEMAS
from .validation import (
    validate_apple_export,
    validate_google_takeout,
    validate_telecom_csv,
)


def parse_google_takeout(root_dir: str | Path) -> List[NormalizedEvent]:
    root_path = Path(root_dir)
    validate_google_takeout(root_path)

    events: List[NormalizedEvent] = []
    for spec in GOOGLE_TAKEOUT_FILES:
        file_path = root_path / spec.relative_path
        schema_key = "google_voice_calls" if "Calls" in spec.relative_path else "google_voice_messages"
        events.extend(_parse_google_voice_csv(file_path, schema_key))
    return events


def parse_apple_export(root_dir: str | Path) -> List[NormalizedEvent]:
    root_path = Path(root_dir)
    validate_apple_export(root_path)

    events: List[NormalizedEvent] = []
    for spec in APPLE_EXPORT_FILES:
        file_path = root_path / spec.relative_path
        schema_key = "apple_calls" if "Calls" in spec.relative_path else "apple_messages"
        events.extend(_parse_apple_csv(file_path, schema_key))
    return events


def parse_telecom_csv(file_path: str | Path, schema_key: str) -> List[NormalizedEvent]:
    schema = _get_telecom_schema(schema_key)
    file_path = Path(file_path)
    validate_telecom_csv(file_path, schema)
    return list(_parse_telecom_rows(file_path, schema))


def _get_telecom_schema(schema_key: str) -> CsvSchema:
    for schema in TELECOM_CSV_SCHEMAS:
        if schema.key == schema_key:
            return schema
    raise ValidationError(f"Unknown telecom schema key: {schema_key}")


def _parse_google_voice_csv(file_path: Path, schema_key: str) -> Iterable[NormalizedEvent]:
    schema = google_voice_schema(schema_key)
    yield from _parse_generic_csv(file_path, schema)


def _parse_apple_csv(file_path: Path, schema_key: str) -> Iterable[NormalizedEvent]:
    schema = apple_schema(schema_key)
    yield from _parse_generic_csv(file_path, schema)


def _parse_telecom_rows(file_path: Path, schema: CsvSchema) -> Iterable[NormalizedEvent]:
    yield from _parse_generic_csv(file_path, schema)


def _parse_generic_csv(file_path: Path, schema: CsvSchema) -> Iterable[NormalizedEvent]:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    reader = csv.DictReader(lines)
    for index, row in enumerate(reader, start=2):
        raw_line = lines[index - 1]
        yield _normalize_row(file_path, index, raw_line, row, schema)


def _normalize_row(
    file_path: Path,
    line_number: int,
    raw_line: str,
    row: Dict[str, str],
    schema: CsvSchema,
) -> NormalizedEvent:
    timestamp = _parse_timestamp(
        row.get(schema.column_map.get("date", ""), ""),
        row.get(schema.column_map.get("time", ""), ""),
    )
    event_type = _normalize_event_type(row.get(schema.column_map.get("event_type", ""), ""))
    direction = _normalize_direction(row.get(schema.column_map.get("direction", ""), ""), schema)
    duration_seconds = _parse_duration(row, schema)

    return NormalizedEvent(
        event_type=event_type,
        timestamp=timestamp,
        direction=direction,
        counterparty=row.get(schema.column_map.get("counterparty", "")) or None,
        duration_seconds=duration_seconds,
        bytes_used=_parse_bytes(row, schema),
        provider=schema.provider,
        raw_reference=RawReference(
            source_file=str(file_path),
            line_number=line_number,
            raw_line=raw_line,
        ),
        metadata={
            "record_type": schema.record_type,
            "schema_key": schema.key,
        },
    )


def _parse_timestamp(date_value: str, time_value: str) -> datetime:
    if not date_value:
        raise ValidationError("Missing date value for record")
    if time_value:
        combined = f"{date_value} {time_value}"
        return datetime.strptime(combined, "%Y-%m-%d %H:%M:%S")
    return datetime.strptime(date_value, "%Y-%m-%d")


def _normalize_event_type(raw_value: str) -> str:
    lowered = raw_value.strip().lower()
    if lowered in {"call", "voice"}:
        return "call"
    if lowered in {"text", "sms", "mms"}:
        return "sms"
    if lowered in {"data"}:
        return "data"
    return "unknown"


def _normalize_direction(raw_value: str, schema: CsvSchema) -> str:
    lowered = raw_value.strip().lower()
    for key, value in schema.direction_map.items():
        if lowered == key:
            return value
    if lowered in {"in", "incoming", "received"}:
        return "inbound"
    if lowered in {"out", "outgoing", "sent", "placed"}:
        return "outbound"
    return "unknown"


def _parse_duration(row: Dict[str, str], schema: CsvSchema) -> Optional[int]:
    if "duration_seconds" in schema.column_map:
        return _int_or_none(row.get(schema.column_map["duration_seconds"], ""))
    if "duration_minutes" in schema.column_map:
        minutes = _int_or_none(row.get(schema.column_map["duration_minutes"], ""))
        return minutes * 60 if minutes is not None else None
    return None


def _parse_bytes(row: Dict[str, str], schema: CsvSchema) -> Optional[int]:
    if "bytes" not in schema.column_map:
        return None
    return _int_or_none(row.get(schema.column_map["bytes"], ""))


def _int_or_none(value: str) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

