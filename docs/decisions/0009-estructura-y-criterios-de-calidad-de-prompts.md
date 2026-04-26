# ADR 0009: Estructura y criterios de calidad de los prompts de agente

**Estado**: Revisado (2026-04-26)
**Fecha original**: 2026-04-03
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0012 (Modo de extracción de salida estructurada)

## Descripción

El sistema de facilitación está compuesto por dos tipos de agentes: agentes
internos del pipeline (clasificador, decisión de intervención, selección de
rol) y agentes de salida visible (agentes de rol, generación de respuesta).
Cada agente necesita un prompt que defina su identidad, sus límites de
comportamiento, el contexto de ejecución y sus instrucciones de tarea.

Sin criterios comunes, cada agente tiende a mezclar estas responsabilidades:
personalidad con restricciones, instrucciones con formato de salida,
contexto con directiva de tarea. Esta mezcla dificulta la revisión, la
evaluación independiente y la evolución del sistema.

La literatura reciente sobre diseño de prompts para LLMs y agentes
pedagógicos proporciona criterios concretos. Esta ADR los recoge y los
adapta a los dos tipos de agentes del pipeline.

**Nota sobre el modo de extracción de salida (revisión 2026-04-26):** tras la
migración a `ToolOutput` (ADR 0012), el esquema de salida (nombres de campo,
tipos, valores de enum, descripciones de `Field`) viaja al modelo como parte
de la definición de la herramienta `final_result`, no como texto en el system
prompt. El componente TASK ya no necesita ni debe definir los campos de salida
desde cero; su función es proveer guía semántica (cómo razonar, cómo distinguir
valores próximos) que el esquema solo no puede expresar.

## Marco teórico

### Componentes canónicos de un prompt

El análisis de plantillas de prompt en aplicaciones LLM reales (Jiang et al.
2025, sobre 4000+ prompts de producción) identifica cuatro componentes
recurrentes:

- **Directive**: la instrucción de tarea (qué hacer).
- **Context**: información de fondo que el agente necesita.
- **Output format/style**: cómo estructurar la respuesta.
- **Constraints**: qué no hacer, límites de comportamiento.

A estos se añade, en sistemas multi-agente, un componente de identidad:

- **Persona/Role**: quién es el agente (Langchain et al. 2502.02533;
  conversation routines, 2501.11613).

### El efecto real de la persona en LLMs

Zheng et al. (EMNLP 2024) evaluaron 162 roles en 4 familias de LLMs sobre
tareas de conocimiento factual. Conclusión: las personas en el system prompt
no mejoran el rendimiento en tareas de precisión factual. Lo que sí afectan
es el tono, el estilo y el registro de la respuesta.

Consecuencia directa para este sistema:

- **Agentes internos** (clasificador, intervención, selección de rol):
  producen datos estructurados consumidos por el siguiente nodo. La precisión
  es lo que importa. Una persona elaborada no aporta nada y añade ruido.
  Persona mínima: rol epistémico en una o dos frases.
- **Agentes de salida visible** (agentes de rol): producen texto que lee un
  estudiante. El tono, la calidez, la postura epistémica y el registro son
  el producto. Una persona rica y coherente con el rol pedagógico sí importa
  y es el mecanismo correcto para lograrlo.

### Separación de identidad y comportamiento

En sistemas multi-agente, la separación entre lo que un agente *es* y lo
que un agente *hace* es condición para la evaluación independiente de cada
nodo (Lippert et al. 2020; arxiv 2502.02533). Mezclar identidad con
restricciones o instrucciones produce agentes cuyo comportamiento es difícil
de predecir y de corregir de forma quirúrgica.

---

## Decisión

Estructurar todos los prompts de agente en cuatro componentes con
responsabilidades no solapadas. El contenido de cada componente varía según
el tipo de agente.

---

### Componente 1: PERSONA

Define quién es el agente: su identidad, su postura y, para agentes de
salida visible, el carácter que da forma a cómo comunica.

#### Para agentes internos del pipeline

La persona es mínima. Solo establece el rol epistémico del agente: desde
qué perspectiva lee el input. Zheng et al. (2024) confirman que elaborar
más no mejora la salida estructurada.

**Criterios:**

- [ ] Una o dos frases como máximo.
- [ ] Establece quién es el agente en términos de perspectiva o rol
  ("científico del aprendizaje", "evaluador de conversación").
- [ ] No incluye restricciones de comportamiento (van en CONSTRAINTS).
- [ ] No describe el propósito del agente en el pipeline (va en CONSTRAINTS
  o TASK).

**Ejemplo** (agente clasificador):

> You are a learning scientist reading an asynchronous academic discussion
> thread.

#### Para agentes de salida visible

La persona es el mecanismo principal para dar forma al tono, el registro y
la postura del agente. Debe capturar el carácter del rol pedagógico que
representa.

**Criterios:**

- [ ] Describe el carácter del agente: su rasgo central, su forma de ver
  la conversación, su postura ante los estudiantes.
- [ ] Hace referencia a la teoría pedagógica que encarna (presencia social,
  presencia cognitiva, ZPD, etc.).
- [ ] Es coherente con el rol de facilitación asignado (organizacional,
  intelectual, social, afectivo, moderador).
- [ ] No incluye restricciones (van en CONSTRAINTS).
- [ ] No incluye directivas de tarea (van en TASK).
- [ ] Máximo cuatro o cinco frases.

**Ejemplos** por rol (referencia de diseño):

- *Rol organizacional* ("The Architect"): estructurado, metódico, ve la
  discusión como un espacio que debe diseñarse antes del primer mensaje.
  Cree que el pensamiento de alto nivel emerge de una estructura macro-script
  bien definida.
- *Rol intelectual* ("The Sage-Facilitator"): académicamente riguroso e
  inquisitivo, actúa como "More Knowledgeable Other", usa la agencia
  epistémica para acortar la distancia entre la comprensión actual del
  estudiante y su potencial.
- *Rol social* ("The Connector"): cálido, inclusivo, orientado a la
  comunidad, focalizado en la presencia social. Cree que un entorno de
  confianza es condición previa para el riesgo intelectual que requiere
  el discurso académico profundo.
- *Rol afectivo* ("The Lifeguard"): empático y vigilante, monitorea la
  zona de pánico emocional y asegura que los estudiantes permanezcan
  motivados durante la lucha productiva.
- *Rol moderador* ("The Balancer"): estratégicamente paciente, sabe que
  intervenir demasiado pronto cierra conversaciones productivas. Ve la
  moderación como un arte de temporización, no de reglas.

---

### Componente 2: CONSTRAINTS

Define lo que el agente **no hace**: sus límites de responsabilidad en el
pipeline y sus restricciones de comportamiento. Separado de PERSONA porque
las restricciones son reglas de comportamiento, no identidad.

**Criterios (todos los agentes):**

- [ ] Declara explícitamente la frontera de responsabilidad del agente en
  el pipeline: qué decisión o acción pertenece al nodo siguiente, no a
  este.
- [ ] Explica por qué esa frontera existe: qué rompe si el agente la cruza.
- [ ] Para agentes internos: declara que el agente no toma decisiones que
  corresponden a nodos siguientes ("no decides si intervenir").
- [ ] Para agentes de salida visible: declara restricciones de tono y de
  contenido (no evaluar, no calificar, no adoptar lenguaje autoritario si
  el rol es de par).
- [ ] Sin ejemplos. Sin definiciones de campos de salida.

**Justificación:** Lippert et al. (2020) muestran que en sistemas MACITS
la separación de roles entre agentes es condición para la evaluación
independiente de cada nodo. Sin CONSTRAINTS explícito, las restricciones
se filtran a PERSONA o TASK y son invisibles para la revisión.

---

### Componente 3: CONTEXT

Contiene información variable en tiempo de ejecución: umbrales, marcas de
tiempo, contexto del curso o del hilo.

**Criterios:**

- [ ] Solo información variable por llamada.
- [ ] Sin instrucciones, sin restricciones, sin definiciones de campos.
- [ ] Cada placeholder `{variable}` documentado en la clase de dependencias
  del agente (tipo, fuente, valor por defecto si aplica).
- [ ] Información mínima necesaria: si el agente no la usa en su
  razonamiento, no va aquí.

---

### Componente 4: TASK

Especifica la tarea concreta: qué debe producir el agente, con qué
vocabulario y con qué guía de razonamiento.

**Criterios:**

- [ ] La directiva de tarea es explícita: qué leer, qué decidir, qué
  producir.
- [ ] Cada campo de salida está descrito con guía de razonamiento semántica
  (qué observar, cómo distinguir valores próximos). Los nombres de campo,
  tipos y valores de enum viajan al modelo automáticamente mediante la
  definición de la herramienta `final_result` (modo `ToolOutput`, ADR 0012).
  TASK no repite esa información; la complementa con criterios de aplicación
  que el esquema no puede expresar.
- [ ] La guía del campo `reasoning` es específica: nombra qué observaciones
  incluir, no solo "explica tu razonamiento".
- [ ] Para agentes de salida visible: especifica el punto de la escala EMT
  en que opera el agente (pump, hint, prompt, assertion) y si puede incluir
  contenido fuera de tarea. Por defecto: solo en-tarea (Veletsianos 2012,
  en Sikstrom et al. 2022).
- [ ] No repite contenido de PERSONA ni de CONSTRAINTS.
- [ ] No repite información que el esquema Pydantic (nombres de campo, tipos,
  descripciones de `Field`) ya entrega al modelo vía la herramienta `final_result`.
- [ ] Cada decisión de diseño (por qué este campo, por qué estos valores)
  es trazable a literatura o a un ADR. La justificación vive en
  `docs/agents/<agente>.md`.

**Justificación:** Jiang et al. (2025) identifican Directive y Output
Format como los componentes más comunes y más influyentes en la calidad
del output. Ho & Swan (2007) muestran que la claridad de las expectativas
es el factor más importante para la calidad del discurso asíncrono; el
mismo principio aplica a agentes LLM.

---

### Documento de especificación por agente

Cada agente tiene un fichero en `docs/agents/<nombre-agente>.md` con:

1. **Propósito**: qué hace el agente y qué lugar ocupa en el pipeline.
2. **Tipo**: interno o de salida visible.
3. **Marco teórico**: literatura que justifica el diseño del prompt.
4. **Dimensiones de observación o acción**: tabla con cada dimensión,
   qué observar o decidir, y a qué tipo de intervención informa.
5. **Draft del prompt**: los cuatro componentes con el texto actual.
6. **Cuestiones abiertas**: decisiones pendientes con referencia a TODOs
   en el código.
7. **Fuentes**: bibliografía con indicación de qué concepto aporta cada una.

El código es la implementación. El documento es la justificación. Cuando
el prompt cambia, el documento se actualiza.

---

### Lista de verificación antes de publicar un prompt nuevo o modificado

**PERSONA**
- [ ] Agente interno: una o dos frases, solo rol epistémico, sin
  restricciones ni directivas.
- [ ] Agente visible: carácter descrito, teoría pedagógica referenciada,
  coherente con el rol de facilitación, sin restricciones ni directivas,
  máximo cinco frases.

**CONSTRAINTS**
- [ ] Frontera de responsabilidad declarada explícitamente.
- [ ] Justificación de la frontera incluida.
- [ ] Sin ejemplos ni definiciones de campos.

**CONTEXT**
- [ ] Solo variables de ejecución.
- [ ] Todos los placeholders documentados en la clase de dependencias.

**TASK**
- [ ] Directiva explícita.
- [ ] Todos los campos de salida definidos con vocabulario consistente
  con `constants.py`.
- [ ] Guía de razonamiento específica.
- [ ] Para agentes visibles: punto EMT declarado y política de contenido
  fuera de tarea especificada.
- [ ] Sin repetición de PERSONA ni CONSTRAINTS.
- [ ] Decisiones de diseño trazables a `docs/agents/`.

**General**
- [ ] El documento `docs/agents/<agente>.md` está actualizado.
- [ ] El agente produce output estructurado válido en al menos un test con
  modelo de prueba: `agent.override(model=TestModel())` sin `custom_output_text`
  (modo `ToolOutput` genera output válido automáticamente desde el esquema).

---

## Consecuencias

### Positivas

- Cuatro componentes con una sola responsabilidad cada uno: la revisión
  quirúrgica es posible sin leer el prompt completo.
- El efecto de la persona es el correcto para cada tipo de agente: mínimo
  donde no aporta (internos), rico donde es el mecanismo principal (visibles).
- Los agentes de rol tienen personalidades diferenciadas que producen texto
  observablemente distinto para cada tipo de facilita ción.
- La separación CONSTRAINTS/TASK hace las restricciones explícitas y
  auditables sin mezclarlas con la tarea.

### Negativas

- Cuatro componentes en lugar de dos o tres: más superficie a mantener.
  Mitigación: cada componente es más corto y más enfocado que en esquemas
  de dos secciones.
- Los agentes de salida visible requieren más trabajo de diseño de persona.
  Mitigación: los cinco arquetipos de esta ADR son un punto de partida
  concreto.

### Cuestiones abiertas

- ¿Se valida el cumplimiento de esta ADR mediante checklist manual en PR
  o mediante prueba automatizada?
- ¿Son obligatorios los ejemplos en TASK para valores de enum difíciles de
  distinguir? La literatura sugiere que ejemplos concretos reducen
  ambigüedad (Lin et al. 2013, en Sikstrom et al. 2022), pero aumentan la
  longitud del prompt.
- Los agentes de salida visible tienen requisitos adicionales sobre efecto
  afectivo y presencia social que esta ADR trata a nivel de checklist.
  ¿Se necesita una ADR específica cuando se diseñen esos prompts?

---

## Referencias

- Jiang, S. et al. (2025). From Prompts to Templates: A Systematic Prompt
  Template Analysis for Real-world LLM Apps. arXiv:2504.02052.
- Zheng, M. et al. (2024). When "A Helpful Assistant" Is Not Really Helpful:
  Personas in System Prompts Do Not Improve Performances of Large Language
  Models. *Findings of EMNLP 2024*. arXiv:2311.10054.
- Chan, C. et al. (2025). Multi-Agent Design: Optimizing Agents with Better
  Prompts and Topologies. arXiv:2502.02533.
- Hu, Y. et al. (2025). Conversation Routines: A Prompt Engineering
  Framework for Task-Oriented Dialog Systems. arXiv:2501.11613.
- Ho, C.-H., & Swan, K. (2007). Evaluating online conversation in an
  asynchronous learning environment: An application of Grice's cooperative
  principle. *Internet and Higher Education*, 10, 3-14.
- Lippert, A., Shubeck, K., Morgan, B., Hampton, A., & Graesser, A. (2020).
  Multiple agent designs in conversational intelligent tutoring systems.
  *Technology, Knowledge and Learning*, 25, 443-463.
- Sikstrom, P., Valentini, C., Sivunen, A., & Kärkkäinen, T. (2022). How
  pedagogical agents communicate with students: A two-phase systematic
  review. *Computers & Education*, 188, 104564.
- Singh, A. B., & Mørch, A. (2022). Instructors' epistemic intervention
  strategies in MOOC discussion forums. *Journal of Educators Online*.
- ADR 0005: Arquitectura multi-agente con pipeline configurable.
