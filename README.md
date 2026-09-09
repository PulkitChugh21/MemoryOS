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

### Currently Live (Phase 1)
- 🧠 **Episodic Memory** — Every conversation stored chronologically
- 🔍 **Semantic Search** — Vector-based retrieval finds relevant context by meaning
- 🔗 **Cross-Session Recall** — AI remembers across sessions, no re-explaining needed
- 💬 **Context-Aware Chat** — Gemini-powered responses enriched with project memory
- 📊 **Memory Stats Dashboard** — Real-time episode, session, and vector counts
- 🎨 **Premium UI** — Glassmorphism, animated gradients, micro-animations
- ✏️ **Project Management** — Create, rename, delete projects with confirmation modals
- 📝 **Markdown Rendering** — Code blocks, headings, math notation (KaTeX) in AI responses
- 💭 **Thinking Indicator** — Animated cycling status messages while AI generates (like GPT/Claude)
- 👤 **User Management** — Update profile, change password, delete account
- 🔐 **JWT Auth** — Secure registration, login, and session management
- 🔒 **Project Isolation** — Each project has its own memory namespace

---

## 🧠 Memory Architecture

### 🕒 Episodic Memory
Stores events and conversations chronologically — **what happened and when**.

### 🔍 Semantic Memory
Vector-based retrieval finds relevant context by meaning — **relevant knowledge even when wording differs**.

### 📊 Structured Memory *(Planned — Phase 2)*
Explicit facts, entities, and relationships in structured form.

### 🩹 Self-Healing Memory *(Planned — Phase 3)*
Auto-detect and repair stale, contradictory, or duplicated knowledge.

---

## 🔄 How It Works

```text
User Message
    │
    ▼
Embed Query (Gemini Embeddings)
    │
    ▼
Retrieve Context (Qdrant Semantic Search)
    │
    ├── Episodic Memory (recent history)
    └── Semantic Memory (relevant past context)
           │
           ▼
    Build Prompt (system + context + query)
           │
           ▼
    Gemini LLM → Context-Aware Response
           │
           ▼
    Store Both Turns (DB + Qdrant)
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
   └──────────────┘      └──────────────┘      └──────────────┘
```

**Tech Stack:**
| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Zustand, ReactMarkdown |
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| Database | Supabase PostgreSQL (connection pooler) |
| Vectors | Qdrant Cloud (3072-dim embeddings) |
| AI | Gemini 3 Flash Preview (LLM), Gemini Embedding 001 |
| Auth | JWT (PyJWT + bcrypt) |
| Deploy | Railway (backend), Vercel (frontend) |

---

## 🚧 Project Status

**Current Phase: Phase 1 — Foundation ✅ DEPLOYED & LIVE**

### Phase 1 — Foundation ✅
Core AI assistant, authentication, project isolation, episodic + semantic memory, premium web application. **Deployed and live.**

### Phase 2 — Multi-Modal Ingestion 🔜
File upload, structured memory extraction, hybrid search (BM25 + semantic), memory timeline UI.

### Phase 3 — Self-Healing Memory 🔜
Conflict detection, contradiction resolution, memory staleness scoring, consolidation, knowledge-gap detection.

### Phase 4 — Enterprise Scale 🔜
Multi-tenancy, RBAC, knowledge graph, public REST API, SDKs, rate limiting.

### Phase 5 — Ecosystem 🔜
GitHub/Jira/Notion integrations, IDE extensions, shared team memory, real-time collaboration, SaaS billing.

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ & npm
- Git
- Google Gemini API key
- Supabase project (PostgreSQL)
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
```

Create a `.env` file from `.env.example` and add your credentials.

```bash
# Start the backend
python -m app.main
```

In a new terminal:
```bash
cd memoryos/frontend
npm install
npm run dev
```

> **⚠️ Never commit `.env` or expose API keys, database credentials, service keys, or JWT secrets.**

### Deployment

| Service | Platform |
|---|---|
| Frontend | Vercel (auto-deploy from GitHub) |
| Backend | Railway (auto-deploy from GitHub) |
| Database | Supabase PostgreSQL (connection pooler) |
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