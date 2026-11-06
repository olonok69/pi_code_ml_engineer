# pi_code_ml_engineer — course / workshop repo

Lean always-on memory for Pi. Detail lives in the guides and `examples/`.

## What this repo is

Material for the **Pi** volume of the course (3 parts): guides, PPTX, and runnable examples under
`examples/`. Not an application codebase — it demos the Pi surface (skills, extensions, MCP, modes).

## Demo surface (this folder's `.pi/`)

⚠️ Project resources under `.pi/` load **only after you trust this folder** (`/trust`; the default
`defaultProjectTrust` is `"ask"`). Print, JSON and RPC modes cannot show the trust prompt: they skip
`.pi/` silently unless you pass `--approve` (`-a`). This `AGENTS.md` loads regardless of trust.

| Piece | Path | How to try |
|---|---|---|
| Skills | `.pi/skills/audit`, `audit-python`, `deploy-staging` | `/skill:audit ex_npm` · `/skill:audit-python ex_app` · `/skill:deploy-staging ex_staging` |
| Extension (hook analogue) | `.pi/extensions/block-external-git.ts` | ask the agent to `git push` — the `tool_call` handler returns `{ block: true, reason }` |
| MCP | `.pi/mcp.json` — context7 + playwright, `exposure: "deferred"` | `pi mcp list` · `/mcp` |
| Subagents | not built in — see `examples/subagents/` | install the example extension first |

For the safety-critical git gate, prefer the **global** copy (`~/.pi/agent/extensions/`): global
extensions are not trust-gated and a repo cannot remove them.

Canonical teaching copies live under `examples/*` (keep them in sync if you edit `.pi/`).

## Rules for any agent working here

- Human owns every external action: no push, PR, merge, release or deploy unless explicitly asked.
- Pi claims must trace to `docs/research/PI_FINDINGS_2026-10-17.md` (1.3.0) or `docs/research/PI_UPDATE_2026-11-06.md`
  (1.5.0 delta); if it says NOT DOCUMENTED, say so.
- Sanitised content only: no client names, ticket IDs, account IDs, emails or secrets.

## Pointers

- Talk track: `SPEAKER_GUIDE.md` · copy-paste reference: `TECHNICAL_GUIDE.md`
- Live demos by slide: `DEMO_RUNBOOK.md`
- Methodology pack: `docs/ai-agents-code-methodology/` (`PI_ADAPTATION.md`, `pi/`)
