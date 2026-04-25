# ADR 0017: Técnicas de facilitación como herramienta dinámica

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0002 (Repertorio de técnicas), ADR 0005 (Arquitectura
multi-agente), ADR 0009 (Estructura de prompts), ADR 0012 (PromptedOutput)

## Descripción

Los agentes de rol necesitan acceso al repertorio de técnicas de facilitación
para seleccionar la más adecuada al contexto del hilo. Hay dos formas de
proporcionarlo: incluir el repertorio completo en el system prompt del agente
(contexto estático), o exponer una herramienta que el agente invoca en tiempo
de ejecución para recuperarlo (contexto dinámico).

La elección afecta al tamaño del contexto, a la compatibilidad con modelos
locales, y a la posibilidad de filtrar el repertorio según el estado del hilo.

## Decisión

El repertorio de técnicas se expone como herramienta pydantic-ai
(`retrieve_techniques`) en lugar de incluirse en el system prompt. El historial
de intervenciones previas sigue el mismo patrón (`get_thread_history`).

```python
@self.agent.tool_plain
def retrieve_techniques(state: str = "") -> str:
    """Retrieve the full technique repertoire."""
    techniques = get_techniques(ds)
    ...

@self.agent.tool
def get_thread_history(ctx: RunContext[RoleAgentDeps]) -> str:
    """Retrieve prior facilitation interventions for this thread."""
    ...
```

El prompt del agente de rol instruye al modelo a llamar ambas herramientas
antes de seleccionar una técnica:

```
- Call get_thread_history before selecting a technique. Do not
  repeat an intervention that produced no progress.
- Call retrieve_techniques to see what is available for the
  current discussion state before selecting a technique.
```

### Por qué herramientas en lugar de contexto estático

**Tamaño del contexto.** El repertorio completo en `knowledge_base.py` ocupa
748 líneas y define 30 técnicas con nombre, descripción, ejemplos y fuente.
Incluirlo íntegro en el system prompt de cada agente de rol añadiría ~3.000
tokens fijos a cada llamada, independientemente de si el agente los necesita.
Con modelos locales limitados en ventana de contexto, este overhead es
relevante.

**Filtrado futuro.** La firma de `retrieve_techniques` acepta un parámetro
`state` para filtrado opcional. Aunque actualmente no se usa, la arquitectura
permite añadir filtrado por estado o por rol sin cambiar el contrato entre
el agente y la herramienta. Con contexto estático, el filtrado requeriría
generar prompts distintos por rol, lo que complica el mantenimiento.

**Separación de responsabilidades.** El repertorio de técnicas es un recurso
de conocimiento, no una instrucción de comportamiento. Separarlos del system
prompt —que define persona, restricciones y tarea— sigue el principio de
ADR 0009: el contexto variable (qué técnicas existen) se inyecta en tiempo
de ejecución; las instrucciones invariantes (cómo comportarse) se definen en
el prompt.

**Historial dinámico.** `get_thread_history` no puede ser contexto estático
porque el historial cambia entre ejecuciones. La simetría de tener ambos
recursos como herramientas simplifica el modelo mental del agente.

### Coste de las llamadas a herramientas

Cada ejecución del agente de rol implica dos llamadas adicionales al modelo
(una por herramienta) antes de generar la respuesta. Esto aumenta la latencia
y el número de tokens consumidos por ejecución.

Con modelos que no soportan herramientas (PromptedOutput, ADR 0012), este
mecanismo no funciona: `retrieve_techniques` y `get_thread_history` son
herramientas funcionales reales, no herramientas de extracción de salida. Un
modelo que no invoca herramientas no recuperará el repertorio y puede
seleccionar una técnica sin información completa o generar una respuesta
genérica.

Este es el motivo por el que los modelos sin soporte de herramientas —aunque
puedan producir JSON válido en los nodos de clasificación e intervención—
fallan en el nodo de rol: no pueden llamar `retrieve_techniques` ni
`get_thread_history`.

## Consecuencias

### Positivas

- El system prompt de cada agente de rol es compacto y estable. El repertorio
  de técnicas puede crecer sin afectar al tamaño del prompt base.
- El historial de intervenciones se recupera en tiempo real, lo que garantiza
  que el agente ve el estado actual del hilo, no el estado en el momento de
  instanciar el agente.
- La arquitectura es extensible: añadir nuevas herramientas (por ejemplo,
  recuperar las contribuciones de un participante específico) no requiere
  cambios en el prompt base.
- El patrón de herramientas es coherente con la arquitectura multi-agente
  de referencia (ADR 0006, sistemas de tutoría inteligente).

### Negativas

- Requiere modelos con soporte de herramientas. Esto excluye a los modelos
  del tier parcial (phi4, gemma2:9b) del nodo de rol, independientemente de
  su capacidad para producir JSON estructurado (ADR 0012, ADR 0014).
- Añade latencia: dos llamadas adicionales por ejecución del agente de rol.
- El modelo puede elegir no llamar a `retrieve_techniques` si interpreta que
  ya conoce el repertorio. En ese caso, selecciona sin información explícita.
  El prompt lo mitiga con instrucciones directas, pero no es una garantía.
- El sesgo de ordenación del repertorio (ADR 0016) se aplica a la lista
  devuelta por la herramienta. La herramienta no mitiga el sesgo.

### Cuestiones abiertas

- ¿Debe el prompt incluir un fragmento mínimo del repertorio (las técnicas
  más relevantes para el rol) como fallback si el modelo no llama a
  `retrieve_techniques`? Aumentaría la robustez a costa de tamaño de contexto.
- ¿Cuándo debe activarse el filtrado por estado en `get_techniques`? La
  infraestructura ya lo soporta (parámetro `state`); falta definir la
  lógica de filtrado y validarla empíricamente.
- ¿Debe `get_thread_history` devolver el historial completo o solo las N
  intervenciones más recientes? ADR 0007 deja este punto abierto.

## Alternativas consideradas

- **Repertorio en el system prompt (estático)**: el contenido de
  `knowledge_base.py` se embebe en el prompt de cada agente de rol en tiempo
  de construcción. Más simple, sin coste de llamada a herramienta, pero
  infla el contexto en ~3.000 tokens por llamada y no permite filtrado
  dinámico. Descartado por el impacto en modelos locales y por dificultar
  el mantenimiento del repertorio.
- **Repertorio en el mensaje de usuario**: en lugar del system prompt, el
  contexto de la tarea incluye el repertorio en cada llamada. Misma desventaja
  de tamaño; además, contamina el turno de usuario con información que no es
  parte del hilo de discusión. Descartado.
- **Herramienta con filtrado obligatorio por rol**: `retrieve_techniques` solo
  devuelve técnicas del rol activo. Elimina el sesgo de ordenación pero impide
  la selección cross-rol. Descartado en esta fase (ver ADR 0016).

## Referencias

- Graesser, A. C., VanLehn, K., Rosé, C. P., Jordan, P. W., & Harter, D.
  (2001). Intelligent tutoring systems with conversational dialogue. *AI
  Magazine*, 22(4), 39-51.
- Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023). Judging LLM-as-a-judge
  with MT-bench and chatbot arena. *NeurIPS 2023*.
