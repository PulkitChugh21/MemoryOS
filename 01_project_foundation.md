# MemoryOS — Project Foundation & Shared Context

*Feed this file to Antigravity first, in every session, before any phase file.
It contains the architecture, decisions, and tech stack that every phase builds on.*

## What MemoryOS Is

MemoryOS is a universal, enterprise-grade, persistent AI workspace — designed
so that any user working on a large-scale project never needs to re-explain
their history, decisions, or shared data to an AI assistant. It combines three
types of memory (episodic, semantic, structured) with a self-healing engine
that automatically detects and repairs stale or contradictory knowledge.

## Core Problems Being Solved

1. **Context Amnesia** — AI assistants forget everything between sessions.
2. **Repetition Tax** — Users waste time re-explaining project history.
3. **Stale Knowledge** — Past decisions become outdated; AI acts on them anyway.
4. **Contradiction Blindness** — AI doesn't notice when facts conflict across sessions.
5. **No File Memory** — Shared files disappear after a session ends.

## Agreed Decisions

| Decision | What Was Agreed |
|---|---|
| Project Type Support | All types: Software Dev, Research & Data Science, Business / Product Management |
| User Interfaces | All interfaces: Web App, VS Code Extension, CLI Tool, REST API, IDE Plugins |
| Deployment Model | Both: Fully cloud-hosted (SaaS) + Self-hosted (open source) |
| Cloud Provider | Most cost-effective: Railway (backend) + Vercel (frontend) + Supabase + Qdrant Cloud + Upstash |
| LLM Provider | Gemini API (generous free tier) |
| First Version Priority | Ship with auth + multi-user from day one |
| Estimated Monthly Cost | $0 to start (all free tiers); scales to ~$20/mo for small teams |

## Architecture Overview

MemoryOS is composed of 8 system layers. Data flows top-down from interfaces
through ingestion, memory storage, self-healing, and retrieval, before being
assembled into a context-enriched prompt for the LLM.

| Layer | Responsibility | Key Technologies |
|---|---|---|
| 1. Interface Layer | All user entry points | React, VS Code API, Click CLI, FastAPI SDK |
| 2. API Gateway & Auth | Security, routing, multi-tenancy | JWT, OAuth2, RBAC, Kong/Traefik |
| 3. Ingestion Pipeline | Parse, chunk, embed, deduplicate | Kafka, Tree-sitter, Gemini Embeddings |
| 4. Memory Store | 3-tier persistent memory | Supabase PostgreSQL, Qdrant, Redis, Neo4j |
| 5. Self-Healing Engine | Conflict detection, staleness, consolidation | Celery, LLM judge, TTL scoring |
| 6. Retrieval Layer | Hybrid search, re-rank, context assembly | BM25, Qdrant, Cohere Rerank |
| 7. LLM Orchestration | Prompt building, streaming, tool execution | Gemini API, LiteLLM, Jinja2 |
| 8. Infrastructure | Cloud + self-hosted deployment | Railway, Vercel, Docker, K8s Helm |

## The Three-Tier Memory System

### Tier 1 — Episodic Memory
Stores the full chronological record of every conversation turn and session.
Old sessions are automatically compressed into high-density summaries by
background workers. Users can "time-travel" back to any project state.
- **Storage**: Supabase PostgreSQL + TimescaleDB extension
- **TTL Policy**: Raw turns: 30 days → compressed summaries: indefinite

### Tier 2 — Semantic Memory
Vector embeddings of all project knowledge: code, documentation, decisions,
shared files. Powers fuzzy, intent-based retrieval.
- **Storage**: Qdrant Cloud (HNSW indexing, cosine similarity)
- **Embedding Model**: Gemini text-embedding-004 (768-dim, free tier)

### Tier 3 — Structured Memory
Hard facts and user preferences stored as key-value pairs and relational
records. Exact-match queryable. Never expires unless explicitly updated.
- **Storage**: Supabase PostgreSQL (relational) + Upstash Redis (fast cache)
- **Schema**: Entities: projects, facts, files, decisions, people, preferences

## Cost-Optimised Tech Stack

Total estimated cost to launch: **$0/month** (all free tiers). Scales to
~$20/month for a small team (10-20 users, moderate usage). No DevOps
expertise required — Railway and Vercel handle all infrastructure.

| Service | Provider | Free Tier Limit |
|---|---|---|
| Backend API | Railway | $5 credit/mo; ~500hr free compute |
| Frontend | Vercel | Unlimited deploys; global CDN |
| PostgreSQL DB | Supabase | 500MB DB; 50MB file storage |
| Vector DB | Qdrant Cloud | 1GB cluster; 1M vectors |
| Redis Cache | Upstash | 10,000 req/day; 256MB |
| LLM + Embeddings | Gemini API | 1M tokens/day free; 1500 req/min |
| Auth (multi-user) | Supabase Auth | 50,000 MAU free |
| File Storage | Supabase Storage | 1GB free |
| Background Jobs | Railway (Celery) | Included in backend compute |
| Monitoring | Railway Metrics | Basic; upgrade to Grafana Cloud free |

### Full Backend Stack
- FastAPI (Python) — main REST API framework, async, OpenAPI auto-docs
- SQLAlchemy (async) + Alembic — ORM and database migrations
- Qdrant Python client — vector store read/write
- google-generativeai SDK — Gemini LLM + text-embedding-004
- Celery + Redis — background job queue for self-healing workers
- python-jose + passlib — JWT auth + bcrypt password hashing
- structlog — structured JSON logging for Railway log drain
- tiktoken — token counting for context window management
- rank-bm25 — BM25 keyword retrieval (no external service needed)

### Full Frontend Stack
- React 18 + Vite — fast SPA with HMR
- Tailwind CSS — utility-first styling
- Zustand — lightweight global state (auth, project, chat)
- TanStack Query (React Query) — server state, caching, refetch
- Socket.IO client — real-time streaming AI responses
- React Router v6 — client-side routing
- shadcn/ui — accessible component library

## Prerequisites (before any phase)

- Node.js 20+ and Python 3.11+ installed locally
- Git repository created (GitHub recommended)
- Accounts created at: Railway, Vercel, Supabase, Qdrant Cloud, Upstash
- Gemini API key from Google AI Studio (aistudio.google.com)
