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
- Phase C.1: framework-centric ingestion path made canonical

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
3. Load document content from disk using LangChain loaders:
   - PDF (`PyPDFLoader`)
   - DOCX (`Docx2txtLoader`)
   - TXT / JSON (`TextLoader`)
   - CSV (`CSVLoader`)
   - XLSX (`UnstructuredExcelLoader`)
4. Build chunks with LangChain text splitter (`RecursiveCharacterTextSplitter`).
5. Replace rows in `document_chunks` for the document.
6. Generate embeddings with LangChain Azure OpenAI wrapper and upsert through LangChain Pinecone adapter.
7. Upsert vectors to Pinecone with metadata:
   - `document_id`, `project_id`, `workspace_id`, `owner_id`
   - `chunk_index`, `token_count`
8. Update document to `ready` with:
   - `chunk_count`
   - `content_hash` (SHA-256 of parsed text)
   - `embedding_model`, `embedding_version`
9. On any failure, set `failed` + persist error message.

## Implemented AI Modules
- `app/ai/rag/ingestion/parser.py`
- `app/ai/rag/ingestion/loaders.py`
- `app/ai/rag/ingestion/splitters.py`
- `app/ai/rag/ingestion/ingestion_pipeline.py`
- `app/ai/llm/clients/azure_openai_client.py`
- `app/ai/llm/wrappers/embeddings.py`
- `app/ai/vectorstore/clients/pinecone_client.py`
- `app/ai/vectorstore/indexing/upsert.py`
- `app/tasks/document_ingestion_tasks.py`

## Runtime Policy
- Active ingestion runtime is framework-centric.
- `parser.py` is preserved only as backup reference and is not used in the current worker path.

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
