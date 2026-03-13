# Async RAG Architecture (Current: Phase C)

## Stack
- API server: FastAPI
- Queue broker: Redis
- Worker runtime: Celery (separate Python process)
- App DB: SQLite (current), Postgres-ready later
- Vector store: Pinecone
- Embeddings provider: provider-switchable (`openai` default, `azure_openai` supported)

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
- Embedding provider selection:
  - `EMBEDDING_PROVIDER`
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL`
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

## End-to-End Runtime Flow (Code Level)
### 1. Upload request enters FastAPI
- Entry route: `app/api/v1/document_routes.py`
- Route uploaded file ko `document_service` ko hand over karti hai.
- Main business flow file: `app/services/document_service.py`

### 2. File is saved on disk and document row is created
- `document_service` pehle ownership and project scope validate karta hai.
- Uploaded file disk par save hoti hai under `data/raw_documents/...`
- `documents` table me new row create hoti hai through `document_repository`.
- Typical saved fields:
  - `owner_id`
  - `workspace_id`
  - `project_id`
  - `file_name`
  - `file_path`
  - `file_size`
  - `mime_type`
  - `ingestion_status="queued"`
- Database model files involved:
  - `app/models/document_model.py`
  - `app/repositories/document_repository.py`

### 3. Ingestion job is queued
- File save and DB insert ke baad Celery task enqueue hota hai.
- Task trigger file: `app/tasks/document_ingestion_tasks.py`
- Celery app config file: `app/tasks/celery_app.py`
- Queue config settings se aata hai:
  - `CELERY_BROKER_URL`
  - `CELERY_RESULT_BACKEND`
  - `CELERY_INGESTION_QUEUE`
- Actual enqueue pattern:
  - `ingest_document.delay(document_id)`
- Is step par API response complete ho jata hai.
- User ko immediate response milta hai, background processing wait nahi karati.

### 4. Worker queue se job pick karta hai
- Separate worker process command:
  - `celery -A app.tasks.celery_app worker -l info`
- Worker Redis broker se `document_ingestion` queue monitor karta hai.
- Job aate hi `document.ingest` task run hota hai.
- Runtime code:
  - `app/tasks/document_ingestion_tasks.py`

### 5. Worker document ko `processing` mark karta hai
- Worker DB se `document_id` ke basis par row fetch karta hai.
- Repository call:
  - `get_document_by_id(...)`
- Phir document status update hota hai:
  - `ingestion_status="processing"`
  - `ingestion_started_at=<utc time>`
  - `ingestion_error=None`
- Status update repository function:
  - `update_document_ingestion_fields(...)`

### 6. LangChain-based ingestion pipeline starts
- Worker canonical ingestion entrypoint call karta hai:
  - `app/ai/rag/ingestion/ingestion_pipeline.py`
  - function: `build_document_chunks(file_path)`
- Ye function 3 outputs return karta hai:
  - `parsed_text`
  - `chunks`
  - `content_hash`

### 7. LangChain document loading happens
- Loader file:
  - `app/ai/rag/ingestion/loaders.py`
- Main function:
  - `load_documents(file_path)`
- Ye file extension detect karta hai aur LangChain community loaders choose karta hai.
- Used package:
  - `langchain-community`
- Used components:
  - `PyPDFLoader`
  - `Docx2txtLoader`
  - `TextLoader`
  - `CSVLoader`
  - `UnstructuredExcelLoader`
- Import source:
  - `langchain_community.document_loaders`

### 8. Why these loader classes are used
- `PyPDFLoader`
  - PDF file read karta hai aur page content ko LangChain `Document` objects me convert karta hai.
- `Docx2txtLoader`
  - DOCX text extract karta hai.
- `TextLoader`
  - TXT aur JSON text ko raw content ki tarah load karta hai.
- `CSVLoader`
  - CSV rows ko textual documents me convert karta hai.
- `UnstructuredExcelLoader`
  - XLSX spreadsheet content ko textual representation me load karta hai.
- In sab loaders ka output common shape me hota hai:
  - list of LangChain document objects
  - each object usually has `page_content` and `metadata`

### 9. Parsed text is normalized
- `ingestion_pipeline.py` loaded documents se `page_content` join karta hai.
- Final `parsed_text` pure document ka normalized text snapshot hota hai.
- Same `parsed_text` ka SHA-256 hash banaya jata hai:
  - `content_hash`
- Hash reason:
  - same content detect karne ke liye
  - future reindex/version comparisons ke liye

### 10. LangChain text splitting happens
- Splitter file:
  - `app/ai/rag/ingestion/splitters.py`
- Main function:
  - `split_documents(documents)`
- Used package:
  - `langchain-text-splitters`
- Used component:
  - `RecursiveCharacterTextSplitter`
- Constructor style used:
  - `RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)`

### 11. Why this splitter is used
- Ye chunk size aur overlap ko settings-driven banata hai.
- `tiktoken` compatible token estimation use karta hai.
- Important settings:
  - `CHUNK_SIZE_TOKENS`
  - `CHUNK_OVERLAP_TOKENS`
  - `EMBEDDING_MODEL_NAME`
- Split result ko project-specific `TextChunk` dataclass me map kiya jata hai:
  - `chunk_index`
  - `chunk_text`
  - `token_count`

### 12. Chunk rows are stored in metadata DB
- Worker `replace_document_chunks(...)` call karta hai.
- File:
  - `app/repositories/document_repository.py`
- Behavior:
  - same `document_id` ke old chunk rows delete
  - new chunk rows insert
- Table:
  - `document_chunks`
- Why replace strategy:
  - duplicate chunk rows avoid karne ke liye
  - reprocessing me stale chunks remove karne ke liye
  - deterministic current-state storage ke liye

### 13. Embeddings client is created
- Embedding wrapper file:
  - `app/ai/llm/wrappers/embeddings.py`
- Main function:
  - `get_embeddings_client()`
- Used package:
  - `langchain-openai`
- Used components:
  - `OpenAIEmbeddings`
  - `AzureOpenAIEmbeddings`
- Settings used:
  - `EMBEDDING_PROVIDER`
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_API_VERSION`
  - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
  - `EMBEDDING_MODEL_NAME`
  - `EMBEDDING_BATCH_SIZE`
  - `EMBEDDING_REQUEST_TIMEOUT_SECONDS`
  - `EMBEDDING_MAX_RETRIES`

### 14. Why provider-switchable LangChain embeddings are used
- Runtime config `EMBEDDING_PROVIDER` decide karta hai kaunsa wrapper use hoga.
- `openai` path:
  - `OpenAIEmbeddings`
  - direct OpenAI API key based access
- `azure_openai` path:
  - `AzureOpenAIEmbeddings`
  - Azure endpoint + deployment based access
- Is wrapper ke through:
  - auth
  - provider-specific connection details
  - batching
  - retry
  - timeout
  standardized object me mil jate hain.
- Worker khud raw HTTP calls nahi likhta.

### 15. Vector store upsert happens
- Vector indexing file:
  - `app/ai/vectorstore/indexing/upsert.py`
- Main function:
  - `upsert_document_vectors(document, chunks)`
- Used package:
  - `langchain-pinecone`
- Used component:
  - `PineconeVectorStore`
- Flow:
  - embeddings client create hota hai
  - Pinecone vector store object initialize hota hai
  - `add_texts(...)` call hota hai

### 16. What `PineconeVectorStore.add_texts(...)` does
- Input:
  - chunk texts
  - chunk metadata
  - deterministic IDs
- Ye internally:
  - text ke embeddings generate karwa sakta hai using provided embedding client
  - Pinecone index me vectors upsert karta hai
- Stored metadata currently includes:
  - `document_id`
  - `project_id`
  - `workspace_id`
  - `owner_id`
  - `chunk_index`
  - `token_count`
- Vector ID pattern:
  - `doc-{document_id}-chunk-{chunk_index}`

### 17. Why metadata is attached with each vector
- Later retrieval time par filtering possible hoti hai:
  - single document
  - project scoped
  - workspace scoped
- Citation mapping easy hota hai.
- Access control and future query routing stronger hoti hai.

### 18. Final document status update
- Agar chunking + upsert successful hai to worker final DB update karta hai:
  - `ingestion_status="ready"`
  - `ingestion_completed_at=<utc time>`
  - `chunk_count=<number of chunks>`
  - `embedding_model=<configured model name>`
  - `embedding_version=<configured version>`
  - `content_hash=<sha256>`
- Same repository function use hota hai:
  - `update_document_ingestion_fields(...)`

### 19. Failure path
- Worker task level par exception catch hoti hai.
- Document ko mark kiya jata hai:
  - `ingestion_status="failed"`
  - `ingestion_error=<trimmed error text>`
  - `ingestion_completed_at=<utc time>`
- Celery task config me retry policy already attached hai:
  - `autoretry_for`
  - `retry_backoff`
  - `retry_jitter`
  - `max_retries`

### 20. Exact module responsibility summary
- `app/api/v1/document_routes.py`
  - HTTP upload/status/chunks endpoints
- `app/services/document_service.py`
  - file save + business validation + task enqueue
- `app/repositories/document_repository.py`
  - document + chunk table persistence
- `app/tasks/document_ingestion_tasks.py`
  - background orchestration
- `app/ai/rag/ingestion/loaders.py`
  - LangChain document loading
- `app/ai/rag/ingestion/splitters.py`
  - LangChain chunk building
- `app/ai/rag/ingestion/ingestion_pipeline.py`
  - parsed text + chunks + hash assembly
- `app/ai/llm/wrappers/embeddings.py`
  - provider-switchable LangChain embedding client
- `app/ai/vectorstore/indexing/upsert.py`
  - LangChain Pinecone upsert
- `app/ai/rag/ingestion/parser.py`
  - preserved backup custom parser, active runtime path ka part nahi
