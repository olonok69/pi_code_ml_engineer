# Pi — Un curso en tres partes (presentación + guías)

> 🇬🇧 **English version:** [`README.md`](./README.md) · [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) ·
> [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) · [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md). La presentación
> (`.pptx`) está **solo en inglés**.

> **El volumen Pi de una serie de cursos.** Mismo curso, mismo método, otra herramienta:
>
> | Volumen | Herramienta | Carpeta |
> |---|---|---|
> | 1 | Claude Code | [`../claude_code_ml_engineer`](https://github.com/olonok69/claude_code_ml_engineer/blob/master/README.md) |
> | 2 | Cursor | [`../cursor_code_ml_engineer`](https://github.com/olonok69/cursor_code_ml_engineer/blob/main/README.md) |
> | 3 | **Pi** | este repo |
> | 4 (próximo) | GitHub Copilot | `copilot_code_ml_engineer` (aún no publicado) |
>
> Los enlaces a los volúmenes hermanos suponen que las carpetas están una al lado de la otra.

Material para un **curso/taller** sobre **Pi**, el agente de programación minimalista para terminal (`pi`,
paquete npm `@earendil-works/pi-coding-agent`, antes `badlogic/pi-mono`). Una sola presentación (`.pptx`) con
**tres partes diferenciadas**, dos guías escritas, un runbook de demos y ejemplos reales y ejecutables. Dirigido
a **desarrolladores**. Cada afirmación sobre Pi se comprobó contra **Pi 1.3.0 el 17 de octubre de 2026** y es
trazable a [`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md); el delta
hasta **Pi 1.5.0** se revisó el **6 de noviembre de 2026**
([`docs/research/PI_UPDATE_2026-11-06.md`](./docs/research/PI_UPDATE_2026-11-06.md)).

Por qué Pi es un tercer volumen interesante: Claude Code y Cursor traen prompts de permisos, subagentes y modo
plan como funciones del producto. Pi **no** los trae a propósito ("What we didn't build": sin popups de
permisos, sin subagentes, sin modo plan) y a cambio te da una API de extensiones en TypeScript. Portar la
metodología a Pi separa lo que era **disciplina** de lo que era **comodidad del producto**.

- **Parte 1 — Pi:** instalación, autenticación y modos (interactivo, print `-p`, JSON, RPC, SDK) · proveedores y
  modelos · **modelos locales en una GPU de 4 GB** (router de llama.cpp integrado, Ollama / LM Studio,
  Qwen3.5-4B) · memoria (`AGENTS.md` hacia arriba, `AGENTS.override.md`, `CLAUDE.md` como alternativa,
  `SYSTEM.md` / `APPEND_SYSTEM.md`; sin carga de subdirectorios, sin reglas con ámbito, sin `@imports`) ·
  permisos (ninguno por diseño → confianza, `--tools`, extensiones, contenedores) · sesiones (JSONL en árbol,
  `/tree` `/fork` `/clone` `/export` `/share`) · ventana de contexto + compactación · prompt caching · **MCP
  (integrado desde la 0.99)** · skills (`/skill:nombre`), plantillas de prompt y paquetes · subagentes (no
  integrados) · **extensiones como hooks** · automatización (print/JSON/RPC/SDK en CI y sus trampas).
- **Parte 2 — La metodología (agnóstica de la herramienta):** el flujo real de 11 etapas con puertas ·
  prevalencia de herramientas (CodeGraph, Serena, oráculos) · la puerta de salida de cinco comprobaciones · la
  transferencia **de Claude Code a Pi** ([`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md)
  + una superficie lista para copiar [`pi/`](./docs/ai-agents-code-methodology/pi/)) · sincronización de máquinas
  **y el registro de ingeniería compartido sobre S3**.
- **Parte 3 — El grafo de conocimiento de tickets:** el mismo caso construido con **graphify**: corpus con
  manifiesto, pipeline `kg-refresh`, consulta `kg` sin LLM y el grafo real (507 nodos · 35 comunidades,
  seudonimizado). La skill `kg` funciona en Pi sin cambios; `kg-refresh` necesita subagentes para su paso de
  extracción (extensión, o dejar ese paso en Claude Code).

## Contenido

| Fichero | Qué es |
|---|---|
| [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) · EN [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) | Guía del ponente: narrativa por diapositiva + frases de cierre 🗣️ + enlaces al código. |
| [`GUIA_TECNICA.md`](./GUIA_TECNICA.md) · EN [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | Referencia de implementación para copiar y pegar (configuración, comandos, código), secciones 1–16 + la tabla de equivalencias **Claude Code → Cursor → Pi**. |
| [`DEMO_RUNBOOK_ES.md`](./DEMO_RUNBOOK_ES.md) · EN [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) | Chuleta de demos en directo: comprobaciones previas, comando por diapositiva, tiempos, fallos habituales. |
| [`presentation/Pi_Presentation.pptx`](./presentation/) | La presentación (16:9, 37 diapositivas, **en inglés**), con el mismo sistema visual que las de los volúmenes hermanos. |
| [`presentation/build_pptx_pi.py`](./presentation/build_pptx_pi.py) | Generador de la presentación (regenerable). |
| [`AGENTS.md`](./AGENTS.md) + [`.pi/`](./.pi/) | La superficie Pi de este propio repo: orientación ligera, skills activas, la extensión de la puerta de git, MCP. |
| [`examples/`](./examples/) | Artefactos reales adaptados a Pi, agrupados por sección del curso (en inglés). |
| [`docs/`](./docs/) | **Referencia**: el paquete de metodología (con la adaptación a Pi), el grafo de conocimiento, los runbooks de sincronización y las notas de investigación (en inglés). |

### Nombres de ficheros (inglés primero, copias en español)

Los volúmenes de Claude Code y Cursor son originales en español con copias `_EN`. **Este volumen se escribió
primero en inglés**, así que los ficheros en inglés llevan el nombre simple; los cuatro documentos principales
tienen **copia en español** (desde el 2026-11-06). La presentación y el material de `examples/` / `docs/` están
**solo en inglés** (excepción: [`examples/local-models/README_ES.md`](./examples/local-models/README_ES.md)).

| Volúmenes hermanos (ES / EN) | Este volumen (EN / ES) |
|---|---|
| `README.md` / `README_EN.md` | `README.md` / `README_ES.md` |
| `GUIA_TECNICA.md` / `GUIA_TECNICA_EN.md` | `TECHNICAL_GUIDE.md` / `GUIA_TECNICA.md` |
| `GUIA_PRESENTACION.md` / `GUIA_PRESENTACION_EN.md` | `SPEAKER_GUIDE.md` / `GUIA_PRESENTACION.md` |
| `DEMO_RUNBOOK.md` / `DEMO_RUNBOOK_EN.md` | `DEMO_RUNBOOK.md` / `DEMO_RUNBOOK_ES.md` |
| `ejemplos/` (`metodologia_en/`) | `examples/` (`methodology/`) |
| `presentacion/` | `presentation/` |
| `Cursor_Presentacion_EN.pptx` | `Pi_Presentation.pptx` |

## Ejemplos (por sección del curso)

**Parte 1:**
- [`examples/local-models/`](./examples/local-models/) ([README en español](./examples/local-models/README_ES.md)) — **modelos locales en una GPU de 4 GB**: preset del router de llama.cpp (Qwen3.5-4B), `models.json` para Ollama/LM Studio, ajustes de compactación y razonamiento por modelo, comparativa de agentes y servidores, y un script de ensayo sin GPU `verify/run.sh` (§01, diapositiva 6).
- [`examples/agents-md/`](./examples/agents-md/) — `AGENTS.md` en dos niveles, `AGENTS.override.md`, `APPEND_SYSTEM.md` (§02).
- [`examples/permissions/`](./examples/permissions/) — sin allowlist por diseño: confianza, `--tools` / `defaultTools`, contenedores, `settings.json.example` (§02).
- [`examples/context/`](./examples/context/) — compactación, `/compact`, `/tree`, palancas para un contexto ligero (§03).
- [`examples/prompt-caching/`](./examples/prompt-caching/) — el mecanismo de caché (demo con la API de Anthropic) + lo que controla Pi (§03).
- [`examples/mcp/`](./examples/mcp/) — `mcp.json` con `exposure` / `toolExposure` (§04).
- [`examples/skills-plugins/`](./examples/skills-plugins/) — skills en `.pi/skills/`, incluidas las del proyecto real: `day`, `atlassian` (Jira/Confluence en solo lectura), `evidence` (evidencias de ejecución en solo lectura) y `preview` (antes/después en local en la página de previsualización real); sus herramientas están en [`examples/methodology/tools/`](./examples/methodology/tools/) (§05).
  **Activas en este repo:** [`.pi/skills/`](./.pi/skills/) (`audit`, `audit-python`, `deploy-staging`).
  **Objetivos de demo:** [`ex_npm/`](./ex_npm/) (`/skill:audit`) · [`ex_app/`](./ex_app/) (`/skill:audit-python`) · [`ex_staging/`](./ex_staging/) (`/skill:deploy-staging`).
- [`examples/subagents/`](./examples/subagents/) — ficheros de agente de solo lectura para la extensión de ejemplo de subagentes + el diagrama extensión frente a procesos paralelos (§06).
- [`examples/extensions/`](./examples/extensions/) — el equivalente a los hooks: la **probada** `block-external-git.ts` + patrones sin probar (§07). **Activa:** [`.pi/extensions/`](./.pi/extensions/).
- [`examples/automation/`](./examples/automation/) — print/JSON/RPC/SDK y un **patrón** de GitHub Actions (no es una acción oficial) (§07).

**Parte 2:**
- [`examples/methodology/`](./examples/methodology/) — el flujo de 11 etapas, un ejemplo de principio a fin, la prevalencia de herramientas, la puerta de salida de cinco comprobaciones, el runbook de operaciones (sincronización de máquinas → registro compartido), el diagrama del flujo; además las `tools/` reales (atlassian, evidence) y los scripts `s3-sync/` (§08, §11).
- [`examples/gsd/`](./examples/gsd/) · [`examples/codegraph/`](./examples/codegraph/) · [`examples/serena/`](./examples/serena/) — las herramientas del método en Pi (§09).
- [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/) — el kit de arranque portable: [`PI_ADAPTATION.md`](./docs/ai-agents-code-methodology/PI_ADAPTATION.md) + [`pi/`](./docs/ai-agents-code-methodology/pi/) (`AGENTS.md.example`, `mcp.json.example`, `settings.json.example`, `extensions/block-external-git.ts`, skills `day`, `atlassian`, `evidence`, `preview`, `kg`, `kg-refresh`, `methodology-plan`, `sanitise-diff`). Las adaptaciones a Cursor y Copilot van en el mismo paquete (§10).
- [`docs/synchro/`](./docs/synchro/) — runbooks de sincronización: `machine-sync/`, `laptop-to-main/` y `s3-sync/` (§11).

**Parte 3:**
- [`docs/knowledge-graph/`](./docs/knowledge-graph/) — diseño, scripts (`kg_query.sh`, `kg_refresh.sh`, `build_manifest.py`, `stage_corpus.py`), tests, manifiesto y la salida real (`output/graph.html` + `GRAPH_REPORT.md`) (§12).
- [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) — resumen narrativo.
- [`presentation/kg_graph.png`](./presentation/) — la captura del grafo usada en la presentación.

## Regenerar la presentación y los diagramas

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_pi.py   # -> presentation/Pi_Presentation.pptx
uv run --with pillow python examples/methodology/render_flow.py                # -> examples/methodology/flow.png
uv run --with pillow python examples/subagents/render_agents.py                # -> examples/subagents/agents.png
uv run --with playwright python presentation/capture_kg_graph.py               # -> presentation/kg_graph.png (necesita Chrome + red para el CDN de vis)
```

## Documentación de las tecnologías

| Tecnología | Papel en el curso | Documentación |
|---|---|---|
| **Pi** | La herramienta (Parte 1) | <https://pi.dev/docs/latest> · [código](https://github.com/earendil-works/pi/tree/main/packages/coding-agent) · [changelog](https://pi.dev/changelog) · [paquetes](https://pi.dev/packages) |
| **llama.cpp / Ollama / LM Studio** | Modelos locales (§01, diapositiva 6) | [Guía de llama.cpp en Pi](https://pi.dev/docs/latest/llama-cpp) · [llama.cpp](https://github.com/ggml-org/llama.cpp) · [Ollama](https://ollama.com) · [LM Studio](https://lmstudio.ai) |
| **Agent Skills** | Formato de skill que implementa Pi (§05) | <https://agentskills.io> |
| **MCP** | El estándar de conexión (§04) | <https://modelcontextprotocol.io> |
| **CodeGraph** | El grafo de código (§09) | <https://colbymchenry.github.io/codegraph/> · [repo](https://github.com/colbymchenry/codegraph) |
| **Serena** | Navegación semántica vía LSP (§09) | <https://github.com/oraios/serena> |
| **GSD** | El método hecho producto, solo Claude Code (§09) | <https://github.com/tomascortereal/claude-code-setup> |
| **graphify** | El grafo de conocimiento de tickets (Parte 3) | <https://graphify.net> · [repo](https://github.com/Graphify-Labs/graphify) |
| **Playwright MCP** | Verificación del contrato (§09) | <https://github.com/microsoft/playwright-mcp> |
| **Context7** | Documentación actualizada de librerías (§09) | <https://context7.com> |

## Fuentes

Documentación de Pi <https://pi.dev/docs/latest>, web <https://pi.dev>, changelog <https://pi.dev/changelog>,
código <https://github.com/earendil-works/pi>, npm
<https://www.npmjs.com/package/@earendil-works/pi-coding-agent>, anuncio de Pi 1.0
<https://earendil.com/posts/pi-1-0/> — **verificado el 2026-10-17 con Pi 1.3.0; delta revisado el 2026-11-06 con
Pi 1.5.0 ([`docs/research/PI_UPDATE_2026-11-06.md`](./docs/research/PI_UPDATE_2026-11-06.md)). Pi avanza rápido
(la 1.0 salió el 2026-10-01 y van seis versiones desde entonces); vuelve a comprobar antes de reutilizar.**
Marcas usadas en todo el material: **[TESTED]** (ejecutado en local), **[3rd-party]** (paquete de la comunidad,
sin probar), **NOT DOCUMENTED** (sin fuente). Notas completas:
[`docs/research/PI_FINDINGS_2026-10-17.md`](./docs/research/PI_FINDINGS_2026-10-17.md).

> Los ejemplos derivados de un proyecto profesional real están **saneados**: las claves de ticket están
> seudonimizadas (`TKT-1xx`), los nombres de cliente sustituidos (`ClientX`), y no hay IDs de cuenta, nombres de
> bucket, correos ni secretos. El paquete de publicación en Confluence que acompaña al volumen de Cursor no se
> incluyó en este.
