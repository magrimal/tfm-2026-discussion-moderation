# DDA-0041: Corpus de discusiones académicas con datos reales y generación sintética

## Estado

Aceptado

## Contexto

El pipeline de facilitación inteligente desarrollado en este TFM necesita un conjunto de discusiones académicas con patrones de participación conocidos para validar su comportamiento. Estos patrones son: dominación, formulismo, angustia explícita, ataque directo, hostilidad seguida de silencio, e integración conceptual.

No existía un corpus etiquetado públicamente disponible que cubriera estos seis patrones en el contexto de cursos MOOC abiertos. Las opciones consideradas eran construir el corpus desde cero con contenido completamente inventado, extraer datos de cursos reales, o combinar ambos enfoques según el contexto del curso.

El sistema de demostración se despliega sobre dos cursos: uno de introducción a la programación (Java) y otro de ética en IA. El primero tiene correspondencia directa con datasets MOOC públicos; el segundo no.

## Decisión

Decidimos construir el corpus con dos fuentes diferenciadas: extracción y curaduría manual de hilos reales del dataset Zenodo de edX (UC3Mx/IT.1.1x, Java MOOC) para el curso de programación, y generación de hilos sintéticos mediante un modelo de lenguaje grande (LLM) para el curso de ética en IA.

### Datos reales — curso de programación

El dataset utilizado es el publicado en Zenodo por Ruipérez-Valiente et al. (2021), que contiene registros de eventos de foro en formato NDJSON de la plataforma edX. Se procesaron 37.992 eventos de tipo `edx.forum.thread.created` y 6.071 de tipo `edx.forum.comment.created`, enlazando comentarios a hilos mediante el campo `event.discussion.id`.

Se desarrolló el script `scripts/extract_mooc_threads.py` para este procesamiento. Los criterios de filtrado fueron: mínimo 3 comentarios por hilo y cuerpo del mensaje inicial de más de 100 caracteres. Se obtuvieron 480 candidatos. De estos, la investigadora revisó los hilos directamente y seleccionó 6, uno por patrón, priorizando aquellos con lenguaje auténtico, variedad de participantes y estructura clara del patrón objetivo. Los nombres de usuario fueron anonimizados (student1, student2, etc.). Los hilos curados se almacenan en `docs/threads/real/`.

### Datos sintéticos — curso de ética en IA

Para el curso de ética en IA no existe un dataset MOOC público equivalente. Se generaron 3 hilos sintéticos con Claude Sonnet (Anthropic, 2024) cubriendo los patrones formulismo, hostilidad-seguida-de-silencio e integración conceptual. El contenido se ancló en los temas del curso (principios éticos, criterios de equidad, marcos de gobernanza) para mantener coherencia pedagógica. Los hilos sintéticos se almacenan en `docs/threads/ai-ethics/`.

### Integración en la plataforma

Los hilos se importan mediante scripts de seeding (`scripts/seed_programming_intro.py` y `scripts/seed_ai_ethics.py`) que usan la API interna del foro de Open edX (`forum.backends.mysql.api.MySQLBackend`). Cada hilo se asigna al componente de discusión correspondiente del curso mediante el `commentable_id` del XBlock.

## Consecuencias

### Positivas

- Los datos reales aportan autenticidad lingüística y variedad de estilos que el contenido completamente inventado no puede replicar.
- La generación sintética permite cubrir contextos sin datos públicos disponibles, con control total sobre el patrón de participación representado.
- La separación en dos fuentes documentadas facilita la reproducibilidad: cualquier evaluador puede acceder al dataset de Zenodo y verificar la curaduría.
- El corpus cubre los seis patrones objetivo con ejemplos en contextos pedagógicos distintos, lo que aumenta la diversidad de la evaluación.

### Negativas

- Los datos sintéticos generados por LLM pueden no capturar la variabilidad real del lenguaje estudiantil, especialmente en situaciones de angustia o conflicto.
- La curaduría manual de los 6 hilos reales introduce sesgo de selección: los hilos elegidos son representativos del patrón, pero pueden no ser representativos de la distribución real de discusiones en MOOC.
- El dataset de Zenodo corresponde a un MOOC de programación en Java de 2016; el lenguaje y las dinámicas pueden no generalizar a otros contextos.

## Alternativas Consideradas

- **Corpus completamente inventado**: descartado porque el lenguaje producido manualmente es predecible y homogéneo, lo que reduciría la validez externa de la evaluación.
- **Uso exclusivo de datos reales**: descartado porque no existe un dataset público equivalente para el dominio de ética en IA, y construir uno desde cero estaba fuera del alcance del TFM.
- **Anotación automática del corpus de Zenodo con todos los patrones**: descartado por la baja cobertura de los patrones menos frecuentes (ataque directo, angustia explícita) en el dataset, que habrían requerido revisión manual extensiva para verificar las etiquetas.
