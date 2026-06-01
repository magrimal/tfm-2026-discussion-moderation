# ADR 0037: Diseño visual del dashboard: generación asistida por IA e iteración hacia simplicidad

**Estado**: Aceptado
**Fecha**: 2026-05-27
**Depende de**: ADR 0036 (gobernanza del frontend del dashboard)

## Descripcion

El dashboard necesitaba un sistema visual coherente y una interfaz usable para el PoC. El punto de partida era codigo generado por Figma Make a partir de un prompt detallado y un UI design brief escrito previamente. Ese codigo generado usaba clases Tailwind arbitrarias (`text-[10px]`, `tracking-[0.24em]`, escalas de grises crudas) sin tokens semanticos comunes, y organizaba las vistas en layouts de dos columnas que resultaban confusos en instalaciones remotas con distintas resoluciones.

El proceso de simplificacion partio de ese codigo generado y lo itero en dos ejes: la organizacion de la informacion (tomando como modelo mental los dashboards de CI/CD al estilo Jenkins) y el sistema visual (migrando a tokens semanticos con shadcn AI como generador del tema CSS).

## Decision

### 1. Figma Make como generador del codigo inicial

Se uso Figma Make (Figma AI) para generar el codigo inicial del dashboard a partir de un prompt en lenguaje natural y un UI design brief escrito previamente. El brief especificaba el proposito de la herramienta (dashboard de investigacion para comparar modelos LLM en escenarios de facilitacion de discusiones academicas), el layout general (sidebar fijo, area de contenido principal), las cinco vistas requeridas, el modelo de datos, y el estilo visual (fondo off-white, acento teal, Inter, monoespaciado para nombres de modelos).

La generacion paso por cuatro fases de iteracion dentro de Figma Make: dashboard inicial, adaptacion al brief de investigacion, integracion de la vista de disparo de ejecuciones al estilo Jenkins, y rediseño visual hacia un look mas moderno con gradientes. El resultado fue un dashboard funcional con cinco vistas, un sistema de gradientes teal, tarjetas con sombras, y una cuadricula de acceso a LogFuse.

Ese codigo generado sirvio como punto de partida. No se uso como especificacion de detalle ni como referencia de diseno: se uso directamente como base de implementacion, que luego se simplifico iterativamente.

### 2. Modelo mental: dashboards de CI/CD al estilo Jenkins

La organizacion general del dashboard toma como referencia dashboards de integracion continua tipo Jenkins. Las analogias concretas que se adoptaron:

- El historial de ejecuciones se presenta como **historial de builds** (no como "experimentos" ni "evaluaciones"), con estado de ejecucion como primer dato visible.
- La accion de disparar una ejecucion se llama **New build**, no "trigger run" ni "lanzar evaluacion".
- La navegacion lateral usa **Builds** y **New build** como entradas, siguiendo el par Jenkins de "Build History" / "Build Now".
- La matriz de trazas (modelos x escenarios) funciona como tabla de resultados de build: cada celda es un job, y el color indica exito, fallo o discrepancia.

Esta analogia fue util porque los usuarios del PoC (investigadores e ingenieros) ya tienen el modelo mental de un dashboard de CI/CD: saben que un "build" produce resultados inspeccionables, que puede fallar, y que se comparan builds para medir regresiones. Aplicar ese modelo a evaluaciones de LLM reduce la curva de aprendizaje sin necesidad de documentacion adicional.

### 3. Generacion del tema inicial con shadcn AI

Se uso el generador de temas de shadcn (`npx shadcn@latest init --preset ... --template vite`) para producir un sistema de variables CSS semanticas completo: colores, radios, tipografia y tokens de estado. El tema generado sigue la convencion shadcn/ui con variables CSS en `:root` mapeadas a clases Tailwind via `@theme inline`.

La generacion asistida se uso exclusivamente para el sistema de tokens, no para componentes de interaccion. Los componentes se escribieron o adaptaron manualmente.

### 4. Migracion de clases arbitrarias a tokens semanticos

Una vez establecido el tema, todos los componentes se migraron de clases arbitrarias a los tokens definidos:

- `text-[10px]` / `text-[11px]` => utilidades `text-label` / `text-caption` (via `@utility`)
- `tracking-[0.24em]` => `tracking-ui`
- Escalas de grises => `text-foreground`, `text-muted-foreground`, `bg-muted`, `border-border`
- Colores de estado (emerald, amber, rose, sky) => tokens `--status-passed`, `--status-unstable`, `--status-failed`, `--status-running`, `--status-noop`

El tema queda como unica fuente de verdad para el aspecto visual del dashboard.

### 5. Iteracion hacia columna unica y patrones secuenciales

Las vistas se simplificaron iterativamente hacia layouts de columna unica:

- **New build**: reemplaza el layout de dos columnas paralelas (hilos a la izquierda, modelos y configuracion a la derecha) por tres pasos secuenciales numerados, cada uno con texto de ayuda breve que explica su proposito.
- **ModelDetail**: reemplaza la cuadricula de tarjetas por una lista colapsable, donde cada hilo es una fila con estado resumido visible y detalle expandible.
- **RunDetail**: elimina la seccion "Run scope" con tarjetas de modelo, consolida el resumen del run en una lista de filas clave/valor, y añade "View details" como accion explicita en la columna de modelo de la matriz de trazas.
- **RunHistory**: la tabla mantiene estructura tabular (es datos comparables en filas), pero se corrige el comportamiento de hover aplicando `bg-muted` directamente a las celdas `<td>` en lugar del elemento `<tr>`.

El criterio guia de la iteracion fue: cada vista debe ser usable sin explicacion previa desde una instalacion remota o local del PoC.

### 6. Texto de ayuda inline

En lugar de documentacion externa o tooltips complejos, se añade texto descriptivo breve directamente en las secciones de la interfaz donde el proposito no es evidente. Las columnas de la tabla de historial conservan sus tooltips de `CircleHelp` por ser datos tecnicos con terminologia especifica. Los campos clasificatorios de cada hilo muestran su dimension como prefijo del valor (`trajectory: ascending`, `balance: dominated`) para que sean autoexplicativos sin interaccion adicional.

## Alternativas consideradas

### Usar una libreria de componentes completa (Material UI, Radix Themes, Ant Design)

Descartado: introduce dependencias de peso y opiniones de layout que habria que sobreescribir para ajustar al caso de uso. El sistema de tokens propio con Tailwind ofrece el mismo control con menos superficie de dependencia.

### Diseñar el tema manualmente desde cero

Descartado para esta fase: el codigo generado por Figma Make ya proporcionaba un punto de partida visual funcional, y el PoC no requiere identidad visual original. El tiempo de un diseño manual completo no es justificable en relacion al valor que aporta en este contexto.

### Mantener layouts en dos columnas

Descartado: en instalaciones locales y remotas con distintas configuraciones de pantalla, la division en columnas paralelas resultaba confusa porque no comunicaba orden de operacion. El layout secuencial hace el flujo explicito.

### Usar terminologia del dominio academico ("evaluacion", "experimento", "lanzar")

Descartado: los usuarios del PoC son ingenieros que ya conocen el modelo mental de CI/CD. La terminologia de builds (New build, build history, trace matrix) transfiere ese conocimiento existente al contexto de evaluacion de LLMs sin necesidad de explicacion adicional.

## Consecuencias

### Positivas

- Un unico sistema de tokens CSS para todo el dashboard: cambios de color o tipografia se aplican en un solo lugar.
- Vistas mas faciles de usar sin contexto previo, especialmente desde instalaciones remotas.
- El flujo de "New build" comunica pasos ordenados, reduciendo errores de uso (por ejemplo, disparar un run sin seleccionar modelos ni hilos).
- Menor diferencia entre lo que el codigo dice y lo que el usuario ve.

### Negativas

- El tema generado por IA requirio ajustes manuales: `@theme inline` en Tailwind v4 no acepta variables de font-size ni letter-spacing directamente, lo que obligo a usar `@utility` para esos tokens.
- La iteracion de simplificacion fue incremental y reactiva al uso real, no planificada desde el inicio. Parte del codigo se reescribio dos veces.

### Neutrales

- Esta decision no afecta contratos de API backend ni semantica de runs.
- El dashboard sigue siendo una herramienta de inspeccion y disparo de evaluaciones, no una interfaz de produccion para usuarios finales.

## Alcance y fuera de alcance

Incluido en esta decision:

- Sistema de tokens CSS del dashboard y migracion de componentes existentes.
- Criterios de layout para vistas nuevas o reescritas.
- Politica de texto de ayuda inline.

Fuera de alcance en esta fase:

- Internacionalizacion de la interfaz.
- Modo oscuro (las variables CSS estan preparadas para soportarlo pero no se activa).
- Tests de interfaz de usuario automatizados.
