# DDA-0039: Estrategia de despliegue en servidor universitario

**Estado**: Aceptado
**Fecha**: 2026-06-02
**Depende de**: ADR 0033 (desarrollo local con Makefile y Procfile), ADR 0035 (configuración en tiempo de despliegue)

## Contexto

El repositorio necesita un mecanismo de despliegue real sobre el servidor
universitario `idril.fdi.ucm.es`, que aloja el proyecto `2526-moderacion`
con acceso restringido a VPN UCM.

La primera aproximación explorada fue servir el dashboard desde el propio
proceso FastAPI como archivos estáticos (`StaticFiles` de Starlette). Esto
generó un conflicto inmediato de espacio de nombres: React Router y FastAPI
comparten el mismo servidor, y rutas como `/runs` son a la vez un endpoint
REST (`GET /runs` devuelve JSON) y una ruta de navegación de la SPA (debe
devolver `index.html`). El intento de resolver el conflicto con un prefijo
`/api` y una ruta catch-all resultó en lógica antinatural para un framework
de API.

El servidor universitario ya tiene nginx configurado con la separación exacta
que se intentaba construir a mano:

- Los archivos en `/home/2526-moderacion/public_html/` se sirven en
  `https://idril.fdi.ucm.es/2526-moderacion/`.
- Las peticiones a rutas que empiezan por `api/` se reenvían al puerto 8080
  del contenedor, preservando el prefijo.

Para servicios persistentes, la infraestructura del servidor expone
`systemctl --user` bajo el usuario del proyecto (`2526-moderacion`).

## Decisión

Decidimos desplegar el dashboard como archivos estáticos en
`/home/2526-moderacion/public_html/` (servidos por el nginx del servidor) y
ejecutar la API FastAPI en el puerto 8080 como servicio systemd de usuario,
con todas las rutas bajo el prefijo `/api`.

## Consecuencias

### Positivas

- Separación limpia entre servidor de archivos estáticos (nginx) y API
  (FastAPI): cada componente hace lo que sabe hacer.
- No hay conflictos de espacio de nombres entre React Router y los endpoints
  REST, porque nginx filtra el tráfico antes de que llegue a uvicorn.
- `main.py` queda sin lógica de archivos estáticos; define únicamente rutas
  de API.
- El servicio se reinicia automáticamente tras un fallo o reinicio del
  servidor gracias a `systemctl --user enable`.
- `make server-deploy` construye el dashboard con las URLs correctas y lo
  copia al servidor en un único paso.

### Negativas

- El despliegue depende de la infraestructura de `idril.fdi.ucm.es`, gestionada
  por los supervisores del proyecto.
- El dashboard debe construirse localmente y copiarse al servidor mediante
  `rsync`; no se construye en el servidor.
- El prefijo `/api` en el router FastAPI asume que nginx reenvía la petición
  preservando ese segmento de ruta, lo que no está documentado explícitamente
  en la configuración nginx del servidor.
- El redespliegue de la API (reinicio del servicio systemd) y el del dashboard
  (nueva copia de archivos) son operaciones independientes.

## Alternativas consideradas

- **Proceso único: FastAPI sirviendo StaticFiles**: descartado porque genera
  conflictos de espacio de nombres entre React Router y los endpoints REST, y
  requiere una ruta catch-all antinatural en un framework de API.
- **Dos contenedores con compose (nginx + FastAPI)**: descartado porque el
  servidor ya proporciona nginx; añadir compose duplicaría esa capa de
  infraestructura sin beneficio.
- **Dashboard bajo una sub-ruta diferente (`/dashboard/*`)**: descartado
  porque cambia la URL pública del frontend sin resolver el problema
  subyacente.

## Referencias

- `Makefile` (targets `server-deploy`, `dev-up`)
- `Procfile.dev`
- `docs/deployment/idril.md`
- `discussion_moderation/rest_api/main.py`
- `dashboard/vite.config.ts`
