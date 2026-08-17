# 🧠 MemoryOS

> A universal, enterprise-grade, persistent AI workspace that remembers project history, decisions, and shared data — so users never have to repeatedly explain their context to an AI assistant.

MemoryOS is designed to give AI assistants **persistent long-term memory** instead of treating every conversation as an isolated session.

It combines **episodic, semantic, and structured memory** with a planned **self-healing memory engine** that can detect and repair stale or contradictory knowledge.

---

## 🎯 Why MemoryOS?

Today's AI assistants are powerful, but their memory is often limited to individual conversations or manually provided context.

When working on a long-running project, users repeatedly have to explain:

- What happened previously
- Which decisions were made
- Why those decisions were made
- What the current project state is
- Which information is still relevant

MemoryOS aims to eliminate this repeated context-sharing by creating a **persistent memory layer between users and AI assistants**.

Instead of starting every conversation from scratch, the assistant can retrieve relevant information from previous interactions and use it to provide more context-aware responses.

---

## 🌐 Vision

MemoryOS aims to become a **persistent AI workspace** where memory is treated as a first-class capability rather than an afterthought.

The long-term vision is to enable AI assistants to:

- 🧠 Remember important information across conversations
- 🗂️ Maintain context across long-running projects
- 🔍 Retrieve relevant memories when needed
- 📚 Combine different types of memory
- 🩹 Detect and repair stale or contradictory knowledge
- 👥 Support multiple users, projects, and organizations
- 🔌 Connect with the tools and workflows teams already use

> **MemoryOS — Give AI a memory worth remembering.**

---

## 🧠 Memory Architecture

MemoryOS is built around multiple complementary memory layers, each serving a different purpose.

### 🕒 Episodic Memory

Episodic memory stores events and conversations that occur over time.

It enables MemoryOS to remember:

- Previous conversations
- Project discussions
- Decisions made during interactions
- User activity and context

This allows the assistant to understand **what happened and when**.

### 🔍 Semantic Memory

Semantic memory stores information that can be retrieved based on meaning rather than exact wording.

MemoryOS uses vector-based semantic retrieval to find relevant information from previous interactions and provide it as context to the AI.

This enables the assistant to recall **relevant knowledge even when the wording of a new question is different**.

### 📊 Structured Memory

Structured memory is designed to store explicit facts, entities, relationships, and project-level information in a structured form.

It will allow MemoryOS to reason over information that is better represented as structured data rather than conversation history.

**Status:** Planned for a future phase.

### 🩹 Self-Healing Memory

Memory should not remain correct forever.

Project information can become outdated, duplicated, irrelevant, or contradictory as the project evolves.

The planned self-healing engine will allow MemoryOS to:

- Detect conflicting information
- Identify stale memories
- Evaluate memory freshness
- Consolidate related memories
- Resolve contradictions
- Detect knowledge gaps

**Status:** Planned for Phase 3.

---

## 🔄 How MemoryOS Works

At a high level, the system follows this flow:

```text
User
  │
  ▼
Conversation
  │
  ▼
Memory Retrieval
  │
  ├── Episodic Memory
  │
  └── Semantic Memory
          │
          ▼
     Relevant Context
          │
          ▼
      Gemini LLM
          │
          ▼
     Context-Aware
        Response
          │
          ▼
   Memory Persistence

---

## 🏗️ Architecture

MemoryOS uses a modular architecture that separates the frontend, backend, AI services, persistent data, and vector memory.

```text
                         ┌─────────────────────┐
                         │      React UI       │
                         │    Vite + TypeScript│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
       │   Supabase   │      │    Qdrant    │      │    Gemini    │
       │  PostgreSQL  │      │ Vector Store │      │  LLM + Embed │
       └──────────────┘      └──────────────┘      └──────────────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │    Memory Layer     │
                         │ Episodic + Semantic │
                         └─────────────────────┘

---

## 🚧 Project Status

**Current Phase: Phase 1 — Foundation**

**Status: 🟢 Core implementation complete · Deployment next**

MemoryOS is being developed incrementally, with each phase adding a major capability to the platform.

### Phase 1 — Foundation ✅

The current implementation includes:

- [x] FastAPI asynchronous backend
- [x] Supabase PostgreSQL integration
- [x] JWT authentication
- [x] User registration and login
- [x] Project creation and management
- [x] User/project memory isolation
- [x] Episodic conversation memory
- [x] Qdrant vector storage
- [x] Semantic memory retrieval
- [x] Gemini LLM integration
- [x] Gemini embeddings
- [x] Context-aware chat responses
- [x] Memory statistics
- [x] React + TypeScript frontend
- [x] Authentication and project management UI
- [x] Chat interface
- [x] Railway backend configuration
- [x] Vercel frontend configuration
- [x] Local end-to-end verification

The next step for Phase 1 is deploying the application and performing end-to-end verification on the live environment.

---

## 🗺️ Roadmap

### Phase 1 — Foundation
**Status: ✅ Complete**

Core AI assistant, authentication, project isolation, episodic memory, semantic retrieval, and web application.

### Phase 2 — Multi-Modal Ingestion
**Status: 🔜 Planned**

- File upload and ingestion
- File versioning and diffing
- Structured memory extraction
- Hybrid search
- BM25 + semantic retrieval
- VS Code extension
- CLI
- Memory timeline

### Phase 3 — Self-Healing Memory
**Status: 🔜 Planned**

- Conflict detection
- Contradiction resolution
- Memory staleness scoring
- Memory consolidation
- Knowledge-gap detection
- Proactive memory prompts
- Memory health dashboard

### Phase 4 — Enterprise Scale
**Status: 🔜 Planned**

- Multi-tenancy
- Role-Based Access Control
- Organization-level isolation
- Knowledge graph
- Public REST API
- SDKs
- Rate limiting
- Self-hosted deployment

### Phase 5 — Ecosystem
**Status: 🔜 Planned**

- GitHub integration
- Jira / Linear integration
- Notion integration
- IDE integrations
- Shared team memory
- Real-time collaboration
- Usage analytics
- SaaS billing

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.12+
- Node.js + npm
- Git
- Google Gemini API key
- Supabase project
- Qdrant Cloud cluster

### Local Setup

```bash
git clone https://github.com/<your-username>/MemoryOS.git
cd MemoryOS/memoryos/backend

python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and add your credentials.

Start the backend:

```bash
python -m app.main
```

In a new terminal, start the frontend:

```bash
cd memoryos/frontend
npm install
npm run dev
```
> **Never commit `.env` or expose API keys, database credentials, service keys, or JWT secrets.**

### Deployment

```text
Frontend  → Vercel
Backend   → Railway
Database  → Supabase
Vectors   → Qdrant Cloud
AI        → Gemini API
```

---

## ⚠️ Current Limitations

MemoryOS is currently in its early development stages. The Phase 1 implementation provides the foundation for persistent AI memory, but several capabilities are still under development.

Current limitations include:

- Structured memory is not yet implemented.
- The self-healing memory engine is planned for a future phase.
- Multi-modal file ingestion is not yet available.
- Enterprise multi-tenancy and RBAC are planned for later phases.
- External integrations such as GitHub, Jira, Linear, and Notion are not yet available.
- Production-scale performance and reliability have not yet been fully validated.

These limitations are addressed progressively through the project's roadmap.

---

## 📚 Documentation

Detailed project documentation is maintained separately to keep the README focused.

| Document | Description |
|---|---|
| `PRD.md` | Product requirements and feature definition |
| `Architecture.md` | System architecture and technical design |
| `Design.md` | Product and UI/UX design |
| `Memory.md` | Memory architecture and behavior |
| `Phases.md` | Development phases and roadmap |
| `Rules.md` | Project development and engineering rules |
| `01_project_foundation.md` | Project foundation and initial planning |

---

## 🔒 Security

MemoryOS uses environment variables for sensitive configuration.

**Never commit or publicly expose:**

- API keys
- Database passwords
- Supabase service keys
- Qdrant API keys
- JWT secrets
- `.env` files

Use `.env.example` as the template for required configuration.

---

## 🤝 Contributing

MemoryOS is currently under active development.

As the project matures, contribution guidelines, issue templates, and development documentation will be expanded.

If you find a bug or have an idea for improving MemoryOS, feel free to open an issue or discussion.

---

## 📌 Future Direction

MemoryOS is being developed toward a broader goal: creating a persistent memory infrastructure that can work across AI assistants, development tools, and collaborative workflows.

The long-term goal is to move from:

```text
AI that remembers conversations
        ↓
AI that remembers projects
        ↓
AI that understands evolving knowledge
        ↓
AI with persistent, self-maintaining memory