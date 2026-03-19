from __future__ import annotations

import csv
import io
from pathlib import Path


def extract_text_from_bytes(filename: str, payload: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {'.txt', '.md'}:
        return payload.decode('utf-8', errors='ignore')
    if suffix == '.csv':
        decoded = payload.decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(decoded))
        return '\n'.join(' | '.join(row) for row in reader)
    if suffix == '.pdf':
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            return payload.decode('utf-8', errors='ignore')

        reader = PdfReader(io.BytesIO(payload))
        extracted = []
        for page in reader.pages:
            extracted.append(page.extract_text() or '')
        return '\n'.join(extracted)

    return payload.decode('utf-8', errors='ignore')
