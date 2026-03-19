from pathlib import Path

from fastapi.testclient import TestClient

from threadline_api.db import Base, engine
from threadline_api.main import app

client = TestClient(app)


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db_file = Path('apps/api/.data/threadline.db')
    db_file.parent.mkdir(parents=True, exist_ok=True)


def test_full_mvp_flow() -> None:
    reset_db()

    create_workspace = client.post('/workspaces', json={'name': 'Case One', 'description': 'MVP flow'})
    assert create_workspace.status_code == 200
    workspace = create_workspace.json()
    workspace_id = workspace['id']

    get_workspaces = client.get('/workspaces')
    assert get_workspaces.status_code == 200
    assert len(get_workspaces.json()) == 1

    upload = client.post(
        f'/workspaces/{workspace_id}/documents',
        files={'file': ('timeline.txt', b'2026-03-10 Court filing was submitted', 'text/plain')},
    )
    assert upload.status_code == 200

    extract = client.post(f'/workspaces/{workspace_id}/extract-events')
    assert extract.status_code == 200
    assert extract.json()['created'] >= 1

    events = client.get(f'/workspaces/{workspace_id}/events')
    assert events.status_code == 200
    payload = events.json()
    assert payload
    assert payload[0]['title']
    assert payload[0]['description'].startswith('Observed in source text:')
    assert payload[0]['source'] == 'timeline.txt'
    assert payload[0]['source_excerpt']

    chat = client.post(f'/workspaces/{workspace_id}/chat', json={'content': 'What happened first?'})
    assert chat.status_code == 200
    answer = chat.json()['assistant_message']['content']
    assert 'Based on current evidence' in answer or "don't see events" in answer
