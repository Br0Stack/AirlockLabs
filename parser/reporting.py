from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

from .anomalies import Anomaly
from .models import NormalizedEvent


def generate_timeline(events: Iterable[NormalizedEvent]) -> List[str]:
    ordered = sorted(events, key=lambda event: event.timestamp)
    lines: List[str] = []
    for event in ordered:
        lines.append(_format_event(event))
    return lines


def generate_report(events: Iterable[NormalizedEvent], anomalies: Iterable[Anomaly]) -> List[str]:
    ordered_events = sorted(events, key=lambda event: event.timestamp)
    ordered_anomalies = list(anomalies)
    lines = [
        "Autopsy Narrative Report",
        "=" * 24,
        "",
        "Executive Summary",
        "-" * 18,
    ]
    if ordered_anomalies:
        lines.append(
            f"{len(ordered_anomalies)} anomalies detected across "
            f"{len(ordered_events)} total events."
        )
    else:
        lines.append("No anomalies detected across the ingested events.")
    lines.extend(
        [
            "",
            "Key Findings",
            "-" * 12,
        ]
    )
    if ordered_anomalies:
        for anomaly in ordered_anomalies:
            lines.append(f"* {anomaly.summary}")
    else:
        lines.append("* No anomalies were detected with the current rule set.")
    lines.extend(
        [
            "",
            "Timeline Excerpts",
            "-" * 17,
        ]
    )
    for event in ordered_events[:15]:
        lines.append(_format_event(event))
    if len(ordered_events) > 15:
        lines.append(f"... {len(ordered_events) - 15} more events not shown.")
    lines.extend(
        [
            "",
            "Corroborating Sources",
            "-" * 21,
        ]
    )
    for event in ordered_events[:10]:
        lines.append(f"- {event.raw_reference.source_file}:{event.raw_reference.line_number}")
    lines.extend(
        [
            "",
            "Appendix",
            "-" * 8,
            "Raw data references are included in the CSV and JSON exports.",
            "",
            "Disclaimer: This report describes observed data and anomalies only.",
            "It does not provide legal conclusions or advice.",
        ]
    )
    return lines


def export_events_csv(events: Iterable[NormalizedEvent], output_path: Path) -> None:
    ordered = sorted(events, key=lambda event: event.timestamp)
    fieldnames = [
        "timestamp",
        "event_type",
        "direction",
        "counterparty",
        "duration_seconds",
        "bytes_used",
        "provider",
        "source_file",
        "line_number",
        "schema_key",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for event in ordered:
            writer.writerow(
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "direction": event.direction,
                    "counterparty": event.counterparty or "",
                    "duration_seconds": event.duration_seconds or "",
                    "bytes_used": event.bytes_used or "",
                    "provider": event.provider,
                    "source_file": event.raw_reference.source_file,
                    "line_number": event.raw_reference.line_number,
                    "schema_key": event.metadata.get("schema_key", ""),
                }
            )


def export_events_json(events: Iterable[NormalizedEvent], output_path: Path) -> None:
    ordered = sorted(events, key=lambda event: event.timestamp)
    payload = [
        _serialize_event(event)
        for event in ordered
    ]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_anomalies_json(anomalies: Iterable[Anomaly], output_path: Path) -> None:
    payload = [asdict(anomaly) for anomaly in anomalies]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_event_cards_json(events: Iterable[NormalizedEvent], output_path: Path) -> None:
    cards = build_event_cards(events)
    output_path.write_text(json.dumps(cards, indent=2), encoding="utf-8")


def generate_unresolved_questions(events: Iterable[NormalizedEvent]) -> List[str]:
    ordered_events = sorted(events, key=lambda event: event.timestamp)
    if not ordered_events:
        return ["No events were ingested. Which files are still missing from the case workspace?"]

    questions: List[str] = []
    unknown_direction = sum(1 for event in ordered_events if event.direction == "unknown")
    if unknown_direction:
        questions.append(
            f"{unknown_direction} events have unknown direction. Which source can confirm who initiated each interaction?"
        )

    missing_counterparty = sum(1 for event in ordered_events if not event.counterparty)
    if missing_counterparty:
        questions.append(
            f"{missing_counterparty} events are missing counterparties. Can additional records identify the other participant?"
        )

    first_timestamp = ordered_events[0].timestamp.strftime("%Y-%m-%d")
    last_timestamp = ordered_events[-1].timestamp.strftime("%Y-%m-%d")
    questions.append(
        f"Timeline currently spans {first_timestamp} to {last_timestamp}. Are there missing exports before or after this window?"
    )
    return questions


def generate_evidence_brief(events: Iterable[NormalizedEvent], anomalies: Iterable[Anomaly]) -> List[str]:
    ordered_events = sorted(events, key=lambda event: event.timestamp)
    ordered_anomalies = list(anomalies)
    lines = [
        "Case Timeline Builder - Evidence Brief",
        "=" * 37,
        "",
        "Event Cards",
        "-" * 11,
    ]
    cards = build_event_cards(ordered_events)
    if cards:
        for card in cards[:20]:
            lines.append(
                f"- [{card['timestamp']}] {card['summary']} "
                f"(confidence={card['confidence']:.2f}, source={card['source_reference']})"
            )
        if len(cards) > 20:
            lines.append(f"... {len(cards) - 20} additional cards not shown.")
    else:
        lines.append("No events available.")

    lines.extend(
        [
            "",
            "Unresolved Questions",
            "-" * 19,
        ]
    )
    for question in generate_unresolved_questions(ordered_events):
        lines.append(f"- {question}")

    lines.extend(
        [
            "",
            "Potential Contradictions / Flags",
            "-" * 32,
        ]
    )
    if ordered_anomalies:
        for anomaly in ordered_anomalies:
            lines.append(f"- {anomaly.summary}")
    else:
        lines.append("- No anomaly flags from the current rule set.")
    return lines


def _format_event(event: NormalizedEvent) -> str:
    timestamp = _format_timestamp(event.timestamp)
    direction = f" ({event.direction})" if event.direction != "unknown" else ""
    counterparty = f" Counterparty: {event.counterparty}." if event.counterparty else ""
    duration = (
        f" Duration: {event.duration_seconds}s."
        if event.duration_seconds is not None
        else ""
    )
    return (
        f"{timestamp} | {event.provider} | {event.event_type}{direction}."
        f"{counterparty}{duration} Source: {event.raw_reference.source_file}"
        f":{event.raw_reference.line_number}"
    )


def _format_timestamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _serialize_event(event: NormalizedEvent) -> dict:
    return {
        "event_type": event.event_type,
        "timestamp": event.timestamp.isoformat(),
        "direction": event.direction,
        "counterparty": event.counterparty,
        "duration_seconds": event.duration_seconds,
        "bytes_used": event.bytes_used,
        "provider": event.provider,
        "raw_reference": {
            "source_file": event.raw_reference.source_file,
            "line_number": event.raw_reference.line_number,
            "raw_line": event.raw_reference.raw_line,
        },
        "metadata": event.metadata,
    }


def build_event_cards(events: Iterable[NormalizedEvent]) -> List[Dict[str, object]]:
    ordered_events = sorted(events, key=lambda event: event.timestamp)
    cards: List[Dict[str, object]] = []
    for index, event in enumerate(ordered_events, start=1):
        confidence = float(event.metadata.get("confidence", 0.5))
        direction = f" ({event.direction})" if event.direction != "unknown" else ""
        counterparty = f" with {event.counterparty}" if event.counterparty else ""
        cards.append(
            {
                "event_id": f"evt-{index:05d}",
                "timestamp": event.timestamp.isoformat(),
                "summary": f"{event.provider} {event.event_type}{direction}{counterparty}",
                "event_type": event.event_type,
                "confidence": max(0.0, min(1.0, confidence)),
                "source_reference": f"{event.raw_reference.source_file}:{event.raw_reference.line_number}",
            }
        )
    return cards
