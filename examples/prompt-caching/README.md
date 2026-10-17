# Prompt caching in Pi (§03)

Caching is a property of the **provider API**: a stable prefix (system prompt + tools + early
messages) is stored and re-read at a fraction of the input price. [`cache_demo.py`](./cache_demo.py)
shows the raw mechanism against the Anthropic API (two calls: the first writes, the second reads).

## What Pi does automatically

- **Anthropic-format requests** get `cache_control` markers on the system prompt, the last tool
  definition, and the last user, assistant or tool-result text (`cacheControlFormat: "anthropic"`
  compat field in `models.json`).
- **OpenAI-style requests** get session affinity and `prompt_cache_key` handling. For long retention Pi
  sends `prompt_cache_retention: "24h"`, or `prompt_cache_options.ttl: "30m"` on GPT-5.6+.

## What you control

| Lever | Where | Effect |
|---|---|---|
| `PI_CACHE_RETENTION=long` | environment | Extended retention where supported (e.g. Anthropic `cache_control.ttl: "1h"`) |
| `cacheWarming: "off" \| "streaming" \| "idle"` | user settings only (default `"streaming"`) | Keeps eligible caches warm during long runs or between runs. Runs only when the model declares a `promptCache` lifetime **and** the saving is estimated at ≥ $0.05. Warm-up usage counts in your totals |
| `showCacheMissNotices: true` | settings | Notices for cache misses, warm-ups and compaction usage |
| `/session` | TUI | Shows the next cache-warming decision (plus tokens and cost) |
| `promptCache: {"short": 300, "long": 3600}` | per model in `models.json` | Declares the model's cache lifetimes (custom/local providers) |
| `cache_warming_decision` | extension event | Override the warming decision in code |

Usage fields to watch in session data: `cacheRead`, `cacheWrite`, `cacheWrite1h`.

## Design choices that protect the cache (and what breaks it)

- Mid-conversation prompt and tool changes are **appended** as transcript deltas, not rewritten (0.86.0).
- MCP server summaries that change after connect are appended "so earlier messages stay cached".
- **Switching models loses the cache.**
- Since 1.3.0 a thinking-level change keeps the cache on OpenAI GPT-6 with an API key.
- Compaction's summarisation requests **disable prompt-cache writes**.

## Practical rules (same as the other volumes)

1. Keep the always-loaded prefix **small and stable**: lean `AGENTS.md`, few direct tools ([`../agents-md/`](../agents-md/), [`../mcp/`](../mcp/)).
2. Don't hop models mid-task without a reason — each switch pays the prefix again.
3. Long run ahead? `PI_CACHE_RETENTION=long` and leave `cacheWarming` at `"streaming"`.
4. Turn on `showCacheMissNotices` for a day to *see* what invalidates your cache before tuning anything.

## Run the demo

```bash
uv run --with anthropic --with python-dotenv python examples/prompt-caching/cache_demo.py
```

Needs `ANTHROPIC_API_KEY`; `CACHE_DEMO_MODEL` overrides the model id.
