# Tool prevalence — what Pi uses and when

`AGENTS.md` and `APPEND_SYSTEM.md` do not only say *what* to do; they say **which tool**
and in what order. That turns "I have MCP installed" into "the agent pulls the right tool."

## The golden rule: graph navigation before reading files

> **"For 'what is this / who depends / what do I touch', a `codegraph_explore` **first** — source + call
> paths + blast radius + test-coverage flags in one call (treat the source it returns as ALREADY
> read; do not re-open it). Serena `find_referencing_symbols` for the **precise** check before renaming or
> deleting a helper (disambiguates by class). grep/Read only for literals."** — rule in
> `AGENTS.md`. In Pi the rule alone is not enough: MCP tools default to `codemode` exposure (not
> declared to the model), so `.pi/mcp.json` sets `codegraph_explore` and Serena's
> `find_referencing_symbols` to **`toolExposure: direct`** — otherwise "reach for it unprompted" weakens.

> **Two graphs, two domains.** CodeGraph indexes the *code*; the **`kg`** skill (graphify) indexes
> *project memory* (tickets, sharp edges). Detail: [`../../docs/KNOWLEDGE_GRAPH.md`](../../docs/KNOWLEDGE_GRAPH.md).

## Prevalence table

| I need… | Preferred tool | Why / rule |
|---|---|---|
| Survey: what is / who depends / blast / tested? | **CodeGraph** `codegraph_explore` | 1 query; treat as ALREADY read |
| Precise check before rename/delete | **Serena** `find_referencing_symbols` | Mandatory; disambiguates by class |
| Body / overview of a large file | Serena `find_symbol` / `get_symbols_overview` | Or the source from `explore` |
| Output contract | **Playwright** / F12 | What the consumer sees |
| Deployed runtime | **Docker** (same image) | Green tests ≠ what was shipped |
| Cheap root cause | **Oracle** (`_diag_*.py` / parser) | No model call to diagnose |
| Cloud logs / config | **AWS CLI** (read-only) | First-class debugging |
| Library docs | **Context7** | Vs training cutoff |
| git / PRs | `gh`, `git` | status-first |
| Tickets / lessons in the area | **Skill `kg`** (or STATUS fallback) | history-first before grep |
| Live ticket status / a wiki page | **Skill `atlassian`** ([`tools/atlassian/`](./tools/atlassian/)) | GET only, enforced in code; tickets and Confluence are written by the person (Confluence: plan → diff → OK per page) |
| Evidence of a failed run | **Skill `evidence`** ([`tools/README.md`](./tools/README.md)) | The log line is the index; S3 version chosen by time window, not the current one; read-only |
| Independent parallel work | **Subagent example extension** or parallel `pi -p` processes | Not built in; without cluttering the main thread ([`../subagents/`](../subagents/)) |

## Install and smoke

Runbook to configure the 5 tools (CodeGraph, Serena, Playwright, Context7, kg) and try them:
[`../../docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md`](../../docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md)
(written for the other agents; in Pi register the servers with `pi mcp add` / `.pi/mcp.json` — see
[`../mcp/`](../mcp/)) · smoke: `pi mcp list`.

## The order (cheap → expensive)

1. Orientation: `STATUS.md` + `git`/`gh` + skill **`kg`**
2. Navigation: CodeGraph → Serena
3. Diagnosis: deterministic oracle
4. Environment: AWS CLI
5. Contract: Playwright
6. Outbound: wrapper + Docker
7. Only at the end: model call to verify the fix

## Skills vs oracles

| | **Skills / MCP** | **Oracles** (`_diag`, parser) |
|---|---|---|
| What it is | Registered capability (auto-select by `description`) | Code the agent writes and runs with `bash` |
| Where (Pi) | `.pi/skills/` · `~/.pi/agent/skills/` · MCP | `data/changes/<ticket>/` (gitignored) or `src/`/`tests/` |
| Examples | `kg`, `sanitise-diff`, Serena, CodeGraph, Playwright | `_diag_pdf.py` |

In Claude Code `/kg` lived in `~/.claude/skills/`. In Pi the **same `SKILL.md`** loads (unknown
frontmatter keys are ignored, [TESTED]) and is invoked as `/skill:kg`.

## Permissions (different from Claude and Cursor)

Claude Code: hand-curated allowlist in `settings.local.json` (`mcp__serena__…`, etc.).
Cursor: rules + UI approvals + hooks + `permissions.json`.

Pi: **no approval prompts and no allowlist file, by design.** Re-implement the *policy* with:

1. A **container** (Docker / Docker Sandboxes) for unattended runs.
2. The **global extension** `block-external-git.ts` for push/PR/merge/release ([`../extensions/`](../extensions/)).
3. `--tools` / `defaultTools` to drop `write`/`edit` in review sessions.
4. MCP `toolExposure: hidden` for destructive MCP tools.
5. Project trust `ask` (the default).

Details: [`../permissions/`](../permissions/).
