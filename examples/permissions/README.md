# Permissions and safety in Pi — none by design (§02)

Claude Code has an allow/deny list in `settings.json` plus approval prompts. Cursor has
`permissions.json` (`mcpAllowlist` / `terminalAllowlist`) plus approvals. **Pi has no approval prompts,
no allowlist file and no sandbox — deliberately.**

- Quickstart: "It does not ask before every tool call."
- Security page: "Pi can read, change, and execute files with the permissions of the account that started
  it, and it does not ask for approval before every tool call."
- Homepage, *What we didn't build*: **"No permission popups — Run in a container, or build your own
  confirmation flow with extensions."**
- Out of scope for security reports: "lack of a built-in sandbox", prompt injection, user-installed extensions.

The **policy** of the methodology does not change (the human owns everything external). Only the
**mechanism** does. Five layers, cheapest first:

| # | Mechanism | What it does | What it does NOT do |
|---|---|---|---|
| 1 | **Container / Docker Sandboxes / OpenShell** | Isolates the whole process: mount only the workspace, never the host `~/.pi/agent` | — this is the only real boundary for unattended runs |
| 2 | **Global extension** (`~/.pi/agent/extensions/block-external-git.ts`) | Content-based gate on `tool_call` → `{ block: true, reason }` ([`../extensions/`](../extensions/)) | Regex gates can be bypassed (`sh -c`, aliases) |
| 3 | **Static tool restriction** — `--tools`, `--exclude-tools`, `-nbt`, `-nt`, `defaultTools` | Removes tools *by name* (e.g. drop `write`/`edit` for a review session) | Does not inspect command content |
| 4 | **MCP exposure** — `exposure: "hidden"` / per-tool `toolExposure` | Makes destructive MCP tools unreachable | — |
| 5 | **Project trust** — `/trust`, saved in `~/.pi/agent/trust.json`; `defaultProjectTrust: "ask" \| "always" \| "never"` | Decides whether a folder's **resources** load (`.pi/settings.json`, `.pi/mcp.json`, `.pi/extensions\|skills\|prompts\|themes`, `.pi/SYSTEM.md`, `.agents/skills`) | **Does not sandbox tool calls**; context files (`AGENTS.md`/`CLAUDE.md`) load regardless |

## Trust gotchas

- Print, JSON and RPC modes cannot prompt. With the default `"ask"` they **skip project resources
  silently** unless you pass `--approve` / `-a` (or `--no-approve` / `-na` to make the skip explicit).
- The project `sessionDir` setting is read *before* trust is resolved.
- `defaultProjectTrust` is a user (agent-directory) setting only.

## `settings.json.example`

[`settings.json.example`](./settings.json.example) uses only keys documented in Pi's settings page as
captured in the course findings. User settings live in `~/.pi/agent/settings.json`; project settings in
`.pi/settings.json` (trust-gated). Project settings override agent-directory settings; resource lists are
combined. `defaultProjectTrust` and `cacheWarming` are honoured only in the user (agent-directory) file.

| Key | Value in the example | Why |
|---|---|---|
| `defaultProjectTrust` | `"ask"` (the default) | Stated explicitly so nobody "simplifies" it to `"always"` |
| `defaultTools` | `["-write"]` | `+name` / `-name` adjust the default set (`read`, `bash`, `edit`, `write`); here: no `write` by default. Illustrative — pick your own |
| `compaction.*` | the documented defaults | See [`../context/`](../context/) |
| `cacheWarming`, `showCacheMissNotices` | `"streaming"`, `true` | See [`../prompt-caching/`](../prompt-caching/) |
| `skills` | two directories | Point at individual skill folders — `"skills": ["~/.claude/skills"]` loads **every** Claude skill (~85 in the tested install) into the prompt |
| `enableInstallTelemetry` | `false` | Defaults to `true`; `PI_TELEMETRY=0` does the same |

> Built-in tools: `read`, `bash`, `powershell`, `edit`, `write`, `grep`, `find`, `ls` — four (`read`,
> `bash`, `edit`, `write`) are on by default. On Windows: `defaultTools: ["-bash", "+powershell"]`.

## Shipped example extensions for confirmation flows (Pi repo, untested here)

`permission-gate.ts` (confirm `rm -rf`, `sudo`, `chmod 777`; **blocks by default when there is no UI**),
`protected-paths.ts`, `confirm-destructive.ts`, `dirty-repo-guard.ts`, `plan-mode/`, `sandbox/` (OS
sandbox via `@anthropic-ai/sandbox-runtime`). The docs also show an MCP-annotation-based approval gate.

[3rd-party], untested: `@gotgenes/pi-permission-system`, `pi-permission-modes` (bubblewrap/sandbox-exec,
allow/ask/deny, bash AST gating), `@czottmann/pi-automode`, `@erichll/pi-auto-review`.
