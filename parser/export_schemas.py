from __future__ import annotations

from .models import ValidationError
from .telecom_schemas import CsvSchema


def google_voice_schema(schema_key: str) -> CsvSchema:
    if schema_key == "google_voice_calls":
        return CsvSchema(
            key="google_voice_calls",
            provider="Google Voice",
            record_type="call",
            required_columns=["Date", "Time", "Direction", "From", "To", "Duration (sec)"],
            column_map={
                "date": "Date",
                "time": "Time",
                "direction": "Direction",
                "counterparty": "From",
                "event_type": "Direction",
                "duration_seconds": "Duration (sec)",
            },
            direction_map={
                "incoming": "inbound",
                "outgoing": "outbound",
            },
            notes="Google Voice call log export.",
        )
    if schema_key == "google_voice_messages":
        return CsvSchema(
            key="google_voice_messages",
            provider="Google Voice",
            record_type="sms",
            required_columns=["Date", "Time", "Type", "From", "To"],
            column_map={
                "date": "Date",
                "time": "Time",
                "direction": "Type",
                "counterparty": "From",
                "event_type": "Type",
            },
            direction_map={
                "received": "inbound",
                "sent": "outbound",
            },
            notes="Google Voice messages export.",
        )
    raise ValidationError(f"Unknown Google Voice schema key: {schema_key}")


def apple_schema(schema_key: str) -> CsvSchema:
    if schema_key == "apple_calls":
        return CsvSchema(
            key="apple_calls",
            provider="Apple",
            record_type="call",
            required_columns=["Date", "Time", "Direction", "Contact", "Duration (sec)"],
            column_map={
                "date": "Date",
                "time": "Time",
                "direction": "Direction",
                "counterparty": "Contact",
                "event_type": "Direction",
                "duration_seconds": "Duration (sec)",
            },
            direction_map={
                "incoming": "inbound",
                "outgoing": "outbound",
                "missed": "unknown",
            },
            notes="Apple calls export.",
        )
    if schema_key == "apple_messages":
        return CsvSchema(
            key="apple_messages",
            provider="Apple",
            record_type="sms",
            required_columns=["Date", "Time", "Direction", "Contact", "Message"],
            column_map={
                "date": "Date",
                "time": "Time",
                "direction": "Direction",
                "counterparty": "Contact",
                "event_type": "Direction",
            },
            direction_map={
                "incoming": "inbound",
                "outgoing": "outbound",
            },
            notes="Apple messages export.",
        )
    raise ValidationError(f"Unknown Apple export schema key: {schema_key}")
