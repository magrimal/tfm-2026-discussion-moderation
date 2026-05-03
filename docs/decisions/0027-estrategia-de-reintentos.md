# ADR 0027: Estrategia de reintentos ante errores de parseo y límite de tasa

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0012 (PromptedOutput), ADR 0014 (Infraestructura de
evaluación)

## Descripción

El pipeline puede fallar de dos formas distintas que requieren estrategias de
reintento diferentes: errores de validación de salida (el modelo devuelve JSON
que no cumple el esquema esperado) y errores de límite de tasa del proveedor
(el modelo devuelve un código 429 o similar porque la cuota de la API se ha
agotado). Estos dos tipos de error ocurren en capas distintas del sistema y
tienen propiedades distintas.

## Decisión

El sistema usa dos mecanismos de reintento independientes, uno por capa:

### Reintento de pydantic-ai por validación (`retries=3`)

Cada agente del pipeline se crea con `retries=3`:

```python
self.agent = Agent(
    model,
    output_type=ClassificationResult,
    retries=3,
)
```

Cuando el modelo devuelve una respuesta que no cumple el esquema de `output_type`
(JSON inválido, campos faltantes, valores fuera del enum), pydantic-ai reintenta
la llamada automáticamente hasta tres veces, incluyendo el error de validación
como retroalimentación al modelo en el turno siguiente. Esto afecta a los cuatro
agentes: clasificación, intervención, orquestador, y todos los agentes de rol.

Este mecanismo opera dentro de una sola llamada a `agent.run()`: el runner de
evaluación no lo ve. Los reintentos son invisibles para el nodo que invoca al
agente.

### Reintento del runner por límite de tasa (backoff exponencial)

El runner de evaluación (`eval_models.py`) reintenta la ejecución completa del
pipeline cuando detecta un error de límite de tasa:

```python
for attempt in range(max_retries):  # max_retries = 3
    try:
        await facilitation_graph.run(...)
        return build_record(state, None, duration)
    except Exception as exc:
        exc_str = str(exc)
        is_rate_limit = (
            "429" in exc_str
            or "rate" in exc_str.lower()
            or "quota" in exc_str.lower()
        )
        if is_rate_limit and attempt < max_retries - 1:
            wait = 10.0 * (2 ** attempt)  # 10s, 20s
            await asyncio.sleep(wait)
            continue
        return build_record(state, exc_str, duration)
```

El backoff es `10s × 2^attempt`: 10 segundos en el primer reintento, 20 en el
segundo. El límite de tres intentos es configurable solo en código.

La detección de límite de tasa usa coincidencia de cadenas en el mensaje de
excepción (`"429"`, `"rate"`, `"quota"`), no un tipo de excepción específico,
porque distintos proveedores lanzan excepciones con nombres distintos.

### Interacción entre los dos mecanismos

Un error de parseo que pydantic-ai no puede resolver en tres intentos escala
a excepción. El runner de evaluación recibe esta excepción, la interpreta como
error no recuperable (no es un límite de tasa), y registra el fallo en el
`RunRecord` sin reintentar.

Un límite de tasa ocurre cuando el modelo rechaza la llamada antes de generar
una respuesta, por lo que pydantic-ai no llega a verificar el esquema. El runner
detecta el error y reintenta la ejecución completa del pipeline.

Los dos mecanismos no se solapan en la práctica: uno actúa sobre errores de
contenido, el otro sobre errores de conectividad/cuota.

### Diagnóstico de errores de parseo

Cuando una ejecución falla, el runner recorre la cadena de excepciones para
extraer la respuesta cruda del modelo:

```python
cause = exc
while cause is not None:
    if isinstance(cause, json.JSONDecodeError) and cause.doc:
        raw = cause.doc; break
    if isinstance(cause, pydantic.ValidationError):
        raw = str(cause); break
    if hasattr(cause, "body") and cause.body:
        raw = str(cause.body); break
    cause = cause.__cause__
```

El texto crudo se guarda en `RunRecord.raw_response`, lo que permite inspeccionar
qué devolvió el modelo cuando el parseo falló. Este campo fue la herramienta
principal para diagnosticar el comportamiento de los modelos sin soporte de
herramientas (ADR 0012, ADR 0014).

## Consecuencias

### Positivas

- El reintento de pydantic-ai es transparente: los nodos no necesitan gestionar
  errores de validación explícitamente. El agente los maneja internamente.
- El backoff exponencial del runner evita saturar la API del proveedor tras un
  error de límite de tasa.
- El campo `raw_response` proporciona trazabilidad para depurar errores de
  parseo sin requerir instrumentación adicional.

### Negativas

- La detección de límite de tasa por coincidencia de cadenas es frágil: un
  mensaje de error que no contiene `"429"`, `"rate"`, ni `"quota"` no
  activa el reintento. Proveedores que usan mensajes no estándar no se
  benefician del mecanismo.
- El límite de tres reintentos es el mismo para errores de validación y para
  errores de tasa, aunque su origen es diferente. No hay configuración separada.
- El backoff de 10s/20s puede no ser suficiente para el tier gratuito de
  OpenRouter, donde los límites de tasa son del proveedor upstream y pueden
  requerir esperas más largas. Los experimentos con OpenRouter mostraron que
  el backoff actual no siempre es suficiente (ADR 0014).
- La interacción entre los dos mecanismos no está especificada formalmente: si
  pydantic-ai agota sus tres reintentos y lanza, y el mensaje de la excepción
  contiene `"rate"` por coincidencia, el runner reintentará incorrectamente.
- En Ollama, los reintentos internos de pydantic-ai por validación generaban un
  error 400 (`invalid message content type: <nil>`) porque la capa OpenAI-compat
  de Ollama rechaza `content: null` en mensajes de asistente con `tool_calls`.
  Este error se propaga como fallo no recuperable (el runner no lo reintenta).
  Resuelto en ADR 0012 usando `PromptedOutput` para el proveedor Ollama, lo que
  elimina el ciclo tool-call/tool-result del mecanismo de extracción.

### Cuestiones abiertas

- ¿Debe la detección de límite de tasa basarse en el tipo de excepción
  (si el proveedor lo expone) en lugar de en la cadena del mensaje?
- ¿Debe el número de reintentos del runner ser configurable desde variables
  de entorno para ajustarse al proveedor?
- ¿Debe el delay inter-llamada (`EVAL_DELAY_SECONDS`) tener un valor más alto
  por defecto para proveedores con límites de tasa bajos?

## Referencias

- ADR 0012: PromptedOutput; documenta los casos en que pydantic-ai falla a
  pesar de los reintentos (modelos sin soporte de herramientas).
- ADR 0014: infraestructura de evaluación; documenta el comportamiento
  observado con OpenRouter free tier.
