# MemoryOS — Product Requirements Document (PRD)

*Status: ACTIVE BUILD · Version 1.0*

## 1. What We're Building

MemoryOS is a universal, enterprise-grade, persistent AI workspace. It gives
any user working on a long-running project an AI assistant that never
forgets — no re-explaining history, decisions, or files across sessions.
It combines three memory types (episodic, semantic, structured) with a
self-healing engine that automatically finds and fixes stale or
contradictory knowledge.

**One-line pitch:** An AI assistant with real, permanent, self-correcting
memory of your project — so you stop repeating yourself.

## 2. Problems This Solves

| # | Problem | Description |
|---|---|---|
| 1 | Context Amnesia | AI assistants forget everything between sessions |
| 2 | Repetition Tax | Users waste time re-explaining project history every session |
| 3 | Stale Knowledge | Past decisions become outdated; AI keeps acting on them anyway |
| 4 | Contradiction Blindness | AI doesn't notice when facts conflict across sessions |
| 5 | No File Memory | Shared files disappear from context after a session ends |

## 3. Target Users

- **Software development teams** — need memory of architecture decisions, tech stack, bugs fixed, code shared
- **Research & data science teams** — need memory of hypotheses, datasets, experiment results, findings
- **Business / product management teams** — need memory of decisions, stakeholders, goals, milestones

Common thread: **anyone working on a project that spans more than one
sitting**, where re-explaining context to an AI assistant is a recurring
tax on their time.

## 4. Core Features (by capability, not by phase)

### Memory
- Episodic memory: full chronological history of every conversation, with automatic compression of old sessions into summaries
- Semantic memory: vector-searchable knowledge of code, docs, decisions, and files
- Structured memory: exact-match facts — tech stack, people, goals, milestones, open questions
- Knowledge graph: relationships between entities across all memory tiers (later phase)

### Self-Healing
- Automatic conflict detection when new information contradicts stored memory
- Domain-aware staleness scoring (code decays faster than people/roles)
- Background consolidation of old memory into dense summaries
- Gap detection — proactively asks the user one targeted question when information is missing

### Interfaces
- Web app (primary interface)
- VS Code extension (captures edits, surfaces memory in-editor)
- CLI tool (`memoryos ask` / `push` / `status`)
- REST API + SDKs (Python, JavaScript, Go)
- Additional IDE plugins (JetBrains, Neovim) — later phase

### Collaboration & Enterprise
- Multi-user, multi-organization support with hard namespace isolation
- Role-based access control (owner, admin, member, viewer)
- Shared team memory in later phases

### Integrations (later phase)
- GitHub (commits, PRs, issues)
- Jira / Linear (tickets)
- Notion (docs)

## 5. Non-Goals (explicitly out of scope for now)

- Training or fine-tuning a custom LLM — MemoryOS orchestrates an existing
  LLM (Gemini), it does not build one
- Real-time multiplayer editing (Google-Docs-style) — collaboration ships
  as shared memory access first, live co-editing is not planned near-term
- On-device / fully offline operation — the architecture assumes cloud
  services (Supabase, Qdrant, Gemini API) are reachable

## 6. Success Criteria for Each Phase

| Phase | Success Looks Like |
|---|---|
| 1 — Foundation | A real user can register, create a project, chat, and get responses that recall earlier messages in that project — deployed on a live public URL |
| 2 — Multi-Modal Ingestion | A user can upload a file, re-upload a changed version, and get a meaningful diff; search finds relevant facts by keyword or meaning |
| 3 — Self-Healing | Contradictory facts get flagged automatically without the user reporting them; a health dashboard shows memory freshness |
| 4 — Enterprise Scale | Multiple organizations can use the product with zero data leakage between them; a public API is documented and usable by a third party |
| 5 — Ecosystem | At least one real external tool (e.g. GitHub) is syncing into memory automatically |

## 7. Key Product Decisions Already Made

| Decision | What Was Agreed |
|---|---|
| Project Type Support | All types: Software Dev, Research & Data Science, Business / Product Management |
| User Interfaces | Web App, VS Code Extension, CLI Tool, REST API, IDE Plugins (all planned) |
| Deployment Model | Both fully cloud-hosted (SaaS) and self-hosted (open source) |
| Cloud Provider | Cost-optimized: Railway + Vercel + Supabase + Qdrant Cloud + Upstash |
| LLM Provider | Gemini API (generous free tier) |
| First Version Priority | Ship with auth + multi-user support from day one, not bolted on later |
| Build Tool | Antigravity (Google's agentic IDE, Gemini-based) |
| Estimated Monthly Cost | $0 to start; scales to ~$20/mo for a small team |

See `Architecture.md` for the technical design behind these decisions, and
`Phases.md` for how the build is sequenced.
