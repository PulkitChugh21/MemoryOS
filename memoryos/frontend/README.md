# MemoryOS — Frontend

Premium React web application for MemoryOS — the AI workspace with persistent memory.

## Tech Stack

- **React 18** with TypeScript
- **Vite** — blazing-fast build tool
- **Zustand** — lightweight state management
- **ReactMarkdown** + remark-gfm + remark-math + rehype-katex — rich AI response rendering
- **Axios** — HTTP client with JWT interceptors

## Pages

| Page | Route | Description |
|---|---|---|
| Login | `/login` | Split-screen auth with glassmorphism form |
| Register | `/register` | Registration with feature highlights |
| Projects | `/projects` | Project grid with create/rename/delete, user settings |
| Chat | `/chat/:projectId` | AI chat with memory sidebar, file upload, facts panel |
| Files | `/files/:projectId` | Drag-and-drop file upload, version history, delete (Phase 2) |
| Timeline | `/timeline/:projectId` | Chronological memory events with filter chips (Phase 2) |

## Design System — "Synaptic Recall"

- **Theme:** Dark glassmorphism with teal (`#4FD1C5`) accent
- **Backgrounds:** Animated gradient with floating orbs + grid overlay
- **Cards:** Glass effect with hover glow + top-line accent
- **Typography:** Space Grotesk (display), Inter (body), JetBrains Mono (code)
- **Signature Element:** "Pulse" — animated teal dot indicating memory activity

## Getting Started

```bash
npm install
npm run dev      # Start dev server
npm run build    # Production build
```

## Environment

The frontend connects to the backend API. Set the `VITE_API_URL` environment variable:

```bash
# .env.local (for local development)
VITE_API_URL=http://localhost:8000

# Production (set in Vercel dashboard)
VITE_API_URL=https://memoryos-production-cf09.up.railway.app
```

## Deployment

Deployed on **Vercel** with auto-deploy from GitHub. SPA rewrite configured in `vercel.json`.
