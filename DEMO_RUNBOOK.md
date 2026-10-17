# DEMO_RUNBOOK — Pi presentation (36 slides)

Runbook for the **presenter**. Commands are bash (macOS, Linux, WSL2). Pi facts checked against
**Pi 1.3.0 on 17 Oct 2026** — see [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md).
Speaker guide: [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) · Deck:
[`presentation/Pi_Presentation.pptx`](./presentation/) · Reference: [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md).

> ⚠️ Live demos that call a model need a provider key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, …) or a
> `/login`. The commands below were written from the documented behaviour; the ones marked **[TESTED]**
> were run during the research. Rehearse the rest on your machine before the session.

## Skills / extension / MCP — live in *this* repo

Pi loads **project** resources from `.pi/` **only after you trust the folder**:

- `.pi/skills/*/SKILL.md` — `audit`, `audit-python`, `deploy-staging`
- `.pi/extensions/block-external-git.ts` — the tested git gate
- `.pi/mcp.json` — `context7`, `playwright` (both `exposure: "deferred"`)
- `AGENTS.md` — loaded **regardless** of trust (context files ignore trust)

The teaching copies under `examples/**/.pi/` are **not** loaded until copied or passed with `--skill`.

**After `cd` into this repo and `pi` → `/trust`**, try:

| What | How |
|---|---|
| Skill **npm** | `/skill:audit ex_npm` (Express mini-app + `npm test`) |
| Skill **Python** | `/skill:audit-python ex_app` (Streamlit forecasting app + `pip-audit`) |
| Skill **staging** | `/skill:deploy-staging ex_staging` (tests → build → **asks OK** → local deploy → smoke) |
| Extension (git gate) | "run `git push`" → the tool result must read `Blocked by policy: external git/PR action …` |
| MCP | `/mcp` → context7 / playwright listed · `pi mcp list` from the shell |
| Context files | `/session` shows the session; AGENTS.md is in the prompt without asking |

### Skill targets (audit + deploy)

| Skill | Target | Stack | What it does |
|---|---|---|---|
| `/skill:audit` | [`ex_npm/`](./ex_npm/) | Node + Express | `npm audit` → safe fix → `npm test` |
| `/skill:audit-python` | [`ex_app/`](./ex_app/) | Python + Streamlit | `pip-audit -r requirements.txt` → smoke |
| `/skill:deploy-staging` | [`ex_staging/`](./ex_staging/) | Node (no Express) | `npm test` → `build` → **human confirmation** → `deploy:staging` → `GET /health` |

**Preflight for those targets (T1):**

```bash
cd ex_npm && npm install && npm test && npm audit; cd ..
cd ex_app && python3 -m pip install pip-audit && python3 -m pip_audit -r requirements.txt; cd ..
cd ex_staging && npm test && npm run build; cd ..
# optional dry-run (no skill): npm run deploy:staging ; curl the health URL ; npm run staging:stop
```

On `/skill:deploy-staging`, the agent **must stop** before `npm run deploy:staging` and wait for your OK.
Pi itself will **not** ask — the stop lives in the skill text. That is the point of slide 8.
"Staging" is a local server (writes `.staging-url`); there is no cloud.

**Better on a real product repo with a CodeGraph index:** CodeGraph, Serena, `/skill:kg`,
`/skill:methodology-plan` — this course repo is not a product app.

---

## Before you start (5 min)

**Suggested terminals**

| # | Open at | For |
|---|---|---|
| T1 | this repo | Part 1 demos + `kg` |
| T2 | a product repo with `.codegraph/` | Part 2 MCP / methodology |
| T3 | (optional) a second pane for tmux / parallel `pi` | slide 17 |

**Preflight**

| Check | OK if… |
|---|---|
| `pi --version` | `1.3.0` (or newer — then re-read the changelog) **[TESTED]** |
| `pi auth check --provider anthropic --json` | exit 0 |
| `pi -p --no-session "Reply: OK-PI" </dev/null` | prints `OK-PI` |
| `uv run --with anthropic --with python-dotenv python examples/prompt-caching/cache_demo.py` | 2nd call `cache_read > 0` |
| `bash docs/knowledge-graph/kg_query.sh find letter` | node list (no LLM, no network) |
| T2: `pi mcp list` | `codegraph: connected` **[TESTED shape]** |
| T2: `codegraph status` | index present |

**Not live demos (slide / explanation only)**

- `examples/gsd/` — GSD is Claude Code only
- `examples/automation/github-action-pi.yml` — a pattern, not an official action; open it, don't run it
- `/share` — uploads a transcript; never on a client repo
- Full `kg_refresh` — slow, and its extraction step needs subagents (slide 33)

---

## Part 1 — Pi (slides 1–19)

| Slide | Topic | Demo (command) | Artifact |
|---|---|---|---|
| 1–3 | Cover / agenda / divider | Deck only | — |
| 4 | Install + auth | T1: `pi --version` · show `~/.pi/agent/` (no `auth.json` on screen!) | — |
| 5 | Modes | `pi -p --no-session "Reply: OK-PI" </dev/null` · then **without** `</dev/null` from a pipe (`true \| pi -p …` is fine; an open pipe hangs — explain) · `pi --mode json "say hi" </dev/null \| head` | [`examples/automation/`](./examples/automation/) |
| 6 | Memory | Open [`examples/agents-md/`](./examples/agents-md/) · `AGENTS.md` + `AGENTS.override.md.example` · say: ancestors only, one file per dir | agents-md |
| 7 | SYSTEM / APPEND_SYSTEM | Open `examples/agents-md/APPEND_SYSTEM.md.example` | agents-md |
| 8 | Permissions | Open [`examples/permissions/`](./examples/permissions/) · `pi --tools read,grep,find,ls` → ask it to edit a file → it has no tool to do so | permissions |
| 9 | Sessions | In TUI: `/session` · `/tree` · `/fork` · `pi -r` picker · `ls ~/.pi/agent/sessions/` | — |
| 10–12 | Context + caching | `/compact focus on the open bug` · run `cache_demo.py` · show `showCacheMissNotices` in `examples/permissions/settings.json.example` | context, prompt-caching |
| 13 | MCP | `pi mcp list` · open [`examples/mcp/mcp.json.example`](./examples/mcp/mcp.json.example) · point at `toolExposure: direct` | mcp |
| 14 | Skills | Live: `/skill:audit ex_npm` · open `examples/skills-plugins/.pi/skills/day/SKILL.md` · `pi list` | skills-plugins |
| 15–17 | Subagents | Open `examples/subagents/agents/refactor-scout.md` + `agents.png` · run a read-only child: `pi -p --no-session --tools read,grep,find,ls "List the functions in ex_app/metrics_utils.py" </dev/null` | subagents |
| 18 | Extensions (hooks) | `/trust`, then ask Pi: "run `git push origin main`" → **Blocked by policy** · then "run `git status`" → runs | extensions |
| 19 | Automation | Open `examples/automation/github-action-pi.yml` (pattern) · `bash examples/automation/json-mode.sh "say hi"` | automation |

**Gate demo without the TUI (print mode needs `--approve` for the project extension):**

```bash
pi -p --no-session --approve "Run exactly this shell command: git push origin main" </dev/null
# expected: the model reports the tool was blocked ("Blocked by policy: external git/PR action ...")
pi -p --no-session --no-approve "Run exactly this shell command: git push origin main" </dev/null
# project extension skipped -> the push is attempted. Do this ONLY in a scratch repo with no remote.
```

The second line is the **control run** — the same "canary the instrument" idea as Part 2. In the
research, the control run is what proved the gate (not the environment) stopped the push.

---

## Part 2 — Methodology (slides 20–30)

**Workspace:** T2 — a product repo with CodeGraph indexed and `.pi/mcp.json` from
[`docs/ai-agents-code-methodology/pi/mcp.json.example`](./docs/ai-agents-code-methodology/pi/mcp.json.example).

| Slide | Topic | Demo | Artifact |
|---|---|---|---|
| 20 | Part 2 divider | Deck only | — |
| 21–23 | Principle, 11-stage flow, outbound gate | Open `examples/methodology/flow.png` · `WORKFLOW.md` · 2 min of `REAL_EXAMPLE.md` | methodology |
| 24 | Tool prevalence | Open `examples/methodology/tools.md` · the trigger map in `docs/ai-agents-code-methodology/pi/AGENTS.md.example` | methodology |
| 25 | CodeGraph | T2: `pi mcp list` (show `codemode` vs `direct`) · ask "who calls `<symbol>`?" and watch `codegraph_explore` fire | codegraph |
| 26 | Serena | Ask for `find_referencing_symbols` before a rename (untested under Pi — rehearse) | serena |
| 27 | GSD | **Slide only** — Claude Code only; plan file + prompt templates in Pi | gsd |
| 28 | Oracles / Playwright / Context7 | Playwright (deferred) navigate + snapshot, if rehearsed | mcp |
| 29 | Transfer Claude Code → Pi | Open `docs/ai-agents-code-methodology/PI_ADAPTATION.md` §2 · the `pi/` folder | pack |
| 30 | Machine sync + S3 | Open `examples/methodology/machine-sync.md` · `docs/synchro/s3-sync/README.md` (1 screen) | synchro |

**If MCP is not connected:** `pi mcp list --json` (exit 1 = failure) · check `~/.pi/agent/mcp.log` ·
is the folder trusted (project `.pi/mcp.json` is skipped otherwise)? · absolute `--path` for CodeGraph.

---

## Part 3 — Ticket graph (slides 31–36)

**Workspace:** T1 (the course graph lives here, pseudonymised).

| Slide | Topic | Demo | Artifact |
|---|---|---|---|
| 31 | Part 3 divider | Deck only | — |
| 32 | KG idea | Open [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) (1 min) | docs |
| 33 | Pipeline + skills in Pi | Show `docs/knowledge-graph/` · open `docs/ai-agents-code-methodology/pi/skills/kg-refresh/SKILL.md` (the Pi caveat) — **do not** run refresh live | knowledge-graph |
| 34 | Real output | Open `docs/knowledge-graph/output/graph.html` · or the slide with `presentation/kg_graph.png` | graph.html |
| 35 | Hook-in | T1: `bash docs/knowledge-graph/kg_query.sh find letter` · then `bash docs/knowledge-graph/kg_query.sh TKT-104` (needs `graphify` importable for `explain`) | kg_query.sh |
| 36 | Close | Recap: tool (Pi) + method (11 stages) + memory (graph) | — |

```bash
bash docs/knowledge-graph/kg_query.sh find letter      # pure python, always works
bash docs/knowledge-graph/kg_query.sh TKT-104          # graphify explain
xdg-open docs/knowledge-graph/output/graph.html        # or: explorer.exe / open
```

---

## Suggested timed order (~90–120 min)

| Block | Slides | Time | Must-run demos |
|---|---|---|---|
| Part 1 | 1–19 | 40–50 min | `pi -p … </dev/null`, cache_demo, git gate blocked + control, `/skill:audit` |
| Part 2 | 20–30 | 30–40 min | flow.png + `pi mcp list` (codemode vs direct) + transfer pack |
| Part 3 | 31–36 | 15–20 min | `kg_query` + graph.html |
| Q&A buffer | — | 10 min | — |

**If short on time:** cut sessions to `/tree` only, machine sync to 1 sentence, GSD to 30 s, skip RPC/SDK
(keep `pi -p`).

**If time left:** on T2 run `/skill:kg <topic>` and `/skill:methodology-plan` end to end.

---

## Common-failure cheat sheet

| Symptom | Quick fix |
|---|---|
| `pi -p` hangs | stdin is an open pipe → add `</dev/null` **[TESTED]** |
| Project skills / MCP / extension missing in `-p` | trust prompt cannot show → add `--approve` |
| Project skills missing in the TUI | `/trust` the folder |
| `/audit` does nothing | Pi skills are `/skill:audit` (or add a prompt template) |
| MCP tool "not available" to the model | default exposure is `codemode` → `toolExposure: direct` |
| JSON-mode script says success on a failed run | JSON mode does not exit non-zero — inspect events |
| SDK session has no MCP tools | add `createMcpExtension()` etc. via `DefaultResourceLoader` |
| `AGENTS.md` and `CLAUDE.md` both present, CLAUDE rules ignored | one file per directory; `AGENTS.md` wins — merge |
| cache_demo fails | `uv run --with anthropic --with python-dotenv …` + key in `.env` |
| Tutorials say "Pi has no MCP" | out of date since 0.99.0 (2026-09-29) |

---

## Example → course-section map

| Folder | Part | Live? |
|---|---|---|
| `examples/agents-md/` | §02 | Yes (open) |
| `examples/permissions/` | §02 | Yes (open + `--tools`) |
| `examples/context/` | §03 | Yes (open + `/compact`) |
| `examples/prompt-caching/` | §03 | Yes (run) |
| `examples/mcp/` | §04 | Yes (open + `pi mcp list`) |
| `examples/skills-plugins/` | §05 | Yes (open + `/skill:audit`) |
| `ex_npm/` · `ex_app/` · `ex_staging/` | §05 | Yes (live `.pi/skills/`) |
| `examples/subagents/` | §06 | Yes (open + read-only `pi -p`) |
| `examples/extensions/` | §07 | Yes (git gate + control run) |
| `examples/automation/` | §07 | Partly (`pi -p`, JSON mode; Action = pattern) |
| `examples/codegraph/` · `serena/` | §09 | Yes on a product repo |
| `examples/gsd/` | §09 | No (explain) |
| `examples/methodology/` | §08/§11 | Yes (MD + PNG) |
| `docs/knowledge-graph/` | §12 | Yes (query + HTML) |
