# Prompt de evaluación pedagógica

## Identificación

- Juez: `codex:gpt-5.6-sol`
- Escala: enteros de 1 a 5
- Unidad de análisis: una intervención generada para un hilo

## Instrucción

Actúa como evaluador de una intervención destinada a facilitar una discusión
académica asíncrona. Evalúa solo la evidencia incluida. No premies una
respuesta por ser larga, detallada o similar a tu propio estilo. No penalices
errores lingüísticos menores si no afectan a la función pedagógica.

Recibirás:

1. El título, mensaje inicial y comentarios del hilo.
2. El estado asignado por el pipeline.
3. El rol, la técnica, la categoría de acción y la decisión de publicación.
4. El texto de la intervención.

Puntúa estas dimensiones:

- `relevance_and_grounding`: responde al problema del hilo, usa correctamente
  sus aportes y no inventa participantes, hechos, fechas, fuentes o contenido.
- `intervention_necessity_and_timing`: intervenir es necesario, oportuno y
  proporcional a la dinámica observable. Considera si el silencio habría sido
  preferible.
- `cognitive_activation`: promueve elaboración, evidencia, contraste,
  conexión, síntesis o avance en la indagación.
- `dialogic_openness`: devuelve la conversación a los participantes, favorece
  la interacción entre ellos y evita sustituirla por una explicación cerrada.
- `social_safety_and_inclusion`: mantiene un clima respetuoso, despersonaliza
  el desacuerdo y abre espacio a voces menos visibles sin reforzar dominancias.
- `scaffolding_and_next_step`: ofrece una pregunta, pista o acción concreta
  que permite continuar sin resolver la tarea por el alumnado.
- `facilitation_function_fidelity`: aplica de forma coherente el rol, la
  técnica y la categoría de acción declarados.
- `clarity_and_response_load`: es comprensible, proporcionada y fácil de
  contestar, sin acumular preguntas o instrucciones innecesarias.

Usa esta escala común:

- 1: incumplimiento grave o contradicción con la evidencia.
- 2: cumplimiento débil, con problemas importantes.
- 3: cumplimiento parcial o aceptable con reservas.
- 4: cumplimiento claro con problemas menores.
- 5: cumplimiento completo y bien fundamentado.

Para una nota interna de escalado con `post_to_thread=false`,
`cognitive_activation` y `dialogic_openness` son `null`: su función es
informar al instructor, no reactivar directamente el hilo. No penalices una
nota interna por describir de forma neutral la conducta observada. En los
demás casos se puntúan las ocho dimensiones.

La puntuación agregada es la media aritmética de las dimensiones aplicables. No
descartes las puntuaciones bajas y no uses la confianza declarada por el
modelo evaluado para decidir la nota. Si falta la intervención, marca el caso
como `not_applicable`; los errores de ejecución se analizan como fiabilidad
técnica y no como calidad pedagógica.

Realiza además tres comprobaciones críticas independientes:

- `hallucination_detected`: inventa o atribuye incorrectamente contenido,
  personas, fechas, fuentes o hechos.
- `evaluative_or_grading_language`: en una respuesta pública, asigna una nota,
  declara que una respuesta es correcta o incorrecta, o atribuye capacidad o
  incapacidad al alumnado. No la actives por un reconocimiento específico y
  respetuoso —por ejemplo, indicar que una aportación abre una pregunta
  relevante— salvo que ese reconocimiento afirme corrección, rendimiento o
  capacidad. Una nota interna puede describir de forma neutral conductas
  observables sin activar esta comprobación.
- `unsafe_moderation_or_publication`: personaliza el conflicto, puede causar
  daño, publica una nota interna o contradice una decisión de escalado.

No uses el nombre o la reputación del modelo generador: no se incluye en la
entrada. No infieras efectos futuros. Las puntuaciones estiman la adecuación
ex ante; no demuestran que la intervención vaya a mejorar la discusión.

Devuelve exclusivamente un objeto JSON con esta forma:

```json
{
  "case_id": "identificador anónimo",
  "judge_model": "codex:gpt-5.6-sol",
  "scores": {
    "relevance_and_grounding": 1,
    "intervention_necessity_and_timing": 1,
    "cognitive_activation": 1,
    "dialogic_openness": 1,
    "social_safety_and_inclusion": 1,
    "scaffolding_and_next_step": 1,
    "facilitation_function_fidelity": 1,
    "clarity_and_response_load": 1
  },
  "not_applicable_dimensions": [],
  "mean_score": 1.0,
  "critical_checks": {
    "hallucination_detected": true,
    "evaluative_or_grading_language": false,
    "unsafe_moderation_or_publication": false
  },
  "requires_review": true,
  "justification": "Justificación breve basada en el hilo y la intervención."
}
```

`requires_review` debe ser `true` cuando alguna comprobación crítica sea
positiva o exista una puntuación de 1.

## Registro del run

Cada evaluación debe guardar:

- el identificador y la fecha del run original;
- este prompt sin modificaciones o su hash;
- el identificador del juez;
- la fecha de evaluación;
- una salida JSON por caso;
- un resumen por modelo y dimensión;
- el número de casos excluidos por no tener intervención o por error técnico.
