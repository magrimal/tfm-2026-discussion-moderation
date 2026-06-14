# Despliegue en AWS EC2 — servicio de facilitación

Runbook operacional para el servicio de facilitación en EC2 con modelos externos (OpenRouter, Anthropic).

El servicio corre como contenedor Docker gestionado por Compose. La imagen se construye localmente con `podman` y se publica en ECR público.

El Open edX asociado corre en una instancia EC2 separada gestionado por Tutor. Ver `docs/decisions/0040-despliegue-openedx-en-aws-ec2.md` para ese contexto.

## Acceso al servidor

- **Host**: configurado en `~/.ssh/config` como `tfm-ec2` (hostname real no se versiona)
- **Usuario**: `ubuntu`
- **Directorio de la app**: `/home/ubuntu/app/`

```bash
ssh tfm-ec2
```

## Arquitectura

El `Containerfile` multi-stage construye la API (FastAPI/uvicorn) y el dashboard (React/Vite) en una sola imagen. Docker Compose orquesta dos servicios en EC2:

- `facilitation`: la imagen del servicio, expuesta internamente en el puerto 8080
- `caddy`: proxy inverso con TLS automático vía Let's Encrypt

El servicio es accesible en `https://facilitation.mgmdy.xyz`. Caddy gestiona el certificado TLS sin configuración adicional.

A diferencia de Idril, el servicio corre en la raíz (sin subpath nginx), por eso `FACILITATION_API_PREFIX` está vacío en `.env.ec2`.

## Imagen en ECR público

```
public.ecr.aws/h1n7c6s4/tfm/facilitation:latest
```

ECR público no requiere autenticación para pull. El push sí requiere credenciales AWS.

## Prerrequisitos (una sola vez)

### 1. Clave SSH

```bash
ssh-copy-id -i ~/.ssh/<clave_aws> ubuntu@<EC2_HOST>
```

Añadir a `~/.ssh/config`:

```
Host tfm-ec2
  HostName <EC2_HOST>
  User ubuntu
  IdentityFile ~/.ssh/<clave_aws>
```

### 2. Puerto 8080 abierto en el security group de EC2

La instancia debe tener el puerto 8080 abierto a las IPs que necesiten acceder al dashboard o la API.

### 3. Crear `.env.ec2` en local

Existe `.env.ec2` en la raíz del repo (no commiteado). Rellenar:

- `LMS_JWT_AUTHENTICATION_TOKEN`: generar desde el OAuth2 del LMS (ver más abajo)
- `LLM_API_KEY`: clave de OpenRouter (o Anthropic si cambias el modelo)

### 4. Generar el token JWT

```bash
curl -s -X POST https://lms.openedx.mgmdy.xyz/oauth2/access_token \
  -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=client_credentials&token_type=jwt"
```

El token dura 1 hora. Genéralo justo antes del despliegue y actualiza `LMS_JWT_AUTHENTICATION_TOKEN` en `.env.ec2`.

## Primer despliegue

```bash
# 1. Construir imagen y publicar en ECR
make ec2-build

# 2. Copiar .env.ec2 + docker-compose.yml al servidor y arrancar
make ec2-setup
```

`ec2-setup` instala Docker si no está, clona el repo, descarga la imagen y ejecuta `docker compose up -d`.

## Redespliegue

```bash
make ec2-build    # nueva imagen en ECR
make ec2-restart  # EC2 descarga y reinicia
```

## Actualizar variables de entorno sin redesplegar código

```bash
scp .env.ec2 tfm-ec2:/home/ubuntu/app/.env.local
ssh tfm-ec2 "cd /home/ubuntu/app && docker compose up -d"
```

## Modelos disponibles

| Modelo | Uso |
|---|---|
| `openrouter:openai/gpt-4o` | facilitación (por defecto) |
| `openrouter:anthropic/claude-3.5-sonnet` | alternativa de alta calidad |
| `openrouter:meta-llama/llama-3.3-70b-instruct:free` | evaluación (gratuito) |
| `anthropic:claude-sonnet-4-20250514` | directo via Anthropic |

Para cambiar el modelo: editar `FACILITATION_LLM_MODEL` en `.env.ec2` y actualizar variables de entorno (ver sección anterior).

## Verificación

```bash
curl https://facilitation.mgmdy.xyz/health
# {"status":"ok","lms_url":"https://lms.openedx.mgmdy.xyz"}
```

## Gestión del servicio desde el servidor

```bash
ssh tfm-ec2
cd /home/ubuntu/app
sudo docker compose ps
sudo docker compose logs -f facilitation
sudo docker compose logs -f caddy
sudo docker compose restart
```
