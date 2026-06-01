# ADR 0038: LogFuse como referencia de observabilidad del pipeline

**Estado**: Aceptado
**Fecha**: 2026-06-01
**Depende de**: ADR 0037 (diseño visual del dashboard)

## Descripcion

El dashboard necesitaba una forma de exponer datos de ejecucion del pipeline que fuera util para el investigador sin convertirse en un visor de trazas completo. El PoC genera datos en dos capas: salidas estructuradas (clasificacion, decision de intervencion, respuesta generada) y mensajes brutos de los agentes (el historial de llamadas al LLM con sus respuestas).

LogFuse es una herramienta de observabilidad para pipelines de IA que almacena trazas de ejecucion a nivel de mensaje. Durante el diseño inicial del dashboard en Figma Make, el primer prompt de generacion incluyó explicitamente LogFuse como referencia: "Dashboard for reviewing pydantic AI pipeline output which will be connected to logfuse for more detailed pipeline run data (something like see source which will redirect to logfuse)". Ese modelo de "ver fuente" inspiro las decisiones de diseño de observabilidad que se documentan aqui.

## Decision

### 1. Patron de observabilidad en dos niveles

El dashboard adopta un patron de observabilidad de dos niveles:

- **Nivel 1 (dashboard)**: salidas estructuradas del pipeline. Clasificacion, decision de intervencion, rol seleccionado, texto de respuesta, metricas de confianza, razonamiento en texto. Lo suficiente para evaluar la calidad de la decision sin necesidad de inspeccionar el trace completo.
- **Nivel 2 (LogFuse u herramienta externa)**: traza bruta de ejecucion. Mensajes completos al LLM, respuestas raw, llamadas a herramientas, latencias por llamada. Para diagnostico de fallos o analisis de comportamiento del modelo a nivel de token.

Este patron evita que el dashboard tenga que implementar un visor de trazas completo, que esta fuera del alcance del PoC.

### 2. `logfuse_url` como campo de primera clase

El campo `logfuse_url` en `ThreadResult` no es metadata opcional sino un punto de integracion diseñado explicitamente. Cada resultado de hilo puede llevar una URL a su traza en LogFuse. El enlace se muestra en la fila del hilo en `ModelDetail` como boton externo.

La URL se persiste en el artefacto JSON del run, de modo que ejecuciones pasadas siguen teniendo acceso a su traza mientras LogFuse la conserve.

### 3. Mensajes de agente inline como nivel intermedio

Con la incorporacion de `pipeline_messages` (PR #35), el dashboard añade un nivel intermedio entre las salidas estructuradas y la traza completa en LogFuse: el historial de mensajes de cada agente del pipeline (`classification`, `intervention`, `orchestrator`, `role`), disponible directamente en la vista de detalle de hilo.

Esto cubre el caso de uso mas frecuente de "ver que le dije al modelo y que respondio" sin salir del dashboard. LogFuse sigue siendo la referencia para casos de diagnostico mas profundo (latencias, tokens, fallos parciales).

### 4. Cuadricula de acceso a LogFuse como patron de navegacion (descartado)

El codigo generado por Figma Make incluia una cuadricula de acceso a LogFuse: una matriz modelos x hilos donde cada celda era un enlace directo a la traza correspondiente. Este patron fue descartado durante la simplificacion del dashboard porque añadia una vista completa adicional para un flujo de uso poco frecuente. Los enlaces individuales en cada fila de hilo cubren el mismo acceso con menor complejidad visual.

## Alternativas consideradas

### Construir un visor de trazas completo en el dashboard

Descartado: duplicaria funcionalidad que LogFuse ya provee, con mayor coste de implementacion y mantenimiento. El dashboard es una herramienta de inspeccion de resultados, no una herramienta de observabilidad general.

### No integrar LogFuse

Descartado: sin acceso a la traza bruta, los fallos del pipeline que no producen error estructurado (por ejemplo, respuestas parcialmente invalidas o comportamientos inesperados de herramientas) son opacos. El enlace externo es la via de escape cuando el nivel 1 no es suficiente.

### Mostrar todos los mensajes brutos directamente en el nivel 1

Descartado inicialmente: los mensajes brutos son voluminosos y relevantes solo para diagnostico, no para evaluacion de calidad de la decision. Se incorporaron finalmente como nivel intermedio colapsable, equilibrando accesibilidad y ruido visual.

## Consecuencias

### Positivas

- El dashboard permanece enfocado en la evaluacion de calidad sin sobrecargar la interfaz con datos de traza.
- Los fallos y comportamientos inesperados del pipeline tienen una via de diagnostico explicita (el enlace a LogFuse).
- El nivel intermedio de mensajes inline reduce la necesidad de salir del dashboard para los casos de uso mas comunes de inspeccion.

### Negativas

- La disponibilidad del nivel 2 depende de que LogFuse tenga la traza almacenada. Si la integracion con LogFuse no esta configurada o la traza expiro, el enlace no es util.
- Los mensajes brutos inline aumentan el tamaño de los artefactos JSON del run cuando todos los agentes los capturan.

### Neutrales

- Esta decision no afecta la semantica del pipeline ni los contratos de API backend.
- LogFuse no es un requisito del PoC: el dashboard funciona sin el enlace. Es un punto de integracion opcional.

## Alcance y fuera de alcance

Incluido en esta decision:

- Patron de dos niveles de observabilidad (dashboard + herramienta externa).
- `logfuse_url` como campo de primera clase en `ThreadResult`.
- Mensajes de agente inline por etapa del pipeline como nivel intermedio.

Fuera de alcance en esta fase:

- Integracion directa con la API de LogFuse (consulta o autenticacion desde el dashboard).
- Visualizacion de latencias o conteo de tokens por llamada.
- Retencion o caducidad de trazas en LogFuse.
