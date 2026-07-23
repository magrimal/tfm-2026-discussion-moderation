# ADR 0023: Fixtures de evaluación: selección y diseño de escenarios

**Estado**: Revisado (2026-07-23)
**Fecha original**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0015 (Taxonomía de
estados), ADR 0022 (Backend stub)

## Descripción

El runner de evaluación necesita hilos de discusión representativos para
verificar que el pipeline clasifica correctamente el estado del hilo, decide
sobre la intervención, y genera una respuesta adecuada. Los hilos de evaluación
deben cubrir el espacio de estados del sistema sin ser tan específicos que
solo funcionen con un modelo concreto.

## Decisión

El registro actual contiene dieciocho fixtures en
`evals/fixtures/threads.py`. Los seis originales cubren uno por uno los estados
de discusión de la taxonomía (ADR 0015):

| Fixture | Estado esperado | Escenario |
|---|---|---|
| `new_thread` | NEW | Hilo recién publicado, sin respuestas |
| `active_thread` | ACTIVE | Discusión con intercambio entre pares |
| `stalled_thread` | STALLED | Una sola respuesta, sin actividad en 4 días |
| `conflictive_thread` | CONFLICTIVE | Intercambios agresivos o desestimadores |
| `convergent_thread` | CONVERGENT | Discusión que converge a consenso prematuro |
| `off_topic_thread` | OFF_TOPIC | Hilo que deriva hacia el tema erróneo |

Se definen además dos fixtures orientados a la evaluación de la intervención
completa (nodo de rol y generación de respuesta), uno por cada rol de
facilitación no cubierto por los seis originales:

| Fixture | Estado esperado | Escenario | Rol esperado |
|---|---|---|---|
| `shallow_discourse_thread` | ACTIVE | Participación distribuida pero discurso formulaico | Intelectual |
| `dominated_thread` | ACTIVE | Un participante domina; otros solo asienten | Social |

Cuatro fixtures sintéticos posteriores cubren casos límite que la primera
versión evitaba:

| Fixture | Propósito |
|---|---|
| `declining_vs_never_posted_thread` | Comprobar si se prioriza a quien dejó de participar frente a quien nunca participó |
| `preventive_social_activation_thread` | Detectar deterioro social antes de un conflicto explícito |
| `ambiguous_signals_thread` | Exponer señales que admiten más de una interpretación |
| `dual_state_stalled_off_topic_thread` | Observar la prioridad cuando coinciden estancamiento y desvío temático |

Los seis fixtures restantes cargan hilos anonimizados del corpus MOOC descrito
en ADR 0041: `real_dominated`, `real_explicit_distress`, `real_formulaic`,
`real_hostile_then_silent`, `real_integration_phase` y `real_overt_attack`.
Estos casos incorporan lenguaje escrito por estudiantes, pero no tienen una
etiqueta de referencia validada por varios anotadores.

Todos los hilos usan el mismo contexto de curso (`course-v1:UCM+TFM+2026`) y el
mismo instructor ficticio (`Prof. García`). Los temas son de ética e IA
(privacidad de LLMs, sesgo algorítmico, licencias de código abierto,
regulación de IA, etc.): un dominio familiar para modelos de lenguaje
entrenados en texto académico reciente.

La función `new_thread`, que no tiene comentarios, sirve también para verificar
que el pipeline no interviene cuando el hilo es nuevo (el sistema debe esperar
a que la discusión comience).

### Criterios de diseño

**Estados básicos y casos límite separados.** Los seis fixtures originales
están diseñados para clasificarse sin ambigüedad. Los cuatro sintéticos
posteriores introducen deliberadamente señales solapadas para comprobar cómo
se comporta una taxonomía que obliga a devolver una sola etiqueta.

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

### Rationale para los fixtures de intervención forzada

Los seis fixtures originales producen intervención solo en dos de los seis hilos
(`conflictive` y `off_topic`). Esto deja los nodos de rol y generación de
respuesta sin ejercitar para la mayoría de los escenarios, y los roles
`intelectual` y `social` sin cobertura.

Los dos fixtures adicionales se diseñaron con el objetivo explícito de que el
pipeline tome la decisión de intervenir, y de que el rol activado sea el
esperado. El criterio de diseño es diferente al de los seis originales: no se
busca representatividad del estado de la discusión, sino cobertura del pipeline
completo y de los roles restantes.

`shallow_discourse_thread` representa un hilo ACTIVE con participación
distribuida pero discurso formulaico: varios estudiantes postean, pero ninguno
desarrolla argumentos, cita evidencia ni conecta ideas. La calidad del discurso
es la señal de intervención, no el estado de actividad. El rol esperado es
intelectual, que actúa cuando la profundidad del razonamiento es insuficiente
para los objetivos de aprendizaje.

`dominated_thread` representa un hilo ACTIVE donde un estudiante postea tres
veces con contenido sustantivo y los demás solo asienten brevemente. El
contenido es de buena calidad, pero la distribución de la participación es
desequilibrada y los demás estudiantes no encuentran espacio para contribuir.
El rol esperado es social, que actúa sobre dinámicas de participación y
presencia social.

Estos fixtures no pretenden ser representativos del espacio de discusiones
posibles. Están diseñados para dar datos sobre el comportamiento del pipeline
en la parte del proceso que los seis fixtures originales no ejercitan.

### Lo que los fixtures no verifican

Los fixtures verifican la **compatibilidad del modelo con el pipeline** y
permiten comparar la etiqueta obtenida con la esperada cuando esa referencia
existe. No verifican la calidad pedagógica de las
respuestas generadas. Esta distinción es explícita en ADR 0020 (marco de
evaluación pedagógica).

Un modelo que clasifica correctamente los seis hilos y completa el pipeline sin
error puede aun así generar respuestas pedagógicamente inadecuadas. Los fixtures
son una cota mínima de validación, no el criterio de calidad final.

## Consecuencias

### Positivas

- Seis fixtures cubren todos los estados básicos; otros seis sintéticos amplían
  la cobertura de intervención y ambigüedad, y seis casos del corpus real
  permiten observar el comportamiento sobre lenguaje no escrito para la prueba.
- Los fixtures están definidos en Python, no en ficheros externos: son
  versionados, revisables en code review, y reproducibles sin dependencias.
- El tiempo de referencia fijo (`NOW`) garantiza que los timestamps no cambian
  entre ejecuciones, lo que hace los resultados comparables entre modelos y
  entre fechas.
- El dominio (IA ética) es coherente con el contexto académico del TFM y
  conocido por todos los modelos evaluados.

### Negativas

- Dieciocho hilos siguen siendo insuficientes para conclusiones estadísticas
  sobre el comportamiento del sistema, y solo ocho tienen una referencia
  usada en el experimento principal.
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
  temática), cuando la evaluación pedagógica lo justifique? Los dos fixtures
  de intervención añadidos en 2026-05-03 responden parcialmente a esta
  pregunta para los roles intelectual y social, pero no cubren variantes
  de los estados originales.
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
