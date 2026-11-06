# Local models on a small GPU (4 GB VRAM)

> 🇪🇸 Versión en español: [`README_ES.md`](./README_ES.md).

How to point Pi at a model running on your own machine, sized for a **4 GB** card, and how Pi compares
with the other agents and servers people usually reach for.

> **Status.** **[TESTED on Pi 1.5.0, 2026-11-06]:** the Pi side of the plumbing — a `models.json` provider
> (`api: "openai-completions"`) against a scripted OpenAI-compatible server, `--model ollama/<id>`,
> `--tools`, `--no-mcp`, the [`settings.json.example`](./settings.json.example) overrides, real tool calls
> round-tripping, and the git gate blocking `git push`. **UNTESTED:** a real model on a real 4 GB card (no GPU
> or model download in the test box). The model choice, file names and VRAM figures come from the model card
> ([qwen35-4b-gguf]); expect to tune `ctx-size` once on your hardware.

## TL;DR

- **Agent: keep Pi.** It is the best fit of the common agents for a small local model: a short system prompt,
  a handful of tools, and a **built-in llama.cpp provider** (`/login llama.cpp`, `/llama`). **Measured on
  1.5.0:** with `--tools read,bash,edit,write --no-mcp -nc`, the system prompt is ~2.3 K characters and the four
  tool schemas ~2.8 K — about **1.3 K tokens** of fixed overhead per request. Agents with very
  long system prompts and many tools leave a 4B model little room and confuse it.
- **Server: llama.cpp router.** It is what Pi integrates natively, and it gives the control a 4 GB card needs
  (quantised KV cache, exact context size, no vision projector). Ollama or LM Studio are the easy fallback.
- **Model: Qwen3.5-4B, `IQ4_XS` (~2.7 GB) or `Q4_K_M` (~3.0 GB), 16–32K context.** 7–9B models do not fit
  4 GB fully on the GPU at a usable context; partial CPU offload works but is slow for an agent loop.
- **Set expectations.** A 4B model can read files, run commands and make small, well-specified edits.
  It will not plan multi-file changes the way a frontier model does. Use it for scoped tasks, or for
  privacy/offline work, and keep a cloud model for the hard ones (`Ctrl+P` cycles models in Pi).

## Files here

| File | Goes to | What it does |
|---|---|---|
| [`qwen3.5-4b.ini`](./qwen3.5-4b.ini) | next to `llama-server` (any path) | llama.cpp router preset sized for 4 GB |
| [`models.json.example`](./models.json.example) | `~/.pi/agent/models.json` | Ollama and LM Studio providers (not needed for llama.cpp) |
| [`verify/`](./verify/) | run in place | `run.sh` + `fake-openai.mjs`: rehearse Pi against a scripted OpenAI-compatible "local model" (no GPU, no download) |
| [`settings.json.example`](./settings.json.example) | merge into `~/.pi/agent/settings.json` | Per-model compaction thresholds that fit a 32K window and thinking `off` — only for the local models (`compaction.modelOverrides`, `modelThinkingLevels`); cloud models keep the defaults |

## Route A — llama.cpp router (recommended)

1. **Install llama.cpp** with GPU support. Docs installer: `curl -LsSf https://llama.app/install.sh | sh`,
   then `llama cli --version` [llama-cpp]. On Windows the prebuilt CUDA release of `llama-server.exe` works
   the same way. The NVIDIA recipe page covers CUDA builds [nvidia-rtx].
2. **Start the router with the preset** (router mode = no `-m` / `--model` / `-hf` on the command line):

   ```bash
   llama serve --models-preset qwen3.5-4b.ini --host 127.0.0.1 --port 9931
   # Windows prebuilt:
   # .\llama-server.exe --models-preset qwen3.5-4b.ini --host 127.0.0.1 --port 9931
   ```

   The first start downloads the GGUF from Hugging Face. Ready when
   `curl http://127.0.0.1:9931/models` lists `qwen3.5-4b` as `loaded`.
3. **Connect Pi:** inside Pi run `/login llama.cpp` and give `http://127.0.0.1:9931`, or

   ```bash
   export LLAMA_BASE_URL=http://127.0.0.1:9931
   pi --tools read,bash,edit,write --no-mcp
   ```

4. **Select the model:** `/model` → `qwen3.5-4b`. Without the preset you can also use `/llama` →
   **Download model…** and type `bartowski/Qwen_Qwen3.5-4B-GGUF:IQ4_XS` [llama-cpp].

**If it does not fit:** lower `ctx-size` to `16384` first, then switch `IQ4_XS` ↔ `Q4_K_M`, then close other
GPU users (a browser with hardware acceleration and the Windows desktop each take a few hundred MB).
Check `nvidia-smi` while the model is loaded: if VRAM is full and generation is slow, layers or cache spilled
to system RAM.

## Route B — Ollama or LM Studio (easiest install)

Both speak the OpenAI Chat Completions API, so Pi talks to them through `~/.pi/agent/models.json`
(`api: "openai-completions"`, dummy `apiKey`) [models]. Copy [`models.json.example`](./models.json.example),
keep the provider you use, and make the model `id` match what the server reports
(`ollama list`, or LM Studio's model identifier). `/model` reloads the file.

- **Ollama:** `ollama pull qwen3.5:4b` (check the tag in the Ollama library). **Gotcha:** Ollama's default
  context is small and it truncates silently past it, which breaks agent sessions. Raise it before starting
  the server, e.g. `OLLAMA_CONTEXT_LENGTH=32768 ollama serve` (Windows: set the variable in System
  Properties, then restart Ollama), and keep `contextWindow` in `models.json` equal to it.
- **LM Studio:** download the same GGUF in the app, set the context length when loading it, enable the
  local server (default port 1234).

## Rehearse without a GPU (for the demo or CI)

```bash
bash examples/local-models/verify/run.sh      # needs node + pi on PATH
```

It starts [`verify/fake-openai.mjs`](./verify/fake-openai.mjs) (a scripted OpenAI-compatible server that plays a
model asking for `git push origin main`, then `echo allowed-ok`), points an **isolated** agent dir at it through
`models.json`, loads this repo's git gate, and prints what Pi actually sent. Expected (**[TESTED] on 1.5.0**):
the push comes back `Blocked by policy…`, the echo runs, and every request carries 4 tool schemas,
`max_tokens=8192` from `models.json`, and a ~2.3 K-character system prompt. Swap the `baseUrl` for
`http://127.0.0.1:9931/v1` or `http://localhost:11434/v1` and the same command talks to a real local server.

## Make Pi lighter for a small model

| Lever | Why |
|---|---|
| `contextWindow` in `models.json` = the server's real context | Pi's default is 128000; if Pi thinks the window is bigger than the server's, compaction never triggers and the server truncates instead |
| `compaction.modelOverrides` → `reserveTokens` ~6K, `keepRecentTokens` ~8K for the local model ([`settings.json.example`](./settings.json.example)) | The defaults (16384 / 20000) are sized for 200K-token models and would eat most of a 32K window. Keys are exact `provider/modelId`, so cloud models keep the defaults. Since 1.4.0 the summary request itself uses the model's output limit (`maxTokens`) |
| `--tools read,bash,edit,write` | Fewer tool schemas in the prompt, fewer wrong tool picks |
| `--no-mcp` | Disables MCP for the run; each server adds tools/instructions to the prompt and this repo's own `.pi/mcp.json` loads two |
| Thinking `off` (`modelThinkingLevels` per model, or `/thinking`, `Shift+Tab`) for quick edits | Qwen3.5 thinks by default; at ~20–40 tok/s long thoughts dominate latency. Turn it on for harder steps |
| Short, scoped prompts with explicit file paths | Small models navigate poorly; point them at the file |

## Which server?

| Server | Fit for 4 GB | Notes |
|---|---|---|
| **llama.cpp (router)** | **Best** | Native Pi provider, `/llama` load/unload/download, KV-cache quantisation, exact context control, GGUF |
| **Ollama** | Good | Easiest install, model library; watch the default context length; less control over offload/cache |
| **LM Studio** | Good | GUI, Windows-friendly, llama.cpp underneath; handy to try models before writing a preset |
| **vLLM / SGLang** | Poor | Built for throughput on big GPUs; pre-allocates VRAM, Linux-first, weak at fitting a model into 4 GB |

## Which agent?

| Agent | Fit for a 4B local model | Why |
|---|---|---|
| **Pi** | **Best of the tool-calling agents** | Minimal system prompt and core tools by design; built-in llama.cpp provider; any OpenAI-compatible server via `models.json`; tunable compaction |
| **Aider** | Strong alternative | Does not need native tool calling: the model answers with edit blocks that Aider applies, and it has per-model edit formats for weak models. Good for "edit these files" work; less autonomous (no free shell loop) |
| **OpenCode** | Weaker | Capable agent, but larger prompts and more tools; small models struggle with its tool calling |
| **Cline / Roo Code** | Poor | Very long system prompts (many thousands of tokens) and XML/tool protocols that 4B models follow unreliably |
| **Continue** | Use for autocomplete | Its agent mode has the same problem, but **tab autocomplete** with a tiny FIM model (e.g. Qwen2.5-Coder-1.5B) runs well on 4 GB beside, or instead of, the agent |

The argument for Pi is the one this course makes elsewhere: Pi ships less (no permission prompts, no
subagents, no plan mode), and on a small model *less prompt* is the feature.

## Model shortlist for 4 GB

| Model | Quant / size | Use |
|---|---|---|
| **Qwen3.5-4B** | IQ4_XS 2.7 GB · Q4_K_M 3.0 GB · Q5_K_M 3.4 GB [qwen35-4b-gguf] | Default pick for the agent: recent, tool-calling chat template, thinking mode |
| Qwen2.5-Coder-3B-Instruct | Q4_K_M ~2 GB | Older; more context headroom; fine for single-file edits |
| Qwen2.5-Coder-1.5B (base) | Q4_K_M ~1 GB | Autocomplete (FIM) only, e.g. with Continue |
| Qwen3.5-9B, Qwen2.5-Coder-7B, Falcon-H1R-7B | Q4 4.5–6 GB | **Do not fit** 4 GB with a usable context; only with partial CPU offload (slow). They are the 8 GB tier [kilo-local] |

Sizes are GGUF file sizes; add the KV cache (grows with context) and ~0.3–0.5 GB of runtime/desktop overhead.

## Sources

- [llama-cpp] Pi docs, llama.cpp — <https://pi.dev/docs/latest/llama-cpp>
- [nvidia-rtx] Pi docs, NVIDIA RTX + llama.cpp presets — <https://pi.dev/docs/latest/nvidia-rtx-llama-cpp>
- [models] Pi docs, Models ("Configure a compatible endpoint") — <https://pi.dev/docs/latest/models>
- [models-configuration] Pi docs, `models.json` reference — <https://pi.dev/docs/latest/models-configuration>
- [qwen35-4b-gguf] Qwen3.5-4B GGUF quants — <https://huggingface.co/bartowski/Qwen_Qwen3.5-4B-GGUF>
- [kilo-local] "The best local coding models for any setup" (2026-07-29) — <https://blog.kilo.ai/p/the-best-local-coding-models-for>
- [compaction] Pi docs, Compaction (`modelOverrides`; summaries use the output limit since 1.4.0) — <https://pi.dev/docs/latest/compaction>

All checked 2026-11-06 against Pi 1.5.0. Agent comparisons (Aider, OpenCode, Cline, Continue) are design-level, not benchmarked here.
