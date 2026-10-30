# MemoryOS — Project Memory

*This file is the project's own memory of itself. Update it after every
meaningful unit of work: what got finished, what's in progress right now,
and what's next. Keep it honest — this is exactly the discipline MemoryOS
itself is meant to enforce for its users, so it should not go stale.*

**Last updated:** 2026-10-30

---

## Current Status: ✅ Phase 2 — Multi-Modal Ingestion: Complete

**Frontend:** https://memory-os-gamma.vercel.app
**Backend:** https://memoryos-production-cf09.up.railway.app

## ✅ Completed

- [x] Master Blueprint reviewed and understood (source: `MemoryOS_Master_Blueprint.docx`)
- [x] Decided on build approach: fine-tune/extend existing models + build
      product layer on top, using Antigravity as the dev environment
- [x] Reviewed Azure student credits ($100) — decided to keep the
      blueprint's original free-tier stack (Railway/Vercel/Supabase/
      Qdrant/Upstash/Gemini) rather than forcing it onto Azure
- [x] Confirmed Antigravity (Google's Gemini-based agentic IDE) as the
      build tool
- [x] Blueprint split into phase-ready files for feeding to Antigravity
- [x] Core project docs created:
  - [x] `PRD.md` — what to build, target users, features, non-goals
  - [x] `Architecture.md` — system layers, data flow, folder structure, tech stack
  - [x] `Rules.md` — approved stack, hard boundaries, error handling, AI agent rules
  - [x] `Phases.md` — 5-phase build roadmap
  - [x] `Design.md` — color system, typography, the "Pulse" signature element
  - [x] `Memory.md` — this file
- [x] **Phase 1 Backend — Fully Built & Tested:**
  - [x] Project folder structure matching Architecture.md §6
  - [x] `requirements.txt` with all Phase 1 dependencies
  - [x] `core/config.py` — Pydantic Settings with validation_alias + os.environ fallback for Railway
  - [x] `core/security.py` — JWT creation/verification + bcrypt password hashing
  - [x] `core/logging.py` — structlog JSON logging for Railway
  - [x] `.env.example` — all Phase 1 env vars documented
  - [x] `db/models.py` — SQLAlchemy models: User, Project, MemoryEpisode
  - [x] `db/session.py` — async session factory with pool_pre_ping, 5-min recycle
  - [x] `schemas/__init__.py` — all Pydantic request/response models + UserUpdate, ChangePassword
  - [x] `memory/episodic.py` — Tier 1 episodic memory CRUD
  - [x] `memory/semantic.py` — Qdrant vector store with auto-recreate on dimension mismatch
  - [x] `memory/retrieval.py` — semantic retrieval with relevance*0.6+recency*0.4 re-ranking
  - [x] `llm/gemini_client.py` — Gemini API wrapper with retry+backoff + fast-fail on quota (60s timeout)
  - [x] `llm/embeddings.py` — Gemini gemini-embedding-001 (3072-dim) wrapper
  - [x] `llm/prompt_builder.py` — Master System Prompt with concise response rules + context assembly
  - [x] `api/auth.py` — /auth/register, /auth/login, /auth/me, PATCH /me, POST /change-password, DELETE /me
  - [x] `api/projects.py` — full CRUD (create, list, get, update, delete) with user isolation
  - [x] `api/chat.py` — core chat loop with short-lived DB sessions + SSE streaming
  - [x] `api/memory.py` — episodes, sessions, stats read endpoints
  - [x] `api/health.py` — health check + /health/debug diagnostic endpoint
  - [x] `main.py` — FastAPI app with CORS (hardcoded + regex), lifecycle, global error handler
  - [x] Alembic configured and initial migration applied to Supabase
- [x] **Phase 1 Frontend — Fully Built & Polished:**
  - [x] Vite + React 18 + TypeScript project initialized
  - [x] Premium "Synaptic Recall v2" design system in `index.css`:
    - Animated gradient backgrounds with floating orbs
    - Grid pattern overlay for depth
    - Glassmorphism cards with hover glow + top-line accent
    - Premium buttons with shine effects
    - Modal system (overlay + card + animations)
    - Badges, stat cards, tech tags
    - Markdown content styles for AI responses
    - KaTeX CSS for math notation rendering
  - [x] `api/client.ts` — Axios client with JWT interceptors, 60s timeout, user management methods
  - [x] `store/authStore.ts` — Zustand auth state management
  - [x] `store/chatStore.ts` — Zustand chat state with retry logic (2 retries, exponential backoff)
  - [x] `pages/LoginPage.tsx` — split-screen layout with hero section + glassmorphism form
  - [x] `pages/RegisterPage.tsx` — matching split-screen with feature highlights
  - [x] `pages/ProjectsPage.tsx` — project grid with:
    - Edit (✏️) and Delete (🗑️) buttons per card
    - Rename modal, delete confirmation modal
    - User profile dropdown (avatar + name → settings/logout)
    - Profile settings modal (update name/email, change password, delete account)
  - [x] `pages/ChatPage.tsx` — chat with:
    - ReactMarkdown + remark-gfm + remark-math + rehype-katex
    - Animated thinking indicator with cycling status messages while AI generates
    - User/assistant avatars
    - Combined input bar (input + send button in one container)
    - Glass sidebar with memory stats
  - [x] `App.tsx` — React Router v6 + protected routes
- [x] **External Services Connected:**
  - [x] Supabase PostgreSQL — tables created via Alembic migration (using connection pooler URL)
  - [x] Qdrant Cloud — collection auto-created per project (3072-dim)
  - [x] Gemini API — gemini-3-flash-preview (LLM) + gemini-embedding-001 (embeddings)
- [x] **Production Deployed & Working:**
  - [x] Backend on Railway (Nixpacks builder, auto-deploy from GitHub)
  - [x] Frontend on Vercel (auto-deploy from GitHub)
  - [x] CORS fixed: hardcoded origins + allow_origin_regex for *.vercel.app
  - [x] Database connection fixed: switched from direct Supabase URL to connection pooler
  - [x] /health/debug diagnostic endpoint for troubleshooting
  - [x] Auth (login/register) working on production
  - [x] Chat working with concise responses and markdown rendering
  - [x] Project CRUD (create, rename, delete) working
  - [x] User management (update profile, change password, delete account) working
  - [x] Git security audit: .gitignore hardened for .env.*, binary files, build artifacts
- [x] **Phase 2 Backend — Fully Built:**
  - [x] `db/models.py` — added `MemoryFact` and `ProjectFile` SQLAlchemy models
  - [x] Alembic migration `b3e7f2a1c504` — `memory_facts` + `project_files` tables with indexes
  - [x] `schemas/__init__.py` — added Pydantic schemas for facts, files, and timeline
  - [x] `memory/structured.py` — facts CRUD: store, query by type/key, search, update, mark stale, count
  - [x] `llm/fact_extractor.py` — Gemini-based fact extraction from conversations (decision, preference, entity, tech_stack, goal, milestone, open_question)
  - [x] `memory/bm25_search.py` — BM25 keyword search using rank-bm25 (pure Python, no external service)
  - [x] `memory/retrieval.py` — upgraded to hybrid search: semantic (Qdrant) + BM25 fused via RRF (k=60), re-ranked by rrf_score * 0.5 + recency * 0.3 + source_type_boost * 0.2
  - [x] `core/config.py` — added file upload config: 10MB max, allowed extensions, chunk size (500 tokens), overlap (100 tokens)
  - [x] `memory/file_processor.py` — file ingestion pipeline: parse → chunk → embed → store in Supabase Storage + Qdrant, with version tracking and diff summary
  - [x] `api/files.py` — file upload, download, list, delete, version history endpoints
  - [x] `main.py` — registered files router
  - [x] `api/chat.py` — integrated hybrid search, structured facts in context, non-blocking fact extraction after each response
  - [x] `llm/prompt_builder.py` — added structured facts section to prompt (high-confidence project knowledge)
  - [x] `api/memory.py` — added facts listing, fact detail, timeline, and updated stats with fact/file counts
  - [x] `requirements.txt` — added rank-bm25==0.2.2 and supabase==2.15.2
- [x] **Phase 2 Frontend — Fully Built:**
  - [x] `api/client.ts` — added `filesApi` (upload, list, get, download, delete, versions, diff) and `factsApi` (list, get) + timeline endpoint
  - [x] `pages/FilesPage.tsx` — drag-and-drop file upload, file list with version badges, delete with confirmation
  - [x] `pages/TimelinePage.tsx` — chronological memory timeline with filter chips (All/Conversations/Files/Facts)
  - [x] `pages/ChatPage.tsx` — added 📎 file upload button in input bar, facts sidebar showing extracted knowledge, navigation links to Files/Timeline pages, updated memory stats with facts/files counts
  - [x] `App.tsx` — added routes: `/files/:projectId`, `/timeline/:projectId`
  - [x] `index.css` — added Phase 2 CSS: upload zone, timeline nodes, filter chips, fact cards, file version badges, responsive adjustments
- [x] **Phase 2 Verification:**
  - [x] TypeScript compilation (`tsc --noEmit`) — zero errors
  - [x] Frontend build (`npm run build`) — passes
  - [x] `.gitignore` audit — all secrets protected, no sensitive files tracked

## 🔨 Currently Being Worked On

- Nothing — Phase 2 code is complete. Ready for deployment.

## ⏭️ Next Up

1. **Deploy Phase 2:**
   - Run Alembic migration `alembic upgrade head` on Supabase (adds `memory_facts` + `project_files` tables)
   - Install new backend dependencies: `pip install rank-bm25 supabase`
   - Redeploy backend to Railway
   - Redeploy frontend to Vercel
   - Manual verification: test file upload, fact extraction, hybrid search, timeline
2. **Phase 2 deferred items:**
   - VS Code extension skeleton (deferred to Phase 2.5)
   - CLI tool (`memoryos ask` / `push` / `status`) (deferred to Phase 2.5)
3. Begin Phase 3 planning and implementation (Self-Healing Memory):
   - Celery worker infrastructure
   - Conflict detection and resolution
   - Staleness TTL scoring
   - Memory consolidation
   - Gap detection
   - Memory health dashboard

## 🧭 Decisions Log (append-only — don't edit past entries, add new ones)

| Date | Decision |
|---|---|
| 2026-07-28 | Fine-tune/extend existing models + build product layer, not train from scratch |
| 2026-07-28 | Keep original free-tier stack; do not port to Azure despite having $100 Azure credit |
| 2026-07-28 | Use Antigravity as the primary build/dev environment |
| 2026-07-28 | Build strictly phase-by-phase; do not build ahead (see `Rules.md` §2, §4) |
| 2026-07-28 | Phase 1 backend uses Gemini 2.0 Flash as default LLM model |
| 2026-07-28 | Tailwind CSS v4 used (latest, with @tailwindcss/vite plugin) |
| 2026-07-28 | All API routes mounted under /api/v1 prefix for future versioning |
| 2026-08-04 | Switched LLM model from gemini-2.0-flash (quota exhausted, limit:0) to gemini-3-flash-preview |
| 2026-08-04 | Switched embedding model from text-embedding-004 (discontinued) to gemini-embedding-001 (3072-dim) |
| 2026-08-04 | Restructured chat.py to use short-lived DB sessions — Supabase drops idle connections during long Gemini API calls |
| 2026-08-04 | Added ResourceExhausted fast-fail in Gemini client to prevent 30s+ SDK retry hangs |
| 2026-08-05 | Reduced SQLAlchemy pool_recycle from 3600s to 300s for Supabase free-tier compatibility |
| 2026-08-11 | Rewrote all frontend pages with inline styles to fix Tailwind class spacing conflicts |
| 2026-08-13 | Initialized git repo; created Railway (railway.toml) + Vercel (vercel.json) deployment configs |
| 2026-08-25 | Deployed to Railway + Vercel. Fixed CORS with hardcoded origins + regex fallback |
| 2026-08-26 | Switched Supabase connection from direct URL to connection pooler (DNS resolution fix on Railway) |
| 2026-08-26 | Added /health/debug endpoint for production diagnostics |
| 2026-09-03 | Full visual overhaul: animated backgrounds, glassmorphism, premium split-screen auth, card hover effects |
| 2026-09-03 | Added user management: update profile, change password, delete account (backend + frontend) |
| 2026-09-03 | Added project rename/delete UI with confirmation modals |
| 2026-09-03 | Added ReactMarkdown + remark-math + rehype-katex for formatted AI responses |
| 2026-09-03 | Chat retry logic: 2 retries with exponential backoff, 60s frontend + backend timeout |
| 2026-09-03 | Updated system prompt for concise responses: 200-400 word max, no LaTeX $..$ syntax |
| 2026-09-09 | Added animated thinking indicator with 8 cycling status phrases while AI generates |
| 2026-10-30 | Phase 2: Files limited to 10MB max, text/code files only (images/PDFs deferred) |
| 2026-10-30 | Phase 2: VS Code extension and CLI deferred to end of Phase 2 / Phase 2.5 |
| 2026-10-30 | Phase 2: rank-bm25 chosen for BM25 keyword search (pure Python, $0/month, no Elasticsearch) |
| 2026-10-30 | Phase 2: RRF fusion with k=60 merges semantic + BM25 ranked lists (standard from RRF paper) |
| 2026-10-30 | Phase 2: BM25 indexes built in-memory at query time (project memory is small enough; caching added later if needed) |
| 2026-10-30 | Phase 2: Fact extraction runs non-blocking after response is sent (same pattern as embedding storage) |
| 2026-10-30 | Phase 2: Short-lived DB sessions strictly enforced around each operation to avoid Supabase connection drops during slow Gemini calls |

## 📝 How to Update This File

After finishing a task:
1. Move the item from "Currently Being Worked On" or "Next Up" into "✅ Completed"
2. Update "Currently Being Worked On" with whatever comes next
3. Add any new decisions to the Decisions Log with today's date
4. Update the "Last updated" date at the top
5. If a task revealed a schema or architecture change, update
   `Architecture.md` in the same pass — don't let the docs drift from the code
