# Threadline Monorepo Apps

## Structure
- `apps/api`: FastAPI + SQLAlchemy + SQLite backend
- `apps/web`: Svelte + TypeScript + Vite frontend

## MVP flow implemented
1. Create workspace
2. Upload documents
3. Extract candidate events (mock AI service)
4. View chronological timeline and source excerpts
5. Chat against workspace evidence (mock Q&A service)

## Run backend
```bash
pip install -r apps/api/requirements.txt
uvicorn threadline_api.main:app --reload --app-dir apps/api
```

## Run frontend
```bash
cd apps/web
npm install
npm run dev
```
