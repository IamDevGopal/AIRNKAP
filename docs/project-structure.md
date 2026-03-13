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
|   |   |-- knowledge_schema.py
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
|   |   |-- knowledge_service.py
|   |   |-- research_task_service.py
|   |   `-- research_service.py
|   |-- ai/
|   |   |-- llm/
|   |   |   |-- clients/
|   |   |   |   `-- __init__.py
|   |   |   `-- wrappers/
|   |   |       |-- embeddings.py
|   |   |       `-- chat.py
|   |   |-- rag/
|   |   |   |-- rag_pipeline.py
|   |   |   |-- ingestion/
|   |   |   |   |-- parser.py
|   |   |   |   |-- loaders.py
|   |   |   |   |-- splitters.py
|   |   |   |   `-- pipeline.py
|   |   |   `-- retrieval/
|   |   |       |-- retriever.py
|   |   |       |-- context_builder.py
|   |   |       `-- pipeline.py
|   |   |-- vectorstore/
|   |   |   |-- clients/
|   |   |   |   `-- pinecone_client.py
|   |   |   |-- indexing/
|   |   |   |   `-- upsert.py
|   |   |   `-- retrieval/
|   |   |       `-- search.py
|   |   |-- agents/
|   |   |   |-- orchestrator/agent_manager.py
|   |   |   |-- research_agent/agent.py
|   |   |   |-- summarizer_agent/agent.py
|   |   |   |-- knowledge_agent/agent.py
|   |   |   `-- report_agent/agent.py
|   |   `-- mcp/
|   |       |-- fastmcp_server.py
|   |       `-- tools_registry.py
|   |-- tasks/
|   |   |-- async_jobs.py
|   |   |-- background_workers.py
|   |   |-- celery_app.py
|   |   `-- document_ingestion_tasks.py
|   `-- utils/
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

## Structure Governance

1. `api/`
- HTTP layer only.
- Request parsing, response mapping, dependency wiring.

2. `services/`
- Domain and business orchestration only.
- AI clients, vector operations, chunking, embedding wrappers yahan nahi.

3. `repositories/`
- DB access only.
- No LLM, vectorstore, prompt, or RAG orchestration.

4. `models/`
- ORM entities and relations only.

5. `schemas/`
- Pydantic request/response contracts only.

6. `app/ai/llm/`
- Provider clients and model wrappers.
- Example: Azure OpenAI embeddings, future chat/completions.

7. `app/ai/rag/`
- Retrieval and ingestion orchestration.
- Active ingestion path LangChain loaders/splitters use karti hai.
- `parser.py` sirf fallback reference ke liye preserved hai.

8. `app/ai/vectorstore/`
- Vector DB specific clients and operations.
- Upsert, search, metadata filters.

9. `app/ai/agents/`
- Multi-agent workflow layer.
- Research, summarization, reporting orchestration.

10. `app/ai/mcp/`
- MCP tool server and tool registry.

11. `tasks/`
- Background execution entrypoints.
- Workers orchestrate `app/ai/*` + repositories/services.

12. `utils/`
- Generic stateless helpers only.

## Golden Runtime Flow

1. API flow:
`api -> services -> repositories/models`

2. Ingestion flow:
`api upload -> task enqueue -> tasks -> app/ai/rag -> app/ai/llm + app/ai/vectorstore -> repositories`

3. Query flow:
`api query -> services -> app/ai/rag(retrieval/context) -> app/ai/llm -> response`

## Prompt and Script Ownership

1. `prompts/`
- Reusable prompt source of truth.
- Runtime prompt text random files me hardcode nahi karna.

2. `scripts/`
- Operational and one-off utilities only.
- Runtime API business logic scripts me nahi jayegi.

## Placement Matrix

1. Azure/OpenAI HTTP call code -> `app/ai/llm/`
2. Embedding/chat wrappers -> `app/ai/llm/`
3. File parsing and chunking for ingestion -> `app/ai/rag/ingestion/`
4. Retrieval and context packing -> `app/ai/rag/retrieval/`
5. Pinecone upsert/search/filter logic -> `app/ai/vectorstore/`
6. Workspace/project/document policy checks -> `app/services/`
7. DB transaction/query code -> `app/repositories/`
8. Background job entrypoints -> `app/tasks/`

## Anti-Patterns

1. Same logic ka duplicate wrapper multiple folders me.
2. `services/` me provider-specific HTTP client code.
3. `app/ai/rag/` me direct SQL/ORM query writing.
4. `repositories/` me LLM or vectorstore calls.
5. Prompt strings ko multiple random files me hardcode karna.
