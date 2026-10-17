#!/usr/bin/env python3
"""
Minimal prompt-caching demo against the Anthropic API.

Makes TWO calls with the same long system prompt (stable, with cache_control) and a different
question (variable, outside the cache). Call 1 WRITES the cache; call 2 READS it.

    uv run --with anthropic --with python-dotenv python examples/prompt-caching/cache_demo.py
    # needs ANTHROPIC_API_KEY in the environment (or a .env at the course root)

Expected output (indicative numbers):
    Call 1: cache_creation=~2100  cache_read=0      input=12
    Call 2: cache_creation=0      cache_read=~2100  input=11
    -> the second call processed the prefix at 0.1x the input price.

Pi applies these markers for you on Anthropic-format requests (system prompt, last tool definition,
last user/assistant/tool-result text). This demo talks to the API directly to show the mechanism.
"""
import os
import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # optional; exporting ANTHROPIC_API_KEY is enough

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY

# --- STABLE prefix: long instructions (>1024 tokens to be cacheable). ---
# In an agent (Pi / Claude Code / Cursor) this role is played by system prompt + tools + AGENTS.md.
STABLE_SYSTEM = (
    "You are a senior code reviewer on a platform team. Follow these conventions:\n"
    + "\n".join(
        f"{i}. Style rule number {i}: modules in domain {i} expose a single facade, "
        f"importing their internals is forbidden; errors propagate typed and logs carry no PII."
        for i in range(1, 61)
    )
)

MODEL = os.environ.get("CACHE_DEMO_MODEL", "claude-sonnet-4-5")


def ask(question: str) -> None:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": STABLE_SYSTEM,
                # the breakpoint goes at the END of the stable block:
                "cache_control": {"type": "ephemeral"},  # 5-min TTL (use {"ttl": "1h"} for one hour)
            }
        ],
        # the variable part (the question) goes AFTER the breakpoint -> it does not invalidate the cache
        messages=[{"role": "user", "content": question}],
    )
    u = resp.usage
    print(
        f"cache_creation={getattr(u, 'cache_creation_input_tokens', 0):>6}  "
        f"cache_read={getattr(u, 'cache_read_input_tokens', 0):>6}  "
        f"input={u.input_tokens:>4}  output={u.output_tokens:>4}"
    )


if __name__ == "__main__":
    print("Call 1 (writes the cache):")
    ask("May a module in domain 3 import internals of domain 7? Answer in one sentence.")
    print("Call 2 (reads the cache):")
    ask("May logs carry the user's email address? Answer in one sentence.")
