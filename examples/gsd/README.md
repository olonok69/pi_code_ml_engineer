# GSD — "Get Stuff Done" — Claude Code only (§09)

GSD is a phase-based project-management setup for Claude Code: a discuss → plan → execute → verify
cycle with durable state in `.planning/` and specialised agents (`gsd-planner`, `gsd-plan-checker`,
`gsd-executor`, `gsd-verifier`, …). Repo referenced by the sibling volumes:
<https://github.com/tomascortereal/claude-code-setup>.

## Status in Pi

| GSD piece | In Pi? |
|---|---|
| Official package | **No.** The official `get-shit-done-cc` lists "Claude Code, OpenCode, Gemini and Codex" (npm description) — **not Pi** |
| Unofficial ports | [3rd-party] `pi-gsd` ("Unofficial port", last published 2026-04-26); `@opengsd/gsd-pi` (a separate GSD-branded agent). **Untested** |
| Loading `~/.claude/skills/gsd-*` into Pi | "Works" at load time [TESTED] — but the skills call Claude tools (Task, AskUserQuestion) that Pi lacks. **Don't.** |
| discuss → plan → execute → verify | **Yes, as a discipline** — files + prompt templates + the subagent example |

**Course stance:** teach GSD as the *reference* for the productised method in Claude Code. In Pi:

1. **Phase/plan files in `data/changes/<ticket>/`** — the methodology's own durable state (not `.planning/`).
2. **Prompt templates** as the commands: `.pi/prompts/plan-phase.md` → `/plan-phase` (frontmatter
   `description`, `argument-hint`; arguments `$1`, `$@`, `$ARGUMENTS`). Example below.
3. **The plan gate:** Pi has no plan mode ("write plans to files, or build it with extensions, or install
   a package"). The simplest faithful port needs no tool: plan in a file, the human agrees, then implement.
   For an enforced read-only planning phase use the `plan-mode/` example extension (`/plan`, `--plan`,
   `Ctrl+Alt+P`; disables edit/write; bash allowlist) or [3rd-party] `@narumitw/pi-plan-mode`,
   `@plannotator/pi-extension`.
4. **The subagent example's chains** for plan-check / implement / review: `/implement`,
   `/scout-and-plan`, `/implement-and-review` ([`../subagents/`](../subagents/)).

Do not say "install GSD in Pi" — there is no official port.

## Example prompt template — `.pi/prompts/plan-phase.md`

```markdown
---
description: Write the plan for one phase into data/changes/<ticket>/ and stop for agreement
argument-hint: <ticket> <phase goal>
---
Ticket: $1. Phase goal: ${@:2}

Fill the methodology planning template (contract, provenance, root-cause probe, fix shape,
verification plan, handover outputs) into data/changes/$1/plan.md. Do not edit any other file.
Stop and ask for explicit agreement before implementing.
```

## The idea still holds

```
discuss → plan (gate) → execute → verify (evidence)
```

GSD embodies plan → agree → implement and verify-with-evidence. The Part 2 project does **not** use GSD
day to day (it runs the 11 stages + `data/changes/`); GSD shines on **multi-component greenfield**.
In Pi, replicate the gates without the package.
