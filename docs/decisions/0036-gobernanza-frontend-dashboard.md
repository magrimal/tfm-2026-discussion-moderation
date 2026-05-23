# ADR 0036: Gobernanza del frontend del dashboard

**Estado**: Aceptado
**Fecha**: 2026-05-23
**Depende de**: ADR 0035 (configuracion en tiempo de despliegue)

## Descripcion

El dashboard habia acumulado tres problemas operativos:

1. Navegacion basada en estado local del componente, sin rutas estables
   (no habia deep-links ni historial del navegador consistente).
2. Refresco automatico continuo en la vista de runs, incluso cuando el usuario
   no estaba monitoreando un cambio activo.
3. Manejo de errores de historial de intervenciones acoplado a un estado global,
   lo que mezclaba errores entre hilos distintos en `ModelDetail`.

Adicionalmente, el frontend mantenia una cantidad significativa de codigo y
paquetes no usados por las vistas activas.

## Decision

Se adoptan las siguientes decisiones para el dashboard:

### 1. Navegacion basada en path (URL como fuente de verdad)

La navegacion del dashboard se modela por ruta y no por estado local opaco.
Se soportan explicitamente:

- `/runs`
- `/runs/:runId`
- `/runs/:runId/model-details/:modelName`
- `/trigger`

La UI sincroniza estado con `window.history` (`pushState`/`popstate`) para que
back/forward del navegador funcione de forma predecible.

### 2. Carga bajo demanda (sin polling global por defecto)

Se elimina el refresco periodico global de runs y detalle de run.
La pagina carga una vez por navegacion. Esto reduce ruido visual, consumo de red
innecesario y cambios inesperados de estado durante inspeccion manual.

### 3. Manejo de errores por hilo en historial de intervenciones

`ModelDetail` mantiene estado de carga/error por `thread_key` y añade una accion
explicita de reintento por hilo.

Consecuencia: un error en un hilo no contamina la visualizacion de historial de
otros hilos.

### 4. Limpieza de codigo no activo

Se eliminan componentes y vistas no alcanzables desde `dashboard/src/main.tsx`.
La limpieza se hace sobre el grafo real de imports, no por intuicion visual.

### 5. Baseline de estilo React con Airbnb

Se adopta ESLint con base Airbnb (`airbnb` + `airbnb-typescript`) como estandar
para el frontend del dashboard.

Para evitar un refactor masivo fuera de alcance, se aplican overrides
pragmaticos en reglas de formato y JSX de alto churn. El objetivo inmediato es
un baseline ejecutable y consistente (`npm run lint`) sobre el estado actual.

## Alternativas consideradas

### Mantener navegacion por estado local

Descartado: impide deep-linking robusto y hace mas dificil depurar reportes de
usuarios que comparten vistas especificas.

### Mantener polling siempre activo

Descartado: provoca refresco perceptible aunque no haya cambios y degrada la
experiencia de lectura/inspeccion.

### Reescribir todo el frontend para cumplir Airbnb estricto sin overrides

Descartado para esta fase: alto coste con bajo impacto funcional inmediato.
Se prioriza una migracion incremental manteniendo calidad operativa.

## Consecuencias

### Positivas

- Navegacion reproducible y compartible por URL.
- Menos refrescos inesperados durante analisis manual.
- Errores de historial encapsulados por hilo con retry explicito.
- Menor superficie de mantenimiento en codigo y dependencias.
- Linter estandarizado y ejecutable en CI/local.

### Negativas

- Al eliminar polling global, la UI no refleja progreso en tiempo real sin
  navegacion/accion de usuario.
- La adopcion Airbnb no es 100% estricta aun: existe deuda de estilo pendiente.

### Neutrales

- Esta decision no cambia contratos de API backend.
- Esta decision no modifica semantica de runs (`experiment`/`live`/`noop`).

## Alcance y fuera de alcance

Incluido en esta decision:

- Rutas del dashboard y sincronizacion con historial del navegador.
- Politica de carga sin refresco periodico global.
- Manejo de error/reintento por hilo en historial de intervenciones.
- Limpieza de codigo no alcanzable y poda de dependencias no usadas.
- Baseline Airbnb para lint del frontend.

Fuera de alcance en esta fase:

- Router declarativo externo (por ejemplo React Router) con arbol de rutas
  completo.
- Realtime streaming de progreso via SSE/WebSocket.
- Migracion completa a cumplimiento Airbnb estricto sin overrides.
