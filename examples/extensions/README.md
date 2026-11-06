# Extensions — Pi's answer to hooks (§07)

Claude Code has `settings.json` hooks (shell command, JSON on stdin, `exit 2` = deny). Cursor has
`.cursor/hooks.json` (`beforeShellExecution`, `permission: "deny"`). **Pi has neither: the same job is
done by a TypeScript extension** that subscribes to events in-process.

```ts
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    // return { block: true, reason: "…" } to stop the call; undefined to let it run
  });
}
```

## Where extensions live and how they load

| Location | Notes |
|---|---|
| `~/.pi/agent/extensions/*.ts` (or `<dir>/index.ts`) | Global. **Not trust-gated** — the right home for safety gates a repo must not remove |
| `.pi/extensions/` | Project; loads only in a **trusted** folder (and print/JSON/RPC need `--approve`) |
| `extensions` setting · `-e` / `--extension <path \| npm:… \| builtin:mcp>` | Explicit / one-off |

- Loaded through `jiti`: **no build step**. `/reload` hot-reloads them.
- They run **in-process with full OS permissions** — an extension is code you trust, not a sandbox.
- They load in all modes; check `ctx.hasUI` / `ctx.mode === "tui"` before showing UI.
- Import types from **`@earendil-works/pi-coding-agent`** (the old `@mariozechner/…` scope is deprecated).

## Files here

| File | Status | What it does |
|---|---|---|
| [`block-external-git.ts`](./block-external-git.ts) | **[TESTED] on Pi 1.3.0 and 1.5.0** | Blocks `git push`, `gh pr create/merge/…`, `gh release`, `gh repo create/delete/edit`, merges from `origin/`/`upstream/`. The methodology's "human owns external actions" gate. Live copy: [`../../.pi/extensions/`](../../.pi/extensions/) |
| [`protect-env.untested.ts`](./protect-env.untested.ts) | UNTESTED pattern | Blocks shell commands that print/copy `.env`. Covers bash only: the `read` tool's input field names are **not in the findings** |
| [`tool-call-logger.untested.ts`](./tool-call-logger.untested.ts) | UNTESTED pattern | Appends every tool call to `.pi-tool-calls.jsonl`; never blocks |

**How `block-external-git.ts` was tested** (2026-10-17 on 1.3.0; re-run 2026-11-06 on 1.5.0 with
[`../local-models/verify/run.sh`](../local-models/verify/run.sh)): a fake OpenAI-compatible server scripted two
bash tool calls — `git push origin main`, then `echo allowed-ok`. Run:
`pi -p --no-session --model fake/fake-1 -e block-external-git.ts "push it" </dev/null`. With the
extension the model received *"Blocked by policy: external git/PR action…"* and the echo still ran.
Control run without it: the push actually executed (and failed on an empty scratch repo) — so the gate,
not the environment, stopped it.

Install the tested gate globally:

```bash
mkdir -p ~/.pi/agent/extensions
cp examples/extensions/block-external-git.ts ~/.pi/agent/extensions/
```

## Event map: Cursor hooks → Pi events

| Cursor `hooks.json` event | Claude Code hook | Pi extension event |
|---|---|---|
| `beforeShellExecution` | `PreToolUse` (Bash) | `tool_call` with `event.toolName === "bash"` (or `"powershell"`) → `{ block: true, reason }` |
| `preToolUse` | `PreToolUse` | `tool_call` (can also **mutate** `event.input`) |
| `postToolUse` | `PostToolUse` | `tool_execution_end` · `tool_result` (composable rewrite of the result) |
| `beforeReadFile` | `PreToolUse` (Read) | `tool_call` on the read tool — input shape not in the findings; see `protect-env` note |
| `afterFileEdit` | `PostToolUse` (Edit/Write) | `tool_result` / `tool_execution_end` for `edit` / `write` |
| `beforeMCPExecution` | `PreToolUse` (`mcp__…`) | `tool_call` — every MCP call, **including calls made from codemode scripts**, passes through it |
| `beforeSubmitPrompt` | `UserPromptSubmit` | `input` · `before_agent_start` (can change prompt sections per run) |
| `stop` | `Stop` | `agent_end` · `agent_settled` |
| `sessionStart` / `sessionEnd` | `SessionStart` / `SessionEnd` | `session_start` / `session_shutdown` |
| — | `PreCompact` | `session_before_compact` (cancel, or supply a custom summary) |
| — (the human's own shell) | — | `user_bash` (the user's `!` commands) — the method leaves it alone: the human owns pushes |

Full event list (from `extensions/types.ts`): `session_*`, `project_trust`, `resources_discover`,
`input`, `before_agent_start`, `agent_start`, `turn_start`, `turn_end`, `agent_end`,
`agent_before_settle`, `agent_settled`, `message_start|update|end`, `context`, `context_with_system`,
`before_provider_headers`, `before_provider_request`, `after_provider_response`,
`provider_stream_event`, `tool_call`, `tool_execution_start|update|end`, `tool_result`, `user_bash`,
`model_select`, `thinking_level_select`, `mcp_servers_change`, `cache_warming_decision`,
`ui_prompt_start`, `ui_prompt_end`.

## Differences that matter

1. **Fail-safe is built in:** "A `tool_call` handler failure blocks the tool as a fail-safe" — the
   equivalent of Cursor's `failClosed`, but always on. That is why the logger catches its own errors.
2. **No `ask` from the hook contract.** Need a confirmation? Use `ctx.ui.confirm(…)` inside the handler —
   and decide what happens without a UI. Pi's own `permission-gate.ts` example **blocks by default when
   there is no UI**; copy that choice.
3. **Nested calls are gated too**: `ctx.executeTool`, codemode scripts and MCP all pass through `tool_call`.
4. **Regex gating can be bypassed** (`sh -c`, aliases, scripts). Same caveat as the Cursor hook. Stronger
   options: OS isolation (container, Docker Sandboxes, the `sandbox/` example) or [3rd-party]
   `pi-permission-modes` (bash AST gating) — untested.
5. **Shipped examples worth reading** (Pi repo, `packages/coding-agent/examples/extensions/`):
   `permission-gate.ts`, `protected-paths.ts`, `confirm-destructive.ts`, `dirty-repo-guard.ts`,
   `plan-mode/`, `sandbox/`, `subagent/`, `claude-rules.ts`, `custom-compaction.ts`, `handoff.ts`.
