# ADR-0002: Facilitación de conversaciones para aprendizaje social en entornos educativos digitales

## Estado

Propuesto (muy temprano, para alinear ideas)

## Contexto

Lo que nos trajo hasta aquí es una intuición bastante clara: cuando pensamos en **qué es lo que realmente aprendemos y recordamos de una clase**, muchas veces no es solo el contenido, sino las **conversaciones**.

En un aula presencial, el aprendizaje es naturalmente social:

- Escuchas a otros estudiantes.
- Reaccionas a ideas distintas.
- Haces preguntas.
- El profesor guía la conversación sin que nadie lo note demasiado.

Ahí aparece algo clave: **la inteligencia del grupo**. El grupo, en conjunto, entiende más y mejor que cada persona por separado.

El problema es que cuando el aprendizaje se mueve a entornos digitales (online, blended, MOOCs, campus virtuales), **ese mecanismo se rompe**. Los foros existen, pero:

- La participación es baja.
- Pocas personas dominan la conversación.
- Muchos leen pero no escriben.
- Los hilos se quedan a medias.
- No hay cierre ni síntesis.

No es que los estudiantes no quieran aprender. Es que **falta facilitación**.

Y esto pasa tanto en MOOCs como en educación universitaria presencial con componentes online (como en la UCM).

## Problema

El problema que queremos abordar no es "falta de contenido" ni "mal diseño de plataformas". El problema es este:

En los entornos de aprendizaje asincrónicos, no existen mecanismos suficientes para sostener la presencia social y la inteligencia colectiva que sí aparecen de forma natural en un aula presencial. Sin facilitación, las conversaciones no evolucionan, no generan aprendizaje profundo y no se convierten en una experiencia significativa a largo plazo.

Los profesores no tienen la capacidad de:

- Leer todos los mensajes.
- Intervenir a tiempo.
- Guiar cada discusión.
- Mantener viva la conversación.

## Observaciones clave

1. El aprendizaje es un proceso **social**, no solo individual.
2. La inteligencia colectiva no emerge sola en entornos digitales.
3. La presencia del instructor es clave, pero no escalable.
4. Los foros actuales están diseñados para "publicar", no para **pensar juntos**.
5. La ausencia de facilitación hace que las discusiones pierdan valor educativo.

## Decisión (qué queremos explorar)

Explorar el uso de **IA como facilitador de conversaciones educativas** para sostener la presencia social y la inteligencia colectiva en entornos de aprendizaje digitales.

La idea no es automatizar la enseñanza, sino **sostener las condiciones que permiten el aprendizaje social**. En concreto:

- Ayudar a que las conversaciones no se mueran.
- Guiar el foco hacia los objetivos del curso.
- Fomentar la participación equilibrada.
- Generar continuidad, síntesis y cierre.

## Qué entendemos por "intervención"

Aquí es importante aclarar algo: **moderación no es solo control**. Hay distintos tipos de moderación/intervención:

### Moderación pasiva

- Flaggear comentarios.
- Detectar toxicidad.
- Eliminar contenido.

Esto es necesario, pero **no es lo más interesante**.

### Moderación activa (la que nos interesa)

- Hacer preguntas cuando un hilo se estanca.
- Conectar una respuesta con el contenido del curso.
- Invitar a otros a participar.
- Resumir lo que se ha dicho.
- Redirigir la conversación si se va por otro lado.

Esta segunda forma es la que **impacta directamente en el aprendizaje**.

## Rol de la IA

La IA **no** toma decisiones pedagógicas finales. No evalúa. No califica. No reemplaza al docente.

Su rol es:

- Facilitar.
- Acompañar.
- Intervenir de forma ligera.
- Ayudar a que emerja la inteligencia del grupo.

Idealmente:

- Entiende el contexto del curso.
- Entiende el estado de la conversación.
- Actúa cuando hace falta y se calla cuando no.

## Alcance del proyecto

- **Vendor-agnóstico**: no depende de Open edX, Moodle ni de una plataforma concreta.
- **Conceptual y educativo**: el problema trasciende la tecnología.
- **Transferible**: el proof of concept puede ser técnico (por ejemplo, Open edX), pero la idea aplica a cualquier entorno.
