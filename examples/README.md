# Examples for the Pi volume

Same structure as the `ejemplos/` folders of the sibling volumes (Claude Code, Cursor), rewritten for
**Pi** (1.3.0, verified 2026-10-17). The methodology and the tool roles (CodeGraph, Serena,
Playwright, graphify) stay; the product *surface* changes (context files, skills, MCP exposure,
extensions, modes). Every Pi claim traces to
[`../docs/research/PI_FINDINGS_2026-10-17.md`](../docs/research/PI_FINDINGS_2026-10-17.md).

Full adaptation guide: [`../docs/ai-agents-code-methodology/PI_ADAPTATION.md`](../docs/ai-agents-code-methodology/PI_ADAPTATION.md).

## Index (mapped to the course sections)

| Folder | § | Claude Code topic | Pi equivalent |
|---|---|---|---|
| [`agents-md/`](./agents-md/) | 02 | Two-tier `CLAUDE.md` | `AGENTS.md` walk-up (one per dir) + `APPEND_SYSTEM.md` for gates + `AGENTS.override.md` |
| [`permissions/`](./permissions/) | 02 | Allowlist `settings.local.json` | **None by design** — containers, extensions, `--tools`/`defaultTools`, MCP `hidden`, project trust; `settings.json.example` |
| [`context/`](./context/) | 03 | Context window / `/compact` | `/compact [instructions]` + `compaction.*`, `/tree`, `/fork`, lean levers |
| [`prompt-caching/`](./prompt-caching/) | 03 | Caching in Claude Code | Automatic markers; `PI_CACHE_RETENTION`, `cacheWarming`, `showCacheMissNotices` + API demo |
| [`mcp/`](./mcp/) | 04 | `.mcp.json` + `claude mcp add` | `.pi/mcp.json` + `pi mcp add`; `codemode` default vs `toolExposure: direct` |
| [`skills-plugins/`](./skills-plugins/) | 05 | Slash commands + skills + plugins | Agent Skills (`/skill:name`), prompt templates, `pi install` packages; `day`, `atlassian`, `evidence`, `preview`, `audit*`, `deploy-staging` |
| [`subagents/`](./subagents/) | 06 | Task + Agent Teams | **Not built in** — subagent example extension, parallel `pi` processes, [3rd-party] packages |
| [`extensions/`](./extensions/) | 07 | Hooks (`exit 2`) | TypeScript extensions: `pi.on("tool_call") → { block: true, reason }` — the [TESTED] git gate |
| [`local-models/`](./local-models/) | 01 | Model choice (cloud) | Local models on a 4 GB GPU: llama.cpp router preset, Ollama/LM Studio `models.json`, small-model settings, agent/server comparison |
| [`automation/`](./automation/) | 07 | `claude -p` + Agent SDK | `pi -p` (`</dev/null`, `--approve`), `--mode json`, `--mode rpc`, SDK, CI pattern |
| [`methodology/`](./methodology/) | 08, 11 | 11-stage flow | Same flow + Pi surface; `tools/` (read-only Jira/Confluence + evidence core, with tests); `s3-sync/` scripts |
| [`codegraph/`](./codegraph/) · [`serena/`](./serena/) | 09 | MCP in Claude | Same servers via Pi MCP (`direct` exposure) |
| [`gsd/`](./gsd/) | 09 | GSD plugin | **Claude Code only** — plan files + prompt templates; [3rd-party] `pi-gsd` unofficial |

Parts 2–3 reference material (methodology pack, knowledge graph, sync runbooks) lives in [`../docs/`](../docs/).

## Live in this repo

Root [`../.pi/`](../.pi/): skills `audit`, `audit-python`, `deploy-staging` · extension
`block-external-git.ts` · `mcp.json` (context7 + playwright, `deferred`). Demo targets: `../ex_npm/`,
`../ex_app/`, `../ex_staging/`. Trust the folder first (`/trust`).

## What is NOT there (or differs) — read before copying blindly

| Claude Code capability | In Pi |
|---|---|
| `CLAUDE.md` + `@import` + nested files + auto-memory | `AGENTS.md`/`CLAUDE.md` in cwd **and ancestors only**, one per directory (`AGENTS.md` wins); `@import` NOT DOCUMENTED; **no** memory |
| `.claude/rules/` (scoped) | None — skill, `APPEND_SYSTEM.md`, `claude-rules.ts` example, or an extension |
| Allowlist + approval prompts | **None** ("No permission popups") — container + extensions |
| Plan mode | None — plan file + human OK, or the `plan-mode/` example |
| Subagents + Agent Teams | None built in — example extension / packages / tmux |
| Hooks (`settings.json`, `exit 2`) | TypeScript extensions (`tool_call`, `tool_result`, `before_agent_start`, …) |
| `/plugin install` | `pi install npm:…` · gallery pi.dev/packages |
| `/name` for a skill | `/skill:name` |
| `claude -p` stdin pipe | `pi -p` — piped stdin is prepended; a never-closed stdin hangs it → `</dev/null` |
| GSD | Not supported (unofficial [3rd-party] `pi-gsd`, untested) |
| MCP tools visible by default | Default `codemode` hides them; set `toolExposure: direct` |

What **does** travel almost unchanged: MCP config shape (`mcpServers`), the 11-stage discipline,
`data/changes/` ledgers, `_diag_*.py` oracles, Playwright for the contract, Docker for the outbound
gate, and `SKILL.md` files (unknown frontmatter keys are ignored, [TESTED]).
