# Pi: research findings for "Pi — a course in three parts"

> Repo copy of the research notes behind this course. Local scratch paths and project-specific names were
> removed; nothing else was changed. Every Pi claim in the guides and the deck must trace back to this file.
> Verified 2026-10-17 against Pi 1.3.0 — **Pi moves fast; re-check before reuse.**

**Verified:** 2026-10-17, by fetching pages and running a local install. **Pi version checked:** 1.3.0, released 2026-10-15.

## 0. Method and source notes (read first)

- **Primary source.** The docs at `https://pi.dev/docs/latest/<page>`. The rendered pages are built from Markdown in
  `github.com/earendil-works/pi/tree/main/packages/coding-agent/docs/` (the page footer links there). I downloaded all 42
  Markdown pages listed in the index from `raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs/*.md`
  on 2026-10-17. Below, a citation like **[cli]** means `https://pi.dev/docs/latest/cli`. The list of pages comes from the
  index's HTML hrefs: cli, cli-integration, codemode, compaction, configuration, containerization, custom-provider,
  environment-variables, extensions, how-pi-works, json, keybindings, llama-cpp, mcp, message-types, models,
  models-configuration, nvidia-rtx-llama-cpp, packages, prompt-templates, providers, quickstart, rpc, rpc-commands,
  rpc-extension-ui, sdk, security, session-format, sessions, settings, shell-aliases, skills, slash-commands,
  terminal-setup, termux, themes, tmux, tui, usage, virtual-models, windows.
  - Caveat: the Markdown came from `main` one day after the v1.3.0 tag. Small drift from "latest" is possible.
- **Source code** was read where the docs were vague: `src/core/resource-loader.ts`, `skills.ts`, `system-prompt.ts` and
  `extensions/types.ts` on `main`, read 2026-10-17. I also used the examples in `packages/coding-agent/examples/extensions/`.
- **Hands-on checks** ran on 2026-10-17, WSL2, Node 24.15. I ran
  `npm install --ignore-scripts @earendil-works/pi-coding-agent@1.3.0` into the scratchpad, with an isolated
  `PI_CODING_AGENT_DIR`. Those artefacts stayed in a local scratch folder (not shipped).
  Each hands-on claim below is marked **[TESTED]**.
- Anything marked **[3rd-party]** is a community npm package: not documented by Pi and not tested. Anything marked
  **NOT DOCUMENTED / UNVERIFIED** has no source behind it.

### Identity: confirmed, with corrections
- Pi **is** the minimal terminal agent that started as **`badlogic/pi-mono`** (Mario Zechner). That repo **now redirects to
  `earendil-works/pi`**: `gh api repos/badlogic/pi-mono` returns `full_name: earendil-works/pi`. Repo description:
  "AI agent toolkit: unified LLM API, agent loop, TUI, coding agent CLI".
- **The npm package was renamed.** `@mariozechner/pi-coding-agent` is deprecated at 0.73.1 with the message "please use
  @earendil-works/pi-coding-agent instead going forward" (npm, 2026-05-07). The current package is
  **`@earendil-works/pi-coding-agent` 1.3.0**. The binary is still called **`pi`**.
- Maintainer: Earendil Inc. (footer of pi.dev). Secondary sources say Earendil acquired Pi in April 2026 and Zechner stayed
  on as a stakeholder ([eesel.ai](https://www.eesel.ai/blog/pi-coding-agent),
  [implicator.ai](https://www.implicator.ai/pi-is-not-a-claude-code-rival-it-is-a-harness-rebellion/)). **Not confirmed
  from a primary source.** Licence: MIT ([README](https://github.com/earendil-works/pi/tree/main/packages/coding-agent)).
- Release timeline (GitHub releases API): v1.0.0 2026-10-01 · 1.0.1 10-03 · 1.0.2 10-04 · 1.0.3 / 1.0.4 10-05 ·
  1.1.0 10-07 · 1.2.0 10-12 · **1.3.0 10-15**. Pi 1.0 was announced at https://earendil.com/posts/pi-1-0/ (2026-10-01).

---

## 1. Install, auth, CLI, modes, providers, models, thinking

### Install ([quickstart], [README])
```bash
curl -fsSL https://pi.dev/install.sh | sh                          # macOS/Linux; pins deps; later: pi update
powershell -c "irm https://pi.dev/install.ps1 | iex"               # Windows (README)
npm install -g --ignore-scripts @earendil-works/pi-coding-agent    # Node >= 22.19; does NOT pin transitive deps
nix profile add github:earendil-works/pi/stable                     # Nix; update with nix profile upgrade pi
pi --version                                                        # [TESTED] -> 1.3.0
```
- Uninstall: `npm uninstall -g @earendil-works/pi-coding-agent`, or rerun the installer and choose "Uninstall Pi".
  Neither removes `~/.pi/agent/` [quickstart].
- Updates: `pi update` updates Pi itself, `pi update --extensions` updates packages, `pi update --models` refreshes the
  model catalogue, `pi update --all` does both [cli].

### Start and authenticate ([quickstart], [models], [providers])
- `cd project && pi`. Inside Pi, `/login` picks a provider (OAuth subscription or API key) and `/model` picks a model.
  Credentials are saved in `~/.pi/agent/auth.json`.
- Environment-variable keys suit CI: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`,
  `COPILOT_GITHUB_TOKEN`, `MISTRAL_API_KEY`, `GROQ_API_KEY`, `XAI_API_KEY`, `AI_GATEWAY_API_KEY`, and about 30 more
  [providers]. Anthropic also accepts `ANTHROPIC_OAUTH_TOKEN` (API credential) and `ANTHROPIC_AUTH_TOKEN` (bearer).
- Credential precedence: `--api-key` → `auth.json` → `models.json` `apiKey` → environment / ambient cloud credentials
  [models].
- A secret manager can supply a key by command: `auth.json` `{"anthropic":{"type":"api_key","key":"!security find-generic-password -ws 'anthropic'"}}`.
  The command's output is cached for the life of the process [providers].
- **Bedrock** uses ambient AWS credentials: `AWS_PROFILE`, `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` /
  `AWS_SESSION_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION` or `AWS_DEFAULT_REGION`, plus ECS task credentials and IRSA
  [providers].
  - Whether a given SSO role has Bedrock entitlement is account-specific. **UNVERIFIED.**
- Other providers: Vertex AI (`GOOGLE_CLOUD_API_KEY` or Application Default Credentials), Azure (provider id `azure`,
  renamed from `azure-openai-responses` in 1.0.3), Cloudflare, and **Radius**, Earendil's own gateway (`/login radius`,
  early alpha) [providers].
- Subscriptions: the docs say "a supported subscription → `/login`" [models] but publish **no list** of supported
  subscriptions.
  - What the docs do mention: "Sign in with ChatGPT" for `openai` [models]; a setting
    `warnings.anthropicExtraUsage` that "warns when Anthropic subscription authentication may use paid extra usage"
    [settings]; and the containerization page using a Claude Pro/Max token from `claude setup-token` passed as
    `ANTHROPIC_OAUTH_TOKEN` [containerization]; the `openai-codex` provider (`pi auth print-bearer-token --provider openai-codex`
    in `pi --help`).
  - The exact subscription list is **NOT DOCUMENTED**.
- Local models: built-in llama.cpp router (`/llama`) [llama-cpp]. Ollama, LM Studio, vLLM and SGLang go through
  `~/.pi/agent/models.json`, for example:
  ```json
  {"providers":{"ollama":{"baseUrl":"http://localhost:11434/v1","api":"openai-completions","apiKey":"ollama","models":[{"id":"qwen2.5-coder:7b"}]}}}
  ```
  Schema: `https://pi.dev/schemas/models.schema.json` [models]. The model catalogue is at https://pi.dev/models.

### Switching models and thinking ([usage], [models], [cli], [settings])
- In the TUI: `/model` or `Ctrl+L` selects; `Ctrl+P` cycles; `/scoped-models` sets the cycle; `Ctrl+S` in the picker
  saves the default. `/thinking` or `Shift+Tab` cycles the thinking level.
- On the CLI: `--model sonnet:high` (fuzzy name plus `:<thinking>` suffix), `--provider`, `--thinking <level>`,
  `--models <patterns>`, `--list-models [search]`.
- **Thinking levels:** `off | minimal | low | medium | high | xhigh | max`, clamped to what the model supports.
  The default is `defaultThinkingLevel: "medium"`. Related settings: `modelThinkingLevels`, `thinkingBudgets`.
- Sessions record model and thinking changes; resuming a session restores them.

### Modes ([cli], [cli-integration], [json], [rpc])
| Mode | Command | Notes |
|---|---|---|
| Interactive TUI | `pi` | Fullscreen by default; `--tui-mode regular` uses normal scrollback |
| Print | `pi -p "…"` / `pi --print` | Prints the final assistant text. Exits non-zero on `error`, `aborted` or `length` |
| JSON events | `pi --mode json "…" > events.jsonl` | Session header, then JSONL events. A failed run does **not** by itself give a non-zero exit |
| RPC | `pi --mode rpc [--no-session]` | Long-lived. JSONL commands on stdin, responses and events on stdout. Commands include `prompt`, `steer`, `follow_up`, `abort`, `get_state`, `get_commands`, `compact`, `fork`, `set_model`, `set_thinking_level`, `export_html`, … [rpc-commands] |
| SDK | `createAgentSession()` | In-process Node or Bun [sdk] |

- Other useful CLI pieces: `@path` adds a file to the first prompt, piped stdin is prepended to it, and `--` ends option
  parsing.
- In the TUI, `!cmd` runs a shell command and sends its output to the model; `!!cmd` runs it without sending output [usage].
- **[TESTED] gotcha:** when stdin is not a TTY and is never closed (CI runners, agent harnesses), `pi -p "…"` waits for
  stdin EOF and appears to hang. Use `pi -p "…" </dev/null`. This fits the docs' "piped stdin is prepended to the first
  prompt" [cli].

---

## 2. Memory and instructions

### Context files ([configuration], source `resource-loader.ts` `loadProjectContextFiles`)
- **Global:** `~/.pi/agent/` (or `$PI_CODING_AGENT_DIR`). Candidates are `AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`,
  `CLAUDE.md` and `CLAUDE.MD`.
- **Project:** the working directory **and every parent directory** up to `/`.
- **Not loaded:** directories *below* the working directory. There is no nested, most-specific-wins discovery as in
  Cursor or Claude Code. The docs say a context file "applies whenever Pi runs in its directory or anywhere below it"
  [configuration]. Pi walks upward from cwd only (source).
- **Precedence is one file per directory.** From source: the first existing file in the order
  `AGENTS.override.md > AGENTS.md > AGENTS.MD > CLAUDE.md > CLAUDE.MD` is the **only** file loaded from that directory.
  - So a directory holding both `AGENTS.md` and `CLAUDE.md` contributes **only `AGENTS.md`**.
  - `AGENTS.override.md` "replaces `AGENTS.md` or `CLAUDE.md` only in the same directory" [configuration].
- **Concatenation order** (source): the global file first, then ancestors from the filesystem root down to cwd. Each is
  wrapped as `<project_instructions path="…">…</project_instructions>` in the `project_context` section of the system
  prompt (`system-prompt.ts` `renderProjectContext`).
  - A nested git **worktree** does not load the main repo's copy of the same file twice (source
    `findShadowedContextFile`).
- **`CLAUDE.md` compatibility:** yes, as a fallback filename (see above).
  - Pi does **not** read `~/.claude/CLAUDE.md`. Its global directory is `~/.pi/agent/`. Symlink or copy if you want the
    file shared.
  - Pi does **not** read `.claude/rules/`. An example extension, `claude-rules.ts`, lists those files in the system prompt
    for on-demand reading.
- Context files load **regardless of project trust**. Disable them with `-nc` / `--no-context-files` [security], [cli].
- `@path` includes inside AGENTS.md: **NOT DOCUMENTED**. Treat AGENTS.md as plain text that can contain pointers.

### System prompt ([configuration], [cli])
- `~/.pi/agent/SYSTEM.md` or `.pi/SYSTEM.md` **replaces** Pi's default system prompt.
- `~/.pi/agent/APPEND_SYSTEM.md` or `.pi/APPEND_SYSTEM.md` **appends** to it.
- The trusted project file wins over the agent-directory file of the same name. The two are **not combined**.
- CLI equivalents: `--system-prompt <text|path>` and `--append-system-prompt <text|path>` (repeatable).
- Extensions can change prompt sections per run (`before_agent_start`) [extensions].

### Cross-session memory
- **No built-in memory feature.** The homepage puts long-term memory in extensions: extensions "can inject messages
  before each turn, filter the message history, implement RAG, or build long-term memory" (https://pi.dev, "Context
  engineering").
- Sessions persist as JSONL and can be resumed (§4).
- [3rd-party] packages: `pi-memory`, `pi-hermes-memory`, `pi-observational-memory` (npm search, 2026-10-17). Untested.

---

## 3. Permissions and safety: a deliberate design choice

- **No approval prompts and no sandbox.** Quickstart: "It does not ask before every tool call." Security: "Pi can read,
  change, and execute files with the permissions of the account that started it, and it does not ask for approval before
  every tool call." Homepage, under "What we didn't build": **"No permission popups — Run in a container, or build your own
  confirmation flow with extensions."**
- **Project trust** (`/trust`; saved in `~/.pi/agent/trust.json`) only decides whether a folder's *resources* load:
  `.pi/settings.json`, `.pi/mcp.json`, `.pi/extensions|skills|prompts|themes`, `.pi/SYSTEM.md` / `APPEND_SYSTEM.md`, and
  project `.agents/skills`.
  - It **does not sandbox tool calls**, and context files load regardless.
  - `defaultProjectTrust: "ask" | "always" | "never"` is user settings only; the default is `"ask"`.
  - Print, JSON and RPC modes cannot prompt. With `"ask"` they *skip* project resources, unless you pass
    `--approve` / `-a` or `--no-approve` / `-na` [security].
  - Gotcha: the project `sessionDir` setting is read *before* trust is resolved [security].
- **Isolation options** [containerization]:
  - Plain Docker (Dockerfile given; mount only the workspace; do **not** mount host `~/.pi/agent`).
  - Docker Sandboxes (`sbx run --kit "docker.io/sbx/pi-kit:latest" pi`; the proxy keeps the real key on the host).
  - NVIDIA OpenShell.
  - The Gondolin micro-VM extension: routes the built-in tools and `!` into a VM, but the Pi process and other extension
    tools stay on the host.
- **Static tool restriction** (by tool *name*, not command content) [cli], [settings]:
  - `--tools read,grep,find,ls` is an allowlist.
  - `--exclude-tools`, `-nbt` and `-nt` remove tools.
  - `defaultTools` with `+name` / `-name` entries adjusts the default set.
  - MCP tools can be hidden with `exposure: "hidden"` or `toolExposure` [mcp].
- **Content-based gates = extensions** (§10). Shipped examples: `permission-gate.ts` (confirm `rm -rf`, `sudo`,
  `chmod 777`; **blocks by default when there is no UI**), `protected-paths.ts`, `confirm-destructive.ts`,
  `dirty-repo-guard.ts`, `plan-mode/`, `sandbox/` (OS sandbox via `@anthropic-ai/sandbox-runtime`).
  - The docs include an MCP-annotation-based approval gate (Codex-style) [extensions].
  - [3rd-party]: `@gotgenes/pi-permission-system`, `pi-permission-modes` (bubblewrap/sandbox-exec plus allow/ask/deny and
    bash AST gating), `@czottmann/pi-automode`, `@erichll/pi-auto-review`.
- **Fail-safe:** "A `tool_call` handler failure blocks the tool as a fail-safe" [extensions].
- **Out of scope for security reports:** "lack of a built-in sandbox", prompt injection, and user-installed extensions
  [security].

---

## 4. Sessions ([sessions], [session-format], [cli], [usage], [slash-commands])

- **Storage:** `~/.pi/agent/sessions/--<path>--/<timestamp>_<session-id>.jsonl`. `<path>` is the cwd with the leading
  separator removed and `/`, `\` and `:` replaced by `-`.
  - Override the location with `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > the `sessionDir` setting.
  - `--no-session` runs ephemeral.
- **Format:** JSONL tree. Entries carry `id` and `parentId`. The header has `version` (now **v3**). Entry types include
  messages, model and thinking changes, `compaction`, `branch_summary`, `custom`, `context_edit` and `usage`
  [session-format].
- **Resume:** `pi -c` / `--continue` resumes the latest session for this cwd. `pi -r` / `--resume`, or `/resume` in the
  TUI, opens a picker (search, rename, delete with `Ctrl+D`). Also `--session <path|id>`, `--session-id <id>`,
  `-n` / `--name`, `/name`, `/session` (file, ID, counts, tokens, cost), and `/new`.
- **Branching:** `/tree` moves within the same file and can summarise the branch you leave. `/fork` creates a new session
  from an earlier user message. `/clone` copies the active branch. `--fork <path|id>` forks from the CLI. Double-Esc
  defaults to `/tree` (`doubleEscapeAction`).
- **Export and share:** `/export [path]` writes HTML or JSONL; `pi --export <file> [out]` writes HTML; `/import <path>`
  reads JSONL.
  - `/share` uploads to a Radius artifact if you are authenticated, else to a private GitHub gist via `gh`. The
    `sessionShareDestination` setting (`auto | gist | radius`) was new in 1.3.0.
  - `/bug` prepares a private report. `/copy` or `Ctrl+X` copies the last reply.
- Shell tools receive `PI_SESSION_ID`, `PI_SESSION_FILE`, `PI_PROVIDER`, `PI_MODEL` and `PI_REASONING_LEVEL`
  [environment-variables].
- There is no cross-surface handoff (Claude Code `--teleport` style). There is a `handoff.ts` example extension:
  `/handoff <goal>` moves context into a new focused session.

---

## 5. Context window and compaction ([sessions], [compaction], [settings])

- The footer shows context usage. **Auto-compaction** triggers when `contextTokens > contextWindow - reserveTokens`. It is
  also checked between tool batches inside a run, and there is one compact-and-retry on overflow.
- **Manual:** `/compact [instructions]` (the instructions focus the summary). Disabling auto does not disable the manual
  command.
- **Settings:** `compaction.enabled` (default `true`), `compaction.reserveTokens` (`16384`),
  `compaction.keepRecentTokens` (`20000`), and `compaction.modelOverrides` (per `provider/modelId`).
  Branch summaries use `branchSummary.reserveTokens` (`16384`) and `branchSummary.skipPrompt` (`false`).
- **How it works:** it summarises older messages into a `CompactionEntry` (`summary`, `firstKeptEntryId`, `tokensBefore`,
  `details.readFiles/modifiedFiles`). The original entries stay in the file.
  - The summary is structured (Goal / Constraints & Preferences / Progress / Key Decisions / Next Steps / Critical
    Context).
  - Summarisation requests **disable prompt-cache writes** [compaction].
- **Extension hooks:** `session_before_compact` (cancel, or supply a custom summary), `session_compact`,
  `session_compact_failed`, `session_before_tree`. Examples: `custom-compaction.ts`, `trigger-compact.ts`.
- **Keeping context lean**, in Pi's own levers:
  - The small default system prompt and four default tools (`read`, `bash`, `edit`, `write`).
  - Skills load only name, description and path until used [skills].
  - MCP tools default to `codemode` exposure, so they are **not** declared as tools; a one-line server summary sits in
    the `mcp_servers` prompt section [mcp]. `tool_search` / `deferred` exposure loads tools on demand.
  - Codemode scripts filter large output before the model sees it [codemode].
  - MCP text results over 20 KB are middle-truncated, with the full text saved to a temp file [mcp].
  - `/tree` and `/fork` for side quests. `--no-context-files`, `--no-skills` and `--no-extensions` for minimal runs.

---

## 6. Prompt caching

What Pi does **automatically**:
- Anthropic-format requests get `cache_control` markers on the system prompt, the last tool definition, and the last
  user, assistant or tool-result text ([models-configuration], `cacheControlFormat: "anthropic"` compat field).
- OpenAI-style requests get session affinity and `prompt_cache_key` handling. For long retention, Pi sends
  `prompt_cache_retention: "24h"`, or `prompt_cache_options.ttl: "30m"` on GPT-5.6+ (compat fields
  `supportsLongCacheRetention`, `supportsExplicitPromptCacheMode`, `sessionAffinityFormat`) [models-configuration],
  changelog 0.85.1.

What the **user controls**:
- `PI_CACHE_RETENTION=long` turns on extended retention where supported (for example Anthropic `cache_control.ttl: "1h"`)
  [environment-variables], [models-configuration].
- `cacheWarming: "off" | "streaming" | "idle"` (default `"streaming"`, global only). It keeps eligible caches warm during
  long runs or between runs. It only runs when the model declares a `promptCache` lifetime and the saving is estimated
  at ≥ $0.05. Warm-up usage counts in the totals [settings]. Extensions can override it with `cache_warming_decision`.
- `showCacheMissNotices: true` shows notices for cache misses, warm-ups and compaction usage.
- `/session` shows the next cache-warming decision.
- `models.json`: `promptCache: {"short": 300, "long": 3600}` per model, plus the compat fields above.

Design choices that protect the cache:
- Mid-conversation prompt and tool changes are **appended** as transcript deltas, not rewritten [extensions], 0.86.0.
- MCP server summaries that change after connect are appended "so earlier messages stay cached" [mcp].
- Switching models loses the cache [virtual-models].
- Since 1.3.0, a thinking-level change keeps the cache on OpenAI GPT-6 with an API key.

Usage fields: `cacheRead`, `cacheWrite`, `cacheWrite1h` [message-types].

---

## 7. MCP: CHANGED. Native since 0.99.0 (2026-09-29)

- **Historic stance:** "does not and will not support MCP". Source: Zechner's blog post of 2025-11-30, via secondary
  write-ups. The pi.dev "What we didn't build" card now reads **"No MCP → Now with MCP+Codemode — MCP is built in"**
  (https://pi.dev, 2026-10-17). Changelog 0.99.0: "Added codemode, tool search, and MCP support as built-in extensions."
  **Course gotcha:** much web material still says "Pi has no MCP". It is out of date.
- **Config files:** `~/.pi/agent/mcp.json` (user) and `.pi/mcp.json` (project, **trusted projects only**). A project entry
  with the same name replaces the user entry. An entry without `command`, `url` or `type` only overrides
  `enabled`, `exposure` and `toolExposure`. The format matches Claude Code and Cursor, so you can "Copy the existing
  `mcpServers` entry" [mcp].
- **Transports:** stdio (`command`, `args`, `env`, `cwd`) and streamable HTTP (`url`, `headers`, `oauth`). **SSE is
  rejected.**
- **Fields:** `timeout`, `enabled`, `description`, `exposure`, `toolExposure`. Values support `${VAR}` and `!command`.
- **Shell commands:**
  - `pi mcp add <name> [--env K=V] [--cwd] [--description] [--exposure] [-l] -- <cmd> [args]`
  - `pi mcp add <name> --url <u> [--bearer-token-env-var NAME | --header K=V | --oauth-*]`
  - `pi mcp remove`, `pi mcp list [--json]` (exits 1 on failure), `pi mcp login|logout`
  - In the TUI: `/mcp`.
  - Logs go to `~/.pi/agent/mcp.log`; OAuth tokens to `~/.pi/agent/mcp-auth.json` [mcp], [cli].
- **Tool naming:** `mcp__<server>__<tool>`, the same convention as Claude Code.
- **Exposure modes:**
  - `codemode` (**default**): callable only from `codemode` JavaScript scripts (QuickJS sandbox), not declared as a tool.
  - `deferred`: loaded by `tool_search`.
  - `direct`: declared like a built-in.
  - `hidden`: unreachable.
  - `toolExposure` sets this per tool, with globs [mcp].
  - **Course implication:** the methodology wants the agent to reach for `codegraph_explore` and Serena's
    `find_referencing_symbols` *unprompted*, so set those tools to `direct` with `toolExposure`.
- **Permissions:** every MCP call, including calls from codemode, goes through the `tool_call` and `tool_result`
  extension handlers, so gates apply. MCP annotations (`readOnlyHint`, …) are available to permission extensions [mcp].
- **CLI filtering:** `--tools` keeps MCP tools unless an entry starts with `mcp__`. `--exclude-tools 'mcp__*'` and
  `--no-mcp` remove them. Built-in MCP can be disabled entirely with `"extensions": ["-builtin:mcp"]`.
- **Alternatives** still supported: the extension `pi-mcp-adapter` [3rd-party, by nicobailon] replaces the built-in when
  installed [mcp]. Or follow Pi's original advice: CLI tools plus a README or skill.

### Connecting the daily servers (config shape from [mcp]; CodeGraph **[TESTED]**)
```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph", "args": ["serve", "--path", "/abs/path/to/your-repo", "--mcp"],
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
- **[TESTED]** `pi mcp add codegraph --description … -- codegraph serve --path /abs/path/to/your-repo --mcp`,
  then `pi mcp list`, printed `codegraph: connected, 1 tool (codemode, global) … tools: codegraph_explore`.
  This shows the default exposure is `codemode`.
- **No `${workspaceFolder}`-style variable is documented.** Use an absolute path in the project `.pi/mcp.json`, or rely on
  `cwd` (relative `cwd` resolves against the session directory) [mcp].
- Serena, Playwright and Context7: the args are copied from the Cursor guide and were **not tested under Pi**.
- [3rd-party] alternatives: `@henryqw/pi-codegraph` and `@vndv/pi-codegraph` (expose `codegraph_explore` as a native Pi
  tool), `@bacnh85/pi-serena`.

---

## 8. Skills, prompt templates, packages

### Skills ([skills], source `skills.ts`)
- Pi implements the **Agent Skills spec** (agentskills.io). A skill is a directory containing `SKILL.md`; it can bundle
  `scripts/`, `references/` and `assets/`.
- **Locations:**
  - `~/.pi/agent/skills/` and project `.pi/skills/` (trusted only).
  - `~/.agents/skills/` and `.agents/skills/` (cwd and ancestors up to the repo root; trust-gated).
  - The `skills` setting array, `--skill <path>`, and packages.
  - Discovery is recursive.
- **`.claude/skills` is NOT auto-discovered**, but it can be added. **[TESTED]**: `"skills": ["~/.claude/skills"]` in
  settings loaded all ~85 of the author's Claude skills (including GSD and graphify). That pours every description into the
  system prompt, so list the wanted directories one by one instead.
- **Frontmatter** (spec fields): `name`, `description` (required; ≤ 1024 chars; drives auto-loading), `license`,
  `compatibility`, `metadata`, `allowed-tools` (experimental), `disable-model-invocation: true` (explicit command only).
  - Name rules: lowercase `a-z0-9-`, ≤ 64 chars, no leading, trailing or double hyphens. Name collisions keep the first
    skill found, with a warning.
  - A missing description means the skill is not loaded.
- **Unknown keys are ignored silently** (source: `[key: string]: unknown`, no warning). **[TESTED]**: the author's
  `day`, `kg` and `kg-refresh` skills, which carry the Claude-specific `trigger: /day` key, loaded fine as `skill:day`,
  `skill:kg` and `skill:kg-refresh`. The YAML `description: >-` folded form in the Cursor `day` skill also parses. All
  five user skills loaded through `--skill`. When the Claude `day` and Cursor `day` were both passed, only one survived:
  first wins.
- **Invocation:**
  - The model auto-loads a skill by `read`ing `SKILL.md` when the description matches.
  - To force one: **`/skill:name [args]`**, where the arguments are appended as a user request.
  - `enableSkillCommands` (default `true`) controls whether skills appear in `/` completion.
  - Skills need a file-read tool (fixed in 0.85.0: "skills being unavailable when Bash is the only enabled tool").
- Examples: https://github.com/anthropics/skills and https://github.com/badlogic/pi-skills [skills].

### Prompt templates ([prompt-templates])
- `~/.pi/agent/prompts/<name>.md` or `.pi/prompts/<name>.md` becomes `/<name>`. Frontmatter: `description`,
  `argument-hint`.
- Arguments: `$1`, `$@`, `$ARGUMENTS`, `${1:-default}`, `${@:N}`, `${@:N:L}`. Only direct `.md` children of the
  directory are loaded.
- This is the closest analogue to Claude Code slash commands.

### Packages and marketplace ([packages], [cli])
- `pi install npm:@scope/pkg@1.0.0 | git:github.com/u/r@v1 | https://… | ./local`, plus `-l` / `--local` for project
  scope. Also `pi list`, `pi remove` / `pi uninstall`, `pi update --extensions`, and `pi config` (TUI to toggle resources
  and built-ins). Try a package once with `pi -e npm:pkg`.
- A package is an npm or git directory with `extensions/`, `skills/`, `prompts/` and `themes/`, or a `"pi": {...}`
  manifest in `package.json`. The `pi-package` keyword lists it in the **gallery at https://pi.dev/packages**: 5,354
  packages on 2026-10-17. The top entries were `pi-mcp-adapter`, `billion-context`, `pi-web-access`, `pi-subagents`, …
- Host packages (`@earendil-works/pi-ai`, `-agent-core`, `-coding-agent`, `-tui`, `typebox`) belong in
  `peerDependencies: "*"`.
- Project packages install only after trust.

---

## 9. Subagents: not built in (a design choice)

- README and homepage: "Pi ships with powerful defaults but **skips features like sub-agents and plan mode**." Under "What
  we didn't build": **"No sub-agents — Spawn Pi instances via tmux, or build your own with extensions, or install a
  package."**
- **Official example extension:** `examples/extensions/subagent/` ([README](https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/extensions/subagent)).
  - Each subagent is a separate `pi` subprocess with an isolated context.
  - Modes: single `{agent, task}`; parallel `{tasks:[…]}` (max 8, 4 concurrent); chain `{chain:[…]}` with a `{previous}`
    placeholder.
  - Agent definitions are Markdown with frontmatter `name`, `description`, `tools`, `model`.
  - Locations: `~/.pi/agent/agents/*.md` always; `.pi/agents/*.md` only with `agentScope: "project" | "both"`.
  - Samples: `scout` (read, grep, find, ls, bash; Haiku), `planner`, `reviewer`, `worker`. Workflow prompts:
    `/implement`, `/scout-and-plan`, `/implement-and-review`.
  - Install: copy or symlink into `~/.pi/agent/extensions/subagent/`.
- **A read-only subagent** is an agent file with `tools: read, grep, find, ls`, without `bash`, `edit` or `write`.
  Note the shipped `scout` includes `bash`.
- [3rd-party]: `pi-subagents` (nicobailon, 0.78.0; "single-agent delegation and scripted multi-agent workflows") and its
  fork `@schovest/pi-subagents`.
- **No agent teams or shared inbox.** NOT DOCUMENTED. The substitute is tmux or parallel `pi -p` / RPC processes.

---

## 10. Hooks = extensions (TypeScript API) ([extensions], `extensions/types.ts`)

- **Where extensions live:** `~/.pi/agent/extensions/*.ts`, or `<dir>/index.ts`; project `.pi/extensions/` (trusted);
  the `extensions` setting; `-e` / `--extension <path | npm:… | builtin:mcp>`.
  - They load through `jiti`, so there is no build step.
  - `/reload` hot-reloads them.
  - They run **in-process with full OS permissions**.
  - They load in all modes; check `ctx.hasUI` and `ctx.mode === "tui"`.
- **Shape:** `export default function (pi: ExtensionAPI) { … }`. The factory may be async. Start long-lived resources in
  `session_start` and clean up in `session_shutdown`.
- **Events** (from `types.ts`):
  - Session and run: `session_start`, `session_shutdown`, `session_before_switch`, `session_before_fork`,
    `session_before_compact`, `session_compact`, `session_compact_failed`, `session_before_tree`, `session_tree`,
    `session_info_changed`, `project_trust`, `resources_discover`, `input`, `before_agent_start`, `agent_start`,
    `turn_start`, `turn_end`, `agent_end`, `agent_before_settle`, `agent_settled`.
  - Messages: `message_start`, `message_update`, `message_end`.
  - Context and providers: `context`, `context_with_system`, `before_provider_headers`, `before_provider_request`,
    `after_provider_response`, `provider_stream_event`.
  - Tools: **`tool_call`** (can mutate `event.input` or block), `tool_execution_start`, `tool_execution_update`,
    `tool_execution_end`, **`tool_result`** (composable rewrite), **`user_bash`** (the author's own `!` commands).
  - Other: `model_select`, `thinking_level_select`, `mcp_servers_change`, `cache_warming_decision`,
    `ui_prompt_start`, `ui_prompt_end`.
- **Blocking:** return `{ block: true, reason }` from `tool_call`; `terminate?: true` is optional. `ToolCallEvent` has
  typed variants per built-in (`toolName: "bash"`, `input.command`).
  - Nested calls (`ctx.executeTool`, codemode scripts, MCP) also pass through `tool_call` [extensions], [mcp].
  - A **`user_bash` handler** can gate the human's `!git push`, but the method says the human owns pushes, so leave
    `user_bash` alone.
- **Other API:** `pi.registerTool({name, label, description, parameters: Type.Object(...), execute(id, params, signal, onUpdate, ctx)})`
  (TypeBox schemas; results are `{content, details}`); `pi.registerCommand(name, {description, handler(args, ctx)})`;
  `registerShortcut`, `registerFlag`, `sendUserMessage`, `sendMessage`, `appendEntry`, `setActiveTools`,
  `registerProvider`, `registerMcpServer`, `registerVirtualModel`, `registerToolRenderer`, `pi.events`.
  - UI: `ctx.ui.confirm`, `select`, `input`, `notify`, `setStatus`, `setWidget`, `custom`, …

### Minimal block-external-git extension: **[TESTED] working on 1.3.0**
File: `~/.pi/agent/extensions/block-external-git.ts` (copy at
``examples/extensions/block-external-git.ts` in this repo`):
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
- **How it was tested:**
  - A fake OpenAI-compatible server (`verify/fake-openai.mjs`), registered in an isolated `models.json`, scripted two bash
    tool calls: `git push origin main`, then `echo allowed-ok`.
  - Run: `pi -p --no-session --model fake/fake-1 -e block-external-git.ts "push it" </dev/null`.
  - **With the extension**, the model received the tool result "Blocked by policy: external git/PR action
    (/\bgit\s+push\b/i)…" and the echo still ran (`allowed-ok`).
  - **Control run without the extension:** the push actually executed and failed with "src refspec main does not match
    any" in an empty scratch repo. That proves the gate, not the environment, stopped it.
- The docs' simplest form is in `examples/extensions/README.md`:
  `pi.on("tool_call", async (event, ctx) => { if (event.toolName === "bash" && event.input.command?.includes("rm -rf")) { … return { block: true, reason: "Blocked by user" }; } });`
- **Limit:** regex gating can be bypassed (`sh -c`, aliases, scripts). For stronger gates, use OS isolation or the
  3rd-party `pi-permission-modes` (tree-sitter bash AST). The same caveat applies to the Cursor hook.

---

## 11. Automation ([cli-integration], [json], [rpc], [sdk])

- **Print mode in CI:**
  ```bash
  pi -p --no-session --approve --model anthropic/<id> "review the diff" </dev/null
  ```
  Use an environment key, not `auth.json`; non-zero exit on error, abort or length. Use `--approve` or `--no-approve` for
  project resources (print mode cannot prompt).
  - `pi auth check --provider X --json` exits 0, 1 or 2 for a readiness gate.
  - `PI_OFFLINE=1`, `PI_SKIP_VERSION_CHECK=1` and `PI_TELEMETRY=0` give deterministic runs [environment-variables].
- **JSON mode:** `pi --mode json "…"` streams events. Assemble text from `message_update` deltas, use `message_end` as
  authoritative, and treat `agent_settled` as the end of automatic work. Don't use Node `readline`; split on LF only
  [json].
- **RPC:** `pi --mode rpc`. In TypeScript, prefer `RpcClient` (from `@earendil-works/pi-coding-agent`, with
  `promptAndWait()`). Extension dialogs are forwarded through the RPC extension-UI sub-protocol [rpc-extension-ui].
- **SDK:**
  ```ts
  import { createAgentSession } from "@earendil-works/pi-coding-agent";
  const { session } = await createAgentSession();      // options: cwd, agentDir, model, thinkingLevel, tools, excludeTools,
  await session.prompt("…");                            // customTools, resourceLoader, sessionManager (SessionManager.inMemory()), settingsManager
  console.log(session.getLastAssistantText()); session.dispose();
  ```
  - `session.subscribe(ev => …)`, `steer()`, `followUp()`, `abort()`, `waitForIdle()`.
  - **SDK sessions do not load built-in MCP or codemode.** Add `createMcpExtension()`, `createCodemodeExtension()` and
    `createToolSearchExtension()` through `DefaultResourceLoader({ extensionFactories })` and call
    `session.bindExtensions()` [sdk].
  - There are 14 typechecked examples in `examples/sdk/`.
- **GitHub Actions:** **NOT DOCUMENTED.** There is no official action and no Bugbot-style PR reviewer. Pattern for the
  course (untested): `npm i -g --ignore-scripts @earendil-works/pi-coding-agent@<pin>`, then the print-mode command above,
  then post the result with `gh` from a later step that the human controls.
- **Scheduling or automations:** none built in. Use cron, CI or `systemd` with `pi -p`.
- **Forking:** a source fork can be rebranded with `"piConfig": {"name", "configDir"}` [cli-integration].

---

## 12. Mapping the methodology onto Pi

| Methodology piece | Pi implementation |
|---|---|
| **Two-level instructions** | Tier 1: `~/.pi/agent/AGENTS.md` (global; the equivalent of `~/.claude/CLAUDE.md`, which Pi does not read) plus the repo-root `AGENTS.md`, small, pointers only. Ancestor files also load: `a workspace-level CLAUDE.md` would load for a session started inside `sample-service`. Tier 2: `data/changes/**`, read on demand, unchanged. Tier 0: `IDENTITY.md`, unchanged. ⚠️ Only one file per directory loads, and AGENTS.md beats CLAUDE.md. A repo with both, like a repo with a gitignored CLAUDE.md, needs them merged or an `AGENTS.override.md`. ⚠️ No nested AGENTS.md below cwd. |
| **Scoped rules** (Cursor `.mdc` globs, Claude `.claude/rules`) | **No native equivalent.** Options: (a) the `claude-rules.ts` example extension lists `.claude/rules/*.md` in the prompt for on-demand reading; (b) turn each scoped rule into a **skill** whose description names the paths it applies to; (c) `APPEND_SYSTEM.md` for always-on gates; (d) an extension that injects rule text in `before_agent_start` when touched paths match. |
| **Tool prevalence** (CodeGraph first, Serena before rename) | Keep the trigger map in AGENTS.md. Make the tools reachable with MCP `toolExposure: direct` (§7); otherwise the model must go through codemode or `tool_search`, which weakens "reach for it unprompted". |
| **Skill `day`** | Copy `SKILL.md` to `~/.pi/agent/skills/day/` or `.pi/skills/day/`, or point `"skills"` at it. The `trigger:` key is ignored harmlessly [TESTED]. Invoke as `/skill:day start`, not `/day`. Optionally add a prompt template `~/.pi/agent/prompts/day.md` ("Run the day skill: $@") to keep `/day` muscle memory; the template approach is my inference, not documented. |
| **Skill `atlassian`** (read-only REST) | Ports unchanged: it is bash plus `atl.py` plus `~/.config/<org>/jira.env`. Read-only is enforced by the tool being GET-only, as in Claude and Cursor. Optional belt and braces: a `tool_call` gate blocking `curl -X (POST|PUT|DELETE)` to `*.atlassian.net`. |
| **Skill `evidence`** (read-only AWS) | Ports unchanged: `uv run … evidence.py` with profile a read-only AWS profile. Pi has no allowlist, so read-only rests on the IAM role (a read-only AWS profile cannot write the KB bucket) and on the skill text. An optional gate can block `aws s3 (cp\|rm\|sync\|mv)` and `ssm put-parameter`. |
| **Skills `kg` / `kg-refresh`** | `kg` ports unchanged (deterministic scripts). `kg-refresh` depends on `/graphify` dispatching **general-purpose extraction subagents**, which Pi lacks. Options: install the subagent example or `pi-subagents` and adapt the extraction step; or run the semantic-extraction step from Claude Code and keep Pi for the deterministic bookends. graphify's support for Pi is **UNVERIFIED**; its SKILL.md does load in Pi [TESTED], but its subagent calls assume Claude Code's Agent tool. |
| **MCP CodeGraph / Serena / Playwright / Context7** | Native `mcp.json` (§7). CodeGraph is [TESTED]. |
| **Block external git ops** | The extension in §10 [TESTED]. Global install at `~/.pi/agent/extensions/block-external-git.ts`, so a repo cannot remove it, and global extensions are not trust-gated. |
| **Read-only subagents** | Subagent example or `pi-subagents`, with agent files limited to `tools: read, grep, find, ls`. Or `pi -p --tools read,grep,find,ls --no-session "…"` as a disposable read-only child process, documented flags [cli]. The plan-mode example shows an allowlist for read-only bash. |
| **Plan gate** (Claude plan mode, Cursor Plan) | Not built in ("No plan mode — write plans to files, or build it with extensions, or install a package"). Use the `plan-mode/` example (`/plan`, `--plan`, `Ctrl+Alt+P`; disables edit/write; bash allowlist), or [3rd-party] `@narumitw/pi-plan-mode` or `@plannotator/pi-extension`. Simplest faithful port: the methodology's "plan in `data/changes/<ticket>/`, human agrees, then implement" needs no tool. |
| **GSD** (Claude-Code-only) | The official `get-shit-done-cc` supports "Claude Code, OpenCode, Gemini and Codex" (npm description), **not Pi**. [3rd-party] `pi-gsd` ("Unofficial port", last published 2026-04-26) and `@opengsd/gsd-pi` (a separate GSD-branded agent) exist but are untested. Suggested course stance: GSD stays Claude-Code-only. In Pi, use phase files in `data/changes/` plus prompt templates (`/plan-phase` → template) plus the subagent example's `/implement` chain. Loading `~/.claude/skills/gsd-*` into Pi "works" at load time [TESTED], but the skills call Claude tools (Task, AskUserQuestion) that Pi lacks. Don't. |
| **Cross-session memory** (claude-mem, auto-memory) | No built-in. The write-once ledgers (`STATUS.md`, `FOLLOWUPS.md`, `SHARP_EDGES.md`) plus `pi -c` / `/resume` plus session JSONL files (greppable; `PI_SESSION_FILE`). [3rd-party]: `pi-memory`, `pi-hermes-memory`, `pi-observational-memory`. claude-mem support for Pi: **UNVERIFIED**. |
| **Permissions policy** | Policy unchanged (the human owns everything external). Mechanism: no allowlist file. Use (1) container or Docker Sandboxes for unattended runs, (2) the global block-git extension, (3) `--tools` / `defaultTools` to drop `write` / `edit` in review sessions, (4) MCP `toolExposure: hidden` for destructive MCP tools, (5) project trust `ask`. |
| **Machine sync** | Add `~/.pi/agent/` to the bring-up (settings, `mcp.json`, extensions, skills, prompts, AGENTS.md). ⚠️ `auth.json`, `mcp-auth.json` and `trust.json` are secrets or machine-local, like `.aws`. Sessions live in `~/.pi/agent/sessions/`. |

---

## 13. Equivalence table: Claude Code → Cursor → Pi

| Concept | Claude Code | Cursor | Pi (1.3.0) |
|---|---|---|---|
| Install | `npm i -g @anthropic-ai/claude-code` / installer | Editor download + `curl https://cursor.com/install \| bash` | `curl -fsSL https://pi.dev/install.sh \| sh` or `npm i -g --ignore-scripts @earendil-works/pi-coding-agent` |
| Binary | `claude` | `agent` (CLI) | `pi` |
| Auth | `/login`, `ANTHROPIC_API_KEY` | `agent login`, `CURSOR_API_KEY` | `/login` (OAuth or key → `~/.pi/agent/auth.json`) or provider env vars; ~40 providers |
| Model / effort | `/model`, effort setting | Model picker | `/model`, `Ctrl+L`, `Ctrl+P`, `--model p/id:high`, `/thinking` (off…max) |
| Headless | `claude -p` | `agent -p --trust [--force]` | `pi -p` (`</dev/null` in CI), `--mode json`, `--mode rpc` |
| Global instructions | `~/.claude/CLAUDE.md` | User rules | `~/.pi/agent/AGENTS.md` (or CLAUDE.md) |
| Project instructions | `CLAUDE.md` (+ nested, `@imports`) | `AGENTS.md` (nested, most specific wins) + `.cursor/rules/*.mdc` | `AGENTS.md` / `CLAUDE.md` in cwd **and ancestors only**; one per directory (AGENTS.md wins); no `@imports`, no globs |
| Override / replace system prompt | `--system-prompt`, `--append-system-prompt` | — | `SYSTEM.md` / `APPEND_SYSTEM.md` (global or `.pi/`), `--system-prompt`, `--append-system-prompt` |
| Scoped rules | `.claude/rules/` (paths) | `.mdc` `globs` | None; skill, extension, or `claude-rules.ts` example |
| Auto-memory | `MEMORY.md` auto-memory | Memories (auto) | None built in; extensions or packages |
| Permissions | `settings.json` allow/deny (`mcp__s__t`, `Bash(…)`) + prompts | `permissions.json` `mcpAllowlist` / `terminalAllowlist` + approvals | **No prompts, no allowlist file.** `--tools` / `--exclude-tools` / `defaultTools` (tool names), MCP `toolExposure: hidden`, project trust, extensions, containers |
| Sandbox | Optional sandbox mode | — | None built in; Docker, Docker Sandboxes, OpenShell, Gondolin extension, `sandbox/` example |
| Sessions storage | `~/.claude/projects/…jsonl` | Chat history | `~/.pi/agent/sessions/--<cwd>--/<ts>_<id>.jsonl` (tree, v3) |
| Resume | `claude -c` / `-r` | Chat list | `pi -c`, `pi -r`, `/resume`, `--session` |
| Branch / rewind | `/rewind`, Esc-Esc | `/rewind` (CLI) | `/tree` (in-file branches + branch summary), `/fork`, `/clone`, Esc-Esc |
| Export / share | `/export` | — | `/export` (HTML/JSONL), `/share` (gist or Radius), `pi --export` |
| Compaction | Auto + `/compact <focus>` | Auto + `/summarize` | Auto (`compaction.*` settings) + `/compact [instructions]` + extension hooks |
| Prompt caching | Automatic; `ENABLE_PROMPT_CACHING_1H`-style env | Not exposed | Automatic `cache_control` / affinity; `PI_CACHE_RETENTION=long`; `cacheWarming`; `showCacheMissNotices` |
| MCP config | `claude mcp add`, `.mcp.json`, `~/.claude.json` | `.cursor/mcp.json`, `~/.cursor/mcp.json` | `pi mcp add`, `.pi/mcp.json` (trusted), `~/.pi/agent/mcp.json`; same `mcpServers` shape; stdio + streamable HTTP (no SSE); `exposure` modes |
| MCP tool names | `mcp__server__tool` | `server:tool` | `mcp__server__tool` |
| Skills | `~/.claude/skills`, `.claude/skills` | `.cursor/skills` (+ reads `.claude/skills`) | `~/.pi/agent/skills`, `.pi/skills`, `~/.agents/skills`, `.agents/skills`, `"skills"` setting (can point at `~/.claude/skills`) |
| Invoke a skill | `/name` | `/name` | `/skill:name [args]` |
| Slash commands | `.claude/commands/*.md` | Skills / commands | Prompt templates `~/.pi/agent/prompts/*.md` → `/name` |
| Marketplace | `/plugin install` | cursor.com/marketplace (UI) | `pi install npm:… / git:…`; gallery pi.dev/packages; `pi config` |
| Subagents | Built in (`Agent` tool, `.claude/agents/`) | Built in (`.cursor/agents/`) | **None built in**; `examples/extensions/subagent` (`~/.pi/agent/agents/*.md`), `pi-subagents`, tmux |
| Agent Teams | Built in | No (Background Agents) | No; parallel `pi` processes / RPC |
| Plan mode | Built in | Plan mode | **None**; `plan-mode/` example or packages |
| Hooks | `settings.json` hooks (shell, JSON stdin/stdout, `exit 2`) | `hooks.json` (`beforeShellExecution`, … `permission: deny`) | **TypeScript extensions**: `pi.on("tool_call", …) → {block:true, reason}`, `tool_result`, `user_bash`, `before_agent_start`, session events… |
| Custom tools | MCP or SDK | MCP | `pi.registerTool()` (TypeBox) or MCP |
| SDK | Claude Agent SDK | `@cursor/sdk` | `@earendil-works/pi-coding-agent` `createAgentSession()`, `RpcClient` |
| CI review bot | GitHub Action | Bugbot | None official; `pi -p` in your own workflow |
| GSD | Supported | Not supported | Not officially supported (unofficial `pi-gsd`) |

---

## 14. Gotchas, versions, recent changes

1. **Name and package moved.** `badlogic/pi-mono` became `earendil-works/pi`. `@mariozechner/pi-coding-agent` is
   deprecated in favour of `@earendil-works/pi-coding-agent` (2026-05-07). Old tutorials and imports use the old scope;
   extensions must import types from `@earendil-works/pi-coding-agent`.
2. **MCP flip-flop.** No MCP up to 0.87.x; native MCP plus codemode since **0.99.0 (2026-09-29)**; hardened in 1.0
   (2026-10-01). The default MCP exposure is `codemode`: the tools are invisible as declared tools. Set `toolExposure`
   to `direct` for tools the methodology wants used unprompted. 1.0.4 changed `--tools` so it keeps MCP tools unless an
   entry starts with `mcp__`.
3. **`--tools` semantics changed in 1.1.0.** A list made only of `+x` / `-x` entries adjusts the defaults; plain names
   replace them; the two kinds cannot be mixed. 1.3.0: resumed sessions keep their active tools.
4. **CLI help inconsistency.** The synopsis lists `pi mcp <list|login|logout>`, but `add` and `remove` exist too
   ([cli] table and `pi mcp add --help`) [TESTED].
5. **Context-file rules differ from Claude and Cursor:** one file per directory (AGENTS.md shadows CLAUDE.md); ancestors
   only, no subdirectories; context files ignore project trust.
6. **`pi -p` waits for stdin EOF** when stdin is a non-TTY pipe. Add `</dev/null` in harnesses and CI [TESTED].
7. **Print, JSON and RPC cannot show the trust prompt.** With the default `defaultProjectTrust: "ask"`, project `.pi/`
   resources (including `.pi/mcp.json` and `.pi/extensions`) are **skipped silently** unless `--approve` is passed.
   Global `~/.pi/agent/` resources still load.
8. **JSON mode does not exit non-zero** on a failed or aborted assistant run. Inspect the events [cli-integration].
9. **SDK sessions do not load built-in MCP or codemode.** Add the factories explicitly [sdk].
10. **Skills:** `/skill:name`, not `/name`; unknown frontmatter keys such as `trigger:` are ignored silently; with name
    collisions the first wins; pointing `"skills"` at all of `~/.claude/skills` loads every skill (~85 here), which costs
    prompt tokens.
11. **Project-local subagents** in the example extension load only with `agentScope: "project" | "both"`.
12. **Windows:** `powershell` is a built-in tool (`defaultTools: ["-bash", "+powershell"]`). Windows Terminal reserves
    some Alt shortcuts [windows], [terminal-setup]. WSL2 behaves like Linux [TESTED].
13. **Telemetry:** `enableInstallTelemetry` defaults to `true` (anonymous install and update reports plus provider
    attribution headers). Disable with `PI_TELEMETRY=0` or the setting [settings], [environment-variables].
14. **Contribution policy:** new issues and PRs from new contributors are closed automatically [README].
15. **Recent changes, per the changelog** (https://pi.dev/changelog, read 2026-10-17):
    - 0.86.0 (09-19): cache warming; transcript-aware prompt and tool changes.
    - 0.87.0 (09-21): `context_edit`; image input limits.
    - 0.99.0 (09-29): codemode, MCP, `tool_search` built in; classifier models.
    - 1.0.0 (10-01): leaner codemode; `models.generateImages()`; Radius in `/login`; MCP OAuth hardening; fullscreen
      default; Pi Durable split out as a separate experimental package.
    - 1.0.1: project MCP overrides; `registerToolRenderer`.
    - 1.0.3: Azure provider renamed to `azure`.
    - 1.0.4: `*` patterns in `--tools`; `--no-mcp`.
    - 1.1.0: `+/-` in `--tools`; GPT-6 Luna classifier.
    - 1.2.0: `reachesTools`, namespace aliases.
    - 1.3.0 (10-15): `sessionShareDestination`; cache-preserving thinking changes on GPT-6; Kimi Code over Chat
      Completions (base URL override must include `/v1`); model switches drop earlier models' thinking blocks.

---

## Appendix: hands-on artefacts (scratchpad, not part of any repo)
- (local scratch, not shipped): Pi 1.3.0 install, isolated agent dir (`agent/` holds the test `models.json`, `auth.json` and
  `mcp.json`).
- (local scratch, not shipped): the tested gate.
- (local scratch, not shipped) and `server.log`: the fake LLM used to drive tool calls.
- (local scratch, not shipped): all 42 doc pages as Markdown, `changelog.xml`, example extensions under `ex/`, source excerpts
  under `src/`.
- (local scratch, not shipped): an abandoned SDK-plus-faux-provider attempt. The runtime rejected the unregistered
  provider "faux"; the black-box CLI test replaced it.
