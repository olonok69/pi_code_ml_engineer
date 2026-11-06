# Pi — Technical implementation guide (course in three parts)

> Copy-paste reference for building each piece. It complements
> [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) (the narrative thread) with the **how**.
> All runnable artifacts are in [`examples/`](./examples/); [`docs/`](./docs/) is reference material from a
> real installation. Sibling volumes, same structure and section numbering:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer/blob/master/GUIA_TECNICA_EN.md) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer/blob/main/GUIA_TECNICA_EN.md) (sibling folders; links assume the volumes
> sit side by side).
>
> **Verification note:** every Pi claim was checked on **17 October 2026** against **Pi 1.3.0**
> (`@earendil-works/pi-coding-agent`, released 2026-10-15) — docs at <https://pi.dev/docs/latest>, source on
> `main`, and a local install. The research notes are in
> [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md). Markers used
> below: **[TESTED]** = run locally · **[3rd-party]** = community package, untested · **NOT DOCUMENTED** =
> no source. **Pi moves fast** (1.0 shipped 2026-10-01; four releases since) — re-check before reuse.

## Table of contents

**Part 1 — Pi**

1. [Installation, auth, modes and models](#1-installation-and-cli)
2. [Memory: AGENTS.md, SYSTEM.md and (no) auto-memory](#2-memory)
3. [Permissions: none by design](#3-permissions)
4. [Sessions: a tree in a JSONL file](#4-sessions)
5. [Context window and compaction](#5-context-window)
6. [Prompt caching](#6-prompt-caching)
7. [MCP (built in since 0.99)](#7-mcp)
8. [Skills, prompt templates and packages](#8-skills-and-packages)
9. [Subagents: not built in](#9-subagents)
10. [Extensions = hooks](#10-extensions-hooks)
11. [Automation: print, JSON, RPC, SDK, CI](#11-automation)

**Part 2 — The methodology**

12. [The workflow and the real example](#12-methodology)
13. [The tools: CodeGraph, Serena, GSD](#13-the-methods-tools)
14. [Transferring the methodology (from Claude Code to Pi)](#14-transferring-the-methodology)
15. [Machine sync (tarball + S3)](#15-machine-sync)

**Part 3 — The ticket knowledge graph (graphify)**

16. [Ticket knowledge graph](#16-ticket-knowledge-graph)

**Appendix**

- [A. Equivalence table: Claude Code → Cursor → Pi](#a-equivalence-table-claude-code--cursor--pi)
- [B. Gotchas checklist](#b-gotchas-checklist)
- [C. Sources](#c-sources)

---

# PART 1 — Pi

What Pi is, in one paragraph: a **minimal terminal coding agent** ("AI agent toolkit: unified LLM API,
agent loop, TUI, coding agent CLI"), started as `badlogic/pi-mono` by Mario Zechner, now
`github.com/earendil-works/pi`, MIT-licensed, maintained by Earendil Inc. It ships a small system prompt,
four default tools (`read`, `bash`, `edit`, `write`) and a TypeScript extension API — and deliberately
**skips** permission popups, sub-agents and plan mode. Its homepage calls that list "What we didn't build".
That design choice shapes every section below.

> ⚠️ **Name and package moved.** `@mariozechner/pi-coding-agent` is deprecated (2026-05-07) in favour of
> **`@earendil-works/pi-coding-agent`**; the binary is still `pi`. Old tutorials and extension imports use
> the old scope.

## 1. Installation and CLI

```bash
curl -fsSL https://pi.dev/install.sh | sh                          # macOS/Linux; pins deps; later: pi update
powershell -c "irm https://pi.dev/install.ps1 | iex"               # Windows
npm install -g --ignore-scripts @earendil-works/pi-coding-agent    # Node >= 22.19; does NOT pin transitive deps
nix profile add github:earendil-works/pi/stable                     # Nix
pi --version                                                        # [TESTED] -> 1.3.0

pi update              # Pi itself      · pi update --extensions   # packages
pi update --models     # model catalogue · pi update --all          # both
```

Uninstall with `npm uninstall -g @earendil-works/pi-coding-agent` or by re-running the installer; neither
removes `~/.pi/agent/` (your settings, sessions and credentials).

### Authentication

```bash
cd my-project && pi
# inside Pi:
/login        # pick a provider: OAuth subscription or API key -> saved in ~/.pi/agent/auth.json
/model        # pick a model
```

- **CI / scripts:** use environment keys — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`, `XAI_API_KEY`, … (about 40 providers).
- **Precedence:** `--api-key` → `auth.json` → `models.json` `apiKey` → environment / ambient cloud credentials.
- **Secret manager:** an `auth.json` key can be a command, e.g.
  `{"anthropic":{"type":"api_key","key":"!security find-generic-password -ws 'anthropic'"}}` (output cached
  for the life of the process).
- **Bedrock** uses ambient AWS credentials (`AWS_PROFILE`, access keys, `AWS_REGION`, ECS task credentials,
  IRSA). Vertex AI, Azure (`azure`), Cloudflare and Earendil's own gateway **Radius** (`/login radius`,
  early alpha) are also there.
- **Subscriptions:** the docs say "a supported subscription → `/login`" but publish **no list** —
  **NOT DOCUMENTED**. Mentioned: "Sign in with ChatGPT" for `openai`; a `warnings.anthropicExtraUsage`
  setting; and the containerisation page passing a token from `claude setup-token` as `ANTHROPIC_OAUTH_TOKEN`.
- **Local models:** built-in llama.cpp router (`/llama`); Ollama, LM Studio, vLLM, SGLang via
  `~/.pi/agent/models.json`:

```json
{"providers":{"ollama":{"baseUrl":"http://localhost:11434/v1","api":"openai-completions","apiKey":"ollama","models":[{"id":"qwen2.5-coder:7b"}]}}}
```

Small-GPU walkthrough (4 GB VRAM: preset, `models.json`, compaction settings, agent and server
comparison): [`examples/local-models/`](./examples/local-models/).

### Models and thinking

| Where | How |
|---|---|
| TUI | `/model` or `Ctrl+L` select · `Ctrl+P` cycle · `/scoped-models` · `/thinking` or `Shift+Tab` |
| CLI | `--model sonnet:high` (fuzzy name + `:<thinking>`), `--provider`, `--thinking <level>`, `--models <patterns>`, `--list-models [search]` |
| Settings | `defaultThinkingLevel` (default `"medium"`), `modelThinkingLevels`, `thinkingBudgets` |

Thinking levels: `off | minimal | low | medium | high | xhigh | max`, clamped to what the model supports.
Sessions record model/thinking changes and restore them on resume.

### Modes

| Mode | Command | Notes |
|---|---|---|
| Interactive TUI | `pi` | Fullscreen by default; `--tui-mode regular` keeps normal scrollback |
| Print | `pi -p "…"` | Prints the final assistant text; **non-zero exit** on `error`, `aborted`, `length` |
| JSON events | `pi --mode json "…" > events.jsonl` | Session header + JSONL events; a failed run does **not** by itself exit non-zero |
| RPC | `pi --mode rpc [--no-session]` | Long-lived; JSONL commands on stdin (`prompt`, `steer`, `follow_up`, `abort`, `get_state`, `compact`, `fork`, `set_model`, …) |
| SDK | `createAgentSession()` | In-process, Node or Bun (§11) |

Handy pieces: `@path` adds a file to the first prompt; piped stdin is **prepended** to the first prompt;
`--` ends option parsing; in the TUI `!cmd` runs a shell command and sends the output to the model, `!!cmd`
runs it without sending.

> ⚠️ **[TESTED] gotcha:** when stdin is a pipe that is never closed (CI runners, agent harnesses),
> `pi -p "…"` waits for EOF and looks hung. Always: `pi -p "…" </dev/null`.

---

## 2. Memory

### Context files — how Pi finds them

| | Rule (from source `resource-loader.ts`) |
|---|---|
| Global | `~/.pi/agent/` (or `$PI_CODING_AGENT_DIR`) |
| Project | the working directory **and every parent directory** up to `/` |
| Not loaded | directories **below** cwd — no nested, most-specific-wins discovery |
| Candidates, in precedence | `AGENTS.override.md` > `AGENTS.md` > `AGENTS.MD` > `CLAUDE.md` > `CLAUDE.MD` |
| Per directory | **only the first existing file** is loaded |
| Order in the prompt | global first, then ancestors from `/` down to cwd, each wrapped in `<project_instructions path="…">` |
| Trust | context files load **regardless of project trust**; disable with `-nc` / `--no-context-files` |

### What is different from Claude Code and Cursor

| Feature | Claude Code | Cursor | Pi |
|---|---|---|---|
| Nested files in sub-directories | yes (loaded when working there) | yes, most specific wins | **no** — ancestors only |
| Scoped rules (globs / paths) | `.claude/rules/` | `.cursor/rules/*.mdc` | **none native** |
| `@imports` inside the file | yes | — | **NOT DOCUMENTED** — treat AGENTS.md as plain text with pointers |
| Reads `CLAUDE.md` | yes | yes (compat) | yes, as a **fallback name**; `AGENTS.md` in the same directory **shadows it** |
| Reads `~/.claude/CLAUDE.md` | yes | — | **no** — symlink or copy into `~/.pi/agent/` |
| Auto-memory | `MEMORY.md` | Memories | **none built in** |

Consequences you will hit:

- A repo holding both a (gitignored) `CLAUDE.md` and an `AGENTS.md` gives Pi **only `AGENTS.md`**. Merge them,
  or use `AGENTS.override.md` deliberately ("replaces `AGENTS.md` or `CLAUDE.md` only in the same directory").
- **Ancestor leakage:** a workspace-level `CLAUDE.md` above your repo loads in every session started inside
  the repo. Useful for shared conventions; expensive if it is long.
- A nested git **worktree** does not load the main repo's copy of the same file twice.

### Scoped-rule substitutes

1. A **skill** whose `description` names the paths it applies to (loaded only when relevant, §8).
2. The `claude-rules.ts` **example extension** — lists `.claude/rules/*.md` in the prompt for on-demand reading.
3. `APPEND_SYSTEM.md` for the few always-on gates.
4. A `before_agent_start` **extension** that injects rule text when touched paths match (§10).

### System prompt files

| File | Effect |
|---|---|
| `~/.pi/agent/SYSTEM.md` or `.pi/SYSTEM.md` | **Replaces** Pi's default system prompt |
| `~/.pi/agent/APPEND_SYSTEM.md` or `.pi/APPEND_SYSTEM.md` | **Appends** to it |
| `--system-prompt <text\|path>` / `--append-system-prompt <text\|path>` (repeatable) | CLI equivalents |

The trusted project file wins over the agent-directory file of the same name; the two are **not combined**.

### Two-tier pattern (see [`examples/agents-md/`](./examples/agents-md/))

```
~/.pi/agent/AGENTS.md          # tier 1, global: who you are, the non-negotiable gates (Pi's ~/.claude/CLAUDE.md)
<repo>/AGENTS.md               # tier 1, project: small, pointers + tool order + output contract
<repo>/data/changes/**         # tier 2: per-ticket detail, read on demand (unchanged)
<repo>/data/changes/s3-sync/IDENTITY.md   # tier 0: machine role, machine-local (unchanged)
```

### Cross-session memory

There is **no built-in memory feature**. Pi's homepage puts long-term memory in extensions ("inject
messages before each turn, filter the message history, implement RAG, or build long-term memory").
The methodology's substitute needs nothing new: write-once ledgers (`STATUS.md`, `FOLLOWUPS.md`,
`SHARP_EDGES.md`) + `pi -c` / `/resume` + the session JSONL files, which are greppable
(`PI_SESSION_FILE` is exported to shell tools). [3rd-party]: `pi-memory`, `pi-hermes-memory`,
`pi-observational-memory` — untested.

---

## 3. Permissions

**Pi has no approval prompts and no sandbox — on purpose.** Quickstart: "It does not ask before every
tool call." Security page: Pi "can read, change, and execute files with the permissions of the account
that started it". Homepage: **"No permission popups — Run in a container, or build your own confirmation
flow with extensions."** Its security policy lists "lack of a built-in sandbox" and prompt injection as
**out of scope**.

### What exists instead — five layers

| # | Layer | What it controls | How |
|---|---|---|---|
| 1 | **Project trust** | Whether a folder's *resources* load (`.pi/settings.json`, `.pi/mcp.json`, `.pi/extensions\|skills\|prompts\|themes`, `.pi/SYSTEM.md`, `.agents/skills`) | `/trust`, saved in `~/.pi/agent/trust.json`; `defaultProjectTrust: "ask" \| "always" \| "never"` (user settings only; default `"ask"`). **Does not sandbox tool calls**; context files load regardless. |
| 2 | **Static tool restriction** (by tool *name*) | Which tools exist | `--tools read,grep,find,ls` (allowlist) · `--exclude-tools` · `-nbt` / `-nt` · `defaultTools` with `+name` / `-name` · MCP `exposure: "hidden"` / `toolExposure` |
| 3 | **Content gates** | What a call may do | Extensions: `pi.on("tool_call") → { block: true, reason }` (§10). Shipped examples: `permission-gate.ts` (confirms `rm -rf`, `sudo`, `chmod 777`; **blocks by default with no UI**), `protected-paths.ts`, `confirm-destructive.ts`, `dirty-repo-guard.ts`, `plan-mode/`, `sandbox/` (OS sandbox via `@anthropic-ai/sandbox-runtime`) |
| 4 | **Isolation** | Blast radius of everything | Plain Docker (mount only the workspace, **never** host `~/.pi/agent`) · Docker Sandboxes (`sbx run --kit "docker.io/sbx/pi-kit:latest" pi`; the real key stays on the host) · NVIDIA OpenShell · Gondolin micro-VM extension (built-in tools + `!` in a VM; the Pi process and other extension tools stay on the host) |
| 5 | **The method** | What the agent is asked to do | AGENTS.md gates; the human owns external actions |

A `tool_call` handler that **throws** blocks the tool — "as a fail-safe".

### Non-interactive modes and trust

Print, JSON and RPC modes **cannot show the trust prompt**. With the default `"ask"`, project `.pi/`
resources — including `.pi/mcp.json` and `.pi/extensions` — are **skipped silently** unless you pass
`--approve` / `-a` (or `--no-approve` / `-na` to make the choice explicit). Global `~/.pi/agent/` resources
still load. Gotcha: the project `sessionDir` setting is read *before* trust is resolved.

### Compared with Claude Code and Cursor

```
Claude Code   settings.json allow/deny (mcp__s__t, Bash(…)) + prompts + optional sandbox
Cursor        permissions.json mcpAllowlist / terminalAllowlist + approvals + hooks.json
Pi            no prompts, no allowlist file -> trust (resources) + --tools/defaultTools (names)
              + extensions (content) + containers (blast radius)
```

Do not look for the allowlist. Re-implement the **policy**: global `block-external-git.ts`
([`examples/extensions/`](./examples/extensions/)), `--tools` without `edit`/`write` for review sessions,
`exposure: "hidden"` for destructive MCP tools, a container for anything unattended. Worked notes:
[`examples/permissions/`](./examples/permissions/). [3rd-party] options: `@gotgenes/pi-permission-system`,
`pi-permission-modes` (bubblewrap/sandbox-exec + allow/ask/deny + bash AST gating), `@czottmann/pi-automode`,
`@erichll/pi-auto-review`.

---

## 4. Sessions

| Topic | Pi |
|---|---|
| Storage | `~/.pi/agent/sessions/--<path>--/<timestamp>_<session-id>.jsonl` (`<path>` = cwd with `/`, `\`, `:` → `-`) |
| Location override | `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > `sessionDir` setting; `--no-session` = ephemeral |
| Format | JSONL **tree**: entries carry `id` + `parentId`; header `version` 3; entry types include messages, model/thinking changes, `compaction`, `branch_summary`, `custom`, `context_edit`, `usage` |
| Resume | `pi -c` (latest for this cwd) · `pi -r` / `/resume` (picker: search, rename, `Ctrl+D` delete) · `--session <path\|id>` · `--session-id` · `-n` / `/name` · `/session` (file, ID, counts, tokens, cost) · `/new` |
| Branch | `/tree` (move within the same file; can summarise the branch you leave) · `/fork` (new session from an earlier user message) · `/clone` (copy the active branch) · `--fork <path\|id>` · Esc-Esc = `/tree` by default (`doubleEscapeAction`) |
| Export / share | `/export [path]` (HTML or JSONL) · `pi --export <file> [out]` (HTML) · `/import <path>` · `/share` (Radius artifact if authenticated, else a private GitHub gist via `gh`; `sessionShareDestination: auto \| gist \| radius`, new in 1.3.0) · `/bug` · `/copy` / `Ctrl+X` |
| Hand-off | No cross-surface hand-off (no `--teleport`). Example extension `handoff.ts`: `/handoff <goal>` moves context into a new focused session |

Shell tools receive `PI_SESSION_ID`, `PI_SESSION_FILE`, `PI_PROVIDER`, `PI_MODEL`, `PI_REASONING_LEVEL`.

> ⚠️ `/share` uploads a transcript. In a client project, sessions contain whatever the agent read —
> treat `/share` like any other outbound action: the human decides, after sanitising.

---

## 5. Context window

- The footer shows context usage.
- **Auto-compaction** triggers when `contextTokens > contextWindow - reserveTokens`; it is also checked
  between tool batches inside a run, and there is one compact-and-retry on overflow.
- **Manual:** `/compact [instructions]` — the instructions focus the summary. Disabling auto does not
  disable the manual command.

```json
{
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "branchSummary": { "reserveTokens": 16384, "skipPrompt": false }
}
```

(`compaction.modelOverrides` sets per-`provider/modelId` values.)

**How it works:** older messages are summarised into a `CompactionEntry` (`summary`, `firstKeptEntryId`,
`tokensBefore`, `details.readFiles/modifiedFiles`); the original entries **stay in the file**. The summary is
structured: Goal / Constraints & Preferences / Progress / Key Decisions / Next Steps / Critical Context.
Summarisation requests **disable prompt-cache writes**.

Extension hooks: `session_before_compact` (cancel, or supply your own summary), `session_compact`,
`session_compact_failed`, `session_before_tree`. Examples: `custom-compaction.ts`, `trigger-compact.ts`.

### Keeping context lean — Pi's own levers

| Lever | Effect |
|---|---|
| Small default system prompt + 4 default tools | Low fixed cost per turn |
| Skills | Only name + description + path until used |
| MCP `codemode` (default) | Tools are **not** declared; a one-line summary per server in `mcp_servers`; `tool_search` / `deferred` load on demand |
| Codemode scripts | Filter large outputs before the model sees them |
| MCP text results > 20 KB | Middle-truncated; full text saved to a temp file |
| `/tree`, `/fork` | Side quests off the main branch |
| `--no-context-files`, `--no-skills`, `--no-extensions` | Minimal runs |

Worked notes: [`examples/context/`](./examples/context/).

---

## 6. Prompt caching

**What Pi does automatically:**

- Anthropic-format requests get `cache_control` markers on the system prompt, the last tool definition, and
  the last user / assistant / tool-result text.
- OpenAI-style requests get session affinity and `prompt_cache_key` handling; for long retention Pi sends
  `prompt_cache_retention: "24h"` (or `prompt_cache_options.ttl: "30m"` on GPT-5.6+).

**What you control:**

| Control | Effect |
|---|---|
| `PI_CACHE_RETENTION=long` | Extended retention where supported (e.g. Anthropic `cache_control.ttl: "1h"`) |
| `cacheWarming: "off" \| "streaming" \| "idle"` | Default `"streaming"`, **global only**. Keeps eligible caches warm during long runs (`idle`: between runs). Runs only if the model declares a `promptCache` lifetime and the estimated saving is ≥ $0.05; warm-up usage counts in totals. Extensions can override via `cache_warming_decision`. |
| `showCacheMissNotices: true` | Notices for cache misses, warm-ups, compaction usage |
| `/session` | Shows the next cache-warming decision |
| `models.json` `promptCache: {"short": 300, "long": 3600}` | Per-model lifetimes (+ compat fields `supportsLongCacheRetention`, `supportsExplicitPromptCacheMode`, `sessionAffinityFormat`) |

**Design choices that protect the cache:** mid-conversation prompt/tool changes are **appended** as
transcript deltas, not rewritten; MCP server summaries that change after connect are appended "so earlier
messages stay cached"; **switching models loses the cache**; since 1.3.0 a thinking-level change keeps the
cache on OpenAI GPT-6 with an API key. Usage fields: `cacheRead`, `cacheWrite`, `cacheWrite1h`.

The mechanism itself (prefix caching, TTLs, break-even) is provider-side — the demo in
[`examples/prompt-caching/`](./examples/prompt-caching/) shows it against the Anthropic API directly.

---

## 7. MCP

> ⚠️ **Course gotcha — the web is out of date.** Pi's original stance was "does not and will not support
> MCP". Since **0.99.0 (2026-09-29)** MCP is **built in** ("Added codemode, tool search, and MCP support as
> built-in extensions"); the pi.dev card now reads "No MCP → Now with MCP+Codemode". Much material online
> still says "Pi has no MCP".

### Configuration

| | |
|---|---|
| Files | `~/.pi/agent/mcp.json` (user) · `.pi/mcp.json` (project, **trusted projects only**) |
| Shape | the same `mcpServers` object as Claude Code and Cursor ("Copy the existing `mcpServers` entry") |
| Merge | a project entry with the same name replaces the user entry; an entry with no `command`/`url`/`type` only overrides `enabled`, `exposure`, `toolExposure` |
| Transports | stdio (`command`, `args`, `env`, `cwd`) · streamable HTTP (`url`, `headers`, `oauth`) · **SSE rejected** |
| Fields | `timeout`, `enabled`, `description`, `exposure`, `toolExposure`; values support `${VAR}` and `!command` |
| Tool names | `mcp__<server>__<tool>` (same as Claude Code) |
| Logs / tokens | `~/.pi/agent/mcp.log` · `~/.pi/agent/mcp-auth.json` |

```bash
pi mcp add codegraph --description "Code intelligence" -- codegraph serve --path /abs/path/to/repo --mcp   # [TESTED]
pi mcp add docs --url https://example.com/mcp --bearer-token-env-var DOCS_TOKEN
pi mcp list            # [TESTED] -> codegraph: connected, 1 tool (codemode, global) … tools: codegraph_explore
pi mcp list --json     # exits 1 on failure — usable as a CI readiness gate
pi mcp login <name>    # OAuth;  pi mcp logout | remove
/mcp                   # in the TUI
```

(The `--help` synopsis lists only `list|login|logout`; `add` and `remove` exist — **[TESTED]**.)

### Exposure modes — the decision that matters

| Mode | Meaning | Use it for |
|---|---|---|
| `codemode` (**default**) | Callable only from `codemode` JavaScript scripts (QuickJS sandbox); **not declared** as a tool | Big servers you rarely need |
| `deferred` | Loaded on demand by `tool_search` | Playwright, Context7 |
| `direct` | Declared like a built-in tool | The tools the method wants used **unprompted** |
| `hidden` | Unreachable | Destructive tools |

`toolExposure` sets this **per tool**, with globs. The methodology's trigger map ("`codegraph_explore`
first; Serena `find_referencing_symbols` before rename") only works if those tools are visible:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph", "args": ["serve", "--path", "/abs/path/to/repo", "--mcp"],
      "description": "Code intelligence: verbatim source + call paths + blast radius",
      "toolExposure": { "codegraph_explore": "direct" }
    },
    "serena": {
      "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
      "toolExposure": { "find_symbol": "direct", "find_referencing_symbols": "direct", "get_symbols_overview": "direct" }
    },
    "playwright": { "command": "npx", "args": ["-y", "@playwright/mcp@latest"], "exposure": "deferred" },
    "context7":   { "url": "https://mcp.context7.com/mcp", "exposure": "deferred" }
  }
}
```

CodeGraph is **[TESTED]**; the Serena / Playwright / Context7 args are copied from the Cursor guide and
**not tested under Pi**. No `${workspaceFolder}`-style variable is documented — use an absolute path (or
`cwd`, which resolves relative to the session directory).

### Gates, filtering, alternatives

- Every MCP call, **including calls from codemode scripts**, passes through the `tool_call` / `tool_result`
  extension handlers — your gates apply. MCP annotations (`readOnlyHint`, …) are available to them.
- `--tools` keeps MCP tools unless an entry starts with `mcp__`; `--exclude-tools 'mcp__*'` and `--no-mcp`
  remove them; `"extensions": ["-builtin:mcp"]` disables built-in MCP entirely.
- **SDK sessions do not load built-in MCP** (§11).
- Alternatives: [3rd-party] `pi-mcp-adapter` (replaces the built-in when installed); native-tool wrappers
  [3rd-party] `@henryqw/pi-codegraph`, `@vndv/pi-codegraph`, `@bacnh85/pi-serena`; or Pi's original advice —
  a CLI plus a README or skill.

Ready-to-copy: [`examples/mcp/`](./examples/mcp/) and
[`docs/ai-agents-code-methodology/pi/mcp.json.example`](./docs/ai-agents-code-methodology/pi/mcp.json.example).

---

## 8. Skills and packages

### Skills — the Agent Skills standard

| Topic | Pi |
|---|---|
| Format | a directory with `SKILL.md` (+ optional `scripts/`, `references/`, `assets/`) — agentskills.io spec |
| Locations | `~/.pi/agent/skills/`, `.pi/skills/` (trusted) · `~/.agents/skills/`, `.agents/skills/` (cwd and ancestors up to the repo root; trust-gated) · the `"skills"` setting · `--skill <path>` · packages. Discovery is recursive. |
| `.claude/skills` | **Not auto-discovered**, but can be added: `"skills": ["~/.claude/skills"]` loaded all of the author's Claude skills **[TESTED]** — and poured every description into the prompt. List directories one by one. |
| Frontmatter | `name`, `description` (**required**, ≤ 1024 chars, drives auto-loading), `license`, `compatibility`, `metadata`, `allowed-tools` (experimental), `disable-model-invocation: true` |
| Names | lowercase `a-z0-9-`, ≤ 64 chars, no leading/trailing/double hyphens. Collision → **first found wins**, with a warning. No description → not loaded. |
| Unknown keys | **ignored silently** **[TESTED]** — a Claude-only `trigger: /day` key loads fine and does nothing |
| Invocation | auto: the model `read`s `SKILL.md` when the description matches · forced: **`/skill:name [args]`** (args appended as the request) · `enableSkillCommands` (default `true`) controls `/` completion |
| Requirement | a file-read tool must be enabled |

```bash
/skill:audit                   # forced invocation
/skill:day start               # args after the name
pi --skill ./examples/skills-plugins/.pi/skills/day "start the day"
```

Live in this repo: [`.pi/skills/`](./.pi/skills/) (`audit`, `audit-python`, `deploy-staging`), against the
demo targets [`ex_npm/`](./ex_npm/), [`ex_app/`](./ex_app/), [`ex_staging/`](./ex_staging/). The methodology's
real skills (`day`, `atlassian`, `evidence`, `preview`) are in
[`examples/skills-plugins/`](./examples/skills-plugins/), their tools in
[`examples/methodology/tools/`](./examples/methodology/tools/).

### Prompt templates — Pi's slash commands

`~/.pi/agent/prompts/<name>.md` or `.pi/prompts/<name>.md` becomes `/<name>`. Frontmatter: `description`,
`argument-hint`. Arguments: `$1`, `$@`, `$ARGUMENTS`, `${1:-default}`, `${@:N}`, `${@:N:L}`. Only direct `.md`
children are loaded. This is the closest analogue to `.claude/commands/`.

```markdown
---
description: Run the day routine
argument-hint: start|end|status|baton
---
Run the day skill: $@
```

(Using a template to keep `/day` muscle memory is an **inference**, not a documented pattern.)

### Packages — Pi's marketplace

```bash
pi install npm:@scope/pkg@1.0.0     # or git:github.com/u/r@v1 | https://… | ./local ;  -l / --local = project scope
pi list · pi remove <pkg> · pi update --extensions · pi config      # pi config = TUI to toggle resources and built-ins
pi -e npm:pkg                       # try a package for one run
```

A package is an npm or git directory with `extensions/`, `skills/`, `prompts/`, `themes/` (or a `"pi": {…}`
manifest in `package.json`); the `pi-package` keyword lists it in the **gallery at <https://pi.dev/packages>**
(5,354 packages on 2026-10-17). Host packages (`@earendil-works/pi-ai`, `-agent-core`, `-coding-agent`,
`-tui`, `typebox`) go in `peerDependencies: "*"`. Project packages install only after trust.

> ⚠️ Packages run **in-process with full OS permissions** (they are extensions). Read before you install,
> pin versions, and prefer project scope for experiments.

---

## 9. Subagents

**Not built in — by design.** README: Pi "skips features like sub-agents and plan mode". Homepage: "No
sub-agents — Spawn Pi instances via tmux, or build your own with extensions, or install a package."

### Option A — the official example extension

`examples/extensions/subagent/` in the Pi repo:

- each subagent is a separate `pi` **subprocess** with an isolated context;
- modes: single `{agent, task}` · parallel `{tasks:[…]}` (max 8, 4 concurrent) · chain `{chain:[…]}` with a
  `{previous}` placeholder;
- agent definitions: Markdown with frontmatter `name`, `description`, `tools`, `model`;
- locations: `~/.pi/agent/agents/*.md` always; `.pi/agents/*.md` only with `agentScope: "project" | "both"`;
- samples `scout` (read, grep, find, ls, bash; Haiku), `planner`, `reviewer`, `worker`; workflow prompts
  `/implement`, `/scout-and-plan`, `/implement-and-review`;
- install: copy or symlink into `~/.pi/agent/extensions/subagent/`.

A **read-only** subagent is an agent file with `tools: read, grep, find, ls` — no `bash`, `edit`, `write`
(note: the shipped `scout` *does* include `bash`):

```markdown
---
name: refactor-scout
description: Read-only blast-radius survey before a rename or delete
tools: read, grep, find, ls
---
Survey every reference to the symbol you are given. Report files, call sites and risk. Never edit.
```

### Option B — disposable child processes (documented flags only)

```bash
pi -p --no-session --tools read,grep,find,ls "List every caller of parse_header and rate the risk" </dev/null
```

### Option C — packages and tmux

[3rd-party] `pi-subagents` (single-agent delegation and scripted multi-agent workflows) and its fork
`@schovest/pi-subagents`; or parallel `pi` instances in tmux panes / RPC processes. **No Agent Teams or
shared inbox** — NOT DOCUMENTED.

Templates and the decision diagram: [`examples/subagents/`](./examples/subagents/).

---

## 10. Extensions (hooks)

Pi's hooks are not a JSON file of shell commands — they are **TypeScript extensions**.

| Topic | Pi |
|---|---|
| Where | `~/.pi/agent/extensions/*.ts` or `<dir>/index.ts` · `.pi/extensions/` (trusted) · `extensions` setting · `-e` / `--extension <path \| npm:… \| builtin:mcp>` |
| Build | none — loaded through `jiti`; `/reload` hot-reloads |
| Power | **in-process, full OS permissions**; load in all modes (check `ctx.hasUI`, `ctx.mode === "tui"`) |
| Shape | `export default function (pi: ExtensionAPI) { … }` (may be async); long-lived resources start in `session_start`, clean up in `session_shutdown` |
| Block a tool | return `{ block: true, reason }` from `tool_call` (optional `terminate: true`) |
| Fail-safe | a `tool_call` handler failure **blocks** the tool |

### Events (from `extensions/types.ts`)

| Family | Events |
|---|---|
| Session / run | `session_start`, `session_shutdown`, `session_before_switch`, `session_before_fork`, `session_before_compact`, `session_compact`, `session_compact_failed`, `session_before_tree`, `session_tree`, `session_info_changed`, `project_trust`, `resources_discover`, `input`, `before_agent_start`, `agent_start`, `turn_start`, `turn_end`, `agent_end`, `agent_before_settle`, `agent_settled` |
| Messages | `message_start`, `message_update`, `message_end` |
| Context / provider | `context`, `context_with_system`, `before_provider_headers`, `before_provider_request`, `after_provider_response`, `provider_stream_event` |
| Tools | **`tool_call`** (mutate `event.input` or block), `tool_execution_start`, `tool_execution_update`, `tool_execution_end`, **`tool_result`** (composable rewrite), **`user_bash`** (the human's own `!` commands) |
| Other | `model_select`, `thinking_level_select`, `mcp_servers_change`, `cache_warming_decision`, `ui_prompt_start`, `ui_prompt_end` |

Nested calls (`ctx.executeTool`, codemode scripts, MCP) also pass through `tool_call`.

### The methodology's gate — [TESTED] on 1.3.0

[`examples/extensions/block-external-git.ts`](./examples/extensions/block-external-git.ts) (also live in
[`.pi/extensions/`](./.pi/extensions/)):

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// The human owns every external action: push, PR, merge, release, deploy.
const EXTERNAL = [
  /\bgit\s+push\b/i,
  /\bgh\s+pr\s+(create|merge|close|edit|review|comment)\b/i,
  /\bgh\s+(release|repo\s+(create|delete|edit))\b/i,
  /\bgit\s+merge\b.*\b(origin|upstream)\//i,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event) => {
    if (event.toolName !== "bash" && event.toolName !== "powershell") return undefined;
    const command = String((event.input as { command?: string }).command ?? "");
    const hit = EXTERNAL.find((re) => re.test(command));
    if (hit) {
      return { block: true, reason: `Blocked by policy: external git/PR action (${hit}). Prepare it and hand it to the human.` };
    }
    return undefined;
  });
}
```

**How it was tested:** a fake OpenAI-compatible server scripted two bash calls (`git push origin main`,
then `echo allowed-ok`); `pi -p --no-session --model fake/fake-1 -e block-external-git.ts "push it" </dev/null`.
With the extension the model received "Blocked by policy…" and the echo still ran. **Control run without
it:** the push actually executed (and failed on an empty scratch repo) — proving the gate, not the
environment, stopped it. That control run is the "canary the instrument" rule from Part 2, applied.

Install it **globally** (`~/.pi/agent/extensions/`): global extensions are not trust-gated, so a repo
cannot switch the gate off. Leave `user_bash` alone — the human owns pushes, including `!git push`.

> **Limit:** regex gating can be bypassed (`sh -c`, aliases, scripts). For stronger gates use OS isolation or
> [3rd-party] `pi-permission-modes` (tree-sitter bash AST). The same caveat applies to Cursor's and Claude
> Code's hooks.

### Cursor `hooks.json` → Pi events

```
beforeShellExecution        -> tool_call (toolName "bash"/"powershell")
beforeMCPExecution          -> tool_call (toolName "mcp__server__tool"; MCP annotations available)
beforeReadFile              -> tool_call (toolName "read")
afterFileEdit               -> tool_result / tool_execution_end
stop                        -> agent_end / agent_settled
(no equivalent)             -> before_agent_start (rewrite prompt sections), context, user_bash
```

Other API surface: `pi.registerTool({ name, label, description, parameters: Type.Object(…), execute(…) })`
(TypeBox), `pi.registerCommand`, `registerShortcut`, `registerFlag`, `sendUserMessage`, `sendMessage`,
`appendEntry`, `setActiveTools`, `registerProvider`, `registerMcpServer`, `registerVirtualModel`,
`registerToolRenderer`, `pi.events`; UI via `ctx.ui.confirm`, `select`, `input`, `notify`, `setStatus`,
`setWidget`, `custom`. More patterns: [`examples/extensions/`](./examples/extensions/).

---

## 11. Automation

### Print mode in CI

```bash
pi -p --no-session --approve --model anthropic/<id> "review the diff" </dev/null
```

- Key from the environment, not `auth.json`. Non-zero exit on error, abort or length.
- `--approve` (or `--no-approve`) because print mode cannot answer the trust prompt — without it, project
  `.pi/` resources are skipped silently.
- `</dev/null` because a never-closed stdin pipe hangs `pi -p` **[TESTED]**.
- Readiness gate: `pi auth check --provider X --json` exits 0, 1 or 2.
- Deterministic runs: `PI_OFFLINE=1`, `PI_SKIP_VERSION_CHECK=1`, `PI_TELEMETRY=0`.

### JSON mode

```bash
pi --mode json "summarise the failing test" </dev/null > events.jsonl
```

Assemble text from `message_update` deltas; `message_end` is authoritative; `agent_settled` marks the end
of automatic work. Split on LF only (don't use Node `readline`). ⚠️ **JSON mode does not exit non-zero on a
failed or aborted run** — inspect the events.

### RPC

`pi --mode rpc` — a long-lived process; JSONL commands on stdin, responses and events on stdout. In
TypeScript prefer `RpcClient` (from `@earendil-works/pi-coding-agent`, with `promptAndWait()`). Extension
dialogs are forwarded through the RPC extension-UI sub-protocol.

### SDK

```ts
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();   // options: cwd, agentDir, model, thinkingLevel, tools, excludeTools,
await session.prompt("List the TODOs in src/");    // customTools, resourceLoader, sessionManager (SessionManager.inMemory()), settingsManager
console.log(session.getLastAssistantText());
session.dispose();
```

`session.subscribe(ev => …)`, `steer()`, `followUp()`, `abort()`, `waitForIdle()`.
⚠️ **SDK sessions do not load built-in MCP or codemode.** Add `createMcpExtension()`,
`createCodemodeExtension()`, `createToolSearchExtension()` through
`DefaultResourceLoader({ extensionFactories })` and call `session.bindExtensions()`. Pi ships 14
typechecked examples in `examples/sdk/`.

### GitHub Actions / scheduling

**NOT DOCUMENTED** — there is no official action and no Bugbot-style reviewer. The course ships a
**pattern** (untested): [`examples/automation/github-action-pi.yml`](./examples/automation/github-action-pi.yml)
— install a pinned `@earendil-works/pi-coding-agent` with `--ignore-scripts`, run the print-mode command
above, and keep posting the result a separate, human-controlled step. Scheduling: none built in — cron, CI
or `systemd` with `pi -p`. Fork rebranding: `"piConfig": {"name", "configDir"}`.

---

# PART 2 — The methodology

## 12. Methodology

All the deep material (11-stage workflow, real end-to-end example, tool-precedence) is in
[`examples/methodology/`](./examples/methodology/). Summary:

### The real workflow (see [`methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md))
Agent = disciplined collaborator; autonomy is earned per-decision. 11 stages chained by **deterministic
gates**: orient (`/skill:kg` + history+status) → inbound triage against the **output contract** →
regression vs pre-existing → investigate with a **deterministic oracle** (before the paid LLM call) →
**plan file** + agreement (Pi has no plan mode; the gate is the human's "yes") → TDD RED→GREEN → verify
(unit+scoped+regression+contract via the *wrapper* AND inside the deployed image) → document →
**sanitise** (`/skill:sanitise-diff` on added lines) → handoff (the agent does **not** push/PR/deploy unless
explicitly asked — global `block-external-git.ts` extension + AGENTS.md; the human does it) → review +
persist (`/skill:kg-refresh` if applicable — see the §16 caveat).
Diagram: [`methodology/flow.png`](./examples/methodology/flow.png) (source `flow.mmd`, render
`render_flow.py`). Concrete case from start to finish:
[`methodology/REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

> **The outbound gate is FIVE checks** (not just "the tests pass"):
> **(0) validate the measuring instrument before trusting it** — any `_diag_*`/`_sweep_*` that informs a ship
> decision is first run against a **known-answer case**, and that result recorded next to the finding; never
> wrap the measurement in your own `try/except → return False`;
> (1) reproduce at the **real output stage** — the *wrapper* that rebuilds the contract, not an internal
> `extract()` function; (2) the local JSON matches the contract, and **is verified on the member LIST,
> never on a total**; (3) verify it **inside the deployed image** (download/build the runtime image, mount
> the `src`, re-run); (4) **look at the output** rendered, by eye, before the PR — for geometry/highlight
> changes, before/after artifacts are **mandatory**.
> Green tests are not proof of what gets deployed. Identical in role to the Claude Code and Cursor gate —
> only which agent runs it changes.
>
> **Five ways a green gate proves nothing** — all five have bitten us:
> **Broken instrument.** Bypassing the constructor to probe a predicate cheaply leaves unset every attribute
> you didn't think to set; if the method reads one and has its own `try/except`, the error is swallowed and
> comes back as a plausible `False`. The probe then reports a confident, uniform "no" for **every** case.
> Canary against a known answer, always.
> **A total that matches.** A count that lands on the expectation is **not** a passing test: one item wrongly
> added and one wrongly dropped cancel exactly. Assert on **titles/ids**, not on `len(...)`; and where the fix
> has a known direction, measure a **delta** against a baseline (gained/lost), not two totals. The closer a
> number falls to the expected one, the **more** suspicious it should be, not less.
> **A gate that couldn't fail.** If the reference corpus holds no positive example of the shape you just
> touched, the clean run proves **no-regression and nothing else**. Say so explicitly, and name what carries
> the correctness evidence instead. (Real case: a detector that fires on **0 of 190** corpus documents —
> `fires=0` reads identically whether the code is correct or completely broken.)
> **A canary that never applied the real perturbation.** The instrument can be flawless and still prove
> nothing, because what it does to the data **is not what production does**. Real case: the synthetic test
> renamed the *containers* and churned 4% of the items, recovered **100%** of the mapping, and was reported
> as "verified"; the real rebuild changed something the test never touched — the **identifiers of the items
> themselves**, 88% of them — and recovery fell below **1%**. Before trusting a green canary, state in one
> sentence *what production does to this data* and check the canary does the same. If you can't, the gate is
> **unproven**: "the test I could build passed" is not "the risk is retired".
> **A structural gate read as a semantic one.** Checking that everything is present, unique and correctly
> wired says **nothing** about whether any of it is *right*. Real case: a migration reported a clean bill of
> health — every group matched, none lost, zero orphans — while **56%** of the carried-over names did not
> describe what they were attached to, because the matching had fallen back to a shallow proxy. A wrong name
> is **worse** than a missing one: the missing one asks a question, the wrong one answers it incorrectly and
> sends the next person to the wrong place. When a value's correctness is a matter of **meaning**, no
> automated check retires it — schedule the human read and say so in the gate's description.
>
> **The output contract is a living document.** When a change alters what is emitted, consult the governing
> rule **before** designing the fix and do exactly one of three things: **comply**, **revise** it as part of
> the same change, or **record** why it's out of scope. All three are valid; **silence is not**. Cite the
> rule by **stable identifier** (never by file path), and don't turn it into a CI gate: the decision is
> **three-valued**, and a binary check would block precisely the correct "revise the rule" outcome.
>
> **Where does the "expected" number come from?** "The other environment returns X" is evidence **about that
> environment**, never a specification — and if that environment runs the same code path you're fixing,
> matching it reproduces the bug. Derive the target from the document's structure and the contract, and say so
> plainly when the ticket's expectation is wrong (real case: the ticket said 12; the correct answer was 13).

### Tool-precedence (see [`methodology/tools.md`](./examples/methodology/tools.md))
`AGENTS.md` doesn't just say *what* to do, but **with which tool and in what order**
(cheap→expensive, deterministic→probabilistic):
```
Orient       -> /skill:kg (ticket knowledge graph) · STATUS.md/ledgers · git · gh   (no inference)
Navigate     -> CodeGraph codegraph_explore (MCP, toolExposure: direct): source+paths+blast radius (treat as ALREADY read)
Refactor-chk -> Serena find_referencing_symbols (MCP, direct)  MANDATORY before renaming/deleting
Diagnose     -> deterministic oracle (parser/validator/_diag_*.py)  (no inference, reproducible)
Environment  -> cloud CLI (logs, function config, queues/DLQ)   (read-only profile)
Contract     -> Playwright (MCP, deferred) / browser against the output endpoint
Deployed     -> Docker: repro inside the runtime image (real stage = wrapper); green tests != what ships
Only at the end -> the agent turn, to VERIFY the fix (not to diagnose)
```

### Method permissions (different mechanism, same policy)
Claude Code: hand-curated allowlist in `settings.local.json`. Cursor: rules + approvals + hooks +
`permissions.json`. **Pi: nothing to allowlist** — (1) **AGENTS.md** carries prevalence and "no push without
asking"; (2) the global **`block-external-git.ts`** extension enforces the git part; (3) **`--tools`** drops
`edit`/`write` for read-only sessions; (4) **containers** for unattended runs. Do not try to port the
`allow` JSON — re-implement the *policy*.

---

## 13. The method's tools

**Setup / smoke of the tools in a demo repo:**
[`AGENT_SETUP_TOOLS.md`](./docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md).

### CodeGraph ([`examples/codegraph/`](./examples/codegraph/)) — local code intelligence (via MCP)
Tree-sitter index → SQLite in `.codegraph/` (no API keys). Returns symbols + call paths + blast radius +
**test-coverage flags**.
```bash
codegraph init        # creates .codegraph/ and builds the index   codegraph sync   # incremental after editing
codegraph explore "<symbol|question>"       # source + paths + blast radius, in 1 round-trip
codegraph impact|callers|node <symbol>      # blast radius / callers / 1 symbol + trail
pi mcp add codegraph --description "Code intelligence" -- codegraph serve --path "$PWD" --mcp   # [TESTED]
```
Then set `"toolExposure": { "codegraph_explore": "direct" }` in the `mcp.json` entry — **[TESTED]** the
default is `codemode`, which hides the tool from the declared list. It is the **first** navigation tool
(before grep/read); treat the source it prints as **already read**. Pin `--path` (no default project
otherwise). On WSL2 `/mnt` the watcher can miss changes → `codegraph sync` after editing. [3rd-party]
alternatives that expose it as a native Pi tool: `@henryqw/pi-codegraph`, `@vndv/pi-codegraph`.

### Serena ([`examples/serena/`](./examples/serena/)) — semantic navigation via LSP (MCP)
```json
{ "mcpServers": { "serena": { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
  "toolExposure": { "find_symbol": "direct", "find_referencing_symbols": "direct", "get_symbols_overview": "direct" } } } }
```
Not tested under Pi (args copied from the Cursor guide). Key tools: `find_symbol`, `get_symbols_overview`,
`search_for_pattern`, and above all **`find_referencing_symbols`** — the **precise** check before
renaming/deleting: it disambiguates same-named methods by class, where CodeGraph's flat `impact` mixes them
up. It complements CodeGraph, it does not replace it. [3rd-party] `@bacnh85/pi-serena`.

### GSD ([`examples/gsd/`](./examples/gsd/)) — the method turned into tooling, **Claude Code only**
Phase-based cycle with versioned state in `.planning/` and specialised subagents (`gsd-planner`,
`gsd-plan-checker`, `gsd-executor`, `gsd-code-reviewer`, `gsd-verifier`, …). The official package supports
"Claude Code, OpenCode, Gemini and Codex" — **not Pi**. [3rd-party] `pi-gsd` ("Unofficial port", last
published 2026-04-26) and `@opengsd/gsd-pi` (a separate GSD-branded agent) exist, untested.

> ⚠️ Pointing Pi's `"skills"` at `~/.claude/skills/gsd-*` "works" at load time **[TESTED]**, but those skills
> call Claude tools (Task, AskUserQuestion) Pi does not have. Don't.

**Practical Pi equivalent:**
```
plan file in data/changes/<id>/  -> discuss gate -> plan (human approves before touching code)
/skill:methodology-plan          -> fills the plan template
prompt templates (.pi/prompts/)  -> /plan-phase-style saved prompts
subagent example /implement chain-> substitutes for the gsd-* roles (scout/planner/worker/reviewer)
data/changes/                    -> the same state as in Claude Code (not GSD's .planning/)
```
> **Honesty — do we use it here?** **No.** The real project uses the 11-stage workflow + `data/changes/`,
> tuned for per-ticket fixes on a service in production. GSD makes more sense in a **multi-component greenfield**.

---

## 14. Transferring the methodology

Real material: [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) —

- **Pi:** [`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md) + surface
  [`pi/`](./docs/ai-agents-code-methodology/pi/) (`AGENTS.md.example`, `APPEND_SYSTEM.md.example`,
  `mcp.json.example`, `settings.json.example`, `extensions/block-external-git.ts`, `skills/day/`,
  `skills/atlassian/`, `skills/evidence/`, `skills/preview/`, `skills/kg/`, `skills/kg-refresh/`, `skills/methodology-plan/`,
  `skills/sanitise-diff/`).
- Shared: [`TRANSFER_AND_BOOTSTRAP.md`](./docs/ai-agents-code-methodology/TRANSFER_AND_BOOTSTRAP.md),
  [`templates/`](./docs/ai-agents-code-methodology/templates/).
- The same pack still ships [`CURSOR_ADAPTATION.md`](./docs/ai-agents-code-methodology/CURSOR_ADAPTATION.md)
  and [`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) — the discipline
  reaches a fourth agent.

**What travels unchanged:** plan→agreement→implement · verify against the consumer's contract · solve the
general class · durable trail · the human owns everything external.

**What changes — the surface (from Claude Code to Pi):**
```
CLAUDE.md (+ nested, @imports)       -> AGENTS.md in cwd + ancestors, one per dir (no nested, no @imports)
~/.claude/CLAUDE.md                  -> ~/.pi/agent/AGENTS.md (Pi does NOT read ~/.claude)
.claude/rules/ (scoped)              -> skill with path-naming description / claude-rules.ts example / extension
Skills ~/.claude/skills/  (/kg)      -> ~/.pi/agent/skills/ (/skill:kg) — SAME SKILL.md, unknown keys ignored
.claude/commands/*.md                -> prompt templates ~/.pi/agent/prompts/*.md
Allowlist settings.local.json        -> (none) trust + --tools/defaultTools + extensions + containers
Hooks (exit 0/2, stdin JSON)         -> TypeScript extension: pi.on("tool_call") -> { block: true, reason }
Plan mode                            -> plan file + human agreement (or plan-mode/ example extension)
Subagents (Task) + Agent Teams       -> subagent example extension / pi -p child processes — NO Agent Teams
claude -p (headless)                 -> pi -p … </dev/null  (+ --approve for project resources)
Auto-memory (MEMORY.md)              -> (none) ledgers + /resume + session JSONL
Agent SDK (query/allowedTools)       -> createAgentSession() / RpcClient (add MCP factories explicitly)
MCP allowlist mcp__s__t              -> same tool names; visibility via exposure/toolExposure
GSD                                  -> stays in Claude Code ([3rd-party] pi-gsd unofficial)
```

**Bootstrap in the target repo (bash):** see the block in
[`pi/README.md`](./docs/ai-agents-code-methodology/pi/README.md) — global extension + skills into
`~/.pi/agent/`, `.pi/mcp.json` with the absolute repo path substituted, `AGENTS.md` if absent. Then `/trust`.

**Fallback without a ticket knowledge graph** (80% of the value, minimal setup): newest-first `STATUS.md` +
per-ticket folders · lexical search by symptom/symbol/contract field · commit history (file overlap) · a
short "danger zones" section.

**First-day checklist:** fill in `STATUS.md` · 3-5 invariants in `SHARP_EDGES.md` · define the output
contract in `AGENTS.md` · scoped test commands · prove the git gate fires once · one complete issue with
RED→GREEN + contract verification.

---

## 15. Machine sync

Two mechanisms, and they do **not** compete: **(A)** tarball+USB for a *full machine bring-up*, and
**(B)** shared object storage (S3) for the *day-to-day engineering record*.

### A. Full bring-up: tarball + USB (asymmetric)

Real (sanitised) procedure — see [`methodology/machine-sync.md`](./examples/methodology/machine-sync.md);
runbooks from the real installation in [`docs/synchro/`](./docs/synchro/). The original runbook was born in
Claude Code — the adaptation table:
```
Claude Code                          Pi
Pointer in CLAUDE.md                 Pointer in AGENTS.md (cwd or an ancestor)
Bundle ~/.claude (skills + memory)   Bundle ~/.pi/agent/: settings.json, mcp.json, extensions/, skills/, prompts/, AGENTS.md
                                     EXCEPT auth.json, mcp-auth.json, trust.json (secrets / machine-local, like .aws)
                                     sessions/ only if you want history on the laptop
codegraph MCP in ~/.claude.json      Re-pin --path in .pi/mcp.json (or ~/.pi/agent/mcp.json) on the laptop
/kg-refresh Claude skill             /skill:kg-refresh + same kg_refresh.sh scripts (extraction step: see §16)
```
**Asymmetric:**

```bash
# OUTBOUND (main -> laptop): FULL COPY. -h dereferences symlinks (critical for a symlinked .aws);
# venvs/node_modules/caches are excluded.
WS=$(ls -d /mnt/*/WORKSPACE 2>/dev/null | head -1)        # DERIVE the root, don't assume it
tar -czhf ~/ws-migration-$(date +%Y%m%d).tar.gz \
  --exclude='*/node_modules' --exclude='*/.codegraph' --exclude='*/.venv' --exclude='*/__pycache__' --exclude='*.pyc' \
  --exclude='.pi/agent/auth.json' --exclude='.pi/agent/mcp-auth.json' --exclude='.pi/agent/trust.json' \
  -C "$(dirname "$WS")" "$(basename "$WS")" \
  -C /home/$USER .pi .aws .ssh
# USB: WSL does not auto-mount a USB plugged in after boot -> sudo mount -t drvfs F: /mnt/f ; copy, sync,
# and verify byte for byte (stat -c %s of source and destination match) before ejecting.
# On the target: target-setup.sh -> reinstall the CodeGraph CLI, fix the MCP --path to the laptop's
# real root, rebuild the index; then /login in Pi (credentials did not travel) and /trust the repos.

# INBOUND (laptop -> main): DELTA ONLY. The code is already on the git host.
git fetch origin                                      # the only network op (read-only)
cp data/changes/STATUS.md data/changes/STATUS.md.mainbak   # backup FIRST
tar -xzf "$TARBALL" -C "$REPO"                         # only the gitignored docs under data/
diff data/changes/STATUS.md.mainbak data/changes/STATUS.md # additions only? keep. own edits? STOP
```

**Two gaps, two idempotent subcommands** (the workspace carries a `kg` graph — §16): on a new laptop,
`kg_refresh.sh bootstrap` installs the tooling that doesn't travel and pins the interpreter; and since
Pi has **no agent memory of its own** to carry, decide explicitly what travels: `snapshot-memory` parks
memory notes under `data/` (so they travel) and `restore-memory` merges them back with a backup on the main
machine, before `kg-refresh`. Single entry point for the laptop's agent: `LAPTOP_START_HERE.md`. The graph is
a **derived** artifact: it is rebuilt wherever the corpus is. ⚠️ **But the curated names overlay does travel
both ways** — it lives inside the generated tree and nothing regenerates it (see §15B and Part 3).

Guardrails (the landing is driven **by an agent**, with an `INSTRUCTIONS.md` written *for* it): only
non-destructive actions (rename, don't delete; never two move ops at once on a Windows mount); no git
writes to remote (the global git gate enforces push/PR); STOP and ask when in doubt; the cloud CLI binary
does **not** travel in the bundle (reinstall + re-login) — same for the CodeGraph CLI and the `.codegraph/`
index. The human owns external actions; the agent prepares and reports with evidence.

### B. The shared record: `data/` over S3

The tarball solves **transport**, not **sharing**. Add a third machine and a second person and three costs
appear: the record is gitignored → it **can't be linked** from a ticket or PR; moving degenerates into
archiving everything; and every teammate ends up with **their own private index** of the same history. Full
runbook: [`docs/synchro/s3-sync/README.md`](./docs/synchro/s3-sync/README.md); scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).

```bash
# Dry-run is the DEFAULT: nothing transfers until --go
./data-pull.sh            # preview  ->  ./data-pull.sh --go
./data-push.sh            # preview  ->  ./data-push.sh --go
./mount-data.sh           # live shared view, READ-ONLY (~/s3-<name>-data)
./validate.sh             # a machine isn't set up until this prints MACHINE READY
```

| Rule | Why |
|---|---|
| Scope grows **in reviewed phases** | Started narrow (`changes/**/*.md` + the graph) and widened in reviewed phases, owner signing off each step. ⚠️ **Every widening is a security event**: scan first, **canary the scanner** (a "clean" scan counts for nothing until it has caught a planted secret), then **reconcile** — a clean transfer report only says *"what I was asked to send, I sent"*. |
| **Write via sync, read via read-only mount** | Object storage has no locking and no atomic rename: a writable mount corrupts, and you find out weeks later. |
| Dry-run by default; `--delete` is a separate opt-in | An exact mirror from a stale local view **erases** what a teammate just pushed. |
| **Deliberate deletion is a tool, with a tombstone** | `aws s3 sync` cannot tell "deleted on purpose" from "missing": a file deleted by hand **came back twice**. `delete.sh` (publisher only) deletes **one** file and appends a tombstone to `_deletions.jsonl`; every pull moves it aside (never `rm`) and every push excludes it. A push that **cannot read** the list refuses (`exit 5`). |
| Docs = source of truth; the graph is **derived** | Per-ticket files almost never collide. The generated graph is the **only** real contention point → **one** machine publishes it. |
| **"Derived" is a property of the file, not of the folder** | Inside the generated tree lives a **hand-authored** file (the curated community names) that nothing regenerates: on a rebuild, **<1%** survived. Classify per file — *source* / *derived* / *authored inside derived* — and treat the third as source. |
| **Pairs must move together** | Sync compares **object by object** → new graph + old names = names glued to the wrong community, **with no error**. Stamp the overlay with a **fingerprint of the graph** and make the health check fail loudly. |
| **Coordinate without locks** | Each contributor writes **their own file** in a queue (`kg_refresh.sh request` → `refresh_queue/<utc>-<machine>.request`). Distinct keys never collide. |
| ⚠️⚠️ **Recovery EXPIRES — and users own their own work** | Versioning usually comes with a lifecycle rule **expiring noncurrent versions after 30 days**. Say it in onboarding: *pull before you edit, push what you changed, and if something of yours disappears, say so within the month.* |
| **Shared ledgers are append-only** | `STATUS.md`, `FOLLOWUPS.md`… Last-writer-wins with no merge: **rewriting one silently drops somebody else's line**. A pull-time warning has essentially no false positives. |
| **The shared store wins on divergence** | *"I have it locally"* stops being an argument once someone else's version is the published one. |
| ⚠️⚠️ **Guard BOTH directions** | Measured: two machines edited the status ledger the same afternoon; the second push replaced the first — **11 lines gone, no conflict, no error**. Guard the push: if the stored copy moved since you last synced, **refuse (exit 4 / `REFUSED`)**. Escape hatch `--allow-clobber`, documented with the reason not to use it. |
| ⚠️ **A per-machine file needs exactly ONE writer, enforced in the tool** | Our tool uploaded every machine's copy of everyone's file, rolling a colleague's record back. **The first symptom was a wrong conclusion about a person.** |
| ⚠️ **A guard that cries wolf on day one teaches people to override it** | The guard now asks: *would this upload actually change the stored object?* **A guard's false-positive rate is a safety property.** |

**The agent-specific part — the machine has a role.** Each machine declares `MACHINE_NAME` /
`MACHINE_ROLE` in its `config.env`; `identity.sh --write` generates a **machine-local** `IDENTITY.md`, and
`AGENTS.md` **points at it**, so every Pi session reads its own role first. `IDENTITY.md` is the one file that
must **not** be the same everywhere: gitignored, never synced, never packaged. (In Pi the pointer can live in
the repo `AGENTS.md` or in `~/.pi/agent/AGENTS.md` — the global file is per machine already.)

**And the habit needs a mechanism, not a paragraph.** "Pull at the start, push at the end" sat in the
operations doc **for months and was not happening** on the very machine that published. The fix packages
the two moments into one callable, **role-aware** routine — `day start` / `day end` — invoked in Pi as
**`/skill:day start`**. Worked example:
[`examples/skills-plugins/.pi/skills/day/SKILL.md`](./examples/skills-plugins/.pi/skills/day/SKILL.md);
scripts (genericised but real): [`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/). Start from
`config.env.example`: that one file is where the design lives. Every dangerous step is gated behind a
question it answers first, and where the answer is ambiguous it **stops and asks**.

> **Before the first shared push:** scrub embedded credentials from the records — investigation notes capture
> signed URLs and tokens **on purpose**, as evidence. Run `/skill:sanitise-diff` over the **whole** record.
> Same for Pi's own artifacts: never sync `auth.json` / `mcp-auth.json`, and treat `/share` as an outbound action.

> ⚠️⚠️ **A safety guard can silently disable the instrument that proves the habit.** A pre-pull snapshot
> installed its own `trap ... EXIT`; Bash keeps **one** EXIT trap, so it replaced the one that wrote the sync
> activity log. Dry runs kept logging and **every real pull went unrecorded for two days**. Ask what else
> claims the same single-slot resource; and remember **the real path and the rehearsal path are different
> code paths**.

> ⚠️ **Measure an optimisation before you quote it.** Predicted "two minutes to seconds"; measured
> **212s → 123s, about 40%**. Measure once, write the number down, date it.

---

# PART 3 — The ticket knowledge graph (graphify)

## 16. Ticket knowledge graph

**Technology: `graphify` — not CodeGraph.** CodeGraph is only the analogy: if CodeGraph indexes the *code*,
this graph indexes the **project's memory** — per-ticket writeups, "sharp edges", runbooks, memory notes.
All the real material is in [`docs/knowledge-graph/`](./docs/knowledge-graph/):
[`design.md`](./docs/knowledge-graph/design.md), scripts, tests, manifest and the real output (pseudonymised
for this course: ticket keys `TKT-1xx`, clients `ClientX`). Narrative summary:
[`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

### The pieces

| Piece | What it is |
|---|---|
| `kg` (skill) | Query: `explain` / `path` / `find` — deterministic, **no LLM** — **works in Pi unchanged** (`/skill:kg`) |
| `kg-refresh` (skill) | Rebuilds the graph: `prepare` → semantic extraction → `finalize` — **extraction step needs subagents** (see below) |
| [`kg_query.sh`](./docs/knowledge-graph/kg_query.sh) | Wrapper around `graphify explain`/`path` over `output/graph.json` + `find` |
| [`kg_refresh.sh`](./docs/knowledge-graph/kg_refresh.sh) | Deterministic bookends: `prepare` / `finalize` / `bootstrap` / `snapshot-memory` / `restore-memory` / `request` / `queue` |
| [`build_manifest.py`](./docs/knowledge-graph/build_manifest.py) / [`stage_corpus.py`](./docs/knowledge-graph/stage_corpus.py) | Enumerate and stage the corpus with provenance-preserving names |
| `test_kg_corpus.py` · `test_kg_query.py` · `test_kg_refresh.py` | The bookends are **tested** — the pipeline is infrastructure |
| [`manifest.txt`](./docs/knowledge-graph/manifest.txt) | The explicit, diffable corpus (~116 files, ~196k words) |

**Is `kg` a slash command or a skill? A skill** — it carries **assets** (the shell wrappers), it has a
**`description`** so the agent auto-selects it at the orient stage, and `kg-refresh` **orchestrates a step of
the agent itself**. In Pi the definitions live at user level (`~/.pi/agent/skills/kg/`, `…/kg-refresh/`) —
the **same `SKILL.md`** as in Claude Code and Cursor; Pi silently ignores Claude-only keys like `trigger:`
**[TESTED]**, and you invoke it as `/skill:kg` instead of `/kg`.

### Building and querying

```bash
# build / refresh (the only agent step is semantic extraction, with parallel subagents)
kg_refresh.sh prepare        # manifest -> stage _corpus/ -> copy to a scratch OUTSIDE the repo
                             # node/edge extraction + clustering -> HTML/JSON/report   <- agent step
kg_refresh.sh finalize       # copy artifacts to output/ + leak-check (nothing outside data/)

# query (zero LLM: kg_query.sh reads output/graph.json directly)
kg explain <ticket|topic>    # a node's neighbours    <- the most common use
kg path <A> <B>              # shortest path A<->B
kg find <substr>             # discover a node's exact name
```

> ⚠️ **The Pi caveat for `kg-refresh`.** `/graphify`'s extraction dispatches **general-purpose subagents**;
> Pi has none built in. Options: (a) install the `subagent` example extension or [3rd-party] `pi-subagents`
> and adapt the extraction step — **UNVERIFIED** (graphify's support for Pi is not documented; its SKILL.md
> loads in Pi **[TESTED]**, but its subagent calls assume Claude Code's Agent tool); or (b) keep the
> deterministic bookends in Pi and **run only the extraction step from Claude Code**. The contributor path
> (`kg_refresh.sh request`) needs no subagents and works in Pi as-is.

**Gotcha that holds the pipeline together:** `graphify` honours `.gitignore` and all of `data/` is ignored →
running the detector in place finds 0 files; the corpus is staged in a scratch outside the repo and the
artifacts are copied back. That's why `kg-refresh` is a skill and not a script.

### The real output (see [`output/`](./docs/knowledge-graph/output/))

- [`graph.html`](./docs/knowledge-graph/output/graph.html) — interactive vis-network visualisation. The deck
  screenshot is regenerated with [`presentation/capture_kg_graph.py`](./presentation/capture_kg_graph.py) →
  `presentation/kg_graph.png`.
- `graph.json` — NetworkX node-link; **typed** edges (`relation`) with `confidence`
  (`EXTRACTED`/`INFERRED` + score). This is what `kg_query.sh` reads.
- [`GRAPH_REPORT.md`](./docs/knowledge-graph/output/GRAPH_REPORT.md) — **507 nodes · 672 edges · 35
  communities**; **92% `EXTRACTED`** · 7% `INFERRED`; god-nodes and "surprising connections". The communities
  map to real danger zones ("Letter-End & Run-in Titles", "Title Detection Failures", "PDF Extractor Cascade"…).

### Hook-in and lifecycle

Hooked into the **history-first** rule of `AGENTS.md` (stage 1, Orient): run `/skill:kg <ticket|topic>`
*before* grepping `data/changes/`; one call surfaces the related tickets + the danger zone to read. Honesty:
the real gain is **recall in dense zones**; `EXTRACTED` = reliable, `INFERRED` = a lead to verify. It is a
**derived** artifact: rebuilt wherever the corpus is (§15).

> ⚠️ **Correction: "derived" is a property of the file, not of the folder.** Inside the generated tree lives a
> **hand-authored** file — the curated community names — that nothing regenerates. Measured on a real rebuild,
> **under 1% survived**, and even after fixing the cause only ~38% carried across. Classify **per file**:
> *source*, *derived*, and **"authored but living inside the derived tree"** — the third always travels. Stamp
> the overlay with a **fingerprint of the graph** it was built against; a per-file sync cannot express
> atomicity, so the check has to live in the data.

> **Cost — honest.** "No LLM at query time" is **not** "free": the expensive reasoning is paid **once** when
> building the graph; each `kg` query is then a deterministic algorithm over `graph.json` → **zero
> inference**, plus the cost of reading a short output. Paid once, collected on every use — from any agent.

---

# Appendix

## A. Equivalence table: Claude Code → Cursor → Pi

| Concept | Claude Code | Cursor | Pi (1.3.0) |
|---|---|---|---|
| Install | `npm i -g @anthropic-ai/claude-code` / installer | Editor download + `curl https://cursor.com/install \| bash` | `curl -fsSL https://pi.dev/install.sh \| sh` or `npm i -g --ignore-scripts @earendil-works/pi-coding-agent` |
| Binary | `claude` | `agent` (CLI) | `pi` |
| Auth | `/login`, `ANTHROPIC_API_KEY` | `agent login`, `CURSOR_API_KEY` | `/login` (OAuth or key → `~/.pi/agent/auth.json`) or provider env vars; ~40 providers |
| Model / effort | `/model`, effort setting | Model picker | `/model`, `Ctrl+L`, `Ctrl+P`, `--model p/id:high`, `/thinking` (off…max) |
| Headless | `claude -p` | `agent -p --trust [--force]` | `pi -p` (`</dev/null` in CI), `--mode json`, `--mode rpc` |
| Global instructions | `~/.claude/CLAUDE.md` | User rules | `~/.pi/agent/AGENTS.md` (or CLAUDE.md) |
| Project instructions | `CLAUDE.md` (+ nested, `@imports`) | `AGENTS.md` (nested, most specific wins) + `.cursor/rules/*.mdc` | `AGENTS.md` / `CLAUDE.md` in cwd **and ancestors only**; one per directory (AGENTS.md wins); no `@imports`, no globs |
| Replace / append system prompt | `--system-prompt`, `--append-system-prompt` | — | `SYSTEM.md` / `APPEND_SYSTEM.md` (global or `.pi/`), `--system-prompt`, `--append-system-prompt` |
| Scoped rules | `.claude/rules/` (paths) | `.mdc` `globs` | None; skill, extension, or `claude-rules.ts` example |
| Auto-memory | `MEMORY.md` auto-memory | Memories (auto) | None built in; extensions or [3rd-party] packages |
| Permissions | `settings.json` allow/deny + prompts | `permissions.json` `mcpAllowlist` / `terminalAllowlist` + approvals | **No prompts, no allowlist file.** `--tools` / `--exclude-tools` / `defaultTools`, MCP `toolExposure: hidden`, project trust, extensions, containers |
| Sandbox | Optional sandbox mode | — | None built in; Docker, Docker Sandboxes, OpenShell, Gondolin extension, `sandbox/` example |
| Sessions storage | `~/.claude/projects/…jsonl` | Chat history | `~/.pi/agent/sessions/--<cwd>--/<ts>_<id>.jsonl` (tree, v3) |
| Resume | `claude -c` / `-r` | Chat list | `pi -c`, `pi -r`, `/resume`, `--session` |
| Branch / rewind | `/rewind`, Esc-Esc | `/rewind` (CLI) | `/tree`, `/fork`, `/clone`, Esc-Esc |
| Export / share | `/export` | — | `/export` (HTML/JSONL), `/share` (gist or Radius), `pi --export` |
| Compaction | Auto + `/compact <focus>` | Auto + `/summarize` | Auto (`compaction.*`) + `/compact [instructions]` + extension hooks |
| Prompt caching | Automatic | Not exposed | Automatic; `PI_CACHE_RETENTION=long`; `cacheWarming`; `showCacheMissNotices` |
| MCP config | `claude mcp add`, `.mcp.json`, `~/.claude.json` | `.cursor/mcp.json`, `~/.cursor/mcp.json` | `pi mcp add`, `.pi/mcp.json` (trusted), `~/.pi/agent/mcp.json`; same `mcpServers` shape; stdio + streamable HTTP (no SSE); `exposure` modes |
| MCP tool names | `mcp__server__tool` | `server:tool` | `mcp__server__tool` |
| Skills | `~/.claude/skills`, `.claude/skills` | `.cursor/skills` (+ reads `.claude/skills`) | `~/.pi/agent/skills`, `.pi/skills`, `~/.agents/skills`, `.agents/skills`, `"skills"` setting |
| Invoke a skill | `/name` | `/name` | `/skill:name [args]` |
| Slash commands | `.claude/commands/*.md` | Skills / commands | Prompt templates `~/.pi/agent/prompts/*.md` → `/name` |
| Marketplace | `/plugin install` | cursor.com/marketplace | `pi install npm:… / git:…`; gallery pi.dev/packages; `pi config` |
| Subagents | Built in (`.claude/agents/`) | Built in (`.cursor/agents/`) | **None built in**; `examples/extensions/subagent` (`~/.pi/agent/agents/*.md`), [3rd-party] `pi-subagents`, tmux |
| Agent Teams | Built in | No (Background Agents) | No; parallel `pi` processes / RPC |
| Plan mode | Built in | Plan mode | **None**; `plan-mode/` example or packages |
| Hooks | `settings.json` hooks (shell, JSON stdin/stdout, `exit 2`) | `hooks.json` (`beforeShellExecution`, … `permission: deny`) | **TypeScript extensions**: `pi.on("tool_call") → {block:true, reason}`, `tool_result`, `user_bash`, `before_agent_start`, session events |
| Custom tools | MCP or SDK | MCP | `pi.registerTool()` (TypeBox) or MCP |
| SDK | Claude Agent SDK | `@cursor/sdk` | `createAgentSession()`, `RpcClient` |
| CI review bot | GitHub Action | Bugbot | None official; `pi -p` in your own workflow |
| GSD | Supported | Not supported | Not officially supported ([3rd-party] `pi-gsd`) |

## B. Gotchas checklist

1. Package renamed: `@earendil-works/pi-coding-agent` (old `@mariozechner/…` deprecated); extensions import types from the new scope.
2. MCP **is** built in (since 0.99.0) — default exposure `codemode` hides tools; set `toolExposure: direct` for the trigger-map tools.
3. `--tools`: plain names replace the defaults; a list of only `+x`/`-x` adjusts them; don't mix (1.1.0). It keeps MCP tools unless an entry starts with `mcp__` (1.0.4).
4. `pi mcp --help` synopsis omits `add`/`remove` — they exist.
5. Context files: one per directory (AGENTS.md shadows CLAUDE.md); ancestors only; they ignore project trust.
6. `pi -p` waits for stdin EOF on a non-TTY pipe → `</dev/null`.
7. Print/JSON/RPC can't show the trust prompt → project `.pi/` resources skipped silently unless `--approve`.
8. JSON mode does not exit non-zero on a failed run — inspect events.
9. SDK sessions load no built-in MCP/codemode — add the factories.
10. Skills: `/skill:name`; unknown frontmatter keys ignored; first-found wins on collision; pointing `"skills"` at all of `~/.claude/skills` floods the prompt.
11. Project-local subagents (example extension) load only with `agentScope: "project" | "both"`.
12. Windows: `powershell` is a built-in tool (`defaultTools: ["-bash", "+powershell"]`); WSL2 behaves like Linux **[TESTED]**.
13. Telemetry: `enableInstallTelemetry` defaults to `true` — `PI_TELEMETRY=0` or the setting.
14. New issues/PRs from new contributors to the Pi repo are closed automatically.

## C. Sources

Verified **2026-10-17, Pi 1.3.0 — Pi moves fast, re-check before reuse.**

- Pi docs: <https://pi.dev/docs/latest> (pages cited by name above: quickstart, cli, cli-integration,
  configuration, security, containerization, sessions, session-format, compaction, settings,
  models, models-configuration, providers, mcp, codemode, skills, prompt-templates, packages, extensions,
  json, rpc, rpc-commands, rpc-extension-ui, sdk, environment-variables, windows, tmux)
- Pi homepage ("What we didn't build"): <https://pi.dev> · changelog <https://pi.dev/changelog> ·
  packages gallery <https://pi.dev/packages> · models <https://pi.dev/models>
- Source and examples: <https://github.com/earendil-works/pi/tree/main/packages/coding-agent>
  (`examples/extensions/`, `examples/sdk/`)
- npm: <https://www.npmjs.com/package/@earendil-works/pi-coding-agent>
- Pi 1.0 announcement: <https://earendil.com/posts/pi-1-0/>
- Agent Skills spec: <https://agentskills.io>
- Research notes for this course: [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md)
