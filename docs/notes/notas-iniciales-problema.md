# Notas iniciales: justificación y problema

Notas de la exploración inicial del espacio del problema, previas a
la revisión de literatura. Capturan la intuición y motivación
personal que originó el proyecto.

Referenciadas desde
[ADR-0002](../decisions/0002-justificacion-y-problema.md).

---

## Qué estoy intentando hacer ahora

En esta fase estoy intentando entender el espacio del problema, no
la implementación técnica.

Las preguntas principales son:

- ¿Cuál es el problema real que intentamos resolver?
- ¿Por qué es importante este problema en educación?
- ¿Qué contexto justifica este proyecto?
- ¿Qué soluciones existen ya?

El objetivo ahora es justificar el proyecto y definir su alcance,
no diseñar el sistema todavía.

Concretamente, quiero:

- describir el problema y su impacto en contextos educativos
- explicar de dónde viene la necesidad del proyecto
- identificar beneficios técnicos y académicos
- investigar soluciones existentes como líneas base
- enmarcar el proyecto como un TFM de ingeniería informática

## Intuición inicial sobre el problema

Desde mi experiencia en educación, una de las partes más importantes
del aprendizaje es la discusión.

En las clases, lo que más me queda es:

- las discusiones con otros estudiantes
- intercambiar ideas
- debatir interpretaciones
- reaccionar a otras perspectivas

Estas interacciones generan curiosidad y exploración más profunda
de las ideas.

Más allá de los trabajos y proyectos, las discusiones son lo que
realmente se queda contigo.

## El aprendizaje como proceso social

El aprendizaje en un aula es muy social.

En aulas presenciales:

- los estudiantes hacen preguntas
- otros responden
- las discusiones evolucionan
- los instructores guían las conversaciones
- las ideas se construyen unas sobre otras

Esto produce algo parecido a la inteligencia de grupo: el grupo
colectivamente alcanza una comprensión más profunda.

Esta es una parte importante de cómo funciona el aprendizaje en
aulas reales.

## Inteligencia de grupo

Creo que la idea de inteligencia de grupo es muy importante.

En las aulas:

- la dinámica de grupo contribuye al aprendizaje
- las ideas emergen de las interacciones
- la comprensión se desarrolla de forma colaborativa

La pregunta es:

¿Cómo podemos llevar esta inteligencia de grupo a los entornos de
aprendizaje online?

## El reto en el aprendizaje online

En la educación online, especialmente en entornos asíncronos, esta
dinámica es difícil de reproducir.

Incluso cuando las plataformas ofrecen foros de discusión:

- la participación puede ser baja
- las conversaciones se estancan
- los hilos no se desarrollan en profundidad
- los estudiantes no siempre interactúan de forma significativa

El problema no es solo tener un foro.

Es cómo evolucionan las discusiones realmente.

## Presencia del instructor

En las aulas, los instructores juegan un rol clave en las
discusiones.

Ellos:

- guían las conversaciones
- redirigen ideas
- hacen preguntas de seguimiento
- conectan las discusiones con el contenido del curso

Pero en entornos asíncronos, los instructores a menudo no pueden
escalar esta presencia.

No pueden:

- seguir cada hilo de discusión
- intervenir en cada conversación
- guiar las discusiones de forma continua

Esto crea un gap en los entornos de aprendizaje online.

## Por qué esto importa en educación online y a distancia

Este problema es aún más relevante en:

- MOOCs
- educación a distancia
- entornos de aprendizaje asíncronos
- formatos blended

En estos contextos, la presencia del instructor es limitada.

Sin embargo, las discusiones siguen siendo un componente importante
del aprendizaje.

Necesitamos pensar en cómo apoyar esas discusiones.

## Rol de la AI

Una dirección posible es usar AI para ayudar a facilitar
discusiones.

Originalmente pensé en construir un modelo específicamente para
moderación.

Pero hay diferentes formas de abordarlo.

Podríamos:

- construir un modelo especializado entrenado para moderación
- usar un modelo general y aplicar context engineering para guiarlo

Esta es todavía una pregunta abierta.

## Importancia del contexto

Para que un sistema AI intervenga de forma significativa en las
discusiones, necesita entender el contexto del curso.

Esto puede incluir:

- el material del curso
- los objetivos de aprendizaje
- el hilo de discusión actual
- lo que ya se ha dicho

El sistema podría necesitar tiempo para procesar el contenido del
curso antes de interactuar con las discusiones.

Cómo hacer esto exactamente no está claro y tendrá que explorarse
más adelante.

## Moderación vs facilitación

Moderación puede significar cosas diferentes.

Una interpretación es:

- detectar comentarios inapropiados
- señalar comportamiento problemático

Pero otra interpretación, más interesante, es:

- ayudar a que las conversaciones evolucionen
- generar discusión
- guiar las conversaciones hacia conclusiones significativas

Esta segunda interpretación está más alineada con los resultados
de aprendizaje.

Ejemplos de intervención significativa incluyen:

- promover más discusión
- hacer preguntas de seguimiento
- conectar la discusión con temas del curso
- fomentar la participación

## Definir intervención

Es importante definir claramente qué queremos decir con
intervención.

Interpretaciones posibles:

Acciones de moderación:

- señalar contenido
- detectar comportamiento problemático

Acciones de facilitación:

- generar conversaciones
- hacer preguntas reflexivas
- guiar el flujo de la discusión

La facilitación es probablemente la dirección con más impacto,
pero también puede ser más compleja.

## Alcance educativo

Quiero que la solución sea independiente de la plataforma.

La idea central no debería depender de un LMS específico.

Debería aplicarse a sistemas como:

- Open edX
- Moodle
- otras plataformas de aprendizaje online

Por razones prácticas, el proof of concept se implementaría en
Open edX.

Pero el concepto debería ser transferible.

## Impacto a largo plazo

El objetivo más amplio es explorar cómo la AI podría intervenir en
discusiones educativas de forma:

- significativa
- sostenible
- beneficiosa para el aprendizaje

La esperanza es que estos sistemas puedan apoyar mejores
conversaciones en entornos de aprendizaje digital, especialmente
donde la presencia del instructor es limitada.

## Motivación personal

Las discusiones que tuve en algunas clases fueron los momentos que
realmente despertaron mi interés y curiosidad.

Esas conversaciones me empujaron a explorar temas más en
profundidad.

Este proyecto es en parte sobre entender cómo llevar ese tipo de
experiencia a la educación online.
