# ADR 0024: Separación entre PipelineDeps (inmutable) y PipelineState (mutable)

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente)

## Descripción

El grafo pydantic-graph pasa dos objetos a cada nodo a través del contexto de
ejecución: las dependencias (`deps`) y el estado (`state`). El diseño del
pipeline necesita distinguir entre lo que es fijo durante toda la ejecución
(configuración, servicios) y lo que se acumula a medida que los nodos procesan
el hilo (resultados parciales, retroalimentación).

Esta decisión documenta la separación entre `PipelineDeps` y `PipelineState`,
su justificación, y las implicaciones para los tests.

## Decisión

El pipeline usa dos dataclasses con roles distintos:

**`PipelineDeps`** (inmutable en la práctica):

```python
@dataclass
class PipelineDeps:
    """Immutable configuration and services for the pipeline."""
    settings: Settings
    lms_backend: LMSBackend | None = None
    history_store: ThreadHistoryStore | None = None
```

Contiene la configuración (`Settings`) y los servicios externos (`LMSBackend`,
`ThreadHistoryStore`). Ningún nodo escribe en `PipelineDeps` durante la
ejecución: es de sólo lectura.

**`PipelineState`** (mutable):

```python
@dataclass
class PipelineState:
    """Mutable state accumulated across graph nodes."""
    thread: DiscussionThread
    classification: ClassificationResult | None = None
    intervention: InterventionDecision | None = None
    role_selection: RoleSelection | None = None
    response: FacilitationResponse | None = None
    orchestrator_attempts: int = 0
    eval_feedback: list[str] = field(default_factory=list)
    raw_response: str | None = None
```

Contiene el hilo de entrada y los resultados acumulados por cada nodo. Los
nodos escriben en `PipelineState` (por ejemplo, `ctx.state.classification =
...`) y leen resultados de nodos anteriores a través del mismo objeto.

### Convención de acceso

Los nodos acceden a los servicios y la configuración vía `ctx.deps`:

```python
settings = ctx.deps.settings
history_store = ctx.deps.history_store
```

Los nodos leen resultados previos y escriben los propios vía `ctx.state`:

```python
classification = ctx.state.classification
ctx.state.role_selection = await orchestrator.run(...)
```

### Por qué separar en lugar de un único objeto de contexto

La alternativa es un único dataclass que contiene tanto la configuración como
los resultados parciales. La separación tiene dos ventajas concretas:

**Testabilidad.** En los tests, `PipelineDeps` se construye con un stub y
opciones de configuración específicas, y se puede reutilizar entre tests.
`PipelineState` se construye con el hilo bajo prueba y empieza vacío. Esta
separación hace que la configuración del test sea explícita: qué servicios se
inyectan y qué estado inicial tiene el pipeline.

**Claridad de responsabilidades.** Un nodo que modifica `ctx.deps.settings`
en tiempo de ejecución sería un error de diseño: la configuración no debe
cambiar durante la ejecución. La separación hace este contrato visible.
`PipelineDeps` no es `frozen=True` en la implementación actual (dataclass normal),
pero la convención de uso lo trata como inmutable.

### Alineación con pydantic-graph

pydantic-graph expone el estado como `GraphRunContext[State, Deps]`, donde
`State` es el tipo mutable que pydantic-graph gestiona entre nodos y `Deps`
es el tipo de dependencias inyectado al inicio de la ejecución. La separación
`PipelineState` / `PipelineDeps` sigue directamente el modelo de la librería.

## Consecuencias

### Positivas

- Los tests pueden construir `PipelineDeps` con stubs y verificar que los
  nodos leen la configuración correctamente, sin mezclar configuración con estado.
- El estado acumulado (`PipelineState`) es directamente serializable a JSON en
  los experimentos de evaluación: `RunRecord` extrae todos los campos de
  `PipelineState` al final de cada ejecución.
- La semántica de lectura-escritura está clara: `ctx.deps` es de sólo lectura,
  `ctx.state` es de lectura y escritura.

### Negativas

- `PipelineDeps` no es `frozen=True`. La inmutabilidad es una convención, no una
  garantía del tipo. Un nodo que modifique `ctx.deps.settings` en tiempo de
  ejecución no sería detectado por el sistema de tipos.
- `PipelineState` contiene campos heterogéneos: el hilo de entrada (que no cambia
  durante la ejecución) junto con resultados parciales (que sí cambian). Esto
  podría separarse en `PipelineInput` + `PipelineState`, pero añadiría un objeto
  más sin beneficio claro en la fase actual.
- El campo `eval_feedback` en `PipelineState` es un detalle de implementación del
  circuito de retroalimentación (ADR 0013) expuesto en el tipo de estado
  principal. Si el circuito se elimina o cambia, este campo quedaría obsoleto.

### Cuestiones abiertas

- ¿Debe `PipelineDeps` declararse como `frozen=True` para que el sistema de
  tipos garantice la inmutabilidad, en lugar de depender de la convención?
- ¿Debe el hilo de entrada separarse de los resultados parciales en un tipo
  `PipelineInput` distinto de `PipelineState`?

## Referencias

- ADR 0005: arquitectura multi-agente; define los cuatro nodos que usan este
  contexto de ejecución.
- ADR 0013: circuito de retroalimentación; explica el campo `eval_feedback` en
  `PipelineState`.
