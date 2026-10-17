---
name: deploy-staging
description: Deploy the current app to staging — runs tests, builds, asks for human confirmation, then runs the staging deploy script and a health smoke check. Use when the user wants to deploy to staging (demo target ex_staging/, a simulated local staging, no cloud).
---

# Deploy to staging

A repeatable, safe staging deploy. Invoke with `/skill:deploy-staging ex_staging`.
**Demo target:** `ex_staging/` (simulated local staging — no real cloud).

## Steps

1. `cd` into the target (`ex_staging/` or the path given as the argument).
2. Check the **target's** git tree: `git status --porcelain -- .` from that folder.
   Uncommitted changes in the target → STOP and say so. (Dirt elsewhere in the course repo can be
   ignored after mentioning it.)
3. Run the tests: `npm test`. Failure → STOP and show the output.
4. Build: `npm run build`. Failure → STOP.
5. **Ask for human confirmation** before deploying (an external, potentially irreversible action).
   Pi has no approval prompt of its own, so this skill text *is* the gate: do not run the deploy until
   the user says OK in this session.
6. After the OK: `npm run deploy:staging` (equivalent to `node scripts/deploy.mjs staging`).
   - In this demo it starts a local server and writes `.staging-url`.
   - In a real repo replace it with your deploy script or pipeline.
7. Smoke check: read `.staging-url` and call `GET {url}/health` (`curl -fsS`). It must be HTTP 200
   with `ok: true`.
8. Summarise: what was deployed, the URL, the smoke result. Mention `npm run staging:stop` to stop the demo.

## Rules

- **Never** deploy with red tests or a dirty target.
- **Never** deploy without an explicit human request/confirmation (handoff gate).
- Always show the real output of each command.
