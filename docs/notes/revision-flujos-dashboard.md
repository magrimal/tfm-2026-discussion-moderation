# Revision de flujos del dashboard

Revision del dashboard actual para explicitar:

- que historias de usuario parece querer cubrir la UI
- que flujos estan realmente implementados hoy
- donde hay gaps, ambiguedades o complejidad innecesaria

La revision se basa en el comportamiento actual de la interfaz, no en una
vision futura ideal.

## Problema observado

La navegacion actual mezcla dos niveles distintos:

- vistas principales del producto
- pasos internos de inspeccion dentro de una ejecucion

Esto hace que el usuario no tenga una jerarquia clara de navegacion.
El caso mas visible es este:

- desde `Run overview` se puede saltar a la vista de un modelo
- esa vista se presenta como una nueva pantalla completa
- no existe una accion local para volver al contexto anterior
- el sidebar sigue marcando `Run overview`, pero no explica donde esta el usuario realmente

El resultado es una sensacion de "me movi a otro sitio sin querer".

## Pantallas actuales

### 1. Run history

Objetivo actual:

- listar ejecuciones disponibles
- abrir una ejecucion concreta

Accion principal:

- `Open` lleva a `Run overview`

### 2. Run overview

Objetivo actual:

- resumir una ejecucion
- comparar modelos por escenario en la trace matrix
- cambiar la ejecucion seleccionada
- abrir el detalle de un modelo

Acciones disponibles:

- cambiar `Current run`
- pulsar un modelo en `Models in this run`
- pulsar el nombre de un modelo en la matriz
- abrir una traza si la celda tiene URL

### 3. Model detail

Objetivo actual:

- inspeccionar un modelo dentro de una ejecucion
- revisar resultados por hilo/escenario
- expandir razonamientos
- abrir una traza si existe

Problema:

- se comporta como una vista top-level, pero conceptualmente es un subnivel de `Run overview`

### 4. Trigger run

Objetivo actual:

- seleccionar hilos
- seleccionar modelos
- disparar una ejecucion

Problema:

- el flujo base ya es real para ejecuciones de evaluacion; falta separar claramente el modo experimento del modo live

### 5. Configuration

Objetivo actual:

- editar configuracion del pipeline

Problema:

- esta vista fue retirada por ADR 0035 para evitar una capacidad que no existe en runtime

## Historias de usuario implicadas por la UI

Estas son las historias de usuario que la interfaz actual ya intenta cubrir.

## HU-01. Revisar el historial de ejecuciones

Como investigadora
quiero ver las ejecuciones recientes y su estado
para decidir cual inspeccionar.

Estado actual:

- implementada de forma razonable

Notas:

- la tabla comunica bien estado, fecha y errores
- la accion `Open` es clara

## HU-02. Abrir una ejecucion y entender su salud general

Como investigadora
quiero abrir una ejecucion y ver un resumen general
para saber si vale la pena inspeccionarla en detalle.

Estado actual:

- implementada

Notas:

- el resumen general es entendible
- el cambio de `Current run` dentro de la vista funciona como acceso rapido

## HU-03. Comparar modelos lado a lado por escenario

Como investigadora
quiero comparar rapidamente como se comportan varios modelos por escenario
para detectar outliers, errores o clasificaciones sospechosas.

Estado actual:

- implementada, pero con complejidad semantica innecesaria

Notas:

- la matriz ya sirve como vista comparativa principal
- habia dependencias heredadas del mock que la hacian confusa
- aun queda aclarar mejor que una celda puede ser informativa aunque no tenga enlace de traza

## HU-04. Abrir el detalle de un modelo desde una ejecucion

Como investigadora
quiero pasar de la vista general de una ejecucion al detalle de un modelo concreto
para entender por que ese modelo se comporto asi.

Estado actual:

- implementada de forma incompleta

Gap principal:

- falta una transicion explicita de contexto y una forma local de volver

## HU-05. Inspeccionar un hilo concreto dentro del detalle de un modelo

Como investigadora
quiero expandir un hilo concreto dentro de un modelo
para revisar clasificacion, decision de intervencion y razonamiento.

Estado actual:

- implementada

Gaps:

- los cards ya usan datos reales por hilo, pero aun falta homogeneizar la semantica para runs con hilos LMS sin `expected_state`

## HU-06. Abrir la traza de ejecucion cuando exista

Como investigadora
quiero abrir la traza de una ejecucion concreta
para auditar el razonamiento completo fuera del dashboard.

Estado actual:

- implementada solo cuando existe `logfuse_url`

Gaps:

- no siempre queda claro cuando una celda no tiene enlace porque no hubo traza, y no porque no hubo resultado

## HU-07. Cambiar de ejecucion sin perder el hilo de inspeccion

Como investigadora
quiero cambiar a otra ejecucion sin perder claridad sobre donde estoy
para comparar runs sin desorientarme.

Estado actual:

- parcialmente implementada

Gaps:

- `Current run` existe, pero la arquitectura de vistas no deja claro si sigo en overview, si cambie de contexto o si deberia resetear el subnivel actual

## HU-08. Lanzar una nueva ejecucion desde el dashboard

Como investigadora
quiero preparar y lanzar una ejecucion nueva
para evaluar un conjunto de hilos y modelos.

Estado actual:

- implementada

Notas:

- el trigger lanza el run real via API y lo ejecuta en background
- el dashboard muestra el `run_id` y permite volver al historial

## HU-09. Configurar el pipeline desde el dashboard

Como investigadora
quiero ajustar modelos y parametros del pipeline
para controlar como se ejecutan futuras evaluaciones.

Estado actual:

- despriorizada por decision de producto (ADR 0035)

Notas:

- la configuracion se gestiona en despliegue (`Settings` + variables de entorno)
- la vista `Configuration` se elimino del dashboard para evitar expectativas falsas

## HU-10. Seleccionar hilos reales de Open edX como entrada de una ejecucion

Como investigadora
quiero poder seleccionar hilos activos de un curso real de Open edX
para evaluar el pipeline contra discusiones reales en lugar de solo fixtures.

Estado actual:

- implementada en backend y trigger UI (pendiente validacion UX integrada)

Descripcion:

- el usuario elige la fuente de hilos al configurar una ejecucion: "Fixtures" (hilos sinteticos ya existentes) o "LMS" (hilos reales de Open edX)
- cuando elige LMS, introduce un course_id y el dashboard obtiene los hilos activos via `GET /lms/threads?course_id=...`
- el backend usa el `OpenEdXBackend` ya existente con `lms_url` y `lms_jwt_authentication_token` de la configuracion
- si el LMS no esta configurado, el endpoint devuelve un error claro y el dashboard lo muestra como estado de advertencia, sin bloquear la seleccion de fixtures
- los hilos obtenidos del LMS se presentan igual que los fixtures: titulo, cuerpo, comentarios visibles bajo expansion

Gaps de diseno abiertos:

- la semantica de un hilo de LMS en una ejecucion de evaluacion es diferente: no tiene "expected_state", asi que la matriz de traza no tiene referencia contra la que comparar
- hay que decidir si los runs con hilos de LMS producen una vista de resultados distinta, o si se adapta la vista actual para mostrar el estado clasificado sin columna de "correcto/incorrecto"
- autenticacion: el JWT del LMS expira; si la sesion del dashboard dura mas que el token, hay que manejar el error

## HU-11. Distinguir entre runs de experimento y runs en vivo

Como investigadora o facilitadora
quiero saber si una ejecucion es un experimento (evaluacion contra fixtures o hilos historicos) o un run en vivo (supervision activa de un hilo real)
para interpretar sus resultados con el contexto correcto.

Estado actual:

- parcialmente implementada

Notas:

- el esquema y la API ya distinguen `run_type: "experiment" | "live"`
- existe `POST /runs/live/trigger` para ejecutar un run en vivo por hilo
- los runs en vivo cerrados terminan como `noop` y no ejecutan facilitacion

Descripcion:

Un **experimento** es una ejecucion que:
- se lanza manualmente desde el dashboard
- procesa hilos congelados (fixtures o snapshot de LMS)
- no genera intervenciones reales en el LMS
- produce una traza completa con expected_state para comparar
- puede ejecutar multiples modelos en paralelo

Un **run en vivo** es una ejecucion que:
- se lanza contra un hilo activo de Open edX
- usa un unico modelo (el configurado como produccion)
- evalua el hilo en el estado actual; si la discusion esta cerrada, el resultado es "noop"
- puede generar una intervencion real y publicarla si la configuracion lo permite
- registra la intervencion en el historial de intervenciones por hilo (ADR 0007) para respetar cooldowns y escalada EMT en la siguiente ejecucion

Comportamiento esperado cuando el hilo esta cerrado:

- el run termina con estado `noop`
- no se genera intervencion
- no se escribe en el historial

Gaps de diseno abiertos:

- como se modela el tipo de run en el esquema de datos: campo `run_type: "experiment" | "live"` en el resultado, o tablas separadas
- los runs en vivo tienen semantica diferente en la vista de resultados: no hay expected_state ni matriz de comparacion; se muestra la decision tomada y si fue publicada
- quien dispara los runs en vivo: el dashboard manualmente, un job periodico externo, o ambos
- un run en vivo con multiples hilos simultaneos no tiene un modelo claro todavia: se propone un hilo por run como unidad atomica

## HU-12. Persistir el historial de intervenciones en base de datos

Como sistema de facilitacion
quiero registrar cada intervencion generada en una base de datos duradera
para poder respetar cooldowns, seguir la escalada EMT y auditar decisiones entre reinicios.

Estado actual:

- implementada en backend

Notas:

- `history_backend` y `history_db_path` se leen desde `Settings` y se aplican en el pipeline
- se expuso `GET /threads/{thread_id}/history` para consultar historial por hilo
- en runs en vivo, el pipeline usa el store configurado; en experimentos se fuerza backend en memoria para aislamiento

Descripcion:

- en un run en vivo, tras generar una intervencion, el pipeline llama a `store.record_intervention(thread_id, record)` antes de devolver el resultado
- el store usado en produccion es `SQLiteThreadStore` con ruta configurable via variable de entorno
- el pipeline consulta `store.get_history(thread_id)` al inicio para respetar cooldown y seguir la escalada EMT desde donde se dejo
- en experimentos, el historial no se escribe en SQLite; se usa `InMemoryThreadStore` para mantener el aislamiento entre runs de evaluacion
- el dashboard puede mostrar el historial de intervenciones de un hilo via `GET /threads/{thread_id}/history`

Gaps de diseno abiertos:

- la distincion experiment/live (HU-11) es la que determina cual store se usa; sin esa distincion, el store correcto no puede seleccionarse automaticamente
- la vista de historial en el dashboard no existe todavia; puede ser un panel dentro de `ModelDetail` o una vista separada por hilo

## HU-13. Persistir los resultados de experimentos en una base de datos consultable

Como investigadora
quiero que los resultados de cada ejecucion de experimento se guarden en una base de datos duradera y consultable
para poder filtrar, comparar y recuperar runs anteriores sin depender del sistema de ficheros local.

Estado actual:

- los resultados se guardan como ficheros JSON por par modelo/hilo bajo `docs/experiments/results/<run_id>/`
- el dashboard los lee via `artifacts.py`, que escanea el directorio y reconstruye la lista de runs
- no hay persistencia real: si el directorio desaparece o el servidor se mueve, el historial desaparece con el
- se introdujo una primera abstraccion `RunResultStore` (backend `filesystem`) para desacoplar lectura de runs del almacenamiento concreto
- el backend `mongo` ya existe en la interfaz y la API selecciona backend por configuracion (`run_results_backend`); los manifests se espejan al backend configurado cuando se lanzan/terminan runs

Descripcion:

- cada run de experimento escribe su resultado completo en una base de datos (candidato: MongoDB) en lugar de, o ademas de, los ficheros JSON actuales
- el dashboard consulta la base de datos para obtener la lista de runs y el detalle de cada uno via la API ya existente (`GET /runs`, `GET /runs/{run_id}`)
- la capa de acceso a datos se abstrae tras una interfaz intercambiable, de forma que el backend de ficheros puede coexistir como fallback durante la transicion
- los runs de experimento y los runs en vivo (HU-11) se distinguen en el esquema y son consultables por tipo
- el historial de intervenciones por hilo (HU-12, ADR 0007) es un store separado con su propia interfaz; no comparte esquema ni backend con los resultados de experimentos

Diferencia clave con HU-12:

- HU-12 / ADR 0007: historial operacional del facilitador por hilo — lo que el sistema hizo y cuando; escrito en runs en vivo, leido por el pipeline antes de cada ejecucion para respetar cooldown y escalada EMT
- HU-13: archivo de resultados de investigacion por run — la salida completa del pipeline por cada par modelo/hilo; escrito en experimentos, leido por el dashboard para inspeccion

Los dos stores son independientes y sirven propositos distintos. No comparten esquema.

Gaps de diseno abiertos:

- ADR pendiente (0034): documentar la eleccion de MongoDB vs. otras opciones (PostgreSQL + JSONB, TinyDB, DynamoDB) y las consecuencias de cada una
- durante la transicion, decidir si se migran los JSON existentes o solo se persisten runs futuros
- la interfaz de acceso a datos para resultados de experimentos todavia no existe en el codigo; `artifacts.py` accede directamente al sistema de ficheros

## Gaps y flujos complejos

## 1. Jerarquia de navegacion ambigua

Problema:

- `Run history`, `Run overview` y `Model detail` no estan modelados con la misma logica
- `Model detail` es un subnivel, pero se trata como una vista global independiente

Impacto:

- el usuario pierde el contexto
- no sabe si hizo drill-down, cambio de pantalla o cambio de modulo

## 2. No existe un camino de vuelta explicito

Problema:

- al entrar en `Model detail` no hay breadcrumb, boton `Back`, ni titulo contextual del run padre

Impacto:

- el flujo de inspeccion es de ida, no de ida y vuelta

## 3. Etiquetas ambiguas

Problema:

- `Run overview` esta bien como concepto
- `Run drill-down` no comunica que en realidad es `Model detail within run`
- `Models in this run` parece una lista informativa, pero tambien es un launcher de navegacion

Impacto:

- el usuario hace click sin anticipar el cambio de contexto

## 4. Click targets con consecuencias demasiado grandes

Problema:

- elementos que visualmente parecen chips o cajas informativas abren otra vista completa

Impacto:

- el dashboard se siente impredecible

## 5. Semantica pendiente en flujos reales

Problema:

- el historial sigue mezclando flujos reales (runs) con pendientes (live monitoring)
- para LMS aun no hay semantica final en la matriz cuando falta `expected_state`

Impacto:

- la UI ya funciona para evaluacion, pero no separa claramente experimento vs live

## 6. Sidebar modela vistas, no tareas

Problema:

- el sidebar mezcla navegacion principal con una vista intermedia de inspeccion
- no hace visible la ruta `History > Run > Model`

Impacto:

- falta una arquitectura de informacion estable

## 7. Cambio de run dentro de overview sin modelo mental claro

Problema:

- cambiar `Current run` dentro de `Run overview` es util
- pero no esta claro que cosas se preservan y cuales se resetean cuando cambia el run

Impacto:

- flujo correcto, pero semantica poco explicita

## Simplificacion propuesta

## Decision estructural recomendada

Separar claramente:

- navegacion principal
- navegacion de inspeccion

### Navegacion principal

Deberia contener solo:

- `Runs`
- `Trigger run`

### Navegacion de inspeccion dentro de Runs

Deberia ser jerarquica:

- `Run history`
- `Run overview`
- `Model detail`

Pero esta segunda capa no deberia vivir como item del sidebar. Deberia vivir como:

- breadcrumb
- boton `Back to run overview`
- encabezado contextual

## Flujo objetivo simplificado

### Flujo A. Inspeccion principal

1. Entrar en `Runs`
2. Elegir una ejecucion
3. Ver `Run overview`
4. Abrir un modelo concreto
5. Volver a `Run overview`
6. Cambiar de run o volver al historial

### Flujo B. Auditoria de trazas

1. Entrar en `Run overview`
2. Detectar una celda interesante en la matriz
3. Si hay traza, abrirla
4. Si no hay traza, seguir usando el dashboard sin perder informacion basica

### Flujo C. Preparacion de ejecucion

1. Ir a `Trigger run`
2. Configurar hilos y modelos
3. Lanzar ejecucion
4. Volver a `Runs`
5. Ver la nueva ejecucion en el historial

## Cambios prioritarios recomendados

## Prioridad 1. Arreglar la navegacion de inspeccion

- renombrar `Run drill-down` a `Model detail`
- agregar breadcrumb: `Run history / {run_name} / {model_name}`
- agregar accion local: `Back to run overview`
- mostrar el nombre del run actual dentro de `Model detail`

## Prioridad 2. Reducir clicks ambiguos

- convertir cajas informativas en elementos no navegables si no aportan una accion clara
- si un elemento abre otra vista, etiquetarlo como CTA explicita
- evitar que chips visuales se comporten como saltos de pantalla inesperados

## Prioridad 3. Alinear la vista de modelo con datos reales

- mantener `ModelDetail` centrado en datos reales de hilo (`thread_title`, contenido, comentarios)
- cerrar la semantica de presentacion para runs sin `expected_state` (LMS/live)

## Prioridad 4. Cerrar flujos faltantes

- la prioridad ya no es marcar mocks, sino cerrar los flujos faltantes: live runs y persistencia de resultados fuera del filesystem

## Preguntas de producto que conviene cerrar antes de seguir

- `Model detail` debe ser una pantalla completa, un panel lateral o una seccion expandida dentro de `Run overview`?
- la accion principal desde la trace matrix debe ser abrir traza, abrir detalle de modelo, o ambas?
- cambiar de run desde `Run overview` debe conservar el modelo abierto si existe uno seleccionado, o siempre volver al overview del nuevo run?

## Conclusiones

La interfaz ya expresa una intencion clara: usar el dashboard como
herramienta de inspeccion de ejecuciones. El problema principal no es
que falten demasiadas piezas, sino que la jerarquia de navegacion no
esta explicitada.

La simplificacion mas importante no es visual. Es estructural:

- el sidebar debe representar modulos principales
- la inspeccion de run/model debe representarse como jerarquia local
- los elementos clicables deben tener consecuencias previsibles

Con esto, el dashboard deberia sentirse menos como un conjunto de
vistas sueltas y mas como un flujo unico de inspeccion.