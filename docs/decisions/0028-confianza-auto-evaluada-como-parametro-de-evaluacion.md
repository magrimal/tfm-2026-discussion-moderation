# ADR 0028: Confianza auto-evaluada como parámetro de evaluación

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de tres fases), ADR 0021 (Diseño del evaluador
de experimentos)

## Descripción

El pipeline produce cuatro tipos de salida estructurada: `ClassificationResult`,
`InterventionDecision`, `RoleSelection` y `FacilitationResponse`. El campo
`confidence` estaba presente en `FacilitationResponse` desde el inicio, pero
ausente en los tres tipos anteriores. Como parámetro de investigación, la
confianza del modelo en cada etapa de decisión es un dato relevante para
comparar el comportamiento de distintos modelos y familias de modelos sobre los
mismos hilos de evaluación.

## Decisión

Se añade `confidence: float = 1.0` a `ClassificationResult`,
`InterventionDecision` y `RoleSelection`, siguiendo el patrón ya establecido
en `FacilitationResponse`. Los cuatro tipos de salida del pipeline ahora
incluyen confianza:

```python
class ClassificationResult(BaseModel):
    # ... campos de clasificación ...
    confidence: float = 1.0  # auto-evaluada, 0.0–1.0

class InterventionDecision(BaseModel):
    should_intervene: bool
    reasoning: str
    confidence: float = 1.0

class RoleSelection(BaseModel):
    role: FacilitationRole
    reasoning: str
    confidence: float = 1.0
```

El campo se transmite al modelo mediante la descripción del campo en el esquema
JSON de la herramienta `final_result` (modo `ToolOutput`): no requiere cambios
en el texto de los prompts de instrucciones.

`RunRecord` captura los cuatro valores como campos separados:
`classification_confidence`, `intervention_confidence`, `role_confidence`,
`response_confidence`. La tabla de resumen del experimento muestra las tres
primeras como columnas `c_conf`, `i_conf`, `r_conf`.

## Por qué esta decisión

La confianza auto-evaluada por un LLM no es una estimación calibrada de
probabilidad. Los experimentos previos muestran que `qwen2.5:14b` devuelve
`1.0` en todos los casos observados, independientemente del hilo. Esta
limitación no invalida el uso del campo: como señal relativa, puede revelar
patrones interesantes en comparaciones entre modelos (por ejemplo, si un modelo
muestra confianza uniformemente alta mientras otro varía según el hilo) o en
análisis de tipos de hilo (si los hilos conflictivos generan menor confianza
declarada que los hilos activos).

La alternativa de no incluir el campo en las etapas anteriores implicaría no
disponer de esos datos en las ejecuciones de evaluación. Añadirlos a posteriori
requeriría repetir los experimentos.

## Consecuencias

### Positivas

- `RunRecord` captura la confianza de cada etapa de decisión, no solo de la
  respuesta final. El análisis post-experimento puede cruzar confianza con
  tipo de hilo, modelo, y resultado del pipeline.
- El esquema JSON del campo incluye la descripción "Research parameter only",
  lo que deja claro en el contrato del modelo que el campo no tiene efecto
  operativo.
- El valor por defecto `1.0` es compatible con ejecuciones anteriores:
  los tipos Pydantic que no devuelven el campo obtienen `1.0` automáticamente.

### Negativas

- La confianza auto-evaluada de los LLMs está mal calibrada. Modelos más
  pequeños o con menor seguimiento de instrucciones pueden devolver `1.0`
  sistemáticamente, lo que hace el campo no informativo para esos modelos.
- El campo `confidence` en `RunRecord` se renombró a `response_confidence`
  para consistencia. Esto rompe el esquema JSON de los archivos de resultados
  de ejecuciones anteriores, aunque esos archivos ya están escritos y no se
  procesan automáticamente.

### Cuestiones abiertas

- ¿La varianza de confianza entre modelos es suficientemente informativa para
  justificar incluirla en el análisis comparativo del TFM?
- ¿Conviene añadir una columna de confianza a la tabla de modelos en
  `docs/experiments/models.md` una vez que se tengan resultados de múltiples
  modelos?

## Referencias

- ADR 0021: diseño del evaluador de experimentos; documenta `RunRecord` y el
  esquema de resultados.
- ADR 0012: modo `ToolOutput`; explica cómo las descripciones de campos Pydantic
  se transmiten al modelo mediante el esquema de la herramienta `final_result`.
