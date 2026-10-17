# Pi — A course in three parts (deck + guides)

> **The Pi volume of a course series.** Same course, same method, different tool:
>
> | Volume | Tool | Folder |
> |---|---|---|
> | 1 | Claude Code | [`../claude_code_ml_engineer`](../claude_code_ml_engineer/README_EN.md) |
> | 2 | Cursor | [`../cursor_code_ml_engineer`](../cursor_code_ml_engineer/README_EN.md) |
> | 3 | **Pi** | this repo |
> | 4 (upcoming) | GitHub Copilot | `copilot_code_ml_engineer` (not published yet) |
>
> Links to sibling volumes assume the folders sit side by side.

Material for a **course/workshop** on **Pi** — the minimal terminal coding agent (`pi`, npm package
`@earendil-works/pi-coding-agent`, formerly `badlogic/pi-mono`). A single presentation (`.pptx`) with
**three distinct parts**, two written guides, a demo runbook, and real, runnable examples. Aimed at
**developers**. Every Pi claim was checked against **Pi 1.3.0 on 17 October 2026** and is traceable to
[`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md).

Why Pi is an interesting third volume: Claude Code and Cursor ship permission prompts, subagents and plan
mode as product features. Pi deliberately **doesn't** ("What we didn't build": no permission popups, no
sub-agents, no plan mode) and hands you a TypeScript extension API instead. Porting the methodology to Pi
separates what was **discipline** from what was **product convenience**.

- **Part 1 — Pi:** install, auth and modes (interactive, print `-p`, JSON, RPC, SDK) · providers and
  models · memory (`AGENTS.md` walk-up, `AGENTS.override.md`, `CLAUDE.md` fallback, `SYSTEM.md` /
  `APPEND_SYSTEM.md` — no nested-subdir loading, no scoped rules, no `@imports`) · permissions (none by
  design → trust, `--tools`, extensions, containers) · sessions (tree JSONL, `/tree` `/fork` `/clone`
  `/export` `/share`) · context window + compaction · prompt caching · **MCP (built in since 0.99)** ·
  skills (`/skill:name`), prompt templates and packages · subagents (not built in) · **extensions as
  hooks** · automation (print/JSON/RPC/SDK in CI and their gotchas).
- **Part 2 — The methodology (tool-agnostic):** the real 11-stage workflow with gates · tool prevalence
  (CodeGraph, Serena, oracles) · the five-check outbound gate · the transfer — **from Claude Code to Pi**
  ([`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md) + a ready-to-copy
  [`pi/`](./docs/ai-agents-code-methodology/pi/) surface) · machine sync **and the shared engineering
  record over S3**.
- **Part 3 — The ticket knowledge graph:** the same case built with **graphify** — corpus with manifest,
  `kg-refresh` pipeline, zero-LLM `kg` query, the real graph (507 nodes · 35 communities, pseudonymised).
  The `kg` skill works in Pi unchanged; `kg-refresh` needs subagents for its extraction step (extension,
  or keep that step in Claude Code).

## Contents

| File | What it is |
|---|---|
| [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) | Speaker guide: narrative per slide + closing one-liners 🗣️ + links to the code. |
| [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | Copy-paste implementation reference (configs, commands, code), sections 1–16 + the **Claude Code → Cursor → Pi** equivalence table. |
| [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) | Live-demo cheatsheet: preflight, command per slide, timings, common failures. |
| [`presentation/Pi_Presentation.pptx`](./presentation/) | The deck (16:9, 36 slides), same visual system as the sibling decks. |
| [`presentation/build_pptx_pi.py`](./presentation/build_pptx_pi.py) | Generator for the deck (regenerable). |
| [`AGENTS.md`](./AGENTS.md) + [`.pi/`](./.pi/) | This repo's own Pi surface: lean orientation, live skills, the git-gate extension, MCP. |
| [`examples/`](./examples/) | Real artifacts adapted for Pi, grouped by course section. |
| [`docs/`](./docs/) | **Reference**: the methodology pack (with the Pi adaptation), the knowledge graph, sync runbooks, and the research notes. |

### Naming choices (English-only volume)

The Claude Code and Cursor volumes are bilingual: Spanish originals plus `_EN` copies. **This volume is
English only**, so files use plain names and the Spanish names were translated rather than suffixed:

| Sibling volumes | This volume |
|---|---|
| `README_EN.md` | `README.md` |
| `GUIA_TECNICA_EN.md` | `TECHNICAL_GUIDE.md` |
| `GUIA_PRESENTACION_EN.md` | `SPEAKER_GUIDE.md` |
| `DEMO_RUNBOOK_EN.md` | `DEMO_RUNBOOK.md` |
| `ejemplos/` (`metodologia_en/`) | `examples/` (`methodology/`) |
| `presentacion/` | `presentation/` |
| `Cursor_Presentacion_EN.pptx` | `Pi_Presentation.pptx` |

## Examples (by course section)

**Part 1:**
- [`examples/agents-md/`](./examples/agents-md/) — two-tier `AGENTS.md`, `AGENTS.override.md`, `APPEND_SYSTEM.md` (§02).
- [`examples/permissions/`](./examples/permissions/) — no allowlist by design: trust, `--tools` / `defaultTools`, containers, `settings.json.example` (§02).
- [`examples/context/`](./examples/context/) — compaction, `/compact`, `/tree`, lean levers (§03).
- [`examples/prompt-caching/`](./examples/prompt-caching/) — the caching mechanism (Anthropic API demo) + what Pi controls (§03).
- [`examples/mcp/`](./examples/mcp/) — `mcp.json` with `exposure` / `toolExposure` (§04).
- [`examples/skills-plugins/`](./examples/skills-plugins/) — skills under `.pi/skills/` incl. the real project's `day`, `atlassian` (read-only Jira/Confluence) and `evidence` (read-only run evidence); their tools are in [`examples/methodology/tools/`](./examples/methodology/tools/) (§05).
  **Live in this repo:** [`.pi/skills/`](./.pi/skills/) (`audit`, `audit-python`, `deploy-staging`).
  **Demo targets:** [`ex_npm/`](./ex_npm/) (`/skill:audit`) · [`ex_app/`](./ex_app/) (`/skill:audit-python`) · [`ex_staging/`](./ex_staging/) (`/skill:deploy-staging`).
- [`examples/subagents/`](./examples/subagents/) — read-only agent files for the subagent example extension + the extension-vs-parallel-processes diagram (§06).
- [`examples/extensions/`](./examples/extensions/) — the hooks analogue: the **tested** `block-external-git.ts` + untested patterns (§07). **Live:** [`.pi/extensions/`](./.pi/extensions/).
- [`examples/automation/`](./examples/automation/) — print/JSON/RPC/SDK, and a GitHub Actions **pattern** (not an official action) (§07).

**Part 2:**
- [`examples/methodology/`](./examples/methodology/) — the 11-stage flow, one end-to-end example, tool prevalence, the five-check outbound gate, the ops runbook (machine sync → shared record), the flow diagram; plus the real `tools/` (atlassian, evidence) and `s3-sync/` scripts (§08, §11).
- [`examples/gsd/`](./examples/gsd/) · [`examples/codegraph/`](./examples/codegraph/) · [`examples/serena/`](./examples/serena/) — the method's tools in Pi (§09).
- [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) — the portable starter kit: [`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md) + [`pi/`](./docs/ai-agents-code-methodology/pi/) (`AGENTS.md.example`, `mcp.json.example`, `settings.json.example`, `extensions/block-external-git.ts`, skills `day`, `atlassian`, `evidence`, `kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff`). The Cursor and Copilot adaptations ship in the same pack (§10).
- [`docs/synchro/`](./docs/synchro/) — sync runbooks: `machine-sync/`, `laptop-to-main/`, and `s3-sync/` (§11).

**Part 3:**
- [`docs/knowledge-graph/`](./docs/knowledge-graph/) — design, scripts (`kg_query.sh`, `kg_refresh.sh`, `build_manifest.py`, `stage_corpus.py`), tests, manifest and the real output (`output/graph.html` + `GRAPH_REPORT.md`) (§12).
- [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) — narrative summary.
- [`presentation/kg_graph.png`](./presentation/) — the graph capture used in the deck.

## Regenerating the deck and diagrams

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_pi.py   # -> presentation/Pi_Presentation.pptx
uv run --with pillow python examples/methodology/render_flow.py                # -> examples/methodology/flow.png
uv run --with pillow python examples/subagents/render_agents.py                # -> examples/subagents/agents.png
uv run --with playwright python presentation/capture_kg_graph.py               # -> presentation/kg_graph.png (needs Chrome + network for the vis CDN)
```

## Technology documentation

| Technology | Role in the course | Documentation |
|---|---|---|
| **Pi** | The tool (Part 1) | <https://pi.dev/docs/latest> · [source](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) · [changelog](https://pi.dev/changelog) · [packages](https://pi.dev/packages) |
| **Agent Skills** | Skill format Pi implements (§05) | <https://agentskills.io> |
| **MCP** | The connection standard (§04) | <https://modelcontextprotocol.io> |
| **CodeGraph** | The code graph (§09) | <https://colbymchenry.github.io/codegraph/> · [repo](https://github.com/colbymchenry/codegraph) |
| **Serena** | Semantic LSP navigation (§09) | <https://github.com/oraios/serena> |
| **GSD** | The productised method — Claude Code only (§09) | <https://github.com/tomascortereal/claude-code-setup> |
| **graphify** | The ticket knowledge graph (Part 3) | <https://graphify.net> · [repo](https://github.com/Graphify-Labs/graphify) |
| **Playwright MCP** | Contract verification (§09) | <https://github.com/microsoft/playwright-mcp> |
| **Context7** | Up-to-date library docs (§09) | <https://context7.com> |

## Sources

Pi docs <https://pi.dev/docs/latest>, homepage <https://pi.dev>, changelog <https://pi.dev/changelog>,
source <https://github.com/earendil-works/pi>, npm
<https://www.npmjs.com/package/@earendil-works/pi-coding-agent>, Pi 1.0 announcement
<https://earendil.com/posts/pi-1-0/> — **verified 2026-10-17, Pi 1.3.0. Pi moves fast (1.0 shipped
2026-10-01, four releases since); re-check before reuse.** Markers used throughout: **[TESTED]** (run
locally), **[3rd-party]** (community package, untested), **NOT DOCUMENTED**. Full notes:
[`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md).

> Examples derived from a real professional project are **sanitised**: ticket keys are pseudonymised
> (`TKT-1xx`), client names replaced (`ClientX`), no account IDs, bucket names, emails or secrets. The
> Confluence publication pack that ships with the Cursor volume was left out of this one.
