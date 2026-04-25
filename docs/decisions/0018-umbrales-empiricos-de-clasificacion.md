# ADR 0018: Umbrales empíricos de clasificación

**Estado**: Propuesto (pendiente de calibración empírica)
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0008 (Principios de
temporización), ADR 0015 (Taxonomía de estados)

## Descripción

La clasificación del estado de un hilo requiere criterios operacionales: ¿cuánto
tiempo sin actividad constituye un hilo estancado? ¿Cuándo la participación es
"dominada" y no simplemente asimétrica? ¿Qué distingue una trayectoria
"en declive" de una "estable"?

Estos criterios están parcialmente implícitos en el prompt del clasificador y
parcialmente externalizados como parámetros de configuración. Ninguno está
fundamentado empíricamente en este sistema. Esta decisión documenta los umbrales
actuales, su origen, y las preguntas de calibración pendientes.

## Umbrales actuales y su origen

### Umbral de estancamiento: 48 horas

El `ClassificationAgent` recibe `stalled_threshold_hours` (por defecto 48,
configurable via `FACILITATION_STALLED_THRESHOLD_HOURS`) e incluye este valor
literalmente en el prompt:

```
Stalled threshold: {stalled_threshold} hours without new posts
[...]
- stalled: No new posts for {stalled_threshold}+ hours.
```

**Origen**: convenio razonable para foros académicos semanales; no está citado
en la literatura revisada. Rovai (2007) y VanLehn (2011) establecen el
principio de intervenir en el impasse, no en el silencio, pero no definen un
umbral temporal. El valor de 48h es configurable precisamente porque no hay
base empírica para fijarlo.

**Interacción con el tipo de curso**: en un curso intensivo de una semana,
48h puede ser excesivo; en un curso semestral con actividad semanal, puede ser
insuficiente. El umbral correcto depende del ritmo del curso, no de una
constante universal.

### Participación dominada: criterio cualitativo en prompt

`ParticipationBalance.DOMINATED` se define en el prompt como:

```
- dominated: One or two voices account for most posts; others
  are largely silent or respond only to the instructor.
```

No hay umbral cuantitativo (por ejemplo, "un participante representa más del
60% de los mensajes"). El criterio es cualitativo y depende del razonamiento
del modelo. Distintos modelos pueden interpretar "most posts" de forma diferente.

**Origen**: Rovai (2007) identifica la participación distribuida como marcador
de presencia social, pero no define un umbral numérico. Ho y Swan (2007)
sugieren que la calidad del discurso —no solo la distribución— predice el
engagement futuro.

### Trayectoria en declive: criterio relativo sin ventana temporal

`DiscussionTrajectory.DECLINING` se define como:

```
- declining: Was more active; pace is slowing or has stopped.
```

No hay ventana temporal ni criterio cuantitativo de tasa de cambio. El modelo
infiere "era más activo" comparando el ritmo reciente con el histórico visible
en el contexto, lo que depende de cuántos mensajes se proporcionan y de cuándo
se ejecuta el clasificador.

**Origen**: Chang y Danescu-Niculescu-Mizil (2019), citados en ADR 0008, muestran
que la trayectoria predice el comportamiento futuro mejor que el estado puntual.
No definen umbrales cuantitativos.

### Calidad del discurso: criterio cualitativo

`DiscourseQuality` (SUBSTANTIVE / MIXED / FORMULAIC) se define en el prompt
con descripciones cualitativas. No hay métricas de longitud, densidad léxica
o presencia de evidencia. El modelo evalúa la calidad discursiva por su
comprensión del texto, no por reglas explícitas.

## Implicación para la evaluación

Los umbrales cualitativos hacen que la clasificación sea sensible al modelo:
dos modelos pueden clasificar el mismo hilo de forma diferente no porque uno
sea más preciso, sino porque interpretan "dominado" o "en declive" de forma
distinta. Esto dificulta la comparación entre modelos y la interpretación de
los resultados de evaluación.

El umbral de 48h es el único parámetro cuantitativo explícito. Los demás son
implícitos en la descripción del prompt.

## Decisión provisional

Los umbrales actuales se mantienen sin modificar hasta que haya datos
suficientes para calibrarlos. Las razones:

1. Cambiar los umbrales ahora, sin datos de evaluación, es especulativo.
2. El umbral de 48h está externalizado como parámetro de configuración
   precisamente para facilitar la experimentación.
3. Los criterios cualitativos son apropiados para la fase de prototipo: un
   modelo grande puede inferir "declive" con más precisión que una regla fija
   basada en conteos.

La calibración empírica es un objetivo explícito de la fase de evaluación
de la tesis.

## Consecuencias

### Positivas

- El umbral de estancamiento es configurable sin cambios de código, lo que
  facilita la experimentación con distintos valores.
- Los criterios cualitativos son flexibles y se adaptan a contextos distintos
  sin necesidad de definir reglas para cada caso.

### Negativas

- Los resultados de clasificación no son completamente reproducibles entre
  modelos: el mismo hilo puede recibir estados distintos dependiendo de cómo
  cada modelo interpreta los criterios cualitativos.
- Sin umbrales cuantitativos para participación y trayectoria, no es posible
  escribir aserciones deterministas en los tests de clasificación. Los tests
  actuales validan la estructura del output, no la corrección semántica.
- El valor de 48h carece de justificación en la literatura. Si se cita en
  la tesis, debe declararse como convenio, no como parámetro fundamentado.

### Cuestiones abiertas

- ¿Cuál es el umbral de estancamiento apropiado para los escenarios de
  evaluación de la tesis? Los fixtures actuales no dependen de tiempo real,
  pero los hilos reales sí.
- ¿Debe añadirse un umbral cuantitativo para "dominado" (por ejemplo,
  porcentaje de mensajes de un único autor)?
- ¿Qué ventana temporal define "era más activo" para la trayectoria? ¿Los
  últimos N mensajes? ¿Las últimas K horas?
- ¿Debe el clasificador recibir metadatos cuantitativos del hilo (número de
  mensajes por autor, timestamps, tasa de respuesta) además del texto, para
  reducir la dependencia de la interpretación cualitativa del modelo?

## Referencias

- Chang, J. P., & Danescu-Niculescu-Mizil, C. (2019). Trajectories of blocked
  community members. *Proceedings of the Web Conference 2019*.
- Ho, C. H., & Swan, K. (2007). Evaluating online conversation in an
  asynchronous learning environment. *The Internet and Higher Education*,
  10(1), 3-10.
- Rovai, A. P. (2007). Facilitating online discussions effectively. *The
  Internet and Higher Education*, 10(1), 77-88.
- VanLehn, K. (2011). The relative effectiveness of human tutoring,
  intelligent tutoring systems, and other tutoring systems. *Educational
  Psychologist*, 46(4), 197-221.
