#!/usr/bin/env bash
# Rehearse Pi against a "local model" without a GPU: scripted server + isolated agent dir.
# Run from anywhere: bash examples/local-models/verify/run.sh   (needs node and pi on PATH)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
TMP="$(mktemp -d)"
trap 'kill "$SRV" 2>/dev/null || true' EXIT

mkdir -p "$TMP/agent/extensions" "$TMP/work"
cat > "$TMP/agent/models.json" <<JSON
{"providers":{"ollama":{"baseUrl":"http://127.0.0.1:18080/v1","api":"openai-completions","apiKey":"ollama",
  "models":[{"id":"fake-4b","name":"Fake 4B","contextWindow":32768,"maxTokens":8192,"reasoning":false}]}}}
JSON
cp "$REPO/.pi/extensions/block-external-git.ts" "$TMP/agent/extensions/"
git -C "$TMP/work" init -q

(cd "$TMP" && node "$HERE/fake-openai.mjs" >/dev/null 2>&1) & SRV=$!
sleep 1

cd "$TMP/work"
PI_CODING_AGENT_DIR="$TMP/agent" PI_OFFLINE=1 PI_TELEMETRY=0 PI_SKIP_VERSION_CHECK=1 \
  pi -p --no-session --model ollama/fake-4b --tools read,bash,edit,write --no-mcp -nc "push it" </dev/null

echo "--- what Pi sent (from $TMP/requests.json):"
node -e '
const r = require(process.argv[1]);
for (const q of r) console.log(`msgs=${q.messages} tools=${q.tools.join(",")} system=${q.systemChars}c schemas=${q.toolSchemaChars}c max_tokens=${q.maxTokens}\n  last: ${q.lastMessage.slice(0,160)}`);
' "$TMP/requests.json"
