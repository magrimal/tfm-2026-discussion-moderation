# Despliegue en idril.fdi.ucm.es

Runbook operacional para el sistema de facilitación en el servidor universitario.

## Acceso al servidor

- **Host**: `idril.fdi.ucm.es`, puerto SSH 22 (por defecto)
- **Usuario personal**: `magrimal`
- **Directorio del proyecto**: `/home/2526-moderacion/app/`

```bash
ssh magrimal@idril.fdi.ucm.es
```

El acceso funciona sin VPN desde cualquier red.

## Arquitectura en el servidor

El nginx del servidor separa el tráfico:

- `https://idril.fdi.ucm.es/2526-moderacion/` sirve los archivos estáticos de `/home/2526-moderacion/public_html/`
- `https://idril.fdi.ucm.es/2526-moderacion/api/*` reenvía al puerto 8080 (FastAPI via uvicorn)

La API corre como servicio systemd de usuario bajo `2526-moderacion`. El dashboard se construye en el servidor y se copia a `public_html/`.

Ollama está disponible en el servidor compartido `10.100.0.1`. La variable `OLLAMA_HOST` se configura en `.env.local`.

## Estructura en el servidor

```
/home/2526-moderacion/
  app/                        repositorio clonado
    .env.local                variables de entorno (secretos, no en git)
    history.db                historial de intervenciones (SQLite)
    scripts/
      server_setup.sh         script de configuración inicial
      server_restart.sh       script de redespliegue
  public_html/                dashboard (servido por nginx en /2526-moderacion/)
```

## Prerrequisitos (una sola vez)

### 1. Clave SSH sin contraseña

```bash
ssh-copy-id magrimal@idril.fdi.ucm.es
```

### 2. Crear `.env.idril` en local

Copia `docs/deployment/server.env.local.example` como `.env.idril` en la raíz del repo y rellena los valores reales. Este fichero es local y nunca se commitea (está en `.gitignore`).

Los valores que requieren configuración manual:

- `FACILITATION_LMS_URL`: URL del LMS de Open edX
- `LMS_JWT_AUTHENTICATION_TOKEN`: token JWT generado desde el OAuth2 del LMS (ver más abajo)
- `LOGFIRE_TOKEN`: token de [logfire.pydantic.dev](https://logfire.pydantic.dev)

Guarda una copia en un gist privado para no perder los secretos.

### 3. Generar el token JWT

El sistema usa un cliente OAuth2 con grant type `client_credentials` registrado en el LMS (`Django OAuth Toolkit > Applications`). El token se genera así:

```bash
curl -s -X POST https://<lms-url>/oauth2/access_token \
  -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=client_credentials&token_type=jwt"
```

El token dura 1 hora por defecto. Genéralo justo antes de ejecutar `make idril-setup` o `make idril-deploy`, y actualiza `LMS_JWT_AUTHENTICATION_TOKEN` en `.env.idril`.

## Configuración inicial (una sola vez)

```bash
make idril-setup
```

Este comando:

1. Copia `.env.idril` al servidor como `.env.local`
2. Clona el repo en `/home/2526-moderacion/app/` (o hace `git pull` si ya existe)
3. Instala las dependencias Python con `uv sync --no-dev`
4. Construye el dashboard con las URLs correctas para el servidor
5. Copia el dashboard a `/home/2526-moderacion/public_html/`
6. Crea el servicio systemd `facilitation-api` y lo habilita

El servicio systemd queda configurado en `~/.config/systemd/user/facilitation-api.service` y arranca automáticamente al reiniciar el servidor.

## Redespliegue

```bash
make idril-deploy
```

Hace `git pull`, reinstala deps, reconstruye el dashboard, copia a `public_html/` y reinicia el servicio.

## Actualizar variables de entorno en el servidor

Si necesitas actualizar `.env.local` sin redesplegar código:

```bash
scp .env.idril magrimal@idril.fdi.ucm.es:/home/2526-moderacion/app/.env.local
ssh magrimal@idril.fdi.ucm.es \
    "su - 2526-moderacion -c 'systemctl --user restart facilitation-api'"
```

## Modelos disponibles en Ollama

El servidor compartido (`10.100.0.1`) es una máquina de la red interna de la
UCM, no un recurso dedicado a este proyecto — su latencia no es
reproducible entre ejecuciones si hay otra carga en el host.

Tiene cuatro modelos instalados, pero `.env.idril` solo usa dos de ellos.
Datos obtenidos directamente de `curl http://10.100.0.1:11434/api/tags`
(2026-07-20) — todos son GGUF cuantizados a Q4_K_M:

| Modelo | Parámetros | Cuantización | Tamaño en disco | Uso configurado |
|---|---|---|---|---|
| `ollama:ministral-3:8b` | 8.9B | Q4_K_M | 6.0 GB | disponible, no usado por defecto |
| `ollama:ministral-3:14b` | 13.9B | Q4_K_M | 9.1 GB | `FACILITATION_LLM_MODEL` — modelo de facilitación en vivo (endpoint `/facilitate`) |
| `ollama:qwen3.5:9b` | 9.7B | Q4_K_M | 6.6 GB | disponible, no usado por defecto |
| `ollama:qwen3.5:27b` | 27.8B | Q4_K_M | 17.4 GB | `EVAL_MODELS` — evaluación comparada junto con `ministral-3:14b` |

`ollama:tags` también lista `ministral-3:latest` y `qwen3.5:latest`, pero
no son modelos adicionales: comparten digest con `ministral-3:8b` y
`qwen3.5:9b` respectivamente (mismo tamaño, mismo hash) — son solo el
alias `latest` de esos dos.

`ministral-3:8b` y `qwen3.5:9b` están instalados en el servidor pero no
forman parte de `EVAL_MODELS` ni de `FACILITATION_LLM_MODEL`; añadirlos
solo requiere editar `.env.idril` y hacer `make idril-deploy`.

### Timeout del pipeline

`FACILITATION_PIPELINE_TIMEOUT_SECONDS=1800` (temporal, solo para medir).
Historial: 180s (original) → 600s (2026-07-20, tras observar que
`qwen3.5:27b` agotaba 180s de forma consistente) → **falló también a
600s** → subido a 1800s como corrida de diagnóstico única, para obtener
la primera duración real y dejar de adivinar el valor. Una vez se tenga
esa duración, bajar a algo como `duración_real × 1.5`, no dejar 1800s
como valor permanente. Ver `docs/TODO.md`, sección de cobertura
modelo × fixture.

### Cobertura de test por modelo

`ministral-3:14b` tiene cobertura completa (8/8 fixtures de evaluación).
`qwen3.5:27b` solo ha corrido 4/8 (`active`, `convergent`, `new`,
`off_topic`) — le faltan `stalled`, `conflictive`, `shallow_discourse` y
`dominated`, pendientes de ejecutar ahora que el timeout es más alto. Ver
la matriz completa en `docs/TODO.md` ("Model × fixture coverage") y el
detalle por caso en `docs/experiments/test-sheets/`.

## Verificación

```bash
curl https://idril.fdi.ucm.es/2526-moderacion/api/health
```

Respuesta esperada: `{"status": "ok"}` con código 200.

El dashboard está en: `https://idril.fdi.ucm.es/2526-moderacion/`

## Gestión del servicio desde el servidor

Para diagnosticar problemas directamente en el servidor:

```bash
ssh magrimal@idril.fdi.ucm.es
su - 2526-moderacion
systemctl --user status facilitation-api
systemctl --user restart facilitation-api
journalctl --user -u facilitation-api -f
```
