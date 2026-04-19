# ADR 0006: Sistemas de referencia para patrones de diseño del pipeline de facilitación

**Estado**: Propuesto
**Fecha**: 2026-03-29
**Depende de**: ADR 0005 (Arquitectura multi-agente)

## Descripción

El pipeline definido en ADR 0005 adopta una arquitectura multi-agente, pero
no ancla sus decisiones de diseño en sistemas desplegados anteriores. Patrones
como la separación orquestador/especialista, el no-op como salida de primera
clase, la gestión del contexto bajo restricciones de ventana, o los umbrales de
confianza para la intervención aparecen en sistemas reales con historiales de
fallos y aprendizajes documentados. Sin mapear explícitamente el pipeline a
esos sistemas de referencia, las decisiones de diseño son más difíciles de
defender y se arriesga reinventar soluciones ya resueltas.

## Decisión

Adoptamos dos categorías de sistemas como referencia para validar los patrones
de diseño del pipeline de facilitación:

- **Referencia primaria - agentes de código multi-agente** (e.g., Claude Code,
  SWE-agent): sistemas desplegados que resuelven el mismo problema estructural
  de decidir cuándo y cómo intervenir, con qué especialista, bajo restricciones
  de contexto, y con "no intervenir" como respuesta legítima.
- **Referencia primaria - sistemas de tutoría inteligente** (e.g., AutoTutor,
  Carnegie Learning): literatura consolidada sobre modelo del estudiante,
  detección de estado de conocimiento, y secuenciación de intervenciones en
  contextos de aprendizaje.

Ambas referencias se utilizan para validar decisiones ya tomadas en ADR
anteriores, no como fuente de nuevos requisitos.

## Mapeo de patrones

### De agentes de código multi-agente

| Patrón en agentes de código | Equivalente en el pipeline de facilitación |
|---|---|
| Separación orquestador / agente especialista | Orquestador selecciona rol; el nodo de rol ejecuta |
| No-op como salida de primera clase | `ClassifierEval` termina sin intervención cuando no hay valor añadido |
| Gestión del contexto bajo límite de ventana | `get_techniques()` recupera técnicas relevantes en lugar de cargar el repertorio completo |
| Evaluador con reintento | `ResponseEval` devuelve al orquestador si la respuesta no es viable |
| Herramientas como intervenciones precisas | Los nodos de rol usan tools para enriquecer contexto dinámicamente |

El patrón más relevante es que los agentes de código aprendieron, a través de
fallos en producción, que la intervención constante degrada el juicio humano.
La inhibición de la intervención no es un caso límite: es el comportamiento
esperado en la mayoría de las ejecuciones.

### De sistemas de tutoría inteligente

| Patrón en ITS | Equivalente en el pipeline de facilitación |
|---|---|
| Modelo del estudiante | `get_participant_history()` - historial de participación por estudiante |
| Detección de estado cognitivo | Clasificador - estado de la discusión (enganche, profundidad, balance) |
| Selección de tipo de intervención | Orquestador - rol organizacional, intelectual o social |
| Secuenciación de intervenciones | Umbral de confianza del evaluador; límite de reintentos |

La diferencia relevante: los ITS asumen un modelo de respuesta correcta/
incorrecta. La facilitación de discusiones académicas abiertas no tiene
respuesta correcta. El patrón de detección de estado sí transfiere; el patrón
de retroalimentación correctiva, no.

## Consecuencias

### Positivas

- Las decisiones de ADR 0005 quedan ancladas en prior art con historial
  documentado, lo que fortalece la argumentación de la tesis.
- El patrón "no intervenir es la respuesta mayoritaria" refuerza el diseño del
  clasificador como primera línea de decisión, no como paso de rutina.
- La literatura de ITS aporta vocabulario y marcos evaluativos reutilizables
  para la sección de evaluación de la tesis.
- Los patrones de herramientas de agentes de código justifican la decisión de
  no incluir el repertorio completo en el prompt del nodo de rol.

### Negativas

- Los agentes de código optimizan para completar tareas, no para aprendizaje.
  Trasladar patrones sin verificar la equivalencia del dominio puede sesgar el
  diseño hacia eficiencia en detrimento del efecto pedagógico.
- Los ITS con mejor documentación (Carnegie Learning, AutoTutor) operan en
  dominios con respuesta correcta definida. La validez del mapeo debe
  justificarse explícitamente para cada patrón adoptado.
- Establecer estos sistemas como referencia crea una deuda de lectura: cada
  decisión de diseño que invoque un patrón necesita la cita correspondiente.

## Alternativas Consideradas

- **Sistemas de recomendación** (Netflix, Spotify): útiles para patrones de
  temporización de intervención y umbrales de confianza, pero diseñados para
  consumo pasivo, no participación activa. Descartados como referencia primaria.
- **Automatización de revisión de código** (GitHub Copilot PR review): paralelo
  estructural directo (leer contexto → clasificar → comentar o no comentar),
  pero optimiza para calidad del código, no para aprendizaje. Útil como
  referencia puntual para el patrón no-op, no como sistema de referencia global.
- **Marco Community of Inquiry** (Garrison et al.): mejor ajuste de dominio
  (presencia cognitiva, social y de enseñanza mapea directamente a los tres
  roles de facilitación), pero es un marco pedagógico, no un sistema
  implementado. Se usa como referencia teórica en otros ADR; no aplica aquí
  como sistema de referencia de implementación.

## Cuestiones Abiertas

- ¿Qué métricas de evaluación de ITS son aplicables al pipeline? Los ITS
  miden aprendizaje post-intervención; la tesis necesita definir qué mide como
  proxy de facilitación efectiva.
- ¿Existe literatura de ITS específica para facilitación de discusiones
  abiertas (sin respuesta correcta) que complemente AutoTutor?
