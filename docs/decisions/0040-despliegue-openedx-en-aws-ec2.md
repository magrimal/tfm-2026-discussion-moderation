# DDA-0040: Despliegue de Open edX en AWS EC2 con imágenes Docker preconstruidas y DNS en Route 53

## Estado

Propuesto

## Contexto

El TFM requiere una instancia de Open edX accesible públicamente por internet. El motivo principal es la integración con el servicio de facilitación desplegado en el servidor del profesor (idril.fdi.ucm.es): ese servicio recibe llamadas desde el plugin `forum_intervention` instalado en Open edX, y necesita poder responder a una URL pública para cerrar el ciclo de intervención. Un entorno local no es suficiente.

### La plataforma

Se usa Tutor (v21.0.4, release Ulmo) como herramienta de despliegue de Open edX. Tutor orquesta todos los servicios de la plataforma mediante Docker Compose: LMS (Django), Studio (CMS), foros (cs_comments_service), MFEs (React), base de datos MySQL, MongoDB y el proxy inverso Caddy (con terminación TLS automática vía Let's Encrypt). Los plugins se instalan como paquetes Python y pueden inyectar configuración, patches de settings y dependencias adicionales en la imagen Docker de Open edX durante el build.

El plugin `forum_intervention` añade un componente Django al LMS que intercepta las discusiones del foro, las envía al servicio de facilitación de idril y aplica las intervenciones generadas. Se instala en la imagen de Open edX desde el repositorio de GitHub durante el build, vía el patch `openedx-dockerfile-post-python-requirements` de Tutor.

La instalación local contiene datos reales de prueba: cursos, usuarios, discusiones de foro. Se migran a EC2 mediante dump/restore de MySQL y MongoDB para preservar el estado.

### Restricciones encontradas

**Construcción de imágenes en EC2:** la instancia t2.medium (2 vCPU, 4 GB RAM) se queda sin memoria construyendo la imagen de Open edX. Las imágenes (`openedx` y `mfe`) se construyen localmente con BuildKit con paralelismo limitado (`max-parallelism = 2` en `buildkitd.toml`) y se publican en repositorios públicos de ECR. EC2 descarga las imágenes ya construidas en lugar de generarlas.

**Sobrescritura de `FACILITATION_SERVICE_URL`:** el plugin `forum_intervention` tiene la URL del servicio de facilitación apuntando a `host.docker.internal` (solo válido en local). En EC2 debe apuntar a `https://idril.fdi.ucm.es/2526-moderacion/api`. En lugar de modificar el código fuente del plugin, se creó `facilitation_override.py`, un plugin Tutor separado que añade un patch de `openedx-common-settings` después del plugin principal. Django ejecuta los settings de arriba a abajo y la última asignación gana, así que el override reemplaza la URL sin tocar el plugin original.

**Plugins inline dispersos:** los plugins `dev_jwt_long_expiry` y `facilitation_override` vivían solo en la máquina local. Se versionaron en el repositorio del TFM bajo `integrations/openedx/tutor/inline_plugins/`. En EC2 se configura `TUTOR_PLUGINS_ROOT` apuntando a ese directorio tras el clone, eliminando la necesidad de copiar archivos manualmente.

**DNS:** el dominio `mgmdy.xyz` se registró en Namecheap y se delegó a Route 53 configurando los nameservers del hosted zone en Namecheap. Se usan dos registros wildcard:
- `*.openedx.mgmdy.xyz` → IP de EC2 (cubre LMS y MFEs)
- `*.lms.openedx.mgmdy.xyz` → IP de EC2 (cubre Studio)

Los hostnames definitivos:
- LMS: `lms.openedx.mgmdy.xyz`
- Studio: `studio.lms.openedx.mgmdy.xyz`
- MFEs: `apps.openedx.mgmdy.xyz`

**Migración de datos:** MySQL y MongoDB se migran con dump/restore (`mysqldump --all-databases`, `mongodump --archive`) y se restauran en EC2 antes de ejecutar `tutor local launch`.

**Stack de plugins habilitados:**
- Pip-distributed: `tutor-forum`, `tutor-mfe`, `tutor-indigo`
- Pip-editable desde el repo: `forum_intervention_tutor_plugin`
- Inline via `TUTOR_PLUGINS_ROOT`: `dev_jwt_long_expiry`, `facilitation_override`

**Duración del JWT emitido por `client_credentials` (2026-07-19):** el
cliente OAuth2 `facilitation-service`, usado por idril y EC2 para
autenticarse contra el LMS, emitía tokens con expiración de 1 hora (el
valor por defecto de Open edX) en vez de la extendida por
`dev_jwt_long_expiry`, porque `TUTOR_PLUGINS_ROOT` no estaba exportado
en la sesión que corrió `tutor config save` — el gotcha ya descrito
arriba. El docstring original del plugin decía "LOCAL DEVELOPMENT ONLY.
Do not enable in production", pero el plugin ya forma parte del stack
habilitado en EC2 según esta misma ADR: se decidió resolver la
contradicción manteniendo el plugin (el token conlleva scope
`administrator`/`superuser`, y esta instancia no tiene alumnado real,
solo datos de prueba del TFM) pero reduciendo la duración de un año a
**un día** (86400 s), en vez de mantener el valor original de un año.
Un día acota la ventana de exposición de un token filtrado sin obligar
a regenerar el token en cada despliegue a idril/EC2.

**Dos causas independientes, ambas resueltas el mismo día (2026-07-19):**

1. `JWT_AUTH["JWT_EXPIRATION"]` y `OAUTH2_PROVIDER["ACCESS_TOKEN_EXPIRE_SECONDS"]`
   (lo que el plugin parcheaba originalmente) no son la settings que
   controla la expiración de un JWT emitido vía `client_credentials` +
   `token_type=jwt`. Leyendo directamente
   `openedx/core/djangoapps/oauth_dispatch/jwt.py` dentro del contenedor:
   `_get_jwt_access_token_expire_seconds()` lee una setting de nivel
   superior, `JWT_ACCESS_TOKEN_EXPIRE_SECONDS` (default `60*60`),
   deliberadamente separada porque los JWT no son revocables. El plugin
   ahora también fija esta tercera variable; es la única de las tres
   que realmente afecta a `LMS_JWT_AUTHENTICATION_TOKEN`.
2. Los contenedores en ejecución se crearon originalmente bajo la raíz
   de configuración de Tutor de `root` (`/root/.local/share/tutor`), no
   la de `ubuntu`. `docker compose restart` no recrea los mounts, así
   que guardar configuración con el `tutor` de `ubuntu` (que opera
   sobre `/home/ubuntu/.local/share/tutor`) nunca llegaba al contenedor
   real — confirmado con `docker inspect` sobre los bind mounts del
   contenedor `lms`. La solución: todos los comandos `tutor` en
   `integrations/openedx/Makefile` corren vía `sudo` (que resuelve
   `$HOME` a `/root`), apuntando así a la raíz de configuración que
   realmente sirve el contenedor.

Verificado end-to-end: `curl .../oauth2/access_token ... token_type=jwt`
devuelve `"expires_in": 86400`.

## Decisión

Decidimos desplegar Open edX en una instancia EC2 (t2.medium, Ubuntu 22.04, 30 GB EBS), construyendo las imágenes Docker localmente y publicándolas en ECR público, con DNS gestionado en Route 53 mediante registros wildcard, la URL del servicio de facilitación sobrescrita por un plugin Tutor separado, y los plugins inline del TFM versionados en el repositorio y cargados vía `TUTOR_PLUGINS_ROOT`.

## Consecuencias

### Positivas

- La plataforma es accesible desde internet con HTTPS real (Caddy + Let's Encrypt), lo que permite la comunicación bidireccional con idril.fdi.ucm.es.
- Los plugins inline quedan versionados junto al resto del código del TFM; el bootstrap de EC2 se reduce a un clone y configurar `TUTOR_PLUGINS_ROOT`.
- La URL del servicio de facilitación se sobrescribe sin modificar el plugin fuente, permitiendo actualizar el plugin sin perder la configuración de despliegue.
- Los registros wildcard cubren cualquier subdominio nuevo sin configuración adicional de DNS.
- ECR público no requiere autenticación para pull, simplificando el despliegue en EC2.

### Negativas

- Cada cambio en la imagen de Open edX requiere reconstruir localmente y hacer push a ECR antes de que EC2 lo recoja.
- Coste mensual de AWS (EC2 + EBS + Route 53 hosted zone) y del dominio.
- t2.medium tiene recursos limitados; no es adecuado para carga real de producción.
- El clone del repositorio privado en EC2 requiere gestionar claves SSH con la identidad correcta.
- `TUTOR_PLUGINS_ROOT` debe estar en el entorno antes de cualquier comando tutor; si no se exporta en la sesión, Tutor no carga los plugins inline.

## Alternativas Consideradas

- **ngrok (nivel gratuito)**: descartado porque solo enruta un dominio, insuficiente para LMS + Studio + MFEs simultáneamente.
- **Construir imágenes en EC2**: descartado porque la instancia t2.medium se queda sin memoria durante el build de Open edX.
- **ECR privado**: descartado porque requiere usuario IAM y gestión de credenciales en EC2; ECR público es suficiente para este caso de uso.
- **DuckDNS**: descartado porque no soporta subdominios wildcard de forma nativa, obligando a registrar cada hostname por separado.
- **Modificar `FACILITATION_SERVICE_URL` directamente en el plugin fuente**: descartado porque mezcla configuración de despliegue con código del plugin, dificultando actualizaciones futuras.
