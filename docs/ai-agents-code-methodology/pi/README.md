# Pi surface pack

Copy-ready artifacts that implement the AI-agent methodology inside a project driven by **Pi**
(`pi`, package `@earendil-works/pi-coding-agent`, checked against **1.3.0** on 2026-10-17).

Parent guide: [`../PI_ADAPTATION.md`](../PI_ADAPTATION.md). Every Pi fact used here is traceable to
[`../../research/PI_FINDINGS_2026-10-17.md`](../../research/PI_FINDINGS_2026-10-17.md).

## What this folder contains

| Path | Goes to | Purpose |
|---|---|---|
| `AGENTS.md.example` | repo root `AGENTS.md` | Lean orientation: gates, tool order, pointers. Pi loads it from cwd and every parent. |
| `APPEND_SYSTEM.md.example` | `~/.pi/agent/APPEND_SYSTEM.md` (or `.pi/APPEND_SYSTEM.md`) | Optional always-on gates appended to Pi's system prompt. The trusted project file wins over the global one; they are **not** combined. Plain text — it is appended verbatim. |
| `mcp.json.example` | `.pi/mcp.json` (trusted projects only) or `~/.pi/agent/mcp.json` | CodeGraph + Serena with `toolExposure: direct` for the tools the method wants used unprompted; Playwright + Context7 `deferred`. |
| `settings.json.example` | `~/.pi/agent/settings.json` | Only documented keys. `defaultProjectTrust` and `cacheWarming` are **agent-directory only** — drop them if you use this as `.pi/settings.json`. |
| `extensions/block-external-git.ts` | `~/.pi/agent/extensions/` | **[TESTED on 1.3.0]** `tool_call` gate: blocks `git push`, `gh pr create/merge/…`, `gh release`, merges from `origin/`. |
| `skills/*/SKILL.md` | `~/.pi/agent/skills/` or `.pi/skills/` | `kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff`, `day`, `atlassian`, `evidence`. Invoke with `/skill:<name>`. |

## Install (from the target repo root, bash)

```bash
src=data/changes/ai-agent-methodology/pi

# Global (per machine): the git gate and the skills. Global extensions are NOT trust-gated,
# so a repo cannot switch the gate off.
mkdir -p ~/.pi/agent/extensions ~/.pi/agent/skills
cp "$src/extensions/block-external-git.ts" ~/.pi/agent/extensions/
cp -r "$src/skills/." ~/.pi/agent/skills/
[ -f ~/.pi/agent/settings.json ] || cp "$src/settings.json.example" ~/.pi/agent/settings.json

# Project: MCP + orientation. .pi/ resources load only after you /trust the folder.
mkdir -p .pi
sed "s|__REPO_ROOT__|$PWD|" "$src/mcp.json.example" > .pi/mcp.json
[ -f AGENTS.md ] || cp "$src/AGENTS.md.example" AGENTS.md
```

## Post-install checklist

1. `pi` in the repo → `/trust` (or answer the trust prompt). Without trust, `.pi/mcp.json`,
   `.pi/skills` and `.pi/extensions` are **skipped**. Print / JSON / RPC modes cannot prompt: pass
   `--approve` there.
2. `pi mcp list` → expect `codegraph: connected …`. No `${workspaceFolder}`-style variable is
   documented, hence the absolute path substituted above.
3. `codegraph init` in the repo; add `.codegraph/` to `.gitignore`.
4. Check the gate: ask Pi to run `git push` in a scratch repo — the tool result must read
   `Blocked by policy: external git/PR action …`.
5. If the repo already has a `CLAUDE.md` **and** you add `AGENTS.md`, Pi reads only `AGENTS.md` from that
   directory. Merge them, or keep one.
6. `/skill:kg <known ticket>` to smoke-test the ticket graph (if you have it).

## Keeping it lean

Pi has no scoped rules: everything in `AGENTS.md` is paid on every turn. Keep it a map plus gates;
history lives in `data/changes/` and is read on demand.
