# ADR 0019: Configuración de modelo por etapa del pipeline

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0014
(Infraestructura de evaluación)

## Descripción

El pipeline tiene cuatro etapas con requisitos distintos: clasificación
(análisis estructurado, salida JSON compacta), intervención (razonamiento
binario con justificación), orquestación (selección de rol), y generación
de respuesta (texto abierto dirigido a estudiantes). No todos los modelos son
igualmente adecuados para todas las etapas, y no todos tienen el mismo coste
por llamada.

Un diseño que usa el mismo modelo para todas las etapas es simple pero no
aprovecha esta heterogeneidad. Un diseño que permite configurar el modelo
por etapa añade flexibilidad a costa de complejidad de configuración.

## Decisión

`Settings` expone cuatro campos opcionales de modelo, uno por etapa del
pipeline, con fallback al modelo por defecto:

| Campo | Variable de entorno | Etapa |
|---|---|---|
| `classification_model` | `FACILITATION_CLASSIFICATION_MODEL` | `ClassificationAgent` |
| `intervention_model` | `FACILITATION_INTERVENTION_MODEL` | `InterventionAgent` |
| `orchestrator_model` | `FACILITATION_ORCHESTRATOR_MODEL` | `OrchestratorAgent` |
| `role_model` | `FACILITATION_ROLE_MODEL` | Todos los `RoleAgent` |

Todos los campos son `str | None` con valor por defecto `None`. El método
`Settings.model_for(agent)` resuelve el modelo efectivo:

```python
def model_for(self, agent: str) -> str:
    return getattr(self, f"{agent}_model", None) or self.llm_model
```

Si ningún override está configurado, todas las etapas usan `llm_model`.
La configuración mínima válida es solo `llm_model`.

### Casos de uso previstos

**Optimización de coste**: usar un modelo pequeño y rápido para clasificación
e intervención (decisiones estructuradas con salida corta) y un modelo más
capaz para la generación de respuesta (texto abierto visible por estudiantes).
Ejemplo:
```
FACILITATION_LLM_MODEL=anthropic:claude-haiku-4-5
FACILITATION_ROLE_MODEL=anthropic:claude-sonnet-4-20250514
```

**Evaluación comparativa de etapas**: mantener un modelo fijo para todas las
etapas excepto una, para aislar el efecto del modelo en esa etapa.

**Compatibilidad con modelos locales**: en evaluación local con Ollama, usar
el mismo modelo para todas las etapas es lo habitual. Los overrides permiten
mezclar modelos locales y remotos si se necesita.

### Granularidad deliberada

Los cuatro campos corresponden a los cuatro agentes del pipeline (ADR 0005).
No hay override por rol individual dentro de `role_model`: todos los agentes
de rol (organizacional, intelectual, social, afectivo, moderador) comparten
el mismo modelo. La razón: los cinco roles tienen requisitos similares
(herramienta + texto abierto) y añadir cinco campos más aumentaría la
complejidad sin beneficio claro en la fase actual.

## Consecuencias

### Positivas

- La configuración mínima es un único campo (`llm_model`). Los overrides
  son opcionales y aditivos.
- Permite estrategias de coste/calidad sin cambios de código.
- Facilita experimentos de ablación: fijar todas las etapas excepto una
  para medir el impacto del modelo en esa etapa.
- El método `model_for()` centraliza la lógica de fallback; los nodos del
  grafo no necesitan conocer si hay override o no.

### Negativas

- Los experimentos con override parcial son más difíciles de reproducir:
  el `summary.md` actual registra el modelo del resultado, no la configuración
  completa de overrides. Un experimento con `role_model` distinto al resto
  no queda completamente registrado en los resultados.
- El campo `role_model` aplica a todos los agentes de rol por igual. Si un
  experimento necesita un modelo distinto para el rol intelectual y otro para
  el rol social, no es posible sin modificar el código.
- La variable de entorno `LLM_API_KEY` es única para todos los modelos. Si
  se mezclan proveedores (Anthropic para clasificación, Ollama para rol), no
  hay soporte para múltiples claves simultáneas.

### Cuestiones abiertas

- ¿Debe el `summary.md` registrar la configuración completa de overrides
  junto al nombre del modelo, para garantizar la reproducibilidad de los
  experimentos con configuración mixta?
- ¿Tiene sentido añadir overrides por rol individual (`organizational_model`,
  etc.) cuando la evaluación de experimentos lo justifique?
- ¿Cómo gestionar múltiples API keys si se quieren mezclar proveedores en un
  mismo pipeline? La arquitectura actual asume una sola clave.

## Alternativas consideradas

- **Un único modelo para todo el pipeline**: más simple, sin overhead de
  configuración. Descartado porque elimina la posibilidad de optimización
  de coste y de experimentos de ablación por etapa.
- **Modelo configurable por nodo en tiempo de construcción del grafo**:
  pasar el modelo directamente al construir cada nodo. Más explícito, pero
  rompe la inyección de configuración desde variables de entorno y complica
  el arranque del sistema.
- **Configuración por rol (cinco campos)**: un campo por cada `FacilitationRole`.
  Más granular, pero añade cinco variables de entorno sin caso de uso claro
  en la fase actual. Puede ser necesario en fases posteriores.

## Referencias

- ADR 0005: arquitectura multi-agente; define los cuatro agentes del pipeline.
- ADR 0014: infraestructura de evaluación; contexto sobre reproducibilidad
  de experimentos con configuración variable.
