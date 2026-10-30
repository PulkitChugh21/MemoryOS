# 🧠 MemoryOS

> A universal, enterprise-grade, persistent AI workspace that remembers project history, decisions, and shared data — so users never have to repeatedly explain their context to an AI assistant.

MemoryOS gives AI assistants **persistent long-term memory** instead of treating every conversation as an isolated session.

It combines **episodic, semantic, and structured memory** with a planned **self-healing memory engine** that can detect and repair stale or contradictory knowledge.

🌐 **Live Demo:** [memory-os-gamma.vercel.app](https://memory-os-gamma.vercel.app)

---

## 🎯 Why MemoryOS?

Today's AI assistants are powerful, but their memory is limited to individual conversations or manually provided context.

When working on a long-running project, users repeatedly have to explain:

- What happened previously
- Which decisions were made
- Why those decisions were made
- What the current project state is
- Which information is still relevant

MemoryOS eliminates this repeated context-sharing by creating a **persistent memory layer between users and AI assistants**.

Instead of starting every conversation from scratch, the assistant retrieves relevant information from previous interactions and provides context-aware responses.

---

## ✨ Features

### Phase 1 — Foundation ✅
- 🧠 **Episodic Memory** — Every conversation stored chronologically
- 🔍 **Semantic Search** — Vector-based retrieval finds relevant context by meaning
- 🔗 **Cross-Session Recall** — AI remembers across sessions, no re-explaining needed
- 💬 **Context-Aware Chat** — Gemini-powered responses enriched with project memory
- 📊 **Memory Stats Dashboard** — Real-time episode, session, and vector counts
- 🎨 **Premium UI** — Glassmorphism, animated gradients, micro-animations
- ✏️ **Project Management** — Create, rename, delete projects with confirmation modals
- 📝 **Markdown Rendering** — Code blocks, headings, math notation (KaTeX) in AI responses
- 💭 **Thinking Indicator** — Animated cycling status messages while AI generates
- 👤 **User Management** — Update profile, change password, delete account
- 🔐 **JWT Auth** — Secure registration, login, and session management
- 🔒 **Project Isolation** — Each project has its own memory namespace

### Phase 2 — Multi-Modal Ingestion ✅
- 📁 **File Upload & Versioning** — Upload text/code files, auto-chunked and embedded into memory with version tracking
- 🧠 **Structured Facts** — AI automatically extracts decisions, preferences, tech stack, goals from conversations
- 🔍 **Hybrid Search** — BM25 keyword + semantic search fused via Reciprocal Rank Fusion (RRF)
- 📅 **Memory Timeline** — Chronological view of all memory events (conversations, files, facts) with filter chips
- 📎 **Chat File Upload** — Upload files directly from the chat input bar
- 🧩 **Facts Sidebar** — Extracted project knowledge displayed alongside chat
- 📄 **File Management Page** — Drag-and-drop upload, file list, version history, delete

---

## 🧠 Memory Architecture

### 🕒 Episodic Memory (Tier 1)
Stores events and conversations chronologically — **what happened and when**.

### 🔍 Semantic Memory (Tier 2)
Vector-based retrieval finds relevant context by meaning — **relevant knowledge even when wording differs**.

### 📊 Structured Memory (Tier 3) ✅
Explicit facts, entities, and relationships extracted by AI — **decisions, preferences, tech stack, goals, milestones**.

### 🩹 Self-Healing Memory *(Planned — Phase 3)*
Auto-detect and repair stale, contradictory, or duplicated knowledge.

---

## 🔄 How It Works

```text
User Message / File Upload
    │
    ▼
Embed Query (Gemini Embeddings)
    │
    ▼
Hybrid Retrieval
    │
    ├── Semantic Search (Qdrant vectors)
    ├── BM25 Keyword Search (rank-bm25)
    └── RRF Fusion (k=60) + Re-ranking
           │
           ▼
    Build Prompt
    │
    ├── Structured Facts (high-confidence project knowledge)
    ├── Retrieved Memory Chunks (hybrid search results)
    └── Recent Conversation History
           │
           ▼
    Gemini LLM → Context-Aware Response
           │
           ▼
    Store (DB + Qdrant + Extract Facts)
```

---

## 🏗️ Architecture

```text
                     ┌─────────────────────┐
                     │      React UI       │
                     │  Vite + TypeScript   │
                     │   (Vercel)          │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │      FastAPI        │
                     │      Backend        │
                     │    (Railway)        │
                     └──────────┬──────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │   Supabase   │      │    Qdrant    │      │    Gemini    │
   │  PostgreSQL  │      │ Vector Store │      │  LLM + Embed │
   │  + Storage   │      │              │      │              │
   └──────────────┘      └──────────────┘      └──────────────┘
```

**Tech Stack:**
| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Zustand, ReactMarkdown, KaTeX |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic, rank-bm25 |
| Database | Supabase PostgreSQL (connection pooler) + Supabase Storage |
| Vectors | Qdrant Cloud (3072-dim embeddings) |
| AI | Gemini 3 Flash Preview (LLM), Gemini Embedding 001, Gemini Fact Extraction |
| Auth | JWT (PyJWT + bcrypt) |
| Deploy | Railway (backend), Vercel (frontend) |

---

## 🚧 Project Status

**Current Phase: Phase 2 — Multi-Modal Ingestion ✅ COMPLETE**

### Phase 1 — Foundation ✅
Core AI assistant, authentication, project isolation, episodic + semantic memory, premium web application. **Deployed and live.**

### Phase 2 — Multi-Modal Ingestion ✅
File upload & versioning, structured memory (fact extraction), hybrid search (BM25 + semantic + RRF), memory timeline UI, chat integration. **Complete — ready to deploy.**

### Phase 3 — Self-Healing Memory 🔜
Conflict detection, contradiction resolution, memory staleness scoring, consolidation, knowledge-gap detection.

### Phase 4 — Enterprise Scale 🔜
Multi-tenancy, RBAC, knowledge graph, public REST API, SDKs, rate limiting.

### Phase 5 — Ecosystem 🔜
GitHub/Jira/Notion integrations, IDE extensions, shared team memory, real-time collaboration, SaaS billing.

---

## 📂 Project Structure

```text
memoryos/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   │   ├── auth.py       # Registration, login, profile
│   │   │   ├── chat.py       # Chat with hybrid retrieval + fact extraction
│   │   │   ├── files.py      # File upload, download, versioning (Phase 2)
│   │   │   ├── health.py     # Health check + diagnostics
│   │   │   ├── memory.py     # Episodes, facts, timeline, stats
│   │   │   └── projects.py   # Project CRUD
│   │   ├── core/         # Config, security, logging
│   │   ├── db/           # SQLAlchemy models + session
│   │   ├── llm/          # Gemini client, embeddings, prompt builder, fact extractor
│   │   ├── memory/       # Memory subsystems
│   │   │   ├── episodic.py       # Tier 1: conversation storage
│   │   │   ├── semantic.py       # Tier 2: Qdrant vector store
│   │   │   ├── structured.py     # Tier 3: facts CRUD (Phase 2)
│   │   │   ├── bm25_search.py    # BM25 keyword search (Phase 2)
│   │   │   ├── retrieval.py      # Hybrid retrieval + RRF fusion
│   │   │   └── file_processor.py # File parsing, chunking, embedding (Phase 2)
│   │   └── schemas/      # Pydantic request/response models
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/          # Axios client + API methods
│       ├── pages/        # React pages (Login, Register, Projects, Chat, Files, Timeline)
│       └── store/        # Zustand state management
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ & npm
- Git
- Google Gemini API key
- Supabase project (PostgreSQL + Storage)
- Qdrant Cloud cluster

### Local Setup

```bash
# Clone the repository
git clone https://github.com/PulkitChugh21/MemoryOS.git
cd MemoryOS/memoryos/backend

# Create and activate virtual environment
python -m venv venv
```

Windows:
```powershell
.\venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend
python -m app.main
```

In a new terminal:
```bash
cd memoryos/frontend
npm install
npm run dev
```

Create a `.env` file from `.env.example` and add your credentials.

> **⚠️ Never commit `.env` or expose API keys, database credentials, service keys, or JWT secrets.**

### Deployment

| Service | Platform |
|---|---|
| Frontend | Vercel (auto-deploy from GitHub) |
| Backend | Railway (auto-deploy from GitHub) |
| Database | Supabase PostgreSQL (connection pooler) + Supabase Storage |
| Vectors | Qdrant Cloud |
| AI | Gemini API |

---

## 📚 Documentation

| Document | Description |
|---|---|
| `PRD.md` | Product requirements and feature definition |
| `Architecture.md` | System architecture and technical design |
| `Design.md` | Product and UI/UX design ("Synaptic Recall" theme) |
| `Memory.md` | Project memory — status, decisions, what's next |
| `Phases.md` | Development phases and roadmap |
| `Rules.md` | Engineering rules and boundaries |

---

## 🔒 Security

MemoryOS uses environment variables for all sensitive configuration.

**Never commit or publicly expose:**
- API keys (Gemini, Qdrant)
- Database passwords / connection strings
- JWT secrets
- `.env` files

---

## 🤝 Contributing

MemoryOS is under active development. If you find a bug or have an idea, feel free to open an issue or discussion.

---

## 📌 Future Direction

```text
AI that remembers conversations
        ↓
AI that remembers projects
        ↓
AI that understands evolving knowledge
        ↓
AI with persistent, self-maintaining memory
```

> **MemoryOS — Give AI a memory worth remembering.**
