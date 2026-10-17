# AGENTS.md — project orientation (Pi)

> **Golden rule of this file:** Pi loads it into the system prompt of every session started in this
> directory or below. Keep it small: orientation + one-line pointers. Detail lives under
> `data/changes/` and is read **on demand**. Pi has no `@imports` and no scoped rules, so pointers are
> the only mechanism — the agent opens them with `read` when needed.

## What this project is

Document-extraction service (Python 3.12). Turns PDFs into structured data and validates them
against a schema.

## Workspace layout

| Repo | Role | Permission |
|---|---|---|
| `sample-service` | **Owned** — where we work. | Edit / commit (push only if the human asks). |
| `frontend`, `backend`, `infra` | **Read-only context.** | Read freely. Do **not** edit unless explicitly asked; propose fixes instead. |

> Never commit/stage from the workspace root: always operate inside one repo.

## Commands

```bash
.venv/bin/pytest tests/ -q          # tests
.venv/bin/python -m parser <pdf>    # run the parser on one file
```

## Code navigation (mandatory order)

1. **CodeGraph** `codegraph_explore` first (survey + blast radius) — exposed `direct` in `.pi/mcp.json`.
2. **Serena** `find_referencing_symbols` **always** before renaming/deleting.
3. grep/read only for literals.

## Conventions

- Branches: `feat/tck-NNNN` · `fix/tck-NNNN`.
- **Confidentiality:** no client names, ticket IDs or secrets in code/commits.
- **No agent self-attribution** in delivered artifacts.
- **Plan → agree → implement**; external actions belong to the human (unless explicitly asked).
  Enforced by the global extension `~/.pi/agent/extensions/block-external-git.ts`.

## On-demand memory — pointers (do NOT copy the detail here)

- Live per-ticket state → `data/changes/STATUS.md`
- Debugging lessons → `data/changes/PLAYBOOK.md`
- Invariants / locked decisions → `data/changes/SHARP_EDGES.md`
- Sanitisation policy → `data/changes/CONVENTIONS.md`
- Handover template → `data/changes/_HANDOVER_TEMPLATE.md`
- Machine role (read before any shared write) → `data/changes/s3-sync/IDENTITY.md`
- Pi methodology pack → `data/changes/ai-agent-methodology/PI_ADAPTATION.md`

<!-- Do NOT add a per-ticket ledger here: this file is always loaded.
     Write each record ONCE in its canonical ledger; only the pointer lives here. -->
