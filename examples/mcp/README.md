# MCP in Pi — built in since 0.99.0 (§04)

> **Course gotcha:** much web material still says "Pi has no MCP". That was Pi's original stance
> ("does not and will not support MCP", late 2025). It changed: **0.99.0 (2026-09-29)** added "codemode,
> tool search, and MCP support as built-in extensions"; 1.0 hardened it. The pi.dev card now reads
> **"No MCP → Now with MCP+Codemode — MCP is built in"**.

## Config files

| Scope | File | Notes |
|---|---|---|
| User | `~/.pi/agent/mcp.json` | Always loads |
| Project | `.pi/mcp.json` | **Trusted projects only**; print/JSON/RPC need `--approve` |

Same `mcpServers` shape as Claude Code and Cursor — you can copy existing entries. A project entry with
the same name replaces the user entry; an entry without `command`, `url` or `type` only overrides
`enabled`, `exposure` and `toolExposure`.

- **Transports:** stdio (`command`, `args`, `env`, `cwd`) and streamable HTTP (`url`, `headers`,
  `oauth`). **SSE is rejected.**
- **Fields:** `timeout`, `enabled`, `description`, `exposure`, `toolExposure`. Values support `${VAR}`
  and `!command`.
- **No `${workspaceFolder}`-style variable is documented.** Use an absolute path in `.pi/mcp.json`, or
  rely on `cwd` (relative `cwd` resolves against the session directory).
- **Tool names:** `mcp__<server>__<tool>` — the same convention as Claude Code (Cursor uses `server:tool`).

## Shell commands

```bash
pi mcp add codegraph --description "Code intelligence" -- codegraph serve --path "$PWD" --mcp
pi mcp add context7 --url https://mcp.context7.com/mcp
pi mcp list            # --json; exits 1 on failure
pi mcp remove <name>
pi mcp login <name>    # / logout — OAuth servers; tokens in ~/.pi/agent/mcp-auth.json
```

In the TUI: `/mcp`. Logs: `~/.pi/agent/mcp.log`. (`pi --help` lists only `pi mcp <list|login|logout>`,
but `add` and `remove` exist — [TESTED].)

## Exposure modes — the part that matters for the methodology

| Mode | What the model sees |
|---|---|
| `codemode` (**default**) | Nothing declared; tools callable only from `codemode` JavaScript scripts (QuickJS sandbox). A one-line server summary sits in the prompt |
| `deferred` | Loaded on demand through `tool_search` |
| `direct` | Declared like a built-in tool |
| `hidden` | Unreachable |

`exposure` sets the server default; `toolExposure` sets it **per tool**, with globs.

**[TESTED]** `pi mcp add codegraph … -- codegraph serve --path <repo> --mcp` then `pi mcp list` printed
`codegraph: connected, 1 tool (codemode, global) … tools: codegraph_explore` — proof the default is
`codemode`.

**Implication:** the methodology wants the agent to reach for `codegraph_explore` and Serena's
`find_referencing_symbols` **unprompted**. Behind codemode or `tool_search` that habit weakens. So
[`mcp.json.example`](./mcp.json.example) sets those tools to `direct` and leaves Playwright/Context7
`deferred` (useful, occasional, not worth a declaration every turn).

Status of each entry: **CodeGraph [TESTED] under Pi**; Serena, Playwright and Context7 args are copied
from the Cursor guide and were **not tested under Pi**.

## Permissions and filtering

- Every MCP call — including calls from codemode scripts — goes through the `tool_call` / `tool_result`
  extension handlers, so your gates apply ([`../extensions/`](../extensions/)). MCP annotations
  (`readOnlyHint`, …) are available to permission extensions.
- `--tools` keeps MCP tools unless an entry starts with `mcp__`; `--exclude-tools 'mcp__*'` and
  `--no-mcp` remove them; `"extensions": ["-builtin:mcp"]` disables built-in MCP entirely.
- MCP text results over 20 KB are middle-truncated, the full text saved to a temp file.
- **SDK sessions do not load built-in MCP** — see [`../automation/`](../automation/).

## Alternatives

- [3rd-party] `pi-mcp-adapter` (replaces the built-in when installed), `@henryqw/pi-codegraph` /
  `@vndv/pi-codegraph` (`codegraph_explore` as a native Pi tool), `@bacnh85/pi-serena`. Untested.
- Pi's original advice still works: a CLI tool plus a README or skill (e.g. `codegraph explore "…"` from bash).

## Secrets

Never hardcode tokens: use `env` with `${VAR}`, `!command` (secret manager), or
`pi mcp add <name> --url <u> --bearer-token-env-var NAME`.
