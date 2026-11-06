# `tools/` — two read-mostly tools for the agent (and two that stay in the project)

Genericised copies of two real project tools. Both share one idea: **the agent can read far more than
it can write**, and that boundary is enforced in code, not in an instruction. That matters even more in
Pi, which has no command allowlist: the tool's own construction is the gate.

| Folder | What it is | Skill that uses it |
|---|---|---|
| [`atlassian/`](./atlassian/) | **Read-only** Jira + Confluence client (`atl.py`) and the only write path — to one Confluence page, with human confirmation (`confluence_write.py`) | [`atlassian`](../../skills-plugins/.pi/skills/atlassian/SKILL.md) |
| [`evidence/`](./evidence/) | The reusable core of run-evidence capture: pick the **S3 version** a run really used, read-only AWS client, signed-URL scrubbing | [`evidence`](../../skills-plugins/.pi/skills/evidence/SKILL.md) |

```bash
cd examples/methodology/tools
uv run -q --with pytest --with boto3 python -m pytest     # offline: no network, no credentials
```

---

## 1. `atlassian/` — read the tracker and the wiki, don't write them

`atl.py` is standard-library Python. It has **a single** network function, `Client._get`, and sends
only `GET`; a test fails if any other method appears. Adding a write is a reviewable code change, not a flag.

```bash
python3 atlassian/atl.py jira issue PROJ-123
python3 atlassian/atl.py jira comments PROJ-123 --last 3
python3 atlassian/atl.py jira xml PROJ-123 --out data/changes/proj-123/
python3 atlassian/atl.py confluence diff docs/page.md <PAGE_ID>
```

Credentials: `~/.config/<org>/jira.env` (`JIRA_BASE_URL=https://<your-site>.atlassian.net`,
`JIRA_EMAIL`, `JIRA_API_TOKEN`), `chmod 600`, **one token per person**, written by that person in their
own terminal. The token is never printed, not even in errors (there is a test).

**Writing to Confluence** is `confluence_write.py`, and its shape is the lesson:

1. `pull <PAGE_ID>` — save the live body for editing.
2. `plan <PAGE_ID> new.xhtml --root <ROOT_ID>` — check the page hangs under the allowed tree (ancestors
   read from Confluence, not from the caller), take a **backup**, print the visible-text diff and a
   **confirmation token**.
3. The human reads the diff and says OK **for that page**.
4. `apply plan.json --confirm <token>` — refuses if the token does not match, if the file changed since
   the plan, or if someone edited the page in Confluence meanwhile; writes version N+1 (a 409 is
   reported, never retried) and **reads the page back** to compare.

⚠️ Lesson measured on the first real write: Confluence reorders macro parameters on save, so a correct
write read back as "does not match". The diff compares **visible text** (without `<ac:parameter>`) but
keeps the content of code blocks — a naive tag strip deleted them, and a change inside a code block
would have gone unnoticed.

Creating, editing, commenting on or transitioning Jira tickets: **always the person**. The agent drafts.

---

## 2. `evidence/` — the evidence of a run, as it was

**Problem.** "This document failed" arrives with an app URL. Gathering the source document, the
generated artefact, the result JSON and the log lines by hand takes half an hour, and almost always picks
the **wrong** version: the file was re-uploaded later, or the result belongs to the next run.

**Design (the full tool lives in the project; the generic core is here):**

- **The log line is the index.** Each run writes a start line with document id, container, variant,
  original name and the exact S3 key of the source. Error lines carry no id, but a log stream is one
  container and a container handles one invocation at a time: everything between two start lines
  belongs to the first.
- **Source version = the newest with `LastModified ≤ start + 60 s`**, never beyond the next run on the
  same key. Measured: the upload that triggers the run lands in S3 **~1 s after** the log line, so
  "≤ start" picked the *previous* upload ([`versions.py`](./evidence/versions.py), `source_version`).
- **Artefact and result = the version written in `[start, next run on the same KEY)`.** Per key, not per
  document: a file re-uploaded under another id reuses the same output keys, and the per-document rule
  grabbed the other run's files.
- **Depends on bucket versioning.** `check_recovery` fails (exit 6) if versioning is not `Enabled` or an
  expiry rule exists: without old versions, "the source as it was" no longer exists, and the tool says
  so instead of returning the current one.
- **Read-only by construction:** [`awsro.py`](./evidence/awsro.py) wraps every boto3 client and refuses
  anything that is not `get_/list_/describe_/head_/filter_log_events`; another test scans the modules for
  writing methods.
- **Log lines carry pre-signed URLs** with temporary credentials: [`scrub.py`](./evidence/scrub.py)
  cleans them before anything is written to disk (log, manifest, summary).
- **`discover --list`** counts and groups failures by signature (`rule:type:message`, ids masked) without
  downloading anything. It exists because the first real pass found ~240 problem runs in 24 h: a
  downloading `discover` would have tripped its own limit every morning. It is what step 3c of
  `day start` runs.
- **The default output (`_evidence/`) is not pushed to the shared record** (`JUNK_ARGS` in
  [`../s3-sync/config.env.example`](../s3-sync/config.env.example)): it may contain client documents.
  Only curated material moves into the ticket folder.

⚠️⚠️ **The canary that passed with the wrong answer.** The first `selftest` compared the sha256 of the
downloaded file with a direct download of "the same" version — and **passed** even though the tool picked
the wrong version, because two uploads were **byte-identical**. A check computed by the tool itself cannot
catch a selection error. The canary now asserts **version timestamps known in advance**, and was shown to
fail with `SOURCE_GRACE = 0`. Canary against a known answer, and on more than one property.

Exit codes: 0 ok · 1 usage · 2 login (`aws sso login`, do not diagnose) · 3 AWS error · 4 nothing found ·
5 guard (narrow `--since`) · 6 the bucket no longer guarantees old versions.

## 3. Not shipped here: `preview/` and `ticket_status/`

Two more project tools are referenced by skills but are **not** copied into the course, because both are
bound to one product rather than to the method:

| Tool | Skill | Why it is not here | What to take from it |
|---|---|---|---|
| `preview/` (`preview.sh`) | [`preview`](../../skills-plugins/.pi/skills/preview/SKILL.md) | Drives the **consumer app's real preview page** and the **deployed service image** (Docker, a consumer clone, real LLM calls). A generic copy would be a re-implementation of a product UI, which is exactly what the tool refuses to be. | The pattern: *before* = what the environment ran (from `evidence`), *after* = the code under test **in the deployed image**, both rendered by the **real** consumer page, plus an item-by-item `compare.txt`. Run folders live **outside** `data/`. |
| `ticket_status/` (`sync.py`) | [`day`](../../skills-plugins/.pi/skills/day/SKILL.md) step 3b (optional) | Maps one tracker's workflow states and one Git host's PR data into one team's status workbook. | Publisher writes, contributors only read (a binary workbook with two writers is last-writer-wins); a **canary** check before any write. |

Both live beside `evidence/` in the project's shared record (`data/changes/tools/`), not in git.
