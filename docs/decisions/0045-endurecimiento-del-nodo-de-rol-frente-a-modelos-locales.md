# ADR 0045: Endurecimiento del nodo de rol frente a modelos locales

**Estado**: Aceptado
**Fecha**: 2026-07-23
**Depende de**: ADR 0012 (modo de extracción de salida estructurada), ADR 0027
(estrategia de reintentos), ADR 0031 (perfiles por modelo), ADR 0032
(degradación graceful en nodos del pipeline)

## Descripción

Ejecuciones en vivo en idril con `ministral-3:14b` y `qwen3.5:27b` mostraron
que el nodo de rol seguía fallando con frecuencia pese a la degradación
graceful de ADR 0032. Esa degradación evita que el pipeline entero se caiga,
pero no explica ni corrige por qué el nodo de rol fallaba tan a menudo. El
análisis de varias ejecuciones reales identificó cinco causas concretas y
distintas:

1. **Mensajes perdidos en el fallo**: cuando `UnexpectedModelBehavior`
   agotaba los reintentos, `pipeline_messages["role"]` quedaba vacío. No
   había forma de ver qué había producido el modelo, solo el texto genérico
   "Exceeded maximum retries (3) for output validation".
2. **Techo de contexto de Ollama**: los `input_tokens` de ejecuciones largas
   quedaban fijados en ~4096 (el valor por defecto de `num_ctx` en Ollama),
   evidencia de truncado silencioso. El prompt de rol incorpora tres veces
   el razonamiento completo de los agentes previos (clasificación,
   intervención, orquestador) más un catálogo de ~30 técnicas devuelto por
   `retrieve_techniques`, con dos ejemplos cada una.
3. **JSON válido con escapado inválido**: el modelo generaba contenido
   correcto para `FacilitationResponse`, pero con saltos de línea literales
   dentro de un campo `reasoning` multilínea en lugar de `\n` escapado.
   `pydantic_core` rechaza esto como "control character found while parsing
   a string" y lo trata igual que un fallo real de contenido.
4. **Alucinación y repetición de herramientas**: el modelo llamaba a
   `get_thread_history` con un argumento `thread_id` inventado (rechazado
   con `extra_forbidden`) y, pese a la instrucción explícita de no repetir
   llamadas, volvía a invocar `get_thread_history`/`retrieve_techniques`
   dentro de la misma respuesta. Cada fallo de este tipo consume parte del
   presupuesto de `retries=3`, que ya es escaso.
5. **Una herramienta caída tumbaba todo el paso**: `get_thread_history`
   (consulta a la base de datos), `web_search` (red) y `flag_content`
   (backend LMS) no capturaban excepciones. Un fallo ahí - no relacionado
   con la calidad de la respuesta - propagaba y activaba la degradación de
   ADR 0032 igualmente, perdiendo una ejecución que podría haber tenido
   éxito.

## Decisión

Cinco medidas, cada una dirigida a una causa específica:

### 1. Capturar mensajes parciales en el fallo

`RoleAgent.run()` pasa de `agent.run()` a `agent.iter()` para retener acceso
al historial de mensajes incluso si la ejecución lanza una excepción:

```python
agent_run = None
try:
    async with self.agent.iter(prompt, deps=deps) as agent_run:
        async for _ in agent_run:
            pass
except Exception as exc:
    if agent_run is not None:
        exc.partial_messages = json.loads(
            ModelMessagesTypeAdapter.dump_json(agent_run.all_messages())
        )
    raise
```

### 2. Reducir el volumen de tokens del prompt

- `retrieve_techniques` devuelve un ejemplo por técnica en lugar de todos.
- `cap_reasoning()` (en `utils.py`, compartida por role/intervention/
  orchestrator) trunca a 500 caracteres el razonamiento heredado de agentes
  anteriores antes de incrustarlo en el prompt siguiente.
- Las instrucciones de clasificación, intervención y orquestador piden
  explícitamente razonamiento conciso (3-5 frases, 2-3 frases). El truncado
  por caracteres queda como red de seguridad, no como mecanismo principal:
  corta desde el principio sin criterio de contenido y puede eliminar
  justo la conclusión más útil si el modelo ignora la instrucción.
- Restricción explícita: no volver a llamar a `get_thread_history` ni a
  `retrieve_techniques` más de una vez por respuesta.

### 3. Reparar JSON como último recurso, no como ruta alternativa del modelo

`json_repair.py` extrae el primer objeto JSON completo de un texto y escapa
caracteres de control sin escapar dentro de literales de cadena. Se aplica
**solo después de que pydantic-ai agota sus propios reintentos**, dentro del
mismo bloque `except` que ya captura `partial_messages`:

```python
if isinstance(exc, UnexpectedModelBehavior):
    raw_text = _last_response_text(agent_run.all_messages())
    if raw_text is not None:
        try:
            salvaged = FacilitationResponse.model_validate_json(
                repair_and_extract_json(raw_text)
            )
        except (ValueError, ValidationError):
            pass
        else:
            return salvaged, exc.partial_messages
raise
```

**Alternativa descartada**: combinar `TextOutput(reparar)` directamente en
`output_type` junto al tipo base, para que pydantic-ai enrutara el texto
mal formado a través de la reparación automáticamente. Se comprobó
empíricamente que esto cambia `model_request_parameters.allow_text_output`
de `False` a `True`, lo que a su vez hace que pydantic-ai envíe
`tool_choice='auto'` en vez de `'required'` a la API de Ollama - eliminando
el único mecanismo que fuerza al modelo a intentar la llamada a la
herramienta en primer lugar. El riesgo de que el modelo abandone antes la
llamada a la herramienta superaba el beneficio de reparar más casos, así
que la reparación se mantiene como último recurso posterior al fallo, sin
tocar `output_type`.

### 4. Tolerar alucinaciones y aplicar "una sola vez" en código, no solo en el prompt

```python
def get_thread_history(
    ctx: RunContext[RoleAgentDeps],
    thread_id: str | None = None,  # ignorado
) -> str:
    call_counts["get_thread_history"] += 1
    if call_counts["get_thread_history"] > 1:
        return "You already called get_thread_history once this response..."
    ...
```

El contador vive en el cierre de `register_tools()`, que se ejecuta una vez
por instancia de agente de rol; como `RoleNode` construye una instancia
nueva en cada ejecución del pipeline, no hay fuga de estado entre
ejecuciones. Devolver un mensaje de rechazo desde la propia herramienta es
gratis en términos de reintentos (el resultado de una herramienta no se
valida contra el esquema de salida) y es una señal más fuerte que repetir
la instrucción en el prompt, que el modelo ya demostró ignorar.

### 5. Aislar el fallo de una herramienta del resto de la ejecución

`get_thread_history` (consulta a BD), `web_search` (red) y `flag_content`
(backend LMS) ahora capturan cualquier excepción, la registran con
`logger.exception()` y devuelven una cadena descriptiva al modelo en lugar
de propagar - alineándose con el patrón que `get_course_context` ya seguía.
El error sigue siendo visible: aparece como el valor de retorno de la
herramienta en `pipeline_messages`, solo que ya no derriba la ejecución.

## Consecuencias

### Positivas

- Un fallo de rol ahora muestra en `pipeline_messages["role"]` exactamente
  qué produjo el modelo, en vez de un mensaje de error genérico.
- El volumen de tokens del prompt de rol se reduce de forma medible
  (confirmado en una ejecución posterior en idril: los `input_tokens` ya no
  quedan fijados en el techo de ~4096).
- Contenido de respuesta que antes se descartaba por un error de escapado
  de JSON ahora se recupera sin pedir al modelo que regenere la respuesta.
- Una alucinación de argumento en `get_thread_history` ya no consume parte
  del presupuesto de reintentos.
- Un backend de historial, de búsqueda web o de LMS caído ya no tumba una
  ejecución que de otro modo habría producido una respuesta válida.

### Negativas

- El truncado por caracteres en `cap_reasoning()` puede cortar contenido
  útil si el modelo ignora la instrucción de concisión; es una red de
  seguridad basta, no una síntesis inteligente.
- La reparación de JSON solo cubre errores de escapado y de texto
  circundante (marcado, llaves sobrantes); no repara un objeto con
  estructura semánticamente distinta al esquema esperado.
- El contador de llamadas "una sola vez" en las herramientas está acotado a
  una instancia de agente; si en el futuro se reutilizara una misma
  instancia entre ejecuciones, el contador debería reiniciarse
  explícitamente.
- Las medidas 2-5 se aplicaron solo al nodo de rol. Los nodos de
  clasificación, intervención y orquestador no tienen herramientas
  registradas ni el mismo problema de repetición, pero si en el futuro se
  les añaden herramientas, necesitarían el mismo tratamiento.

### Cuestiones abiertas

- ¿Debe aumentarse `num_ctx` en el servidor Ollama de idril? No es algo que
  se pueda configurar desde este repositorio (requiere acceso de
  administrador al servidor); pendiente de evaluar si se puede pedir el
  cambio o si conviene explorar un modelo con mayor capacidad ya disponible
  para pull.
- ¿Merece la pena una revisión sistemática de verbosidad en los cuatro
  agentes (no solo el de rol), dado que el hallazgo de tokens aplica en
  distinta medida a todos?
- La reparación de JSON (medida 3) no se ha extendido a clasificación,
  intervención u orquestador porque ninguno mostró este fallo en las
  ejecuciones revisadas; si apareciera, la función `repair_and_extract_json`
  ya es reutilizable sin cambios.

## Referencias

- ADR 0012: modo de extracción de salida estructurada; documenta el bug de
  Ollama de contenido nulo que esta ADR complementa con reintentos
  dirigidos en `eval_models.py` (fuera del alcance de este documento).
- ADR 0027: estrategia de reintentos; `retries=3` es el presupuesto que las
  medidas 2 y 4 buscan no malgastar.
- ADR 0031: perfiles por modelo; `extraction_mode="prompted"` es
  incompatible con combinar `PromptedOutput` con cualquier otro
  `output_type`, la razón técnica por la que se descartó la alternativa de
  la medida 3.
- ADR 0032: degradación graceful en nodos del pipeline; esta ADR reduce la
  frecuencia con la que esa degradación se activa en el nodo de rol, sin
  reemplazarla.
