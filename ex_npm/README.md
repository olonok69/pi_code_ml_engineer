# ex_npm — mini app for `/skill:audit`

Tiny Express service used in the Pi course to demo the **npm** audit skill.

## Install & test

```powershell
cd ex_npm
npm install
npm test
npm audit
```

## Endpoints

- `GET /health` → `{ "ok": true, "service": "ex-npm" }`

## Course usage

```text
/skill:audit ex_npm
```

See [`DEMO_RUNBOOK.md`](../DEMO_RUNBOOK.md).
