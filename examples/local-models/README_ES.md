# Modelos locales en una GPU pequeña (4 GB de VRAM)

> 🇬🇧 English: [`README.md`](./README.md).

Cómo conectar Pi a un modelo que se ejecuta en tu propia máquina, dimensionado para una tarjeta de **4 GB**, y
cómo se compara Pi con los otros agentes y servidores que se suelen usar.

> **Estado.** **[TESTED en Pi 1.5.0, 2026-11-06]:** la parte de Pi de la fontanería: un proveedor en
> `models.json` (`api: "openai-completions"`) contra un servidor compatible con OpenAI guionizado,
> `--model ollama/<id>`, `--tools`, `--no-mcp`, los ajustes de [`settings.json.example`](./settings.json.example),
> llamadas reales a herramientas de ida y vuelta, y la puerta de git bloqueando `git push`. **UNTESTED:** un
> modelo real en una tarjeta real de 4 GB (en la máquina de pruebas no había GPU ni descarga de modelos). La
> elección de modelo, los nombres de fichero y las cifras de VRAM salen de la ficha del modelo
> ([qwen35-4b-gguf]); cuenta con ajustar `ctx-size` una vez en tu hardware.

## Resumen

- **Agente: quédate con Pi.** De los agentes habituales es el que mejor encaja con un modelo local pequeño: un
  prompt de sistema corto, pocas herramientas y un **proveedor de llama.cpp integrado** (`/login llama.cpp`,
  `/llama`). **Medido en la 1.5.0:** con `--tools read,bash,edit,write --no-mcp -nc`, el prompt de sistema son
  ~2,3 K caracteres y los cuatro esquemas de herramienta ~2,8 K: unos **1,3 K tokens** de coste fijo por petición.
  Los agentes con prompts de sistema muy largos y muchas herramientas dejan poco espacio a un modelo de 4 B y lo
  confunden.
- **Servidor: el router de llama.cpp.** Es lo que Pi integra de forma nativa y da el control que necesita una
  tarjeta de 4 GB (caché KV cuantizada, tamaño de contexto exacto, sin proyector de visión). Ollama o LM Studio
  son la alternativa fácil.
- **Modelo: Qwen3.5-4B, `IQ4_XS` (~2,7 GB) o `Q4_K_M` (~3,0 GB), 16–32 K de contexto.** Los modelos de 7–9 B no
  caben enteros en la GPU de 4 GB con un contexto usable; descargar parte en la CPU funciona, pero es lento para
  el bucle de un agente.
- **Ajusta expectativas.** Un modelo de 4 B puede leer ficheros, ejecutar comandos y hacer ediciones pequeñas y
  bien especificadas. No va a planificar cambios en varios ficheros como un modelo de frontera. Úsalo para tareas
  acotadas, o para trabajo privado/sin conexión, y deja un modelo en la nube para lo difícil (`Ctrl+P` rota los
  modelos en Pi).

## Ficheros

| Fichero | Va a | Qué hace |
|---|---|---|
| [`qwen3.5-4b.ini`](./qwen3.5-4b.ini) | junto a `llama-server` (cualquier ruta) | preset del router de llama.cpp dimensionado para 4 GB |
| [`models.json.example`](./models.json.example) | `~/.pi/agent/models.json` | proveedores de Ollama y LM Studio (no hace falta para llama.cpp) |
| [`verify/`](./verify/) | se ejecuta en el sitio | `run.sh` + `fake-openai.mjs`: ensaya Pi contra un "modelo local" compatible con OpenAI guionizado (sin GPU ni descargas) |
| [`settings.json.example`](./settings.json.example) | fusionar en `~/.pi/agent/settings.json` | umbrales de compactación por modelo para una ventana de 32 K y razonamiento `off`, solo para los modelos locales (`compaction.modelOverrides`, `modelThinkingLevels`); los modelos en la nube conservan los valores por defecto |

## Ruta A — router de llama.cpp (recomendada)

1. **Instala llama.cpp** con soporte de GPU. Instalador de la documentación: `curl -LsSf https://llama.app/install.sh | sh`,
   y luego `llama cli --version` [llama-cpp]. En Windows la versión precompilada con CUDA de `llama-server.exe`
   funciona igual. La página de recetas de NVIDIA cubre las compilaciones con CUDA [nvidia-rtx].
2. **Arranca el router con el preset** (modo router = sin `-m` / `--model` / `-hf` en la línea de comandos):

   ```bash
   llama serve --models-preset qwen3.5-4b.ini --host 127.0.0.1 --port 9931
   # Windows, versión precompilada:
   # .\llama-server.exe --models-preset qwen3.5-4b.ini --host 127.0.0.1 --port 9931
   ```

   El primer arranque descarga el GGUF de Hugging Face. Está listo cuando
   `curl http://127.0.0.1:9931/models` lista `qwen3.5-4b` como `loaded`.
3. **Conecta Pi:** dentro de Pi ejecuta `/login llama.cpp` e indica `http://127.0.0.1:9931`, o

   ```bash
   export LLAMA_BASE_URL=http://127.0.0.1:9931
   pi --tools read,bash,edit,write --no-mcp
   ```

4. **Elige el modelo:** `/model` → `qwen3.5-4b`. Sin el preset también puedes usar `/llama` →
   **Download model…** y escribir `bartowski/Qwen_Qwen3.5-4B-GGUF:IQ4_XS` [llama-cpp].

**Si no cabe:** baja primero `ctx-size` a `16384`, luego cambia entre `IQ4_XS` y `Q4_K_M`, y después cierra otros
usuarios de la GPU (un navegador con aceleración por hardware y el escritorio de Windows se llevan unos cientos de
MB cada uno). Mira `nvidia-smi` con el modelo cargado: si la VRAM está llena y la generación va lenta, capas o
caché se han ido a la RAM del sistema.

## Ruta B — Ollama o LM Studio (la instalación más fácil)

Los dos hablan la API Chat Completions de OpenAI, así que Pi habla con ellos a través de
`~/.pi/agent/models.json` (`api: "openai-completions"`, `apiKey` ficticia) [models]. Copia
[`models.json.example`](./models.json.example), deja el proveedor que uses y haz que el `id` del modelo coincida
con lo que informa el servidor (`ollama list`, o el identificador del modelo en LM Studio). `/model` vuelve a
leer el fichero.

- **Ollama:** `ollama pull qwen3.5:4b` (comprueba la etiqueta en la biblioteca de Ollama). **Trampa:** el contexto
  por defecto de Ollama es pequeño y trunca en silencio cuando se pasa, lo que rompe las sesiones del agente.
  Súbelo antes de arrancar el servidor, por ejemplo `OLLAMA_CONTEXT_LENGTH=32768 ollama serve` (Windows: define
  la variable en Propiedades del sistema y reinicia Ollama), y deja `contextWindow` en `models.json` igual.
- **LM Studio:** descarga el mismo GGUF en la app, fija la longitud de contexto al cargarlo y activa el servidor
  local (puerto por defecto 1234).

## Ensayar sin GPU (para la demo o CI)

```bash
bash examples/local-models/verify/run.sh      # necesita node + pi en el PATH
```

Arranca [`verify/fake-openai.mjs`](./verify/fake-openai.mjs) (un servidor compatible con OpenAI guionizado que
hace de modelo y pide `git push origin main` y luego `echo allowed-ok`), apunta a él un directorio de agente
**aislado** mediante `models.json`, carga la puerta de git de este repo e imprime lo que Pi envió de verdad.
Resultado esperado (**[TESTED] en 1.5.0**): el push vuelve como `Blocked by policy…`, el echo se ejecuta, y cada
petición lleva 4 esquemas de herramienta, `max_tokens=8192` tomado de `models.json` y un prompt de sistema de
~2,3 K caracteres. Cambia el `baseUrl` por `http://127.0.0.1:9931/v1` o `http://localhost:11434/v1` y el mismo
comando habla con un servidor local real.

## Aligerar Pi para un modelo pequeño

| Palanca | Por qué |
|---|---|
| `contextWindow` en `models.json` = el contexto real del servidor | El valor por defecto de Pi es 128000; si Pi cree que la ventana es mayor que la del servidor, la compactación no salta nunca y el servidor trunca |
| `compaction.modelOverrides` → `reserveTokens` ~6 K, `keepRecentTokens` ~8 K para el modelo local ([`settings.json.example`](./settings.json.example)) | Los valores por defecto (16384 / 20000) están pensados para modelos de 200 K tokens y se comerían casi toda una ventana de 32 K. Las claves son `proveedor/idModelo` exactos, así que los modelos en la nube conservan los valores por defecto. Desde la 1.4.0 la propia petición de resumen usa el límite de salida del modelo (`maxTokens`) |
| `--tools read,bash,edit,write` | Menos esquemas de herramienta en el prompt, menos elecciones de herramienta equivocadas |
| `--no-mcp` | Desactiva MCP para la ejecución; cada servidor añade herramientas/instrucciones al prompt y el propio `.pi/mcp.json` de este repo carga dos |
| Razonamiento `off` (`modelThinkingLevels` por modelo, o `/thinking`, `Shift+Tab`) para ediciones rápidas | Qwen3.5 razona por defecto; a ~20–40 tok/s, los razonamientos largos dominan la latencia. Actívalo para los pasos difíciles |
| Prompts cortos y acotados, con rutas de fichero explícitas | Los modelos pequeños navegan mal; señálales el fichero |

## ¿Qué servidor?

| Servidor | Encaje para 4 GB | Notas |
|---|---|---|
| **llama.cpp (router)** | **El mejor** | Proveedor nativo de Pi, `/llama` para cargar/descargar de memoria/bajar modelos, cuantización de la caché KV, control exacto del contexto, GGUF |
| **Ollama** | Bueno | La instalación más fácil, biblioteca de modelos; vigila la longitud de contexto por defecto; menos control sobre la descarga a CPU y la caché |
| **LM Studio** | Bueno | Interfaz gráfica, cómodo en Windows, llama.cpp por debajo; útil para probar modelos antes de escribir un preset |
| **vLLM / SGLang** | Malo | Pensados para rendimiento en GPUs grandes; reservan VRAM por adelantado, priorizan Linux, no se les da bien meter un modelo en 4 GB |

## ¿Qué agente?

| Agente | Encaje para un modelo local de 4 B | Por qué |
|---|---|---|
| **Pi** | **El mejor de los agentes con llamadas a herramientas** | Prompt de sistema mínimo y herramientas básicas por diseño; proveedor de llama.cpp integrado; cualquier servidor compatible con OpenAI vía `models.json`; compactación ajustable |
| **Aider** | Alternativa fuerte | No necesita llamadas a herramientas nativas: el modelo responde con bloques de edición que Aider aplica, y tiene formatos de edición por modelo para modelos débiles. Bueno para "edita estos ficheros"; menos autónomo (sin bucle libre de shell) |
| **OpenCode** | Más flojo | Agente capaz, pero con prompts más grandes y más herramientas; a los modelos pequeños les cuesta su llamada a herramientas |
| **Cline / Roo Code** | Malo | Prompts de sistema muy largos (muchos miles de tokens) y protocolos XML/de herramientas que los modelos de 4 B siguen mal |
| **Continue** | Para autocompletado | Su modo agente tiene el mismo problema, pero el **autocompletado** con un modelo FIM diminuto (p. ej. Qwen2.5-Coder-1.5B) va bien en 4 GB junto al agente, o en su lugar |

El argumento a favor de Pi es el mismo que el curso hace en otras partes: Pi trae menos (sin prompts de permisos,
sin subagentes, sin modo plan), y con un modelo pequeño *menos prompt* es la ventaja.

## Lista corta de modelos para 4 GB

| Modelo | Cuantización / tamaño | Uso |
|---|---|---|
| **Qwen3.5-4B** | IQ4_XS 2,7 GB · Q4_K_M 3,0 GB · Q5_K_M 3,4 GB [qwen35-4b-gguf] | Elección por defecto para el agente: reciente, plantilla de chat con llamadas a herramientas, modo de razonamiento |
| Qwen2.5-Coder-3B-Instruct | Q4_K_M ~2 GB | Más antiguo; más margen para el contexto; vale para ediciones en un solo fichero |
| Qwen2.5-Coder-1.5B (base) | Q4_K_M ~1 GB | Solo autocompletado (FIM), por ejemplo con Continue |
| Qwen3.5-9B, Qwen2.5-Coder-7B, Falcon-H1R-7B | Q4 4,5–6 GB | **No caben** en 4 GB con un contexto usable; solo descargando parte en la CPU (lento). Son de la gama de 8 GB [kilo-local] |

Los tamaños son los de los ficheros GGUF; súmales la caché KV (crece con el contexto) y ~0,3–0,5 GB del runtime y
el escritorio.

## Fuentes

- [llama-cpp] Documentación de Pi, llama.cpp — <https://pi.dev/docs/latest/llama-cpp>
- [nvidia-rtx] Documentación de Pi, NVIDIA RTX + presets de llama.cpp — <https://pi.dev/docs/latest/nvidia-rtx-llama-cpp>
- [models] Documentación de Pi, Models ("Configure a compatible endpoint") — <https://pi.dev/docs/latest/models>
- [models-configuration] Documentación de Pi, referencia de `models.json` — <https://pi.dev/docs/latest/models-configuration>
- [compaction] Documentación de Pi, Compaction (`modelOverrides`; el resumen usa el límite de salida desde la 1.4.0) — <https://pi.dev/docs/latest/compaction>
- [qwen35-4b-gguf] Cuantizaciones GGUF de Qwen3.5-4B — <https://huggingface.co/bartowski/Qwen_Qwen3.5-4B-GGUF>
- [kilo-local] "The best local coding models for any setup" (2026-07-29) — <https://blog.kilo.ai/p/the-best-local-coding-models-for>

Todo comprobado el 2026-11-06 contra Pi 1.5.0. Las comparativas de agentes (Aider, OpenCode, Cline, Continue)
son de diseño, no se han medido aquí.
