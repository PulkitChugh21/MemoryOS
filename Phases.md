# MemoryOS — Build Phases

*Companion to `PRD.md` (what/why), `Architecture.md` (how), and `Rules.md`
(boundaries). Build phases strictly in order — do not start a phase until
the previous one is deployed and stable. See `Rules.md` §4 on not building
ahead of the current phase.*

---

## Phase 1 — Foundation (Weeks 1–6)

**Goal:** A live, deployed, working AI assistant with basic memory and multi-user auth.

- FastAPI backend with full async SQLAlchemy + Supabase PostgreSQL
- Supabase Auth integration — registration, login, JWT verification
- Episodic memory: store and retrieve conversation history per project
- Gemini API integration — LLM responses + text-embedding-004
- Qdrant vector store — embed and search conversation chunks
- Basic React web app — auth flow, project list, chat interface
- Railway + Vercel deployment — live public URL

**Ships:** `users`, `projects`, `memory_episodes` tables · auth + project +
basic chat endpoints · the Master System Prompt with RULE-1, 2, 4, 5, 7, 8
active (RULE-3 self-healing runs in basic recency-only form; RULE-6 file
versioning is stubbed, fully built in Phase 2).

---

## Phase 2 — Multi-Modal Ingestion (Weeks 7–12)

**Goal:** Users can share files, code, and data — all remembered and versioned.

- File upload + versioning (Supabase Storage, diff on re-upload)
- Structured memory store — fact extraction from conversations via Gemini
- Hybrid search — BM25 keyword + semantic combined with RRF fusion
- VS Code extension skeleton — captures edits, surfaces memory in sidebar
- CLI tool — `memoryos ask` / `push` / `status` commands
- Memory timeline UI — scrollable project history view

**Ships:** `memory_facts` table · file + memory/search endpoints · RULE-6
(file versioning) fully implemented · retrieval upgraded from
semantic-only to hybrid (semantic + BM25) with recency re-ranking.

---

## Phase 3 — Self-Healing (Weeks 13–18)

**Goal:** Memory stays accurate automatically — no user maintenance needed.

- Celery worker infrastructure on Railway (background jobs)
- Conflict resolver — LLM judge detects and flags contradictions
- Staleness TTL scoring — domain-aware decay (code 7d, decisions 30d, goals 90d)
- Memory consolidator — compresses old episodes into summaries nightly
- Gap detector — low-confidence retrievals trigger proactive user prompts
- Memory health dashboard — coverage score, freshness, conflict count

**Ships:** `memory_conflicts` table · conflict + health endpoints · RULE-3
(self-healing) fully implemented with all 4 sub-steps (contradiction
check, surfacing, recency/confidence scoring, TTL staleness flagging).

---

## Phase 4 — Enterprise Scale (Weeks 19–26)

**Goal:** Production-ready multi-org platform with full RBAC and public API.

- Multi-tenancy — hard namespace isolation per org, Row Level Security
- RBAC — owner, admin, member, viewer roles at org + project level
- Knowledge graph (Neo4j or PostgreSQL graph extension) — entity relationships
- Public REST API — versioned, documented, rate-limited
- Python, JavaScript, and Go SDKs
- Self-hosted Helm chart — full Kubernetes deployment package

**Ships:** Tier 4 (Knowledge Graph) becomes active · retrieval strategy
adds graph traversal (+2 hops) as its final step · RULE-7 (multi-user
isolation) extends from per-user to per-org with role checks within an org.

**Sub-sequencing note:** build multi-tenancy + RBAC first (it touches
every existing table), knowledge graph second (additive to hybrid search),
public API + SDKs last (needs a stable surface to document).

---

## Phase 5 — Ecosystem (Weeks 27–36)

**Goal:** Integration hub — MemoryOS connects to every tool teams already use.

- GitHub integration — auto-ingest commits, PRs, issues
- Jira / Linear integration — link tickets to memory
- Notion integration — sync docs into semantic memory
- JetBrains + Neovim plugins
- Shared team memory + real-time collaboration
- SaaS billing (Stripe) + usage analytics dashboard

**Sequencing note:** don't build all six speculatively. Prioritize by what
real users from Phases 1–4 actually ask for. If monetizing, build Stripe
billing first regardless of which integration follows. Real-time
collaboration is the most technically complex item — sequence it last.

---

## How to Use This File With Antigravity

- Start a fresh Antigravity session per phase, not one continuous session
  for the whole project — this keeps its working context focused.
- Feed it, in order: `PRD.md` → `Architecture.md` → `Rules.md` → the
  relevant phase section above.
- Tell it explicitly: "Build exactly what's described for this phase. Do
  not implement anything from later phases yet."
- Update `Memory.md` as work completes, so the next session (or the next
  person) knows exactly where things stand.
