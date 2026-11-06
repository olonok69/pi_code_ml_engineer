---
name: preview
description: Show a processed document in the product's real preview page locally — what an environment produced (before) next to what the code under test produces on the same input inside the deployed service image (after), with an item-by-item compare. Non-prod environments only. Use to see a fix the way QA will see it before merging, to look at a reported document without logging in to the app, or to check that a branch changes (or does not change) a given document.
---

# preview: before/after of a document in the real preview page (local)

Tool: `data/changes/tools/preview/preview.sh` in the project repo. It lives in the shared record beside
`evidence`, not in git. Read-only AWS profile (`<read-only-profile>`). It builds on `evidence`: the
*before* is the run the environment really did, and the *after* re-runs the same input through the code
under test inside the **deployed service image**, then serves both through the consumer app's real
preview page.

```bash
cd data/changes/tools/preview
./preview.sh --doc <doc_id>                                   # dev; after = this checkout
./preview.sh --doc <doc_id> --src <worktree of the fix>        # after = a fix branch
./preview.sh --doc <doc_id> --env stg --before-only            # just look (nothing re-run)
./preview.sh --doc <doc_id> --src <worktree> --after-only      # only the fix's pane
./preview.sh --stop                                            # always stop it when done
```

- Doc id: `evidence` resolves an app URL to one (`evidence.py fetch --url … --file …`), or take it from a
  `discover` list. Only runs inside evidence's window (e.g. the last 7 days).
- Needs locally: Docker, `uv`, the AWS CLI, the document converter the service uses (e.g. LibreOffice), a
  clone of the **consumer** app (for its real preview page and data adapter) and the test env file with
  the model API key: the after makes **real LLM calls**.
- It opens a local index page (before and after panes on their own ports). Views: default = side by side;
  `--before-only` = no re-run (also the automatic fallback if the after fails); `--after-only` = one pane,
  the compare still runs and a failed after is an error. The two exclude each other.
- Read `compare.txt` in the run folder (outside `data/`, e.g. `<repo>/../_preview_runs/<env>_<doc>_<utc>/`):
  item by item (title + body), first line = verdict. Check `run.json` too.
- Documents that the consumer post-processes go through the consumer's **real** adapter (a clone of its
  default branch), as for a fresh upload. Never a re-implementation of it.

## Reading the result
1. **Identical** on a branch that should change the output → the change does not reach this document's path.
2. The before is what the environment ran **then**. If `run.json` says `image_changed_since_run: true`, run
   once with `--src` on the environment's own commit first: a difference may be the deploy, not your branch.
3. A **single** difference in LLM-derived text can be model variance: run it again before believing it.

## Hard rules
1. Never point the run folder inside `data/`: a run holds a copy of `src/` and a client document, and the
   next push of the shared record would publish both.
2. It spends real LLM calls and runs Docker: one document at a time, `--stop` after.
3. Re-login (`aws sso login`) before drawing any conclusion from an AWS error.
4. It is a viewing aid, not a gate: it does not replace the wrapper-stage repro, the deployed-image check or
   the tests. It does show the "look at the output" check of the outbound gate in the real page.
5. Prod is not supported (no access, by design).
