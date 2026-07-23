# ADR 0003: Modelo de intervención en tres fases

**Estado**: Propuesto
**Fecha**: 2026-03-10
**Depende de**: ADR 0046 (Repertorio de técnicas de facilitación)
**Refinado por**: ADR 0008 (Principios de temporización de la intervención)

## Descripción

El sistema de facilitación inteligente necesita un proceso estructurado para
decidir cuándo y cómo intervenir en una discusión académica asíncrona. La
literatura muestra que tanto la intervención excesiva como la insuficiente
producen resultados negativos: demasiada participación del facilitador desplaza
la interacción entre estudiantes (An et al., 2009), mientras que la ausencia de
intervención cuando es necesaria permite la escalación de conflictos (Korre et
al., 2025, §6.1).

Se requiere un modelo que combine la evaluación del estado de la discusión, la
selección de una acción apropiada y la generación de una respuesta textual,
respetando el principio de intervención mínima.

## Decisión

Adoptar un modelo de intervención en tres fases secuenciales. Dado un hilo de
discusión (con tema, objetivos de aprendizaje y contexto del curso), el sistema
ejecuta las fases en orden y produce una respuesta textual o decide no
intervenir.

### Fase 1: Evaluar el estado de la discusión

El sistema lee el hilo y clasifica su estado entre las siguientes categorías:

| Estado | Descripción |
|--------|-------------|
| **Nueva** | Sin respuestas todavía |
| **Activa** | Intercambio en curso |
| **Estancada** | Sin publicaciones nuevas tras un periodo configurable |
| **Conflictiva** | Lenguaje agresivo o despectivo |
| **Convergente** | Los participantes están llegando a conclusiones |
| **Fuera de tema** | La discusión se ha alejado del tema propuesto |

A partir de la clasificación, el sistema decide si debe intervenir. La mayoría
de estados pueden resultar en "no intervenir".

**Precisión sobre el estado "Estancada"**:

El estado *estancada* no equivale a silencio. Una discusión puede estar en
silencio porque los participantes están reflexionando (no requiere
intervención) o porque ha alcanzado un impasse genuino - un punto en el que
no es posible avanzar sin entrada externa (requiere intervención). La
distinción no se resuelve solo con un umbral temporal: hay que examinar si
las últimas contribuciones eran sustantivas o eran movimientos de cierre.

**Trayectoria, no solo estado puntual**:

La clasificación no debe basarse únicamente en el estado actual del hilo. Dos
hilos en estado *estancada* pueden requerir intervenciones distintas según su
historia: un hilo que era activo y ha decaído es diferente a uno que nunca
despegó. El clasificador debe describir la trayectoria en su razonamiento -
no como campo adicional, sino como parte de la justificación de su
clasificación - para que los agentes de rol dispongan de este contexto.

**Justificación desde la literatura**:

- Elegir el momento adecuado para intervenir es determinante; intervenir
  innecesariamente puede aumentar la toxicidad (Korre et al., 2025, §6.1;
  Schaffner et al., 2024; Trujillo & Cresci, 2022).
- Distintos estados de discusión requieren distintos tipos de mensaje (Blignaut
  & Trollip, 2003, Tabla 3).
- El grupo con intervención mínima del instructor y respuesta obligatoria entre
  pares produjo la mayor interacción estudiantil y la presencia social más alta
  (An et al., 2009, Grupo 3).
- No responder demasiado rápido para dar oportunidad a que los estudiantes
  respondan primero (Rovai, 2007, §3.2).
- Intervenir antes del impasse - mientras la discusión todavía progresa -
  interrumpe la lucha productiva que genera aprendizaje profundo. Los sistemas
  de tutoría inteligente producen los mayores efectos cuando intervienen en el
  impasse, no antes (VanLehn, 2011, d≈0.76; Kapur, 2016 - efecto de fallo
  productivo).
- Ante señales ambiguas, la abstención es la respuesta correcta. El coste de
  una intervención innecesaria supera el coste de una oportunidad perdida
  (Koedinger & Aleven, 2007 - dilema de asistencia; Anthropic, 2025 -
  principio de huella mínima).
- No re-intervenir hasta que los participantes hayan tenido oportunidad de
  responder a la intervención anterior. La intervención repetida desplaza la
  discusión de centrada en el estudiante a centrada en el facilitador (Rovai,
  2007, §3.6 - sobreintervención calibrada).
- El tono declinante es señal de intervención social preventiva antes de que
  el conflicto sea explícito (Chang & Danescu-Niculescu-Mizil, 2019 -
  predicción de descarrilamiento conversacional).
- El estado "fuera de tema" es especialmente difícil de manejar en entornos
  asíncronos porque el instructor no puede redirigir inmediatamente; las
  técnicas preventivas (diseño de preguntas, guías de preparación) son
  prioritarias (Beaudin, 1999, §IV).

**Trabajo relacionado sobre el momento de intervenir**:

La decisión de cuándo intervenir tiene paralelos en sistemas multi-agente y
de interacción multipartita, aunque estos trabajos no se sitúan en el contexto
de discusiones académicas asíncronas:

- En interacciones multipartita con agentes, Paetzel-Prüsmann & Kennedy (2023)
  identifican tres capacidades necesarias para decidir cuándo tomar la palabra:
  (1) tomar el turno, (2) ceder o mantener el turno ante interrupciones
  intencionales, y (3) mantener el turno ante interrupciones no intencionales.
  En su corpus anotado de 9.342 muestras, aproximadamente un tercio de las
  intervenciones no estaban dirigidas al agente (§5, Fig. 4). Un modelo basado
  únicamente en umbrales de pausa produce intervenciones falsas frecuentes
  (§5); se requieren señales más ricas.
- Gosmar et al. (2024) proponen un protocolo para conversaciones multipartita
  entre agentes de IA donde un *Convener Agent* evalúa solicitudes de turno
  "basándose en reglas predefinidas y el estado actual de la conversación"
  (§2.2.2). Las solicitudes incluyen "la razón y urgencia de su contribución"
  (§2.2.4). Un *Floor Manager* ejecuta las políticas sobre quién tiene la
  palabra y cuándo (§2.2.1).

Estos conceptos - detección de destinatario, evaluación de urgencia, y
evaluación del estado de la conversación antes de intervenir - son
transferibles al diseño de la Fase 1, aunque su validación empírica
corresponde a entornos síncronos y multi-agente, no a discusiones académicas
asíncronas.

### Fase 2: Seleccionar una acción

Si la Fase 1 determina que se debe intervenir, el sistema selecciona **una
única acción** de entre cinco categorías. Cada categoría agrupa acciones con
un rol de facilitación distinto.

#### Acciones organizacionales

| Condición | Acción |
|-----------|--------|
| Inicio de conversación | Lanzar la discusión con una pregunta enfocada o un problema |
| Objetivos alcanzados | Resumir y cerrar la discusión |
| Discusión activa pero dispersa | Sintetizar el estado actual (sin cerrar) |
| Discusión fuera de tema | Reformular la pregunta original para redirigir |

**Justificación**:

- Las preguntas deben ser "basadas en contenido, abiertas y construidas para
  revelar comprensión e inducir pensamiento crítico" (Baker, 2011, Rol
  Pedagógico).
- El primer mensaje debe ser un tema de discusión enfocado publicado por el
  instructor (Rovai, 2007, §2.4).
- El rol de *Starter* activa la discusión con mensajes iniciales sobre los que
  otros puedan construir (De Wever et al., 2010, Apéndice A).
- El rol de *Summariser* publica resúmenes intermedios y una sinopsis final,
  identificando disonancias y armonías entre los mensajes; este rol tuvo el
  mayor efecto positivo en la construcción de conocimiento (De Wever et al.,
  2010, Apéndice A).
- Las discusiones necesitan un inicio y un cierre específicos (Baker, 2011, Rol
  Gerencial; Rovai, 2007, §3.2).
- "Reformular la pregunta original cuando las respuestas van en la dirección
  equivocada" fue la tercera técnica más recomendada y utilizada para mantener
  la discusión en tema (Beaudin, 1999, Tabla 1, rango 3, media 4.60/6).

#### Acciones intelectuales

| Condición | Acción |
|-----------|--------|
| Preguntas sin respuesta o respuestas incompletas | Responder basándose en el contenido del curso |
| Errores conceptuales o malentendidos | Redirigir el pensamiento sin dar la respuesta |
| Contribuciones desconectadas entre sí | Conectar contribuciones entre participantes |
| Contenido externo relevante podría enriquecer | Aportar fuentes externas pertinentes |

**Justificación**:

- Los mensajes informativos proporcionan retroalimentación de apoyo o expandida
  desde la perspectiva del contenido (Blignaut & Trollip, 2003, Tabla 3).
- El rol de *Theoretician* asegura que los conceptos teóricos relevantes se
  incorporen a la discusión (De Wever et al., 2010, Apéndice A).
- Los mensajes correctivos redirigen malentendidos mediante preguntas, no
  mediante corrección directa (Blignaut & Trollip, 2003, Tabla 3 - Correctivo
  y Socrático).
- Preferir preguntas de sondeo sobre afirmaciones directas; responder
  directamente tiende a terminar el discurso productivo (Rovai, 2007, §3.2).
- El rol de *Moderator* relaciona contribuciones de los estudiantes señalando
  similitudes y diferencias (De Wever et al., 2010, Apéndice A).
- El rol de *Source searcher* aporta fuentes externas argumentando su relevancia
  para la discusión (De Wever et al., 2010, Apéndice A).

#### Acciones sociales y de participación

| Condición | Acción |
|-----------|--------|
| Sin comentarios tras un periodo | Fomentar la participación con preguntas invitadoras |
| Participación desbalanceada | Redistribuir la atención |
| Conflicto presente | Gestionar el conflicto |

**Justificación**:

- Publicar al menos un mensaje diario para indicar que las publicaciones se
  leen; pueden ser tan simples como expresar aprecio o ánimo (Rovai, 2007,
  §3.1).
- Designar un rol rotativo de "rompehielos" para combatir el síndrome de
  "nadie quiere empezar" (Baker, 2011, Rol Gerencial).
- Elevar el estatus de estudiantes con menor participación reconociendo la
  importancia de sus contribuciones (Rovai, 2007, §3.5).
- Tratar con tacto y en privado a estudiantes que dominan o que permanecen en
  silencio (Rovai, 2007, §3.2).
- Los facilitadores humanos siguen una "escalera de escalación": primero
  tácticas de facilitación estándar, luego advertencias, y acción disciplinaria
  como último recurso. La "moderación conversacional" ha demostrado ser
  efectiva (Korre et al., 2025, §6.2).
- Atender problemas que puedan interrumpir la discusión, particularmente
  comunicación agresiva que puede silenciar a otros (Rovai, 2007, §3.2; Baker,
  2011).

#### Acciones de moderación (pasiva)

| Condición | Acción |
|-----------|--------|
| Contenido inapropiado | Señalar para revisión |
| Contenido con derechos de autor | Señalar para revisión |

**Nota**: Estas acciones corresponden a moderación pasiva, no a facilitación
activa. Se incluyen por completitud, pero constituyen un rol distinto con
disparadores diferentes (Korre et al., 2025, Apéndice C). La acción
disciplinaria es siempre último recurso. La detección de contenido tóxico o
inapropiado por LLMs tiene soporte empírico (Korre et al., 2025, §7.2).

#### Acciones afectivas

| Condición | Acción |
|-----------|--------|
| Contribuciones valiosas identificadas | Reconocer y reforzar positivamente |

**Justificación**:

- La retroalimentación positiva por contribuir a las discusiones fomenta la
  participación continuada (Rovai, 2007, §3.1; Knowles, 1989).
- Los mensajes afectivos reconocen la participación y proporcionan apoyo
  emocional (Blignaut & Trollip, 2003, Tablas 2-3).

### Fase 3: Generar la respuesta

Una vez seleccionada la acción, el sistema genera una respuesta textual
siguiendo estas restricciones:

1. **Una acción por intervención**: no combinar múltiples acciones en un mismo
   mensaje. Demasiada intervención desplaza la interacción entre pares (An et
   al., 2009).
2. **Preferir preguntas sobre afirmaciones**: las preguntas socráticas y de
   sondeo son más efectivas que las afirmaciones directas (Blignaut & Trollip,
   2003, categoría Socrática; Rovai, 2007, §3.2).
3. **Usar nombres de estudiantes y referenciar sus contribuciones
   específicas**: la intersubjetividad se construye dirigiéndose a los
   participantes por su nombre, lo que genera solidaridad y familiaridad (An et
   al., 2009, §5.3, Tabla 1).
4. **Personalizar la intervención**: las estrategias no deben aplicarse en
   masa; considerar las características de cada individuo (Korre et al., 2025,
   §6.3).

### Distinción facilitación vs. moderación

Es importante señalar que este modelo integra dos roles distintos (Korre et
al., 2025, Apéndice C):

- **Facilitadores**: promueven la participación y estructuran el diálogo. Las
  acciones organizacionales, intelectuales, sociales y afectivas corresponden a
  este rol.
- **Moderadores**: hacen cumplir las normas y aseguran interacciones ordenadas,
  con la amenaza de acción disciplinaria como último recurso. Las acciones de
  moderación corresponden a este rol.

Ambos roles son necesarios, pero tienen disparadores y lógicas diferentes.

## Consecuencias

### Positivas

- La estructura en tres fases proporciona un proceso auditable: se puede
  inspeccionar qué estado se detectó, qué acción se seleccionó y por qué.
- La decisión explícita de "no intervenir" como resultado válido de la Fase 1
  protege contra la sobreintervención.
- La restricción de una acción por intervención mantiene el espacio para la
  interacción entre estudiantes.
- Cada acción tiene justificación en la literatura, lo que permite evaluar la
  fidelidad del sistema respecto al modelo teórico.

### Negativas

- La clasificación del estado de la discusión en categorías discretas puede no
  capturar estados mixtos (por ejemplo, una discusión activa pero parcialmente
  fuera de tema).
- El modelo asume que una única acción por turno es siempre suficiente; pueden
  existir situaciones que requieran intervención compuesta.
- Los umbrales temporales (por ejemplo, "sin publicaciones tras X tiempo") son
  configurables pero su calibración óptima requiere evaluación empírica.
- La distinción entre facilitación y moderación está clara conceptualmente, pero
  la implementación puede encontrar casos donde ambos roles se activen
  simultáneamente.

### Cuestiones abiertas

- ¿Cómo se priorizan las acciones cuando múltiples condiciones se cumplen
  simultáneamente? (Por ejemplo: discusión estancada con participación
  desbalanceada.)
- ¿Cómo se manejan los estados mixtos de discusión?
- ¿Cuál es el mecanismo de retroalimentación para ajustar los umbrales de
  intervención?
- ¿Cómo se integra la señalización de contenido inapropiado (moderación pasiva)
  con el flujo de facilitación activa sin interrumpirlo?

## Referencias

- An, H., Shin, S., & Lim, K. (2009). The effects of different instructor
  facilitation approaches on students' interactions during asynchronous online
  discussions.
- Baker, D. L. (2011). Designing and orchestrating online discussions.
- Beaudin, B. P. (1999). Keeping online asynchronous discussions on topic.
- Blignaut, A. S., & Trollip, S. R. (2003). Measuring faculty participation in
  asynchronous discussion forums.
- De Wever, B., Van Keer, H., Schellens, T., & Valcke, M. (2010). Roles as a
  structuring tool in online discussion groups.
- Gosmar, D., Dahl, D. A., Coin, E., & Attwater, D. (2024). AI multi-agent
  interoperability: Extension for managing multiparty conversations.
- Chang, J. P., & Danescu-Niculescu-Mizil, C. (2019). Trouble on the horizon:
  Forecasting the derailment of online conversations as they develop.
  *Proceedings of EMNLP-IJCNLP 2019*, pp. 4743-4754.
- Kapur, M. (2016). Examining productive failure, productive success,
  unproductive failure, and unproductive success in learning. *Instructional
  Science*, 44(4), 379-401.
- Koedinger, K. R., & Aleven, V. (2007). Exploring the assistance dilemma in
  experiments with cognitive tutors. *Educational Psychology Review*, 19(3),
  239-264.
- Korre, D., Tsipas, N., & Peppes, N. (2025). Facilitation and moderation in
  online discussions: A systematic review.
- Paetzel-Prüsmann, M., & Kennedy, J. (2023). Improving a robot's turn-taking
  behavior in dynamic multiparty interactions.
- Rovai, A. P. (2007). Facilitating online discussions effectively.
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent
  tutoring systems, and other tutoring systems. *Educational Psychologist*,
  46(4), 197-221.
