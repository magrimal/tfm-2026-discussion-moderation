# TFM 2026

Diseño, implementación e integración de un modelo de moderación inteligente para discusiones académicas en plataformas de aprendizaje abiertas.

## Descripción

Este repositorio contiene el trabajo asociado al Trabajo Fin de Máster (TFM), centrado en el diseño, implementación e integración de un modelo de moderación inteligente basado en modelos de lenguaje (LLMs).

El objetivo del proyecto es desarrollar un servicio interoperable y vendor-neutral que permita moderar discusiones académicas  en entornos educativos en línea, y que pueda integrarse con plataformas de aprendizaje abiertas como pero no limitado a Open edX.

## Gestión del trabajo

La planificación y el seguimiento del proyecto se realizan mediante:

* GitHub Issues, utilizados como backlog del TFM.
* GitHub Projects, utilizados para la gestión y visualización del progreso.

La información detallada sobre tareas, hitos y estado del trabajo se mantiene directamente en estas herramientas.

## Estructura del repositorio

La estructura del repositorio podrá evolucionar a lo largo del desarrollo del TFM. Actualmente se organiza con un servicio backend en Python y una aplicación de interfaz separada en la raíz del repositorio:

```
tfm-2026/
├── discussion_moderation/
├── dashboard/
└── docs/
```

## Desarrollo local

Desde la raíz del repositorio:

- `make dev-setup` instala las dependencias del dashboard.
- `make dev-up` arranca el backend y el frontend juntos con un runner de procesos a nivel de repositorio.
- `make serve` arranca solo el backend en el puerto definido por `DISCUSSION_MODERATION_API_PORT`.

Estos dos comandos son la interfaz canónica de desarrollo local. No se
mantienen comandos equivalentes en `pyproject.toml` para arrancar varios
procesos; los scripts del paquete quedan reservados para herramientas Python
propias del proyecto.

El puerto local del backend es configurable mediante
`DISCUSSION_MODERATION_API_PORT` en `.env` o `.env.local`. Por defecto se usa
`8765`. Por ejemplo:

- `DISCUSSION_MODERATION_API_PORT=8765 make dev-up`
- `DISCUSSION_MODERATION_API_PORT=8765 make serve`

En desarrollo local, `.env.local` sobrescribe `.env`.

El archivo `Procfile.dev` define los procesos locales:

- `api` ejecuta el backend FastAPI con recarga.
- `web` ejecuta el dashboard Vite.

## Autora

María Grimaldi
Máster en Ingeniería Informática, UCM
2026
