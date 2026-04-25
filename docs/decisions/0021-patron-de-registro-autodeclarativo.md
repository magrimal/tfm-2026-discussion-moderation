# ADR 0021: Patrón de registro autodeclarativo para proveedores y backends

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0007 (Historial de
intervenciones), ADR 0010 (Puntos de integración)

## Descripción

El sistema necesita soporte para múltiples proveedores de LLM (Anthropic, Ollama,
OpenRouter) y múltiples backends de LMS (Open edX, stub para desarrollo). Añadir
un nuevo proveedor o backend no debe requerir modificar ningún fichero existente
más allá del nuevo módulo: el acoplamiento explícito entre la implementación y el
lugar donde se usa es frágil y dificulta la extensión.

Esta decisión documenta el mecanismo mediante el cual los proveedores y backends
se registran y se resuelven sin un diccionario central de fábrica.

## Decisión

Los tres puntos de extensión del sistema usan el mismo patrón: una clase base con
`__init_subclass__` que registra cada subclase en un diccionario de clase interno
(`_registry`) en el momento de su definición.

### ModelProvider (`providers.py`)

```python
class ModelProvider:
    _registry: ClassVar[dict[str, type[ModelProvider]]] = {}

    def __init_subclass__(cls, prefix: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if prefix:
            ModelProvider._registry[prefix] = cls

    @classmethod
    def for_model(cls, model_str: str, api_key: str) -> Model | str:
        prefix, model_name = model_str.split(":", 1)
        provider_cls = cls._registry.get(prefix)
        if provider_cls is None:
            return model_str
        return provider_cls().build(model_name, api_key)
```

Las subclases registradas actualmente:

| Subclase | Clave | Uso |
|---|---|---|
| `AnthropicModelProvider` | `"anthropic"` | API Anthropic |
| `OllamaModelProvider` | `"ollama"` | Modelos locales vía Ollama |
| `OpenRouterModelProvider` | `"openrouter"` | OpenRouter (reenvío a APIs cloud) |

### LMSBackend (`tools/protocols.py`)

```python
class LMSBackend:
    _registry: ClassVar[dict[str, type[LMSBackend]]] = {}

    def __init_subclass__(cls, key: str = "", **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if key:
            LMSBackend._registry[key] = cls
```

Las subclases registradas:

| Subclase | Clave | Uso |
|---|---|---|
| `OpenEdXBackend` | `"openedx"` | Integración con Open edX vía API REST |
| `StubLMSBackend` | `"stub"` | Hilos en memoria para desarrollo y evaluación |

### ThreadHistoryStore (`tools/history.py`)

El mismo patrón, con `key=` como argumento de registro. Subclases registradas:
`InMemoryThreadStore` (`"memory"`) y `SQLiteThreadStore` (`"sqlite"`).

### Resolución en tiempo de ejecución

Los tres puntos de extensión se configuran desde `Settings` (ADR 0019) y se
resuelven al construir el grafo:

```
FACILITATION_LLM_MODEL=anthropic:claude-sonnet-4-20250514
FACILITATION_LMS_BACKEND=openedx
FACILITATION_HISTORY_STORE=sqlite
```

El prefijo o clave identifica la subclase sin ningún import explícito en el
código que construye el grafo. La subclase está registrada en el momento en
que su módulo es importado: los imports de `providers.py`, `tools/protocols.py`,
`tools/history.py` son suficientes para que todos los registros estén disponibles.

### Por qué `__init_subclass__` en lugar de un diccionario explícito

La alternativa directa es un diccionario de fábrica definido en el mismo módulo
que la clase base:

```python
PROVIDERS: dict[str, type[ModelProvider]] = {
    "anthropic": AnthropicModelProvider,
    "ollama": OllamaModelProvider,
}
```

Este enfoque requiere modificar el diccionario central cada vez que se añade una
subclase. Con `__init_subclass__`, añadir un proveedor es una sola operación: la
definición de la subclase. El fichero central no cambia.

La alternativa de un framework de inyección de dependencias (por ejemplo,
`dependency-injector`) añade dependencias externas y complejidad de configuración
para un problema que Python resuelve con una sola línea. El patrón de registro
es más simple, más legible, y no requiere infraestructura adicional.

El patrón es coherente con el mecanismo de `entry_points` de Python (usado en
Open edX para plugins), pero no requiere la instalación de paquetes separados
ni la modificación de `pyproject.toml` para el caso de uso actual.

## Consecuencias

### Positivas

- Añadir un nuevo proveedor o backend no requiere cambios en ningún fichero
  existente: solo la definición de la subclase en un módulo nuevo.
- El mecanismo de resolución está centralizado en la clase base y no está
  duplicado en los puntos de uso.
- El patrón es uniforme en los tres puntos de extensión, lo que reduce la
  carga cognitiva al entender cualquiera de los tres.
- La afirmación de diseño neutral respecto al proveedor (ADR 0005) se implementa
  aquí: el grafo no depende de ningún proveedor concreto.

### Negativas

- El registro depende de que el módulo de la subclase sea importado antes de
  la resolución. Si un módulo no se importa (por ejemplo, porque está en un
  paquete opcional no instalado), su registro no existe y la clave falla
  silenciosamente con el fallback.
- No hay lista estática de las claves registradas disponibles: el contenido de
  `_registry` solo es visible en tiempo de ejecución, lo que dificulta la
  validación de configuración en tiempo de arranque.
- La convención `prefix=` para proveedores y `key=` para backends es una
  inconsistencia de nomenclatura que no tiene justificación funcional.

### Cuestiones abiertas

- ¿Debe el arranque del sistema validar que las claves configuradas están
  registradas antes de ejecutar el pipeline, en lugar de fallar al primer uso?
- ¿Debe existir un mecanismo de descubrimiento automático (tipo `entry_points`)
  para registrar backends de terceros sin modificar el paquete principal?
- ¿Debe unificarse el parámetro de registro (`prefix=` vs. `key=`) en los
  tres puntos de extensión?

## Alternativas consideradas

- **Diccionario de fábrica explícito**: más visible y fácil de grep, pero
  requiere modificar el fichero central al añadir cada subclase. Descartado
  por el acoplamiento que introduce.
- **Framework de inyección de dependencias**: más potente, pero añade
  dependencias externas y configuración innecesaria para el problema actual.
  Descartado.
- **`entry_points` de Python packaging**: apropiado para plugins de terceros,
  pero añade overhead de empaquetado innecesario cuando todos los backends
  están en el mismo repositorio. Puede ser relevante en una fase posterior
  si el sistema crece como plataforma.
