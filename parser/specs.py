from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ExportFileSpec:
    label: str
    relative_path: str
    description: str


GOOGLE_TAKEOUT_FILES: List[ExportFileSpec] = [
    ExportFileSpec(
        label="google_voice_calls",
        relative_path="Takeout/Google Voice/Calls.csv",
        description="Google Voice call log export from Google Takeout.",
    ),
    ExportFileSpec(
        label="google_voice_messages",
        relative_path="Takeout/Google Voice/Texts.csv",
        description="Google Voice SMS/MMS log export from Google Takeout.",
    ),
]

APPLE_EXPORT_FILES: List[ExportFileSpec] = [
    ExportFileSpec(
        label="apple_calls",
        relative_path="Apple Messages/Calls.csv",
        description="Calls export from privacy.apple.com data download.",
    ),
    ExportFileSpec(
        label="apple_messages",
        relative_path="Apple Messages/Messages.csv",
        description="Messages export from privacy.apple.com data download.",
    ),
]

EXPORT_FILE_LOOKUP: Dict[str, ExportFileSpec] = {
    spec.label: spec for spec in GOOGLE_TAKEOUT_FILES + APPLE_EXPORT_FILES
}
