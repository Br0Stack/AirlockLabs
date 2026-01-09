from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RawReference:
    source_file: str
    line_number: int
    raw_line: str


@dataclass(frozen=True)
class NormalizedEvent:
    event_type: str
    timestamp: datetime
    direction: str
    counterparty: Optional[str]
    duration_seconds: Optional[int]
    bytes_used: Optional[int]
    provider: str
    raw_reference: RawReference
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationError(ValueError):
    def __init__(self, message: str, issues: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.issues = issues or []
