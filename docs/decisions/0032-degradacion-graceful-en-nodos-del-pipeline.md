# ADR 0032: Degradación graceful en nodos del pipeline

**Estado**: Aceptado
**Fecha**: 2026-05-05
**Depende de**: ADR 0027 (estrategia de reintentos), ADR 0029 (observabilidad con Logfire)

## Descripción

El pipeline de facilitación ejecuta cuatro nodos en secuencia: clasificación,
intervención, orquestador y rol. Cada nodo llama a un agente LLM que puede
fallar por razones variadas: esquema de salida agotado tras tres reintentos,
error 400 de la capa OpenAI-compat de Ollama, modelo que no soporta
herramientas funcionales, timeout de red.

Hasta esta decisión, cualquier excepción en cualquier nodo propagaba
directamente al runner de evaluación o al endpoint HTTP, que lo registraba
como fallo total del pipeline. El fallo era indiferenciado: no había forma
de distinguir entre "el pipeline no pudo clasificar el hilo" (fallo temprano,
sin datos útiles) y "el pipeline clasificó e intervino correctamente pero no
generó una respuesta de rol" (fallo tardío, con datos parciales útiles).

## Decisión

Los nodos de intervención, orquestador y rol capturan cualquier excepción
de su llamada al agente, la registran mediante `logger.exception()`, y
devuelven un `PipelineResult` parcial con los campos producidos hasta ese
punto. El nodo de clasificación no captura: una excepción allí significa
que el pipeline no tiene ningún dato útil que devolver.

```python
# InterventionNode
try:
    ctx.state.intervention = await agent.run(ctx.state.thread, deps)
except Exception as exc:
    logger.exception(
        "[intervention] agent failed, returning without decision: %s", exc
    )
    return End(PipelineResult(classification=classification))

# OrchestratorNode
try:
    ctx.state.role_selection = await orchestrator.run(ctx.state.thread, deps)
except Exception as exc:
    logger.exception(
        "[orchestrator] agent failed, returning without role: %s", exc
    )
    return End(PipelineResult(
        classification=classification, intervention=intervention
    ))

# RoleNode
try:
    ctx.state.response = await role_agent.run(ctx.state.thread, deps)
except Exception as exc:
    logger.exception(
        "[role:%s] agent failed, returning without response: %s",
        role_selection.role.value, exc
    )
    return End(PipelineResult(
        classification=classification,
        intervention=intervention,
        role_selection=role_selection,
    ))
```

### Por qué captura amplia y no específica

Una captura específica (por ejemplo, solo `UnexpectedModelBehavior` de
pydantic-ai o `httpx.HTTPStatusError`) requeriría conocer de antemano todos
los modos de fallo de cada modelo y proveedor, que varían entre versiones.
La evidencia experimental muestra que los fallos de modelos locales toman
formas distintas: errores 400 con cuerpo JSON específico de Ollama,
excepciones de validación de pydantic-ai, errores de deserialización.
La captura amplia cubre todos sin mantenimiento por fallo nuevo.

El riesgo de la captura amplia es silenciar bugs del framework en desarrollo.
Se mitiga con `logger.exception()`, que emite el traceback completo tanto
en el log estándar como en Logfire (vía `instrument_pydantic_ai()`), y con
el hecho de que los tests con `TestModel` siguen propagando normalmente.

### Qué contiene un PipelineResult parcial

`PipelineResult.response` y `PipelineResult.final_text` son `None` por
defecto. El caller (runner de evaluación, endpoint HTTP) puede distinguir
un resultado parcial de uno completo inspeccionando qué campos están
poblados:

- `classification` presente, `intervention` ausente: el nodo de intervención
  falló.
- `intervention` presente, `role_selection` ausente: el orquestador falló.
- `role_selection` presente, `response` ausente: el nodo de rol falló.

## Consecuencias

### Positivas

- El runner de evaluación registra el resultado parcial en lugar de un
  fallo total. Los datos de clasificación e intervención son válidos aunque
  el nodo de rol falle, y son útiles para evaluar esas etapas del pipeline.
- Los modelos con `has_functional_tools=False` (phi4, gemma2:9b) completan
  los nodos de clasificación e intervención correctamente. Solo el nodo de
  rol falla cuando la intervención se activa. Sin esta captura, el fallo del
  nodo de rol descartaba datos de clasificación válidos.
- El endpoint HTTP devuelve una respuesta 200 con resultado parcial en lugar
  de un 500. El sistema degrada con gracia en producción.
- Logfire captura la excepción en el span del agente pydantic-ai (antes de
  que el nodo la capture) y adicionalmente en `logger.exception()`. La
  excepción es observable desde dos rutas de instrumentación.

### Negativas

- Un `PipelineResult` parcial es válido según el tipo pero semánticamente
  incompleto. Los callers deben comprobar qué campos están presentes antes
  de usarlos. Callers que asuman que `response` siempre está poblado si
  `should_intervene` es True se encontrarán con un `None` inesperado.
- La captura amplia puede silenciar bugs del framework durante el desarrollo
  si no se revisan los logs. La mitigación es que `logger.exception()` emite
  el traceback completo en todos los entornos.
- `ClassificationNode` sigue propagando. El comportamiento entre nodos no
  es uniforme, lo que puede sorprender. La asimetría es intencional: sin
  clasificación no hay datos útiles que devolver.

### Cuestiones abiertas

- ¿Debe `PipelineResult` incluir un campo `node_error: str | None` para
  que los callers puedan distinguir un resultado parcial de uno completo
  sin inspeccionar la presencia de campos?
- ¿Debe el runner de evaluación distinguir explícitamente entre fallo total
  (excepción propagada desde ClassificationNode) y resultado parcial
  (PipelineResult con campos ausentes)?

## Referencias

- ADR 0027: estrategia de reintentos; el contrato de propagación de
  excepciones que este ADR modifica para los nodos posteriores a clasificación.
- ADR 0029: observabilidad con Logfire; `logger.exception()` emite el
  traceback, que Logfire captura adicionalmente como span del agente pydantic-ai.
- ADR 0031: perfiles por modelo; `has_functional_tools=False` identifica los
  modelos para los que el nodo de rol fallará consistentemente.
