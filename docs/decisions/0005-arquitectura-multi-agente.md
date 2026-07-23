# ADR 0005: Arquitectura multi-agente con pipeline configurable

**Estado**: Propuesto
**Fecha**: 2026-03-23
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0004 (Roles de
facilitación)

## Descripción

El PoC de agente único (PR #15) implementa las tres fases del modelo de
intervención (ADR 0003) en un único prompt monolítico. Esto impide evaluar
cada fase de forma independiente, ajustar el comportamiento por rol de
facilitación o modificar una fase sin afectar las demás. El sistema necesita
evolucionar hacia una arquitectura que refleje la separación de
responsabilidades definida en los ADR anteriores.

Además, para investigar qué configuración del pipeline produce mejores
resultados de facilitación, la topología del pipeline debe ser configurable
sin modificar código.

## Decisión

Adoptar una arquitectura multi-agente implementada como un grafo dirigido
mediante `pydantic_graph` (incluido en la dependencia `pydantic-ai`). Cada
agente es un nodo del grafo con tipos de entrada y salida definidos. Los
nodos se comunican mediante un estado mutable compartido (`PipelineState`),
y la configuración del pipeline (qué nodos están activos) se define en
dependencias inmutables (`PipelineDeps`).

### Agentes (nodos del grafo)

| Nodo | Responsabilidad | Entrada | Salida |
|------|----------------|---------|--------|
| **Classifier** | Clasifica el estado de la discusión y decide si intervenir (Fase 1, ADR 0003) | Hilo de discusión | `ClassificationResult` |
| **ClassifierEval** | Validación opcional de la clasificación: comprobaciones basadas en reglas + confianza LLM | `ClassificationResult` | Pasa al orquestador o termina |
| **Orchestrator** | Selecciona qué rol de facilitación activar (ADR 0004). No selecciona la acción. | Clasificación + hilo | `RoleSelection` |
| **Role** (uno por rol) | Selecciona la técnica y genera la respuesta. Tiene herramientas para consultar la base de conocimiento y el contexto del curso. | Selección de rol + hilo | `FacilitationResponse` |
| **ResponseEval** | Validación de la respuesta: reglas primero (respuesta no vacía, técnica válida, sin lenguaje evaluativo), luego confianza LLM opcional. Si no es viable, retorna al orquestador (reintento). | `FacilitationResponse` | Pasa al escritor o reintenta |
| **Writer** | Adapta tono y lenguaje al contexto del curso y audiencia. Opcional, desactivable. | Respuesta + contexto del curso | `WriterOutput` |

### Topología del grafo

```
[*] --> Classifier
Classifier --> ClassifierEval
ClassifierEval --> Orchestrator : intervenir
ClassifierEval --> [*] : no intervenir
Orchestrator --> Role
Role --> ResponseEval
ResponseEval --> Writer : respuesta viable
ResponseEval --> Orchestrator : reintento (máx. N)
ResponseEval --> [*] : reintentos agotados
Writer --> [*]
```

### Nodos evaluadores configurables

Los nodos `ClassifierEval` y `ResponseEval` son activables mediante
configuración. Cuando están desactivados, pasan directamente al siguiente
nodo sin coste adicional (ni reglas ni llamada LLM). Cuando están
activados, ejecutan:

1. **Comprobaciones basadas en reglas** (coste cero): respuesta no vacía,
   técnica perteneciente al repertorio del rol, ausencia de lenguaje
   evaluativo (invariante: el sistema facilita, no evalúa).
2. **Evaluación de confianza LLM** (opcional, coste adicional): un agente
   ligero que califica la adecuación de la respuesta.

Esta configurabilidad permite experimentar con diferentes topologías del
pipeline cambiando parámetros, no código.

### Herramientas para enriquecimiento de contexto

Los agentes de rol disponen de herramientas (`pydantic-ai` tools) para
consultar información de forma dinámica:

- `get_techniques(role, state)`: recupera técnicas relevantes del
  repertorio (ADR 0046) filtradas por rol y estado de la discusión. Evita
  incluir todo el repertorio en el prompt.
- `get_course_context(course_id)`: obtiene contexto del curso desde el
  backend LMS configurado.
- `get_participant_history(course_id, user_id)`: obtiene historial de
  participación de un estudiante.

La interfaz del backend LMS es abstracta (`LMSBackend` protocol), con
implementación para Open edX como prueba de concepto. Otros backends
(Moodle, etc.) pueden añadirse implementando el mismo protocolo.

## Consecuencias

### Positivas

- Cada agente se puede evaluar de forma independiente.
- Los prompts de cada rol codifican conocimiento especializado del ADR 0046.
- La topología del pipeline es configurable para experimentación.
- El patrón de herramientas evita prompts excesivamente largos.
- `pydantic_graph` proporciona transiciones tipadas, visualización Mermaid
  y persistencia de estado sin código adicional.
- Diseño neutral respecto a plataforma: el backend LMS es intercambiable.

### Negativas

- Múltiples llamadas LLM por ejecución del pipeline (mayor latencia y
  coste). Mitigación: el clasificador retorna temprano cuando no se
  necesita intervención (caso más frecuente).
- Superficie de testing más amplia: cada nodo y cada transición requiere
  pruebas.
- El orquestador puede seleccionar un rol incorrecto. Mitigación: nodo
  evaluador con reintento.

### Cuestiones abiertas

- ¿Qué umbral de confianza debe usar el evaluador LLM para considerar una
  respuesta no viable?
- ¿Cuándo se activa el agente escritor por defecto? ¿Solo cuando hay
  contexto de curso disponible?
- ¿Cómo se evalúa la calidad de facilitación del pipeline completo frente
  a configuraciones alternativas?
- ¿Es necesario un mecanismo de feedback del orquestador al rol cuando se
  produce un reintento (e.g., "el rol social no fue efectivo, intenta
  intelectual")?
