# Context window in Pi — the resource that governs everything (§03)

Instructions, MCP, skills and subagents all exist to avoid wasting the context window. Pi's take is
**minimalism by default**: a small system prompt and four default tools.

## 1. Anatomy: what fills the context in Pi

| Block | Notes |
|---|---|
| Pi's system prompt | Small by design. Replace with `SYSTEM.md`, append with `APPEND_SYSTEM.md` |
| Default tools | `read`, `bash`, `edit`, `write` — four declarations, nothing else unless you add it |
| Context files | Global `~/.pi/agent/AGENTS.md` + `AGENTS.md`/`CLAUDE.md` of cwd and every parent (**you control this**) |
| Skills | Only **name, description and path** until a skill is used |
| MCP | Default `codemode` exposure: tools are **not** declared; a one-line summary per server sits in the `mcp_servers` prompt section. `direct` tools are declared like built-ins |
| Conversation | Messages, files read, command output, tool results |

## 2. Compaction

- The footer shows context usage. **Auto-compaction** fires when
  `contextTokens > contextWindow - reserveTokens`; it is also checked between tool batches inside a run,
  with one compact-and-retry on overflow.
- **Manual:** `/compact [instructions]` — the instructions focus the summary. Disabling auto does not
  disable the manual command.
- The summary is structured: Goal / Constraints & Preferences / Progress / Key Decisions / Next Steps /
  Critical Context. It becomes a `CompactionEntry` (`summary`, `firstKeptEntryId`, `tokensBefore`,
  `details.readFiles/modifiedFiles`); **the original entries stay in the session file**.
- Summarisation requests **disable prompt-cache writes**.

| Setting | Default |
|---|---|
| `compaction.enabled` | `true` |
| `compaction.reserveTokens` | `16384` |
| `compaction.keepRecentTokens` | `20000` |
| `compaction.modelOverrides` | per `provider/modelId` |
| `branchSummary.reserveTokens` | `16384` |
| `branchSummary.skipPrompt` | `false` |

Extension hooks: `session_before_compact` (cancel, or supply your own summary), `session_compact`,
`session_compact_failed`, `session_before_tree`. Examples in the Pi repo: `custom-compaction.ts`,
`trigger-compact.ts`.

## 3. Side quests without polluting the main thread

- **`/tree`** — move to another branch *inside the same session file*; it can summarise the branch you
  leave. Double-Esc opens it by default (`doubleEscapeAction`).
- **`/fork`** — new session from an earlier user message. **`/clone`** — copy the active branch.
- **Subagents** are not built in ([`../subagents/`](../subagents/)); a disposable
  `pi -p --no-session --tools read,grep,find,ls "…" </dev/null` is the zero-install side quest.
- **`/new`** when the task is unrelated. `/handoff <goal>` exists only as an example extension.

## 4. The lean levers (the ones we actually use)

1. **Small `AGENTS.md` + pointers** — [`../agents-md/`](../agents-md/), [`AGENTS.pointers-example.md`](./AGENTS.pointers-example.md).
2. **Few `direct` MCP tools** — only the ones the method wants used unprompted (`codegraph_explore`,
   Serena's three); the rest `deferred` ([`../mcp/`](../mcp/)).
3. **Codemode filters big output** before the model sees it; MCP text results over 20 KB are
   middle-truncated with the full text saved to a temp file.
4. **List skill directories one by one** — pointing `skills` at all of `~/.claude/skills` put ~85
   descriptions in the prompt in the tested install.
5. **Minimal runs**: `--no-context-files`, `--no-skills`, `--no-extensions`.
6. **Targeted reads** — CodeGraph first ([`../codegraph/`](../codegraph/)): one call with signal beats ten whole files.

## 5. Claude Code → Cursor → Pi

| Claude Code | Cursor | Pi |
|---|---|---|
| `/context` | Context ring in the UI | Footer usage + `/session` (tokens, cost) |
| `/compact [focus]` + auto | `/summarize` + auto | `/compact [instructions]` + auto (`compaction.*`) + extension hooks |
| `/rewind`, Esc-Esc | `/rewind` (CLI) | `/tree`, `/fork`, `/clone`, Esc-Esc |
| `@import` in `CLAUDE.md` | none | NOT DOCUMENTED — pointers only |

**Link to Part 2:** the CodeGraph → Serena → grep precedence is a context-management policy.
