from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Workspace(Base):
    __tablename__ = 'workspaces'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    documents: Mapped[List['Document']] = relationship(back_populates='workspace', cascade='all, delete-orphan')
    events: Mapped[List['Event']] = relationship(back_populates='workspace', cascade='all, delete-orphan')
    chat_messages: Mapped[List['ChatMessage']] = relationship(back_populates='workspace', cascade='all, delete-orphan')


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspaces.id'), index=True)
    filename: Mapped[str]
    file_type: Mapped[str]
    path: Mapped[str]
    raw_text: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    workspace: Mapped[Workspace] = relationship(back_populates='documents')
    events: Mapped[List['Event']] = relationship(back_populates='document', cascade='all, delete-orphan')


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspaces.id'), index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'), index=True)
    title: Mapped[str]
    description: Mapped[str]
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    source_excerpt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    workspace: Mapped[Workspace] = relationship(back_populates='events')
    document: Mapped[Document] = relationship(back_populates='events')

    @property
    def source(self) -> str:
        return self.document.filename if self.document else f'document:{self.document_id}'


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey('workspaces.id'), index=True)
    role: Mapped[str]
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    workspace: Mapped[Workspace] = relationship(back_populates='chat_messages')
