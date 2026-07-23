# Glosario

Referencia de términos, acrónimos y conceptos usados en este repositorio. Actualizar cuando se introduce un término nuevo en el código, documentación o ADRs.

Para convenciones de escritura y términos que deben evitarse, ver también `.claude/agent-memory/terminology.md`.

---

## Acrónimos

| Acrónimo | Expansión | Descripción |
|----------|-----------|-------------|
| ADR | Architecture Decision Record | Registro de una decisión de arquitectura: contexto, decisión y consecuencias. Los ADRs de este proyecto están en `docs/decisions/`. |
| API | Application Programming Interface | Interfaz de programación; en este proyecto, la HTTP REST API del sistema de facilitación y la API del foro de Open edX. |
| CLI | Command Line Interface | Interfaz de línea de comandos. El playground del proyecto se invoca como `uv run facilitate <thread>.json`. |
| JWT | JSON Web Token | Formato de token de autenticación. Usado para autenticar las llamadas del sistema de facilitación al foro de Open edX. |
| LLM | Large Language Model | Modelo de lenguaje de gran escala (p. ej. Claude). Los nodos del pipeline que realizan razonamiento invocan un LLM. |
| PoC | Proof of Concept | Prueba de concepto. Open edX es el PoC de integración; el diseño del sistema es independiente de la plataforma. |
| TFM | Trabajo Fin de Máster | Este proyecto. Título completo: *Diseño, implementación e integración de un modelo de moderación inteligente para discusiones académicas en plataformas de aprendizaje abiertas*. |

---

## Conceptos de dominio

| Término | Definición | Notas |
|---------|-----------|-------|
| Entorno asíncrono | Espacio de interacción donde las respuestas no ocurren en tiempo real (foros, tableros de discusión). | El sistema opera exclusivamente en este tipo de entorno. |
| Escalera de diálogo tutorial (EMT) | Cuatro movimientos de diálogo con intensidad creciente: pump (L1), hint (L2), prompt (L3), assertion (L4). El sistema aplica el nivel mínimo efectivo y escala solo si niveles anteriores no produjeron avance. | Fuente: Lippert et al. 2020; Graesser 2017 (AutoTutor). Ver ADR 0046 §2.2. |
| Facilitación | El proceso de apoyar y guiar una conversación sin imponer conclusiones. | Término preferido sobre "moderación" cuando se habla del rol activo de apoyo. |
| Facilitador intelectual | Rol que conecta la conversación con los objetivos de aprendizaje mediante preguntas, síntesis y desafíos. | Usa la escalera EMT completa; por defecto L1-L2. |
| Facilitador organizacional | Rol que gestiona la estructura, flujo y logística de la conversación. | Usa EMT L1 (pumps) y resúmenes; L3 solo para problemas estructurales claros. |
| Facilitador social | Rol que fomenta la participación equilibrada y la cohesión del grupo. | Usa pumps afectivos (L1) y reconocimientos. Evita prompts directos. |
| Inteligencia colectiva | El conocimiento o comprensión que emerge del grupo como conjunto, más allá de las contribuciones individuales. | No confundir con "group knowledge" como suma de partes. |
| Intervención | Un acto del sistema de facilitación dirigido a una conversación: texto generado, pregunta, síntesis o escalada. | Cada intervención se registra en el historial del hilo. |
| Moderación activa | Intervenciones que guían la conversación: preguntas, síntesis, conexiones entre ideas. | El foco del TFM. |
| Moderación pasiva | Acciones de control: flagging, eliminación de contenido, detección de toxicidad. | Mencionada por contraste; no es el foco. |
| Presencia social | La sensación de estar con otros en un entorno de aprendizaje digital; condición necesaria para el aprendizaje colaborativo. | Del marco Community of Inquiry (CoI). |

---

## Conceptos del sistema

| Término | Definición | Notas |
|---------|-----------|-------|
| Agente de rol | Agente especializado que genera la intervención final según uno de los tres roles de facilitación. | Seleccionado por el orquestador tras decidir intervenir. |
| Clasificación | Primer paso del pipeline: analiza el estado de la discusión y produce señales estructuradas. | Sin estado de discusión claro, el pipeline no continúa. |
| Cooldown | Restricción temporal que impide intervenir en el mismo hilo si ya se intervino recientemente. | Configurado por `min_hours_between_interventions`; verificado contra el historial. |
| Estado de la discusión | Clasificación del hilo: `stalled`, `off_topic`, `conflictive`, `formulaic`, `shallow`, `healthy`. | Producido por el nodo de clasificación; determina si el pipeline interviene. |
| Historial de intervenciones | Registro por hilo de las intervenciones anteriores: rol usado, técnica, timestamp. | Necesario para la escalada EMT en orden y las restricciones de cooldown. Ver ADR 0007. |
| Nodo | Unidad del pipeline que recibe el estado y produce una decisión o acción. Los nodos con LLM realizan una llamada al modelo. | Los nodos sin LLM aplican reglas deterministas. |
| Orquestador | Nodo que decide qué rol de facilitación actuar dado el estado clasificado del hilo. | Ver `docs/agents/orchestrator-agent.md`. |
| Pipeline | Secuencia de nodos que procesa un hilo: clasificación → decisión de intervención → orquestación → rol. | Descrito en `docs/pipeline.md`. |
| Técnica de facilitación | Acción concreta seleccionada por un agente de rol (p. ej. pump, hint, desafío, síntesis). | Repertorio completo en ADR 0046. |
