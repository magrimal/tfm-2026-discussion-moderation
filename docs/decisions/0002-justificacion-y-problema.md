# ADR-0002: Justificación y problema

## Estado

Propuesto

## Contexto

Este ADR formaliza la exploración inicial documentada en las
[notas iniciales](../notes/notas-iniciales-problema.md), contrastada
con la
[evidencia de la literatura](../literature/evidence-by-hypothesis.md).

### El aprendizaje como proceso social

El aprendizaje significativo no ocurre solo a través de la
transmisión de contenido. En un aula presencial, lo que más impacto
tiene suele ser la discusión: intercambiar ideas, debatir
interpretaciones, reaccionar a otras perspectivas. Estas interacciones
generan curiosidad y exploración más profunda de los temas.

Este proceso es fundamentalmente social. Los estudiantes preguntan,
otros responden, las discusiones evolucionan, el instructor guía la
conversación, y las ideas se construyen unas sobre otras. El resultado
es algo parecido a la inteligencia de grupo: el grupo colectivamente
alcanza una comprensión más profunda que cualquier individuo por
separado.

La literatura respalda esta observación: la interacción significativa
requiere negociación social, múltiples perspectivas y andamiaje dentro
de la zona de desarrollo próximo (Woo & Reeves, 2007). La inteligencia
colectiva depende más de la calidad de la interacción que del
rendimiento individual (Woolley et al., 2010, citado en Casebourne
et al., 2025). Ver
[evidencia, sección 1](../literature/evidence-by-hypothesis.md#1-el-aprendizaje-es-un-proceso-social).

### Las discusiones asíncronas no generan aprendizaje profundo

Cuando el aprendizaje se mueve a entornos digitales — especialmente
asíncronos — ese mecanismo se rompe. Incluso cuando las plataformas
ofrecen foros de discusión, las conversaciones no evolucionan como en
un aula.

Los foros de discusión con hilos de texto (threaded discussions) son
el formato predominante en plataformas educativas (Moodle, Open edX,
Canvas, Blackboard). El problema no es solo que la participación sea
baja. Es que las discusiones no se convierten en experiencias de
aprendizaje:

- La participación sustantiva rara vez ocurre sin estructura
  (An et al., 2009).
- Sin facilitación activa, los hilos se estancan (Lim, 2011).
- La mayoría de los entornos web no soportan adecuadamente la
  interacción significativa (Woo & Reeves, 2007).
- La calidad de un post predice respuestas; la longitud, no
  (Ho & Swan, 2007).

Esto es relevante en MOOCs, educación a distancia, entornos
asíncronos y formatos blended. Ver
[evidencia, sección 2](../literature/evidence-by-hypothesis.md#2-las-discusiones-online-pierden-valor-sin-facilitación).

### La facilitación es efectiva pero depende de recursos que no escalan

En un aula presencial, el instructor guía las conversaciones,
redirige ideas, hace preguntas de seguimiento, conecta la discusión
con el contenido del curso. En entornos asíncronos, los instructores
no pueden escalar esa presencia: no pueden seguir cada hilo,
intervenir en cada conversación, ni guiar las discusiones de forma
continua.

La facilitación es efectiva — la evidencia es clara. La asignación
de roles incrementa la construcción de conocimiento (De Wever et al.,
2010). La facilitación activa lleva al 79.3% de contribuciones con
pensamiento crítico profundo (Lim, 2011). Pero el feedback correctivo
del instructor representó solo el 4.9% de sus postings (Blignaut &
Trollip, 2003). La facilitación funciona, pero depende de un recurso
que no escala. Ver
[evidencia, secciones 3 y 4](../literature/evidence-by-hypothesis.md#3-la-facilitación-activa-mejora-los-resultados-de-aprendizaje).

La facilitación opera en tres dimensiones (Lim, 2011; Pilkington &
Walker, 2003; Richardson et al., 2015):

- **Organizational**: gestión del flujo, estructura, timing.
- **Intellectual**: estimular pensamiento profundo, hacer preguntas,
  conectar ideas.
- **Social**: fomentar participación, crear espacio seguro, reconocer
  contribuciones.

Ver
[evidencia, sección 5](../literature/evidence-by-hypothesis.md#5-roles-de-facilitación-organizational-intellectual-social).

### La AI no se ha aplicado a facilitación de discusiones grupales

Una dirección posible es usar AI para ayudar a facilitar discusiones.
No moderación en el sentido de detectar comentarios inapropiados o
comportamiento problemático, sino facilitación: ayudar a que las
conversaciones evolucionen, generar discusión, guiar las
conversaciones hacia conclusiones significativas.

La investigación en AI educativa se ha centrado en tutoría
(uno-a-uno) y evaluación, no en facilitación de discusiones grupales.
La mayoría del trabajo de NLP se centra en clasificación, no
en facilitación generativa (Korre, 2025). Aproximadamente el 70% de
los estudios se enfoca en AI como entorno, no como agente que facilita
activamente (Casebourne et al., 2025). Ver
[evidencia, sección 6](../literature/evidence-by-hypothesis.md#6-estado-del-arte-ai-como-facilitador-de-discusiones).

Sin embargo, hay señales de que la AI puede operar en este espacio:
personas AI influyen en dinámicas de grupo sin ser detectadas (Yan,
2025), y AI supportive mejora la calidad del razonamiento y reduce el
drift temático (Jin, 2025).

## Problema

En las discusiones remoto basadas en hilos de texto, no existen
mecanismos suficientes para sostener la presencia social y la
construcción colectiva de conocimiento que sí aparecen de forma
natural en un aula presencial.

La facilitación humana es efectiva pero no escalable. La AI educativa
se ha centrado en tutoría y evaluación, no en facilitación de
discusiones grupales. Hay un gap en la investigación y en las
herramientas disponibles.

## Decisión

Este proyecto aborda el gap identificado: diseñar e implementar un
sistema basado en LLMs y context engineering para la facilitación de
discusiones en entornos remotos basadas en plataformas
educativas. Los objetivos, alcance y especificación técnica del
sistema se definen en el
[issue #3](https://github.com/magrimal/tfm-2026-discussion-moderation/issues/3).

El sistema facilita, no evalúa ni califica.

## Consecuencias

### Positivas

- El problema está respaldado por evidencia de la literatura, no solo
  por intuición.
- El scope está acotado a un formato concreto (threaded text-based
  discussions) con problemas documentados y medibles.
- La estructura de tres roles de facilitación (organizational,
  intellectual, social) tiene base en múltiples fuentes
  independientes.

### Negativas

- Excluimos discusiones síncronas, voz y video del scope.
- La evidencia sobre AI como facilitador de discusiones grupales es
  todavía emergente — estamos en un espacio con poca validación
  previa.

## Alcance

- **Formato**: discusiones asíncronas basadas en hilos de texto
  (threaded discussions).
- **Contexto**: educación superior.
- **Vendor-agnóstico**: el diseño no depende de una plataforma
  concreta. Open edX es el proof of concept.
- **El sistema facilita, no evalúa ni califica.**

## Referencias

- An, H., Shin, S., & Lim, K. (2009). The effects of different
  instructor facilitation approaches.
- Blignaut, S. & Trollip, S. R. (2003). Developing a taxonomy of
  faculty participation.
- Casebourne, I. et al. (2025). Using AI to support education for
  collective intelligence.
- De Wever, B. et al. (2010). Roles as a structuring tool in online
  discussion groups.
- Ho, C. H. & Swan, K. (2007). Evaluating online conversation.
- Jin, Y. et al. (2025). When machines join the moral circle.
- Korre, K. et al. (2025). Evaluation and facilitation of online
  discussions in the LLM era.
- Lim, S. C. R. et al. (2011). Critical thinking in asynchronous
  online discussion.
- Pilkington, R. M. & Walker, S. A. (2003). Facilitating debate in
  networked learning.
- Richardson, J. C. et al. (2015). Conceptualizing and investigating
  instructor presence.
- Woo, Y. & Reeves, T. C. (2007). Meaningful interaction in
  web-based learning.
- Woolley, A. W. et al. (2010). Evidence for a collective
  intelligence factor.
- Yan, L. et al. (2025). The social blindspot in human-AI
  collaboration.
