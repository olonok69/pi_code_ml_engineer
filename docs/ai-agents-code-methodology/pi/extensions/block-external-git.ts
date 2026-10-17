import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// The human owns every external action: push, PR, merge, release, deploy.
const EXTERNAL = [
  /\bgit\s+push\b/i,
  /\bgh\s+pr\s+(create|merge|close|edit|review|comment)\b/i,
  /\bgh\s+(release|repo\s+(create|delete|edit))\b/i,
  /\bgit\s+merge\b.*\b(origin|upstream)\//i,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event) => {
    if (event.toolName !== "bash" && event.toolName !== "powershell") return undefined;
    const command = String((event.input as { command?: string }).command ?? "");
    const hit = EXTERNAL.find((re) => re.test(command));
    if (hit) {
      return { block: true, reason: `Blocked by policy: external git/PR action (${hit}). Prepare it and hand it to the human.` };
    }
    return undefined;
  });
}
