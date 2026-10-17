# Ticket knowledge graph — "CodeGraph, but for tickets and lessons"

> A real (sanitised) pattern built on a live project. The idea: just as **CodeGraph** indexes the
> *code*, this skill indexes the **project's memory** — per-ticket writeups, "sharp edges", runbooks and
> memory notes — into a **navigable graph** the agent queries *before* touching anything. It is invoked
> with the **`kg`** skill (`/skill:kg` in Pi) and rebuilt with **`kg-refresh`**. Everything lives under
> `data/` (gitignored): the nodes carry internal names, so it **never leaves the repo**. (The copy shipped
> in this course was pseudonymised: ticket keys became `TKT-1xx`, client names `ClientX`.)

It complements CodeGraph, it does not replace it: **CodeGraph = the *what/how* of the code** (symbols,
calls, blast radius); **this graph = the *why* and the *what broke before*** (which tickets touch each
other, which danger zone surrounds an area, how one ticket connects to another).

---

## 1. The problem it solves

In a repo with hundreds of per-ticket writeups (`data/changes/<ticket>/`), a "new" bug almost always has
**prior context that constrains the fix**: an invariant you must not break, a ticket that already fixed
something similar, a documented regression. Finding it by hand = remembering it exists and grepping. The
graph **makes it explicit**: one query returns the related tickets + the danger-zone cluster.

Real example: for a "letter end" fix, `kg get_letter_end` instantly returns the full danger zone (the 5–6
tickets that share that code) — exactly what you would otherwise have to *remember* in order not to regress.

## 2. The corpus (what goes into the graph)

A **reproducible, diffable manifest** (`manifest.txt`) lists exactly which files go in, instead of a glob
that changes silently. Membership rules:

| Group | Rule |
|---|---|
| Primary per ticket | `data/changes/<ticket>/<ticket>.md` |
| Per-ticket fallback | for folders without `<ticket>.md`, the largest `.md` (deterministic) |
| Extractor state | `data/changes/extractors/*/process.md` |
| Hubs | `STATUS.md`, `SHARP_EDGES.md`, `FOLLOWUPS.md`, `PLAYBOOK.md`, … |
| Orientation | `CLAUDE.md` / `AGENTS.md`, `CODE_NAVIGATION.md` |
| Ops | the `machine-sync` runbooks + the `s3-sync` shared record |
| Memory | the agent's memory notes (`~/.claude/…/memory/*.md` in the original install) |

Hard exclusions: binaries (`.png`/`.json`/`.docx`), stale copies from a travel tarball (`payload/`),
handovers that only repeat the ticket. **Density without new knowledge = noise.**

## 3. The build pipeline (`kg-refresh`)

A deterministic wrapper around one semantic-extraction pass with subagents:

```
kg_refresh.sh prepare   # build_manifest -> stage _corpus/ -> copy to a scratch dir outside the repo
graphify <scratch>      # detect -> extraction by (general-purpose) subagents -> clustering -> HTML/JSON
kg_refresh.sh finalize  # copy artifacts to output/ + sync the in-place copy + leak-check
```

- **The gotcha that holds it together:** `graphify` honours `.gitignore`, and **all of `data/` is
  gitignored** → running the detector *in place* finds **0 files**. Fix: stage the corpus in a **scratch
  directory outside the repo** (`~/.cache/…`), run there, copy the 3 artifacts back to
  `data/knowledge-graph/output/`.
- **Full rebuild** every time; ~5 `general-purpose` subagents in parallel (that is why `kg-refresh` is a
  skill and not a script: the semantic step is an agent step).
- ⚠️ **In Pi** there are no built-in subagents: the bookends run unchanged, but the extraction step needs the
  `subagent` example extension / a [3rd-party] package (UNVERIFIED with graphify), or is run from Claude Code.
- **Leak-check** in `finalize`: aborts if any graph artifact landed outside `data/`.

Output: `output/graph.json` (NetworkX node-link, **typed edges** with `relation` + `confidence`),
`output/graph.html` (interactive), `output/GRAPH_REPORT.md` (god-nodes, surprising connections, questions).

## 4. The query surface (`kg`) — deterministic, no LLM

The engine already exists in `graphify`: `explain` (neighbours) and `path` (shortest path) read
`graph.json` **directly, with no LLM** — that *is* the CodeGraph analogue. The `kg` skill is a thin wrapper
(`kg_query.sh`) that pins the interpreter + the graph path and normalises the token:

```bash
kg <ticket-or-topic>   # a node's neighbours    (graphify explain)  <- the most common use
kg <A> <B>             # shortest path A<->B    (graphify path)
kg find <substr>       # discover a node's exact name
```

Tokens match fuzzily: `TKT-100`, `tkt-100`, `get_letter_end`, `"letter end"` all resolve. If a topic
does not resolve, `find <substr>` gives the exact id to retry with.

> **"No LLM" is not "free" — it is a smaller, amortised cost.** The expensive inference (extraction with
> subagents) is paid **once** in `kg-refresh`; each `explain`/`path`/`find` query is then a deterministic
> algorithm reading `graph.json` → **zero inference**. The only per-query cost is the agent reading a small
> output (like a `grep`): smaller and targeted, not zero. Seen that way, building the graph is an
> **investment** — no inference per query, **deterministic and reproducible** answers, and expensive
> reasoning replaced by a cheap lookup → better results and time/money saved per task.

## 5. Hooked into the workflow (the real goal)

A graph nobody queries is worth nothing. The **history-first** rule in the orientation file now says:
**before designing a fix near a known area, run `kg <ticket-or-topic>`** — *before* grepping
`data/changes/`. One deterministic call puts the reading list in front of you (related tickets + danger
zone); then you read the ticket writeup and the "sharp edges" entry before writing. The graph points at
*what to read*; it does not replace reading it.

Honesty about what it adds: the gain is **recall in dense zones** (letter end, title clean-up, subsection
numbering) — there it saves greps and catches the 1 relevant ticket you would have missed. In an isolated
area it adds little. `EXTRACTED` edges = reliable; `INFERRED` / `semantically_similar_to` = leads to
verify, not facts.

## 6. Travelling between machines (main ⇄ laptop)

The graph is an **almost** derived artifact → **the built graph does not travel back**: whichever machine
holds the current corpus rebuilds it. ⚠️ **With one exception that is NOT negotiable:**
`community_labels.json` (the community names, written by hand) **is not a pure function of the corpus** —
nothing regenerates it, and in a real rebuild **under 1%** survived. If it was edited on the other machine,
**it has to travel back**, paired with the graph it was written against. "Derived" is a property of the
file, not of the folder. Two subcommands close the loop (memory does not travel in the delta by default):

```bash
# Bare metal (new laptop): install tooling + pin the interpreter + verify kg
bash data/knowledge-graph/kg_refresh.sh bootstrap
# Before going back: memory is not in the delta -> park it under data/ so it travels
bash data/knowledge-graph/kg_refresh.sh snapshot-memory
# On the main machine, when the delta lands: merge memory back (with backup) and rebuild
bash data/knowledge-graph/kg_refresh.sh restore-memory  &&  kg-refresh
```

Full travel-kit detail in [`../examples/methodology/machine-sync.md`](../examples/methodology/machine-sync.md).

## 7. Confidentiality

Nodes carry internal names → **internal only**; the whole tree lives under `data/` (gitignored) and is
**never committed**. A sanitised version (name → role) to share outside is a separate deliverable, with
its own anonymisation pass — the copy in this course went through one (consistent pseudonyms, re-captured
screenshot).

---

## Map of the pieces

| Piece | What it is |
|---|---|
| `kg` (skill) | query: `explain` / `path` / `find` — deterministic |
| `kg-refresh` (skill) | rebuilds the graph (prepare → `graphify` → finalize) |
| `kg_query.sh` | wrapper for `graphify explain`/`path` + `find` in Python |
| `kg_refresh.sh` | deterministic bookends + `snapshot-memory` / `restore-memory` / `bootstrap` |
| `build_manifest.py` / `stage_corpus.py` | enumerate and stage the corpus |
| `data/knowledge-graph/output/` | `graph.json` + `graph.html` + `GRAPH_REPORT.md` |

> In one sentence: **the graph is the map; the agent's job after the pipeline is to be the guide.**
> Rebuildable, queryable in 1 call, hooked into the "history first" rule.
