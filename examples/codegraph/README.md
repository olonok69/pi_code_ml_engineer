# CodeGraph — local code intelligence, via MCP in Pi (§09)

A *local-first* tool that indexes your code with **tree-sitter** into a **SQLite graph** and exposes it
as an MCP server (and a CLI). Repo: <https://github.com/colbymchenry/codegraph> · Docs:
<https://colbymchenry.github.io/codegraph/>.

## What it indexes (deterministic, from the AST — not summarised by an LLM)

- **Symbols:** functions, classes, methods, types, routes, components.
- **Edges:** calls, imports, inheritance, references, framework relations.
- **Files:** structure + full-text search.

Everything lives in `.codegraph/` (local SQLite). **No external services, no API keys.** Add
`.codegraph/` to `.gitignore`.

## CLI (same as in the other volumes)

```bash
codegraph init        # create .codegraph/ and build the index
codegraph sync        # incremental re-index (do this after editing on WSL /mnt — the watcher can miss changes)
codegraph explore "<symbol or question>"
codegraph serve --path <repo> --mcp
codegraph status
```

## Connect it to Pi — [TESTED] on Pi 1.3.0

```bash
pi mcp add codegraph --description "Code intelligence: verbatim source + call paths + blast radius" \
  -- codegraph serve --path "$PWD" --mcp
pi mcp list    # -> codegraph: connected, 1 tool (codemode, global) … tools: codegraph_explore
```

That registers it with the **default `codemode` exposure** — the tool is not declared to the model.
For the methodology, make it `direct` (edit `~/.pi/agent/mcp.json` or the project `.pi/mcp.json`):

```json
"codegraph": {
  "command": "codegraph",
  "args": ["serve", "--path", "<absolute-repo-path>", "--mcp"],
  "toolExposure": { "codegraph_explore": "direct" }
}
```

- No `${workspaceFolder}` variable is documented in Pi: use the absolute path. Set `--path` and
  `codegraph_explore` will not need `projectPath`; pass it only to query **another** indexed repo.
- A project `.pi/mcp.json` loads only in a trusted folder.
- [3rd-party] alternatives exposing `codegraph_explore` as a native Pi tool: `@henryqw/pi-codegraph`,
  `@vndv/pi-codegraph` (untested).
- No MCP at all? The CLI works from `bash`: `codegraph explore "<symbol>"` prints the same output.

Treat the source `codegraph_explore` prints as **already read** — do not re-open that file.

## CodeGraph vs. Serena vs. grep

| Question | Tool |
|---|---|
| Survey: source + callers + blast radius + tested? | **CodeGraph** `codegraph_explore` |
| Precise check before rename/delete | **Serena** `find_referencing_symbols` |
| Overview / body of one symbol | Serena, or the source `explore` already returned |
| Literal / string | grep |

Methodology stage 4: CodeGraph first, Serena before touching. See
[`../methodology/REAL_EXAMPLE.md`](../methodology/REAL_EXAMPLE.md).

## Blast radius

The ripple of touching a symbol: transitive callers + coverage flags. CodeGraph's blast radius is *flat*
(it mixes same-named symbols); the fine-grained pre-rename verdict comes from Serena.
