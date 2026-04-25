# ADR 0014: Infraestructura de evaluación experimental

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0005 (Arquitectura multi-agente), ADR 0012 (PromptedOutput)

## Descripción

Validar el pipeline requiere ejecutarlo contra múltiples modelos y escenarios
de forma reproducible y comparable. Se necesita una infraestructura que:

1. Ejecute el pipeline completo para cada combinación modelo × hilo.
2. Capture el estado completo de cada ejecución para análisis posterior.
3. Permita comparar modelos de distintas familias y proveedores.
4. Sea reproducible: el resultado de una ejecución no debe depender del estado
   de la rama de trabajo ni del entorno de desarrollo activo.

Esta decisión documenta el diseño del runner de experimentos, los tres entornos
de proveedor configurados, y los mecanismos de reproducibilidad asociados.

## Decisión

### Runner de experimentos (`eval-models`)

El comando `eval-models` ejecuta el pipeline completo para cada par
(modelo, hilo de prueba) y escribe los resultados en
`docs/experiments/results/<timestamp>[-<nombre>]/`.

Cada ejecución produce:

- Un fichero JSON por par modelo/hilo (`<modelo>__<hilo>.json`) con el
  `RunRecord` completo.
- Un fichero `summary.md` con tablas de resultados, razonamientos expandibles,
  y secciones de observaciones y conclusiones.

#### Esquema `RunRecord`

Captura el estado completo del pipeline por ejecución:

| Grupo | Campos |
|---|---|
| Clasificación | `state`, `trajectory`, `participation_balance`, `discourse_quality`, `inquiry_phase`, `classification_reasoning` |
| Intervención | `should_intervene`, `intervention_reasoning` |
| Selección de rol | `role`, `role_reasoning` |
| Respuesta | `technique`, `action_category`, `confidence`, `post_to_thread`, `response_reasoning`, `response_text` |
| Meta | `model`, `thread`, `thread_title`, `error`, `raw_response`, `duration_seconds` |

El campo `error` y `raw_response` se populan en caso de fallo, lo que permite
distinguir entre fallos de modelo (JSON malformado, timeout) y fallos de
infraestructura (rate limit, modelo no disponible).

El campo `thread_title` viaja con el registro en lugar de derivarse en el
momento de leer: garantiza que el título sea el del escenario exacto ejecutado,
independientemente de cambios posteriores en los fixtures.

#### Nomenclatura de directorios de resultados

Los directorios siguen el patrón `<timestamp-ISO>[-<EVAL_NAME>]`. La variable
`EVAL_NAME` (opcional) permite etiquetar la ejecución con el nombre del
experimento sin modificar el runner. El timestamp garantiza unicidad; la
etiqueta humana garantiza identificabilidad.

#### Reintentos ante límites de tasa

El runner implementa backoff exponencial para errores 429: espera
`10s × 2^intento`, máximo 3 intentos. Permite ejecutar contra proveedores con
límites estrictos sin fallar inmediatamente.

### Herramienta de inspección `render-prompt`

El comando `render-prompt` captura los mensajes exactos que pydantic-ai envía
al modelo para el `ClassificationAgent`, sin hacer una llamada real al LLM.
Usa `FunctionModel` de pydantic-ai junto con `ClassificationAgent.__new__` para
registrar el system prompt, el contenido de usuario, y las herramientas
(si las hay), en ambos modos: tool-calling y PromptedOutput.

Esta herramienta fue decisiva para confirmar empíricamente la diferencia entre
modos (ADR 0012): con tool-calling, el mensaje incluye la definición de
`final_result`; con PromptedOutput, no hay herramientas de salida.

### Aislamiento mediante git worktree (`eval-models-isolated`)

Las evaluaciones largas (6 modelos × 6 hilos ≈ 30+ minutos) se ejecutan en un
worktree git separado con `git worktree add --detach HEAD`. Esto permite cambiar
de rama en el checkout principal sin interrumpir el experimento en curso.

Los resultados se escriben en `docs/experiments/results/` del checkout principal
mediante un symlink creado al inicio de la ejecución. El worktree se elimina al
finalizar.

Se usa `--detach HEAD` en lugar de `git worktree add <path> <branch>` para
evitar el error `branch already checked out` cuando la rama activa en el
checkout principal es la misma que se quiere usar en el worktree.

### Tres entornos de proveedor

#### Entorno local — Ollama

Modelos ejecutados localmente via Ollama. Sin coste por llamada. Sin límites de
tasa. Adecuado para iteración rápida y validación de compatibilidad.

Configuración: `.env.local` con `LLM_API_KEY=ollama`.

Limitaciones: velocidad dependiente del hardware local (CPU/iGPU). Los modelos
grandes (>14B) son lentos en inferencia CPU. No reproduce las condiciones de
un despliegue real.

Modelos con compatibilidad completa confirmada (6/6): `qwen2.5:14b`,
`mistral-nemo:12b`, `llama3.1:8b`. Ver `docs/experiments/models.md`.

#### Entorno cloud — OpenRouter

Acceso a múltiples proveedores y familias de modelos via una única API
OpenAI-compatible. Permite comparar modelos frontier sin gestionar credenciales
por proveedor.

Configuración: `.env.openrouter` con `LLM_API_KEY=<clave-openrouter>`.
Prefijo de modelo: `openrouter:<proveedor>/<modelo>`.

Limitaciones observadas: los modelos en tier gratuito (`:free`) devuelven
cuerpo nulo (`choices: None`) cuando se supera el límite de tasa upstream en
lugar de un error HTTP estándar. Esto causa un fallo de parseo en pydantic-ai,
no un error recuperable. Los límites de tasa varían por modelo y proveedor
upstream; no son controlables desde el cliente.

#### Entorno cloud — Anthropic directo

Acceso directo a los modelos Claude via API de Anthropic. Útil para comparar
el comportamiento del pipeline con el modelo más capaz disponible, sin la
intermediación de OpenRouter.

Configuración: `.env` con `LLM_API_KEY=<clave-anthropic>` y
`FACILITATION_LLM_MODEL=anthropic:<modelo>`. Prefijo de modelo: `anthropic:`.

### Selección de modelos para evaluación

Solo se incluyen en `EVAL_MODELS` modelos con soporte de herramientas nativo.
Los modelos sin soporte de herramientas fallan en el nodo `RoleAgent` con
independencia del modo de extracción de salida (PromptedOutput no elimina la
necesidad de herramientas funcionales). Sus resultados reflejan una limitación
de infraestructura, no de calidad de la respuesta, y distorsionan la
comparación entre modelos.

## Consecuencias

### Positivas

- Los resultados son reproducibles: cada ejecución queda registrada con su
  estado completo, y el worktree garantiza que el código ejecutado es el del
  commit en HEAD.
- La comparación entre modelos es directa: todos los modelos se ejecutan
  contra los mismos hilos con el mismo pipeline.
- El runner es agnóstico al proveedor: añadir un nuevo proveedor requiere solo
  registrar un nuevo `ModelProvider` (ADR auto-registrado, ver ADR siguiente).
- `render-prompt` permite inspeccionar el pipeline sin consumir créditos de API.

### Negativas

- Los resultados de ejecuciones pasadas no se actualizan si cambia el pipeline.
  Comparar resultados de commits distintos requiere verificar que el pipeline
  era equivalente.
- El backoff exponencial no garantiza éxito con proveedores que aplican límites
  estrictos por cuota (no por ventana de tiempo). En ese caso, la única opción
  es esperar o usar un modelo distinto.
- El formato JSON + Markdown no es adecuado para análisis estadístico
  automatizado a gran escala. Para comparaciones extensas se necesitaría un
  formato tabular (CSV, Parquet).

### Cuestiones abiertas

- ¿Conviene añadir un parámetro `EVAL_CONCURRENCY` para limitar el número de
  llamadas paralelas al modelo? Actualmente todas las combinaciones se lanzan
  concurrentemente, lo que agota los límites de tasa de los proveedores
  gratuitos.
- ¿Debe el runner detectar y advertir cuando el modelo especificado no tiene
  soporte de herramientas antes de lanzar las ejecuciones?
- Los resultados de OpenRouter con tier gratuito son parcialmente no fiables
  (cuerpo nulo en lugar de error recuperable). ¿Debe el runner detectar este
  patrón específico y marcarlo como fallo de infraestructura, no de modelo?

## Referencias

- Documentación de Ollama: modelos disponibles y requisitos de hardware.
- OpenRouter: API compatible con OpenAI; límites de tasa por modelo en
  `openrouter.ai/models`.
- `docs/experiments/models.md`: tabla de compatibilidad de modelos por tier.
