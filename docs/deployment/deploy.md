# Guía de despliegue — idril.fdi.ucm.es

## Acceso al servidor

```bash
ssh magrimal@idril.fdi.ucm.es
```

Puerto por defecto (22). No se necesita VPN.

El servidor Ollama compartido está en `10.100.0.1`. La variable `OLLAMA_HOST`
ya está configurada en el entorno del contenedor, no hay que añadirla manualmente.

---

## Configuración inicial (una sola vez)

### 1. Preparar `.env.local` en local

Copia la plantilla y rellena los valores:

```bash
cp docs/deployment/server.env.local.example .env.local.server
# Edita .env.local.server con los valores reales
```

Los valores que debes rellenar:
- `FACILITATION_LMS_URL` — URL de la instancia Open edX
- `LMS_JWT_AUTHENTICATION_TOKEN` — token JWT del LMS
- `LOGFIRE_TOKEN` — token de logfire.pydantic.dev (opcional)

Guarda una copia en un gist privado para no perderla.

### 2. Ejecutar `make server-setup`

```bash
make server-setup
```

Esto hace automáticamente:
1. Copia `.env.local` al servidor
2. Clona el repositorio en `/home/2526-moderacion/app`
3. Instala las dependencias Python (`uv sync --no-dev`)
4. Instala las dependencias del dashboard y lo construye
5. Copia el dashboard a `/home/2526-moderacion/public_html/`
6. Crea y habilita el servicio systemd

El servicio queda configurado en
`~/.config/systemd/user/facilitation-api.service` y arranca automáticamente
al reiniciar el servidor.

### 3. Verificar

```bash
curl https://idril.fdi.ucm.es/2526-moderacion/api/health
```

Abre `https://idril.fdi.ucm.es/2526-moderacion/` en el navegador.

---

## Redespliegue

### API y dashboard (código nuevo)

```bash
make server-restart
```

Hace `git pull`, reinstala dependencias, reconstruye el dashboard y reinicia
el servicio.

### Solo la API (sin cambios en el dashboard)

```bash
make server-restart-api
```

---

## Gestión manual del servicio

Si necesitas gestionar el servicio directamente en el servidor:

```bash
ssh magrimal@idril.fdi.ucm.es
su - 2526-moderacion

systemctl --user status facilitation-api
systemctl --user restart facilitation-api
systemctl --user stop facilitation-api

# Ver logs
journalctl --user -u facilitation-api -f
```

---

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

La API se sirve en el puerto 8080 interno. nginx redirige
`/2526-moderacion/api/*` a ese puerto.

---

## Actualizar `.env.local` en el servidor

```bash
scp .env.local.server magrimal@idril.fdi.ucm.es:/home/2526-moderacion/app/.env.local
ssh magrimal@idril.fdi.ucm.es \
    "su - 2526-moderacion -c 'systemctl --user restart facilitation-api'"
```
