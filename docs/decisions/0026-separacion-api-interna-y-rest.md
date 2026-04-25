# ADR 0026: Separación entre API Python interna y capa REST

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0010 (Puntos de
integración), ADR 0024 (PipelineDeps/PipelineState)

## Descripción

El sistema expone el pipeline de facilitación de dos formas: como función Python
importable para uso en el mismo proceso, y como endpoint HTTP para uso desde
servicios externos. La organización de este código afecta a la testabilidad,
a la complejidad de las dependencias, y a la capacidad de evolucionar cada
capa de forma independiente.

## Decisión

El sistema tiene dos capas de interfaz con responsabilidades distintas:

**API Python interna** (`api/facilitation.py`): única fuente de verdad para la
lógica de arranque del pipeline. Expone dos funciones:

```python
async def facilitate(thread: DiscussionThread) -> PipelineResult:
    """Run the pipeline on a preloaded thread."""

async def facilitate_by_id(thread_id: str) -> PipelineResult:
    """Fetch a thread by ID and run the pipeline."""
```

`facilitate` construye `PipelineDeps` desde `Settings`, resuelve los backends
configurados, y llama a `run_pipeline`. `facilitate_by_id` recupera el hilo del
backend LMS antes de llamar a `facilitate`.

Esta capa no tiene dependencias de HTTP, no maneja timeouts de red, y no serializa
respuestas.

**Capa REST** (`rest_api/router.py`): delega a `facilitate` para la lógica del
pipeline y añade solo lo que es específico del protocolo HTTP:

```python
@router.post("/facilitate")
async def facilitate_thread(thread: DiscussionThread) -> ...:
    settings = get_settings()
    try:
        return await asyncio.wait_for(
            facilitate(thread),
            timeout=settings.pipeline_timeout_seconds,
        )
    except TimeoutError:
        return JSONResponse(status_code=504, ...)
```

La capa REST añade: timeout configurable con respuesta 504 en caso de expiración,
deserialización del cuerpo HTTP a `DiscussionThread`, y serialización de
`PipelineResult` a JSON. No contiene lógica del pipeline.

### Por qué esta separación

La lógica de arranque del pipeline (resolver backends, construir `PipelineDeps`)
es la misma independientemente de si la llamada viene de HTTP, de un script de
evaluación, de un test de integración, o de un plugin Open edX. Duplicar esa
lógica en la capa REST y en otros puntos de uso crearía divergencia.

La capa REST añade restricciones de protocolo (timeout, serialización) que no
son relevantes para el uso programático. Incluirlas en la API interna impondría
esas restricciones a todos los callers.

### Uso del timeout

El timeout de `asyncio.wait_for` en la capa REST sirve para prevenir que una
llamada LLM lenta bloquee indefinidamente una petición HTTP. El valor por defecto
está definido en `Settings.pipeline_timeout_seconds`. Los scripts de evaluación
no usan este timeout: cada ejecución del runner es independiente y tiene su
propio manejo de reintentos (ADR 0027).

## Consecuencias

### Positivas

- La API interna puede importarse directamente desde el plugin Open edX, scripts
  de evaluación, o tests, sin dependencias de FastAPI.
- Los tests de integración del pipeline prueban `facilitate()` directamente,
  sin necesidad de levantar un servidor HTTP.
- La capa REST es delgada: cambiar el comportamiento del pipeline no requiere
  tocar el router.

### Negativas

- La ruta `facilitate_by_id` en la API interna no tiene un endpoint HTTP
  equivalente en el router actual. Un caller externo que solo tiene el ID del
  hilo necesita llamar primero al LMS para obtener el hilo, o este endpoint
  debe añadirse más adelante.
- El timeout es solo para el endpoint `/facilitate`. Si se añaden más endpoints,
  el timeout debe replicarse o abstraerse.

### Cuestiones abiertas

- ¿Debe existir un endpoint `/facilitate/{thread_id}` que use
  `facilitate_by_id` directamente, para que el caller no necesite precargar
  el hilo?
- ¿Debe el timeout estar en la API interna (como parámetro opcional) en lugar
  de solo en la capa REST, para que los scripts de larga duración puedan
  activarlo si lo necesitan?

## Referencias

- ADR 0010: puntos de integración; documenta cómo el plugin Open edX importa
  desde la API interna.
- ADR 0024: `PipelineDeps`/`PipelineState`; describe los tipos que la API
  interna construye antes de llamar al pipeline.
