# MemoryOS — Architecture

*Companion to `PRD.md` (what/why) and `Rules.md` (constraints). This file
is the how: system layers, data flow, folder structure, and tech stack.*

## 1. System Architecture Overview

MemoryOS is composed of 8 layers. Data flows top-down from interfaces
through ingestion, memory storage, and self-healing, before being
assembled into a context-enriched prompt for the LLM.

| Layer | Responsibility | Key Technologies |
|---|---|---|
| 1. Interface Layer | All user entry points | React, VS Code API, Click CLI, FastAPI SDK |
| 2. API Gateway & Auth | Security, routing, multi-tenancy | JWT, OAuth2, RBAC |
| 3. Ingestion Pipeline | Parse, chunk, embed, deduplicate | Tree-sitter, Gemini Embeddings |
| 4. Memory Store | 3-tier persistent memory | Supabase PostgreSQL, Qdrant, Redis, Neo4j (later) |
| 5. Self-Healing Engine | Conflict detection, staleness, consolidation | Celery, LLM judge, TTL scoring |
| 6. Retrieval Layer | Hybrid search, re-rank, context assembly | BM25, Qdrant, re-ranking |
| 7. LLM Orchestration | Prompt building, streaming, tool execution | Gemini API, Jinja2 |
| 8. Infrastructure | Cloud + self-hosted deployment | Railway, Vercel, Docker |

## 2. Web / App Flow

### 2.1 Chat Request Flow (core loop)
```
User sends message (web / VS Code / CLI)
        │
        ▼
API Gateway — verify JWT, resolve org_id + project_id
        │
        ▼
Retrieval Layer
   1. Embed the query (Gemini text-embedding-004)
   2. Hybrid search: semantic (Qdrant) + keyword (BM25)
   3. Re-rank: relevance_score * 0.6 + recency_score * 0.4
   4. (Phase 4+) Traverse knowledge graph, +2 hops max
   5. Assemble top-8 chunks, summarise if over budget
        │
        ▼
LLM Orchestration — build prompt (system prompt + retrieved context
   + new message) → stream response from Gemini via SSE
        │
        ▼
Self-Healing Engine (async, after response is sent)
   - Extract new facts/preferences/files/action items from the turn
   - Check for contradictions against existing memory_facts
   - Tag confidence + source on everything stored
        │
        ▼
Memory Store — write to memory_episodes (always) and memory_facts
   (when a durable fact was extracted)
```

### 2.2 File Upload Flow
```
User uploads file → Supabase Storage
        │
        ▼
Ingestion Pipeline — parse (Tree-sitter for code, plain text otherwise),
   chunk, embed each chunk
        │
        ▼
Check for existing version of this file
   → if found: generate diff, surface to user
   → store new version, keep old version with timestamp
        │
        ▼
Write chunks + embeddings to Qdrant; write file metadata to Postgres
```

### 2.3 Self-Healing Background Loop (Celery, runs continuously)
```
Every N minutes:
  - Staleness sweep: flag memory_facts past their domain TTL as is_stale
  - Consolidation sweep: compress episodes older than 30 days into
    summaries (mark is_compressed = true)
  - Conflict sweep: LLM judge compares related facts, writes rows to
    memory_conflicts where contradictions are found
```

## 3. The Three-Tier Memory System

### Tier 1 — Episodic Memory
Full chronological record of every conversation turn/session. Old
sessions are compressed into summaries by background workers.
- **Storage**: Supabase PostgreSQL (+ TimescaleDB extension for time-series efficiency)
- **TTL Policy**: Raw turns: 30 days → compressed summaries: indefinite

### Tier 2 — Semantic Memory
Vector embeddings of all project knowledge for fuzzy, intent-based retrieval.
- **Storage**: Qdrant Cloud (HNSW indexing, cosine similarity)
- **Embedding Model**: Gemini text-embedding-004 (768-dim, free tier)

### Tier 3 — Structured Memory
Hard facts and preferences as key-value/relational records. Exact-match
queryable. Never expires unless explicitly updated.
- **Storage**: Supabase PostgreSQL (relational) + Upstash Redis (fast cache)
- **Entities**: projects, facts, files, decisions, people, preferences

### Tier 4 — Knowledge Graph (Phase 4+)
Relationships between entities across all memory tiers.
- **Storage**: Neo4j or a PostgreSQL graph extension

## 4. Tech Stack

### Backend
- FastAPI (Python) — async REST API, OpenAPI auto-docs
- SQLAlchemy (async) + Alembic — ORM and migrations
- Qdrant Python client — vector store read/write
- google-generativeai SDK — Gemini LLM + embeddings
- Celery + Redis — background job queue (self-healing workers)
- python-jose + passlib — JWT auth + bcrypt hashing
- structlog — structured JSON logging
- tiktoken — token counting for context budget
- rank-bm25 — keyword retrieval, no external service needed

### Frontend
- React 18 + Vite — SPA with HMR
- Tailwind CSS — utility-first styling (see `Design.md` for tokens)
- Zustand — global state (auth, project, chat)
- TanStack Query — server state, caching, refetch
- Socket.IO client — real-time streaming responses
- React Router v6 — client-side routing
- shadcn/ui — accessible component primitives

### Infrastructure
- Railway — backend + Celery worker hosting
- Vercel — frontend hosting, global CDN
- Supabase — PostgreSQL, Auth, file storage
- Qdrant Cloud — vector database
- Upstash — Redis (REST-based, serverless-friendly)

## 5. Database Schema (summary — see phase files for full column detail)

- `users` — id, email, name, org_id, preferences
- `projects` — id, owner_id, org_id, name, tech_stack, status
- `memory_episodes` — episodic tier: role, content, summary, embedding_id, confidence
- `memory_facts` — structured tier: fact_type, key, value, source, confidence, is_stale, ttl_days
- `memory_conflicts` — conflict_type, fact_a_id, fact_b_id, resolution

Qdrant collection per project: `project_{project_id}_memories`, 768-dim
vectors, cosine distance, payload indexed on `source_type` and `created_at`.

## 6. Folder & File Structure

```
memoryos/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entrypoint
│   │   ├── worker.py                  # Celery worker entrypoint
│   │   ├── api/
│   │   │   ├── auth.py                # /auth/* routes
│   │   │   ├── projects.py            # /projects/* routes
│   │   │   ├── chat.py                # /chat/* routes (SSE streaming)
│   │   │   ├── memory.py              # /memory/* routes
│   │   │   ├── files.py               # /files/* routes
│   │   │   └── health.py              # /health route
│   │   ├── core/
│   │   │   ├── config.py              # env var loading (pydantic settings)
│   │   │   ├── security.py            # JWT, password hashing
│   │   │   └── logging.py             # structlog setup
│   │   ├── db/
│   │   │   ├── models.py              # SQLAlchemy ORM models
│   │   │   ├── session.py             # async DB session factory
│   │   │   └── rls.sql                # Row Level Security policies
│   │   ├── memory/
│   │   │   ├── episodic.py            # episodic tier read/write
│   │   │   ├── semantic.py            # Qdrant read/write
│   │   │   ├── structured.py          # facts read/write
│   │   │   ├── retrieval.py           # hybrid search + re-rank
│   │   │   └── self_healing/
│   │   │       ├── conflict_resolver.py
│   │   │       ├── staleness_detector.py
│   │   │       ├── consolidator.py
│   │   │       └── gap_detector.py
│   │   ├── llm/
│   │   │   ├── gemini_client.py       # Gemini API wrapper
│   │   │   ├── prompt_builder.py      # assembles system + context + message
│   │   │   └── embeddings.py          # embedding generation
│   │   └── schemas/                   # Pydantic request/response models
│   ├── alembic/                       # DB migrations
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── pages/                     # Login, Register, ProjectList, Chat, MemoryTimeline, Settings
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui primitives
│   │   │   ├── chat/
│   │   │   ├── memory/
│   │   │   └── layout/
│   │   ├── store/                     # Zustand slices
│   │   ├── api/                       # React Query hooks
│   │   ├── styles/                    # Tailwind config, design tokens
│   │   └── lib/
│   ├── index.html
│   ├── vite.config.ts
│   └── tailwind.config.js
├── vscode-extension/                  # Phase 2+
├── cli/                                # Phase 2+
├── sdks/                               # Phase 4+: python/, javascript/, go/
└── docs/
    ├── PRD.md
    ├── Architecture.md
    ├── Rules.md
    ├── Phases.md
    ├── Design.md
    └── Memory.md
```

## 7. Environment Variables Reference

| Variable | Where to Get It |
|---|---|
| GEMINI_API_KEY | aistudio.google.com → API Keys |
| DATABASE_URL | Supabase → Settings → Database → Connection string |
| SUPABASE_URL | Supabase → Settings → API → Project URL |
| SUPABASE_SERVICE_KEY | Supabase → Settings → API → service_role key |
| QDRANT_URL | Qdrant Cloud → Cluster → Endpoint |
| QDRANT_API_KEY | Qdrant Cloud → Cluster → API Key |
| UPSTASH_REDIS_REST_URL | Upstash Console → REST API → Endpoint |
| UPSTASH_REDIS_REST_TOKEN | Upstash Console → REST API → Token |
| JWT_SECRET_KEY | Generate: `openssl rand -hex 32` |
| CORS_ORIGINS | Your Vercel domain (comma-separated) |
