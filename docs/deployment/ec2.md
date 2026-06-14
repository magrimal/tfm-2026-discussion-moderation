# Despliegue en AWS EC2 — servicio de facilitación

Runbook operacional para el servicio de facilitación en EC2 con modelos externos (OpenRouter, Anthropic).

El servicio corre como tres contenedores Docker Compose gestionados por Caddy. La imagen se construye localmente con `podman` y se publica en ECR público.

El Open edX asociado corre en una instancia EC2 separada gestionada por Tutor. Ver `docs/decisions/0040-despliegue-openedx-en-aws-ec2.md` para ese contexto.

## Acceso al servidor

- **URL pública**: `https://facilitation.mgmdy.xyz`
- **Host SSH**: configurado en `~/.ssh/config` como `tfm-ec2` (hostname real no se versiona)
- **Usuario**: `ubuntu`
- **Directorio de la app**: `/home/ubuntu/app/`

```bash
ssh tfm-ec2
```

## Arquitectura

Tres contenedores en Docker Compose:

| Contenedor | Imagen | Rol |
|---|---|---|
| `dashboard-init` | `facilitation:latest` | Copia `dashboard/dist` al volumen compartido y termina |
| `facilitation` | `facilitation:latest` | API FastAPI en el puerto 8080 interno |
| `caddy` | `caddy:2-alpine` | Proxy inverso HTTPS; sirve el dashboard estático y proxea `/api/*` a `facilitation:8080` |

Caddy gestiona TLS automáticamente con Let's Encrypt. El volumen `dashboard_dist` es el canal entre `dashboard-init` (escribe) y `caddy` (lee). `caddy` solo arranca cuando `dashboard-init` termina con éxito.

El prefijo `/api` es obligatorio en EC2: `FACILITATION_API_PREFIX=/api` en `.env.ec2`, y el `Containerfile` compila el dashboard con `VITE_API_BASE_URL="/api"`.

## Imagen en ECR público

```
public.ecr.aws/h1n7c6s4/tfm/facilitation:latest
```

ECR público no requiere autenticación para pull. El push requiere credenciales AWS.

## Prerrequisitos (una sola vez)

### 1. Clave SSH y alias

Añadir a `~/.ssh/config`:

```
Host tfm-ec2
  HostName <EC2_HOST>
  User ubuntu
  IdentityFile ~/.ssh/<clave_aws>
```

Verificar conexión:

```bash
ssh tfm-ec2 echo OK
```

### 2. Puertos 80 y 443 abiertos en el security group

Caddy necesita el puerto 80 para el desafío ACME de Let's Encrypt y el 443 para HTTPS. El puerto 8080 no se expone al exterior.

### 3. Registro DNS en Route 53

Registro A: `facilitation.mgmdy.xyz` → IP de la instancia EC2. Hosted zone `mgmdy.xyz` (ID: `Z02030192A97E4Y6SRVJX`).

### 4. Crear `.env.ec2` en local

Existe `.env.ec2` en la raíz del repo (no commiteado, en `.gitignore`). Rellenar:

- `LMS_JWT_AUTHENTICATION_TOKEN`: generar desde el OAuth2 del LMS (ver más abajo)
- `LLM_API_KEY`: clave de OpenRouter (o Anthropic si se cambia el modelo)

### 5. Generar el token JWT

```bash
curl -s -X POST https://lms.openedx.mgmdy.xyz/oauth2/access_token \
  -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=client_credentials&token_type=jwt"
```

El token dura 1 hora. Genéralo justo antes del despliegue y actualiza `LMS_JWT_AUTHENTICATION_TOKEN` en `.env.ec2`.

## Primer despliegue

```bash
# 1. Construir imagen y publicar en ECR
make ec2-build

# 2. Copiar .env.ec2, docker-compose.yml al servidor, instalar Docker y arrancar
make ec2-setup
```

`ec2-setup` instala Docker si no está, clona el repo, copia el env y ejecuta `docker compose up -d`.

## Redespliegue

```bash
make ec2-build    # reconstruye imagen y la publica en ECR
make ec2-restart  # git pull en EC2, descarga imagen, recrea volumen y reinicia
```

`ec2-restart` recrea el volumen `dashboard_dist` en cada ejecución para que `dashboard-init` copie los archivos de la nueva imagen.

## Actualizar variables de entorno sin redesplegar código

```bash
scp .env.ec2 tfm-ec2:/home/ubuntu/app/.env.local
ssh tfm-ec2 "cd /home/ubuntu/app && sudo docker compose up -d"
```

## Modelos disponibles

| Modelo | Uso |
|---|---|
| `openrouter:openai/gpt-4o` | facilitación (por defecto) |
| `openrouter:anthropic/claude-3.5-sonnet` | alternativa de alta calidad |
| `openrouter:meta-llama/llama-3.3-70b-instruct:free` | evaluación (gratuito) |
| `anthropic:claude-sonnet-4-20250514` | directo via Anthropic (requiere clave Anthropic) |

Para cambiar el modelo: editar `FACILITATION_LLM_MODEL` en `.env.ec2` y actualizar variables de entorno (ver sección anterior).

## Verificación

```bash
# API
curl https://facilitation.mgmdy.xyz/api/health
# {"status":"ok","lms_url":"https://lms.openedx.mgmdy.xyz"}

# Dashboard (debe devolver HTML)
curl -s https://facilitation.mgmdy.xyz/ | head -3
```

El dashboard es accesible en el navegador en `https://facilitation.mgmdy.xyz`.

## Gestión del servicio desde el servidor

```bash
ssh tfm-ec2
cd /home/ubuntu/app
sudo docker compose ps
sudo docker compose logs -f facilitation
sudo docker compose logs -f caddy
sudo docker compose restart facilitation
```
