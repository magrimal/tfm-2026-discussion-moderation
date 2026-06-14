# Despliegue en AWS EC2 — servicio de facilitación

Runbook operacional para el servicio de facilitación en EC2 con modelos externos (OpenRouter, Anthropic).

El Open edX asociado corre en la misma instancia EC2 gestionado por Tutor. Ver `docs/decisions/0040-despliegue-openedx-en-aws-ec2.md` para el contexto de esa decisión.

## Acceso al servidor

- **Host**: configurado en `~/.ssh/config` como `tfm-ec2` (hostname real no se versiona)
- **Usuario**: `ubuntu`
- **Directorio de la app**: `/home/ubuntu/app/`

```bash
ssh ubuntu@tfm-ec2
```

## Arquitectura en el servidor

El servicio de facilitación corre como un servicio systemd bajo el usuario `ubuntu`. Nginx actúa como proxy inverso:

- `/api/*` reenvía al puerto 8080 (FastAPI via uvicorn)
- `/` sirve el dashboard estático

A diferencia de Idril, el servicio corre en el dominio raíz (sin subpath), por eso `FACILITATION_API_PREFIX` está vacío en `.env.ec2`.

## Estructura en el servidor

```
/home/ubuntu/
  app/                  repositorio clonado
    .env.local          variables de entorno (secretos, no en git)
    history.db          historial de intervenciones (SQLite)
    scripts/
      ec2_setup.sh      script de configuración inicial
      ec2_restart.sh    script de redespliegue
```

## Prerrequisitos (una sola vez)

### 1. Clave SSH

```bash
ssh-copy-id ubuntu@tfm-ec2
```

### 2. Crear `.env.ec2` en local

Copia `.env.local.example` como `.env.ec2` en la raíz del repo (ya existe una versión base). Rellena los valores:

- `LMS_JWT_AUTHENTICATION_TOKEN`: generar desde el OAuth2 del LMS (ver más abajo)
- `LLM_API_KEY`: clave de OpenRouter (o Anthropic si cambias el modelo)
- `FACILITATION_LMS_URL`: debe apuntar a `https://lms.openedx.mgmdy.xyz`

### 3. Generar el token JWT

```bash
curl -s -X POST https://lms.openedx.mgmdy.xyz/oauth2/access_token \
  -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=client_credentials&token_type=jwt"
```

El token dura 1 hora. Genéralo justo antes del despliegue y actualiza `LMS_JWT_AUTHENTICATION_TOKEN` en `.env.ec2`.

## Configuración inicial (una sola vez)

```bash
make ec2-setup
```

Esto copia `.env.ec2` al servidor como `.env.local`, clona el repo e instala el servicio systemd.

Si el target de make no existe todavía, el equivalente manual:

```bash
scp .env.ec2 ubuntu@tfm-ec2:/home/ubuntu/app/.env.local
ssh ubuntu@tfm-ec2 bash -s < scripts/ec2_bootstrap.sh
```

## Redespliegue

```bash
make ec2-restart
```

O manualmente:

```bash
ssh ubuntu@tfm-ec2 bash /home/ubuntu/app/scripts/ec2_restart.sh
```

## Actualizar variables de entorno

```bash
scp .env.ec2 ubuntu@tfm-ec2:/home/ubuntu/app/.env.local
ssh ubuntu@tfm-ec2 systemctl restart facilitation-api
```

## Variables de entorno

El archivo `.env.ec2` local se sube al servidor como `.env.local`. La app lo lee automáticamente (pydantic-settings carga `.env` y `.env.local` en ese orden).

Localmente, para probar con la configuración de EC2 sin renombrar el archivo:

```bash
APP_ENV_FILE=.env.ec2 uv run python -c \
  "from discussion_moderation.config import get_settings; print(get_settings().llm_model)"
```

## Modelos disponibles

| Modelo | Uso |
|---|---|
| `openrouter:openai/gpt-4o` | facilitación (por defecto) |
| `openrouter:anthropic/claude-3.5-sonnet` | alternativa de alta calidad |
| `openrouter:meta-llama/llama-3.3-70b-instruct:free` | evaluación (gratuito) |
| `anthropic:claude-sonnet-4-20250514` | directo via Anthropic (requiere `LLM_API_KEY` de Anthropic) |

Para cambiar el modelo sin redesplegar:

```bash
# Editar .env.ec2 localmente, luego:
scp .env.ec2 ubuntu@tfm-ec2:/home/ubuntu/app/.env.local
ssh ubuntu@tfm-ec2 systemctl restart facilitation-api
```

## Verificación

```bash
curl https://<EC2_DOMAIN>/api/health
```

Respuesta esperada: `{"status": "ok"}` con código 200.

## Gestión del servicio desde el servidor

```bash
ssh ubuntu@tfm-ec2
systemctl status facilitation-api
systemctl restart facilitation-api
journalctl -u facilitation-api -f
```
