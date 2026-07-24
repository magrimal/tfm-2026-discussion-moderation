# DDA-0041: Corpus de discusiones académicas con datos históricos y escenarios sintéticos

## Estado

Aceptado, con procedencia verificada el 24 de julio de 2026.

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

El archivo de origen es `filtered_forum_data_v2.mongo`, publicado por Carlos
Alario-Hoyos en el conjunto *Dataset MOOC Forum edX*:

- DOI de la versión empleada: <https://doi.org/10.5281/zenodo.5115573>;
- DOI del conjunto, válido para todas sus versiones:
  <https://doi.org/10.5281/zenodo.5115572>;
- fecha de publicación: 20 de julio de 2021;
- licencia declarada: Creative Commons Attribution 4.0;
- tamaño del archivo: 556.388.439 bytes;
- suma publicada por Zenodo:
  `md5:7b6ea993c621e0b5716f8c9d09dd8b5c`.

La descripción del registro indica que el archivo reúne información de los
foros de tres MOOC de programación, en español e inglés y a lo largo de varias
ediciones. Esto concuerda con los identificadores de curso conservados en los
seis casos seleccionados.

El script `scripts/extract_mooc_threads.py` procesa el archivo como NDJSON.
Enlaza eventos
`edx.forum.thread.created` y `edx.forum.comment.created`, conserva candidatos
con al menos tres comentarios y un mensaje inicial de más de cien caracteres,
y aplica una heurística de idioma basada en la proporción de caracteres ASCII.
Antes de escribir los resultados, sustituye los nombres de usuario por
identificadores estables (`student1`, `student2`, etc.).

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

### Cadena de trazabilidad

La procedencia puede seguirse mediante estos artefactos:

1. Zenodo conserva el archivo de origen, sus metadatos, su licencia y su suma
   de comprobación.
2. `scripts/extract_mooc_threads.py` documenta los filtros y la transformación.
3. `scripts/mooc_thread_candidates.json` conserva los 480 candidatos obtenidos.
4. `docs/threads/real/` contiene los seis casos seleccionados y anonimizados.
5. `docs/experiments/thread-corpus.md` registra las claves utilizadas en las
   ejecuciones.

Para repetir la extracción se descarga la versión citada, se comprueba su MD5
y se ejecuta:

```text
python3 scripts/extract_mooc_threads.py \
  --input filtered_forum_data_v2.mongo \
  --output scripts/mooc_thread_candidates.json
```

La selección final de seis casos fue manual. El título, el identificador del
hilo, el curso de origen, la categoría, las fechas y el contenido permiten
localizar cada caso dentro del resultado intermedio.

## Consecuencias

### Positivas

- Las entradas sintéticas hacen reproducibles situaciones diseñadas de
  antemano.
- Los hilos históricos incorporan lenguaje que no fue redactado para la
  evaluación.
- El inventario separa la clave experimental, el título y el origen de cada
  caso.
- La anonimización se realiza antes de escribir el archivo de candidatos.
- El DOI de versión y la suma de comprobación fijan el archivo de partida.

### Negativas

- La curaduría manual introduce sesgo de selección.
- Los nombres de patrón de los hilos históricos no constituyen una anotación
  experta.
- La heurística de idioma basada en caracteres ASCII solo aproxima la
  detección de textos en inglés.

## Alternativas consideradas

- **Usar solo escenarios sintéticos**: descartado porque elimina el lenguaje
  histórico no escrito para el experimento.
- **Usar los nombres de patrón como verdad de referencia**: descartado porque
  no hubo anotación independiente.
- **Describir el corpus como una sola edición de `UC3Mx/IT.1.1x`**: descartado
  porque los metadatos de los casos muestran varias ediciones y también el
  curso `UC3Mx/IT.1.2x`.
