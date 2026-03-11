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
|   |   |-- research_task_model.py
|   |   `-- report_model.py
|   |-- schemas/
|   |   |-- auth_schema.py
|   |   |-- user_schema.py
|   |   |-- workspace_schema.py
|   |   |-- project_schema.py
|   |   |-- document_schema.py
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
|   |   `-- background_workers.py
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
