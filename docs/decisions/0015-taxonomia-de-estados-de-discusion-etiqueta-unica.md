# ADR 0015: Taxonomía de estados de discusión con etiqueta única

**Estado**: Aceptado (con cuestiones abiertas)
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0004 (Roles de
facilitación)

## Descripción

El modelo de intervención en tres fases requiere que el `ClassificationAgent`
asigne un estado a cada hilo antes de decidir si intervenir y cómo. La
taxonomía de estados es, por tanto, el vocabulario de entrada del pipeline:
determina qué intervenciones son posibles, qué rol se activa, y qué técnicas
están disponibles.

Dos decisiones de diseño en esta taxonomía no estaban documentadas y tienen
implicaciones directas para la validez del sistema:

1. La clasificación asigna **una única etiqueta** por hilo, aunque un hilo
   pueda reunir condiciones de varios estados simultáneamente.
2. El estado `CONFLICTIVE` cubre conflicto abierto pero no dinámicas de
   silenciamiento más sutiles documentadas en la literatura.

## Decisión

### Etiqueta única por hilo

`DiscussionState` es un `StrEnum` con seis valores mutuamente excluyentes:
`new`, `active`, `stalled`, `conflictive`, `convergent`, `off_topic`. El
clasificador asigna exactamente uno por ejecución.

Esta restricción es deliberada, no una limitación técnica. Las razones:

1. **Determinismo de la intervención**: cada estado mapea a un conjunto de
   roles y técnicas en el orquestador (ADR 0004). Con etiqueta única, la
   selección de intervención es determinista y auditable. Con múltiples
   etiquetas, se necesitarían reglas de prioridad o un orquestador capaz
   de combinar intervenciones, lo que añade complejidad sin evidencia de
   que mejore el resultado.

2. **Simplicidad del prompt de clasificación**: el clasificador recibe una
   instrucción clara con seis opciones. Un esquema multi-etiqueta requeriría
   instrucciones más complejas y aumentaría la probabilidad de errores de
   formato en el output.

3. **Correspondencia con la práctica de ITS**: los sistemas de tutoría
   inteligente de referencia (ADR 0006) también asignan un único estado de
   estudiante y activan una única intervención por ciclo. No hay evidencia en
   la literatura revisada de que la multi-etiqueta mejore la calidad de la
   facilitación.

#### Caso conocido: STALLED + OFF_TOPIC

Un hilo puede estar tanto estancado (sin actividad reciente) como fuera de
tema. Con etiqueta única, el clasificador debe elegir. La elección afecta la
intervención:

- Si elige `stalled`, el sistema interviene para reactivar el hilo sin
  abordar la desviación temática.
- Si elige `off_topic`, el sistema interviene para redirigir el tema sin
  abordar el estancamiento.

La decisión de diseño es que **el clasificador priorice la condición más
relevante para el aprendizaje**. El prompt incluye criterios de prioridad
implícitos en la definición de cada estado. Esta lógica de priorización no
está actualmente explicitada como regla formal; es parte del razonamiento del
modelo.

### Alcance de `CONFLICTIVE`

El estado `CONFLICTIVE` cubre intercambios con conflicto abierto o tono hostil.
Rovai (2007) identifica también dinámicas de silenciamiento más sutiles:
participantes que dominan el espacio de forma competitiva o dismissiva sin
cruzar al conflicto explícito. Estas dinámicas están parcialmente cubiertas
por `ParticipationBalance.DOMINATED`, que el clasificador captura como campo
separado, no como estado de discusión.

La decisión de no crear un estado separado para silenciamiento sutil se basa
en que `DOMINATED` ya lo captura como dimensión y el rol social lo aborda. Un
séptimo estado aumentaría la complejidad sin ganancia clara en la selección
de intervención.

## Consecuencias

### Positivas

- La selección de intervención es determinista: dado un estado, el orquestador
  sabe qué roles considerar.
- Los prompts del clasificador y el orquestador son directos: seis opciones,
  sin lógica de combinación.
- La evaluación de experimentos es más limpia: el estado asignado por el
  modelo se puede comparar directamente con el estado esperado del fixture.

### Negativas

- Los hilos con condiciones múltiples simultáneas reciben una intervención
  parcial: la condición no elegida no se aborda explícitamente.
- La lógica de priorización entre estados es implícita en el prompt, no
  declarada como regla. Distintos modelos pueden priorizar de forma diferente
  sin que el sistema lo detecte.
- Si la priorización implícita es sistemáticamente errónea (por ejemplo, el
  modelo siempre prefiere `off_topic` sobre `stalled`), el historial de
  evaluaciones no lo revela directamente.

### Cuestiones abiertas

- ¿Debe explicitarse la priorización entre estados en el prompt del
  clasificador como reglas ordenadas? Por ejemplo: `off_topic > conflictive >
  stalled > active > convergent > new`. Esto daría consistencia entre modelos
  pero podría sobreajustar la clasificación a los fixtures actuales.
- ¿Es necesario un campo `secondary_state` opcional en `ClassificationResult`
  para capturar la condición secundaria sin cambiar el flujo de intervención?
  Permitiría auditabilidad sin multi-etiqueta completa.
- ¿Las dinámicas de silenciamiento sutil de Rovai (2007) están suficientemente
  cubiertas por la combinación `DOMINATED + rol social`, o requieren un estado
  propio para ser detectadas con fiabilidad?

## Alternativas consideradas

- **Multi-etiqueta con prioridad fija**: el clasificador asigna todas las
  condiciones presentes y el orquestador las ordena por prioridad predefinida.
  Descartado: añade complejidad al orquestador y no hay evidencia de que mejore
  el resultado en la literatura revisada.
- **Multi-etiqueta con intervención combinada**: el sistema genera una
  intervención que aborda múltiples condiciones. Descartado: el principio de
  mínima intervención (ADR 0003, ADR 0008) y el constraint de una acción por
  intervención (ADR 0009) son incompatibles con intervenciones combinadas.
- **Estado `SILENCED` independiente**: un séptimo estado para dinámicas de
  silenciamiento sutil. Descartado en esta fase porque `DOMINATED` captura
  la señal y el rol social la aborda; añadir el estado requeriría fixtures
  adicionales y evidencia de que la separación mejora la intervención.

## Referencias

- Garrison, D. R., Anderson, T., & Archer, W. (2000). Critical inquiry in a
  text-based environment. *The Internet and Higher Education*, 2(2-3), 87-105.
- Ho, C. H., & Swan, K. (2007). Evaluating online conversation in an
  asynchronous learning environment. *The Internet and Higher Education*,
  10(1), 3-10.
- Rovai, A. P. (2007). Facilitating online discussions effectively. *The
  Internet and Higher Education*, 10(1), 77-88.
- VanLehn, K. (2011). The relative effectiveness of human tutoring,
  intelligent tutoring systems, and other tutoring systems. *Educational
  Psychologist*, 46(4), 197-221.
