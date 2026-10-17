# AGENTS.md — lazy pointers vs eager loading (example)

> Fragment of a tier-1 `AGENTS.md`. Compare with the full pattern in
> [`../agents-md/AGENTS.md`](../agents-md/AGENTS.md).
>
> ⚠️ Claude Code has `@path` (**EAGER**: pulled in at start-up). Pi's support for `@path` includes
> inside `AGENTS.md` is **NOT DOCUMENTED** — treat the file as plain text. The only safe pattern:
> - **Pointer** (`data/changes/STATUS.md` …) = **LAZY**: the agent opens it with `read` when needed.
> - **Anti-pattern:** pasting STATUS/SHARP_EDGES/PLAYBOOK into `AGENTS.md` or `APPEND_SYSTEM.md` → paid
>   on **every** turn.
> - Note: `@path` on the **command line** (`pi @src/app.py "…"`) is documented — it adds a file to the
>   first prompt. That is a per-run choice, not a context-file feature.

## Project

Billing API. Monorepo: `api/` (FastAPI) + `web/` (React).
Repo overview: read `README.md` when needed (do not embed it here).
npm scripts: read `package.json` on demand.

## Commands

- Tests: `.venv/bin/pytest tests/ -q` (never bare `pytest`: use the venv)
- Lint: `npm run lint --workspace=web`

## Rules

- Before renaming/deleting a shared symbol: `codegraph_explore` + Serena
  `find_referencing_symbols` (the why lives in `data/changes/CONVENTIONS.md`).
- Live per-ticket state: `data/changes/STATUS.md` (read when orienting, never copy here).
- Always-on gates: `.pi/APPEND_SYSTEM.md`.

<!--
  - Everything is a one-line pointer: the agent reads on demand.
  - ANTI-PATTERN: do NOT paste big ledgers into AGENTS.md or APPEND_SYSTEM.md.
  - Result: a small, stable tier 1 — which also keeps the prompt cache warm.
-->
