# AI Research & Knowledge Automation Platform

## Professional Project Structure

```text
ai-research-platform/
|-- app/
|   |-- main.py
|   |-- api/
|   |   |-- router.py
|   |   `-- v1/
|   |       |-- auth_routes.py
|   |       |-- user_routes.py
|   |       |-- workspace_routes.py
|   |       |-- project_routes.py
|   |       |-- document_routes.py
|   |       |-- research_task_routes.py
|   |       |-- research_routes.py
|   |       |-- knowledge_routes.py
|   |       |-- agent_routes.py
|   |       `-- health_routes.py
|   |-- config/
|   |   |-- settings.py
|   |   `-- logging.py
|   |-- core/
|   |   `-- exceptions/
|   |       |-- handlers.py
|   |       `-- register.py
|   |-- middlewares/
|   |   |-- rate_limit.py
|   |   `-- security_headers.py
|   |-- auth/
|   |   |-- jwt_handler.py
|   |   |-- password_utils.py
|   |   `-- dependencies.py
|   |-- database/
|   |   |-- connection.py
|   |   |-- migrations/
|   |   |   |-- env.py
|   |   |   |-- script.py.mako
|   |   |   `-- versions/
|   |   |-- duckdb/
|   |   |   `-- analytics_db.py
|   |   `-- sqlite/
|   |       `-- metadata_db.py
|   |-- models/
|   |   |-- user_model.py
|   |   |-- workspace_model.py
|   |   |-- project_model.py
|   |   |-- document_model.py
|   |   |-- document_chunk_model.py
|   |   |-- research_task_model.py
|   |   `-- report_model.py
|   |-- schemas/
|   |   |-- auth_schema.py
|   |   |-- user_schema.py
|   |   |-- workspace_schema.py
|   |   |-- project_schema.py
|   |   |-- document_schema.py
|   |   |-- document_ingestion_schema.py
|   |   |-- research_task_schema.py
|   |   |-- research_schema.py
|   |   |-- agent_schema.py
|   |   `-- response_schema.py
|   |-- repositories/
|   |   |-- user_repository.py
|   |   |-- workspace_repository.py
|   |   |-- project_repository.py
|   |   |-- document_repository.py
|   |   |-- research_repository.py
|   |   `-- report_repository.py
|   |-- services/
|   |   |-- auth_service.py
|   |   |-- user_service.py
|   |   |-- workspace_service.py
|   |   |-- project_service.py
|   |   |-- document_service.py
|   |   |-- research_task_service.py
|   |   |-- research_service.py
|   |   |-- rag_service.py
|   |   |-- embedding_service.py
|   |   |-- vector_index_service.py
|   |   |-- chunking_service.py
|   |   `-- llm_service.py
|   |-- agents/
|   |   |-- orchestrator/agent_manager.py
|   |   |-- research_agent/agent.py
|   |   |-- summarizer_agent/agent.py
|   |   |-- knowledge_agent/agent.py
|   |   `-- report_agent/agent.py
|   |-- llm/
|   |   |-- azure_openai_client.py
|   |   |-- embeddings.py
|   |   `-- prompt_templates.py
|   |-- rag/
|   |   |-- pipeline.py
|   |   |-- retriever.py
|   |   `-- context_builder.py
|   |-- vectorstore/
|   |   |-- vector_client.py
|   |   `-- indexing.py
|   |-- mcp/
|   |   |-- fastmcp_server.py
|   |   `-- tools_registry.py
|   |-- tasks/
|   |   |-- async_jobs.py
|   |   |-- background_workers.py
|   |   |-- celery_app.py
|   |   `-- document_ingestion_tasks.py
|   `-- utils/
|       |-- text_processing.py
|       |-- chunking.py
|       `-- helpers.py
|-- data/
|   |-- raw_documents/
|   |-- processed_chunks/
|   |-- embeddings/
|   `-- sqlite/
|-- prompts/
|   |-- research_prompts/
|   |-- summarization_prompts/
|   `-- reasoning_prompts/
|-- scripts/
|   |-- ingest_documents.py
|   |-- generate_embeddings.py
|   `-- run_research_pipeline.py
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- agent_tests/
|-- deployment/
|   |-- docker/
|   |   |-- Dockerfile
|   |   `-- docker-compose.yml
|   |-- kubernetes/
|   |   |-- backend-deployment.yaml
|   |   `-- service.yaml
|   `-- ci-cd/
|       `-- github-actions.yml
|-- docs/
|   |-- architecture.md
|   |-- agent_design.md
|   |-- rag_pipeline.md
|   |-- rag-async-architecture.md
|   |-- project-clarity.md
|   |-- project-structure.md
|   |-- project-flow.md
|   |-- project-phases.md
|   `-- objectives-tech-classification.md
|-- alembic.ini
|-- .env
|-- .env.example
|-- .gitignore
|-- .pre-commit-config.yaml
|-- README.md
|-- SETUP.md
|-- pyproject.toml
|-- requirements.txt
`-- requirements-dev.txt
```

## Structure Governance (Must Follow)

Is section ka purpose hai decide karna ki code exactly kis module me jayega.

### 1) Layer Ownership Rules

1. `api/`
- Only HTTP layer (request parsing, response mapping, dependency wiring).
- Business logic yahan nahi.

2. `services/`
- Domain/business orchestration only (auth, users, workspace, project, documents, tasks, reports).
- Generic technical utilities ka duplicate wrapper yahan nahi banana.

3. `repositories/`
- DB read/write queries only.
- No prompt/model/vector/LLM calls.

4. `models/`
- ORM entities and relations only.

5. `schemas/`
- Request/response contracts only (Pydantic models).

6. `llm/`
- Model provider clients and wrappers only (Azure/OpenAI chat/embeddings).
- No business workflow orchestration.

7. `vectorstore/`
- Vector DB specific client/query/indexing operations only.
- No prompt/model routing/business task logic.

8. `rag/`
- Retrieval + context building + RAG orchestration.
- Calls `llm/` and `vectorstore/`, but provider-specific internals hold nahi karega.

9. `tasks/`
- Background execution entrypoints (Celery jobs).
- Pipeline steps invoke `rag/llm/vectorstore/repositories/services` as needed.

10. `utils/`
- Pure reusable helpers (stateless/generic utilities).
- Domain-specific orchestration yahan nahi.

11. `agents/`
- Multi-agent orchestration (later phases), not base ingestion pipeline.

12. `mcp/`
- Tool server + tool registry integration for agent/tool invocation (later phases).

### 2) Golden Runtime Flow

1. API flow:
`api -> services -> repositories/models`

2. Ingestion async flow:
`api upload -> task enqueue -> tasks -> rag -> llm + vectorstore -> repositories`

3. Query flow:
`api query -> services -> rag(retriever/context) -> llm -> response`

### 3) Prompt and Script Ownership

1. `prompts/`
- Reusable prompt source of truth.
- Prompt text hardcode karne ke bajay yahan maintain karo.

2. `scripts/`
- Operational utilities only (backfill, one-off reindex, batch jobs).
- Runtime API business logic scripts me place mat karo.

## Placement Matrix (Quick Decision Guide)

1. Azure/OpenAI HTTP request code -> `app/llm/`
2. Pinecone upsert/query/filter code -> `app/vectorstore/`
3. Retrieve + context pack + answer orchestration -> `app/rag/`
4. Workspace/project/document policy checks -> `app/services/`
5. DB transaction/query code -> `app/repositories/`
6. File parsing/chunk/token helpers -> `app/utils/` (or `rag/` if pipeline-specific)
7. Async worker entrypoint -> `app/tasks/`

## Anti-Patterns (Avoid)

1. Same logic ka duplicate wrapper multiple folders me.
2. `services/` me provider-specific HTTP client code rakhna.
3. `rag/` me direct SQL/ORM query writing.
4. `repositories/` me LLM or vectorstore calls.
5. Prompt strings ko random files me hardcode karna.

## Recommended Canonical Sub-Layout (Evolution)

Current tree valid hai, lekin growth ke liye ye canonical split follow karein:

1. `app/llm/`
- `clients/` (provider clients)
- `wrappers/` (chat/embeddings wrappers)
- `router/` (optional model selection)

2. `app/vectorstore/`
- `clients/`
- `indexing/`
- `retrieval/`

3. `app/rag/`
- `pipeline.py`
- `retriever.py`
- `context_builder.py`
- `prompt_loader.py` (load from root `prompts/`)

Note:
- Ye evolution stepwise hona chahiye; unnecessary early over-engineering avoid karein.
