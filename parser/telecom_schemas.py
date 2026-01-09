from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class CsvSchema:
    key: str
    provider: str
    record_type: str
    required_columns: List[str]
    column_map: Dict[str, str]
    direction_map: Dict[str, str]
    notes: str


TELECOM_CSV_SCHEMAS: List[CsvSchema] = [
    CsvSchema(
        key="verizon_usage_v1",
        provider="Verizon",
        record_type="call",
        required_columns=[
            "Date",
            "Time",
            "Direction",
            "Number",
            "Type",
            "Duration (min)",
        ],
        column_map={
            "date": "Date",
            "time": "Time",
            "direction": "Direction",
            "counterparty": "Number",
            "event_type": "Type",
            "duration_minutes": "Duration (min)",
        },
        direction_map={
            "incoming": "inbound",
            "outgoing": "outbound",
        },
        notes=(
            "Expected Date as YYYY-MM-DD, Time as HH:MM:SS, and Duration in minutes. "
            "Type should be 'Call' or 'Text'."
        ),
    ),
    CsvSchema(
        key="att_wireless_usage_v1",
        provider="AT&T",
        record_type="call",
        required_columns=[
            "Date",
            "Time",
            "Direction",
            "Number",
            "Usage Type",
            "Duration (seconds)",
        ],
        column_map={
            "date": "Date",
            "time": "Time",
            "direction": "Direction",
            "counterparty": "Number",
            "event_type": "Usage Type",
            "duration_seconds": "Duration (seconds)",
        },
        direction_map={
            "received": "inbound",
            "placed": "outbound",
        },
        notes=(
            "Expected Date as YYYY-MM-DD, Time as HH:MM:SS, "
            "Duration in seconds, and Usage Type of 'Voice' or 'SMS'."
        ),
    ),
]
