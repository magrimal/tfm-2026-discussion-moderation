# DDA-0010: Punto de entrada de integración entre el foro y el pipeline

## Estado

Propuesto

## Contexto

El backend `OpenEdXBackend` implementa `get_thread()`, que llama al servicio
interno del foro (`GET /api/v2/threads/{thread_id}`) y construye un
`DiscussionThread` directamente desde el JSON de respuesta. Por otro lado,
`facilitate()` recibe un `DiscussionThread` ya ensamblado y ejecuta el
pipeline. Estas dos operaciones existen por separado: ningún componente del
sistema llama actualmente a `get_thread()`.

El playground carga hilos desde archivos JSON locales. Esto es suficiente para
pruebas aisladas, pero no permite trabajar con hilos reales del foro sin
exportarlos manualmente. El sistema necesita un punto de entrada que conecte
los datos del foro con el pipeline de manera directa.

Se identificaron tres opciones de integración:

- Extender el playground con `--thread-id` para uso en experimentos.
- Definir un endpoint REST que reciba un `thread_id` como punto de integración
  canónico desde Open edX.
- Implementar un manejador de webhook que reaccione a eventos del foro (cuando
  se crea o actualiza un hilo).

Para el propósito de este TFM, el punto de integración necesita ser
suficientemente realista para evaluar el sistema, pero no necesita cubrir
todos los escenarios de producción.

## Decisión

Decidimos exponer dos puntos de entrada: el playground acepta `--thread-id`
para experimentos contra el foro real, y un endpoint REST
`POST /api/v1/facilitate` acepta `{"thread_id": "..."}` como punto de
integración canónico desde Open edX.

## Consecuencias

### Positivas

- Los experimentos del playground pueden ejecutarse contra hilos reales sin
  exportar JSON manualmente.
- El endpoint REST es el punto natural de integración para el plugin de Open
  edX: una petición HTTP desde el LMS activa el pipeline.
- La separación entre ensamblado (`get_thread`) y procesamiento (`facilitate`)
  se mantiene limpia: cada capa tiene una responsabilidad única.

### Negativas

- Dos puntos de entrada con lógicas similares que mantener (playground y REST).
- La integración reactiva basada en webhooks o señales del foro queda fuera de
  alcance. Para este POC, el sistema responde a llamadas explícitas, no a
  eventos del foro.
- El endpoint REST requiere que el llamante sepa cuándo invocar el pipeline
  (no hay detección automática de hilos que necesiten intervención).

## Alternativas Consideradas

- **Manejador de webhook**: descartado para esta fase porque introduce
  complejidad de infraestructura (registro del webhook en Open edX, manejo de
  reintentos, idempotencia) que no aporta valor diferencial para la evaluación
  del TFM.
- **Bucle de polling**: descartado porque introduce latencia artificial y
  estado operativo continuo que no es necesario para un POC de evaluación.
