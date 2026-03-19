from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from sqlalchemy.orm import Session

from .. import models

DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


@dataclass
class ExtractedEvent:
    title: str
    description: str
    event_date: datetime | None
    source_excerpt: str
    confidence_score: float


class EventExtractionService(Protocol):
    def extract_events(self, text: str) -> list[ExtractedEvent]:
        ...


class SummaryService(Protocol):
    def summarize_workspace(self, db: Session, workspace_id: int) -> str:
        ...


class QAService(Protocol):
    def answer(self, db: Session, workspace_id: int, question: str) -> str:
        ...


class MockEventExtractionService:
    def extract_events(self, text: str) -> list[ExtractedEvent]:
        events: list[ExtractedEvent] = []
        for line in [row.strip() for row in text.splitlines() if row.strip()]:
            normalized_line = ' '.join(line.split())
            date_match = DATE_PATTERN.search(line)
            event_date = None
            if date_match:
                event_date = datetime.fromisoformat(date_match.group(1)).replace(tzinfo=timezone.utc)

            if len(normalized_line) < 12:
                continue
            title = build_title(normalized_line)
            events.append(
                ExtractedEvent(
                    title=title,
                    description=build_grounded_description(normalized_line),
                    event_date=event_date,
                    source_excerpt=normalized_line[:240],
                    confidence_score=0.72 if event_date else 0.55,
                )
            )

        return events[:40]


class MockSummaryService:
    def summarize_workspace(self, db: Session, workspace_id: int) -> str:
        event_count = db.query(models.Event).filter(models.Event.workspace_id == workspace_id).count()
        doc_count = db.query(models.Document).filter(models.Document.workspace_id == workspace_id).count()
        return f"Workspace has {doc_count} documents and {event_count} extracted events."


class MockQAService:
    def answer(self, db: Session, workspace_id: int, question: str) -> str:
        events = (
            db.query(models.Event)
            .filter(models.Event.workspace_id == workspace_id)
            .order_by(models.Event.event_date.asc().nulls_last())
            .limit(3)
            .all()
        )
        if not events:
            return "I don't see events yet. Upload documents and run extraction first."

        snippets = '; '.join(
            f"{event.event_date.date() if event.event_date else 'undated'}: {event.title}"
            for event in events
        )
        return f"Based on current evidence, here are relevant events: {snippets}. Question: {question}"


def build_title(text_line: str) -> str:
    clipped = text_line[:72].strip()
    if ':' in clipped:
        return clipped.split(':', maxsplit=1)[0][:72].strip() or clipped
    return clipped


def build_grounded_description(text_line: str) -> str:
    """
    Keep descriptions factual and source-grounded by only reusing source text.
    No speculation or inferred intent is added here.
    """
    return f"Observed in source text: {text_line[:280]}"
