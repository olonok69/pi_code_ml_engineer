# Pi — Guía técnica de implementación (curso en tres partes)

> 🇬🇧 English version: [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md)
>
> Referencia para copiar y pegar al construir cada pieza. Complementa
> [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) (el hilo narrativo) con el **cómo**.
> Todos los artefactos ejecutables están en [`examples/`](./examples/); [`docs/`](./docs/) es material de
> referencia de una instalación real. Volúmenes hermanos, misma estructura y numeración de secciones:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer/blob/master/GUIA_TECNICA_EN.md) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer/blob/main/GUIA_TECNICA_EN.md) (carpetas hermanas; los
> enlaces asumen que los volúmenes están uno junto al otro).
>
> **Nota de verificación:** cada afirmación sobre Pi se comprobó el **17 de octubre de 2026** contra **Pi 1.3.0**
> (`@earendil-works/pi-coding-agent`, publicado el 2026-10-15) — documentación en <https://pi.dev/docs/latest>,
> código fuente en `main` y una instalación local. Las notas de investigación están en
> [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md). Marcadores usados
> abajo: **[TESTED]** = ejecutado localmente · **[3rd-party]** = paquete de la comunidad, sin probar ·
> **NOT DOCUMENTED** = sin fuente. **Pi avanza rápido** (la 1.0 salió el 2026-10-01; seis versiones desde
> entonces) — vuelve a comprobar antes de reutilizar.
>
> **Actualización 2026-11-06 — Pi 1.5.0.** La guía se revisó de nuevo contra **1.4.0 (2026-10-21)** y **1.5.0
> (2026-11-02)**: changelog, la documentación incluida en el paquete 1.5.0 y una instalación local de 1.5.0
> (git gate, proveedor local en `models.json`, nueva prueba del gotcha de `</dev/null`). Qué cambió y qué se volvió
> a probar: [`docs/research/PI_UPDATE_2026-11-06.md`](./docs/research/PI_UPDATE_2026-11-06.md). Los cambios se
> marcan en línea como *(1.4.0)* / *(1.5.0)*.

## Índice

**Parte 1 — Pi**

1. [Instalación, autenticación, modos y modelos](#1-instalación-y-cli) — incl. [modelos locales en una GPU de 4 GB](#modelos-locales-llamacpp-ollama-lm-studio--y-una-gpu-de-4-gb)
2. [Memoria: AGENTS.md, SYSTEM.md y (sin) auto-memoria](#2-memoria)
3. [Permisos: ninguno por diseño](#3-permisos)
4. [Sesiones: un árbol en un fichero JSONL](#4-sesiones)
5. [Ventana de contexto y compactación](#5-ventana-de-contexto)
6. [Prompt caching](#6-prompt-caching)
7. [MCP (integrado desde la 0.99)](#7-mcp)
8. [Skills, plantillas de prompt y paquetes](#8-skills-y-paquetes)
9. [Subagentes: no integrados](#9-subagentes)
10. [Extensiones = hooks](#10-extensiones-hooks)
11. [Automatización: print, JSON, RPC, SDK, CI](#11-automatización)

**Parte 2 — La metodología**

12. [El flujo de trabajo y el ejemplo real](#12-metodología)
13. [Las herramientas: CodeGraph, Serena, GSD](#13-las-herramientas-del-método)
14. [Transferir la metodología (de Claude Code a Pi)](#14-transferir-la-metodología)
15. [Sincronización de máquinas (tarball + S3)](#15-sincronización-de-máquinas)

**Parte 3 — El grafo de conocimiento de tickets (graphify)**

16. [Grafo de conocimiento de tickets](#16-grafo-de-conocimiento-de-tickets)

**Apéndice**

- [A. Tabla de equivalencias: Claude Code → Cursor → Pi](#a-tabla-de-equivalencias-claude-code--cursor--pi)
- [B. Checklist de gotchas](#b-checklist-de-gotchas)
- [C. Fuentes](#c-fuentes)

---

# PARTE 1 — Pi

Qué es Pi, en un párrafo: un **agente de programación minimalista para terminal** ("AI agent toolkit: unified LLM
API, agent loop, TUI, coding agent CLI"), que empezó como `badlogic/pi-mono` de Mario Zechner, ahora
`github.com/earendil-works/pi`, con licencia MIT y mantenido por Earendil Inc. Trae un system prompt pequeño,
cuatro herramientas por defecto (`read`, `bash`, `edit`, `write`) y una API de extensiones en TypeScript — y
deliberadamente **omite** los popups de permisos, los subagentes y el modo plan. Su página principal llama a esa
lista "What we didn't build". Esa decisión de diseño condiciona cada sección siguiente.

> ⚠️ **El nombre y el paquete cambiaron.** `@mariozechner/pi-coding-agent` está deprecado (2026-05-07) en favor de
> **`@earendil-works/pi-coding-agent`**; el binario sigue siendo `pi`. Los tutoriales antiguos y los imports de
> extensiones usan el scope antiguo.

## 1. Instalación y CLI

```bash
curl -fsSL https://pi.dev/install.sh | sh                          # macOS/Linux; fija dependencias; luego: pi update
powershell -c "irm https://pi.dev/install.ps1 | iex"               # Windows
npm install -g --ignore-scripts @earendil-works/pi-coding-agent    # Node >= 22.19; NO fija dependencias transitivas
nix profile add github:earendil-works/pi/stable                     # Nix
pi --version                                                        # [TESTED] -> 1.5.0 (investigado en 1.3.0)

pi update              # Pi en sí       · pi update --extensions   # paquetes
pi update --models     # catálogo de modelos · pi update --all     # ambos
```

*(1.5.0)* Los wrappers u otros gestores de paquetes pueden encargarse de la auto-actualización con
`PI_SELF_UPDATE_COMMAND` / el ajuste `selfUpdateCommand`; tras una actualización, el siguiente arranque limpio muestra
los changelogs de las extensiones instaladas (`collapseChangelog` los condensa).

Desinstala con `npm uninstall -g @earendil-works/pi-coding-agent` o volviendo a ejecutar el instalador; ninguno de
los dos borra `~/.pi/agent/` (tus ajustes, sesiones y credenciales).

### Autenticación

```bash
cd my-project && pi
# dentro de Pi:
/login        # elige un proveedor: suscripción OAuth o API key -> se guarda en ~/.pi/agent/auth.json
/model        # elige un modelo
```

- **CI / scripts:** usa claves de entorno — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`, `XAI_API_KEY`, … (unos 40 proveedores).
- **Precedencia:** `--api-key` → `auth.json` → `apiKey` de `models.json` → entorno / credenciales cloud del entorno.
- **Gestor de secretos:** una clave en `auth.json` puede ser un comando, p. ej.
  `{"anthropic":{"type":"api_key","key":"!security find-generic-password -ws 'anthropic'"}}` (la salida se cachea
  durante la vida del proceso).
- **Bedrock** usa las credenciales AWS del entorno (`AWS_PROFILE`, access keys, `AWS_REGION`, credenciales de tarea
  ECS, IRSA). También están Vertex AI, Azure (`azure`), Cloudflare y la pasarela propia de Earendil **Radius**
  (`/login radius`, alfa temprana).
- **Suscripciones:** la documentación dice "a supported subscription → `/login`" pero no publica **ninguna lista** —
  **NOT DOCUMENTED**. Se mencionan: "Sign in with ChatGPT" para `openai`; un ajuste `warnings.anthropicExtraUsage`;
  y la página de contenedores que pasa un token de `claude setup-token` como `ANTHROPIC_OAUTH_TOKEN`.
- **Modelos locales:** ver la siguiente subsección.

### Modelos locales (llama.cpp, Ollama, LM Studio) — y una GPU de 4 GB

Dos rutas, ambas documentadas:

| Ruta | Cómo | Cuándo |
|---|---|---|
| **Proveedor llama.cpp integrado** | Arranca un **router** de llama.cpp (`llama serve` sin `-m`/`-hf`, por defecto `http://127.0.0.1:9931`), luego `/login llama.cpp` (o `LLAMA_BASE_URL`), `/llama` para cargar/descargar/bajar GGUFs de Hugging Face, `/model` para seleccionar | Máximo control; la ruta nativa de Pi |
| **`models.json`** (compatible con OpenAI) | Proveedor en `~/.pi/agent/models.json` con `baseUrl`, `api: "openai-completions"`, una `apiKey` ficticia y `models[]` (`id`, `contextWindow`, `maxTokens`, `reasoning`) — `/model` recarga el fichero | Ollama, LM Studio, vLLM, SGLang, cualquier proxy |

```json
{"providers":{"ollama":{"baseUrl":"http://localhost:11434/v1","api":"openai-completions","apiKey":"ollama",
  "models":[{"id":"qwen3.5:4b","contextWindow":32768,"maxTokens":8192,"reasoning":true}]}}}
```

**Pon en `contextWindow` el contexto real del servidor.** El valor por defecto de Pi es 128000; si Pi cree que la
ventana es mayor que la del servidor, la auto-compactación nunca se dispara y el servidor trunca en su lugar
(Ollama lo hace en silencio).

**GPU pequeña (4 GB de VRAM) — la recomendación del curso:** Pi + el router de llama.cpp + **Qwen3.5-4B** (`IQ4_XS`
~2,7 GB o `Q4_K_M` ~3,0 GB, `no-mmproj`, contexto de 16–32 K, caché KV en q8_0). Los modelos de 7–9 B no caben en
4 GB con un contexto usable. Reduce Pi para el modelo pequeño: `--tools read,bash,edit,write --no-mcp`, y
`compaction.modelOverrides` por modelo (`reserveTokens` ~6 K, `keepRecentTokens` ~8 K) más
`modelThinkingLevels: "off"` para que los modelos cloud mantengan sus valores por defecto. **[TESTED] en 1.5.0**
(servidor guionizado): con esos flags cada petición lleva 4 esquemas de herramientas (~2,8 K caracteres) y un system
prompt de ~2,3 K caracteres — unos **1,3 K tokens** de sobrecoste fijo, y por eso Pi encaja mejor con un modelo
pequeño que los agentes con prompts largos (Cline, Roo, OpenCode). Aider es la alternativa más fuerte (no necesita
tool calling nativo). Todo — preset, `models.json`, ajustes, tablas comparativas y un script de ensayo sin GPU —
está en [`examples/local-models/`](./examples/local-models/) ([versión en español](./examples/local-models/README_ES.md)).

### Modelos y thinking

| Dónde | Cómo |
|---|---|
| TUI | `/model` o `Ctrl+L` seleccionar · `Ctrl+P` rotar · `/scoped-models` · `/thinking` o `Shift+Tab` |
| CLI | `--model sonnet:high` (nombre aproximado + `:<thinking>`), `--provider`, `--thinking <level>`, `--models <patterns>`, `--list-models [search]` |
| Ajustes | `defaultThinkingLevel` (por defecto `"medium"`), `modelThinkingLevels`, `thinkingBudgets` |

Niveles de thinking: `off | minimal | low | medium | high | xhigh | max`, limitados a lo que soporte el modelo.
Las sesiones registran los cambios de modelo/thinking y los restauran al reanudar.

### Modos

| Modo | Comando | Notas |
|---|---|---|
| TUI interactiva | `pi` | Pantalla completa por defecto; `--tui-mode regular` mantiene el scrollback normal |
| Print | `pi -p "…"` | Imprime el texto final del asistente; **exit distinto de cero** en `error`, `aborted`, `length` |
| Eventos JSON | `pi --mode json "…" > events.jsonl` | Cabecera de sesión + eventos JSONL; una ejecución fallida **no** sale por sí sola con código distinto de cero |
| RPC | `pi --mode rpc [--no-session]` | Proceso de larga vida; comandos JSONL por stdin (`prompt`, `steer`, `follow_up`, `abort`, `get_state`, `compact`, `fork`, `set_model`, …) |
| SDK | `createAgentSession()` | En proceso, Node o Bun (§11) |

Piezas útiles: `@path` añade un fichero al primer prompt; el stdin por tubería se **antepone** al primer prompt;
`--` termina el análisis de opciones; en la TUI `!cmd` ejecuta un comando de shell y envía la salida al modelo,
`!!cmd` lo ejecuta sin enviarla.

> ⚠️ **Gotcha [TESTED]:** cuando stdin es una tubería que nunca se cierra (runners de CI, harnesses de agentes),
> `pi -p "…"` espera EOF y parece colgado. Siempre: `pi -p "…" </dev/null`.

---

## 2. Memoria

### Ficheros de contexto — cómo los encuentra Pi

| | Regla (del código fuente `resource-loader.ts`) |
|---|---|
| Global | `~/.pi/agent/` (o `$PI_CODING_AGENT_DIR`) |
| Proyecto | el directorio de trabajo **y cada directorio padre** hasta `/` |
| No se cargan | directorios **por debajo** del cwd — sin descubrimiento anidado de "el más específico gana" |
| Candidatos, por precedencia | `AGENTS.override.md` > `AGENTS.md` > `AGENTS.MD` > `CLAUDE.md` > `CLAUDE.MD` |
| Por directorio | **solo se carga el primer fichero existente** |
| Orden en el prompt | primero el global, luego los ancestros desde `/` hasta el cwd, cada uno envuelto en `<project_instructions path="…">` |
| Confianza | los ficheros de contexto se cargan **con independencia de la confianza del proyecto**; desactívalos con `-nc` / `--no-context-files` |

### Qué es distinto respecto a Claude Code y Cursor

| Característica | Claude Code | Cursor | Pi |
|---|---|---|---|
| Ficheros anidados en subdirectorios | sí (se cargan al trabajar allí) | sí, gana el más específico | **no** — solo ancestros |
| Reglas con ámbito (globs / rutas) | `.claude/rules/` | `.cursor/rules/*.mdc` | **ninguna nativa** |
| `@imports` dentro del fichero | sí | — | **NOT DOCUMENTED** — trata AGENTS.md como texto plano con punteros |
| Lee `CLAUDE.md` | sí | sí (compat) | sí, como **nombre de respaldo**; `AGENTS.md` en el mismo directorio **lo oculta** |
| Lee `~/.claude/CLAUDE.md` | sí | — | **no** — enlace simbólico o copia en `~/.pi/agent/` |
| Auto-memoria | `MEMORY.md` | Memories | **ninguna integrada** |

Consecuencias con las que te vas a encontrar:

- Un repo que tenga a la vez un `CLAUDE.md` (en gitignore) y un `AGENTS.md` le da a Pi **solo `AGENTS.md`**.
  Fusiónalos, o usa `AGENTS.override.md` a propósito ("replaces `AGENTS.md` or `CLAUDE.md` only in the same
  directory").
- **Fuga desde ancestros:** un `CLAUDE.md` a nivel de workspace por encima de tu repo se carga en cada sesión
  iniciada dentro del repo. Útil para convenciones compartidas; caro si es largo.
- Un **worktree** de git anidado no carga dos veces la copia del repo principal del mismo fichero.

### Sustitutos de las reglas con ámbito

1. Una **skill** cuya `description` nombre las rutas a las que aplica (se carga solo cuando es relevante, §8).
2. La **extensión de ejemplo** `claude-rules.ts` — lista `.claude/rules/*.md` en el prompt para leerlas bajo demanda.
3. `APPEND_SYSTEM.md` para las pocas reglas siempre activas.
4. Una **extensión** `before_agent_start` que inyecte el texto de la regla cuando coincidan las rutas tocadas (§10).

### Ficheros de system prompt

| Fichero | Efecto |
|---|---|
| `~/.pi/agent/SYSTEM.md` o `.pi/SYSTEM.md` | **Sustituye** el system prompt por defecto de Pi |
| `~/.pi/agent/APPEND_SYSTEM.md` o `.pi/APPEND_SYSTEM.md` | Lo **amplía** al final |
| `--system-prompt <text\|path>` / `--append-system-prompt <text\|path>` (repetible) | Equivalentes en CLI |

El fichero del proyecto de confianza gana sobre el del directorio del agente con el mismo nombre; los dos **no se
combinan**.

### Patrón de dos niveles (ver [`examples/agents-md/`](./examples/agents-md/))

```
~/.pi/agent/AGENTS.md          # nivel 1, global: quién eres, las reglas innegociables (el ~/.claude/CLAUDE.md de Pi)
<repo>/AGENTS.md               # nivel 1, proyecto: pequeño, punteros + orden de herramientas + contrato de salida
<repo>/data/changes/**         # nivel 2: detalle por ticket, se lee bajo demanda (sin cambios)
<repo>/data/changes/s3-sync/IDENTITY.md   # nivel 0: rol de la máquina, local a la máquina (sin cambios)
```

### Memoria entre sesiones

**No hay función de memoria integrada.** La página principal de Pi sitúa la memoria a largo plazo en las extensiones
("inject messages before each turn, filter the message history, implement RAG, or build long-term memory").
El sustituto de la metodología no necesita nada nuevo: registros de escritura única (`STATUS.md`, `FOLLOWUPS.md`,
`SHARP_EDGES.md`) + `pi -c` / `/resume` + los ficheros JSONL de sesión, que se pueden buscar con grep
(`PI_SESSION_FILE` se exporta a las herramientas de shell). [3rd-party]: `pi-memory`, `pi-hermes-memory`,
`pi-observational-memory` — sin probar.

---

## 3. Permisos

**Pi no tiene prompts de aprobación ni sandbox — a propósito.** Quickstart: "It does not ask before every
tool call." Página de seguridad: Pi "can read, change, and execute files with the permissions of the account
that started it". Página principal: **"No permission popups — Run in a container, or build your own confirmation
flow with extensions."** Su política de seguridad deja la "lack of a built-in sandbox" y el prompt injection
**fuera de alcance**.

### Lo que existe en su lugar — cinco capas

| # | Capa | Qué controla | Cómo |
|---|---|---|---|
| 1 | **Confianza del proyecto** | Si se cargan los *recursos* de una carpeta (`.pi/settings.json`, `.pi/mcp.json`, `.pi/extensions\|skills\|prompts\|themes`, `.pi/SYSTEM.md`, `.agents/skills`) | `/trust`, guardado en `~/.pi/agent/trust.json`; `defaultProjectTrust: "ask" \| "always" \| "never"` (solo en ajustes de usuario; por defecto `"ask"`). **No aísla las llamadas a herramientas**; los ficheros de contexto se cargan igualmente. |
| 2 | **Restricción estática de herramientas** (por *nombre*) | Qué herramientas existen | `--tools read,grep,find,ls` (allowlist) · `--exclude-tools` · `-nbt` / `-nt` · `defaultTools` con `+name` / `-name` · MCP `exposure: "hidden"` / `toolExposure` |
| 3 | **Puertas de contenido** | Qué puede hacer una llamada | Extensiones: `pi.on("tool_call") → { block: true, reason }` (§10). Ejemplos incluidos: `permission-gate.ts` (confirma `rm -rf`, `sudo`, `chmod 777`; **bloquea por defecto sin UI**), `protected-paths.ts`, `confirm-destructive.ts`, `dirty-repo-guard.ts`, `plan-mode/`. *(1.5.0)* El ejemplo de sandbox nativo del SO `sandbox/` se **eliminó** — usa la capa 4 |
| 4 | **Aislamiento** | El radio de impacto de todo | Docker simple (monta solo el workspace, **nunca** el `~/.pi/agent` del host) · Docker Sandboxes (`sbx run --kit "docker.io/sbx/pi-kit:latest" pi`; la clave real se queda en el host) · NVIDIA OpenShell · extensión de micro-VM Gondolin (herramientas integradas + `!` en una VM; el proceso de Pi y las herramientas de otras extensiones se quedan en el host) |
| 5 | **El método** | Qué se le pide al agente | Reglas de AGENTS.md; el humano es dueño de las acciones externas |

Un handler de `tool_call` que **lanza una excepción** bloquea la herramienta — "as a fail-safe".

### Modos no interactivos y confianza

Los modos print, JSON y RPC **no pueden mostrar el prompt de confianza**. Con el valor por defecto `"ask"`, los
recursos `.pi/` del proyecto — incluidos `.pi/mcp.json` y `.pi/extensions` — se **omiten en silencio** salvo que
pases `--approve` / `-a` (o `--no-approve` / `-na` para hacer explícita la decisión). Los recursos globales de
`~/.pi/agent/` se siguen cargando. Gotcha: el ajuste de proyecto `sessionDir` se lee *antes* de resolver la
confianza.

### Comparado con Claude Code y Cursor

```
Claude Code   settings.json allow/deny (mcp__s__t, Bash(…)) + prompts + sandbox opcional
Cursor        permissions.json mcpAllowlist / terminalAllowlist + aprobaciones + hooks.json
Pi            sin prompts, sin fichero de allowlist -> confianza (recursos) + --tools/defaultTools (nombres)
              + extensiones (contenido) + contenedores (radio de impacto)
```

No busques la allowlist. Reimplementa la **política**: `block-external-git.ts` global
([`examples/extensions/`](./examples/extensions/)), `--tools` sin `edit`/`write` para sesiones de revisión,
`exposure: "hidden"` para herramientas MCP destructivas, un contenedor para cualquier cosa desatendida. Notas
prácticas: [`examples/permissions/`](./examples/permissions/). Opciones [3rd-party]: `@gotgenes/pi-permission-system`,
`pi-permission-modes` (bubblewrap/sandbox-exec + allow/ask/deny + filtrado por AST de bash), `@czottmann/pi-automode`,
`@erichll/pi-auto-review`.

---

## 4. Sesiones

| Tema | Pi |
|---|---|
| Almacenamiento | `~/.pi/agent/sessions/--<path>--/<timestamp>_<session-id>.jsonl` (`<path>` = cwd con `/`, `\`, `:` → `-`) |
| Cambiar ubicación | `--session-dir` > `PI_CODING_AGENT_SESSION_DIR` > ajuste `sessionDir`; `--no-session` = efímera |
| Formato | **Árbol** JSONL: las entradas llevan `id` + `parentId`; cabecera `version` 3; los tipos de entrada incluyen mensajes, cambios de modelo/thinking, `compaction`, `branch_summary`, `custom`, `context_edit`, `usage` |
| Reanudar | `pi -c` (la última de este cwd) · `pi -r` / `/resume` (selector: buscar, renombrar, `Ctrl+D` borrar) · `--session <path\|id>` · `--session-id` · `-n` / `/name` · `/session` (fichero, ID, contadores, tokens, coste) · `/new` |
| Ramificar | `/tree` (moverse dentro del mismo fichero; puede resumir la rama que dejas) · `/fork` (nueva sesión desde un mensaje de usuario anterior) · `/clone` (copia la rama activa) · `--fork <path\|id>` · Esc-Esc = `/tree` por defecto (`doubleEscapeAction`) |
| Exportar / compartir | `/export [path]` (HTML o JSONL) · `pi --export <file> [out]` (HTML) · `/import <path>` · `/share` (artefacto Radius si estás autenticado; si no, un gist privado de GitHub vía `gh`; `sessionShareDestination: auto \| gist \| radius`, nuevo en 1.3.0) · `/bug` · `/copy` / `Ctrl+X` |
| Traspaso | Sin traspaso entre superficies (no hay `--teleport`). Extensión de ejemplo `handoff.ts`: `/handoff <goal>` mueve el contexto a una nueva sesión enfocada |

Las herramientas de shell reciben `PI_SESSION_ID`, `PI_SESSION_FILE`, `PI_PROVIDER`, `PI_MODEL`, `PI_REASONING_LEVEL`.

> ⚠️ `/share` sube una transcripción. En un proyecto de cliente, las sesiones contienen todo lo que leyó el
> agente — trata `/share` como cualquier otra acción hacia fuera: decide el humano, después de sanear.

---

## 5. Ventana de contexto

- El pie de la TUI muestra el uso de contexto.
- La **auto-compactación** se dispara cuando `contextTokens > contextWindow - reserveTokens`; también se comprueba
  entre lotes de herramientas dentro de una ejecución, y hay un compactar-y-reintentar en caso de desbordamiento.
- **Manual:** `/compact [instructions]` — las instrucciones enfocan el resumen. Desactivar la automática no
  desactiva el comando manual.

```json
{
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "branchSummary": { "reserveTokens": 16384, "skipPrompt": false }
}
```

(`compaction.modelOverrides` fija valores por `provider/modelId` — p. ej. presupuestos menores para un modelo
local de 32 K.)

*(1.4.0)* `reserveTokens` ahora **solo decide cuándo empieza la compactación**; la propia petición de resumen usa el
límite de salida del modelo (`maxTokens`), reducido cuando hace falta para que entrada y salida quepan en la
ventana. Así que el `maxTokens` de un modelo local en `models.json` importa.

**Cómo funciona:** los mensajes antiguos se resumen en una `CompactionEntry` (`summary`, `firstKeptEntryId`,
`tokensBefore`, `details.readFiles/modifiedFiles`); las entradas originales **se quedan en el fichero**. El resumen
está estructurado: Goal / Constraints & Preferences / Progress / Key Decisions / Next Steps / Critical Context.
Las peticiones de resumen **desactivan las escrituras de prompt cache**.

Hooks de extensión: `session_before_compact` (cancelar, o aportar tu propio resumen), `session_compact`,
`session_compact_failed`, `session_before_tree`. Ejemplos: `custom-compaction.ts`, `trigger-compact.ts`.

### Mantener el contexto ligero — las palancas propias de Pi

| Palanca | Efecto |
|---|---|
| System prompt pequeño por defecto + 4 herramientas por defecto | Coste fijo bajo por turno |
| Skills | Solo nombre + descripción + ruta hasta que se usan |
| MCP `codemode` (por defecto) | Las herramientas **no** se declaran; un resumen de una línea por servidor en `mcp_servers`; `tool_search` / `deferred` cargan bajo demanda |
| Scripts de codemode | Filtran salidas grandes antes de que las vea el modelo |
| Resultados de texto MCP > 20 KB | Truncados por el medio; el texto completo se guarda en un fichero temporal |
| `/tree`, `/fork` | Desvíos fuera de la rama principal |
| `--no-context-files`, `--no-skills`, `--no-extensions` | Ejecuciones mínimas |

Notas prácticas: [`examples/context/`](./examples/context/).

---

## 6. Prompt caching

**Lo que Pi hace automáticamente:**

- Las peticiones en formato Anthropic reciben marcadores `cache_control` en el system prompt, la última definición
  de herramienta y el último texto de usuario / asistente / resultado de herramienta.
- Las peticiones de estilo OpenAI reciben afinidad de sesión y gestión de `prompt_cache_key`; para retención larga
  Pi envía `prompt_cache_retention: "24h"` (o `prompt_cache_options.ttl: "30m"` en GPT-5.6+).

**Lo que controlas tú:**

| Control | Efecto |
|---|---|
| `PI_CACHE_RETENTION=long` | Retención extendida donde se soporte (p. ej. Anthropic `cache_control.ttl: "1h"`) |
| `cacheWarming: "off" \| "streaming" \| "idle"` | Por defecto `"streaming"`, **solo global**. Mantiene calientes las cachés elegibles durante ejecuciones largas (`idle`: entre ejecuciones). Solo actúa si el modelo declara una vida `promptCache` y el ahorro estimado es ≥ 0,05 $; el uso de calentamiento cuenta en los totales. Las extensiones pueden sobrescribirlo vía `cache_warming_decision`. |
| `showCacheMissNotices: true` | Avisos de fallos de caché, calentamientos y uso de compactación |
| `/session` | Muestra la siguiente decisión de calentamiento de caché |
| `promptCache: {"short": 300, "long": 3600}` en `models.json` | Vida por modelo (+ campos de compatibilidad `supportsLongCacheRetention`, `supportsExplicitPromptCacheMode`, `sessionAffinityFormat`) |

**Decisiones de diseño que protegen la caché:** los cambios de prompt/herramientas a mitad de conversación se
**añaden** como deltas de transcripción, no se reescriben; los resúmenes de servidores MCP que cambian tras conectar
se añaden "so earlier messages stay cached"; **cambiar de modelo pierde la caché**; desde la 1.3.0 un cambio de
nivel de thinking conserva la caché en OpenAI GPT-6 con API key. Campos de uso: `cacheRead`, `cacheWrite`,
`cacheWrite1h`.

El mecanismo en sí (caché de prefijo, TTLs, punto de equilibrio) está del lado del proveedor — la demo de
[`examples/prompt-caching/`](./examples/prompt-caching/) lo muestra directamente contra la API de Anthropic.

---

## 7. MCP

> ⚠️ **Gotcha del curso — la web está desactualizada.** La postura original de Pi era "does not and will not
> support MCP". Desde la **0.99.0 (2026-09-29)** MCP está **integrado** ("Added codemode, tool search, and MCP
> support as built-in extensions"); la tarjeta de pi.dev ahora dice "No MCP → Now with MCP+Codemode". Mucho
> material online sigue diciendo "Pi has no MCP".

### Configuración

| | |
|---|---|
| Ficheros | `~/.pi/agent/mcp.json` (usuario) · `.pi/mcp.json` (proyecto, **solo proyectos de confianza**) |
| Forma | el mismo objeto `mcpServers` que Claude Code y Cursor ("Copy the existing `mcpServers` entry") |
| Fusión | una entrada de proyecto con el mismo nombre sustituye a la de usuario; una entrada sin `command`/`url`/`type` solo sobrescribe `enabled`, `exposure`, `toolExposure` |
| Transportes | stdio (`command`, `args`, `env`, `cwd`) · streamable HTTP (`url`, `headers`, `oauth`) · **SSE rechazado** |
| Campos | `timeout`, `enabled`, `description`, `exposure`, `toolExposure`; los valores admiten `${VAR}` y `!command` |
| Nombres de herramientas | `mcp__<server>__<tool>` (igual que Claude Code) |
| Logs / tokens | `~/.pi/agent/mcp.log` · `~/.pi/agent/mcp-auth.json` |

```bash
pi mcp add codegraph --description "Code intelligence" -- codegraph serve --path /abs/path/to/repo --mcp   # [TESTED]
pi mcp add docs --url https://example.com/mcp --bearer-token-env-var DOCS_TOKEN
pi mcp list            # [TESTED] -> codegraph: connected, 1 tool (codemode, global) … tools: codegraph_explore
pi mcp list --json     # sale con 1 si falla — sirve como puerta de disponibilidad en CI
pi mcp login <name>    # OAuth;  pi mcp logout | remove
/mcp                   # en la TUI
```

(En la 1.3.0 la sinopsis de `--help` solo listaba `list|login|logout`; *(1.5.0)* ahora lista también `add` y
`remove` **[TESTED]**.) *(1.5.0)* Los servidores OAuth usan por defecto `oauth.clientRegistration: "auto"` (Client ID
Metadata Document cuando se soporta, registro dinámico si no; `"dcr"` siempre registra); `pi mcp add
--oauth-client-registration` lo fija. Los argumentos de herramientas MCP reciben ahora la misma coerción que las
herramientas integradas (cadenas numéricas → números, un valor suelto → array).

### Modos de exposición — la decisión que importa

| Modo | Significado | Úsalo para |
|---|---|---|
| `codemode` (**por defecto**) | Solo invocable desde scripts JavaScript de `codemode` (sandbox QuickJS); **no se declara** como herramienta | Servidores grandes que rara vez necesitas |
| `deferred` | Se carga bajo demanda mediante `tool_search` | Playwright, Context7 |
| `direct` | Se declara como una herramienta integrada | Las herramientas que el método quiere que se usen **sin pedirlo** |
| `hidden` | Inalcanzable | Herramientas destructivas |

`toolExposure` fija esto **por herramienta**, con globs. El mapa de disparadores de la metodología
("`codegraph_explore` primero; Serena `find_referencing_symbols` antes de renombrar") solo funciona si esas
herramientas son visibles:

```json
{
  "mcpServers": {
    "codegraph": {
      "command": "codegraph", "args": ["serve", "--path", "/abs/path/to/repo", "--mcp"],
      "description": "Code intelligence: verbatim source + call paths + blast radius",
      "toolExposure": { "codegraph_explore": "direct" }
    },
    "serena": {
      "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
      "toolExposure": { "find_symbol": "direct", "find_referencing_symbols": "direct", "get_symbols_overview": "direct" }
    },
    "playwright": { "command": "npx", "args": ["-y", "@playwright/mcp@latest"], "exposure": "deferred" },
    "context7":   { "url": "https://mcp.context7.com/mcp", "exposure": "deferred" }
  }
}
```

CodeGraph está **[TESTED]**; los args de Serena / Playwright / Context7 están copiados de la guía de Cursor y
**no se han probado con Pi**. No hay documentada ninguna variable estilo `${workspaceFolder}` — usa una ruta absoluta
(o `cwd`, que se resuelve relativa al directorio de la sesión).

### Puertas, filtrado, alternativas

- Cada llamada MCP, **incluidas las de los scripts de codemode**, pasa por los handlers de extensión `tool_call` /
  `tool_result` — tus puertas aplican. Las anotaciones MCP (`readOnlyHint`, …) están disponibles para ellos.
- `--tools` conserva las herramientas MCP salvo que una entrada empiece por `mcp__`; `--exclude-tools 'mcp__*'` y
  `--no-mcp` las quitan; `"extensions": ["-builtin:mcp"]` desactiva por completo el MCP integrado.
- **Las sesiones del SDK no cargan el MCP integrado** (§11).
- Alternativas: [3rd-party] `pi-mcp-adapter` (sustituye al integrado cuando se instala); wrappers de herramientas
  nativas [3rd-party] `@henryqw/pi-codegraph`, `@vndv/pi-codegraph`, `@bacnh85/pi-serena`; o el consejo original de
  Pi — una CLI más un README o una skill.

Listo para copiar: [`examples/mcp/`](./examples/mcp/) y
[`docs/ai-agents-code-methodology/pi/mcp.json.example`](./docs/ai-agents-code-methodology/pi/mcp.json.example).

---

## 8. Skills y paquetes

### Skills — el estándar Agent Skills

| Tema | Pi |
|---|---|
| Formato | un directorio con `SKILL.md` (+ `scripts/`, `references/`, `assets/` opcionales) — especificación de agentskills.io |
| Ubicaciones | `~/.pi/agent/skills/`, `.pi/skills/` (de confianza) · `~/.agents/skills/`, `.agents/skills/` (cwd y ancestros hasta la raíz del repo; sujetos a confianza) · el ajuste `"skills"` · `--skill <path>` · paquetes. El descubrimiento es recursivo. |
| `.claude/skills` | **No se descubre automáticamente**, pero se puede añadir: `"skills": ["~/.claude/skills"]` cargó todas las skills de Claude del autor **[TESTED]** — y volcó todas sus descripciones en el prompt. Lista los directorios uno a uno. |
| Frontmatter | `name`, `description` (**obligatoria**, ≤ 1024 caracteres, guía la carga automática), `license`, `compatibility`, `metadata`, `allowed-tools` (experimental), `disable-model-invocation: true` |
| Nombres | minúsculas `a-z0-9-`, ≤ 64 caracteres, sin guiones al principio/final ni dobles. Colisión → **gana la primera encontrada**, con aviso. Sin descripción → no se carga. |
| Claves desconocidas | **se ignoran en silencio** **[TESTED]** — una clave solo de Claude `trigger: /day` carga bien y no hace nada |
| Invocación | automática: el modelo hace `read` de `SKILL.md` cuando la descripción encaja · forzada: **`/skill:name [args]`** (los args se añaden como la petición) · `enableSkillCommands` (por defecto `true`) controla el autocompletado con `/` |
| Requisito | debe estar habilitada una herramienta de lectura de ficheros |

```bash
/skill:audit                   # invocación forzada
/skill:day start               # args después del nombre
pi --skill ./examples/skills-plugins/.pi/skills/day "start the day"
```

En vivo en este repo: [`.pi/skills/`](./.pi/skills/) (`audit`, `audit-python`, `deploy-staging`), contra los
objetivos de demo [`ex_npm/`](./ex_npm/), [`ex_app/`](./ex_app/), [`ex_staging/`](./ex_staging/). Las skills reales
de la metodología (`day`, `atlassian`, `evidence`, `preview`) están en
[`examples/skills-plugins/`](./examples/skills-plugins/), y sus herramientas en
[`examples/methodology/tools/`](./examples/methodology/tools/).

### Plantillas de prompt — los slash commands de Pi

`~/.pi/agent/prompts/<name>.md` o `.pi/prompts/<name>.md` se convierte en `/<name>`. Frontmatter: `description`,
`argument-hint`. Argumentos: `$1`, `$@`, `$ARGUMENTS`, `${1:-default}`, `${@:N}`, `${@:N:L}`. Solo se cargan los
hijos `.md` directos. Es lo más parecido a `.claude/commands/`.

```markdown
---
description: Run the day routine
argument-hint: start|end|status|baton
---
Run the day skill: $@
```

(Usar una plantilla para conservar la memoria muscular de `/day` es una **inferencia**, no un patrón documentado.)

### Paquetes — el marketplace de Pi

```bash
pi install npm:@scope/pkg@1.0.0     # o git:github.com/u/r@v1 | https://… | ./local ;  -l / --local = ámbito de proyecto
pi list · pi remove <pkg> · pi update --extensions · pi config      # pi config = TUI para activar recursos e integrados
pi -e npm:pkg                       # probar un paquete en una sola ejecución
```

Un paquete es un directorio npm o git con `extensions/`, `skills/`, `prompts/`, `themes/` (o un manifiesto
`"pi": {…}` en `package.json`); la palabra clave `pi-package` lo lista en la **galería <https://pi.dev/packages>**
(5.354 paquetes el 2026-10-17). Los paquetes anfitriones (`@earendil-works/pi-ai`, `-agent-core`, `-coding-agent`,
`-tui`, `typebox`) van en `peerDependencies: "*"`. Los paquetes de proyecto solo se instalan tras la confianza.

> ⚠️ Los paquetes se ejecutan **en proceso con todos los permisos del SO** (son extensiones). Lee antes de instalar,
> fija versiones y prefiere el ámbito de proyecto para experimentos.

---

## 9. Subagentes

**No integrados — por diseño.** README: Pi "skips features like sub-agents and plan mode". Página principal: "No
sub-agents — Spawn Pi instances via tmux, or build your own with extensions, or install a package."

### Opción A — la extensión de ejemplo oficial

`examples/extensions/subagent/` en el repo de Pi:

- cada subagente es un **subproceso** `pi` separado con un contexto aislado;
- modos: individual `{agent, task}` · paralelo `{tasks:[…]}` (máx. 8, 4 concurrentes) · cadena `{chain:[…]}` con un
  marcador `{previous}`;
- definiciones de agente: Markdown con frontmatter `name`, `description`, `tools`, `model`;
- ubicaciones: `~/.pi/agent/agents/*.md` siempre; `.pi/agents/*.md` solo con `agentScope: "project" | "both"`;
- muestras `scout` (read, grep, find, ls, bash; Haiku), `planner`, `reviewer`, `worker`; prompts de flujo
  `/implement`, `/scout-and-plan`, `/implement-and-review`;
- instalación: copia o enlace simbólico en `~/.pi/agent/extensions/subagent/`.

Un subagente de **solo lectura** es un fichero de agente con `tools: read, grep, find, ls` — sin `bash`, `edit`,
`write` (ojo: el `scout` incluido *sí* tiene `bash`):

```markdown
---
name: refactor-scout
description: Read-only blast-radius survey before a rename or delete
tools: read, grep, find, ls
---
Survey every reference to the symbol you are given. Report files, call sites and risk. Never edit.
```

### Opción B — procesos hijos desechables (solo flags documentados)

```bash
pi -p --no-session --tools read,grep,find,ls "List every caller of parse_header and rate the risk" </dev/null
```

### Opción C — paquetes y tmux

[3rd-party] `pi-subagents` (delegación a un agente y flujos multiagente guionizados) y su fork
`@schovest/pi-subagents`; o instancias `pi` en paralelo en paneles de tmux / procesos RPC. **Sin Agent Teams ni
bandeja compartida** — NOT DOCUMENTED.

Plantillas y el diagrama de decisión: [`examples/subagents/`](./examples/subagents/).

---

## 10. Extensiones (hooks)

Los hooks de Pi no son un fichero JSON de comandos de shell — son **extensiones en TypeScript**.

| Tema | Pi |
|---|---|
| Dónde | `~/.pi/agent/extensions/*.ts` o `<dir>/index.ts` · `.pi/extensions/` (de confianza) · ajuste `extensions` · `-e` / `--extension <path \| npm:… \| builtin:mcp>` |
| Compilación | ninguna — se cargan con `jiti`; `/reload` recarga en caliente |
| Poder | **en proceso, todos los permisos del SO**; se cargan en todos los modos (comprueba `ctx.hasUI`, `ctx.mode === "tui"`) |
| Forma | `export default function (pi: ExtensionAPI) { … }` (puede ser async); los recursos de larga vida arrancan en `session_start` y se limpian en `session_shutdown` |
| Bloquear una herramienta | devuelve `{ block: true, reason }` desde `tool_call` (opcional `terminate: true`) |
| Fail-safe | un fallo en un handler de `tool_call` **bloquea** la herramienta |

### Eventos (de `extensions/types.ts`)

| Familia | Eventos |
|---|---|
| Sesión / ejecución | `session_start`, `session_shutdown`, `session_before_switch`, `session_before_fork`, `session_before_compact`, `session_compact`, `session_compact_failed`, `session_before_tree`, `session_tree`, `session_info_changed`, `project_trust`, `resources_discover`, `input`, `before_agent_start`, `agent_start`, `turn_start`, `turn_end`, `agent_end`, `agent_before_settle`, `agent_settled` |
| Mensajes | `message_start`, `message_update`, `message_end` |
| Contexto / proveedor | `context`, `context_with_system`, `before_provider_headers`, `before_provider_request`, `after_provider_response`, `provider_stream_event` |
| Herramientas | **`tool_call`** (mutar `event.input` o bloquear), `tool_execution_start`, `tool_execution_update`, `tool_execution_end`, **`tool_result`** (reescritura componible), **`user_bash`** (los comandos `!` del propio humano) |
| Otros | `model_select`, `thinking_level_select`, `mcp_servers_change`, `cache_warming_decision`, `ui_prompt_start`, `ui_prompt_end` |

Las llamadas anidadas (`ctx.executeTool`, scripts de codemode, MCP) también pasan por `tool_call`.

### La puerta de la metodología — [TESTED] en 1.3.0 y 1.5.0

[`examples/extensions/block-external-git.ts`](./examples/extensions/block-external-git.ts) (también en vivo en
[`.pi/extensions/`](./.pi/extensions/)):

```typescript
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
```

**Cómo se probó:** un servidor falso compatible con OpenAI guionizó dos llamadas bash (`git push origin main`,
luego `echo allowed-ok`); `pi -p --no-session --model fake/fake-1 -e block-external-git.ts "push it" </dev/null`.
Con la extensión el modelo recibió "Blocked by policy…" y el echo se ejecutó igualmente. **Ejecución de control
sin ella:** el push se ejecutó de verdad (y falló en un repo vacío de pruebas) — prueba de que lo paró la puerta, no
el entorno. Esa ejecución de control es la regla de "canary the instrument" de la Parte 2, aplicada.
**Repetido en 1.5.0 (2026-11-06)** con el mismo resultado — reproducible con
[`examples/local-models/verify/run.sh`](./examples/local-models/verify/run.sh).

Instálala **globalmente** (`~/.pi/agent/extensions/`): las extensiones globales no dependen de la confianza, así que
un repo no puede desactivar la puerta. Deja `user_bash` en paz — el humano es dueño de los pushes, incluido
`!git push`.

> **Límite:** el filtrado por regex se puede saltar (`sh -c`, alias, scripts). Para puertas más fuertes usa
> aislamiento del SO o [3rd-party] `pi-permission-modes` (AST de bash con tree-sitter). La misma advertencia aplica
> a los hooks de Cursor y de Claude Code.

### `hooks.json` de Cursor → eventos de Pi

```
beforeShellExecution        -> tool_call (toolName "bash"/"powershell")
beforeMCPExecution          -> tool_call (toolName "mcp__server__tool"; anotaciones MCP disponibles)
beforeReadFile              -> tool_call (toolName "read")
afterFileEdit               -> tool_result / tool_execution_end
stop                        -> agent_end / agent_settled
(sin equivalente)           -> before_agent_start (reescribir secciones del prompt), context, user_bash
```

Otra superficie de la API: `pi.registerTool({ name, label, description, parameters: Type.Object(…), execute(…) })`
(TypeBox), `pi.registerCommand`, `registerShortcut`, `registerFlag`, `sendUserMessage`, `sendMessage`,
`appendEntry`, `setActiveTools`, `registerProvider`, `registerMcpServer`, `registerVirtualModel`,
`registerToolRenderer`, `pi.events`; UI vía `ctx.ui.confirm`, `select`, `input`, `notify`, `setStatus`,
`setWidget`, `custom`. Más patrones: [`examples/extensions/`](./examples/extensions/).

*(1.5.0, cambio incompatible)* Los argumentos de herramientas se validan con `@earendil-works/pi-schema`: las
funcionalidades de TypeBox fuera de JSON Schema (`Type.Refine()`, `Type.BigInt()`, `Type.Undefined()`, codecs,
`Format.Set()`) ya no aplican a los argumentos de herramientas, y los errores de validación llegan al modelo en el
formato de pi-schema. `pi.exec()` gana `maxBuffer` y un campo de resultado `truncated`.

---

## 11. Automatización

### Modo print en CI

```bash
pi -p --no-session --approve --model anthropic/<id> "review the diff" </dev/null
```

- Clave desde el entorno, no desde `auth.json`. Exit distinto de cero en error, abort o length.
- `--approve` (o `--no-approve`) porque el modo print no puede responder al prompt de confianza — sin él, los
  recursos `.pi/` del proyecto se omiten en silencio.
- `</dev/null` porque una tubería de stdin que nunca se cierra cuelga `pi -p` **[TESTED]**.
- Puerta de disponibilidad: `pi auth check --provider X --json` sale con 0, 1 o 2.
- Ejecuciones deterministas: `PI_OFFLINE=1`, `PI_SKIP_VERSION_CHECK=1`, `PI_TELEMETRY=0`.

### Modo JSON

```bash
pi --mode json "summarise the failing test" </dev/null > events.jsonl
```

Monta el texto a partir de los deltas de `message_update`; `message_end` es el autoritativo; `agent_settled` marca
el fin del trabajo automático. Divide solo por LF (no uses `readline` de Node). ⚠️ **El modo JSON no sale con código
distinto de cero en una ejecución fallida o abortada** — inspecciona los eventos.

### RPC

`pi --mode rpc` — un proceso de larga vida; comandos JSONL por stdin, respuestas y eventos por stdout. En
TypeScript es preferible `RpcClient` (de `@earendil-works/pi-coding-agent`, con `promptAndWait()`). Los diálogos de
las extensiones se reenvían mediante el subprotocolo extension-UI de RPC.

### SDK

```ts
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();   // options: cwd, agentDir, model, thinkingLevel, tools, excludeTools,
await session.prompt("List the TODOs in src/");    // customTools, resourceLoader, sessionManager (SessionManager.inMemory()), settingsManager
console.log(session.getLastAssistantText());
session.dispose();
```

`session.subscribe(ev => …)`, `steer()`, `followUp()`, `abort()`, `waitForIdle()`.
⚠️ **Las sesiones del SDK no cargan el MCP integrado ni codemode.** Añade `createMcpExtension()`,
`createCodemodeExtension()`, `createToolSearchExtension()` mediante
`DefaultResourceLoader({ extensionFactories })` y llama a `session.bindExtensions()`. Pi incluye 14 ejemplos con
comprobación de tipos en `examples/sdk/`.

### GitHub Actions / programación

**NOT DOCUMENTED** — no hay action oficial ni revisor estilo Bugbot. El curso incluye un **patrón** (sin probar):
[`examples/automation/github-action-pi.yml`](./examples/automation/github-action-pi.yml) — instala una versión fijada
de `@earendil-works/pi-coding-agent` con `--ignore-scripts`, ejecuta el comando en modo print de arriba, y deja la
publicación del resultado como un paso separado controlado por un humano. Programación: nada integrado — cron, CI
o `systemd` con `pi -p`. Rebranding de forks: `"piConfig": {"name", "configDir"}`.

---

# PARTE 2 — La metodología

## 12. Metodología

Todo el material de fondo (flujo de 11 etapas, ejemplo real de principio a fin, precedencia de herramientas) está en
[`examples/methodology/`](./examples/methodology/). Resumen:

### El flujo real (ver [`methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md))
Agente = colaborador disciplinado; la autonomía se gana decisión a decisión. 11 etapas encadenadas por **puertas
deterministas**: orientarse (`/skill:kg` + historial + estado) → triaje de entrada contra el **contrato de salida** →
regresión frente a preexistente → investigar con un **oráculo determinista** (antes de la llamada de pago al LLM) →
**fichero de plan** + acuerdo (Pi no tiene modo plan; la puerta es el "sí" del humano) → TDD RED→GREEN → verificar
(unitarios + acotados + regresión + contrato vía el *wrapper* Y dentro de la imagen desplegada) → documentar →
**sanear** (`/skill:sanitise-diff` sobre las líneas añadidas) → traspaso (el agente **no** hace push/PR/deploy salvo
que se le pida explícitamente — extensión global `block-external-git.ts` + AGENTS.md; lo hace el humano) → revisión +
persistir (`/skill:kg-refresh` si aplica — ver la advertencia de §16).
Diagrama: [`methodology/flow.png`](./examples/methodology/flow.png) (fuente `flow.mmd`, render
`render_flow.py`). Caso concreto de principio a fin:
[`methodology/REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

> **La puerta de salida son CINCO comprobaciones** (no solo "pasan los tests"):
> **(0) valida el instrumento de medida antes de fiarte de él** — cualquier `_diag_*`/`_sweep_*` que informe una
> decisión de envío se ejecuta primero contra un **caso de respuesta conocida**, y ese resultado se registra junto al
> hallazgo; nunca envuelvas la medición en tu propio `try/except → return False`;
> (1) reproduce en la **etapa de salida real** — el *wrapper* que reconstruye el contrato, no una función interna
> `extract()`; (2) el JSON local cumple el contrato, y **se verifica sobre la LISTA de miembros, nunca sobre un
> total**; (3) verifícalo **dentro de la imagen desplegada** (descarga/construye la imagen de runtime, monta el `src`,
> vuelve a ejecutar); (4) **mira la salida** renderizada, a ojo, antes del PR — para cambios de geometría/resaltado,
> los artefactos antes/después son **obligatorios**.
> Los tests en verde no son prueba de lo que se despliega. Idéntica en función a la puerta de Claude Code y Cursor —
> solo cambia qué agente la ejecuta.
>
> **Cinco formas en que una puerta en verde no prueba nada** — las cinco nos han mordido:
> **Instrumento roto.** Saltarse el constructor para sondear un predicado barato deja sin asignar todos los atributos
> que no se te ocurrió asignar; si el método lee uno y tiene su propio `try/except`, el error se traga y vuelve como un
> `False` plausible. La sonda informa entonces un "no" seguro y uniforme para **todos** los casos. Canario contra una
> respuesta conocida, siempre.
> **Un total que cuadra.** Un recuento que cae en lo esperado **no** es un test superado: un elemento añadido por error
> y otro quitado por error se cancelan exactamente. Afirma sobre **títulos/ids**, no sobre `len(...)`; y cuando la
> corrección tiene una dirección conocida, mide un **delta** contra una línea base (ganados/perdidos), no dos totales.
> Cuanto más se acerque un número al esperado, **más** sospechoso debería resultar, no menos.
> **Una puerta que no podía fallar.** Si el corpus de referencia no contiene ningún ejemplo positivo de la forma que
> acabas de tocar, la ejecución limpia prueba **la no-regresión y nada más**. Dilo explícitamente, y nombra qué aporta
> en su lugar la evidencia de corrección. (Caso real: un detector que salta en **0 de 190** documentos del corpus —
> `fires=0` se lee igual tanto si el código es correcto como si está completamente roto.)
> **Un canario que nunca aplicó la perturbación real.** El instrumento puede ser impecable y aun así no probar nada,
> porque lo que hace a los datos **no es lo que hace producción**. Caso real: el test sintético renombró los
> *contenedores* y alteró el 4% de los elementos, recuperó el **100%** del mapeo y se dio por "verificado"; la
> reconstrucción real cambió algo que el test nunca tocó — los **identificadores de los propios elementos**, el 88% de
> ellos — y la recuperación cayó por debajo del **1%**. Antes de fiarte de un canario en verde, di en una frase *qué
> le hace producción a estos datos* y comprueba que el canario hace lo mismo. Si no puedes, la puerta está **sin
> probar**: "el test que pude construir pasó" no es "el riesgo está retirado".
> **Una puerta estructural leída como semántica.** Comprobar que todo está presente, es único y está bien conectado no
> dice **nada** sobre si algo de ello es *correcto*. Caso real: una migración informó un estado de salud impecable —
> todos los grupos emparejados, ninguno perdido, cero huérfanos — mientras el **56%** de los nombres trasladados no
> describían aquello a lo que estaban asociados, porque el emparejamiento había recurrido a un proxy superficial. Un
> nombre erróneo es **peor** que uno ausente: el ausente plantea una pregunta, el erróneo la responde mal y manda a la
> siguiente persona al sitio equivocado. Cuando la corrección de un valor es una cuestión de **significado**, ninguna
> comprobación automática la retira — programa la lectura humana y dilo en la descripción de la puerta.
>
> **El contrato de salida es un documento vivo.** Cuando un cambio altera lo que se emite, consulta la regla que lo
> gobierna **antes** de diseñar la corrección y haz exactamente una de tres cosas: **cumplirla**, **revisarla** como
> parte del mismo cambio, o **registrar** por qué queda fuera de alcance. Las tres son válidas; **el silencio no**.
> Cita la regla por **identificador estable** (nunca por ruta de fichero), y no la conviertas en una puerta de CI: la
> decisión tiene **tres valores**, y una comprobación binaria bloquearía precisamente el resultado correcto de
> "revisar la regla".
>
> **¿De dónde sale el número "esperado"?** "El otro entorno devuelve X" es evidencia **sobre ese entorno**, nunca una
> especificación — y si ese entorno ejecuta la misma ruta de código que estás corrigiendo, igualarlo reproduce el bug.
> Deriva el objetivo de la estructura del documento y del contrato, y dilo claramente cuando la expectativa del ticket
> sea errónea (caso real: el ticket decía 12; la respuesta correcta era 13).

### Precedencia de herramientas (ver [`methodology/tools.md`](./examples/methodology/tools.md))
`AGENTS.md` no solo dice *qué* hacer, sino **con qué herramienta y en qué orden**
(barato→caro, determinista→probabilista):
```
Orientarse     -> /skill:kg (grafo de conocimiento de tickets) · STATUS.md/registros · git · gh   (sin inferencia)
Navegar        -> CodeGraph codegraph_explore (MCP, toolExposure: direct): fuente+rutas+radio de impacto (trátalo como YA leído)
Comprob. refac -> Serena find_referencing_symbols (MCP, direct)  OBLIGATORIO antes de renombrar/borrar
Diagnosticar   -> oráculo determinista (parser/validador/_diag_*.py)  (sin inferencia, reproducible)
Entorno        -> CLI cloud (logs, config de funciones, colas/DLQ)   (perfil de solo lectura)
Contrato       -> Playwright (MCP, deferred) / navegador contra el endpoint de salida
Desplegado     -> Docker: reproducir dentro de la imagen de runtime (etapa real = wrapper); tests verdes != lo que se envía
Solo al final  -> el turno del agente, para VERIFICAR la corrección (no para diagnosticar)
```

### Permisos del método (mecanismo distinto, misma política)
Claude Code: allowlist curada a mano en `settings.local.json`. Cursor: reglas + aprobaciones + hooks +
`permissions.json`. **Pi: nada que poner en allowlist** — (1) **AGENTS.md** lleva la precedencia y "nada de push sin
preguntar"; (2) la extensión global **`block-external-git.ts`** hace cumplir la parte de git; (3) **`--tools`** quita
`edit`/`write` en sesiones de solo lectura; (4) **contenedores** para ejecuciones desatendidas. No intentes portar el
JSON de `allow` — reimplementa la *política*.

---

## 13. Las herramientas del método

**Setup / smoke test de las herramientas en un repo de demo:**
[`AGENT_SETUP_TOOLS.md`](./docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md).

### CodeGraph ([`examples/codegraph/`](./examples/codegraph/)) — inteligencia de código local (vía MCP)
Índice tree-sitter → SQLite en `.codegraph/` (sin API keys). Devuelve símbolos + rutas de llamada + radio de impacto +
**indicadores de cobertura de tests**.
```bash
codegraph init        # crea .codegraph/ y construye el índice   codegraph sync   # incremental tras editar
codegraph explore "<symbol|question>"       # fuente + rutas + radio de impacto, en 1 ida y vuelta
codegraph impact|callers|node <symbol>      # radio de impacto / llamadores / 1 símbolo + rastro
pi mcp add codegraph --description "Code intelligence" -- codegraph serve --path "$PWD" --mcp   # [TESTED]
```
Después pon `"toolExposure": { "codegraph_explore": "direct" }` en la entrada de `mcp.json` — **[TESTED]** el valor
por defecto es `codemode`, que oculta la herramienta de la lista declarada. Es la **primera** herramienta de
navegación (antes de grep/read); trata la fuente que imprime como **ya leída**. Fija `--path` (si no, no hay proyecto
por defecto). En WSL2 `/mnt` el watcher puede perder cambios → `codegraph sync` tras editar. Alternativas
[3rd-party] que la exponen como herramienta nativa de Pi: `@henryqw/pi-codegraph`, `@vndv/pi-codegraph`.

### Serena ([`examples/serena/`](./examples/serena/)) — navegación semántica vía LSP (MCP)
```json
{ "mcpServers": { "serena": { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
  "toolExposure": { "find_symbol": "direct", "find_referencing_symbols": "direct", "get_symbols_overview": "direct" } } } }
```
No probada con Pi (args copiados de la guía de Cursor). Herramientas clave: `find_symbol`, `get_symbols_overview`,
`search_for_pattern`, y sobre todo **`find_referencing_symbols`** — la comprobación **precisa** antes de
renombrar/borrar: desambigua métodos homónimos por clase, donde el `impact` plano de CodeGraph los mezcla. Complementa
a CodeGraph, no lo sustituye. [3rd-party] `@bacnh85/pi-serena`.

### GSD ([`examples/gsd/`](./examples/gsd/)) — el método convertido en herramienta, **solo Claude Code**
Ciclo por fases con estado versionado en `.planning/` y subagentes especializados (`gsd-planner`,
`gsd-plan-checker`, `gsd-executor`, `gsd-code-reviewer`, `gsd-verifier`, …). El paquete oficial soporta
"Claude Code, OpenCode, Gemini and Codex" — **no Pi**. Existen [3rd-party] `pi-gsd` ("Unofficial port", publicado por
última vez el 2026-04-26) y `@opengsd/gsd-pi` (un agente separado con marca GSD), sin probar.

> ⚠️ Apuntar el `"skills"` de Pi a `~/.claude/skills/gsd-*` "funciona" al cargar **[TESTED]**, pero esas skills
> llaman a herramientas de Claude (Task, AskUserQuestion) que Pi no tiene. No lo hagas.

**Equivalente práctico en Pi:**
```
fichero de plan en data/changes/<id>/ -> puerta de discusión -> plan (el humano aprueba antes de tocar código)
/skill:methodology-plan               -> rellena la plantilla de plan
plantillas de prompt (.pi/prompts/)   -> prompts guardados al estilo /plan-phase
cadena /implement del ejemplo subagent-> sustituye a los roles gsd-* (scout/planner/worker/reviewer)
data/changes/                         -> el mismo estado que en Claude Code (no el .planning/ de GSD)
```
> **Honestidad — ¿lo usamos aquí?** **No.** El proyecto real usa el flujo de 11 etapas + `data/changes/`, ajustado a
> correcciones por ticket en un servicio en producción. GSD tiene más sentido en un **greenfield multicomponente**.

---

## 14. Transferir la metodología

Material real: [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) —

- **Pi:** [`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md) + superficie
  [`pi/`](./docs/ai-agents-code-methodology/pi/) (`AGENTS.md.example`, `APPEND_SYSTEM.md.example`,
  `mcp.json.example`, `settings.json.example`, `extensions/block-external-git.ts`, `skills/day/`,
  `skills/atlassian/`, `skills/evidence/`, `skills/preview/`, `skills/kg/`, `skills/kg-refresh/`, `skills/methodology-plan/`,
  `skills/sanitise-diff/`).
- Compartido: [`TRANSFER_AND_BOOTSTRAP.md`](./docs/ai-agents-code-methodology/TRANSFER_AND_BOOTSTRAP.md),
  [`templates/`](./docs/ai-agents-code-methodology/templates/).
- El mismo paquete sigue incluyendo [`CURSOR_ADAPTATION.md`](./docs/ai-agents-code-methodology/CURSOR_ADAPTATION.md)
  y [`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) — la disciplina llega a un
  cuarto agente.

**Lo que viaja sin cambios:** plan→acuerdo→implementar · verificar contra el contrato del consumidor · resolver la
clase general · rastro duradero · el humano es dueño de todo lo externo.

**Lo que cambia — la superficie (de Claude Code a Pi):**
```
CLAUDE.md (+ anidados, @imports)     -> AGENTS.md en cwd + ancestros, uno por dir (sin anidados, sin @imports)
~/.claude/CLAUDE.md                  -> ~/.pi/agent/AGENTS.md (Pi NO lee ~/.claude)
.claude/rules/ (con ámbito)          -> skill con descripción que nombra rutas / ejemplo claude-rules.ts / extensión
Skills ~/.claude/skills/  (/kg)      -> ~/.pi/agent/skills/ (/skill:kg) — MISMO SKILL.md, claves desconocidas ignoradas
.claude/commands/*.md                -> plantillas de prompt ~/.pi/agent/prompts/*.md
Allowlist settings.local.json        -> (ninguna) confianza + --tools/defaultTools + extensiones + contenedores
Hooks (exit 0/2, stdin JSON)         -> extensión TypeScript: pi.on("tool_call") -> { block: true, reason }
Modo plan                            -> fichero de plan + acuerdo humano (o extensión de ejemplo plan-mode/)
Subagentes (Task) + Agent Teams      -> extensión de ejemplo subagent / procesos hijos pi -p — SIN Agent Teams
claude -p (headless)                 -> pi -p … </dev/null  (+ --approve para recursos del proyecto)
Auto-memoria (MEMORY.md)             -> (ninguna) registros + /resume + JSONL de sesión
Agent SDK (query/allowedTools)       -> createAgentSession() / RpcClient (añade las factorías MCP explícitamente)
Allowlist MCP mcp__s__t              -> mismos nombres de herramientas; visibilidad vía exposure/toolExposure
GSD                                  -> se queda en Claude Code ([3rd-party] pi-gsd no oficial)
```

**Bootstrap en el repo destino (bash):** ver el bloque en
[`pi/README.md`](./docs/ai-agents-code-methodology/pi/README.md) — extensión global + skills en `~/.pi/agent/`,
`.pi/mcp.json` con la ruta absoluta del repo sustituida, `AGENTS.md` si no existe. Luego `/trust`.

**Alternativa sin grafo de conocimiento de tickets** (el 80% del valor, setup mínimo): `STATUS.md` con lo más reciente
primero + carpetas por ticket · búsqueda léxica por síntoma/símbolo/campo del contrato · historial de commits
(solapamiento de ficheros) · una sección corta de "zonas peligrosas".

**Checklist del primer día:** rellena `STATUS.md` · 3-5 invariantes en `SHARP_EDGES.md` · define el contrato de
salida en `AGENTS.md` · comandos de test acotados · demuestra una vez que la puerta de git salta · un issue completo
con RED→GREEN + verificación de contrato.

---

## 15. Sincronización de máquinas

Dos mecanismos, y **no** compiten: **(A)** tarball+USB para la *puesta en marcha completa de una máquina*, y
**(B)** almacenamiento de objetos compartido (S3) para el *registro de ingeniería del día a día*.

### A. Puesta en marcha completa: tarball + USB (asimétrica)

Procedimiento real (saneado) — ver [`methodology/machine-sync.md`](./examples/methodology/machine-sync.md);
runbooks de la instalación real en [`docs/synchro/`](./docs/synchro/). El runbook original nació en Claude Code —
la tabla de adaptación:
```
Claude Code                          Pi
Puntero en CLAUDE.md                 Puntero en AGENTS.md (cwd o un ancestro)
Empaquetar ~/.claude (skills+memoria) Empaquetar ~/.pi/agent/: settings.json, mcp.json, extensions/, skills/, prompts/, AGENTS.md
                                     EXCEPTO auth.json, mcp-auth.json, trust.json (secretos / locales a la máquina, como .aws)
                                     sessions/ solo si quieres el historial en el portátil
MCP codegraph en ~/.claude.json      Volver a fijar --path en .pi/mcp.json (o ~/.pi/agent/mcp.json) en el portátil
Skill de Claude /kg-refresh          /skill:kg-refresh + mismos scripts kg_refresh.sh (paso de extracción: ver §16)
```
**Asimétrica:**

```bash
# SALIDA (principal -> portátil): COPIA COMPLETA. -h desreferencia enlaces simbólicos (crítico para un .aws enlazado);
# se excluyen venvs/node_modules/cachés.
WS=$(ls -d /mnt/*/WORKSPACE 2>/dev/null | head -1)        # DERIVA la raíz, no la supongas
tar -czhf ~/ws-migration-$(date +%Y%m%d).tar.gz \
  --exclude='*/node_modules' --exclude='*/.codegraph' --exclude='*/.venv' --exclude='*/__pycache__' --exclude='*.pyc' \
  --exclude='.pi/agent/auth.json' --exclude='.pi/agent/mcp-auth.json' --exclude='.pi/agent/trust.json' \
  -C "$(dirname "$WS")" "$(basename "$WS")" \
  -C /home/$USER .pi .aws .ssh
# USB: WSL no monta automáticamente un USB conectado tras el arranque -> sudo mount -t drvfs F: /mnt/f ; copia, sync,
# y verifica byte a byte (stat -c %s de origen y destino coinciden) antes de expulsar.
# En el destino: target-setup.sh -> reinstala la CLI de CodeGraph, corrige el --path del MCP a la raíz real
# del portátil, reconstruye el índice; luego /login en Pi (las credenciales no viajaron) y /trust en los repos.

# ENTRADA (portátil -> principal): SOLO EL DELTA. El código ya está en el host de git.
git fetch origin                                      # la única operación de red (solo lectura)
cp data/changes/STATUS.md data/changes/STATUS.md.mainbak   # copia de seguridad PRIMERO
tar -xzf "$TARBALL" -C "$REPO"                         # solo los docs en gitignore bajo data/
diff data/changes/STATUS.md.mainbak data/changes/STATUS.md # ¿solo añadidos? se queda. ¿ediciones propias? PARA
```

**Dos huecos, dos subcomandos idempotentes** (el workspace lleva un grafo `kg` — §16): en un portátil nuevo,
`kg_refresh.sh bootstrap` instala las herramientas que no viajan y fija el intérprete; y como Pi **no tiene memoria
de agente propia** que llevar, decide explícitamente qué viaja: `snapshot-memory` aparca las notas de memoria bajo
`data/` (para que viajen) y `restore-memory` las vuelve a fusionar con copia de seguridad en la máquina principal,
antes de `kg-refresh`. Punto de entrada único para el agente del portátil: `LAPTOP_START_HERE.md`. El grafo es un
artefacto **derivado**: se reconstruye allí donde esté el corpus. ⚠️ **Pero la capa de nombres curados sí viaja en
ambos sentidos** — vive dentro del árbol generado y nada la regenera (ver §15B y la Parte 3).

Salvaguardas (el aterrizaje lo conduce **un agente**, con un `INSTRUCTIONS.md` escrito *para* él): solo acciones no
destructivas (renombrar, no borrar; nunca dos operaciones de mover a la vez en un montaje de Windows); sin escrituras
de git al remoto (la puerta global de git impone push/PR); PARA y pregunta en caso de duda; el binario de la CLI cloud
**no** viaja en el paquete (reinstalar + volver a iniciar sesión) — lo mismo para la CLI de CodeGraph y el índice
`.codegraph/`. El humano es dueño de las acciones externas; el agente prepara e informa con evidencias.

### B. El registro compartido: `data/` sobre S3

El tarball resuelve el **transporte**, no la **compartición**. Añade una tercera máquina y una segunda persona y
aparecen tres costes: el registro está en gitignore → **no se puede enlazar** desde un ticket o PR; mover degenera en
archivarlo todo; y cada compañero acaba con **su propio índice privado** de la misma historia. Runbook completo:
[`docs/synchro/s3-sync/README.md`](./docs/synchro/s3-sync/README.md); scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).

```bash
# Dry-run es el valor POR DEFECTO: nada se transfiere hasta --go
./data-pull.sh            # vista previa  ->  ./data-pull.sh --go
./data-push.sh            # vista previa  ->  ./data-push.sh --go
./mount-data.sh           # vista compartida en vivo, SOLO LECTURA (~/s3-<name>-data)
./validate.sh             # una máquina no está configurada hasta que esto imprima MACHINE READY
```

| Regla | Por qué |
|---|---|
| El alcance crece **en fases revisadas** | Empezó estrecho (`changes/**/*.md` + el grafo) y se amplió en fases revisadas, con el responsable aprobando cada paso. ⚠️ **Cada ampliación es un evento de seguridad**: escanea primero, **pon un canario al escáner** (un escaneo "limpio" no cuenta nada hasta que haya cazado un secreto plantado), y luego **concilia** — un informe de transferencia limpio solo dice *"lo que me pidieron enviar, lo envié"*. |
| **Escribir vía sync, leer vía montaje de solo lectura** | El almacenamiento de objetos no tiene bloqueos ni renombrado atómico: un montaje con escritura corrompe, y te enteras semanas después. |
| Dry-run por defecto; `--delete` es una opción aparte | Un espejo exacto desde una vista local desactualizada **borra** lo que un compañero acaba de subir. |
| **El borrado deliberado es una herramienta, con lápida** | `aws s3 sync` no distingue "borrado a propósito" de "ausente": un fichero borrado a mano **volvió dos veces**. `delete.sh` (solo el publicador) borra **un** fichero y añade una lápida a `_deletions.jsonl`; cada pull lo aparta (nunca `rm`) y cada push lo excluye. Un push que **no puede leer** la lista se niega (`exit 5`). |
| Docs = fuente de verdad; el grafo es **derivado** | Los ficheros por ticket casi nunca colisionan. El grafo generado es el **único** punto real de contención → **una** máquina lo publica. |
| **"Derivado" es una propiedad del fichero, no de la carpeta** | Dentro del árbol generado vive un fichero **escrito a mano** (los nombres curados de las comunidades) que nada regenera: en una reconstrucción sobrevivió **<1%**. Clasifica por fichero — *fuente* / *derivado* / *escrito dentro de derivado* — y trata el tercero como fuente. |
| **Los pares deben moverse juntos** | Sync compara **objeto a objeto** → grafo nuevo + nombres viejos = nombres pegados a la comunidad equivocada, **sin error**. Sella la capa con una **huella del grafo** y haz que el chequeo de salud falle ruidosamente. |
| **Coordinar sin bloqueos** | Cada contribuidor escribe **su propio fichero** en una cola (`kg_refresh.sh request` → `refresh_queue/<utc>-<machine>.request`). Claves distintas nunca colisionan. |
| ⚠️⚠️ **La recuperación CADUCA — y cada usuario es dueño de su trabajo** | El versionado suele venir con una regla de ciclo de vida que **caduca las versiones no actuales a los 30 días**. Dilo en el onboarding: *haz pull antes de editar, push de lo que cambiaste, y si desaparece algo tuyo, dilo dentro del mes.* |
| **Los registros compartidos son de solo-añadir** | `STATUS.md`, `FOLLOWUPS.md`… El último en escribir gana, sin fusión: **reescribir uno borra en silencio la línea de otro**. Un aviso en el pull prácticamente no tiene falsos positivos. |
| **El almacén compartido gana en caso de divergencia** | *"Lo tengo en local"* deja de ser un argumento cuando la versión de otro es la publicada. |
| ⚠️⚠️ **Protege AMBAS direcciones** | Medido: dos máquinas editaron el registro de estado la misma tarde; el segundo push sustituyó al primero — **11 líneas perdidas, sin conflicto, sin error**. Protege el push: si la copia almacenada cambió desde tu último sync, **niégate (exit 4 / `REFUSED`)**. Vía de escape `--allow-clobber`, documentada con la razón para no usarla. |
| ⚠️ **Un fichero por máquina necesita exactamente UN escritor, impuesto en la herramienta** | Nuestra herramienta subía la copia que cada máquina tenía del fichero de todos, haciendo retroceder el registro de un compañero. **El primer síntoma fue una conclusión errónea sobre una persona.** |
| ⚠️ **Una salvaguarda que da falsas alarmas el primer día enseña a la gente a saltársela** | La salvaguarda ahora pregunta: *¿esta subida cambiaría realmente el objeto almacenado?* **La tasa de falsos positivos de una salvaguarda es una propiedad de seguridad.** |

**La parte específica del agente — la máquina tiene un rol.** Cada máquina declara `MACHINE_NAME` /
`MACHINE_ROLE` en su `config.env`; `identity.sh --write` genera un `IDENTITY.md` **local a la máquina**, y `AGENTS.md`
**apunta a él**, así que cada sesión de Pi lee primero su propio rol. `IDENTITY.md` es el único fichero que **no** debe
ser igual en todas partes: en gitignore, nunca sincronizado, nunca empaquetado. (En Pi el puntero puede vivir en el
`AGENTS.md` del repo o en `~/.pi/agent/AGENTS.md` — el fichero global ya es por máquina.)

**Y el hábito necesita un mecanismo, no un párrafo.** "Pull al empezar, push al terminar" estuvo en el documento de
operaciones **durante meses y no se hacía** en la misma máquina que publicaba. La solución empaqueta los dos momentos
en una rutina invocable y **consciente del rol** — `day start` / `day end` — invocada en Pi como
**`/skill:day start`**. Ejemplo práctico:
[`examples/skills-plugins/.pi/skills/day/SKILL.md`](./examples/skills-plugins/.pi/skills/day/SKILL.md);
scripts (genéricos pero reales): [`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/). Empieza por
`config.env.example`: ese único fichero es donde vive el diseño. Cada paso peligroso está detrás de una pregunta que
responde primero, y cuando la respuesta es ambigua **para y pregunta**.

> **Antes del primer push compartido:** limpia las credenciales incrustadas en los registros — las notas de
> investigación capturan URLs firmadas y tokens **a propósito**, como evidencia. Ejecuta `/skill:sanitise-diff` sobre
> **todo** el registro. Lo mismo para los artefactos propios de Pi: nunca sincronices `auth.json` / `mcp-auth.json`, y
> trata `/share` como una acción hacia fuera.

> ⚠️⚠️ **Una salvaguarda puede desactivar en silencio el instrumento que prueba el hábito.** Un snapshot previo al
> pull instaló su propio `trap ... EXIT`; Bash guarda **un** solo trap EXIT, así que sustituyó al que escribía el log
> de actividad de sync. Los dry runs seguían registrando y **ningún pull real quedó registrado durante dos días**.
> Pregunta qué más reclama el mismo recurso de una sola plaza; y recuerda que **la ruta real y la de ensayo son rutas
> de código distintas**.

> ⚠️ **Mide una optimización antes de citarla.** Se predijo "de dos minutos a segundos"; se midió
> **212 s → 123 s, alrededor del 40%**. Mide una vez, apunta el número, ponle fecha.

---

# PARTE 3 — El grafo de conocimiento de tickets (graphify)

## 16. Grafo de conocimiento de tickets

**Tecnología: `graphify` — no CodeGraph.** CodeGraph es solo la analogía: si CodeGraph indexa el *código*, este grafo
indexa la **memoria del proyecto** — informes por ticket, "sharp edges", runbooks, notas de memoria. Todo el material
real está en [`docs/knowledge-graph/`](./docs/knowledge-graph/):
[`design.md`](./docs/knowledge-graph/design.md), scripts, tests, manifiesto y la salida real (seudonimizada para este
curso: claves de ticket `TKT-1xx`, clientes `ClientX`). Resumen narrativo:
[`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

### Las piezas

| Pieza | Qué es |
|---|---|
| `kg` (skill) | Consulta: `explain` / `path` / `find` — determinista, **sin LLM** — **funciona en Pi sin cambios** (`/skill:kg`) |
| `kg-refresh` (skill) | Reconstruye el grafo: `prepare` → extracción semántica → `finalize` — **el paso de extracción necesita subagentes** (ver abajo) |
| [`kg_query.sh`](./docs/knowledge-graph/kg_query.sh) | Wrapper de `graphify explain`/`path` sobre `output/graph.json` + `find` |
| [`kg_refresh.sh`](./docs/knowledge-graph/kg_refresh.sh) | Extremos deterministas: `prepare` / `finalize` / `bootstrap` / `snapshot-memory` / `restore-memory` / `request` / `queue` |
| [`build_manifest.py`](./docs/knowledge-graph/build_manifest.py) / [`stage_corpus.py`](./docs/knowledge-graph/stage_corpus.py) | Enumeran y preparan el corpus con nombres que preservan la procedencia |
| `test_kg_corpus.py` · `test_kg_query.py` · `test_kg_refresh.py` | Los extremos están **probados** — el pipeline es infraestructura |
| [`manifest.txt`](./docs/knowledge-graph/manifest.txt) | El corpus explícito y comparable con diff (~116 ficheros, ~196k palabras) |

**¿`kg` es un slash command o una skill? Una skill** — lleva **assets** (los wrappers de shell), tiene una
**`description`** para que el agente la seleccione automáticamente en la etapa de orientación, y `kg-refresh`
**orquesta un paso del propio agente**. En Pi las definiciones viven a nivel de usuario (`~/.pi/agent/skills/kg/`,
`…/kg-refresh/`) — el **mismo `SKILL.md`** que en Claude Code y Cursor; Pi ignora en silencio las claves solo de Claude
como `trigger:` **[TESTED]**, y se invoca como `/skill:kg` en lugar de `/kg`.

### Construir y consultar

```bash
# construir / refrescar (el único paso del agente es la extracción semántica, con subagentes en paralelo)
kg_refresh.sh prepare        # manifiesto -> preparar _corpus/ -> copiar a un scratch FUERA del repo
                             # extracción de nodos/aristas + clustering -> HTML/JSON/informe   <- paso del agente
kg_refresh.sh finalize       # copiar artefactos a output/ + comprobación de fugas (nada fuera de data/)

# consultar (cero LLM: kg_query.sh lee output/graph.json directamente)
kg explain <ticket|topic>    # los vecinos de un nodo    <- el uso más común
kg path <A> <B>              # camino más corto A<->B
kg find <substr>             # descubrir el nombre exacto de un nodo
```

> ⚠️ **La advertencia de Pi para `kg-refresh`.** La extracción de `/graphify` despacha **subagentes de propósito
> general**; Pi no tiene ninguno integrado. Opciones: (a) instalar la extensión de ejemplo `subagent` o [3rd-party]
> `pi-subagents` y adaptar el paso de extracción — **SIN VERIFICAR** (el soporte de graphify para Pi no está
> documentado; su SKILL.md carga en Pi **[TESTED]**, pero sus llamadas a subagentes asumen la herramienta Agent de
> Claude Code); o (b) mantener los extremos deterministas en Pi y **ejecutar solo el paso de extracción desde Claude
> Code**. La ruta del contribuidor (`kg_refresh.sh request`) no necesita subagentes y funciona en Pi tal cual.

**El gotcha que sostiene el pipeline:** `graphify` respeta `.gitignore` y todo `data/` está ignorado → ejecutar el
detector in situ encuentra 0 ficheros; el corpus se prepara en un scratch fuera del repo y los artefactos se copian de
vuelta. Por eso `kg-refresh` es una skill y no un script.

### La salida real (ver [`output/`](./docs/knowledge-graph/output/))

- [`graph.html`](./docs/knowledge-graph/output/graph.html) — visualización interactiva con vis-network. La captura de
  la presentación se regenera con [`presentation/capture_kg_graph.py`](./presentation/capture_kg_graph.py) →
  `presentation/kg_graph.png`.
- `graph.json` — node-link de NetworkX; aristas **tipadas** (`relation`) con `confidence`
  (`EXTRACTED`/`INFERRED` + puntuación). Es lo que lee `kg_query.sh`.
- [`GRAPH_REPORT.md`](./docs/knowledge-graph/output/GRAPH_REPORT.md) — **507 nodos · 672 aristas · 35
  comunidades**; **92% `EXTRACTED`** · 7% `INFERRED`; god-nodes y "conexiones sorprendentes". Las comunidades
  corresponden a zonas peligrosas reales ("Letter-End & Run-in Titles", "Title Detection Failures", "PDF Extractor
  Cascade"…).

### Enganche y ciclo de vida

Enganchado a la regla de **historial primero** de `AGENTS.md` (etapa 1, Orientarse): ejecuta `/skill:kg <ticket|topic>`
*antes* de hacer grep en `data/changes/`; una llamada saca a la luz los tickets relacionados + la zona peligrosa que
leer. Honestidad: la ganancia real es el **recall en zonas densas**; `EXTRACTED` = fiable, `INFERRED` = una pista a
verificar. Es un artefacto **derivado**: se reconstruye allí donde esté el corpus (§15).

> ⚠️ **Corrección: "derivado" es una propiedad del fichero, no de la carpeta.** Dentro del árbol generado vive un
> fichero **escrito a mano** — los nombres curados de las comunidades — que nada regenera. Medido en una reconstrucción
> real, **sobrevivió menos del 1%**, e incluso tras corregir la causa solo ~38% se trasladó. Clasifica **por fichero**:
> *fuente*, *derivado*, y **"escrito a mano pero viviendo dentro del árbol derivado"** — el tercero siempre viaja.
> Sella la capa con una **huella del grafo** contra el que se construyó; un sync por fichero no puede expresar
> atomicidad, así que la comprobación tiene que vivir en los datos.

> **Coste — con honestidad.** "Sin LLM al consultar" **no** es "gratis": el razonamiento caro se paga **una vez** al
> construir el grafo; cada consulta `kg` es luego un algoritmo determinista sobre `graph.json` → **cero inferencia**,
> más el coste de leer una salida corta. Se paga una vez y se cobra en cada uso — desde cualquier agente.

---

# Apéndice

## A. Tabla de equivalencias: Claude Code → Cursor → Pi

| Concepto | Claude Code | Cursor | Pi (1.5.0) |
|---|---|---|---|
| Instalación | `npm i -g @anthropic-ai/claude-code` / instalador | Descarga del editor + `curl https://cursor.com/install \| bash` | `curl -fsSL https://pi.dev/install.sh \| sh` o `npm i -g --ignore-scripts @earendil-works/pi-coding-agent` |
| Binario | `claude` | `agent` (CLI) | `pi` |
| Autenticación | `/login`, `ANTHROPIC_API_KEY` | `agent login`, `CURSOR_API_KEY` | `/login` (OAuth o clave → `~/.pi/agent/auth.json`) o variables de entorno del proveedor; ~40 proveedores |
| Modelo / esfuerzo | `/model`, ajuste de esfuerzo | Selector de modelo | `/model`, `Ctrl+L`, `Ctrl+P`, `--model p/id:high`, `/thinking` (off…max) |
| Modelos locales | Vía una pasarela / `ANTHROPIC_BASE_URL` | Base URL de OpenAI personalizada | Proveedor llama.cpp integrado (`/llama`) + `models.json` (Ollama, LM Studio, vLLM, SGLang) — [`examples/local-models/`](./examples/local-models/) |
| Headless | `claude -p` | `agent -p --trust [--force]` | `pi -p` (`</dev/null` en CI), `--mode json`, `--mode rpc` |
| Instrucciones globales | `~/.claude/CLAUDE.md` | User rules | `~/.pi/agent/AGENTS.md` (o CLAUDE.md) |
| Instrucciones de proyecto | `CLAUDE.md` (+ anidados, `@imports`) | `AGENTS.md` (anidados, gana el más específico) + `.cursor/rules/*.mdc` | `AGENTS.md` / `CLAUDE.md` en cwd **y solo ancestros**; uno por directorio (gana AGENTS.md); sin `@imports`, sin globs |
| Sustituir / ampliar system prompt | `--system-prompt`, `--append-system-prompt` | — | `SYSTEM.md` / `APPEND_SYSTEM.md` (global o `.pi/`), `--system-prompt`, `--append-system-prompt` |
| Reglas con ámbito | `.claude/rules/` (rutas) | `globs` de `.mdc` | Ninguna; skill, extensión o ejemplo `claude-rules.ts` |
| Auto-memoria | Auto-memoria `MEMORY.md` | Memories (auto) | Ninguna integrada; extensiones o paquetes [3rd-party] |
| Permisos | allow/deny en `settings.json` + prompts | `permissions.json` `mcpAllowlist` / `terminalAllowlist` + aprobaciones | **Sin prompts, sin fichero de allowlist.** `--tools` / `--exclude-tools` / `defaultTools`, MCP `toolExposure: hidden`, confianza del proyecto, extensiones, contenedores |
| Sandbox | Modo sandbox opcional | — | Ninguno integrado; Docker, Docker Sandboxes, OpenShell, extensión Gondolin (ejemplo `sandbox/` eliminado en 1.5.0) |
| Almacenamiento de sesiones | `~/.claude/projects/…jsonl` | Historial de chat | `~/.pi/agent/sessions/--<cwd>--/<ts>_<id>.jsonl` (árbol, v3) |
| Reanudar | `claude -c` / `-r` | Lista de chats | `pi -c`, `pi -r`, `/resume`, `--session` |
| Ramificar / rebobinar | `/rewind`, Esc-Esc | `/rewind` (CLI) | `/tree`, `/fork`, `/clone`, Esc-Esc |
| Exportar / compartir | `/export` | — | `/export` (HTML/JSONL), `/share` (gist o Radius), `pi --export` |
| Compactación | Auto + `/compact <focus>` | Auto + `/summarize` | Auto (`compaction.*`) + `/compact [instructions]` + hooks de extensión |
| Prompt caching | Automático | No expuesto | Automático; `PI_CACHE_RETENTION=long`; `cacheWarming`; `showCacheMissNotices` |
| Config MCP | `claude mcp add`, `.mcp.json`, `~/.claude.json` | `.cursor/mcp.json`, `~/.cursor/mcp.json` | `pi mcp add`, `.pi/mcp.json` (de confianza), `~/.pi/agent/mcp.json`; misma forma `mcpServers`; stdio + streamable HTTP (sin SSE); modos de `exposure` |
| Nombres de herramientas MCP | `mcp__server__tool` | `server:tool` | `mcp__server__tool` |
| Skills | `~/.claude/skills`, `.claude/skills` | `.cursor/skills` (+ lee `.claude/skills`) | `~/.pi/agent/skills`, `.pi/skills`, `~/.agents/skills`, `.agents/skills`, ajuste `"skills"` |
| Invocar una skill | `/name` | `/name` | `/skill:name [args]` |
| Slash commands | `.claude/commands/*.md` | Skills / comandos | Plantillas de prompt `~/.pi/agent/prompts/*.md` → `/name` |
| Marketplace | `/plugin install` | cursor.com/marketplace | `pi install npm:… / git:…`; galería pi.dev/packages; `pi config` |
| Subagentes | Integrados (`.claude/agents/`) | Integrados (`.cursor/agents/`) | **Ninguno integrado**; `examples/extensions/subagent` (`~/.pi/agent/agents/*.md`), [3rd-party] `pi-subagents`, tmux |
| Agent Teams | Integrado | No (Background Agents) | No; procesos `pi` en paralelo / RPC |
| Modo plan | Integrado | Plan mode | **Ninguno**; ejemplo `plan-mode/` o paquetes |
| Hooks | hooks en `settings.json` (shell, JSON por stdin/stdout, `exit 2`) | `hooks.json` (`beforeShellExecution`, … `permission: deny`) | **Extensiones TypeScript**: `pi.on("tool_call") → {block:true, reason}`, `tool_result`, `user_bash`, `before_agent_start`, eventos de sesión |
| Herramientas propias | MCP o SDK | MCP | `pi.registerTool()` (TypeBox) o MCP |
| SDK | Claude Agent SDK | `@cursor/sdk` | `createAgentSession()`, `RpcClient` |
| Bot de revisión en CI | GitHub Action | Bugbot | Ninguno oficial; `pi -p` en tu propio workflow |
| GSD | Soportado | No soportado | No soportado oficialmente ([3rd-party] `pi-gsd`) |

## B. Checklist de gotchas

1. Paquete renombrado: `@earendil-works/pi-coding-agent` (el antiguo `@mariozechner/…` está deprecado); las extensiones importan los tipos desde el nuevo scope.
2. MCP **sí** está integrado (desde la 0.99.0) — la exposición por defecto `codemode` oculta las herramientas; pon `toolExposure: direct` para las herramientas del mapa de disparadores.
3. `--tools`: los nombres simples sustituyen a los valores por defecto; una lista de solo `+x`/`-x` los ajusta; no los mezcles (1.1.0). Conserva las herramientas MCP salvo que una entrada empiece por `mcp__` (1.0.4).
4. La sinopsis de `pi mcp --help` omitía `add`/`remove` hasta la 1.3.0 (existían); corregido en la 1.5.0.
5. Ficheros de contexto: uno por directorio (AGENTS.md oculta CLAUDE.md); solo ancestros; ignoran la confianza del proyecto.
6. `pi -p` espera el EOF de stdin en una tubería que no es TTY → `</dev/null`.
7. Print/JSON/RPC no pueden mostrar el prompt de confianza → los recursos `.pi/` del proyecto se omiten en silencio salvo con `--approve`.
8. El modo JSON no sale con código distinto de cero en una ejecución fallida — inspecciona los eventos.
9. Las sesiones del SDK no cargan MCP/codemode integrados — añade las factorías.
10. Skills: `/skill:name`; las claves de frontmatter desconocidas se ignoran; en colisión gana la primera encontrada; apuntar `"skills"` a todo `~/.claude/skills` inunda el prompt.
11. Los subagentes locales al proyecto (extensión de ejemplo) solo se cargan con `agentScope: "project" | "both"`.
12. Windows: `powershell` es una herramienta integrada (`defaultTools: ["-bash", "+powershell"]`); WSL2 se comporta como Linux **[TESTED]**.
13. Telemetría: `enableInstallTelemetry` vale `true` por defecto — `PI_TELEMETRY=0` o el ajuste.
14. Los issues/PRs nuevos de contribuidores nuevos en el repo de Pi se cierran automáticamente.
15. Modelos locales: pon `contextWindow` (y `maxTokens`) en `models.json` con los valores reales del servidor — el valor por defecto de 128 K hace que la compactación nunca se dispare y el servidor trunque (§1).
16. *(1.4.0)* `compaction.reserveTokens` solo fija *cuándo* empieza la compactación; el resumen usa el límite de salida del modelo.
17. *(1.5.0)* El ejemplo de extensión `sandbox/` ya no existe; la validación de argumentos de herramientas pasó a `pi-schema` (las funcionalidades exclusivas de TypeBox ya no aplican).

## C. Fuentes

Verificado el **2026-10-17, Pi 1.3.0**; delta revisado el **2026-11-06, Pi 1.5.0** — Pi avanza rápido, vuelve a
comprobar antes de reutilizar.

- Documentación de Pi: <https://pi.dev/docs/latest> (páginas citadas por nombre arriba: quickstart, cli, cli-integration,
  configuration, security, containerization, sessions, session-format, compaction, settings,
  models, models-configuration, providers, mcp, codemode, skills, prompt-templates, packages, extensions,
  json, rpc, rpc-commands, rpc-extension-ui, sdk, environment-variables, windows, tmux, llama-cpp,
  nvidia-rtx-llama-cpp)
- Página principal de Pi ("What we didn't build"): <https://pi.dev> · changelog <https://pi.dev/changelog> ·
  galería de paquetes <https://pi.dev/packages> · modelos <https://pi.dev/models>
- Código y ejemplos: <https://github.com/earendil-works/pi/tree/main/packages/coding-agent>
  (`examples/extensions/`, `examples/sdk/`)
- npm: <https://www.npmjs.com/package/@earendil-works/pi-coding-agent>
- Anuncio de Pi 1.0: <https://earendil.com/posts/pi-1-0/>
- Especificación Agent Skills: <https://agentskills.io>
- Notas de investigación de este curso: [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md) ·
  actualización [`docs/research/PI_UPDATE_2026-11-06.md`](./docs/research/PI_UPDATE_2026-11-06.md)
