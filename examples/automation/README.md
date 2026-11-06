# Automation in Pi — print, JSON, RPC, SDK (§07)

Four levels, lightest first. Pi has **no** built-in scheduler, automations product, official GitHub
Action or PR-review bot (NOT DOCUMENTED, 2026-10-17): you compose these from the modes below plus cron /
CI / `systemd`.

## 1. Extensions — deterministic control inside the session

See [`../extensions/`](../extensions/). That is where Pi's "hooks" live.

## 2. Print mode — `pi -p`

```bash
pi -p "summarise the changes on this branch"
git diff main... | pi -p "review this diff for security issues"   # piped stdin is prepended to the prompt
pi -p @src/app.py "explain this file"          # @path adds a file to the first prompt
```

In CI:

```bash
pi -p --no-session --approve --model anthropic/<id> "review the diff" </dev/null
```

**Gotchas:**

1. **[TESTED]** When stdin is a non-TTY that is never closed (CI runners, agent harnesses), `pi -p` waits
   for stdin EOF and appears to hang — because piped stdin is prepended to the first prompt. Add
   `</dev/null` when you are not piping anything. (A real pipe closes on its own — and `</dev/null`
   would replace it, so never combine the two.)
2. **Trust:** print/JSON/RPC cannot show the trust prompt. With the default `defaultProjectTrust: "ask"`,
   the repo's `.pi/` (MCP, extensions, skills) is **skipped silently** unless you pass `--approve`/`-a`.
   Global `~/.pi/agent/` resources still load.
3. Use an **environment key** (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, …), not `auth.json`, in CI.
4. Readiness gate: `pi auth check --provider X --json` exits 0, 1 or 2.
5. Deterministic runs: `PI_OFFLINE=1`, `PI_SKIP_VERSION_CHECK=1`, `PI_TELEMETRY=0`.
6. Print mode exits **non-zero** on `error`, `aborted` or `length`.

## 3. JSON events — `pi --mode json`

[`json-mode.sh`](./json-mode.sh). ⚠️ JSON mode does **not** exit non-zero when the run fails — inspect
the events. Split on LF only; text from `message_update` deltas; `message_end` is authoritative;
`agent_settled` ends automatic work.

## 4. RPC — `pi --mode rpc`

A long-lived process: JSONL commands on stdin (`prompt`, `steer`, `follow_up`, `abort`, `get_state`,
`get_commands`, `compact`, `fork`, `set_model`, `set_thinking_level`, `export_html`, …), responses and
events on stdout. From TypeScript prefer `RpcClient` with `promptAndWait()` — [`rpc.ts`](./rpc.ts)
(constructor/return shape marked VERIFY: not in the findings).

## 5. SDK — `createAgentSession()`

[`sdk.ts`](./sdk.ts):

```bash
cd examples/automation && npm i && npx tsx sdk.ts
```

`session.prompt()`, `subscribe()`, `steer()`, `followUp()`, `abort()`, `waitForIdle()`,
`getLastAssistantText()`, `dispose()`. ⚠️ SDK sessions **do not load built-in MCP or codemode** — add
the factories explicitly (comment in `sdk.ts`).

## 6. CI — [`github-action-pi.yml`](./github-action-pi.yml)

**A pattern, not an official action, and not run in CI.** Read-only agent job (pinned
`@earendil-works/pi-coding-agent@1.5.0`, `--tools read,grep,find,ls`, `--approve`, `</dev/null`) that
uploads `review.md` as an artifact; a second job behind a GitHub environment with required reviewers
posts it. The human owns the external action — same policy as the methodology.

## 7. Scheduled tasks

| Claude Code | Cursor | Pi |
|---|---|---|
| Routines `/schedule`, `/loop` | Automations | **None built in** — cron / CI / `systemd` running `pi -p … </dev/null` |

## Map from the other volumes

| Need | Claude Code | Cursor | Pi |
|---|---|---|---|
| One-shot CLI | `claude -p` | `agent -p --trust` | `pi -p` (`</dev/null`, `--approve`) |
| Event stream | `--output-format stream-json` | `--output-format` | `--mode json` (exit code ≠ outcome) |
| Long-lived driver | — | — | `--mode rpc` / `RpcClient` |
| SDK | Claude Agent SDK | `@cursor/sdk` | `createAgentSession()` |
| PR bot | GitHub Action | Bugbot | your own workflow (pattern above) |
