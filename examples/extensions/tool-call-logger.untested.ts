// UNTESTED PATTERN — the Pi analogue of the Cursor/Claude "log the payload" hook.
// Appends one JSON line per tool call to .pi-tool-calls.jsonl in the working directory.
// Never blocks (returns undefined). Remember: a tool_call handler that THROWS blocks the tool as a
// fail-safe, so the write is wrapped in try/catch on purpose — logging must not stop the agent.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { appendFileSync } from "node:fs";

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event) => {
    try {
      appendFileSync(
        ".pi-tool-calls.jsonl",
        JSON.stringify({ ts: new Date().toISOString(), tool: event.toolName, input: event.input }) + "\n",
      );
    } catch {
      // swallow: an audit log must never become a gate
    }
    return undefined;
  });
}
