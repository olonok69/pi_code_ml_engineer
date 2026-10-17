---
name: audit-python
description: Audit Python dependencies with pip-audit and verify the app still works. Use when the user asks for pip-audit, a Python CVE check, or an audit of a requirements.txt project (demo target ex_app/). For Node/npm, use the audit skill.
---

# Dependency audit (Python)

Invoke explicitly with `/skill:audit-python ex_app`, or let the model load it from the description.

Target: a folder with `requirements.txt` (demo: `ex_app/`).

1. `cd` into the target (the skill argument, or `ex_app/`).
2. Make sure `pip-audit` is available: `python -m pip install pip-audit` if needed
   (or `uvx pip-audit` if the machine uses uv).
3. Run `python -m pip_audit -r requirements.txt` (or the requirements file the user names).
4. Do **not** apply major upgrades automatically. If the user asks for a safe fix:
   `python -m pip_audit -r requirements.txt --fix`, only after explicit confirmation.
5. Tests:
   - If there is `pytest` / `tests/` / `test_*.py` → run `pytest` (or the README's command).
   - No suite → minimal smoke: `python -c "import ast,sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" *.py`.
6. Summarise: CVEs found, fixes applied (if any), test/smoke result.

Always show the real command output (evidence over claims).

If the target is Node (`package.json`), do **not** improvise pip — tell the user to run `/skill:audit`.
