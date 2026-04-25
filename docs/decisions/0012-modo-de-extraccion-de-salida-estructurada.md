# ADR 0012: Modo de extracción de salida estructurada

**Estado**: Aceptado
**Fecha**: 2026-04-25
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0009 (Estructura de prompts)

## Descripción

Los agentes del pipeline producen salida estructurada (tipos Pydantic como
`ClassificationResult`, `InterventionDecision`, `RoleSelection`,
`FacilitationResponse`). pydantic-ai ofrece dos mecanismos para extraer esa
salida del modelo:

- **Modo tool-calling**: el framework define una herramienta `final_result` con
  el esquema JSON del tipo de salida. El modelo debe invocar esa herramienta
  para entregar su respuesta. pydantic-ai extrae los argumentos de la llamada.
- **Modo PromptedOutput**: no se define ninguna herramienta de extracción. El
  framework informa al modelo de que debe devolver JSON plano y valida el texto
  resultante contra el tipo Pydantic. El esquema se transmite al modelo mediante
  el system prompt o la descripción de tarea.

La decisión de cuál usar afecta la compatibilidad con modelos locales, que es
un objetivo explícito del sistema (ADR 0002).

## Evidencia experimental

Dos experimentos con los mismos seis hilos de prueba, antes y después de
introducir `PromptedOutput`:

### Sin PromptedOutput (tool-calling)

| Modelo | Éxito / Total | Causa de fallo |
|--------|:---:|---|
| `ollama:qwen2.5:14b` | 2 / 6 | `invalid message content type: <nil>` en respuesta de herramienta |
| `ollama:phi4` | 0 / 6 | `does not support tools` |

### Con PromptedOutput

| Modelo | Éxito / Total | Nota |
|--------|:---:|---|
| `ollama:qwen2.5:14b` | 6 / 6 | Sin errores de protocolo |
| `ollama:phi4` | 5 / 6 | Falla solo cuando la intervención requiere llegar al nodo de rol |
| `ollama:mistral` | 0 / 6 | Modelo demasiado pequeño: devuelve el esquema en lugar de una instancia |
| `ollama:llama3.2` | 0 / 6 | Mismo patrón que mistral |
| `ollama:gemma3:4b` | 0 / 6 | Mismo patrón que mistral |

El caso phi4 merece aclaración: phi4 no soporta herramientas en absoluto. Con
`PromptedOutput`, los nodos de clasificación, intervención y selección de rol
no envían herramientas y phi4 los completa. Falla únicamente en el nodo de
agente de rol, que usa herramientas funcionales reales (`retrieve_techniques`,
`get_thread_history`) independientes del modo de extracción de salida. Esas
herramientas no son negociables: son parte del comportamiento del agente, no
del protocolo de extracción.

### Qué envía el framework en cada modo

El comando `render-prompt` (`uv run --env-file .env.local render-prompt`)
captura la petición real antes de enviarla al modelo:

- **Tool-calling**: el mensaje incluye la definición de `final_result` con el
  esquema JSON completo; `allow_text_output: False`. El modelo debe responder
  con una invocación de herramienta en formato estructurado.
- **PromptedOutput**: no hay herramientas de salida (`output_tools: none`);
  `allow_text_output: True`. El modelo devuelve texto plano que el framework
  parsea y valida.

## Decisión

Usar `PromptedOutput` para la extracción de salida estructurada en todos los
agentes del pipeline (`ClassificationAgent`, `InterventionAgent`,
`OrchestratorAgent`, `RoleAgent`).

```python
from pydantic_ai.output import PromptedOutput

self.agent = Agent(
    model,
    output_type=PromptedOutput(OutputType),
    retries=3,
)
```

Esta decisión afecta exclusivamente al mecanismo de extracción de salida. Las
herramientas funcionales de los agentes de rol (`retrieve_techniques`,
`get_thread_history`) no cambian.

## Consecuencias

### Positivas

- Los modelos que no implementan el protocolo de herramientas (phi4 y
  equivalentes) pueden participar en los nodos sin herramientas funcionales.
- Desaparece la clase de errores `invalid message content type: <nil>` de
  Ollama, que ocurría cuando la respuesta de herramienta tenía contenido nulo.
- El sistema es compatible con cualquier modelo que produzca JSON válido como
  texto, sin depender de que el proveedor implemente la API de herramientas.

### Negativas

- Los modelos muy pequeños (< ~14B parámetros en los experimentos) tienden a
  devolver el esquema JSON en lugar de una instancia válida. El mecanismo de
  reintentos de pydantic-ai absorbe algunos casos, pero no todos. El umbral de
  tamaño no es un invariante: depende del modelo y del esquema.
- El modo tool-calling tiene una ventaja de fiabilidad cuando el modelo lo
  soporta bien: el formato estructurado de la invocación reduce la ambigüedad
  de parseo. Con `PromptedOutput`, si el modelo produce JSON malformado, el
  sistema reintenta, pero la señal de error es menos informativa.

### Estratificación de capacidad resultante

Los experimentos revelan tres niveles de compatibilidad:

1. **Compatibilidad completa**: modelos que soportan herramientas funcionales y
   producen JSON estructurado (>= 14B en los experimentos; ej. qwen2.5:14b).
   Pueden ejecutar el pipeline completo incluyendo nodos con herramientas reales.
2. **Compatibilidad parcial**: modelos sin soporte de herramientas pero capaces
   de producir JSON válido (ej. phi4). Ejecutan los nodos de clasificación e
   intervención; fallan si la intervención requiere el nodo de rol.
3. **Sin compatibilidad funcional**: modelos demasiado pequeños para seguir el
   esquema de salida. Producen el esquema como respuesta o JSON malformado.

Esta estratificación es observable y documentable en los experimentos; no
requiere decisiones de diseño adicionales.

### Impacto en tests

`TestModel` de pydantic-ai usa por defecto el modo tool-calling. Con
`PromptedOutput`, todos los `TestModel()` en los tests de cableado deben
recibir `custom_output_text` con JSON válido del tipo de salida esperado:

```python
with agent.agent.override(
    model=TestModel(custom_output_text=ClassificationResult(...).model_dump_json())
):
    result = await agent.run(thread, deps)
```

### Cuestiones abiertas

- ¿El umbral de ~14B es estable con modelos de familias distintas o depende de
  la familia y el fine-tuning de seguimiento de instrucciones?
- ¿Conviene añadir una validación de capacidad al arranque del sistema que
  advierte si el modelo configurado no produce JSON válido con el esquema de
  clasificación?
