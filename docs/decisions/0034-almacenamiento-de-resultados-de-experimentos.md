# ADR 0034: Almacenamiento de resultados de experimentos

**Estado**: Supersedido por ADR 0044
**Fecha**: 2026-05-19
**Depende de**: ADR 0014 (Infraestructura de evaluación experimental)
**Relacionado con**: ADR 0007 (Historial de intervenciones por hilo), ADR 0044 (Almacenamiento de resultados de evaluación en S3)

> Esta propuesta no se implementó. La decisión final conserva el sistema de
> archivos como backend por defecto y añade S3 como backend configurable, tal
> como documenta ADR 0044.

## Descripción

El runner de experimentos (`eval-models`, ADR 0014) escribe hoy sus resultados
como ficheros JSON en `docs/experiments/results/<run_id>/`. El dashboard los
lee escaneando ese directorio a través de `artifacts.py`. Este enfoque fue
suficiente para el PoC inicial pero tiene límites concretos que bloquean el
trabajo en curso:

- El historial de runs desaparece si el directorio cambia de ubicación o el
  servidor se reinstala.
- No es posible filtrar runs por tipo, modelo, fecha o estado sin leer todos los
  ficheros.
- Los runs en vivo (HU-11) no tienen un lugar donde persistir su resultado con
  la misma interfaz que los experimentos.
- El dashboard no puede consultar runs pasados de forma eficiente a medida que
  crece el número de ejecuciones.

Esta decisión documenta la estrategia de persistencia de resultados de
experimentos y su separación del historial de intervenciones operacionales
(ADR 0007).

## Distinción clave: dos stores con propósitos distintos

Estos dos componentes se confunden fácilmente pero son independientes:

| Aspecto | Historial de intervenciones (ADR 0007) | Resultados de experimentos (este ADR) |
|---|---|---|
| Qué guarda | Una entrada por intervención generada en un hilo real | El estado completo del pipeline por par modelo/hilo |
| Escrito en | Runs en vivo, cuando el sistema interviene | Runs de experimento, al finalizar cada ejecución |
| Leído por | El pipeline antes de ejecutar (cooldown, escalada EMT) | El dashboard, para inspeccion y comparación |
| Unidad de indexación | `thread_id` | `run_id` |
| Horizonte temporal | Permanente, acumulativo por hilo | Por run, inmutable tras completarse |
| Backend actual | `SQLiteThreadStore` / `InMemoryThreadStore` | Ficheros JSON en sistema de ficheros |
| Backend objetivo | `SQLiteThreadStore` para PoC; PostgreSQL/Redis para producción | MongoDB (ver decisión) |

No comparten esquema, interfaz ni backend. Cambiar uno no implica cambiar el otro.

## Decisión

### Backend: MongoDB

Se adopta MongoDB como backend de persistencia para los resultados de
experimentos. La elección se justifica por:

1. **Esquema flexible sin migraciones**: el `RunRecord` ha evolucionado varias
   veces (ADR 0014) y seguirá cambiando a medida que el pipeline añada etapas.
   Un esquema fijo en SQL requeriría migraciones frecuentes o columnas JSONB
   que hacen perder la ventaja relacional. MongoDB permite evolución sin
   coordinación de esquema.

2. **Consultas anidadas naturales**: el resultado de un run es un documento
   jerárquico (run → modelos → hilos → etapas). Las consultas típicas del
   dashboard — "todos los runs del último mes", "runs donde el modelo X produjo
   más del 50% de intervenciones" — son queries sobre ese documento completo.
   MongoDB los expresa directamente; SQL requiere joins o desnormalización.

3. **Sin servidor extra para el PoC**: MongoDB puede correr local sin
   infraestructura adicional, igual que SQLite para el historial de
   intervenciones. Para la tesis, un contenedor Docker o MongoDB Atlas Free Tier
   es suficiente.

4. **Separación de responsabilidades respecto a ADR 0007**: usar backends
   distintos hace explícito que los dos stores tienen propósitos distintos y
   ciclos de vida distintos. No hay riesgo de confundir qué dato va a qué store.

### Alternativas consideradas

**PostgreSQL + JSONB**: viable y más familiar, pero requiere gestionar
migraciones y un servidor relacional completo. Tiene ventaja si el sistema ya
usa PostgreSQL para otras cosas; en este PoC no es el caso.

**Mantener ficheros JSON**: suficiente para el PoC actual, pero no resuelve el
problema de filtrado eficiente ni la persistencia entre despliegues. Se
mantiene como fallback durante la transición.

**TinyDB**: base de datos documental en fichero puro Python, sin servidor.
Atractiva para el PoC, pero no escala más allá de miles de registros y no
tiene soporte de queries avanzadas.

### Interfaz de acceso a datos

Se introduce una interfaz `RunResultStore` análoga a `ThreadHistoryStore`:

```python
class RunResultStore(Protocol):
    def save_run(self, run: EvalRunManifest) -> None: ...
    def get_run(self, run_id: str) -> EvalRunDetail | None: ...
    def list_runs(self) -> list[EvalRunSummary]: ...
```

Dos implementaciones:

- `FilesystemRunStore`: lee de `docs/experiments/results/` (comportamiento
  actual de `artifacts.py`). Sirve como fallback y para compatibilidad con
  runs históricos.
- `MongoRunStore`: escribe y lee de MongoDB. Se activa cuando
  `MONGO_URI` está configurado.

El router usa la interfaz, no la implementación. El backend se selecciona en
startup según la configuración disponible.

### Esquema de documento en MongoDB

Cada run se guarda como un documento con la estructura:

```json
{
  "_id": "<run_id>",
  "run_type": "experiment",
  "status": "completed",
  "name": "...",
  "timestamp": "2026-05-19T...",
  "models": ["gpt-4o-mini", "claude-3-5-haiku"],
  "thread_count": 8,
  "completed_runs": 16,
  "total_runs": 16,
  "results": [
    {
      "model": "gpt-4o-mini",
      "thread": "scenario-key",
      "classification": { ... },
      "intervention": { ... },
      "error": null,
      "duration_seconds": 2.1
    }
  ]
}
```

El campo `run_type` distingue experimentos de runs en vivo (HU-11). Los runs
en vivo tienen `"run_type": "live"` y omiten campos que no aplican
(`expected_state`, comparación de clasificación).

### Transición desde ficheros JSON

- Los runs existentes en `docs/experiments/results/` no se migran
  automáticamente. El `FilesystemRunStore` los sigue sirviendo.
- Los runs nuevos se escriben en MongoDB si está configurado.
- El dashboard muestra runs de ambas fuentes mezclados, ordenados por
  timestamp. El origen no es visible para el usuario a menos que sea
  relevante para diagnóstico.

## Consecuencias

### Positivas

- Los resultados de experimentos sobreviven a reinicios, cambios de directorio
  y despliegues.
- El dashboard puede filtrar y paginar runs eficientemente sin leer todos los
  ficheros.
- El esquema puede evolucionar con el pipeline sin migraciones.
- Los runs en vivo y los runs de experimento comparten la misma interfaz de
  consulta, con `run_type` como discriminador.

### Negativas

- Añade una dependencia de infraestructura (MongoDB) que no existe hoy.
- El desarrollador local necesita un proceso MongoDB o acceso a Atlas.
- La transición requiere mantener dos backends funcionando en paralelo
  temporalmente.

### Neutrales

- `artifacts.py` no desaparece; se convierte en la implementación
  `FilesystemRunStore` de la interfaz `RunResultStore`.
- El historial de intervenciones (ADR 0007) no cambia. Son stores distintos.
