# Skills, prompt templates and packages in Pi (§05)

Claude Code has three layers — **slash commands** (`.claude/commands/`), **skills** (`.claude/skills/`)
and **plugins/marketplaces**. Cursor has skills (`.cursor/skills/`) and a web Marketplace. Pi has the
same three ideas under different names: **skills**, **prompt templates** and **packages**.

## 1. Skills — the Agent Skills standard

Pi implements the **Agent Skills spec** (agentskills.io): a skill is a directory with `SKILL.md`, and it
may bundle `scripts/`, `references/` and `assets/`.

**Locations** (discovery is recursive):

| Where | Notes |
|---|---|
| `~/.pi/agent/skills/` | Global |
| `.pi/skills/` | Project — **trusted folders only** |
| `~/.agents/skills/`, `.agents/skills/` | The cross-tool location; project copies from cwd and ancestors up to the repo root (trust-gated) |
| `"skills": [ … ]` setting, `--skill <path>`, packages | Explicit |

**`.claude/skills` is not auto-discovered**, but you can point at it. **[TESTED]**:
`"skills": ["~/.claude/skills"]` loaded all ~85 of a real user's Claude skills — and poured every
description into the system prompt. List the directories you want **one by one**.

**Frontmatter** (spec fields only): `name`, `description` (required, ≤ 1024 chars, drives auto-loading),
`license`, `compatibility`, `metadata`, `allowed-tools` (experimental), `disable-model-invocation: true`
(explicit command only). Name: lowercase `a-z0-9-`, ≤ 64 chars, no leading/trailing/double hyphens.
A missing description means the skill is **not loaded**; on a name collision the first one found wins.

**Unknown keys are ignored silently** **[TESTED]**: Claude-style `trigger: /day` loaded fine. The skills
in this folder keep only `name` + `description` anyway, so they are portable as-is.

**Invocation:**

- The model auto-loads a skill by `read`ing its `SKILL.md` when the description matches. (So a skill
  needs a file-read tool enabled.)
- To force one: **`/skill:name [args]`** — the arguments are appended as a user request. **Not** `/name`.
- `enableSkillCommands` (default `true`) controls whether skills appear in `/` completion.

## 2. The skills in this folder

| Skill | What it shows | Try it |
|---|---|---|
| [`audit`](./.pi/skills/audit/SKILL.md) | npm audit + tests, evidence over claims | `/skill:audit ex_npm` |
| [`audit-python`](./.pi/skills/audit-python/SKILL.md) | pip-audit + tests/smoke | `/skill:audit-python ex_app` |
| [`deploy-staging`](./.pi/skills/deploy-staging/SKILL.md) | tests → build → **human OK** → deploy → smoke | `/skill:deploy-staging ex_staging` |
| [`day`](./.pi/skills/day/SKILL.md) | The methodology's start/end-of-day routine for the shared record (role-aware) | `/skill:day start` |
| [`atlassian`](./.pi/skills/atlassian/SKILL.md) | Read-only Jira/Confluence; tool in [`../methodology/tools/atlassian/`](../methodology/tools/atlassian/) | `/skill:atlassian jira issue PROJ-123` |
| [`evidence`](./.pi/skills/evidence/SKILL.md) | Read-only run-evidence capture; core in [`../methodology/tools/evidence/`](../methodology/tools/evidence/) | `/skill:evidence discover --env dev --since 24h --list` |

The first three are also **live** in this repo's root [`.pi/skills/`](../../.pi/skills/) (open the repo in
Pi, `/trust`, then invoke). `day`'s scripts: [`../methodology/s3-sync/`](../methodology/s3-sync/).

**Read-only is enforced by the tools, not by Pi.** Pi has no allowlist: `atl.py` sends GET only (tested),
`evidence` wraps boto3 in a read-only client (tested) and runs under a read-only IAM role. That is the
same design as in the other volumes — it just carries more weight here.

## 3. Prompt templates — Pi's slash commands

`~/.pi/agent/prompts/<name>.md` or `.pi/prompts/<name>.md` becomes `/<name>`. Frontmatter: `description`,
`argument-hint`. Arguments: `$1`, `$@`, `$ARGUMENTS`, `${1:-default}`, `${@:N}`, `${@:N:L}`. Only direct
`.md` children of the directory load. This is the closest analogue to `.claude/commands/`.

[`.pi/prompts/day.md`](./.pi/prompts/day.md) restores the `/day start` muscle memory by forwarding to the
skill ("Run the day skill: $@"). ⚠️ That template-forwards-to-skill trick is the **course's inference**,
not a documented Pi pattern — `/skill:day start` is the documented way.

## 4. Packages — the marketplace analogue

```bash
pi install npm:@scope/pkg@1.0.0          # or git:github.com/u/r@v1 · https://… · ./local
pi install -l npm:@scope/pkg             # -l / --local = project scope (installs only after trust)
pi -e npm:pkg                            # try once without installing
pi list · pi remove <pkg> · pi update --extensions · pi config   # pi config = TUI to toggle resources
```

A package is an npm or git directory with `extensions/`, `skills/`, `prompts/`, `themes/` (or a `"pi"`
manifest in `package.json`). The `pi-package` keyword lists it in the gallery at
<https://pi.dev/packages> — 5,354 packages on 2026-10-17. There is **no in-app marketplace UI** like
Claude's `/plugin` or Cursor's Marketplace: browse the gallery, install from the CLI.

Everything in a package runs with your permissions (extensions are in-process code) — review before
installing; [3rd-party] packages named in this course are untested.

## 5. Claude Code → Cursor → Pi

| Claude Code | Cursor | Pi |
|---|---|---|
| `~/.claude/skills`, `.claude/skills` | `.cursor/skills` (+ reads `.claude/skills`) | `~/.pi/agent/skills`, `.pi/skills`, `.agents/skills`, `"skills"` setting |
| `/name` | `/name` | `/skill:name [args]` |
| `.claude/commands/*.md` | skills / commands | prompt templates `prompts/*.md` → `/name` |
| `/plugin install` | cursor.com/marketplace | `pi install npm:… / git:…`; gallery pi.dev/packages |
