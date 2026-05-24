---
title: "Introducción"
author: "María Grimaldi"
lang: es
bibliography: "references.bib"
csl: "apa.csl"
---

# Introducción

Los debates en clase aumentan el pensamiento crítico y el aprendizaje colaborativo en educación superior [@Brown2015]. Esto tiene sentido desde el constructivismo social, que plantea que el aprendizaje es un proceso colectivo que requiere interacción social para ser efectivo[@WooReeves2007]. Un debate, como técnica de generación de conocimiento, es más útil que la clase tradicional porque da voz a estudiantes más callados y crea un espacio donde todos pueden participar en igualdad [@BineyEkeyi2018; @WooReeves2007] ayudando a interiorizar el conocimiento a través de la interacción con otros. En la educación superior, esto puede verse en el aula, donde un instructor guía la discusión, o fuera de ella, a través de plataformas digitales que permiten el trabajo asíncrono.

En los últimos años, la educación superior en línea ha crecido en Europa. En 2021, el 100% de las instituciones del Espacio Europeo de Educación Superior ya usaba alguna forma de aprendizaje digital [@GaebelEtAl2021]. Para 2025, el 75% de las universidades usa blended learning como modalidad principal y el 36% ofrece al menos un programa de grado completamente en línea [@GaebelEtAl2025]. Dependiendo del tipo de institución, estas plataformas, conocidas como sistemas de gestión del aprendizaje (LMS, por sus siglas en inglés), son la modalidad principal del curso o un complemento a la educación presencial. Soluciones como Moodle, Canvas, Open edX o Coursera permiten organizar contenidos, actividades y foros de discusión en un mismo entorno, y pueden estar guiadas por un instructor o avanzar a ritmo del estudiante.

La pandemia de 2020 aceleró este proceso de forma significativa, y diversas instituciones reportaron más avances en digitalización durante los primeros cuatro meses de la crisis que en los cuatro años anteriores [@GaebelEtAl2021]. Como consecuencia, la interacción entre estudiantes pasó a ocurrir casi exclusivamente a través de herramientas digitales, lo que la literatura describe como comunicación mediada por computador (CMC), y los foros de discusión se consolidaron como el mecanismo principal de este tipo de interacción en educación en línea [@Rovai2007; @MasseyEtAl2019].

Los foros de discusión en plataformas educativas cumplen funciones concretas que el aula presencial no puede ofrecer. Permiten escalar la participación a un número de estudiantes que sería inmanejable en un aula tradicional, como muestra el estudio de Zulfikar et al. (2019) con más de 5.000 estudiantes en discusiones paralelas a través de Moodle [@ZulfikarEtAl2019]. Además, la CMC le da a cada estudiante más oportunidades de participar que en el formato presencial, donde el instructor puede acaparar hasta el 80% del tiempo de habla [@SullivanPratt1996], y en los foros todos pueden contribuir sin importar su ubicación o disponibilidad de horario [@MasseyEtAl2019]. Por último, permiten formas nuevas de evaluación, como rúbricas basadas en la calidad de los aportes que hacen posible medir el pensamiento crítico de manera más directa que un examen tradicional [@HoSwan2007; @Rovai2007].

La facilitación de las discusiones en CMC recae principalmente sobre el instructor, que cumple un rol organizacional, uno intelectual y uno social [@Abdous2011]. Cuando los asume de forma activa, la participación se distribuye de manera más equitativa entre estudiantes [@AnEtAl2009], el 79.3% de las contribuciones alcanza pensamiento crítico profundo [@LimEtAl2011] y la asignación de roles estructurados aumenta significativamente la construcción de conocimiento [@DeWeverEtAl2010]. Sin embargo, este nivel de presencia tiene un límite práctico, y Rovai (2007) lo establece entre 20 y 30 estudiantes como máximo manejable para un solo foro activo, señalando que superar ese número genera abrumamiento tanto en docentes como en estudiantes [@Rovai2007]. Estudios de cursos de posgrado muestran que el 57% de los comportamientos de presencia del instructor son de tipo social, no instruccional [@RichardsonEtAl2015], y el feedback correctivo representó apenas el 4.9% de los posteos a pesar de que los estudiantes lo consideran esencial [@BlignautTrollip2003]. Facilitadores también reportaron que gestionar varias discusiones simultáneamente hizo imposible mantener la profundidad del compromiso [@Mansour2024]. En el contexto de la educación en línea masiva, donde un solo curso puede concentrar miles de estudiantes, los problemas de escala se vuelven críticos para cualquier facilitador humano [@GuEtAl2021; @YuEtAl2024maic].

Los LLMs han demostrado capacidad para operar en educación a escala masiva. Plataformas como Coursera han integrado asistentes basados en GPT-4 en más de 100 cursos [@PENDIENTE: Coursera2024] y edX alcanzó 1.2 millones de estudiantes en seis meses con laboratorios virtuales impulsados por IA [@PENDIENTE: MarketGrowthReports2026]. La revisión de Chu et al. (2025) documenta avances en la automatización de tareas pedagógicas usando agentes LLM a escala [@ChuEtAl2025]. Sin embargo, la mayoría de estas aplicaciones se centran en tutoría individual y evaluación, no en la facilitación de discusiones grupales. Korre et al. (2025) señalan que el trabajo de NLP existente se enfoca en clasificación (detectar toxicidad, analizar postura) en lugar de producir intervenciones que mejoren activamente la calidad de una discusión [@KorreEtAl2025], y alrededor del 70% de los estudios posicionan a la IA como un entorno que estructura condiciones de aprendizaje, no como un agente que facilita activamente [@CasebourneEtAl2025]. Los sistemas que sí intentan facilitar discusiones, como MAIC [@YuEtAl2024maic] y el sistema de razonamiento por casos de Gu et al. (2021) [@GuEtAl2021], muestran limitaciones en el pensamiento profundo y en la adaptación a contenidos no previstos.

En esta tesis nos centramos en discusiones asíncronas mediadas por computador, donde la facilitación es responsabilidad del instructor. Aunque la literatura reconoce que los estudiantes también pueden facilitar, ese no es nuestro enfoque. Los rasgos psicológicos del instructor tampoco forman parte del problema que buscamos resolver, sino las decisiones más sistemáticas y controlables, como cuándo intervenir, en qué estado está la conversación y qué decir.

El sistema propuesto no fue evaluado con grupos reales de estudiantes a escala, es más un escenario teórico donde este tipo de intervención sería necesaria. La validación empírica de su impacto en el aprendizaje queda para trabajo futuro.

El objetivo de este trabajo de fin de máster es diseñar e implementar un sistema basado en LLMs y técnicas de context engineering para facilitar discusiones asíncronas en LMS de código abierto. El sistema debe interactuar de forma contextualizada con los participantes, utilizando el contenido del curso y literatura pedagógica sobre discusiones, e integrarse con Open edX como plataforma de referencia.

Los objetivos específicos son los siguientes.

- Diseñar e implementar un sistema de agentes basado en LLMs, organizado en etapas, capaz de producir intervenciones coherentes con el tema de la discusión y con continuidad conversacional, dentro de tiempos y consumo de recursos razonables.
- Definir e implementar una estrategia de context engineering fundamentada en la literatura, que integre el contenido del curso y literatura pedagógica sobre discusiones, con criterios de desempeño derivados de cómo un instructor facilita una discusión de forma efectiva.
- Diseñar e implementar la arquitectura de integración con Open edX, incluyendo los puntos de conexión, el flujo de datos y los mecanismos de comunicación que permiten al sistema consumir threads de discusión como input.
- Evaluar el comportamiento del sistema en escenarios generados a partir de estudios anteriores, midiendo la precisión en la clasificación del estado de la conversación y la coherencia de las intervenciones generadas.

## Plan de trabajo

El trabajo se desarrolla en las siguientes fases.

### 1. Definición del problema y planificación

- Delimitar el problema de investigación en torno a la facilitación de discusiones asíncronas en educación superior.
- Definir el alcance funcional y técnico del sistema.
- Definición del problema, objetivos, requisitos y establecimiento del enfoque de planificación y metodología de trabajo.

### 2. Investigación y exploración técnica

- Analizar el estado del arte en discusiones asíncronas en educación superior.
- Estudiar cómo se facilita una discusión efectiva y cuál es el rol de los distintos participantes.
- Investigar el uso de agentes conversacionales en contextos educativos y su impacto en el engagement.
- Explorar técnicamente el uso de LLMs para moderación y facilitación de discusiones.
- Definir la estrategia de context engineering basándose en la investigación inicial, considerando:
  - Rol pedagógico del agente.
  - Objetivos de la discusión.
  - Estructura y dinámica del debate.
  - Contenido del curso como contexto base.
  - Problemas comunes documentados en la literatura sobre discusiones asíncronas (por ejemplo: baja participación, intervenciones superficiales, falta de cohesión, pérdida de foco, turnos), con el objetivo de proponer mecanismos para abordarlos o mitigarlos mediante el diseño del contexto.
- Realizar pruebas exploratorias (spikes) para evaluar viabilidad técnica y posibles limitaciones.

### 3. Diseño de la arquitectura del sistema

- Diseñar la arquitectura interna del sistema basado en LLMs, incluyendo:
  - Estructura de agentes.
  - Orquestación.
  - Construcción y gestión del contexto.
  - Flujo de intervención en discusiones.
- Diseñar la arquitectura completa del sistema a nivel general, incluyendo:
  - Componentes internos.
  - Comunicación entre módulos.
  - Separación entre sistema de agentes y plataforma educativa.
- Diseñar la arquitectura de integración con Open edX, definiendo:
  - Puntos de conexión.
  - Flujo de datos.
  - Mecanismos de comunicación.

### 4. Implementación técnica

- Implementar el sistema basado en LLMs y context engineering en Python.
- Desarrollar los componentes internos del sistema (agentes, manejo de contexto, lógica de intervención).
- Implementar los mecanismos de integración con Open edX (backend, infraestructura y plugin si aplica).
- Desarrollar la capa frontend necesaria para permitir la interacción entre estudiantes y el sistema dentro del entorno de discusión.

### 5. QA y validación

- Realizar pruebas técnicas (rendimiento, estabilidad y carga).
- Evaluar el comportamiento del sistema en escenarios reales o simulados.
- Realizar pruebas piloto con estudiantes.
- Recoger feedback cualitativo y cuantitativo.
- Analizar el impacto del sistema en la dinámica y calidad de las discusiones.
