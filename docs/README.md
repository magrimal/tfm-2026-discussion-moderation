# Documentación del TFM

Este directorio contiene la documentación asociada al Trabajo Fin de Máster (TFM).

Aquí se incluyen los documentos de contexto, planificación, diseño, evaluación y redacción de la memoria, a medida que el proyecto avanza.

El contenido de este directorio puede evolucionar durante el desarrollo del TFM y no necesariamente refleja un estado final en todo momento.

## Índice

- `TODO.md` — lo que falta: bugs abiertos, huecos de test, cobertura
  modelo × fixture pendiente. Solo lo pendiente, no un registro de lo
  ya hecho (eso está en `git log` y en el Status de cada fila de
  `experiments/test-sheets/`)
- `glossary.md` — términos, acrónimos y conceptos del sistema
- `decisions/` — ADRs (registros de decisión de arquitectura)
- `agents/` — documentación de los agentes del pipeline
- `pipeline.md` — mapa del pipeline de facilitación
- `experiments.md` — registro de experimentos y resultados
- `experiments/research-questions.md` — preguntas de investigación para
  el capítulo de evaluación, fundamentadas en ADRs y hallazgos propios
  (no en literatura de otros sistemas)
- `experiments/test-sheets/all-tests.csv` — hoja única de ejecución de
  tests, formato estándar de QA (Section, Requirement, Test Setup, Test
  Description, Expected Result, Actual Result, Pass/Fail, Environment,
  Comments). `Section` reemplaza los CSVs separados de antes (Pipeline
  Correctness, Dashboard Functionality, Reliability & Security,
  Evaluation Framework, Research Questions). Reseteada por completo
  el 2026-07-20 tras limpiar el historial de runs en idril/EC2 — toda
  fila parte de `Not started`, incluso donde hay evidencia histórica,
  porque la aplicación ha cambiado desde que se generó esa evidencia.
- `discussion_api_v1.md` — esquema de hilos/comentarios de Open edX Discussion API v1
- `forum_api.md` — referencia de endpoints internos del servicio forum usado por el backend
