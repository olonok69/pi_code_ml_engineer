# DEMO_RUNBOOK — Presentación de Pi (37 diapositivas)

> 🇬🇧 English: [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md). Los textos de las diapositivas están en inglés; los
> comandos son los mismos.

Runbook para el **ponente**. Los comandos son bash (macOS, Linux, WSL2). Los datos de Pi se comprobaron contra
**Pi 1.3.0 el 17 de octubre de 2026** (ver [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md))
y se actualizaron para **Pi 1.5.0 el 6 de noviembre de 2026**
([`docs/research/PI_UPDATE_2026-11-06.md`](./docs/research/PI_UPDATE_2026-11-06.md)).
Guía del ponente: [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) · Presentación:
[`presentation/Pi_Presentation.pptx`](./presentation/) · Referencia: [`GUIA_TECNICA.md`](./GUIA_TECNICA.md).

> ⚠️ Las demos en directo que llaman a un modelo necesitan una clave de proveedor (`ANTHROPIC_API_KEY`,
> `OPENAI_API_KEY`, …) o un `/login`. Los comandos de abajo se escribieron a partir del comportamiento
> documentado; los marcados **[TESTED]** se ejecutaron durante la investigación. Ensaya el resto en tu máquina
> antes de la sesión.

## Skills / extensión / MCP — activas en *este* repo

Pi carga los recursos del **proyecto** desde `.pi/` **solo después de que confíes en la carpeta**:

- `.pi/skills/*/SKILL.md` — `audit`, `audit-python`, `deploy-staging`
- `.pi/extensions/block-external-git.ts` — la puerta de git probada
- `.pi/mcp.json` — `context7`, `playwright` (ambos `exposure: "deferred"`)
- `AGENTS.md` — se carga **siempre**, haya o no confianza (los ficheros de contexto la ignoran)

Las copias didácticas en `examples/**/.pi/` **no** se cargan hasta que las copies o las pases con `--skill`.

**Después de `cd` a este repo y `pi` → `/trust`**, prueba:

| Qué | Cómo |
|---|---|
| Skill **npm** | `/skill:audit ex_npm` (mini-app Express + `npm test`) |
| Skill **Python** | `/skill:audit-python ex_app` (app de previsión en Streamlit + `pip-audit`) |
| Skill **staging** | `/skill:deploy-staging ex_staging` (tests → build → **pide OK** → despliegue local → smoke) |
| Extensión (puerta de git) | "ejecuta `git push`" → el resultado de la herramienta debe decir `Blocked by policy: external git/PR action …` |
| MCP | `/mcp` → aparecen context7 / playwright · `pi mcp list` desde la shell |
| Ficheros de contexto | `/session` muestra la sesión; AGENTS.md está en el prompt sin pedirlo |

### Objetivos de las skills (audit + deploy)

| Skill | Objetivo | Stack | Qué hace |
|---|---|---|---|
| `/skill:audit` | [`ex_npm/`](./ex_npm/) | Node + Express | `npm audit` → arreglo seguro → `npm test` |
| `/skill:audit-python` | [`ex_app/`](./ex_app/) | Python + Streamlit | `pip-audit -r requirements.txt` → smoke |
| `/skill:deploy-staging` | [`ex_staging/`](./ex_staging/) | Node (sin Express) | `npm test` → `build` → **confirmación humana** → `deploy:staging` → `GET /health` |

**Comprobación previa de esos objetivos (T1):**

```bash
cd ex_npm && npm install && npm test && npm audit; cd ..
cd ex_app && python3 -m pip install pip-audit && python3 -m pip_audit -r requirements.txt; cd ..
cd ex_staging && npm test && npm run build; cd ..
# ensayo opcional (sin skill): npm run deploy:staging ; curl a la URL de health ; npm run staging:stop
```

Con `/skill:deploy-staging`, el agente **debe pararse** antes de `npm run deploy:staging` y esperar tu OK. Pi por
sí mismo **no** preguntará: la parada vive en el texto de la skill. Ese es el punto de la diapositiva 9.
"Staging" es un servidor local (escribe `.staging-url`); no hay nube.

**Mejor en un repo de producto real con índice de CodeGraph:** CodeGraph, Serena, `/skill:kg`,
`/skill:methodology-plan`; este repo del curso no es una app de producto.

---

## Antes de empezar (5 min)

**Terminales sugeridas**

| # | Abierta en | Para |
|---|---|---|
| T1 | este repo | demos de la Parte 1 + `kg` |
| T2 | un repo de producto con `.codegraph/` | MCP / metodología de la Parte 2 |
| T3 | (opcional) un segundo panel para tmux / `pi` en paralelo | diapositiva 18 |

**Comprobaciones previas**

| Comprobación | Está bien si… |
|---|---|
| `pi --version` | `1.5.0` (o más nueva: entonces relee el changelog) **[TESTED]** |
| `bash examples/local-models/verify/run.sh` | push `Blocked by policy…`, `allowed-ok`, 3 líneas de petición (no hace falta GPU) **[TESTED en 1.5.0]** |
| (opcional, diapositiva 6 en directo) `curl http://127.0.0.1:9931/models` | el router de llama.cpp lista `qwen3.5-4b` como `loaded` |
| `pi auth check --provider anthropic --json` | sale con 0 |
| `pi -p --no-session "Reply: OK-PI" </dev/null` | imprime `OK-PI` |
| `uv run --with anthropic --with python-dotenv python examples/prompt-caching/cache_demo.py` | la 2.ª llamada tiene `cache_read > 0` |
| `bash docs/knowledge-graph/kg_query.sh find letter` | lista de nodos (sin LLM, sin red) |
| T2: `pi mcp list` | `codegraph: connected` **[TESTED, la forma]** |
| T2: `codegraph status` | índice presente |

**No son demos en directo (solo diapositiva / explicación)**

- `examples/gsd/`: GSD es solo de Claude Code
- `examples/automation/github-action-pi.yml`: un patrón, no una acción oficial; ábrelo, no lo ejecutes
- `/share`: sube una transcripción; nunca en un repo de cliente
- `kg_refresh` completo: lento, y su paso de extracción necesita subagentes (diapositiva 34)

---

## Parte 1 — Pi (diapositivas 1–20)

| Diap. | Tema | Demo (comando) | Artefacto |
|---|---|---|---|
| 1–3 | Portada / agenda / separador | Solo diapositivas | — |
| 4 | Instalación + autenticación | T1: `pi --version` · enseña `~/.pi/agent/` (¡sin `auth.json` en pantalla!) | — |
| 5 | Modos | `pi -p --no-session "Reply: OK-PI" </dev/null` · luego **sin** `</dev/null` desde una tubería (`true \| pi -p …` va bien; una tubería abierta se cuelga: explícalo) · `pi --mode json "say hi" </dev/null \| head` | [`examples/automation/`](./examples/automation/) |
| 6 | Modelos locales (GPU de 4 GB) | Sin GPU: `bash examples/local-models/verify/run.sh` (modelo guionizado, puerta de git, imprime lo que envió Pi) · Con GPU: router arrancado → `pi` → `/login llama.cpp` → `/llama` → `/model qwen3.5-4b` → "lista las funciones de `ex_app/metrics_utils.py`" · abre las tablas de [`examples/local-models/README_ES.md`](./examples/local-models/README_ES.md) | local-models |
| 7 | Memoria | Abre [`examples/agents-md/`](./examples/agents-md/) · `AGENTS.md` + `AGENTS.override.md.example` · di: solo ancestros, un fichero por directorio | agents-md |
| 8 | SYSTEM / APPEND_SYSTEM | Abre `examples/agents-md/APPEND_SYSTEM.md.example` | agents-md |
| 9 | Permisos | Abre [`examples/permissions/`](./examples/permissions/) · `pi --tools read,grep,find,ls` → pídele que edite un fichero → no tiene herramienta para hacerlo | permissions |
| 10 | Sesiones | En la TUI: `/session` · `/tree` · `/fork` · selector `pi -r` · `ls ~/.pi/agent/sessions/` | — |
| 11–13 | Contexto + caché | `/compact focus on the open bug` · ejecuta `cache_demo.py` · enseña `showCacheMissNotices` en `examples/permissions/settings.json.example` | context, prompt-caching |
| 14 | MCP | `pi mcp list` · abre [`examples/mcp/mcp.json.example`](./examples/mcp/mcp.json.example) · señala `toolExposure: direct` | mcp |
| 15 | Skills | En directo: `/skill:audit ex_npm` · abre `examples/skills-plugins/.pi/skills/day/SKILL.md` · `pi list` | skills-plugins |
| 16–18 | Subagentes | Abre `examples/subagents/agents/refactor-scout.md` + `agents.png` · lanza un hijo de solo lectura: `pi -p --no-session --tools read,grep,find,ls "List the functions in ex_app/metrics_utils.py" </dev/null` | subagents |
| 19 | Extensiones (hooks) | `/trust`, luego pide a Pi: "ejecuta `git push origin main`" → **Blocked by policy** · luego "ejecuta `git status`" → se ejecuta | extensions |
| 20 | Automatización | Abre `examples/automation/github-action-pi.yml` (patrón) · `bash examples/automation/json-mode.sh "say hi"` | automation |

**Demo de la puerta sin TUI (el modo print necesita `--approve` para la extensión del proyecto):**

```bash
pi -p --no-session --approve "Run exactly this shell command: git push origin main" </dev/null
# esperado: el modelo informa de que la herramienta se bloqueó ("Blocked by policy: external git/PR action ...")
pi -p --no-session --no-approve "Run exactly this shell command: git push origin main" </dev/null
# extensión del proyecto omitida -> se intenta el push. Hazlo SOLO en un repo de prueba sin remoto.
```

La segunda línea es la **ejecución de control**: la misma idea de "poner a prueba el instrumento" de la Parte 2.
En la investigación, la ejecución de control es lo que demostró que fue la puerta (y no el entorno) la que paró el
push.

---

## Parte 2 — Metodología (diapositivas 21–31)

**Espacio de trabajo:** T2, un repo de producto con CodeGraph indexado y `.pi/mcp.json` a partir de
[`docs/ai-agents-code-methodology/pi/mcp.json.example`](./docs/ai-agents-code-methodology/pi/mcp.json.example).

| Diap. | Tema | Demo | Artefacto |
|---|---|---|---|
| 21 | Separador de la Parte 2 | Solo diapositiva | — |
| 22–24 | Principio, flujo de 11 etapas, puerta de salida | Abre `examples/methodology/flow.png` · `WORKFLOW.md` · 2 min de `REAL_EXAMPLE.md` | methodology |
| 25 | Prevalencia de herramientas | Abre `examples/methodology/tools.md` · el mapa de disparadores en `docs/ai-agents-code-methodology/pi/AGENTS.md.example` | methodology |
| 26 | CodeGraph | T2: `pi mcp list` (enseña `codemode` frente a `direct`) · pregunta "¿quién llama a `<símbolo>`?" y mira cómo salta `codegraph_explore` | codegraph |
| 27 | Serena | Pide `find_referencing_symbols` antes de renombrar (sin probar en Pi: ensáyalo) | serena |
| 28 | GSD | **Solo diapositiva**: solo Claude Code; fichero de plan + plantillas de prompt en Pi | gsd |
| 29 | Oráculos / Playwright / Context7 | Playwright (deferred) navegar + snapshot, si lo has ensayado | mcp |
| 30 | Transferencia Claude Code → Pi | Abre `docs/ai-agents-code-methodology/PI_ADAPTATION.md` §2 · la carpeta `pi/` | pack |
| 31 | Sincronización de máquinas + S3 | Abre `examples/methodology/machine-sync.md` · `docs/synchro/s3-sync/README.md` (1 pantalla) | synchro |

**Si MCP no conecta:** `pi mcp list --json` (salida 1 = fallo) · revisa `~/.pi/agent/mcp.log` · ¿confías en la
carpeta? (si no, `.pi/mcp.json` del proyecto se omite) · `--path` absoluto para CodeGraph.

---

## Parte 3 — Grafo de tickets (diapositivas 32–37)

**Espacio de trabajo:** T1 (el grafo del curso vive aquí, seudonimizado).

| Diap. | Tema | Demo | Artefacto |
|---|---|---|---|
| 32 | Separador de la Parte 3 | Solo diapositiva | — |
| 33 | La idea del KG | Abre [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) (1 min) | docs |
| 34 | Pipeline + skills en Pi | Enseña `docs/knowledge-graph/` · abre `docs/ai-agents-code-methodology/pi/skills/kg-refresh/SKILL.md` (la advertencia de Pi); **no** ejecutes el refresh en directo | knowledge-graph |
| 35 | Salida real | Abre `docs/knowledge-graph/output/graph.html` · o la diapositiva con `presentation/kg_graph.png` | graph.html |
| 36 | Enganche | T1: `bash docs/knowledge-graph/kg_query.sh find letter` · luego `bash docs/knowledge-graph/kg_query.sh TKT-104` (necesita `graphify` importable para `explain`) | kg_query.sh |
| 37 | Cierre | Resumen: herramienta (Pi) + método (11 etapas) + memoria (grafo) | — |

```bash
bash docs/knowledge-graph/kg_query.sh find letter      # python puro, funciona siempre
bash docs/knowledge-graph/kg_query.sh TKT-104          # graphify explain
xdg-open docs/knowledge-graph/output/graph.html        # o: explorer.exe / open
```

---

## Orden con tiempos sugerido (~90–120 min)

| Bloque | Diapositivas | Tiempo | Demos imprescindibles |
|---|---|---|---|
| Parte 1 | 1–20 | 45–55 min | `pi -p … </dev/null`, `run.sh` de local-models, cache_demo, puerta de git bloqueada + control, `/skill:audit` |
| Parte 2 | 21–31 | 30–40 min | flow.png + `pi mcp list` (codemode frente a direct) + paquete de transferencia |
| Parte 3 | 32–37 | 15–20 min | `kg_query` + graph.html |
| Margen para preguntas | — | 10 min | — |

**Si vas corto de tiempo:** sesiones solo con `/tree`, sincronización de máquinas en 1 frase, GSD en 30 s, sáltate
RPC/SDK (quédate con `pi -p`).

**Si sobra tiempo:** en T2 ejecuta `/skill:kg <tema>` y `/skill:methodology-plan` de principio a fin.

---

## Chuleta de fallos habituales

| Síntoma | Arreglo rápido |
|---|---|
| `pi -p` se cuelga | stdin es una tubería abierta → añade `</dev/null` **[TESTED]** |
| Faltan skills / MCP / extensión del proyecto en `-p` | la pregunta de confianza no se puede mostrar → añade `--approve` |
| Faltan skills del proyecto en la TUI | `/trust` en la carpeta |
| `/audit` no hace nada | las skills de Pi son `/skill:audit` (o añade una plantilla de prompt) |
| Herramienta MCP "no disponible" para el modelo | la exposición por defecto es `codemode` → `toolExposure: direct` |
| Un script en modo JSON dice éxito en una ejecución fallida | el modo JSON no sale con código distinto de cero: revisa los eventos |
| La sesión del SDK no tiene herramientas MCP | añade `createMcpExtension()` etc. con `DefaultResourceLoader` |
| Están `AGENTS.md` y `CLAUDE.md` y se ignoran las reglas de CLAUDE | un fichero por directorio; gana `AGENTS.md`: fusiónalos |
| cache_demo falla | `uv run --with anthropic --with python-dotenv …` + clave en `.env` |
| Los tutoriales dicen "Pi no tiene MCP" | desfasado desde la 0.99.0 (2026-09-29) |
| Modelo local: respuestas cortadas / olvida el principio | `contextWindow` en `models.json` mayor que el contexto del servidor → ponlo igual (Ollama: `OLLAMA_CONTEXT_LENGTH`) |
| Modelo local: no carga / muy lento en 4 GB | baja `ctx-size` a 16384, `IQ4_XS`, cierra apps que usen la GPU; revisa `nvidia-smi` |
| `/llama` no muestra modelos | el router no está en modo router (arrancado con `-m`/`-hf`) o `--models-dir` incorrecto; reinícialo |

---

## Mapa ejemplo → sección del curso

| Carpeta | Parte | ¿En directo? |
|---|---|---|
| `examples/local-models/` | §01 | Sí (`verify/run.sh`; modelo real si hay GPU preparada) |
| `examples/agents-md/` | §02 | Sí (abrir) |
| `examples/permissions/` | §02 | Sí (abrir + `--tools`) |
| `examples/context/` | §03 | Sí (abrir + `/compact`) |
| `examples/prompt-caching/` | §03 | Sí (ejecutar) |
| `examples/mcp/` | §04 | Sí (abrir + `pi mcp list`) |
| `examples/skills-plugins/` | §05 | Sí (abrir + `/skill:audit`) |
| `ex_npm/` · `ex_app/` · `ex_staging/` | §05 | Sí (`.pi/skills/` activas) |
| `examples/subagents/` | §06 | Sí (abrir + `pi -p` de solo lectura) |
| `examples/extensions/` | §07 | Sí (puerta de git + ejecución de control) |
| `examples/automation/` | §07 | En parte (`pi -p`, modo JSON; la Action es un patrón) |
| `examples/codegraph/` · `serena/` | §09 | Sí, en un repo de producto |
| `examples/gsd/` | §09 | No (explicar) |
| `examples/methodology/` | §08/§11 | Sí (MD + PNG) |
| `docs/knowledge-graph/` | §12 | Sí (consulta + HTML) |
