# MemoryOS — Rules

*Guardrails for anyone (human or AI agent) writing code on this project.
If Antigravity or any contributor is about to do something this file says
not to do, stop and follow this instead.*

## 1. Approved Stack — Do Not Substitute Without Asking

These were deliberately chosen for cost (free-tier fit) and simplicity.
Don't swap them for "better" alternatives without checking with the
project owner first — every substitution risks breaking the $0/month
cost model or the free-tier limits documented in `Architecture.md`.

| Layer | Use | Do Not Use Instead |
|---|---|---|
| Backend framework | FastAPI | Django, Flask (async story is weaker) |
| ORM | SQLAlchemy (async) + Alembic | Raw SQL strings, Django ORM, Prisma |
| Vector DB | Qdrant Cloud | Pinecone, Weaviate, pgvector (unless explicitly revisited) |
| Cache / fast KV | Upstash Redis (REST) | Standard Redis (needs persistent TCP, breaks serverless) |
| LLM + embeddings | Gemini API | OpenAI, Anthropic API (unless the project owner changes providers) |
| Auth | Supabase Auth | Rolling a custom auth system from scratch |
| Background jobs | Celery + Redis | Cron scripts, threading, unmanaged async tasks |
| Frontend framework | React 18 + Vite | Next.js, Angular, Vue (unless project owner revisits) |
| Styling | Tailwind CSS | Styled-components, plain CSS, Bootstrap |
| Frontend state | Zustand + TanStack Query | Redux, Context-API-as-global-store |
| Deployment | Railway (backend) + Vercel (frontend) | AWS/GCP/Azure from-scratch setups, unless cost-justified later |

## 2. Hard Boundaries — Never Do These

- **Never commit secrets.** No API keys, DB URLs, or JWT secrets in code —
  everything comes from environment variables, and `.env` is gitignored.
- **Never expose `SUPABASE_SERVICE_KEY` to the frontend.** It only lives
  in backend environment variables. The frontend only ever uses the anon key.
- **Never skip auth on a data-bearing endpoint.** Every route that reads or
  writes project/memory data requires a valid Bearer JWT, checked at the
  API Gateway layer before it reaches business logic.
- **Never let one user's or org's memory leak into another's.** Every
  query against `memory_episodes`, `memory_facts`, or Qdrant must be scoped
  by `project_id` and `org_id`. This is RULE-7 from the master system
  prompt — treat it as non-negotiable, not best-effort.
- **Never store more PII than necessary.** Names are fine. Do not store
  passwords, payment details, or credentials inside memory tiers —
  those belong in dedicated, purpose-built secure storage (e.g. Supabase
  Auth's own tables), not in `memory_facts`.
- **Never let the LLM context grow unbounded.** Always token-count with
  `tiktoken` and summarize/truncate before hitting the model's context
  limit — this is what the Retrieval Layer's "top-8 chunks, summarize if
  over budget" rule exists to enforce.
- **Never build ahead of the current phase.** If you're implementing
  Phase 1, do not also wire up the knowledge graph (Phase 4) or
  integrations (Phase 5) "while you're in there." See `Phases.md`.

## 3. Error Handling Conventions

- **Standard error shape.** Every API error returns:
  ```json
  { "error": { "code": "string", "message": "human-readable", "details": {} } }
  ```
- **HTTP status codes mean what they mean.** 400 for bad input, 401 for
  missing/invalid auth, 403 for permission denied, 404 for missing
  resources, 409 for conflicts (e.g. duplicate project name), 422 for
  validation errors, 500 only for genuinely unexpected server failures.
- **Never swallow exceptions silently.** Every caught exception either
  gets re-raised as a typed API error or logged via `structlog` with
  enough context to debug (user_id, project_id, request_id) — never a
  bare `except: pass`.
- **Never leak stack traces to the client** in production. Log the full
  trace server-side; return a generic message + error code to the client.
- **LLM calls need retries with backoff.** Gemini API calls should retry
  on transient failures (rate limit, timeout) with exponential backoff,
  capped at 3 attempts, before surfacing an error to the user.
- **Background jobs must be idempotent.** Celery tasks (consolidation,
  conflict detection, staleness sweep) can be retried or run twice safely
  — never assume exactly-once execution.
- **Self-healing failures should degrade, not break.** If the Self-Healing
  Engine fails to run for a project (e.g. Celery worker down), the chat
  flow must still work using whatever memory already exists — self-healing
  is an enhancement layer, not a hard dependency of every request.

## 4. Boundaries for Antigravity / AI Agents Specifically

- **Follow the phase file exactly.** When given a phase file from
  `Phases.md`, build only what's described in it. Don't add features from
  later phases even if they seem like small additions.
- **Don't introduce new paid services.** If a task seems to need a service
  outside the approved stack (Section 1), stop and flag it to the user
  instead of adding it unprompted — this could break the $0/month model.
- **Update `Memory.md` after every meaningful unit of work.** Mark what
  was completed, what file is currently being worked on, and what's next.
  This file is the project's own memory — keep it honest and current,
  the same discipline MemoryOS itself is meant to embody.
- **Don't silently change the schema.** If a task requires a schema change
  not described in `Architecture.md`, update `Architecture.md` in the same
  change, so the docs and the code never drift apart.
- **Ask before destructive actions.** Dropping tables, deleting
  migrations, or force-pushing over existing deployed data should always
  be confirmed with the user first.
- **No scope creep.** If an idea comes up that isn't in `PRD.md`, note it
  rather than building it — new features get added to the PRD and phase
  plan deliberately, not organically mid-implementation.
