---
name: audit
description: Audit npm dependencies for vulnerabilities and verify tests still pass. Use for Node/JavaScript packages with a package.json (demo target ex_npm/). For Python apps with requirements.txt, use the audit-python skill instead.
---

# Dependency audit (npm)

Invoke explicitly with `/skill:audit ex_npm` (arguments are appended as the user request), or let
the model load this skill when the request matches the description.

Target: a folder with `package.json` (demo: `ex_npm/`).

1. `cd` into the target (the path given as the skill argument, or `ex_npm/`).
2. Run `npm audit` to list vulnerable packages.
3. Run `npm audit fix` for safe updates only. Never `--force` a major upgrade without asking.
4. Run the tests (`npm test`) to check nothing broke.
5. Summarise what was updated and which vulnerabilities still need manual work.

Always show the real command output (evidence over claims).

If the target is Python (`requirements.txt`, no `package.json`), do **not** improvise npm — tell
the user to run `/skill:audit-python`.
