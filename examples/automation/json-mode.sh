#!/usr/bin/env bash
# JSON event mode with an honest exit code.
#
# Gotcha (docs, cli-integration): `pi --mode json` does NOT exit non-zero when the assistant run
# fails or is aborted. A script must inspect the events. Print mode (-p) does exit non-zero on
# error / aborted / length — prefer it when you only need the final text.
#
# Parsing rules from the [json] docs: split on LF only (not Node readline), assemble text from
# message_update deltas, treat message_end as authoritative, agent_settled = end of automatic work.
#
# ⚠️ The stopReason check below is a PATTERN: the field name comes from Pi's message types as used in
# the course's hands-on probe, not from a documented "failure" contract. Verify against [json] /
# [message-types] on your version.
set -euo pipefail
PROMPT="${1:?usage: json-mode.sh \"prompt\"}"
OUT="${OUT:-events.jsonl}"

pi --mode json --no-session "$PROMPT" </dev/null > "$OUT" || true

if ! grep -q '"type":"agent_settled"' "$OUT"; then
  echo "FAIL: run never settled — see $OUT" >&2; exit 3
fi
if grep -E '"type":"message_end"' "$OUT" | grep -Eq '"stopReason":"(error|aborted|length)"'; then
  echo "FAIL: assistant run ended with error/aborted/length — see $OUT" >&2; exit 2
fi
echo "OK: $(grep -c '' "$OUT") events in $OUT"
