// UNTESTED PATTERN — written against the API documented in the course findings (§10), not run.
// Blocks shell commands that would print or copy a .env file.
//
// Why bash and not the `read` tool? The findings document the typed `bash` variant
// (`event.toolName === "bash"`, `event.input.command`) but NOT the input field names of the
// built-in `read` tool. Gating `read` would mean guessing a field name — so this pattern only
// covers the shell path. Check the `ToolCallEvent` types in your installed
// @earendil-works/pi-coding-agent before extending it to `read`.
//
// Regex gates can be bypassed (`sh -c`, aliases, scripts). For real isolation use a container.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const SECRET_READ = /\b(cat|less|more|head|tail|cp|scp|base64|xxd)\b[^|;&]*(^|[\s/])\.env(\.[\w-]+)?\b/i;

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event) => {
    if (event.toolName !== "bash" && event.toolName !== "powershell") return undefined;
    const command = String((event.input as { command?: string }).command ?? "");
    if (SECRET_READ.test(command)) {
      return { block: true, reason: "Blocked by policy: .env files hold secrets. Ask the human for the value you need." };
    }
    return undefined;
  });
}
