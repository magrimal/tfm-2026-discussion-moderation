# ADR 0030: Perfiles de configuración por modelo

**Estado**: Aceptado
**Fecha**: 2026-05-04
**Depende de**: ADR 0012 (modo de extracción), ADR 0021 (registro autodeclarativo)

## Descripción

El sistema usa un registro de proveedores autodeclarativo (ADR 0021) para
construir modelos pydantic-ai a partir de cadenas prefijadas como
`ollama:qwen2.5:14b`. Tras el primer ciclo de evaluación con 10 modelos locales,
se hace evidente que la configuración a nivel de proveedor es insuficiente: modelos
del mismo proveedor tienen capacidades distintas que determinan qué modo de
extracción funciona y si el nodo de rol puede ejecutarse.

La decisión anterior (ADR 0012, tercera revisión) introdujo `uses_prompted_output`
como bandera booleana a nivel de proveedor. Esto resulta ser demasiado grueso:
`deepseek-r1:14b` pasa de 5/6 a 0/6 si se aplica `PromptedOutput` globalmente a
todos los modelos Ollama, porque ese modelo depende específicamente del protocolo
de herramientas para generar salida estructurada válida.

## Decisión

Se introduce `ModelProfile`, un dataclass que representa las capacidades de un
modelo concreto. Cada proveedor mantiene un diccionario `MODEL_PROFILES` con
entradas por nombre de modelo, y un perfil por defecto `_default_profile` para
modelos sin entrada específica.

### Estructura

```python
@dataclass
class ModelProfile:
    extraction_mode: Literal["tool", "prompted"] = "tool"
    has_functional_tools: bool = True
```

`extraction_mode` determina si pydantic-ai usa el protocolo de herramientas
(`"tool"`) o extracción por prompt de texto (`"prompted"`) para la salida
estructurada. `has_functional_tools` es `False` para modelos que rechazan
explícitamente el uso de herramientas, lo que implica que el nodo de rol siempre
fallará para esos modelos.

### Orden de resolución

`ModelProvider.profile_for(model_str)` resuelve el perfil en este orden:

1. Entrada en `provider_cls.MODEL_PROFILES[model_name]` (perfil específico)
2. `provider_cls._default_profile` (perfil por defecto del proveedor)
3. `ModelProfile()` (perfil base: ToolOutput, has_functional_tools=True)

`AgentMixin.resolve_output_type(model_str, base_type, overrides)` añade un
nivel adicional antes de consultar el registro estático:

0. Entrada en `overrides[model_name]` — variable de entorno en tiempo de ejecución

Esto permite cambiar el modo de extracción de un modelo sin modificar el código,
útil tras observar un fallo en un run de evaluación.

### Perfiles actuales de Ollama

Los perfiles se basan en los resultados del run de 10 modelos locales
(2026-04-26). El perfil por defecto de `OllamaModelProvider` es ToolOutput:
los modelos sin entrada específica usan el protocolo de herramientas.

| Modelo | extraction_mode | has_functional_tools | Justificación |
|---|---|---|---|
| `qwen2.5:14b` | tool | True | 6/6 con ToolOutput; también funciona con PromptedOutput |
| `llama3.1:8b` | tool | True | 6/6 con ToolOutput; estable en ambos modos |
| `deepseek-r1:14b` | tool | True | 5/6 con ToolOutput; 0/6 con PromptedOutput |
| `mistral-nemo:12b` | prompted | True | 4/6 con ToolOutput (schema-echo); 6/6 con PromptedOutput |
| `phi4` | prompted | False | Sin soporte de herramientas funcionales; falla en nodo de rol |
| `gemma2:9b` | prompted | False | Sin soporte de herramientas funcionales; falla en nodo de rol |

Modelos no incluidos en esta tabla (no evaluados) usan el perfil por defecto
del proveedor (ToolOutput, has_functional_tools=True). Tras evaluar un modelo
nuevo, se añade su entrada aquí.

### Override en tiempo de ejecución

`Settings.model_extraction_overrides` es un dict opcional (vacío por defecto)
que permite cambiar el modo de extracción sin modificar el código:

```
# .env.local
FACILITATION_MODEL_EXTRACTION_OVERRIDES='{"phi4": "tool", "mymodel:7b": "prompted"}'
```

Las claves son nombres de modelo sin el prefijo de proveedor. Este mecanismo
tiene prioridad sobre el registro estático.

## Consecuencias

### Positivas

- Los fallos de extracción son ahora atribuibles a un modelo concreto, no al
  proveedor completo. El perfil es la fuente de verdad sobre las capacidades
  observadas de cada modelo.
- Añadir un nuevo modelo evaluado requiere una sola línea en `MODEL_PROFILES`.
  No hay otros cambios.
- El override por variable de entorno permite ajustar el comportamiento entre
  runs de evaluación sin necesidad de commit.
- `has_functional_tools=False` documenta explícitamente qué modelos no pueden
  completar el nodo de rol, lo que permite filtrarlos en el runner de evaluación
  si se desea.

### Negativas

- Los perfiles son conocimiento estático basado en evaluaciones pasadas. Un
  modelo actualizado en Ollama puede cambiar de comportamiento sin que el
  perfil se actualice. Los perfiles no tienen fecha de validez.
- El override por variable de entorno acepta cualquier cadena como valor de
  `extraction_mode`; un valor no reconocido (ni `"tool"` ni `"prompted"`)
  se trata silenciosamente como ToolOutput.
- `has_functional_tools` es informacional por ahora. El runner de evaluación
  no lo usa para filtrar automáticamente; esa lógica es una cuestión abierta.

### Cuestiones abiertas

- ¿Debe el runner de evaluación leer `has_functional_tools` del perfil y omitir
  automáticamente los modelos que no completarán el pipeline completo?
- ¿Deben los perfiles incluir un campo `last_verified` para detectar entradas
  obsoletas tras actualizaciones de modelos en Ollama?
- ¿El campo `extraction_mode` del override debe validarse estrictamente
  (`"tool"` | `"prompted"`) con un error explícito para valores desconocidos?

## Referencias

- ADR 0012: historial de decisiones sobre modos de extracción; documentación
  del bug de null-content en Ollama y la estratificación de modelos por nivel
  de capacidad.
- ADR 0021: patrón de registro autodeclarativo que este ADR extiende al nivel
  de modelo.
