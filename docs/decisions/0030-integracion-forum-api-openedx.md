# ADR 0030: Integración con la API del foro de Open edX

**Estado**: Aceptado
**Fecha**: 2026-05-03
**Depende de**: ADR 0026 (Separación API interna y REST)

## Descripción

El pipeline de facilitación opera sobre hilos de discusión representados como
objetos `DiscussionThread`. Hasta ahora, estos objetos se construían desde
fixtures sintéticas o desde la llamada `GET /api/v2/threads/{id}` ya
implementada en `OpenEdXBackend`. Dos capacidades críticas para el ciclo
completo de integración no estaban implementadas:

1. Postear la respuesta de facilitación de vuelta al foro una vez que el
pipeline decide intervenir.
2. Disponer de un endpoint en el servicio de facilitación al que Open edX (u
otro cliente) pueda llamar con un `thread_id` para desencadenar el ciclo
completo.

Además, existía una ambigüedad de configuración: `FACILITATION_LMS_URL`
apuntaba al LMS, pero las rutas `/api/v2/` que usa `OpenEdXBackend` pertenecen
al servicio de foro (`forum`), que en Tutor corre en un puerto separado.

## Contexto técnico: dos APIs distintas

Open edX expone dos APIs de discusión con propósitos distintos, ambas servidas
por el LMS:

**API interna del foro** (`/api/v2/`): servida por el paquete `forum`, instalado
como Django app en el LMS. No es un servicio separado: las rutas `api/v1/` y
`api/v2/` se registran en el mismo proceso que el LMS. Requiere JWT. Los
endpoints relevantes para la facilitación son:

- `GET /api/v2/threads/{thread_id}?recursive=true`: hilo completo con
  comentarios anidados en una sola llamada.
- `POST /api/v2/threads/{thread_id}/comments`: crear un comentario de nivel
  superior en un hilo.

**LMS Discussion API** (`/api/discussion/v1/`): API pública orientada al
cliente web. Devuelve una estructura diferente (con `rendered_body`,
`comment_list_url`, metadatos de usuario), no apta para ingesta directa por el
pipeline. No se usa en la integración.

Ambas APIs están disponibles en `FACILITATION_LMS_URL` (por defecto
`http://localhost:18000`). No se necesita ninguna variable separada para el
foro.

## Decisión

Usar `FACILITATION_LMS_URL` como única variable de configuración de URL. Como
el foro es una Django app instalada en el LMS, todas las llamadas (tanto a
`/api/v2/` del foro como a `/api/discussion/v1/` del LMS) van al mismo host.
No se necesita ninguna variable separada.

Se añade `post_comment(thread, body, author_id)` al protocolo `LMSBackend`. La
firma recibe el objeto `DiscussionThread` completo (no solo el ID) porque la API
del foro requiere `course_id` en el cuerpo de la petición, y el hilo ya lo
lleva. La implementación hace:

```
POST {lms_url}/api/v2/threads/{thread.id}/comments
Body: {"body": body, "course_id": thread.course_id, "author_id": author_id}
Authorization: JWT {token}
```

El ID del usuario que publica la respuesta de facilitación se configura con
`FACILITATION_BOT_USER_ID`. Si está vacío, el servicio ejecuta el pipeline pero
no postea la respuesta (modo dry-run). Esto permite correr evaluaciones contra
un Tutor real sin escribir en el foro.

## Modelo de activación: pull-on-demand

El servicio de facilitación no suscribe eventos del foro de Open edX. En cambio,
expone un endpoint `POST /facilitate/thread/{thread_id}` que cualquier cliente
puede llamar con un `thread_id`. El ciclo completo es:

1. El cliente (un script, un plugin de Open edX, o un webhook) llama al endpoint.
2. El servicio obtiene el hilo del foro (`GET /api/v2/threads/{id}`).
3. Ejecuta el pipeline (clasificación, intervención, selección de rol, respuesta).
4. Si el pipeline decide intervenir y `FACILITATION_BOT_USER_ID` está definido,
   postea el comentario (`POST /api/v2/threads/{id}/comments`).
5. Devuelve el `PipelineResult` más un campo `comment_posted: bool`.

Este modelo es compatible con una integración futura basada en eventos (el plugin
de Open edX llamaría al endpoint en respuesta a una señal Django), sin requerir
una cola de mensajes ni un event bus en esta fase.

## Consecuencias

### Positivas

- El servicio puede completar el ciclo de facilitación sin intervención manual.
- Una sola variable `FACILITATION_LMS_URL` cubre todas las llamadas al LMS y
  al foro, sin ambigüedad de configuración.
- El modo dry-run (sin `FACILITATION_BOT_USER_ID`) permite ejecutar evaluaciones
  completas contra un Tutor real sin escribir en el foro.
- El script `scripts/facilitate_course.py` permite activar el ciclo completo
  para un conjunto de hilos desde la línea de comandos, sin necesidad de un
  plugin instalado.

### Negativas

- El bot postea como un usuario existente (por defecto el administrador). No hay
  una identidad de "facilitador IA" diferenciada en el foro. Esto es aceptable
  para el prototipo pero debería resolverse antes de una integración real.
- El ciclo de activación es pull: el servicio no se entera de nuevos posts
  automáticamente. Para el TFM, el script de activación suple esta carencia;
  una integración productiva requeriría un plugin o un webhook desde Open edX.

### Cuestiones abiertas

- ¿Debería el bot crear un usuario de foro específico ("Facilitador IA") en vez
  de postear como el administrador? Requeriría llamar a `POST /api/v2/users`
  y gestionar el `author_id` resultado.
- Si en fases posteriores el sistema escala a múltiples cursos, ¿cómo se
  descubren los hilos activos sin que el activador los conozca de antemano?
  La opción más directa es `GET /api/v2/search/threads` con filtros por
  `course_id` y fecha de última actividad.

## Referencias

- `discussion_moderation/tools/openedx.py`: implementación de `OpenEdXBackend`.
- `discussion_moderation/tools/protocols.py`: protocolo `LMSBackend`.
- ADR 0026: separa la API interna Python de la capa REST HTTP.
- `scripts/seed_discussions.py`: script para poblar el foro del curso demo.
- `scripts/facilitate_course.py`: script de activación del ciclo completo.
