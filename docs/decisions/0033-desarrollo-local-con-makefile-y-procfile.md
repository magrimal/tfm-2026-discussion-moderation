# ADR 0033: Desarrollo local con Makefile y Procfile

**Estado**: Aceptado
**Fecha**: 2026-05-18
**Depende de**: ADR 0024 (separacion deps/state), ADR 0026 (separacion API interna y REST)

## Descripción

El repositorio necesita arrancar dos procesos de desarrollo de forma
coordinada: el backend FastAPI y el dashboard Vite. Durante esta iteración
se evaluaron tres alternativas:

- exponer un comando de desarrollo en `pyproject.toml` mediante un script
  Python propio del paquete;
- documentar solo comandos crudos (`npm --prefix dashboard install` y
  `uv run --extra dev honcho start -f Procfile.dev`);
- usar un `Makefile` como interfaz ergonómica y un `Procfile.dev` como
  definición declarativa de procesos.

La primera opción mezclaba orquestación local con código del paquete
`discussion_moderation`. La segunda reducía abstracción, pero obligaba a
recordar comandos largos y heterogéneos entre Python y Node.js.

## Decisión

El comportamiento final de desarrollo local se define así:

- `Procfile.dev` es la fuente de verdad de los procesos locales.
- `make dev-setup` instala las dependencias del dashboard.
- `make dev-up` arranca el backend y el frontend usando `honcho` sobre
  `Procfile.dev`.
- `pyproject.toml` no expone comandos equivalentes para arrancar el stack
  local multi-proceso.

Los scripts de `pyproject.toml` quedan reservados para entry points Python que
sí pertenecen al paquete o a sus herramientas de línea de comandos, por
ejemplo `facilitate`, `eval-pipeline` o `render-prompt`.

La definición efectiva de procesos es:

```text
api: uv run uvicorn discussion_moderation.rest_api.main:app --reload
web: npm run dev --prefix dashboard
```

## Consecuencias

### Positivas

- Hay una única interfaz canónica y corta para desarrolladores: `make
  dev-setup` y `make dev-up`.
- La composición de procesos queda en un archivo declarativo (`Procfile.dev`)
  en lugar de código Python imperativo dentro del paquete.
- El `Makefile` conserva ergonomía sin forzar a `pyproject.toml` a resolver
  un caso que no es su responsabilidad natural.
- El backend y el frontend siguen pudiendo ejecutarse por separado cuando hace
  falta depuración puntual.

### Negativas

- Se introduce una capa adicional (`make`) por encima de `uv`, `npm` y
  `honcho`.
- Quien no use `make` debe conocer igualmente los comandos subyacentes.
- La interfaz canónica depende de una convención de repositorio, no de una
  convención universal del ecosistema Python.

### Opciones descartadas

- **Script Python en `pyproject.toml` para desarrollo local**: descartado
  porque convierte la orquestación del repositorio en lógica de paquete, y
  tiende a crecer con manejo de procesos, señales y validaciones ad hoc.
- **Solo comandos crudos documentados**: descartado por ergonomía. El coste de
  recordar dos comandos largos y distintos era innecesario para el flujo
  diario.
- **Contenedores como interfaz principal**: descartado en esta fase porque el
  repositorio no necesita todavía orquestar infraestructura local propia.

## Referencias

- `Makefile`
- `Procfile.dev`
- `pyproject.toml`
- `dashboard/README.md`
- `README.md`