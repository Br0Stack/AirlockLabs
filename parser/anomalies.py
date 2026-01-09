from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List

from .models import NormalizedEvent


@dataclass(frozen=True)
class Anomaly:
    anomaly_type: str
    summary: str
    why_unusual: str
    why_matters: str
    evidence: List[str]


def detect_anomalies(events: Iterable[NormalizedEvent]) -> List[Anomaly]:
    ordered = sorted(events, key=lambda event: event.timestamp)
    anomalies: List[Anomaly] = []
    anomalies.extend(_detect_nighttime_activity(ordered))
    anomalies.extend(_detect_activity_bursts(ordered))
    anomalies.extend(_detect_large_gaps(ordered))
    return anomalies


def _detect_nighttime_activity(events: List[NormalizedEvent]) -> List[Anomaly]:
    nighttime_events = [event for event in events if event.timestamp.hour < 5]
    if len(nighttime_events) < 3:
        return []
    evidence = [event.raw_reference.raw_line for event in nighttime_events[:5]]
    return [
        Anomaly(
            anomaly_type="nighttime_activity",
            summary=(
                f"{len(nighttime_events)} events occurred between 12:00 AM and 4:59 AM."
            ),
            why_unusual=(
                "Activity clustered overnight can indicate automated access or unexpected usage."
            ),
            why_matters=(
                "If this timeframe is outside normal behavior, it may warrant a closer review."
            ),
            evidence=evidence,
        )
    ]


def _detect_activity_bursts(events: List[NormalizedEvent]) -> List[Anomaly]:
    window = timedelta(minutes=10)
    anomalies: List[Anomaly] = []
    start = 0
    for end, event in enumerate(events):
        while events[start].timestamp < event.timestamp - window:
            start += 1
        window_events = events[start : end + 1]
        if len(window_events) >= 8:
            evidence = [item.raw_reference.raw_line for item in window_events[:5]]
            anomalies.append(
                Anomaly(
                    anomaly_type="activity_burst",
                    summary=(
                        f"{len(window_events)} events occurred within 10 minutes on "
                        f"{event.timestamp.strftime('%Y-%m-%d')}."
                    ),
                    why_unusual=(
                        "Dense bursts of activity can indicate automated behavior or rapid" 
                        "account use."
                    ),
                    why_matters=(
                        "Sudden spikes may help pinpoint suspicious activity windows."
                    ),
                    evidence=evidence,
                )
            )
    return anomalies


def _detect_large_gaps(events: List[NormalizedEvent]) -> List[Anomaly]:
    if len(events) < 2:
        return []
    anomalies: List[Anomaly] = []
    for previous, current in zip(events, events[1:]):
        gap = current.timestamp - previous.timestamp
        if gap >= timedelta(days=7):
            anomalies.append(
                Anomaly(
                    anomaly_type="activity_gap",
                    summary=(
                        f"No events recorded between {previous.timestamp:%Y-%m-%d} and "
                        f"{current.timestamp:%Y-%m-%d} ({gap.days} days)."
                    ),
                    why_unusual=(
                        "Gaps can indicate missing data, disabled services, or periods" 
                        "of inactivity."
                    ),
                    why_matters=(
                        "Missing periods may hide other relevant events or confirm a timeline."
                    ),
                    evidence=[
                        previous.raw_reference.raw_line,
                        current.raw_reference.raw_line,
                    ],
                )
            )
    return anomalies
