// A scripted OpenAI-compatible server: rehearse the Pi <-> local-server plumbing with no GPU and no model.
// It answers /v1/models and streams three /v1/chat/completions turns:
//   1) a bash tool call `git push origin main`  (the git gate should block it)
//   2) a bash tool call `echo allowed-ok`       (should run)
//   3) the text "done"
// Every request is summarised in requests.json (model, message count, tool names, prompt sizes, max_tokens).
// Usage: node fake-openai.mjs [port]   (default 18080)
import http from "node:http";
import fs from "node:fs";

const port = Number(process.argv[2] ?? 18080);
const script = [
  { tool: { name: "bash", args: { command: "git push origin main" } } },
  { tool: { name: "bash", args: { command: "echo allowed-ok" } } },
  { text: "done" },
];
let turn = 0;
const log = [];

http.createServer((req, res) => {
  let body = "";
  req.on("data", (c) => (body += c));
  req.on("end", () => {
    if (req.url.endsWith("/models")) {
      res.setHeader("content-type", "application/json");
      res.end(JSON.stringify({ data: [{ id: "fake-4b" }] }));
      return;
    }
    const j = JSON.parse(body || "{}");
    log.push({
      model: j.model,
      messages: (j.messages ?? []).length,
      tools: (j.tools ?? []).map((t) => t.function?.name),
      systemChars: JSON.stringify(j.messages?.[0] ?? "").length,
      toolSchemaChars: JSON.stringify(j.tools ?? []).length,
      maxTokens: j.max_tokens ?? j.max_completion_tokens,
      lastMessage: JSON.stringify(j.messages?.at(-1)).slice(0, 300),
    });
    fs.writeFileSync("requests.json", JSON.stringify(log, null, 1));

    const step = script[Math.min(turn++, script.length - 1)];
    res.writeHead(200, { "content-type": "text/event-stream" });
    const chunk = (d) =>
      res.write(`data: ${JSON.stringify({ id: "x", object: "chat.completion.chunk", created: 0, model: j.model, ...d })}\n\n`);
    if (step.tool) {
      chunk({ choices: [{ index: 0, delta: { role: "assistant", tool_calls: [{ index: 0, id: `call_${turn}`, type: "function",
        function: { name: step.tool.name, arguments: JSON.stringify(step.tool.args) } }] }, finish_reason: null }] });
      chunk({ choices: [{ index: 0, delta: {}, finish_reason: "tool_calls" }], usage: { prompt_tokens: 10, completion_tokens: 5, total_tokens: 15 } });
    } else {
      chunk({ choices: [{ index: 0, delta: { role: "assistant", content: step.text }, finish_reason: null }] });
      chunk({ choices: [{ index: 0, delta: {}, finish_reason: "stop" }], usage: { prompt_tokens: 10, completion_tokens: 1, total_tokens: 11 } });
    }
    res.end("data: [DONE]\n\n");
  });
}).listen(port, "127.0.0.1", () => console.log(`fake OpenAI-compatible server on http://127.0.0.1:${port}/v1`));
