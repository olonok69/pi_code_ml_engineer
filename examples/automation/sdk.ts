// Minimal Pi SDK run — shape taken from the Pi SDK docs as captured in the course findings.
// Run: npm i && npx tsx sdk.ts   (needs a provider key in the environment, e.g. ANTHROPIC_API_KEY)
//
// ⚠️ SDK sessions do NOT load built-in MCP or codemode. To get them, add createMcpExtension(),
// createCodemodeExtension() and createToolSearchExtension() through
// DefaultResourceLoader({ extensionFactories }) and call session.bindExtensions() — see the 14
// typechecked examples in the Pi repo's packages/coding-agent/examples/sdk/.
import { createAgentSession, SessionManager } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession({
  cwd: process.cwd(),
  sessionManager: SessionManager.inMemory(), // ephemeral, like --no-session
  // other documented options: agentDir, model, thinkingLevel, tools, excludeTools, customTools,
  // resourceLoader, settingsManager
});

const unsubscribe = session.subscribe((ev) => {
  // stream events here if you need progress (same event family as --mode json)
  void ev;
});

try {
  await session.prompt("Summarise what this repository does in five bullet points.");
  console.log(session.getLastAssistantText());
} finally {
  unsubscribe?.();
  session.dispose();
}
