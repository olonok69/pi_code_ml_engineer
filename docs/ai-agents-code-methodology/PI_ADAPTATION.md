# Adapting the AI-agent methodology for Pi

> Purpose: take the methodology from [`README.md`](README.md) / [`TECHNICAL.md`](TECHNICAL.md)
> and run it end-to-end in **Pi** (`pi`, `@earendil-works/pi-coding-agent`), with the same tool *roles*
> you use in Claude Code (CodeGraph, Serena, Playwright, graphify/`kg`, deterministic oracles).
>
> Companion pack (copy-ready AGENTS.md, MCP, extension, settings, skills): [`pi/`](pi/).
> Sibling guides: [`CURSOR_ADAPTATION.md`](CURSOR_ADAPTATION.md), [`COPILOT_ADAPTATION.md`](COPILOT_ADAPTATION.md).
>
> **Verified 2026-10-17 against Pi 1.3.0; delta to 1.5.0 re-checked 2026-11-06
> ([`../research/PI_UPDATE_2026-11-06.md`](../research/PI_UPDATE_2026-11-06.md)).** Every Pi fact here comes from
> [`../research/PI_FINDINGS_2026-10-17.md`](../research/PI_FINDINGS_2026-10-17.md); markers:
> **[TESTED]** (run locally), **[3rd-party]** (community package, untested), **NOT DOCUMENTED**.
> Pi moves fast — re-check before reuse.

---

## 0) The one thing to understand first

Pi is a **minimal harness by design**. Its homepage lists what it deliberately did *not* build:
no permission popups, no sub-agents, no plan mode (and, until 0.99.0, no MCP — that one changed).
Claude Code and Cursor give you those as product features; Pi gives you a **TypeScript extension API**
and expects you to build, install or skip them.

So the porting question is never "where is the Pi setting for X?". It is: **"which part of X was
discipline, and which part was mechanism?"** The discipline travels unchanged. The mechanism is
re-implemented with Pi's levers — AGENTS.md, skills, prompt templates, MCP exposure, extensions,
containers — or consciously dropped.

---

## 1) What transfers unchanged

1. Plan -> agree -> implement.
2. Verify via the consumer-visible output contract, not internal functions.
3. Solve the general class of issue, not one sample input.
4. Keep a durable decision trail (why, what changed, how verified).
5. Human owns irreversible external actions (merge, deploy, stakeholder comms).
6. **Canary the instrument before believing it** — a filter/lock/scan that returns "nothing" or "ok"
   without a known-answer check is not evidence.
7. **Read the machine/session role before writing shared state** — point `AGENTS.md` at a
   machine-local `IDENTITY.md`.

If you keep only five rules, keep **1–5**. Add **6–7** as soon as you share a durable trail.

---

## 2) Claude Code → Pi surface map

| Role in the methodology | Claude Code | Pi (1.3.0) |
|---|---|---|
| Always-loaded orientation | `CLAUDE.md` (+ nested, `@imports`) + `~/.claude/CLAUDE.md` | `AGENTS.md` (or `CLAUDE.md`) in **cwd and every ancestor** + `~/.pi/agent/AGENTS.md`. **One file per directory** (`AGENTS.override.md` > `AGENTS.md` > `AGENTS.MD` > `CLAUDE.md` > `CLAUDE.MD`). No sub-directory loading, no `@imports` (NOT DOCUMENTED). Pi does **not** read `~/.claude/CLAUDE.md`. |
| Always-on gates outside AGENTS.md | `--append-system-prompt` | `APPEND_SYSTEM.md` (`~/.pi/agent/` or `.pi/`) or `--append-system-prompt`; `SYSTEM.md` *replaces* the default prompt |
| Scoped rules | `.claude/rules/` (paths) | **None native.** Skill whose description names the paths · `claude-rules.ts` example extension · `APPEND_SYSTEM.md` · a `before_agent_start` extension |
| On-demand detail | `data/changes/**` | Same path — unchanged |
| Tool prevalence (auto-select) | Rules in `CLAUDE.md` + MCP allowlist | Trigger map in `AGENTS.md` + MCP **`toolExposure: direct`** for `codegraph_explore` and Serena's lookups (default exposure is `codemode`, invisible as a declared tool) |
| Skills (`kg`, `day`, …) | `~/.claude/skills/` → `/kg` | `~/.pi/agent/skills/`, `.pi/skills/`, `~/.agents/skills/`, `.agents/skills/`, or the `"skills"` setting → **`/skill:kg`** |
| Slash commands | `.claude/commands/*.md` | Prompt templates `~/.pi/agent/prompts/*.md` / `.pi/prompts/*.md` → `/<name>` |
| Hard gates (block push, …) | Hooks (`exit 2`) + `settings.local.json` allowlist | **Extension**: `pi.on("tool_call", …)` → `{ block: true, reason }` — [`pi/extensions/block-external-git.ts`](pi/extensions/block-external-git.ts) **[TESTED]** |
| Permission prompts / allowlist | Built in | **None by design.** Containers (Docker, Docker Sandboxes, OpenShell, Gondolin), `--tools` / `defaultTools`, MCP `exposure: hidden`, project trust, extensions (`permission-gate.ts`, `protected-paths.ts` examples; the `sandbox/` example was removed in 1.5.0) |
| Plan gate | Plan mode | **None built in.** The plan is a file the human agrees to; optional `plan-mode/` example extension or `--tools read,grep,find,ls` |
| Parallel / isolated exploration | Subagents / Agent Teams | **None built in.** `examples/extensions/subagent/` (agent files in `~/.pi/agent/agents/`), [3rd-party] `pi-subagents`, tmux, or `pi -p --tools read,grep,find,ls --no-session` child processes. No Agent Teams. |
| Persistent memory | auto-memory + claude-mem | **None built in.** Write-once ledgers + `pi -c` / `/resume` + greppable session JSONL. [3rd-party] `pi-memory` & co. |
| Headless / CI | `claude -p` | `pi -p … </dev/null`, `--mode json`, `--mode rpc`, SDK `createAgentSession()` |
| GSD | Supported | **Not supported** officially; [3rd-party] unofficial `pi-gsd`. Stance: GSD stays Claude-Code-only. |
| External git/PR | Hook + allowlist | Global `block-external-git.ts` (a repo cannot remove a global extension) |

Tools are fungible; discipline is not. CodeGraph / Serena / Playwright / graphify fill the same roles —
they speak MCP in Pi too (built in since 0.99.0; same `mcpServers` shape as Claude Code and Cursor;
tool names `mcp__<server>__<tool>`, as in Claude Code).

---

## 3) The 11 stages in Pi

| # | Stage | Pi practice | Preferred tools |
|---|---|---|---|
| 1 | Orient | Session start: AGENTS.md loads → read `IDENTITY.md`, `STATUS.md` → `/skill:kg` → `git`/`gh` live state | Skill `kg` · ledgers · `bash` |
| 2 | Inbound triage | Reproduce symptom at the **output contract** before any edit | Playwright MCP (`deferred`) · contract fixture |
| 3 | Provenance | Repro on pre-change baseline; regression vs pre-existing | `bash` + git · same harness |
| 4 | Investigate | Cheap deterministic oracle before expensive model diagnosis | `codegraph_explore` (direct) → Serena → `_diag_*.py` |
| 5 | Plan | `/skill:methodology-plan` → write the plan to `data/changes/<id>/` → **stop for agreement**. Optional: run read-only (`--tools read,grep,find,ls`) | Plan file · human |
| 6 | Implement | TDD RED → GREEN; minimal diff | `edit` / `write` · test runner |
| 7 | Verify | Unit + scoped + full suite; outbound gate ×5 | Tests · Playwright · Docker |
| 8 | Document | Write-once: issue note, STATUS pointer, QA, handover | Templates under `data/changes/` |
| 9 | Sanitise | Scan **added** staged lines | `/skill:sanitise-diff` |
| 10 | Hand off | Prepare branch + handover; **do not** push/PR/deploy | `block-external-git.ts` (global) + AGENTS.md gate |
| 11 | Review + persist | Triage bot findings; update ledgers; refresh ticket graph | `gh` (read) · `/skill:kg-refresh` (see §8 caveat) |

Cost concentration is unchanged: cheap fact-finding in 1–4 and 9; expensive inference in 5–7.
Use `/tree` or `/fork` for side quests so the main branch of the session stays lean.

---

## 4) Tool prevalence (same order as Claude Code)

Encode this in `AGENTS.md` — it is the only always-loaded place Pi has:

> For "what is this / who depends / what breaks", call **CodeGraph `codegraph_explore` first**
> (treat returned source as already read). Use **Serena `find_referencing_symbols`** before
> rename/delete. Use grep/read only for literals. For history-first orientation, run `/skill:kg`
> before grepping `data/changes/`.

⚠️ **The Pi-specific trap.** MCP tools default to `exposure: "codemode"`: callable only from a
`codemode` JavaScript script, **not declared as tools**. **[TESTED]** `pi mcp list` printed
`codegraph: connected, 1 tool (codemode, global)`. The model then has to discover the tool through
codemode or `tool_search`, which defeats "reach for it unprompted". Set `toolExposure` to `direct`
for exactly the tools the trigger map names (see [`pi/mcp.json.example`](pi/mcp.json.example)), and
leave the rest `deferred` or `codemode` to keep the prompt small.

| Need | Tool | Stage |
|---|---|---|
| Related prior tickets / danger zone | `/skill:kg` → graphify index (or STATUS fallback) | 1 |
| Symbol + callers + blast radius + test coverage | `codegraph_explore` (`direct`) | 4 |
| Precise refs before rename/delete | Serena `find_referencing_symbols` (`direct`) | 4–6 |
| Consumer-visible contract | Playwright MCP (`deferred`) | 2, 7 |
| Deployed runtime parity | Docker (same image as prod) | 7 |
| Root cause without LLM diagnosis | `_diag_*.py` / parser / schema check | 4 |
| Live library docs | Context7 MCP (`deferred`) | 4 |
| Branch / PR state | `git`, `gh` (read) | 1, 10–11 |

### No-knowledge-graph fallback

1. `data/changes/STATUS.md` newest-first + per-issue folders.
2. Lexical search by symptom / contract fields / symbols.
3. Commit/PR history by file overlap.
4. Short `SHARP_EDGES.md` danger-zone list.

That recovers ~80% of graph value with minimal setup.

---

## 5) Fast path — install the Pi pack (30–60 minutes)

From a target repository root, after copying this methodology folder to
`data/changes/ai-agent-methodology` (bash; macOS, Linux, WSL):

```bash
# 1) Ledger templates (shared with the other agents' paths) — PowerShell script, see TRANSFER_AND_BOOTSTRAP.md
#    or copy templates/STATUS_TEMPLATE.md etc. into data/changes/ by hand.

# 2) Pi surface — see pi/README.md for the full block
src=data/changes/ai-agent-methodology/pi
mkdir -p ~/.pi/agent/extensions ~/.pi/agent/skills .pi
cp "$src/extensions/block-external-git.ts" ~/.pi/agent/extensions/
cp -r "$src/skills/." ~/.pi/agent/skills/
sed "s|__REPO_ROOT__|$PWD|" "$src/mcp.json.example" > .pi/mcp.json
[ -f AGENTS.md ] || cp "$src/AGENTS.md.example" AGENTS.md
```

Then:

1. `pi` → `/trust` this folder (project `.pi/` resources are skipped until you do).
2. `pi mcp list` — CodeGraph must say `connected`.
3. `codegraph init`; add `.codegraph/` to `.gitignore`.
4. Fill `data/changes/STATUS.md` + 3–5 `SHARP_EDGES.md` entries + the output contract paragraph in `AGENTS.md`.
5. Prove the gate: ask Pi to `git push` in a scratch repo → the tool result must be `Blocked by policy …`.
6. Run **one** issue fully: plan file → agreement → RED → GREEN → contract outbound → sanitise → human push.

---

## 6) MCP setup notes (Pi-specific)

1. **Files:** `~/.pi/agent/mcp.json` (user) and `.pi/mcp.json` (project, **trusted projects only**).
   A project entry with the same name replaces the user entry; an entry with no `command`/`url`/`type`
   only overrides `enabled`, `exposure`, `toolExposure`.
2. **CLI:** `pi mcp add <name> [--env K=V] [--description …] [--exposure …] -- <cmd> [args]`,
   `pi mcp add <name> --url <u> …`, `pi mcp list [--json]`, `pi mcp login|logout`, `pi mcp remove`;
   `/mcp` in the TUI. (The `--help` synopsis lists only `list|login|logout`; `add`/`remove` exist — **[TESTED]**.)
3. **Transports:** stdio and streamable HTTP. **SSE is rejected.**
4. **CodeGraph** — `codegraph serve --path <repo> --mcp` **[TESTED]**. No `${workspaceFolder}`-style
   variable is documented: use an absolute path in `.pi/mcp.json`.
5. **Serena / Playwright / Context7** — same args as the Cursor guide; **not tested under Pi**.
   [3rd-party] `@bacnh85/pi-serena`, `@henryqw/pi-codegraph`, `@vndv/pi-codegraph` expose them as native Pi tools.
6. **Secrets** — `${VAR}` and `!command` expansion in values; never hardcode tokens. OAuth tokens land in
   `~/.pi/agent/mcp-auth.json` (machine-local secret).
7. **Gates still apply:** every MCP call, including calls from codemode scripts, passes through the
   `tool_call` / `tool_result` extension handlers.

---

## 7) Context architecture in Pi

| Layer | What lives there | Pi artifact |
|---|---|---|
| Always-loaded (small) | Pointers, locked decisions, gates, tool order | `AGENTS.md` (cwd + ancestors) + `~/.pi/agent/AGENTS.md` + optional `APPEND_SYSTEM.md` |
| Live snapshot | In-flight work index | `data/changes/STATUS.md` |
| On-demand | Per-ticket writeups, playbooks, full policy | `data/changes/<id>/`, `PLAYBOOK.md`, … |
| Skills (name + description only until used) | `kg`, sanitise, plan checklist, `day` | `~/.pi/agent/skills/*/SKILL.md` |
| MCP summaries | One line per server in `mcp_servers` | `codemode` / `deferred` exposure for everything not in the trigger map |

**Two Pi-specific anti-patterns:**

- **Ancestor leakage.** Pi loads `AGENTS.md`/`CLAUDE.md` from **every parent directory**. A workspace-level
  `CLAUDE.md` above your repo is paid for in every session started inside it. Audit the chain once.
- **Skill flooding.** `"skills": ["~/.claude/skills"]` works **[TESTED]** but pours *every* skill description
  (dozens) into the system prompt. List the directories you want, one by one.

---

## 8) Skills: what ports and how

| Skill | Ports? | Notes |
|---|---|---|
| `kg` | **Unchanged** | Deterministic scripts; `/skill:kg <ticket|topic>`. |
| `kg-refresh` | **Partly** | The `prepare` / `finalize` / `queue` / `request` bookends are scripts and run in Pi. The **semantic-extraction step** of `/graphify` dispatches general-purpose subagents, which Pi lacks → install the `subagent` example extension or [3rd-party] `pi-subagents` and adapt (**UNVERIFIED**), **or run that one step from Claude Code**. |
| `day` | **Unchanged** | `/skill:day start` (not `/day`). Optional prompt template `~/.pi/agent/prompts/day.md` ("Run the day skill: $@") keeps `/day` muscle memory — an inference, not documented. |
| `atlassian` | **Unchanged** | bash + `atl.py`; GET-only enforced by the tool. |
| `evidence` | **Unchanged** | Read-only rests on the IAM role + skill text (no allowlist in Pi). |
| `preview` | **Unchanged** | Local shell + Docker; `/skill:preview --doc <id>`. Nothing gates a second concurrent run or the LLM spend in Pi: one document at a time, always `--stop`. |
| `methodology-plan` | **Unchanged** | The plan gate becomes "plan file + human agreement". |
| `sanitise-diff` | **Unchanged** | `git diff --cached` + scan. |

Frontmatter: Pi implements the Agent Skills spec (`name`, `description`, `license`, `compatibility`,
`metadata`, `allowed-tools` (experimental), `disable-model-invocation`). **Unknown keys are ignored
silently** **[TESTED]** — a Claude-only `trigger:` key does no harm, but also does nothing. On a name
collision the **first** skill found wins, with a warning.

---

## 9) Planning template (issue start)

Same template as the Cursor and Copilot adaptations — keep one voice. It lives in
[`pi/skills/methodology-plan/SKILL.md`](pi/skills/methodology-plan/SKILL.md). Fill it after stages 1–4,
save it under `data/changes/<id>/`, stop for agreement.

---

## 10) Governance policy (minimum)

1. No merge/deploy/customer comms by the agent unless the human explicitly requests it in-session.
2. No secrets or forbidden identifiers in committed artifacts.
3. No "fixed" claim without command-level evidence.
4. No silent dismissal of automated-review findings.
5. No prompt/extension/MCP changes that weaken gates without explicit acknowledgement.
6. Sanitise **added** staged lines before handoff every time.
7. **Pi-specific:** unattended runs (CI, long autonomous sessions) go in a **container** that mounts only
   the workspace — never the host `~/.pi/agent/` (it holds `auth.json`). Pi's own security page lists
   "lack of a built-in sandbox" and prompt injection as out of scope.

---

## 11) Folder structure (target repo)

```text
~/.pi/agent/                 # per machine — NOT in the repo
  AGENTS.md                  # global orientation (Pi's ~/.claude/CLAUDE.md)
  settings.json
  extensions/block-external-git.ts
  skills/{kg,kg-refresh,methodology-plan,sanitise-diff,day,atlassian,evidence,preview}/SKILL.md
  auth.json  mcp-auth.json  trust.json   # machine-local secrets/state — never synced
.pi/
  mcp.json                   # project MCP (trusted projects only)
data/
  changes/
    STATUS.md  FOLLOWUPS.md  SHARP_EDGES.md
    ai-agent-methodology/    # this pack
    <issue-id>/<issue-id>.md  _handover.md  qa_acceptance_criteria.md
AGENTS.md                    # lean pointer file (one per directory — merge with CLAUDE.md if both exist)
```

---

## 12) 14-day rollout (Pi)

**Days 1–2: Baseline.** Install the pack; trust the repo; wire MCP with `toolExposure: direct`;
define contract + 3–5 sharp edges; agree the working agreement; decide the container story for unattended runs.

**Days 3–5: First controlled ticket.** Full 11-stage run; plan file + agreement; RED → GREEN;
outbound contract; prove sanitise + human-owned push (and watch the git gate fire once).

**Days 6–10: Stabilise.** Add `kg` or harden the STATUS fallback; decide the `kg-refresh` extraction
path (subagent extension vs Claude Code); add content gates you find you need (e.g. `aws s3 rm`).

**Days 11–14: Harden.** Port remaining skills; move CI review to `pi -p … </dev/null` in a
container; publish a one-page "how we run Pi here".

---

## 13) Honest gaps vs Claude Code

| Capability | Status in the Pi pack |
|---|---|
| 11 gates + durable trail | Full parity (discipline, files) |
| CodeGraph / Serena / Playwright roles | Parity via MCP — needs `toolExposure: direct`; only CodeGraph **[TESTED]** |
| Plan → agree → implement | Parity as discipline; no plan-mode mechanism unless you add the example extension |
| Block external git | Parity (**[TESTED]** extension); regex gates can be bypassed (`sh -c`, aliases) — same caveat as hooks |
| Permission prompts / allowlist | **Gap by design** → containers + `--tools` + extensions |
| Ticket graph query | Full parity (`kg`) |
| Ticket graph refresh | Partial: extraction step needs subagents → extension or Claude Code |
| Subagents / Agent Teams | Example extension / [3rd-party] / tmux; no teams |
| GSD | Not supported (unofficial [3rd-party] `pi-gsd`, untested) |
| Cross-session memory | Ledgers + sessions; no auto-memory |
| CI review bot | None official; `pi -p` in your own workflow (pattern, untested) |

Aim for **methodology parity**, not product-clone parity.

---

## 14) Direct answer

Yes — the methodology runs in Pi, and Pi is a useful stress test of it: almost every guard rail that
Claude Code and Cursor ship as a feature is, in Pi, something you write down or build. What survives
that test is the method; what doesn't was a product convenience.

1. AGENTS.md + skills + MCP (`direct`) + one global extension cover the daily loop.
2. The knowledge graph query ports unchanged; its refresh needs subagents.
3. Safety is your job: container for unattended runs, extension for content gates.
4. The invariant gates stay the real source of quality.

Start with [`pi/README.md`](pi/README.md).
