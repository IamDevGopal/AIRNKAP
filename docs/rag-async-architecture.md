# Async RAG Architecture (Current: Phase C)

## Stack
- API server: FastAPI
- Queue broker: Redis
- Worker runtime: Celery (separate Python process)
- App DB: SQLite (current), Postgres-ready later
- Vector store: Pinecone
- Embeddings provider: Azure OpenAI

## Implemented Phases
- Phase A: async ingestion skeleton + status polling
- Phase B: parsing + chunking + chunk persistence
- Phase C: embeddings + Pinecone upsert

## Data Model (Implemented)
### `documents` ingestion fields
- `ingestion_status` (`queued|processing|ready|failed`)
- `ingestion_error`
- `ingestion_started_at`
- `ingestion_completed_at`
- `content_hash`
- `chunk_count`
- `embedding_model`
- `embedding_version`

### `document_chunks` table
- `document_id`
- `chunk_index` (deterministic ordering)
- `chunk_text`
- `token_count`

## API Contract (Implemented)
- `POST /api/v1/documents/upload`
  - stores file + creates document
  - enqueues ingestion task
  - returns document with ingestion status (`queued`)
- `GET /api/v1/documents/{id}/status`
  - ingestion lifecycle status polling
- `GET /api/v1/documents/{id}/chunks`
  - chunk inspection endpoint (debug/admin friendly)

## Worker Pipeline
1. Pick job from `document_ingestion` queue.
2. Mark document `processing` with `ingestion_started_at`.
3. Parse file text from disk:
   - PDF (`pypdf`)
   - DOCX (`python-docx`)
   - TXT / JSON / CSV (stdlib)
   - XLSX (`openpyxl`)
4. Chunk text via token-aware chunker (`tiktoken`) using configured size/overlap.
5. Replace rows in `document_chunks` for the document.
6. Generate embeddings via Azure OpenAI wrapper:
   - batching
   - request timeout
   - retry with exponential backoff (`tenacity`)
7. Upsert vectors to Pinecone with metadata:
   - `document_id`, `project_id`, `workspace_id`, `owner_id`
   - `chunk_index`, `token_count`
8. Update document to `ready` with:
   - `chunk_count`
   - `content_hash` (SHA-256 of parsed text)
   - `embedding_model`, `embedding_version`
9. On any failure, set `failed` + persist error message.

## Implemented Service Modules
- `app/services/file_parser_service.py`
- `app/services/chunking_service.py`
- `app/services/embedding_service.py`
- `app/services/vector_index_service.py`
- `app/tasks/document_ingestion_tasks.py`

## Key Environment Variables
- Queue:
  - `REDIS_URL`
  - `CELERY_BROKER_URL`
  - `CELERY_RESULT_BACKEND`
  - `CELERY_INGESTION_QUEUE`
  - `CELERY_INGESTION_MAX_RETRIES`
- Chunking:
  - `CHUNK_SIZE_TOKENS`
  - `CHUNK_OVERLAP_TOKENS`
- Azure embeddings:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_API_VERSION`
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
  - `EMBEDDING_MODEL_NAME`
  - `EMBEDDING_MODEL_VERSION`
  - `EMBEDDING_BATCH_SIZE`
  - `EMBEDDING_REQUEST_TIMEOUT_SECONDS`
  - `EMBEDDING_MAX_RETRIES`
- Pinecone:
  - `PINECONE_API_KEY` (legacy alias `PINECODE_DB_API_KEY` supported)
  - `PINECONE_INDEX_NAME`
  - `PINECONE_NAMESPACE`
  - `PINECONE_UPSERT_BATCH_SIZE`

## Current Scope Boundary
- Implemented: ingestion pipeline up to vector indexing.
- Deferred intentionally:
  - retrieval/query APIs
  - answer generation over retrieved context
  - advanced ops hardening (DLQ, alerts, worker health checks)
