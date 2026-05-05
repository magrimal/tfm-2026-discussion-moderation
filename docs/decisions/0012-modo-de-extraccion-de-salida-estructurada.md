# ADR 0012: Modo de extracción de salida estructurada

**Estado**: Revisado (2026-05-03)
**Fecha original**: 2026-04-25
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0009 (Estructura de prompts)

## Descripción

Los agentes del pipeline producen salida estructurada (tipos Pydantic como
`ClassificationResult`, `InterventionDecision`, `RoleSelection`,
`FacilitationResponse`). pydantic-ai ofrece tres mecanismos para extraer esa
salida del modelo:

- **ToolOutput** (por defecto): el framework define una herramienta `final_result`
  con el esquema JSON del tipo de salida. El modelo invoca esa herramienta para
  entregar su respuesta. pydantic-ai extrae los argumentos de la llamada y los
  valida contra el tipo Pydantic.
- **NativeOutput**: usa `response_format` de la API del proveedor para forzar
  salida JSON estructurada. Incompatible con el uso simultáneo de herramientas
  funcionales en la mayoría de backends locales (Ollama, llama.cpp, vLLM).
- **PromptedOutput**: no se define ninguna herramienta de extracción. El
  framework informa al modelo de que debe devolver JSON plano mediante el system
  prompt. El modelo devuelve texto que el framework parsea y valida.

La decisión afecta la compatibilidad con modelos locales, que es un objetivo
explícito del sistema (ADR 0002).

## Cómo difieren los modos en lo que el modelo recibe

### PromptedOutput

El system prompt incluye una instrucción de texto con el esquema JSON:

```
Respond with a JSON object compatible with this schema:
{"properties": {"state": {"enum": ["new","active","stalled",...], ...}, ...}, "type": "object"}
```

No se definen herramientas de extracción. El modelo produce texto libre que el
framework parsea y valida contra el tipo Pydantic. La instrucción "compatible
con este esquema" es semánticamente ambigua: puede interpretarse como "rellena
los valores siguiendo esta estructura" (correcto) o como "devuelve la estructura
del esquema con los valores insertados" (schema-echo).

### ToolOutput

El system prompt no contiene ninguna instrucción de esquema. En su lugar, el
framework registra una herramienta con firma:

```
final_result(state: DiscussionState, trajectory: DiscussionTrajectory, ...)
```

Los nombres de campo, tipos, enums y descripciones de `Field` viajan como
parámetros de la herramienta. El modelo debe *invocar* esta herramienta con los
argumentos correctos — no producir texto JSON, sino generar una llamada de
herramienta estructurada.

### Por qué el schema-echo persiste en ambos modos

El schema-echo es un comportamiento del modelo, no del framework. Algunos
modelos devuelven la definición del esquema como argumento de la herramienta:

```json
{"properties": {"state": "STALLED", "trajectory": "DECLINING", ...}, "type": "object"}
```

en lugar de la instancia plana:

```json
{"state": "STALLED", "trajectory": "DECLINING", ...}
```

El canal de entrega cambia (texto en prompt vs. definición de herramienta),
pero el fallo es el mismo: el modelo confunde el meta-nivel (la descripción
del esquema) con el nivel objeto (los valores a rellenar). Este comportamiento
está correlacionado con la calidad del fine-tuning para seguimiento de
instrucciones, no con el tamaño del modelo.

### Por qué ToolOutput es la elección correcta

`ToolOutput` elimina una clase de problemas (incompatibilidad `tools +
response_format` en Ollama, llama.cpp y vLLM) sin empeorar el schema-echo. Los
modelos que producen schema-echo con `ToolOutput` también lo producen con
`PromptedOutput`. Los modelos bien ajustados para tool-calling (qwen2.5:14b,
llama3.1:8b) son más fiables con `ToolOutput` porque el protocolo de herramientas
es el contrato explícito para el que fueron entrenados.

## Historial de decisiones

### Primera decisión (2026-04-25): adoptar PromptedOutput

Los primeros experimentos con tool-calling (pydantic-ai por defecto) produjeron
dos clases de error:

| Error | Modelos afectados |
|---|---|
| `invalid message content type: <nil>` | `ollama:qwen2.5:14b` (2/6 hilos) |
| `does not support tools` | `ollama:phi4`, `ollama:gemma2:9b` |

Con `PromptedOutput`, `qwen2.5:14b` pasó de 2/6 a 6/6 y `phi4` obtuvo 5/6
(falla solo en el nodo de rol, que usa herramientas funcionales reales).

### Segunda decisión (2026-04-26): revertir a ToolOutput

Nuevos experimentos con `ollama:gemma3:12b` revelaron un modo de fallo distinto
con `PromptedOutput`: el modelo devuelve la estructura del esquema en lugar de
una instancia. La respuesta tiene los valores correctos pero envueltos en la
jerarquía de definición del esquema:

```json
{"properties": {"state": "STALLED", "trajectory": "DECLINING", ...}, "type": "object"}
```

Este patrón indica que el modelo interpreta "devuelve un objeto compatible con
este esquema" como "rellena el esquema". La ambigüedad es intrínseca al modo
de extracción por prompt.

Adicionalmente, investigación sobre el estado del arte confirma que la
incompatibilidad `tools + response_format` (que motivó el abandono del modo
tool-calling original) es un bug conocido y documentado en Ollama, llama.cpp y
vLLM, y no afecta a `ToolOutput`: ese modo usa exclusivamente el protocolo de
herramientas para la extracción de salida, sin usar `response_format`.

### Evidencia experimental tras la segunda decisión (2026-04-26)

Run completo con 10 modelos locales en modo `ToolOutput` (`2026-04-26T11-25-all-10-local-tool-output`). Comparación con los mejores resultados previos en `PromptedOutput`:

| Modelo | PromptedOutput | ToolOutput | Delta | Causa de cambio |
|---|:---:|:---:|:---:|---|
| `ollama:qwen2.5:14b` | 6/6 | 6/6 | 0 | — |
| `ollama:mistral-nemo:12b` | 6/6 | 4/6 | -2 | Schema-echo en ClassificationNode (2 hilos) |
| `ollama:llama3.1:8b` | 6/6 | 6/6 | 0 | — |
| `ollama:gemma2:9b` | 4/6 | 4/6 | 0 | Modo de fallo distinto: 1 herramienta + 1 schema-echo |
| `ollama:phi4` | 5/6 | 4/6 | -1 | Sin soporte de herramientas (1 hilo adicional) |
| `ollama:deepseek-r1:14b` | 0/6 | 5/6 | +5 | Con PromptedOutput fallaba por herramienta; con ToolOutput funciona |
| `ollama:llama3.2` | 1/6 | 2/6 | +1 | Pequeña mejora |
| `ollama:gemma3:4b` | 1/6 | 0/6 | -1 | Regresión menor |
| `ollama:mistral` | 0/6 | 0/6 | 0 | — |
| `ollama:gemma3:12b` | 0/6 | 0/6 | 0 | — |

**El schema-echo no desaparece con `ToolOutput`.** `mistral-nemo:12b` produce el mismo patrón (`{'properties': {'state': ...}}`) en 2 de 6 hilos incluso con extracción por herramienta. El patrón es un comportamiento del modelo, no del framework: algunos modelos devuelven la definición del esquema en lugar de una instancia independientemente del mecanismo de entrega. `ToolOutput` reduce la frecuencia (gemma3:12b pasó de schema-echo en todos los hilos a fallo por validación agotada) pero no lo elimina.

**`deepseek-r1:14b`** es el resultado más sorprendente: pasó de 0/6 a 5/6. Con `PromptedOutput`, fallaba con `does not support tools` en el nodo de rol. Eso indicaba ausencia de soporte de herramientas, pero la evidencia era del nodo de rol (que usa herramientas funcionales reales). Con `ToolOutput`, el modelo sí invoca la herramienta `final_result` en los nodos de clasificación, intervención y selección de rol. El único fallo es un schema-echo intermitente en el nodo de intervención sobre el hilo `stalled`.

### Tercera decisión (2026-05-03): PromptedOutput por proveedor

Tras añadir campos de confianza a `ClassificationResult`, `InterventionDecision` y
`RoleSelection` (ADR 0028), el esquema de la herramienta `final_result` se volvió
más complejo. `qwen2.5:14b` comenzó a fallar la validación en el primer intento con
mayor frecuencia, activando el mecanismo de reintento interno de pydantic-ai (`retries=3`).
En el reintento, el historial de mensajes contiene la respuesta fallida del modelo, que
tenía `content: null` en el mensaje de asistente con `tool_calls` (comportamiento válido
según la especificación OpenAI). La capa de compatibilidad OpenAI de Ollama rechaza ese
historial con `invalid message content type: <nil>`, produciendo un error 400 antes de
que el reintento tenga efecto.

El error no ocurrió antes porque el esquema más simple (sin campos de confianza) era
suficientemente fácil para que `qwen2.5:14b` lo produjera correctamente en el primer
intento, sin necesidad de reintento.

La causa raíz es un bug conocido y no resuelto en la capa OpenAI-compat de Ollama,
documentado en pydantic-ai issues #703 y #3406. No afecta a la API nativa de Ollama
(`/api/chat`), solo a la capa de compatibilidad OpenAI (`/v1/chat/completions`).
pydantic-ai no tiene un parche para esto en las versiones disponibles.

La solución adoptada es usar `PromptedOutput` para los modelos que presentan este bug
y `ToolOutput` para los demás. `PromptedOutput` no usa el ciclo tool-call/tool-result
para la extracción de salida, por lo que el historial nunca acumula mensajes con
`content: null`. Los modelos sin soporte de herramientas (phi4, gemma2:9b) se
benefician igualmente: pueden completar los nodos que no usan herramientas funcionales.

La selección del modo vive en un único lugar: `AgentMixin.resolve_output_type()`,
que consulta `ModelProvider.profile_for(model_str).extraction_mode`. Los perfiles
por modelo están declarados en `MODEL_PROFILES` de cada proveedor (ADR 0031).
Añadir un modelo con el mismo bug requiere únicamente una entrada en ese diccionario.

### Re-análisis del error original con qwen2.5:14b

El error `invalid message content type: <nil>` con `PromptedOutput` era
intermitente: el hilo `off_topic` completaba el pipeline completo incluyendo
el nodo de rol. La causa exacta no está identificada. La hipótesis más probable
es que el contenido de ciertos hilos genera un cuerpo de respuesta nulo en el
protocolo de herramientas de Ollama. El error no volvió a aparecer en ejecuciones
posteriores, incluyendo el run baseline con 5 modelos y el run con todos los
modelos locales.

## Decisión

Usar `ToolOutput` como modo por defecto y `PromptedOutput` para los modelos concretos
que presentan el bug de null-content en Ollama o problemas de schema-echo con
ToolOutput. La selección es automática: `AgentMixin.resolve_output_type()` consulta
`ModelProvider.profile_for(model_str).extraction_mode` y devuelve el tipo apropiado.
Cada agente lo llama en su constructor:

```python
settings = get_settings()
model_str = settings.model_for("classification")
self.agent = Agent(
    model or build_model(model_str, settings.llm_api_key),
    output_type=self.resolve_output_type(
        model_str, ClassificationResult, settings.model_extraction_overrides
    ),
    retries=3,
)
```

Los perfiles por modelo están en `OllamaModelProvider.MODEL_PROFILES`. El modo
también es configurable en tiempo de ejecución mediante
`FACILITATION_MODEL_EXTRACTION_OVERRIDES` sin modificar el código (ADR 0031).

Esta decisión afecta exclusivamente al mecanismo de extracción de salida. Las
herramientas funcionales de los agentes de rol (`retrieve_techniques`,
`get_thread_history`) no cambian.

## Consecuencias

### Positivas

- `ToolOutput` es el patrón estándar de pydantic-ai: el esquema se transmite al
  modelo mediante el protocolo de herramientas, no como texto. Los modelos con
  soporte de herramientas interpretan la instrucción de forma menos ambigua.
- El modo de fallo schema-echo se reduce pero no desaparece: algunos modelos
  (`mistral-nemo:12b` en 2/6 hilos) devuelven la definición del esquema como
  argumento de la herramienta en lugar de una instancia. El mecanismo de
  extracción cambia el canal de entrega, pero no el comportamiento del modelo
  cuando no interpreta correctamente el contrato del esquema.
- `TestModel` de pydantic-ai genera salida válida automáticamente en modo
  `ToolOutput`. Los tests de cableado no necesitan `custom_output_text`.

### Negativas

- Los modelos sin soporte de herramientas (phi4, gemma2:9b y equivalentes) no
  pueden completar ningún nodo, incluyendo clasificación e intervención. Con
  `PromptedOutput` completaban esos nodos aunque fallaran en el nodo de rol.
  La pérdida neta es que esos modelos pasan de "partial" a "none" en la
  evaluación de agentes sin herramientas funcionales.
- El error `invalid message content type: <nil>` en Ollama está resuelto para
  todos los agentes que usan extracción de salida. El bug de null-content en la
  capa OpenAI-compat de Ollama sigue abierto upstream (pydantic-ai #703, #3406),
  pero el sistema lo evita usando `PromptedOutput` para ese proveedor.

### Estratificación de capacidad resultante

La evidencia experimental con 10 modelos revela cuatro niveles:

1. **Completo** (6/6): soporte de herramientas estable, sin schema-echo. Ejecutan
   el pipeline completo en todos los hilos probados. `qwen2.5:14b`, `llama3.1:8b`.

2. **Parcial-schema** (2–5/6): soporte de herramientas presente, pero producen
   schema-echo de forma intermitente dependiendo del hilo. `mistral-nemo:12b`
   (4/6), `deepseek-r1:14b` (5/6), `llama3.2` (2/6).

3. **Parcial-herramienta** (0–4/6 según threads): sin soporte de herramientas
   para extracción de salida; pasan solo los hilos donde la intervención no se
   activa (pipeline termina antes del nodo de rol). `phi4` (4/6), `gemma2:9b`
   (4/6 combinado, con errores de tipo mixto).

4. **Ninguno** (0/6): fallan en clasificación por schema-echo consistente o
   ausencia total de capacidad de seguimiento de esquema. `mistral:7b`,
   `gemma3:4b`, `gemma3:12b`.

La estratificación no es binaria ni predecible únicamente por el tamaño del
modelo: `deepseek-r1:14b` (14B) está en nivel 2 mientras `llama3.1:8b` (8B)
está en nivel 1. El factor determinante es la calidad del fine-tuning para
seguimiento de instrucciones con herramientas, no el tamaño.

### Impacto en tests

`TestModel` genera salida válida automáticamente en modo `ToolOutput`. Los
tests de cableado usan `TestModel()` sin argumentos adicionales:

```python
with agent.agent.override(model=TestModel()):
    result = await agent.run(thread, deps)
```

### Cuestiones abiertas

- ¿Conviene añadir una validación de capacidad al arranque del sistema que
  advierte si el modelo configurado no soporta herramientas?
- Los modelos frontier con tool-calling nativo (GPT-4o, Claude, Gemini) están
  entrenados específicamente para function calling y deberían ser más fiables con
  `ToolOutput` que con `PromptedOutput`.
- OpenRouter usa la misma capa OpenAI-compat que Ollama para ciertos modelos
  locales expuestos vía API. Si aparece el mismo error 400 en OpenRouter, añadir
  una entrada en `OpenRouterModelProvider.MODEL_PROFILES` con
  `extraction_mode="prompted"` resuelve el problema con el mismo mecanismo.

## Referencias

- [pydantic-ai #703](https://github.com/pydantic/pydantic-ai/issues/703): tools + retries no funcionan correctamente en Ollama
- [pydantic-ai #3406](https://github.com/pydantic/pydantic-ai/issues/3406): `invalid message content type: <nil>` con Ollama 0.12.6 y pydantic-ai 1.14.1
- [pydantic-ai #4116](https://github.com/pydantic/pydantic-ai/issues/4116): propuesta de usar la API nativa de Ollama en lugar de la capa OpenAI-compat
