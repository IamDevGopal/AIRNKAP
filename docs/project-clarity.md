# Project Clarity: Purpose, Flow, and Next Build Steps

## 1) Project Ka Core Purpose

Ye project sirf APIs banane ke liye nahi hai. Iska real goal hai:

- raw uploaded documents ko searchable knowledge base me convert karna
- us knowledge ke basis par grounded AI answers/reports dena
- user ko workspace/project based research workflow provide karna

Short formula:

`Raw Docs -> Structured Knowledge -> Grounded AI Outputs`

---

## 2) End-to-End Product Flow (User Perspective)

1. User sign up/login karta hai.
2. User workspace create karta hai.
3. Workspace ke andar project create karta hai.
4. Project me documents upload karta hai.
5. System async ingestion run karta hai:
   - parse
   - chunk
   - embeddings
   - Pinecone upsert
6. User query/research task run karta hai.
7. System relevant context retrieve karke answer/report generate karta hai.

---

## 3) Abhi Tak Kya Complete Hua Hai

Implemented and working:

1. Auth + user basics
2. Workspace CRUD
3. Project CRUD
4. Document upload
5. Async RAG ingestion pipeline:
   - file parsing
   - token chunking
   - embedding generation
   - vector indexing (Pinecone)
   - ingestion status tracking (`queued -> processing -> ready/failed`)
6. Polling APIs:
   - document status
   - document chunks

Meaning:
- "Knowledge banana" wala major foundation complete hai.

---

## 4) Ab Next Kya Banana Hai Aur Kyu

Current ingestion ke baad next value-delivering phase:

1. Retrieval API
- Kya: query pe top-k relevant chunks lana
- Kyu: indexed vectors ko user query me use karna

2. RAG Answer API (chat/query)
- Kya: retrieved context + LLM se grounded answer
- Kyu: user-facing intelligence yahi hai

3. Citation/Source Mapping
- Kya: answer ke saath source chunks/pages dena
- Kyu: trust, auditability, professional UX

4. Research Task Execution
- Kya: structured tasks (summary, comparison, risk analysis, etc.)
- Kyu: chatbot se product workflow tak jump

5. Report Generation
- Kya: task outputs ko saved/exportable reports me convert karna
- Kyu: real business/research deliverable

---

## 5) Structure Ka Clear Mental Model

### Runtime responsibilities

1. `app/api/`
- HTTP routes/endpoints

2. `app/services/`
- business orchestration layer

3. `app/ai/rag/`
- retrieval/context pipeline logic

4. `app/ai/llm/`
- model/provider communication (Azure OpenAI, prompts, wrappers)

5. `app/ai/vectorstore/`
- vector DB operations (upsert/query)

6. `app/ai/agents/` + `app/ai/mcp/`
- AI orchestration and tool integration layers

7. `app/tasks/`
- background async jobs (Celery workers)

8. `app/repositories/` + `app/models/`
- persistence/data access

### Two primary system loops

1. Ingestion loop
`upload -> task queue -> parse/chunk/embed/index`

2. Query loop
`user query -> retrieve -> context build -> LLM answer -> response`

---

## 6) Why This Clarity Matters

Jab purpose clear hota hai to folder layout aur implementation decisions naturally clear hote hain:

- kaunsa code ingestion side ka hai
- kaunsa code query side ka hai
- kaunsa module future placeholder hai
- kaunsa module immediate build priority hai

Isi se development fast, consistent, aur low-confusion hota hai.

---

## 7) User-Facing Next Modules and APIs

### A) Knowledge Query Module

Use case:
- document-specific ya project-wide knowledge queries

Proposed APIs:
- `POST /api/v1/knowledge/query`
- `POST /api/v1/knowledge/query/document`
- `POST /api/v1/knowledge/query/project`

### B) Chat Module

Use case:
- conversational research over project knowledge base

Proposed APIs:
- `POST /api/v1/research/chat`
- `GET /api/v1/research/chat/sessions`
- `GET /api/v1/research/chat/sessions/{session_id}`
- `DELETE /api/v1/research/chat/sessions/{session_id}`

### C) Research Task Module

Use case:
- structured tasks (summary, comparison, risk extraction, etc.)

Proposed APIs:
- `POST /api/v1/research-tasks`
- `GET /api/v1/research-tasks`
- `GET /api/v1/research-tasks/{task_id}`
- `POST /api/v1/research-tasks/{task_id}/run`
- `POST /api/v1/research-tasks/{task_id}/cancel`

### D) Report Module

Use case:
- generated outputs ko report artifacts me save/export karna

Proposed APIs:
- `POST /api/v1/reports/generate`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{report_id}`
- `DELETE /api/v1/reports/{report_id}`

### E) Knowledge Operations Module

Use case:
- reindex/reprocess lifecycle operations

Proposed APIs:
- `POST /api/v1/documents/{id}/reindex`
- `POST /api/v1/projects/{id}/reindex`
- `GET /api/v1/documents/{id}/status` (already implemented)
- `GET /api/v1/documents/{id}/chunks` (already implemented)

### F) Automation Module (Later Phase)

Use case:
- workflow scheduling/event-triggered execution

Proposed APIs:
- `POST /api/v1/automation/workflows`
- `GET /api/v1/automation/workflows`
- `POST /api/v1/automation/workflows/{id}/run`
- `POST /api/v1/automation/workflows/{id}/pause`
