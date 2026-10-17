# AGENT SETUP — day-to-day tools (Pi / Part 2)

> Smoke checklist for the five tools the methodology leans on, wired into **Pi**.
> Guides: [`../../SPEAKER_GUIDE.md`](../../SPEAKER_GUIDE.md) · [`../../TECHNICAL_GUIDE.md`](../../TECHNICAL_GUIDE.md)
> §7 + §13 · [`PI_ADAPTATION.md`](./PI_ADAPTATION.md). The Cursor version of this checklist lives in the
> Cursor volume.

## The 5 tools

| # | Tool | Kind | Smoke test |
|---|---|---|---|
| 1 | **CodeGraph** | MCP + CLI | `codegraph explore "<known symbol>"` · `pi mcp list` shows `codegraph: connected` **[TESTED]** |
| 2 | **Serena** | MCP (`uvx`) | `find_referencing_symbols` on a known method (untested under Pi — rehearse) |
| 3 | **Playwright** | MCP (`npx`, `exposure: deferred`) | Open `https://example.com`, report the title |
| 4 | **Context7** | MCP URL (`deferred`) | Library docs query (e.g. pytest fixtures) |
| 5 | **kg** | Skill + `kg_query.sh` | `/skill:kg letter-end` or `bash data/knowledge-graph/kg_query.sh letter-end` |

## Why they often look "not installed" in Pi

1. The folder is **not trusted** → `.pi/mcp.json`, `.pi/skills`, `.pi/extensions` are skipped. `/trust`.
2. You are in print/JSON/RPC mode → no trust prompt → project resources skipped. Add `--approve`.
3. The tool is connected but **invisible to the model**: default MCP exposure is `codemode`. Set
   `toolExposure: { "codegraph_explore": "direct" }` (and Serena's lookups).
4. CodeGraph `--path` still points at another machine's path (no `${workspaceFolder}` variable is documented).
5. Serena/Playwright need a first cold start (`uvx` / `npx` download); check `~/.pi/agent/mcp.log`.
6. An SDK session: built-in MCP is **not** loaded unless you add the MCP extension factories.

## Agent instructions (short)

When asked to configure tools in a repo:

1. Install host CLIs if missing (`codegraph`, `uvx`, `node`/`npx`, `bash`).
2. Write `.pi/mcp.json` from [`pi/mcp.json.example`](./pi/mcp.json.example) with this repo's absolute path.
3. Ensure the skills (`kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff`) and the global
   `block-external-git.ts` extension exist under `~/.pi/agent/` ([`pi/README.md`](./pi/README.md)).
4. Ask the human to `/trust` the folder.
5. Run all five smoke tests; report a pass/fail table with evidence.

Do **not** look for an allowlist to port — Pi has none. Do **not** push/PR unless asked.

## Pack paths

- MCP example: [`pi/mcp.json.example`](./pi/mcp.json.example)
- Install block: [`pi/README.md`](./pi/README.md)
- Examples: [`../../examples/mcp/`](../../examples/mcp/), [`../../examples/codegraph/`](../../examples/codegraph/), [`../../examples/serena/`](../../examples/serena/)
