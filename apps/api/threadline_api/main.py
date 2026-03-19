from __future__ import annotations

from datetime import timezone
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from . import models, schemas
from .services.ai import MockEventExtractionService, MockQAService
from .services.text_extraction import extract_text_from_bytes

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Threadline API', version='0.1.0')

UPLOAD_ROOT = Path('apps/api/.data/uploads')
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

extractor = MockEventExtractionService()
qa_service = MockQAService()


@app.post('/workspaces', response_model=schemas.WorkspaceRead)
def create_workspace(payload: schemas.WorkspaceCreate, db: Session = Depends(get_db)):
    workspace = models.Workspace(name=payload.name, description=payload.description)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@app.get('/workspaces', response_model=list[schemas.WorkspaceRead])
def list_workspaces(db: Session = Depends(get_db)):
    return db.query(models.Workspace).order_by(models.Workspace.created_at.desc()).all()


@app.get('/workspaces/{workspace_id}', response_model=schemas.WorkspaceRead)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail='Workspace not found')
    return workspace


@app.post('/workspaces/{workspace_id}/documents', response_model=schemas.DocumentRead)
async def upload_document(workspace_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    workspace = db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail='Workspace not found')

    payload = await file.read()
    text = extract_text_from_bytes(file.filename or 'upload.bin', payload)
    filename = file.filename or 'upload.bin'
    workspace_dir = UPLOAD_ROOT / str(workspace_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)
    saved_path = workspace_dir / filename
    saved_path.write_bytes(payload)

    document = models.Document(
        workspace_id=workspace_id,
        filename=filename,
        file_type=file.content_type or 'application/octet-stream',
        path=str(saved_path),
        raw_text=text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@app.get('/workspaces/{workspace_id}/documents', response_model=list[schemas.DocumentRead])
def list_documents(workspace_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Document)
        .filter(models.Document.workspace_id == workspace_id)
        .order_by(models.Document.uploaded_at.desc())
        .all()
    )


@app.post('/workspaces/{workspace_id}/extract-events', response_model=schemas.ExtractEventsResponse)
def extract_events(workspace_id: int, db: Session = Depends(get_db)):
    documents = db.query(models.Document).filter(models.Document.workspace_id == workspace_id).all()
    if not documents:
        raise HTTPException(status_code=400, detail='No documents uploaded')

    created_events: list[models.Event] = []
    for document in documents:
        extracted = extractor.extract_events(document.raw_text)
        for candidate in extracted:
            event = models.Event(
                workspace_id=workspace_id,
                document_id=document.id,
                title=candidate.title,
                description=candidate.description,
                event_date=candidate.event_date,
                confidence_score=candidate.confidence_score,
                source_excerpt=candidate.source_excerpt,
            )
            db.add(event)
            created_events.append(event)

    db.commit()
    for event in created_events:
        db.refresh(event)

    return schemas.ExtractEventsResponse(created=len(created_events), events=created_events)


@app.get('/workspaces/{workspace_id}/events', response_model=list[schemas.EventRead])
def list_events(workspace_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(models.Event)
        .filter(models.Event.workspace_id == workspace_id)
        .order_by(models.Event.event_date.asc().nulls_last(), models.Event.created_at.asc())
        .all()
    )
    return events


@app.patch('/events/{event_id}', response_model=schemas.EventRead)
def update_event(event_id: int, payload: schemas.EventUpdate, db: Session = Depends(get_db)):
    event = db.get(models.Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event


@app.post('/workspaces/{workspace_id}/chat', response_model=schemas.ChatResponse)
def workspace_chat(workspace_id: int, payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    workspace = db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail='Workspace not found')

    user_msg = models.ChatMessage(workspace_id=workspace_id, role='user', content=payload.content)
    db.add(user_msg)
    db.flush()

    answer = qa_service.answer(db, workspace_id, payload.content)
    assistant_msg = models.ChatMessage(workspace_id=workspace_id, role='assistant', content=answer)
    db.add(assistant_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    return schemas.ChatResponse(user_message=user_msg, assistant_message=assistant_msg)
