# Project Clarity: Purpose, Systems, and Consumer Flow

## 1. Core Product Purpose

Ye project sirf document upload ya chatbot nahi hai.

Iska real product goal hai:

- raw uploaded documents ko structured searchable knowledge base me convert karna
- us prepared knowledge ko multiple product systems me reuse karna
- grounded AI outputs dena:
  - answers
  - research outputs
  - reports
  - agent workflows
  - automation outputs

Short formula:

`Raw Documents -> Prepared Knowledge Base -> Retrieval/Context System -> Product Outputs`

---

## 2. Current Product Status

Abhi tak jo major system complete hua hai wo hai:

### A. Knowledge Preparation System

Ye system documents ko AI-ready banata hai.

Current implemented flow:

1. user document upload karta hai
2. file disk par save hoti hai
3. metadata `documents` table me save hoti hai
4. Celery job queue me add hoti hai
5. worker job pick karta hai
6. LangChain loader document load karta hai
7. LangChain splitter chunks banata hai
8. chunk rows `document_chunks` table me save hoti hain
9. embedding client chunks ko vectors me convert karta hai
10. vectors Pinecone me upsert hoti hain
11. document `ready` mark hota hai

Meaning:

- knowledge base prepare ho chuka hai
- knowledge query aur session-aware chat ka base implementation bhi aa chuka hai
- research task lifecycle ka base implementation bhi aa chuka hai
- remaining higher-level consumers abhi next phase me hain

---

## 3. Two Main Systems of the Product

Is project ko samajhne ka best tareeka ye hai ki ise do major systems me dekho:

### System 1: Knowledge Preparation System

Purpose:
- uploaded knowledge ko ready karna

Main responsibilities:
- upload
- parsing/loading
- chunking
- embeddings
- vector indexing
- ingestion status tracking

Main runtime flow:

`upload -> save -> queue -> worker -> load -> split -> embed -> index -> ready`

Main modules:
- `app/api/v1/document_routes.py`
- `app/services/document_service.py`
- `app/tasks/document_ingestion_tasks.py`
- `app/ai/rag/ingestion/`
- `app/ai/llm/wrappers/embeddings.py`
- `app/ai/vectorstore/indexing/upsert.py`
- `app/repositories/document_repository.py`

### System 2: Knowledge Usage System

Purpose:
- prepared knowledge base ko actual user features me use karna

Main responsibilities:
- retrieval
- filtering by scope
- context building
- citation/source mapping
- context ko downstream modules ko dena

Main runtime flow:

`question/task/workflow input -> retrieve -> build context -> consumer module -> result`

Yahi next major system hai jo abhi build hona baaki hai.

---

## 4. Retrieval System Ka Exact Role

Retrieval system ko simplest tareeke se samjho:

- prepared knowledge base ka consumer-facing access layer
- ye khud final product output nahi hai
- ye baaki modules ko relevant context deta hai

Isliye retrieval system ko product ka **shared intelligence access layer** samajhna chahiye.

### Retrieval system kya karega

1. input lega
- user query
- chat message
- research task instruction
- report request
- agent step input
- workflow trigger input

2. scope decide karega
- single document
- project-wide
- later workspace-wide

3. vector search karega
- Pinecone me
- metadata filters ke saath

4. relevant chunks return karega

5. context build karega
- dedup
- order
- token-budget fit
- citations/source references

6. final context consumer module ko dega

### Retrieval system khud final answer nahi hai

Ye bahut important distinction hai.

Retrieval system ka output ho sakta hai:
- relevant chunks
- normalized context package
- citation-ready source bundle

Final answer ya report retrieval system nahi, downstream consumer banayega.

---

## 5. Consumer Modules Ka Concept

Prepared knowledge base ko directly user nahi use karega.
User jo features dekhega wo alag-alag consumer modules honge.

Ye saare modules same retrieval system ko consume karenge.

Simple formula:

`Prepared Knowledge Base -> Retrieval System -> Consumer Module -> User Output`

---

## 6. Query and Chat: Same Ya Alag?

Ye related hain, but exactly same nahi hain.

### A. Query Module

Purpose:
- one-shot retrieval based answer ya search-style response

Typical use:
- "Is document me revenue drop ka reason kya hai?"
- "Project me risk related top relevant content dikhao"

Nature:
- stateless ya near-stateless
- single request -> single response

Output:
- direct answer
- sources
- maybe raw retrieval results

### B. Chat Module

Purpose:
- conversational interface over same knowledge base

Typical use:
- "Is project ka summary batao"
- "Achha ab sirf legal risk waale points batao"
- "Isko aur short me samjhao"

Nature:
- session-aware
- follow-up aware
- same retrieval system ko repeatedly call karega

Output:
- conversational answer
- citations
- session history linked response

Current implementation:
- persisted chat sessions
- persisted user and assistant messages
- document scoped chat
- project scoped chat

### Clear conclusion

- Query aur Chat same nahi hain
- but dono same retrieval/context system ko use karenge

Short distinction:

- Query = one-shot consumption interface
- Chat = session-based consumption interface

---

## 7. Main Future Consumer Systems

Ye product ke major upcoming systems honge jo retrieval layer ko use karenge.

### A. Knowledge Query System

Use case:
- user selected document ya project par question kare

Consumer role:
- retrieval result ko direct user answer me convert karna

Scope examples:
- document scoped
- project scoped

### B. Chat System

Use case:
- conversational research over uploaded knowledge

Consumer role:
- retrieval + prior conversation context combine karna

Scope examples:
- project chat
- document chat

### C. Research Task System

Use case:
- structured task execution

Examples:
- summarize this document
- compare two documents
- extract risks
- generate timeline
- identify action items

Consumer role:
- retrieval context ko task-specific prompt/process me use karna

Important:
- research task direct chat nahi hai
- ye instruction-driven structured execution hai

### D. Report Generation System

Use case:
- user ko final business/research deliverable dena

Examples:
- executive summary
- due diligence report
- risk report
- comparison report

Consumer role:
- retrieval context + research outputs ko structured report me assemble karna

### E. Agent System

Use case:
- multi-step AI workflows

Examples:
- research agent
- summarizer agent
- report agent

Consumer role:
- har agent step retrieval/context system use kar sakta hai
- agents same knowledge base ko different tasks ke liye consume karenge

### F. MCP Tool System

Use case:
- tools ke through structured knowledge access

Examples:
- semantic document search tool
- source lookup tool
- scoped retrieval tool

Consumer role:
- retrieval system MCP tools ke andar expose ho sakta hai

### G. Automation / Workflow System

Use case:
- n8n ya internal workflows

Examples:
- new document upload ke baad auto-summary
- scheduled weekly report
- triggered research run

Consumer role:
- workflow same retrieval/context layer ko programmatically call karega

---

## 8. Retrieval System Ko Kaun Kaun Use Karega

Crystal clear mapping:

1. `knowledge query` module use karega
2. `chat` module use karega
3. `research task` module use karega
4. `report generation` module use karega
5. `agents` use karenge
6. `MCP tools` use karenge
7. `automation workflows / n8n` use karega

Yani:

- retrieval system ek shared dependency hoga
- not a user-visible product by itself
- but almost saare intelligent modules usko consume karenge

---

## 9. Scope Levels: Document vs Project vs Workspace

Future clarity ke liye ye important hai:

### A. Document Scope

Use when:
- user ek specific document par kaam karna chahta hai

Example:
- "Is PDF ka summary batao"

Filter basis:
- `document_id`

### B. Project Scope

Use when:
- user poore project knowledge base par kaam karna chahta hai

Example:
- "Is project ke sabhi uploaded docs me key risks kya hain?"

Filter basis:
- `project_id`

### C. Workspace Scope

Use later when:
- multiple projects ke across knowledge consume karna ho

Example:
- "Mere workspace ke sabhi projects me legal risk trend kya hai?"

Filter basis:
- `workspace_id`

Current practical priority:
- document scope
- project scope

---

## 10. API Modules and Retrieval Alignment

### A. Knowledge Query APIs

Proposed APIs:
- `POST /api/v1/knowledge/query`
- `POST /api/v1/knowledge/query/document`
- `POST /api/v1/knowledge/query/project`

How retrieval is used:
- query input aata hai
- scope detect ya explicitly pass hota hai
- retrieval system top-k chunks nikalta hai
- context builder final context pack karta hai
- answer layer response generate karti hai

### B. Chat APIs

Proposed APIs:
- `POST /api/v1/research/chat`
- `POST /api/v1/research/chat/stream`
- `GET /api/v1/research/chat/sessions`
- `GET /api/v1/research/chat/sessions/{session_id}`
- `DELETE /api/v1/research/chat/sessions/{session_id}`

How retrieval is used:
- current user message + session scope input
- retrieval same knowledge base se context lata hai
- chat layer conversation state ke saath answer banata hai

### C. Research Task APIs

Proposed APIs:
- `POST /api/v1/research-tasks`
- `GET /api/v1/research-tasks`
- `GET /api/v1/research-tasks/{task_id}`
- `POST /api/v1/research-tasks/{task_id}/run`
- `POST /api/v1/research-tasks/{task_id}/cancel`

How retrieval is used:
- task run hone par task type ke hisab se retrieval chalega
- same retrieved context ko task-specific transformation me use kiya jayega

Current implementation:
- task create/list/get
- synchronous task run
- task cancel before execution completion
- document scoped and project scoped research tasks

### D. Report APIs

Proposed APIs:
- `POST /api/v1/reports/generate`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{report_id}`
- `DELETE /api/v1/reports/{report_id}`

How retrieval is used:
- report generation direct retrieval use kar sakta hai
- ya research tasks ke outputs ke through indirectly same knowledge consume karega

### E. Knowledge Operations APIs

Proposed APIs:
- `POST /api/v1/documents/{id}/reindex`
- `POST /api/v1/projects/{id}/reindex`
- `GET /api/v1/documents/{id}/status`
- `GET /api/v1/documents/{id}/chunks`

How retrieval relates:
- ye retrieval consumers nahi hain
- ye knowledge preparation lifecycle ko manage karte hain

### F. Automation APIs

Proposed APIs:
- `POST /api/v1/automation/workflows`
- `GET /api/v1/automation/workflows`
- `POST /api/v1/automation/workflows/{id}/run`
- `POST /api/v1/automation/workflows/{id}/pause`

How retrieval is used:
- workflow execution ke andar retrieval/context same reusable system se aayega

---

## 11. Query Loop vs Research Loop vs Report Loop

Ye teen loops related hain, but identical nahi hain.

### A. Query Loop

`user asks -> retrieve -> context build -> answer`

Use:
- direct knowledge access

### B. Research Loop

`user task instruction -> retrieve -> context build -> structured reasoning -> saved result`

Use:
- structured task outputs

### C. Report Loop

`user report request -> retrieve or reuse research outputs -> compose report -> save/export`

Use:
- final artifact generation

Conclusion:
- retrieval sab jagah common hoga
- but final consumer behavior alag hoga

---

## 12. Structure Mental Model (Final)

### A. Knowledge Preparation Side

`document_routes -> document_service -> task queue -> worker -> rag/ingestion -> llm/embeddings -> vectorstore/upsert`

### B. Knowledge Usage Side

`knowledge/chat/research/report/agent/mcp/automation -> rag/retrieval -> context builder -> llm/consumer logic -> output`

### C. Rule

- ingestion prepares knowledge
- retrieval accesses knowledge
- consumer modules convert retrieved knowledge into product outputs

---

## 13. Immediate Next Build Priority

Current priority should be:

1. retrieval system
2. context builder
3. knowledge query module
4. chat module
5. research task module
6. report generation module

Reason:
- knowledge base already ready hai
- ab product value tab aayegi jab prepared knowledge ka actual usage layer banega

---

## 14. One-Line Final Clarity

Abhi tak:

- `knowledge prepare karne wala system` ban chuka hai

Ab next:

- `same prepared knowledge ko query, chat, research, report, agents, MCP, aur automation me reuse karne wala shared retrieval/context system` banana hai
