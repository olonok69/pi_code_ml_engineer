# Serena — semantic code navigation (MCP in Pi) (§09)

[Serena](https://github.com/oraios/serena) gives the agent symbol-level understanding through LSP.
Same tool as in Claude Code and Cursor; only **how the server is registered** changes.

## Registering it in Pi

Add to `~/.pi/agent/mcp.json` or `.pi/mcp.json` (see [`../mcp/mcp.json.example`](../mcp/mcp.json.example)):

```json
"serena": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
  "toolExposure": {
    "find_symbol": "direct",
    "find_referencing_symbols": "direct",
    "get_symbols_overview": "direct"
  }
}
```

Or from the shell: `pi mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server`
(then add the `toolExposure` block by hand). Check with `pi mcp list` or `/mcp`.

> ⚠️ These args are copied from the Cursor guide and were **not tested under Pi** (only CodeGraph was).
> [3rd-party] alternative: `@bacnh85/pi-serena` (untested).

Why `direct` for three tools: Pi's default `codemode` exposure hides MCP tools from the model's tool
list; the methodology wants `find_referencing_symbols` used **unprompted** before every rename.

## The tools that matter

| Tool | What it does | When |
|---|---|---|
| `find_symbol` | Locate a symbol (`body=true` → its body) | One method out of a 5k-line file |
| `get_symbols_overview` | File skeleton | First look |
| `find_referencing_symbols` | References disambiguated by class | **Mandatory before rename/delete** |
| `search_for_pattern` | Pattern with symbolic context | Literal + its enclosing symbol |
| `activate_project` | Switch the indexed project | Multi-repo |

The last two stay reachable through codemode / `tool_search` without being declared every turn.

## Precedence (same as in Claude Code and Cursor)

1. CodeGraph `codegraph_explore` first.
2. Serena `find_referencing_symbols` before rename/delete.
3. grep/read only for literals.

Scout agent: [`../subagents/agents/refactor-scout.md`](../subagents/agents/refactor-scout.md).

## Permissions

Claude Code used an allowlist (`mcp__serena__…` in `settings.local.json`); Cursor uses UI approvals +
`permissions.json`. Pi has neither: Serena's tools run without prompts. If you need to stop a
destructive tool, set it to `hidden` with `toolExposure`, or gate it in a `tool_call` extension (MCP
calls are named `mcp__serena__<tool>`).
