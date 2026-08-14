# MemoryOS — Design System

*Companion to `Architecture.md` (frontend stack: React + Tailwind +
shadcn/ui). This file is the single source of truth for color, type, and
visual identity — Antigravity should derive every UI color/font decision
from this file rather than defaulting to generic Tailwind/shadcn presets.*

## 1. Design Concept: "Synaptic Recall"

MemoryOS's whole premise is memory that persists and repairs itself — like
a living neural network rather than a static database. The visual system
should feel like looking into an active memory store: a deep, calm base
punctuated by small, precise signals showing memory state (fresh, stale,
conflicted). This is a developer/enterprise tool used for long sessions —
the design should stay quiet and legible by default, and reserve color for
information that actually matters (memory health), not decoration.

**Avoid:** the cream-background-plus-terracotta-serif look, the
near-black-plus-single-neon-accent look, and the hairline-broadsheet look —
all are current AI-generated-design defaults. MemoryOS's palette below is
close in spirit to the "dark plus accent" family but is specifically tuned
so color is functional (it encodes memory state), not just moody.

## 2. Color Palette

| Token | Hex | Role |
|---|---|---|
| `--ink` | `#0E1524` | Base background — deep indigo-black, "long-term storage" |
| `--surface` | `#161F33` | Cards, panels, sidebar — one step up from base |
| `--surface-raised` | `#1E2A45` | Modals, dropdowns, hover states |
| `--text-primary` | `#E7ECF6` | Primary text on dark surfaces |
| `--text-muted` | `#8B96AC` | Secondary text, labels, timestamps |
| `--recall` | `#4FD1C5` | Primary brand accent — "synapse firing," active retrieval, links, primary buttons |
| `--stale` | `#E8A33D` | Amber — memory flagged as stale by the Staleness Detector |
| `--conflict` | `#E8617B` | Rose — memory_conflicts, contradictions, destructive actions |
| `--healthy` | `#4ADE80` | Emerald — confirmed/high-confidence memory, success states |

These map directly to real product states, not just arbitrary UI color:

- **Recall (teal)** = memory is being actively retrieved right now
- **Stale (amber)** = flagged by the self-healing TTL sweep
- **Conflict (rose)** = a contradiction the Conflict Resolver found
- **Healthy (green)** = high-confidence, up-to-date memory

### Light Mode (secondary, for users who prefer it)
| Token | Hex | Role |
|---|---|---|
| `--ink-light` | `#F7F8FB` | Background |
| `--surface-light` | `#FFFFFF` | Cards, panels |
| `--text-primary-light` | `#0E1524` | Primary text |
| `--text-muted-light` | `#5B6478` | Secondary text |

Accent colors (`--recall`, `--stale`, `--conflict`, `--healthy`) stay the
same in both modes — they're slightly desaturated by ~8% in light mode to
avoid vibrating against the white background.

## 3. Typography

| Role | Typeface | Used For |
|---|---|---|
| Display | **Space Grotesk** | Page titles, section headers, the wordmark — geometric with a slightly technical, engineered character that fits a memory/systems product without tipping into cold/corporate |
| Body | **Inter** | All UI copy, chat messages, buttons, labels — high legibility at small sizes, developer-familiar |
| Data / Mono | **JetBrains Mono** | Code snippets, API endpoints, memory IDs, timestamps, the VS Code extension and CLI output |

### Type Scale
| Level | Size / Line Height | Weight | Face |
|---|---|---|---|
| Display XL | 40px / 48px | 600 | Space Grotesk |
| Display L | 28px / 36px | 600 | Space Grotesk |
| Heading | 20px / 28px | 600 | Space Grotesk |
| Body | 15px / 24px | 400 | Inter |
| Body Small | 13px / 20px | 400 | Inter |
| Caption / Label | 12px / 16px | 500, uppercase, +0.04em tracking | Inter |
| Code / Data | 13px / 20px | 400 | JetBrains Mono |

Fonts load via Google Fonts or self-hosted `.woff2` — specify both in
`frontend/src/styles/fonts.css` and reference as CSS variables
(`--font-display`, `--font-body`, `--font-mono`) so Tailwind config
consumes them rather than hardcoding font-family strings in components.

## 4. The Signature Element: "The Pulse"

Every place memory is referenced in the UI (a chat message drawing on
past context, a fact card, a file version) gets a small dot/ring indicator
next to it — **the Pulse** — colored by that memory's current state:

- Teal, gently animating = actively retrieved for this response
- Amber, static = stale, flagged by the self-healing engine
- Rose, static = part of an unresolved conflict
- Green, static = confirmed high-confidence memory

This is the one recurring visual motif across every surface (web app,
memory timeline, health dashboard, VS Code sidebar, CLI output where
color is supported) — it's what makes MemoryOS's self-healing behavior
*visible* rather than something that just happens invisibly in the
background. Keep every other UI element quiet and disciplined so the
Pulse is what people remember.

## 5. Layout Principles

- **Density over whitespace-for-its-own-sake.** This is a working tool
  used for hours at a time, not a marketing page — favor a compact,
  information-dense layout (closer to a code editor or terminal) over
  generous consumer-app padding.
- **Sidebar + main pane** as the primary app shell: project/memory
  navigation on the left, chat or content in the center, contextual memory
  panel (facts, conflicts, health) foldable on the right.
- **Motion is functional, not decorative.** The only animation that
  matters is the Pulse's retrieval indicator and streaming text as
  responses arrive — avoid page-load choreography or hover flourishes
  that don't correspond to a real system event.
- **Accessibility floor:** all color-coded states (Pulse colors) must also
  be distinguishable by shape/label for colorblind users — pair color with
  an icon or text label, never color alone. Maintain visible keyboard
  focus rings using `--recall` at 2px. Respect `prefers-reduced-motion`
  by disabling the Pulse's animation (keep the static color/shape).

## 6. Tailwind Config Mapping

```js
// tailwind.config.js — extend, do not replace, shadcn/ui defaults
colors: {
  ink: '#0E1524',
  surface: '#161F33',
  'surface-raised': '#1E2A45',
  'text-primary': '#E7ECF6',
  'text-muted': '#8B96AC',
  recall: '#4FD1C5',
  stale: '#E8A33D',
  conflict: '#E8617B',
  healthy: '#4ADE80',
},
fontFamily: {
  display: ['Space Grotesk', 'sans-serif'],
  body: ['Inter', 'sans-serif'],
  mono: ['JetBrains Mono', 'monospace'],
}
```
