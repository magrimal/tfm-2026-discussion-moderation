# ADR 0023: Fixtures de evaluación: selección y diseño de escenarios

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0015 (Taxonomía de
estados), ADR 0022 (Backend stub)

## Descripción

El runner de evaluación necesita hilos de discusión representativos para
verificar que el pipeline clasifica correctamente el estado del hilo, decide
sobre la intervención, y genera una respuesta adecuada. Los hilos de evaluación
deben cubrir el espacio de estados del sistema sin ser tan específicos que
solo funcionen con un modelo concreto.

## Decisión

Se definen seis fixtures de hilo en `evals/fixtures/threads.py`, uno por estado
de discusión de la taxonomía (ADR 0015):

| Fixture | Estado esperado | Escenario |
|---|---|---|
| `new_thread` | NEW | Hilo recién publicado, sin respuestas |
| `active_thread` | ACTIVE | Discusión con intercambio entre pares |
| `stalled_thread` | STALLED | Una sola respuesta, sin actividad en 4 días |
| `conflictive_thread` | CONFLICTIVE | Intercambios agresivos o desestimadores |
| `convergent_thread` | CONVERGENT | Discusión que converge a consenso prematuro |
| `off_topic_thread` | OFF_TOPIC | Hilo que deriva hacia el tema erróneo |

Los seis hilos usan el mismo contexto de curso (`course-v1:UCM+TFM+2026`) y el
mismo instructor ficticio (`Prof. García`). Los temas son de ética e IA
(privacidad de LLMs, sesgo algorítmico, licencias de código abierto,
regulación de IA, etc.): un dominio familiar para modelos de lenguaje
entrenados en texto académico reciente.

La función `new_thread`, que no tiene comentarios, sirve también para verificar
que el pipeline no interviene cuando el hilo es nuevo (el sistema debe esperar
a que la discusión comience).

### Criterios de diseño

**Un fixture por estado, sin solapamiento.** Cada fixture está diseñado para
clasificarse sin ambigüedad en un estado. No se persigue cubrir casos límite
ni estados combinados: la taxonomía de un solo estado (ADR 0015) hace que
los casos límite sean imposibles por diseño.

**Participación realista, no mínima.** Los hilos con comentarios incluyen
intercambios entre participantes con nombres, citas de ideas previas, y
variación en longitud y tono. Esto evita que el modelo clasifique por heurísticas
simples como la ausencia o presencia de mensajes.

**Temas con contenido sustantivo.** Los temas son debates reales en el campo de
la IA ética. El modelo no necesita conocimiento especializado para razonar
sobre ellos, pero los hilos tienen suficiente contenido para que el clasificador
tenga información real sobre la calidad del discurso.

**Timestamps coherentes con el estado.** El hilo estancado tiene actividad de
hace 4 días (supera el umbral de 48h de ADR 0018). El hilo activo tiene mensajes
de las últimas horas. El tiempo de referencia es `NOW = datetime(2026, 3, 12,
14:00, UTC)`, un valor fijo para reproducibilidad.

**Objetivos de aprendizaje explícitos.** Todos los hilos incluyen
`learning_objectives`, que el pipeline usa para evaluar la coherencia entre la
discusión y los objetivos del instructor.

### Lo que los fixtures no verifican

Los fixtures verifican la **compatibilidad del modelo con el pipeline** y la
**coherencia de la clasificación**. No verifican la calidad pedagógica de las
respuestas generadas. Esta distinción es explícita en ADR 0020 (marco de
evaluación pedagógica).

Un modelo que clasifica correctamente los seis hilos y completa el pipeline sin
error puede aun así generar respuestas pedagógicamente inadecuadas. Los fixtures
son una cota mínima de validación, no el criterio de calidad final.

## Consecuencias

### Positivas

- Seis fixtures cubren todos los estados de la taxonomía con una ejecución de
  evaluación completa. El resultado es binario por fixture: éxito o error.
- Los fixtures están definidos en Python, no en ficheros externos: son
  versionados, revisables en code review, y reproducibles sin dependencias.
- El tiempo de referencia fijo (`NOW`) garantiza que los timestamps no cambian
  entre ejecuciones, lo que hace los resultados comparables entre modelos y
  entre fechas.
- El dominio (IA ética) es coherente con el contexto académico del TFM y
  conocido por todos los modelos evaluados.

### Negativas

- Seis hilos son insuficientes para conclusiones estadísticas sobre el
  comportamiento del sistema. Son suficientes para descartar modelos
  incompatibles, no para comparar modelos compatibles entre sí.
- Los temas elegidos pueden estar representados de forma desigual en los datos
  de entrenamiento de distintos modelos, lo que introduce varianza no controlada
  en los resultados de clasificación.
- Un único fixture por estado no detecta si el modelo clasifica correctamente
  por razonamiento o por coincidencia. Un modelo que clasifica el hilo estancado
  correctamente porque "tiene pocos mensajes" y el activo correctamente porque
  "tiene muchos" puede fallar en un hilo con mucha actividad pero estancado
  por falta de profundidad temática.
- Los hilos no cubren variantes de cada estado. El hilo conflictivo representa
  conflicto abierto; el ADR 0015 señala que el sistema no detecta dinámicas
  de silenciamiento más sutiles (Rovai, 2007).

### Cuestiones abiertas

- ¿Debe añadirse un fixture por cada variante relevante de cada estado (por
  ejemplo, hilo estancado por falta de replies vs. estancado por desviación
  temática), cuando la evaluación pedagógica lo justifique?
- ¿Deben los fixtures incluir metadatos cuantitativos adicionales (número de
  mensajes por autor, tasa de respuesta) para reducir la dependencia de la
  clasificación cualitativa (ADR 0018)?
- ¿Cuántos fixtures son necesarios para que los resultados sean estadísticamente
  significativos en la evaluación de la tesis? La respuesta depende del marco
  de evaluación (ADR 0020).

## Referencias

- ADR 0003: modelo de intervención; define los estados y condiciones de
  intervención que los fixtures deben cubrir.
- ADR 0015: taxonomía de estados; define los seis valores de `DiscussionState`.
- ADR 0018: umbrales empíricos; el umbral de 48h que hace que `stalled_thread`
  sea clasificable como estancado.
- ADR 0020: marco de evaluación pedagógica; distingue compatibilidad del modelo
  de calidad de respuesta.
