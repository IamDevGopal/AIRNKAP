# Async RAG Architecture (Phase 0 Lock)

## Stack
- API server: FastAPI
- Queue broker: Redis
- Worker runtime: Celery (separate Python process)
- App DB: SQLite (temporary, Postgres-ready design)
- Vector store: Pinecone

## High-level Flow
1. Client uploads document via API.
2. API stores file and document metadata.
3. API enqueues ingestion job in Redis queue.
4. Celery worker processes job:
   - parse -> chunk -> embed -> vector upsert
5. Document status transitions:
   - `queued` -> `processing` -> `ready` or `failed`

## Phase 0 Output
- Environment variables finalized for:
  - broker/worker connectivity
  - upload constraints
  - chunking parameters
  - embedding configuration
  - Pinecone configuration
- Package declarations finalized for:
  - queue + retries
  - document parsing (`pdf`, `docx`, `xlsx`)
  - token chunking
  - vector client

## Notes
- `PINECONE_API_KEY` and legacy `PINECODE_DB_API_KEY` are both supported in settings.
- Celery beat/scheduler is intentionally deferred to later phases.
