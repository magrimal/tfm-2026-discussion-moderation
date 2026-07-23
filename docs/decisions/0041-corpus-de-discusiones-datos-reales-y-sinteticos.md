# DDA-0041: Corpus de discusiones académicas con datos históricos y escenarios sintéticos

## Estado

Aceptado, con trazabilidad revisada el 24 de julio de 2026.

## Contexto

El pipeline necesita discusiones con dinámicas distintas para observar la
clasificación, la decisión de intervenir y la respuesta generada. Un único tipo
de hilo no permite recorrer las rutas de silencio, actividad, estancamiento,
conflicto, convergencia, desvío temático o participación desigual.

El repositorio contiene dos clases de entrada:

- escenarios sintéticos definidos en
  `discussion_moderation/evals/fixtures/threads.py`;
- seis discusiones históricas anonimizadas conservadas en
  `docs/threads/real/`.

El inventario exacto empleado en las ejecuciones principales se mantiene en
`docs/experiments/thread-corpus.md`.

## Decisión

Las comparaciones utilizan ambos tipos de entrada, pero no les asignan el mismo
valor de referencia.

Los escenarios sintéticos se diseñan para recorrer una situación concreta y
pueden declarar un estado esperado. Los hilos históricos aportan lenguaje y
dinámicas que no fueron escritos para el experimento, pero sus nombres de
patrón (`real_dominated`, `real_formulaic`, etc.) representan la razón de su
selección, no una etiqueta pedagógica validada por anotadores independientes.

### Extracción de los hilos históricos

El script `scripts/extract_mooc_threads.py` reconstruye hilos a partir de un
archivo NDJSON llamado `filtered_forum_data_v2.mongo`. Enlaza eventos
`edx.forum.thread.created` y `edx.forum.comment.created`, conserva candidatos
con al menos tres comentarios y un mensaje inicial de más de cien caracteres,
y sustituye los nombres de usuario por identificadores estables
(`student1`, `student2`, etc.).

El resultado intermedio versionado,
`scripts/mooc_thread_candidates.json`, contiene 480 candidatos. Los seis casos
curados se copiaron después a `docs/threads/real/`. Los metadatos del resultado
intermedio muestran que no proceden todos de una única edición:

| Clave | Título | Curso registrado |
|---|---|---|
| `real_dominated` | Error in the week1 exam. | `course-v1:UC3Mx+IT.1.1x+3T2015` |
| `real_explicit_distress` | can someone explain how we got 59 ? | `course-v1:UC3Mx+IT.1.1x+3T2016` |
| `real_formulaic` | Knowing vs Doing | `course-v1:UC3Mx+IT.1.2x+2016T2` |
| `real_hostile_then_silent` | Extension of deadline for “Peer Assessment 1: reviews” until 16 June (11:59 am UTC) | `UC3Mx/IT.1.1x/1T2015` |
| `real_integration_phase` | Test is just too difficult - no link from tutorial to test. | `UC3Mx/IT.1.1x/1T2015` |
| `real_overt_attack` | @ Stuff - peer assessment | `UC3Mx/IT.1.1x/1T2015` |

### Límite de procedencia

La primera versión de este ADR atribuía `filtered_forum_data_v2.mongo` a un
registro de Zenodo y citaba el DOI `10.5281/zenodo.4558788`. Esa atribución no
se pudo verificar: el DOI no proporciona un registro localizable y el
repositorio no conserva el archivo de origen, su URL de descarga, un checksum
ni documentación de licencia. También era incorrecto describir los seis hilos
como procedentes exclusivamente de `UC3Mx/IT.1.1x` en una única edición.

Por tanto:

- se retira el DOI de la memoria y de la bibliografía;
- se conserva como evidencia verificable el proceso desde el archivo NDJSON
  local hasta los 480 candidatos y los seis hilos anonimizados;
- no se afirma que un tercero pueda reconstruir el corpus desde una fuente
  pública hasta que se identifique y verifique la procedencia original.

## Consecuencias

### Positivas

- Las entradas sintéticas hacen reproducibles situaciones diseñadas de
  antemano.
- Los hilos históricos incorporan lenguaje que no fue redactado para la
  evaluación.
- El inventario separa la clave experimental, el título y el origen de cada
  caso.
- La anonimización se realiza antes de escribir el archivo de candidatos.

### Negativas

- La curaduría manual introduce sesgo de selección.
- Los nombres de patrón de los hilos históricos no constituyen una anotación
  experta.
- La procedencia externa del volcado original queda sin verificar.
- Sin el archivo original y su licencia no puede afirmarse reproducibilidad
  completa desde la fuente primaria.

## Alternativas consideradas

- **Usar solo escenarios sintéticos**: descartado porque elimina el lenguaje
  histórico no escrito para el experimento.
- **Usar los nombres de patrón como verdad de referencia**: descartado porque
  no hubo anotación independiente.
- **Mantener la atribución bibliográfica sin verificar**: descartado durante
  la revisión de trazabilidad de julio de 2026.
