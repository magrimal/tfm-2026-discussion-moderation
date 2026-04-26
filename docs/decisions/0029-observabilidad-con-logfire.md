# ADR 0029: Observabilidad del pipeline con Logfire

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0026 (Separación API
interna y REST)

## Descripción

El pipeline de facilitación es una cadena de llamadas LLM con decisiones
intermedias (clasificación, intervención, selección de rol, respuesta). Los
archivos de log actuales capturan el resultado de cada etapa pero no el
contenido exacto de los mensajes enviados al modelo, los reintentos de
validación, ni la duración individual de cada llamada. Sin trazabilidad
estructurada, depurar el comportamiento de un modelo concreto sobre un hilo
concreto requiere inspeccionar múltiples archivos JSON de resultados.

## Opciones consideradas

**Logfire** (Pydantic): servicio SaaS con tier gratuito. pydantic-ai emite spans
OpenTelemetry nativamente cuando Logfire está configurado. La integración
requiere dos llamadas en el punto de entrada: `logfire.configure()` y
`Agent.instrument_all()`. No es auto-hosteable: el backend es cerrado, aunque
los traces son OpenTelemetry estándar y pueden redirigirse a otro colector.

**Langfuse**: open-source (MIT), auto-hosteable con Docker Compose, tier gratuito
en cloud. Específico para LLMs: gestión de prompts, coste por token, sesiones.
La integración con pydantic-ai requiere un callback handler; no es nativa.

**Datadog**: SaaS enterprise, sin tier gratuito relevante, sin auto-hosting.
Descartado.

## Decisión

Usar Logfire. La integración nativa con pydantic-ai es el factor determinante:
al llamar a `logfire.configure()` y `Agent.instrument_all()` en el punto de
entrada de la aplicación, todos los agentes del pipeline emiten automáticamente
spans con el historial de mensajes, las llamadas a herramientas, los reintentos
de validación, y la duración de cada paso. No se requieren cambios en los
agentes.

La configuración se activa condicionalmente: si `LOGFIRE_TOKEN` no está
definido en el entorno, el sistema funciona sin trazabilidad (modo silencioso).
Esto evita que el tier gratuito o la ausencia de token sea un error de arranque.

```python
import os
import logfire
from pydantic_ai import Agent

if os.environ.get("LOGFIRE_TOKEN"):
    logfire.configure()
    Agent.instrument_all()
```

Este bloque se ejecuta en los puntos de entrada de la aplicación:
- `api/facilitation.py` — para el uso desde plugin Open edX y tests de integración
- `rest_api/router.py` — para el endpoint HTTP (vía lifespan de FastAPI)
- `evals/eval_models.py` — para los runs de evaluación

La configuración en el evaluador permite trazar cada ejecución del pipeline
durante los experimentos, incluyendo el contenido exacto de los mensajes y
los reintentos, que actualmente solo son visibles a través de `render-prompt`
o de los archivos `raw_response` en los `RunRecord`.

## Por qué no Langfuse

Langfuse es la alternativa natural si el requisito de auto-hosting se vuelve
prioritario (por ejemplo, para no transmitir contenido de hilos a un servicio
externo). El costo de cambiar de Logfire a Langfuse es bajo: la integración con
pydantic-ai es un punto de entrada único. Si en una fase posterior del TFM se
evalúan hilos reales con datos de estudiantes, la pregunta de privacidad debe
revisarse antes de mantener Logfire.

## Consecuencias

### Positivas

- Trazabilidad de extremo a extremo del pipeline sin modificar los agentes.
- Los spans incluyen automáticamente: historial de mensajes por agente,
  argumentos de herramientas, errores de validación con el JSON crudo, y
  duración por nodo.
- El tier gratuito de Logfire es suficiente para un TFM: 30 días de retención,
  sin límite de volumen para proyectos de investigación.
- La integración es OpenTelemetry estándar: los traces pueden redirigirse a
  cualquier colector OTLP (Jaeger, Grafana Tempo, Honeycomb) sin cambiar el
  código de la aplicación.

### Negativas

- Los traces se envían a la infraestructura de Pydantic (logfire.pydantic.dev).
  Datos de hilos de discusión transmitidos al exterior. Aceptable para hilos
  sintéticos de evaluación; requiere revisión antes de usar con datos reales.
- El backend de Logfire no es auto-hosteable. La alternativa OpenTelemetry
  mitiga el vendor lock-in a nivel de datos, pero no de UI.
- Requiere una cuenta y un token. El sistema debe seguir funcionando sin él
  (modo silencioso implementado).

### Cuestiones abiertas

- ¿Debe el evaluador de experimentos trazar todos los runs por defecto cuando
  `LOGFIRE_TOKEN` está presente, o debe ser opt-in con una variable separada
  (`EVAL_TRACE=true`)?
- Si en fases posteriores se usan datos reales de estudiantes, ¿qué datos
  deben excluirse de los traces antes de enviarlos?

## Referencias

- pydantic-ai instrumentation: `Agent.instrument_all()` y el parámetro
  `instrument` del constructor de `Agent`.
- ADR 0026: describe los puntos de entrada donde se añade la configuración.
- ADR 0021: describe el evaluador de experimentos donde se añade trazabilidad
  de runs.
