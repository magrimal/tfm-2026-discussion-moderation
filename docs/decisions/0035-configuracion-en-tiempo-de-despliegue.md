# ADR 0035: Configuración gestionada en tiempo de despliegue

**Estado**: Aceptado
**Fecha**: 2026-05-19
**Depende de**: ADR 0031 (perfiles de configuración por modelo), ADR 0033 (desarrollo local)

## Descripción

El dashboard incluía una pantalla de configuración ("Pipeline Configuration")
que permitía editar modelos, pesos de evaluación y el endpoint de observabilidad
desde la interfaz. Esa pantalla era un mock puro: su estado vivía exclusivamente
en el componente React y nunca se enviaba al backend. Un botón "Save" llamaba a
`alert('Configuration saved successfully!')`.

La existencia de esa pantalla creaba una expectativa falsa: que el sistema
soporta reconfiguración en caliente desde el navegador. Esa capacidad no es
necesaria para los objetivos de la tesis ni está prevista a corto plazo.

## Decisión

La configuración del sistema es responsabilidad exclusiva del despliegue. No
existe una pantalla de configuración en el dashboard.

Los parámetros configurables se gestionan mediante variables de entorno y el
fichero `.env` local, siguiendo el patrón ya establecido por `Settings`
(pydantic-settings) en `discussion_moderation/config.py`:

| Parámetro | Variable de entorno |
|---|---|
| Modelo(s) para evaluación | `EVAL_MODELS` |
| URL del LMS | `FACILITATION_LMS_URL` / `LMS_URL` |
| Token JWT del LMS | `LMS_JWT_AUTHENTICATION_TOKEN` |
| Backend LMS | `FACILITATION_LMS_BACKEND` |
| Ruta de la base de datos SQLite | (pendiente, HU-12) |
| URI de MongoDB | (pendiente, ADR 0034) |
| Endpoint de observabilidad | `LOGFIRE_TOKEN` |

Los perfiles de modelo (modo de extracción, herramientas funcionales) se
gestionan en código mediante `ModelProfile` y `MODEL_PROFILES` por proveedor
(ADR 0031). Sobreescrituras puntuales son posibles con variables de entorno
en tiempo de ejecución sin tocar el registro estático.

## Alternativas consideradas

**Pantalla de configuración conectada al backend**: requeriría un endpoint
`PUT /config`, persistencia de la configuración (fichero o BD), y recarga
del pipeline en caliente. El coste de implementación no está justificado para
un PoC de tesis donde el operador y la investigadora son la misma persona.

**Mantener la pantalla como mock con advertencia**: añade ruido sin aportar
valor. El warning "Prototype flow. These settings are local UI state" comunicaba
el problema, no la solución. Un mock que parece funcional es peor que no tener
la funcionalidad.

## Consecuencias

### Positivas

- La interfaz no promete capacidades que no existen.
- El sidebar refleja con precisión lo que el sistema realmente puede hacer
  desde el navegador: inspeccionar runs y lanzar ejecuciones.
- Se elimina `Configuration.tsx` y sus imports, reduciendo la superficie de
  código mock sin valor funcional.

### Negativas

- Un operador que quiera cambiar la lista de modelos o el endpoint de
  observabilidad tiene que hacerlo editando variables de entorno y
  reiniciando el proceso, no desde el navegador.

### Neutrales

- Si en el futuro se necesita reconfiguración en caliente, el patrón a seguir
  es un endpoint `PUT /config` protegido por autenticación, no una pantalla
  de dashboard que lea y escriba estado local. Esa decisión es independiente
  de esta.
