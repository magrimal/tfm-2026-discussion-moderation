# ADR 0046: Repertorio de técnicas de facilitación

> Renumerada desde ADR 0002 para eliminar la colisión con
> `0002-justificacion-y-problema.md`. El contenido y la decisión no cambian.

**Estado**: Propuesto
**Fecha**: 2026-03-10

## Descripción

El sistema de facilitación inteligente necesita un repertorio fundamentado de
técnicas de intervención. Antes de definir cuándo y cómo intervenir (ADR 0003),
es necesario establecer qué acciones existen, cómo se clasifican y qué
evidencia las respalda.

Este ADR sintetiza las técnicas de facilitación y moderación identificadas en
la revisión de 35 artículos (de un corpus de 37; 2 excluidos por estar fuera
de alcance: uno sobre interoperabilidad multi-agente y otro sobre
turn-taking en robótica síncrona).
Su objetivo es servir como base para la selección de acciones del modelo de
intervención y como referencia para la implementación del sistema.

**Alcance**: Solo técnicas aplicables a discusiones académicas asíncronas
basadas en texto. Se excluyen técnicas específicas de entornos síncronos,
embodied agents o tutorización individual.

## Decisión

Adoptar un repertorio organizado en seis categorías de técnicas, alineadas con
los tres roles de facilitación (organizacional, intelectual, social) más
categorías transversales de retroalimentación, activación proactiva y
restricciones de generación.

### 1. Técnicas organizacionales

Estructuran la discusión antes y durante su desarrollo. Corresponden al rol de
facilitador organizacional.

#### 1.1 Diseño de la pregunta inicial

Formular preguntas abiertas, basadas en contenido, que revelen comprensión e
induzcan pensamiento crítico. La calidad de la pregunta inicial condiciona toda
la discusión posterior.

**Evidencia**:
- Las preguntas deben ser "basadas en contenido, abiertas y construidas para
  revelar comprensión e inducir pensamiento crítico" (Baker, 2011, Rol
  Pedagógico).
- El primer mensaje debe ser un tema enfocado publicado por el instructor
  (Rovai, 2007, §2.4).
- Cuando los estudiantes proponen los temas, la participación aumenta
  significativamente respecto a temas iniciados por el docente (Zulfikar et
  al., 2019).
- "Diseñar cuidadosamente preguntas que eliciten específicamente discusión
  sobre el tema" fue la técnica más recomendada y más utilizada por 135
  instructores (Beaudin, 1999, Tabla 1, rango 1, media 5.18/6).

#### 1.2 Asignación de roles de discusión

Distribuir roles explícitos entre los participantes para estructurar la
interacción y garantizar diversidad de contribuciones.

| Rol | Función |
|-----|---------|
| *Starter* | Abre la discusión con una posición inicial |
| *Moderator* | Conecta contribuciones señalando similitudes y diferencias |
| *Theoretician* | Incorpora conceptos teóricos relevantes |
| *Source searcher* | Aporta fuentes externas con justificación de relevancia |
| *Summariser* | Publica resúmenes intermedios y sinopsis final |

El rol de *Summariser* tuvo el mayor efecto positivo en la construcción de
conocimiento (De Wever et al., 2010, Apéndice A).

**Evidencia adicional**: Pilkington (2003) identifica tres clases de roles
complementarias: construcción de comunidad, gestión y argumentación.

#### 1.3 Organización de grupos

Formar grupos pequeños (4-6 personas) para aumentar la densidad de
participación. Mezclar niveles de habilidad para aprendizaje entre pares;
rotar composición periódicamente.

**Evidencia**: Casebourne (2025) identifica el agrupamiento (*Grouping*) como
una de las tres funciones clave de la IA para inteligencia colectiva. Baker
(2011) recomienda grupos pequeños con rotación.

#### 1.4 Estructuración en fases

Dividir la discusión en fases temporales con objetivos distintos:

| Fase | Función |
|------|---------|
| **Antes** | Establecer expectativas, proporcionar recursos, asignar roles |
| **Durante** | Monitorizar, intervenir cuando sea necesario, facilitar |
| **Después** | Resumir, reflexionar, evaluar |

**Evidencia**: Abdous (2011) propone un marco orientado a procesos en tres
fases. Casebourne (2025) identifica el *Staging* (secuenciación temporal) como
función clave.

#### 1.5 Establecimiento de normas y expectativas

Publicar guías de discusión: extensión esperada, frecuencia, criterios de
calidad, reglas de interacción respetuosa.

**Evidencia**: Baker (2011), Rovai (2007), Massey (2019). La presencia del
instructor al inicio establece que la discusión importa (Richardson & Lowenthal,
2015). "Proporcionar guías para ayudar a los estudiantes a preparar respuestas
sobre el tema" fue la segunda técnica más recomendada y utilizada (Beaudin,
1999, Tabla 1, rango 2, media 4.87/6).

#### 1.6 Síntesis y cierre

Resumir periódicamente los argumentos clave del hilo. Identificar áreas de
acuerdo, desacuerdo y cuestiones abiertas. Cerrar la discusión cuando los
objetivos se han alcanzado.

**Evidencia**: De Wever et al. (2010, rol *Summariser*), Abdous (2011, fase
"Después"), Lim (2011, técnica de *summarizing*). "Proporcionar resúmenes de
la discusión de forma regular" fue la cuarta técnica más recomendada y
utilizada (Beaudin, 1999, Tabla 1, rango 4, media 4.58/6).

#### 1.7 Protocolos de participación

Requerir responder al menos a un par antes de publicar nuevos hilos. Usar
aperturas de frase (*sentence openers*) para andamiar la participación.

**Evidencia**: Casebourne (2025), Rovai (2007). Los *sentence openers*
estructuran la interacción y reducen la barrera de entrada.

#### 1.8 Redirección de discusiones fuera de tema

Reformular la pregunta original cuando las respuestas se desvían del tema.
Proporcionar un espacio alternativo ("café") para conversaciones fuera de tema
en lugar de suprimirlas.

**Evidencia**: Beaudin (1999, N=135) encuentra que "reformular la pregunta
original cuando las respuestas van en la dirección equivocada" fue la tercera
técnica más recomendada y utilizada (rango 3, media 4.60/6). "Proporcionar
ubicaciones alternativas (café) para discusiones fuera de tema" ocupó el rango
5 (media 4.29/6). En el contexto asíncrono, el instructor no puede redirigir
inmediatamente como en el aula presencial; por eso las técnicas preventivas
(§1.1, §1.5) tienen prioridad, y la redirección actúa como mecanismo
correctivo.

### 2. Técnicas intelectuales

Profundizan el pensamiento y promueven la construcción de conocimiento.
Corresponden al rol de facilitador intelectual.

#### 2.1 Preguntas socráticas (taxonomía de Paul)

Seis categorías de preguntas, ordenadas por profundidad creciente:

| Tipo | Ejemplo | Cuándo usar |
|------|---------|-------------|
| **Clarificación** | "¿Qué quieres decir con X?" | Afirmaciones vagas o ambiguas |
| **Sondeo de supuestos** | "¿Qué estás asumiendo al decir...?" | Premisas no examinadas |
| **Sondeo de evidencia** | "¿Qué evidencia respalda eso?" | Afirmaciones sin soporte |
| **Sondeo de perspectivas** | "¿Cómo respondería alguien que no esté de acuerdo?" | Argumentos unilaterales |
| **Sondeo de implicaciones** | "Si eso es cierto, ¿qué se sigue?" | Consecuencias no exploradas |
| **Meta-preguntas** | "¿Por qué es importante esta pregunta?" | La discusión necesita reencuadre |

**Evidencia**: Degen (2025) evalúa un tutor socrático basado en la taxonomía de
Paul (1990) y encuentra que los estudiantes reportan mayor apoyo al pensamiento
crítico, independiente y reflexivo. Blignaut & Trollip (2003) incluyen la
categoría "Socrática" como una de las seis categorías de facilitación. Ekeyi
clasifica nueve tipos de preguntas basándose en Christensen (1991).

#### 2.2 Escalera de diálogo tutorial (EMT)

Cuatro movimientos de diálogo con intensidad creciente:

1. **Pump** (elicitación abierta): "¿Puedes decir más sobre eso?"
2. **Hint** (pista indirecta): "Piensa en lo que discutimos sobre X..."
3. **Prompt** (guía dirigida): "¿Cómo se relaciona el concepto Y con tu
   argumento?"
4. **Assertion** (afirmación directa): proporcionar información cuando el
   andamiaje no funciona

**Evidencia**: Graesser (2017) describe el marco tutorial de cinco pasos de
AutoTutor. Lippert (2020) aplica los movimientos EMT en diseños multi-agente.
Korre (2025) propone una escalera de escalación similar.

#### 2.3 Desafío y contraargumentación

Introducir perspectivas alternativas, contraejemplos o evidencia contradictoria
para profundizar el análisis.

**Evidencia**: Lim (2011) identifica *challenging* como una de las nueve
técnicas de facilitación entre pares. Jin (2025, N=217) muestra que un agente
con persona "contraria" mantiene el pluralismo de valores en razonamiento
moral. Brown (2015) documenta el debate estructurado (formato a favor/en
contra, formato fishbowl) como estrategia pedagógica.

**Precaución**: Yan (2025, N=905) demuestra que la persona contraria reduce la
seguridad psicológica y la calidad de la discusión, aunque mejora el
rendimiento analítico. Usar selectivamente y no como modo por defecto.

#### 2.4 Solicitud de evidencia y fundamentación

Pedir que las afirmaciones se conecten a lecturas, ejemplos o datos concretos.
Promover la progresión de afirmaciones simples a afirmaciones fundamentadas y
cualificadas.

**Evidencia**: Jin (2025) aplica el marco de Construcción Argumentativa del
Conocimiento (Weinberger & Fischer, 2006): afirmaciones simples → cualificadas
→ fundamentadas → fundamentadas y cualificadas. An (2009) identifica "pedir
evidencia" como componente de la facilitación intelectual. Murphy (2018)
documenta la evolución del enfoque Quality Talk hacia la fundamentación.

#### 2.5 Revoicing y reencuadre

Parafrasear la contribución de un estudiante para clarificarla y elevarla.
Conectar publicaciones aisladas entre sí.

**Evidencia**: Casebourne (2025) identifica el *revoicing* como técnica clave
de la IA para inteligencia colectiva. Murphy (2018) lo documenta en el enfoque
Quality Talk. Glina lo describe en el contexto del habla exploratoria
(*exploratory talk*), donde el facilitador actúa como participante igual.

#### 2.6 Estructuración argumentativa (IBIS)

Enmarcar contribuciones como **Issues** (preguntas), **Positions** (respuestas
propuestas) o **Arguments** (a favor/en contra). Hacer visible la estructura
argumentativa de la discusión.

**Evidencia**: Gu (2021) aplica un marco de razonamiento basado en casos (CBR)
usando la estructura IBIS para facilitar discusiones.

#### 2.7 Promoción de negociación y co-construcción

Empujar más allá del intercambio superficial (compartir/comparar) hacia la
co-construcción de significado. Los niveles de construcción de conocimiento de
Gunawardena proporcionan la referencia:

1. Compartir/comparar información
2. Descubrir y explorar disonancias
3. Negociar significado / co-construcción
4. Probar y modificar la síntesis propuesta
5. Aplicar el conocimiento co-construido

**Evidencia**: Woo (2007) define la interacción significativa en constructivismo
social como responder, negociar, argumentar y sintetizar. Korre (2025) utiliza
los niveles de Gunawardena como referencia para la calidad de la discusión.
Pilkington (2003) asigna un rol específico de argumentación.

### 3. Técnicas sociales y afectivas

Construyen comunidad, motivación y seguridad psicológica. Corresponden al rol
de facilitador social.

#### 3.1 Reconocimiento y validación

Nombrar explícitamente lo que es valioso en una contribución. Agradecer
esfuerzos específicos, no solo participación genérica.

**Evidencia**: Lim (2011) identifica *acknowledging* como técnica frecuente.
Blignaut & Trollip (2003) incluyen la categoría "Afectiva". Richardson &
Lowenthal (2015) documentan la presencia del instructor como intersección de
presencia social y docente. Rovai (2007, §3.1) recomienda publicar al menos un
mensaje diario de aprecio.

#### 3.2 Apoyo emocional y afectivo

Reconocer la dificultad ("Este es un tema complejo, está bien tener
incertidumbre"). Usar lenguaje cálido y alentador sin perder sustancia.

**Evidencia**: Blignaut & Trollip (2003, categoría Afectiva). Hare (2024)
implementa una estrategia de "alentar y reencuadrar" (*encourage and reframe*)
cuando el estudiante está frustrado. Sikstrom (2022) encuentra que la
retroalimentación afectiva mejora la autorreflexión de los estudiantes.

#### 3.3 Modelado de comportamiento

Publicar contribuciones propias como ejemplo. Demostrar cómo expresar
desacuerdo respetuosamente. Participar como igual en el habla exploratoria.

**Evidencia**: Glina describe al facilitador como participante igual en el
*exploratory talk*. Richardson & Lowenthal (2015) documentan cinco roles de
presencia docente. Murphy (2018) describe la evolución del rol docente de
directivo a facilitativo.

#### 3.4 Persona de apoyo como modo por defecto

El lenguaje de apoyo (afiliativo, alentador, orientado al consenso) mejora la
calidad de la discusión y la seguridad psicológica. El lenguaje desafiante
tiene usos específicos pero no debe ser el modo por defecto.

**Evidencia**: Yan (2025, N=905) demuestra que la persona de apoyo mejora la
calidad de la discusión; la persona contraria reduce la seguridad psicológica.
Jin (2025, N=217) muestra que la persona de apoyo aumenta las afirmaciones
fundamentadas y cualificadas.

#### 3.5 Construcción de presencia social

Usar rompehielos al inicio. Referenciar a estudiantes por nombre. Compartir
ejemplos personales relevantes cuando sea apropiado.

**Evidencia**: Baker (2011), Richardson & Lowenthal (2015), Abdous (2011). An
(2009, §5.3) documenta que dirigirse a los participantes por nombre genera
solidaridad y familiaridad.

#### 3.6 Reenganche por trayectoria declinante

Dirigirse específicamente a participantes cuya participación ha disminuido
tras un inicio activo, en lugar de limitarse a invitar a quienes nunca han
participado. El mensaje referencia la contribución anterior del participante
para conectar con su historial en el hilo.

**Distinción con §3.1 y §3.5**: el reconocimiento (§3.1) responde a
contribuciones recientes; la construcción de presencia social (§3.5) actúa al
inicio. Esta técnica actúa cuando un participante que ya estaba involucrado se
ha desenganchado.

**Evidencia**:
- Kim et al. (2021, N=64) demuestran que dirigirse específicamente a
  participantes reticentes - no al hilo en general - produce mayor alineación
  de opiniones, distribución más equitativa de contribuciones y mayor cohesión.
  La facilitación genérica del hilo tuvo efectos menores que la facilitación
  dirigida a personas.
- Baker et al. (2004) identifican el patrón de evitación de ayuda (*help
  avoidance*): estudiantes que dejan de participar sin pedir apoyo. La
  invitación explícita antes de que el desenganche sea completo es la
  intervención más efectiva para este patrón.

#### 3.7 Presencia del instructor calibrada

Participación regular y visible para señalar que la discusión importa, pero sin
sobreintervenir. La sobreintervención suprime la voz estudiantil.

**Evidencia**: Richardson & Lowenthal (2015) definen la presencia del instructor
como intersección de presencia social y docente. Massey (2019) establece que la
presencia del instructor es pivotal. Zulfikar et al. (2019) muestran que la
sobreintervención reduce la participación. Glina advierte contra las
interjecciones excesivas del facilitador.

### 4. Técnicas de retroalimentación

Aplicables al responder a publicaciones específicas de estudiantes.

#### 4.1 Retroalimentación elaborada

Explicar por qué algo es correcto o incorrecto, no solo señalarlo. La
retroalimentación elaborada produce mejores resultados de aprendizaje que la
retroalimentación simple.

**Evidencia**: Sikstrom (2022) sintetiza 31 estudios empíricos sobre
comunicación de agentes pedagógicos. Los estudiantes que recibieron
retroalimentación elaborada obtuvieron puntuaciones significativamente más altas
(Lin et al., 2013 vía Sikstrom). An (2009) identifica tres enfoques: dar
información, hacer preguntas y proporcionar retroalimentación de andamiaje.

#### 4.2 Retroalimentación de andamiaje

Dar pistas que guíen sin dar la respuesta. Apoyar la autorregulación ("¿Cuál
es tu plan para abordar esto?"). Incluir indicaciones metacognitivas ("¿Qué
tan seguro estás? ¿Qué cambiaría tu opinión?").

**Evidencia**: An (2009), Graesser (2017), Simmhan (2025). Sikstrom (2022)
documenta que el andamiaje metacognitivo mejora las habilidades de
autorregulación. Kostopoulos et al. (2025) identifican el andamiaje con
desvanecimiento progresivo (*fading*) como práctica responsable.

#### 4.3 Retroalimentación correctiva directa

Para errores factuales: corregir de forma clara y amable. La retroalimentación
directa es más efectiva para la adquisición de conocimiento que la indirecta en
estos casos.

**Evidencia**: Blignaut & Trollip (2003, categoría Correctiva). Sikstrom (2022)
reporta que la retroalimentación directa es más efectiva para la adquisición de
conocimiento y el razonamiento explícito (Tegos et al., 2016 vía Sikstrom).

#### 4.4 Encuadre positivo de los mensajes

Enfatizar resultados positivos ("Esto te ayudará a...") sobre negativos ("Te
falta..."). Los mensajes con encuadre de pérdida son más llamativos pero
producen mayor carga cognitiva.

**Evidencia**: Sikstrom (2022) sintetiza los hallazgos de Tan et al. (2020)
sobre *loss-framed* vs. *gain-framed messages* en agentes pedagógicos.

### 5. Disparadores proactivos

Condiciones que señalan cuándo intervenir y qué tipo de intervención aplicar.

| Condición | Acción recomendada | Fuente |
|-----------|-------------------|--------|
| Frustración + errores repetidos | Alentar y reencuadrar | Hare, 2024 |
| Éxito en tarea difícil | Reforzar y extender con pregunta más profunda | Hare, 2024 |
| Sin publicaciones nuevas tras periodo X | Publicar pregunta de elicitación o resumen | Korre, 2025; Massey, 2019 |
| Hilo estancado / argumentos repetidos | Introducir nueva evidencia o ángulo diferente | Lippert, 2020; Gu, 2021 |
| Una persona domina | Redistribuir: "Escuchemos otras perspectivas" | Lippert, 2020 |
| Lenguaje agresivo o despectivo | Abordar en privado; reafirmar normas públicamente | Lippert, 2020; Korre, 2025 |
| Discusión en nivel superficial | Preguntar socráticamente un nivel más profundo | Degen, 2025; Korre, 2025 |
| Contribución valiosa sin respuestas | Revoice al grupo | Casebourne, 2025 |
| Cobertura temática estrecha | Preguntar sobre subtema no explorado | Simmhan, 2025 |
| Discusión fuera de tema | Reformular la pregunta original; ofrecer espacio alternativo | Beaudin, 1999 |
| Hilo próximo a cerrar sin síntesis | Solicitar publicación de síntesis | De Wever, 2010; Abdous, 2011 |
| Participante que contribuyó antes y ha dejado de hacerlo | Invitar a retomar con referencia a su contribución anterior (§3.6) | Kim et al., 2021; Baker et al., 2004 |
| Tono del hilo deteriorándose antes de que el conflicto sea explícito | Intervención social preventiva; no esperar al estado conflictivo | Chang & Danescu-Niculescu-Mizil, 2019 |
| Discusión todavía en desarrollo activo y natural | No intervenir - esperar al impasse genuino | VanLehn, 2011; Kapur, 2016 |
| Señales ambiguas sin estado claramente problemático | Abstenerse - la incertidumbre no justifica intervención | Koedinger & Aleven, 2007 |

### 6. Restricciones de generación

Principios que rigen cómo se produce la intervención textual, independientemente
de la técnica seleccionada.

#### 6.1 Una acción por intervención

No combinar múltiples técnicas en un mismo mensaje. La sobreintervención
desplaza la interacción entre pares.

**Evidencia**: An et al. (2009) documentan que el grupo con intervención mínima
del instructor produjo la mayor interacción estudiantil.

#### 6.2 Preferir preguntas sobre afirmaciones

Las preguntas socráticas y de sondeo son más efectivas que las afirmaciones
directas para mantener el discurso productivo.

**Evidencia**: Blignaut & Trollip (2003, categoría Socrática), Rovai (2007,
§3.2), Degen (2025).

#### 6.3 Referenciar contribuciones específicas

Dirigirse a los participantes por nombre y citar sus contribuciones concretas.
La intersubjetividad se construye a través de la referencia directa.

**Evidencia**: An et al. (2009, §5.3, Tabla 1).

#### 6.4 Personalizar la intervención

Las estrategias no deben aplicarse en masa. Considerar las características
individuales del participante y el contexto específico del hilo.

**Evidencia**: Korre et al. (2025, §6.3). Simmhan (2025) implementa
persistencia de contexto para mantener coherencia a lo largo del diálogo.

#### 6.5 Escalera de intensidad

Empezar por la intervención más suave y escalar solo cuando no funcione:

1. Monitorizar en silencio
2. Reconocer ("Buenos puntos aquí")
3. Elicitar abiertamente ("¿Alguien puede elaborar sobre X?")
4. Revoice ("Entonces [estudiante] argumenta que... ¿Todos están de acuerdo?")
5. Dar pista ("Piensen en cómo [concepto] podría aplicarse aquí")
6. Pregunta socrática dirigida
7. Desafiar ("¿Pero qué pasa con [contraejemplo]?")
8. Instrucción directa (proporcionar información, corregir)
9. Reestructurar (asignar roles, dividir en subgrupos, cambiar la pregunta)

**Evidencia**: Korre (2025) propone la escalera de escalación. Graesser (2017)
documenta la progresión de movimientos tutoriales. Murphy (2018) describe la
evolución de directivo a facilitativo.

### Anti-patrones documentados

Patrones a evitar, identificados en la literatura:

| Anti-patrón | Por qué es contraproducente | Fuente |
|-------------|---------------------------|--------|
| Intervenir con demasiada frecuencia | Suprime la voz estudiantil y la agencia | Zulfikar, 2019; Glina |
| Dar respuestas en lugar de preguntas | Cortocircuita la construcción de conocimiento | Graesser, 2017; Degen, 2025 |
| Usar tono desafiante como modo por defecto | Reduce la seguridad psicológica y la calidad | Yan, 2025 |
| Publicar mensajes no-tarea en exceso | Produce efecto "uncanny valley"; daña el aprendizaje | Sikstrom, 2022 (Veletsianos, 2012) |
| Ignorar la dimensión afectiva | Los estudiantes se desconectan sin sentirse escuchados | Richardson, 2015; Sikstrom, 2022 |
| Sobre-andamiar | Crea dependencia; impide la lucha productiva | Kostopoulos et al., 2025 |
| No diagnosticar antes de intervenir | Aplicar técnica incorrecta al estado incorrecto | Korre, 2025 |
| Intervenir antes del impasse - mientras la discusión progresa naturalmente | Cortocircuita la lucha productiva que genera aprendizaje profundo | VanLehn, 2011; Kapur, 2016 |
| Re-intervenir sin cooldown - antes de que los participantes hayan respondido | Desplaza la discusión de centrada en el estudiante a centrada en el facilitador | Rovai, 2007 |
| Decisión basada en estado puntual sin considerar trayectoria | Un hilo que decae desde actividad alta requiere respuesta diferente a uno que nunca despegó | Chang & Danescu-Niculescu-Mizil, 2019 |
| Generar intervención de baja confianza en lugar de abstenerse | La abstención ante señales ambiguas es la respuesta correcta, no un fallo | Koedinger & Aleven, 2007; Anthropic, 2025 |

## Consecuencias

### Positivas

- El repertorio proporciona una base fundamentada para la selección de acciones
  en ADR 0003, donde cada técnica tiene trazabilidad a la literatura.
- La organización en seis categorías permite que el modelo de intervención
  seleccione técnicas de forma estructurada según el estado de la discusión.
- Los disparadores proactivos (§5) proporcionan condiciones explícitas y
  verificables para decidir cuándo intervenir.
- Los anti-patrones documentados funcionan como restricciones negativas que
  protegen contra errores comunes de facilitación.
- La escalera de intensidad (§6.5) operacionaliza el principio de intervención
  mínima.

### Negativas

- El repertorio sintetiza técnicas diseñadas para facilitadores humanos. Su
  transferencia directa a un agente de IA es una propuesta de diseño, no un
  resultado empírico validado.
- Algunas técnicas (asignación de roles, formación de grupos) operan a nivel de
  diseño del curso, no de intervención en un hilo, y requieren integración con
  el LMS.
- La efectividad relativa de las técnicas varía según contexto educativo, nivel
  de los estudiantes y disciplina. No se establece aquí una jerarquía universal.
- La taxonomía de Paul para preguntas socráticas (§2.1) tiene amplio uso
  pedagógico, pero su validación empírica específica en discusiones asíncronas
  con agentes de IA es limitada (Degen, 2025 es un primer estudio).

### Cuestiones abiertas

- ¿Qué subconjunto mínimo de técnicas debe implementar la primera versión del
  sistema (MVP)?
- ¿Cómo se mide la efectividad de cada técnica en el contexto del sistema
  implementado?
- ¿Cómo se integran las técnicas que requieren coordinación con el LMS
  (asignación de roles, formación de grupos) frente a las que operan
  exclusivamente a nivel de texto?
- ¿Cuál es el mecanismo para incorporar nuevas técnicas al repertorio a medida
  que se publique nueva evidencia?

## Referencias

- Abdous, M., & Yen, C. J. (2011). A process-oriented framework for online
  discussion facilitation.
- An, H., Shin, S., & Lim, K. (2009). The effects of different instructor
  facilitation approaches on students' interactions during asynchronous online
  discussions.
- Baker, D. L. (2011). Designing and orchestrating online discussions.
- Beaudin, B. P. (1999). Keeping online asynchronous discussions on topic.
- Blignaut, A. S., & Trollip, S. R. (2003). Measuring faculty participation in
  asynchronous discussion forums.
- Brown, Z. (2015). The use of in-class debates as a teaching strategy in
  increasing students' critical thinking and collaborative learning skills in
  higher education.
- Casebourne, I. (2025). AI for collective intelligence in education.
- De Wever, B., Van Keer, H., Schellens, T., & Valcke, M. (2010). Roles as a
  structuring tool in online discussion groups.
- Degen, M. (2025). Beyond automation: Socratic AI tutor for scaffolding
  research question development.
- Ekeyi, D. N. Question typology based on Christensen (1991).
- Glina. Exploratory talk and the role of the facilitator.
- Graesser, A. C. (2017). AutoTutor and the five-step tutoring frame.
- Gu, P. (2021). Facilitating online discussions using case-based reasoning
  with IBIS.
- Hare, R. (2024). Multi-agent neuro-symbolic framework for tutoring and peer
  interaction.
- Ho, C. H. (2007). Grice's Cooperative Principle and online discussion
  quality.
- Jin, D. (2025). Persona effect of GenAI agents in collaborative moral
  reasoning.
- Korre, D., Tsipas, N., & Peppes, N. (2025). Facilitation and moderation in
  online discussions: A systematic review.
- Kostopoulos, G., Gkamas, V., Rigou, M., & Kotsiantis, S. (2025). Agentic AI
  in education: State of the art and future directions.
- Lim, C. P. (2011). Nine facilitation techniques for peer-led online
  discussions.
- Lippert, A. (2020). Multiple agent designs in conversational intelligent
  tutoring systems.
- Mansour, N. (2024). E-facilitation styles and moderation supports.
- Massey, J. (2019). Faculty presence in asynchronous online discussions.
- Murphy, P. K. (2018). Quality Talk: Developing students' discourse to promote
  high-level comprehension.
- Pilkington, R. (2003). Analysing educational dialogue interaction: Towards
  models that support learning.
- Richardson, J. C., & Lowenthal, P. R. (2015). Instructor social presence and
  teaching presence in online discussions.
- Rovai, A. P. (2007). Facilitating online discussions effectively.
- Sikstrom, P. (2022). How pedagogical agents communicate with students: A
  two-phase systematic review.
- Simmhan, Y. (2025). AI Instructor Agent: Design principles and deployment in
  graduate classrooms.
- Woo, Y. (2007). Meaningful interaction in web-based learning: A social
  constructivist interpretation.
- Yan, L. (2025). Social blindspot in human-AI collaboration: AI persona
  effects on team dynamics.
- Zulfikar, A. F. (2019). The effectiveness of online learning with facilitation
  method.

**Referencias añadidas en revisión 2026-03-30 (integración de investigación
sobre temporización de la intervención - ADR 0006):**

- Aleven, V., & Koedinger, K. R. (2000). Limitations of student control: Do
  students know when they need help? *Proceedings of ITS 2000*, pp. 292-303.
- Baker, R. S. J. d., Corbett, A. T., & Koedinger, K. R. (2004). Detecting
  student misuse of intelligent tutoring systems. *Proceedings of ITS 2004*,
  pp. 531-540.
- Chang, J. P., & Danescu-Niculescu-Mizil, C. (2019). Trouble on the horizon:
  Forecasting the derailment of online conversations as they develop.
  *Proceedings of EMNLP-IJCNLP 2019*, pp. 4743-4754.
- Kapur, M. (2016). Examining productive failure, productive success,
  unproductive failure, and unproductive success in learning. *Instructional
  Science*, 44(4), 379-401.
- Kim, S., Eun, J., Seering, J., & Lee, J. (2021). Moderator chatbot for
  deliberative discussion: Effects of discussion structure and discussant
  facilitation. *Proceedings of the ACM on Human-Computer Interaction*,
  5(CSCW1), Article 38.
- Koedinger, K. R., & Aleven, V. (2007). Exploring the assistance dilemma in
  experiments with cognitive tutors. *Educational Psychology Review*, 19(3),
  239-264.
- VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent
  tutoring systems, and other tutoring systems. *Educational Psychologist*,
  46(4), 197-221.
