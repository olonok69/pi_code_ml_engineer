# AGENTS.md in Pi — the two-tier context pattern (§02)

Claude Code's always-loaded file is `CLAUDE.md`; Cursor uses `AGENTS.md` + `.cursor/rules/*.mdc`.
Pi uses **context files** — `AGENTS.md` (or `CLAUDE.md`) — with loading rules that differ from both.
The classic mistake is the same everywhere: stuffing history into the always-loaded file until every
turn pays a huge tax.

## How Pi finds context files (source: `resource-loader.ts`, [configuration] docs)

| Rule | Detail |
|---|---|
| **Global** | `~/.pi/agent/` (or `$PI_CODING_AGENT_DIR`): `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, `CLAUDE.MD` |
| **Walk-up** | The working directory **and every parent** up to `/` |
| **Not below** | Subdirectories of cwd are **never** loaded — no nested, most-specific-wins discovery |
| **One file per directory** | First existing of `AGENTS.override.md > AGENTS.md > AGENTS.MD > CLAUDE.md > CLAUDE.MD`. A directory with both `AGENTS.md` and `CLAUDE.md` contributes **only `AGENTS.md`** |
| **Order** | Global first, then ancestors from `/` down to cwd; each wrapped as `<project_instructions path="…">` |
| **Trust** | Context files load **regardless of project trust**. Disable with `-nc` / `--no-context-files` |
| **Worktrees** | A nested git worktree does not load the main repo's copy of the same file twice |

What Pi does **not** read: `~/.claude/CLAUDE.md` (its global dir is `~/.pi/agent/` — symlink or copy
if you want one shared file) and `.claude/rules/`.

## Differences vs Claude Code and Cursor

| | Claude Code | Cursor | Pi |
|---|---|---|---|
| Nested files below cwd | Yes (on demand) | Yes (most specific wins) | **No** |
| Parent directories | Yes | — | **Yes** (all the way to `/`) |
| Several files in one dir | `CLAUDE.md` + `CLAUDE.local.md` | — | **One** — `AGENTS.md` shadows `CLAUDE.md` |
| `@path` imports | Yes (eager) | No | **NOT DOCUMENTED** — treat as plain text with pointers |
| Scoped rules (globs/paths) | `.claude/rules/` | `.mdc` `globs` | **None** |
| Replace / append system prompt | `--system-prompt` / `--append-system-prompt` | — | `SYSTEM.md` / `APPEND_SYSTEM.md` (global or `.pi/`) + same CLI flags |

⚠️ Walk-up has a side effect: a session started inside `workspace/repo/` also loads
`workspace/AGENTS.md` (or `CLAUDE.md`). Useful for a shared workspace file — but know it is there.

## Files in this folder

| File | Tier | Use |
|---|---|---|
| [`AGENTS.md`](./AGENTS.md) | 1 — always loaded | Orientation + one-line pointers |
| [`APPEND_SYSTEM.md.example`](./APPEND_SYSTEM.md.example) | 1 — always loaded | The always-on **gates** (Pi's nearest thing to an `alwaysApply` rule) |
| [`AGENTS.override.md.example`](./AGENTS.override.md.example) | 1 — local | Merge a committed `AGENTS.md` with a personal `CLAUDE.md` that Pi would otherwise shadow |

### Tier 2 — on demand (all the detail)

| File | Content |
|---|---|
| `STATUS.md` | Live ledger: state per ticket (branch/commit/PR/test count) |
| `PLAYBOOK.md` | Codified debugging lessons |
| `SHARP_EDGES.md` | "Do not touch" invariants with the ticket that established them |
| `CONVENTIONS.md` | Confidentiality / sanitisation policy |
| `<ticket>/<ticket>.md` | Per-ticket ledgers, each self-contained |

> **Write-once discipline:** each record lives in exactly one canonical ledger; tier 1 carries a
> **pointer**, never a copy. In the original Claude Code project the trim was ~73% with no loss.

## Substitutes for scoped rules

Pi has no `.mdc`/`.claude/rules` equivalent. Options, in rising order of effort:

1. **A skill per scoped rule** whose `description` names the paths it applies to — the model loads it
   when relevant ([`../skills-plugins/`](../skills-plugins/)).
2. **`APPEND_SYSTEM.md`** for gates that must always apply (file above).
3. The **`claude-rules.ts` example extension** (Pi repo) — lists `.claude/rules/*.md` in the system prompt
   for on-demand reading.
4. A small **extension on `before_agent_start`** that injects rule text when touched paths match
   ([`../extensions/`](../extensions/)).

See also [`../context/`](../context/) and the pack
[`PI_ADAPTATION.md`](../../docs/ai-agents-code-methodology/PI_ADAPTATION.md).
