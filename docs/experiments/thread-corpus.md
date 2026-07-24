# Corpus de hilos de las ejecuciones principales

Este documento enumera las 18 entradas utilizadas en las comparaciones de
Idril y EC2 del 23 de julio de 2026. La fuente ejecutable es
`ALL_THREADS`, en
`discussion_moderation/evals/fixtures/threads.py`.

## Escenarios sintéticos

| Clave | Título |
|---|---|
| `new` | Privacy implications of large language models |
| `active` | Algorithmic bias in hiring systems |
| `stalled` | Open source licensing in AI research |
| `conflictive` | Regulation of AI systems in the EU |
| `convergent` | Explainability vs. accuracy tradeoff |
| `off_topic` | Environmental impact of training large models |
| `shallow_discourse` | Transparency requirements for AI decision systems |
| `dominated` | Federated learning as a privacy-preserving approach |
| `declining_vs_never_posted` | Fairness tradeoffs in credit scoring models |
| `preventive_social_activation` | Should model cards be legally mandated? |
| `ambiguous_signals` | Interpretability methods for tabular models |
| `dual_state_stalled_off_topic` | Data minimization principles in ML pipelines |

Estos escenarios están definidos en código y usan
`source="synthetic"`. El estado esperado, cuando existe, es una propiedad del
diseño del escenario y no una anotación obtenida de actividad estudiantil.

## Hilos históricos anonimizados

Los casos proceden de *Dataset MOOC Forum edX*, versión
<https://doi.org/10.5281/zenodo.5115573>, publicado por Carlos
Alario-Hoyos con licencia CC BY 4.0. El registro contiene el archivo
`filtered_forum_data_v2.mongo`; el procedimiento de extracción, los filtros,
la suma de comprobación del archivo de origen y la selección de los casos se
documentan en DDA-0041.

| Clave | Título | Archivo |
|---|---|---|
| `real_dominated` | Error in the week1 exam. | `docs/threads/real/dominated.json` |
| `real_explicit_distress` | can someone explain how we got 59 ? | `docs/threads/real/explicit_distress.json` |
| `real_formulaic` | Knowing vs Doing | `docs/threads/real/formulaic.json` |
| `real_hostile_then_silent` | Extension of deadline for “Peer Assessment 1: reviews” until 16 June (11:59 am UTC) | `docs/threads/real/hostile_then_silent.json` |
| `real_integration_phase` | Test is just too difficult - no link from tutorial to test. | `docs/threads/real/integration_phase.json` |
| `real_overt_attack` | @ Stuff - peer assessment | `docs/threads/real/overt_attack.json` |

Las claves describen el patrón por el que cada hilo fue seleccionado. No son
etiquetas pedagógicas validadas.

## Relación con los artefactos

Los manifiestos preservan `thread_key` y `thread_title` para cada combinación
de modelo e hilo:

- Idril:
  `docs/experiments/results-s3/idril/2026-07-23T11-51-18-threads-4-models/`;
- EC2:
  `docs/experiments/results-s3/ec2/2026-07-23T14-26-all-sample-threads-claude-gpt-deepseek-2/`.

Las entradas sometidas al LLM-as-judge conservan las mismas claves en
`docs/experiments/judge-runs/2026-07-23-main-comparison/`.
