from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None


class WorkspaceRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentRead(BaseModel):
    id: int
    workspace_id: int
    filename: str
    file_type: str
    path: str
    raw_text: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class EventRead(BaseModel):
    id: int
    workspace_id: int
    document_id: int
    title: str
    description: str
    event_date: datetime | None
    confidence_score: float
    source_excerpt: str
    created_at: datetime

    class Config:
        from_attributes = True


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_date: datetime | None = None
    confidence_score: float | None = None
    source_excerpt: str | None = None


class ExtractEventsResponse(BaseModel):
    created: int
    events: list[EventRead]


class ChatRequest(BaseModel):
    content: str


class ChatMessageRead(BaseModel):
    id: int
    workspace_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
