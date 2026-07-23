# ADR 0008: Principios de temporización de la intervención

**Estado**: Propuesto
**Fecha**: 2026-03-30
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0006 (Sistemas de
referencia para patrones del pipeline)

## Descripción

ADR 0003 establece que la Fase 1 del modelo de intervención debe decidir si
intervenir o no, y que la no-intervención es un resultado válido. Sin embargo,
no especifica qué principios gobiernan esa decisión más allá de las categorías
de estado de la discusión.

La revisión de literatura adicional - en particular la investigación sobre
sistemas de tutoría inteligente, facilitación de discusiones en línea y sistemas
de agentes - identifica un conjunto convergente de principios sobre cuándo
intervenir que no estaban explícitos en el modelo original. Estos principios son
transversales a todos los roles (ADR 0004) y deben guiar el diseño del nodo
clasificador (ADR 0005).

## Decisión

Adoptar los siguientes seis principios de temporización como restricciones
explícitas del modelo de intervención, vinculantes para el clasificador y para
todos los roles de facilitación.

---

### Principio 1: Intervenir en el impasse, no en el silencio

Un hilo sin publicaciones nuevas no equivale a un hilo que necesita
intervención. El silencio puede significar reflexión activa en curso. El
impasse es el estado en que el hilo no puede avanzar sin entrada externa - los
participantes han agotado sus recursos disponibles sin alcanzar nuevo
conocimiento.

La intervención es efectiva en el impasse. La intervención antes del impasse
interrumpe la lucha productiva que genera aprendizaje profundo.

**Evidencia**:
- VanLehn (2011) demuestra que los sistemas de tutoría que intervienen a nivel
  de paso (*step-based*) - es decir, en el impasse de cada paso - producen
  efectos equivalentes a la tutoría humana (d≈0.76). Los sistemas que solo
  intervienen al final de la tarea (*answer-based*) producen efectos
  significativamente menores.
- Kapur (2016) documenta el efecto de fallo productivo: los estudiantes que
  trabajan un problema sin asistencia antes de recibir instrucción obtienen
  mejores resultados de transferencia que los que reciben instrucción primero.
  La instrucción prematura suprime el proceso generativo que prepara al
  aprendiz.

**Implicación para el sistema**: el umbral de intervención no es temporal
(*"X horas sin publicaciones"*) sino de estado (*"los participantes no pueden
avanzar sin entrada externa"*). El tiempo sin publicaciones es una señal
necesaria pero no suficiente.

---

### Principio 2: Trayectoria sobre estado puntual

El estado actual del hilo es insuficiente para tomar la decisión de
intervención. Un hilo que estaba activo y ha decaído requiere una respuesta
diferente a un hilo que nunca despegó, aunque ambos presenten el mismo estado
en el momento de la clasificación.

El clasificador debe describir la trayectoria del hilo - no solo su estado
actual - para que los agentes de rol dispongan de este contexto. Esta
descripción va en el campo de razonamiento de la clasificación, no requiere
un campo estructurado adicional.

**Evidencia**:
- Chang & Danescu-Niculescu-Mizil (2019) demuestran que el descarrilamiento
  conversacional puede predecirse antes de que ocurra, siguiendo la trayectoria
  del tono y el contenido a lo largo de la conversación. Un modelo que evalúa
  solo el estado puntual pierde esta señal predictiva.
- La distinción silencio-vs-impasse (Principio 1) también depende de la
  trayectoria: un hilo que era activo y se ha estancado tiene más probabilidad
  de estar en impasse genuino que uno que nunca tuvo actividad.

---

### Principio 3: Preferir los falsos negativos a los falsos positivos

El coste de una intervención innecesaria supera el coste de una oportunidad
de intervención perdida. Una intervención cuando no era necesaria:

- Desplaza la interacción de centrada en el estudiante a centrada en el
  facilitador.
- Puede interrumpir un proceso de aprendizaje en curso.
- Entrena a los participantes a ignorar intervenciones futuras (efecto de
  saturación).

Una intervención perdida simplemente significa que el hilo avanza sin
asistencia, que es el estado deseable por defecto.

**Evidencia**:
- Rovai (2007) documenta empíricamente que la sobreintervención del instructor
  suprime la voz estudiantil y convierte las discusiones en intercambios
  centrados en el instructor.
- An et al. (2009) muestran que el grupo con intervención mínima del instructor
  produjo la mayor interacción estudiantil y la presencia social más alta.
- Anthropic (2025) articula el principio de huella mínima para agentes
  autónomos: preferir acciones reversibles y de menor alcance; errar hacia
  hacer menos y confirmar.

---

### Principio 4: Abstenerse bajo ambigüedad

Cuando las señales del hilo son ambiguas - el estado no es claramente
problemático en ninguna dimensión - la respuesta correcta es no intervenir.
La abstención es una política coherente, no un fallo del sistema.

Generar una intervención de baja confianza porque "algo podría estar mal" es
peor que no intervenir: aplica una técnica potencialmente incorrecta al estado
incorrecto.

**Evidencia**:
- Koedinger & Aleven (2007) formalizan el dilema de asistencia: la cantidad
  óptima de asistencia depende del estado del aprendiz, y proporcionar asistencia
  cuando no se necesita produce los mismos efectos negativos que no
  proporcionarla cuando sí se necesita.
- Korre et al. (2025, §6.1) señalan que intervenir innecesariamente puede
  aumentar la toxicidad de la discusión.

---

### Principio 5: Respetar el cooldown entre intervenciones

No re-intervenir en un hilo hasta que los participantes hayan tenido
oportunidad de responder a la intervención anterior. La frecuencia de
intervención tiene un efecto acumulativo: intervenciones múltiples en poco
tiempo desplazan la discusión de centrada en el estudiante a centrada en el
facilitador, independientemente de la calidad de cada intervención individual.

**Evidencia**:
- Rovai (2007) documenta la sobreintervención como anti-patrón específico.
  El consejo de "publicar al menos un mensaje diario" tiene como contrapartida
  implícita no publicar en exceso.
- La investigación en sistemas de recomendación documenta efectos de saturación
  (Afsar et al., 2022): intervenciones del mismo tipo repetidas dentro de la
  misma sesión tienen rendimiento decreciente.

**Implicación de implementación**: el clasificador debe consultar el historial
de intervenciones del hilo (ADR 0007 - ThreadHistoryStore) antes de decidir
intervenir.

---

### Principio 6: Escalada gradual de intensidad

Cuando se decide intervenir, empezar por el nivel mínimo de asistencia y
escalar solo cuando el nivel anterior no ha producido avance. No saltar al
nivel de mayor asistencia porque sea más fácil de generar o más visible.

Este principio es especialmente relevante para el rol intelectual, donde la
escalera EMT (pump → hint → prompt → assertion) proporciona cuatro niveles
explícitos (ADR 0046, §2.2; ADR 0004). Sin embargo, el principio aplica
también a los roles social y organizacional: comenzar por la técnica más
suave del repertorio antes de escalar.

**Evidencia**:
- Lippert et al. (2020) documentan la escalera EMT en sistemas de tutoría
  inteligente multi-agente: el tutor empieza con pump (elicitación abierta),
  solo pasa a hint si el pump no produce avance, y así sucesivamente.
- Korre et al. (2025) proponen una escalera de escalación equivalente para
  facilitación de discusiones: desde reconocimiento silencioso hasta
  instrucción directa.
- Koedinger & Aleven (2007) muestran empíricamente que el andamiaje excesivo
  produce los mismos efectos negativos que la ausencia de andamiaje.

**Implicación de implementación**: la aplicación completa de este principio
en el rol intelectual requiere conocer qué nivel EMT se usó en intervenciones
anteriores del mismo hilo (ADR 0007 - ThreadHistoryStore).

---

## Relación con otros ADR

| ADR | Relación |
|-----|---------|
| ADR 0046 | El repertorio de técnicas incluye los niveles EMT (§2.2) y la tabla de disparadores proactivos (§5) que operacionalizan estos principios |
| ADR 0003 | El modelo de tres fases implementa estos principios: la Fase 1 es donde el clasificador los aplica |
| ADR 0004 | Los roles tienen restricciones de temporización específicas derivadas de estos principios |
| ADR 0006 | Los sistemas de referencia (agentes de código, ITS) son la fuente de los patrones que estos principios formalizan |
| ADR 0007 | El historial de intervenciones es la infraestructura que habilita los Principios 5 y 6 |

## Consecuencias

### Positivas

- Los principios son explícitos, citados y por tanto evaluables: es posible
  medir si el sistema los cumple o los viola.
- Proporcionan criterio para diseñar los casos de prueba del clasificador:
  un hilo activo nunca debería generar intervención; un hilo con cooldown
  activo tampoco.
- Justifican el diseño de `ThreadHistoryStore` (ADR 0007) con fundamento en
  la literatura, no solo como decisión técnica.
- Unifican bajo un marco coherente decisiones que de otro modo aparecerían
  dispersas en la implementación de cada rol.

### Negativas

- Los umbrales concretos (¿cuánto tiempo define un cooldown? ¿cuándo es
  genuino un impasse?) no están determinados por los principios - requieren
  calibración empírica que el PoC no puede proporcionar aún.
- El Principio 1 (intervenir en el impasse) es más difícil de operacionalizar
  que un umbral temporal. El clasificador necesita inferir el impasse a partir
  del texto, lo cual es una tarea de mayor complejidad que contar horas.
- El Principio 6 (escalada gradual) en el rol intelectual asume que las
  intervenciones anteriores fueron recibidas y leídas. Si un estudiante no
  vio el pump anterior, escalar al hint puede parecer descontextualizado.

### Cuestiones abiertas

- ¿Cuál es el periodo de cooldown por defecto y debe ser configurable por
  rol, por curso o globalmente?
- ¿Cómo se detecta empíricamente el impasse en una discusión asíncrona de
  texto? ¿Qué señales textuales lo indican?
- ¿Cómo se evalúa si el sistema aplica estos principios correctamente? ¿Qué
  métricas lo capturan?

## Referencias

- Afsar, M. M., Crump, T., & Far, B. (2022). Reinforcement learning based
  recommender systems: A survey. *ACM Computing Surveys*, 55(7), Article 145.
- An, H., Shin, S., & Lim, K. (2009). The effects of different instructor
  facilitation approaches on students' interactions during asynchronous online
  discussions.
- Anthropic (2025). Model specification for Claude.
- Chang, J. P., & Danescu-Niculescu-Mizil, C. (2019). Trouble on the horizon:
  Forecasting the derailment of online conversations as they develop.
  *Proceedings of EMNLP-IJCNLP 2019*, pp. 4743-4754.
- Kapur, M. (2016). Examining productive failure, productive success,
  unproductive failure, and unproductive success in learning. *Instructional
  Science*, 44(4), 379-401.
- Koedinger, K. R., & Aleven, V. (2007). Exploring the assistance dilemma in
  experiments with cognitive tutors. *Educational Psychology Review*, 19(3),
  239-264.
- Korre, K., Tsirmpas, D., Gkoumas, N., Cabalé, E., Kontarinis, D., Myrtzani,
  D., Evgeniou, T., Androutsopoulos, I., & Pavlopoulos, J. (2025). Evaluation
  and facilitation of online discussions in the LLM era: A survey.
  *arXiv:2503.01513*.
- Lippert, A., Shubeck, K., Morgan, B., Hampton, A., & Graesser, A. (2020).
  Multiple agent designs in conversational intelligent tutoring systems.
  *Technology, Knowledge and Learning*, 25, 443-463.
- Rovai, A. P. (2007). Facilitating online discussions effectively.
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent
  tutoring systems, and other tutoring systems. *Educational Psychologist*,
  46(4), 197-221.
