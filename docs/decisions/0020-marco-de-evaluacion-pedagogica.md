# ADR 0020: Marco de evaluación pedagógica de las respuestas

**Estado**: Propuesto (diseño pendiente de implementación)
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0013 (Evaluación de
respuesta), ADR 0014 (Infraestructura de evaluación)

## Descripción

El sistema dispone de dos niveles de validación de respuestas:

1. **Aserciones estructurales** (`assertions.py`): verifican que la respuesta
   cumple invariantes formales independientemente del contenido (texto no
   vacío, técnica conocida, confianza en rango válido, `post_to_thread`
   coherente con la técnica).
2. **Comprobaciones por reglas** en `RoleNode` (ADR 0013): detectan lenguaje
   evaluativo y técnica no especificada en tiempo de ejecución del pipeline.

Estos dos niveles son necesarios pero no suficientes para evaluar si una
respuesta es pedagógicamente adecuada. Una respuesta puede superar todas las
comprobaciones estructurales y seguir siendo inapropiada: la técnica puede
estar mal aplicada al contexto, el tono puede ser incorrecto, o el texto puede
no estar fundamentado en el hilo.

Esta decisión documenta el marco de evaluación pedagógica previsto para la
fase de evaluación de la tesis.

## Decisión

La evaluación pedagógica de las respuestas generadas seguirá tres capas
complementarias:

### Capa 1: Aserciones estructurales (ya implementada)

Verifica invariantes formales sobre la salida del pipeline. No depende del
contexto del hilo ni de criterios pedagógicos. Cubre:

- Respuesta no vacía; técnica en el repertorio conocido.
- Confianza en rango válido [0.0, 1.0].
- `instructor_escalation` implica `post_to_thread=False`.
- Ausencia de lenguaje evaluativo (regla en `RoleNode`).

Esta capa ya está implementada en `assertions.py` y `nodes.py`.

### Capa 2: LLM-as-judge (pendiente)

Un segundo modelo evalúa cada respuesta contra una rúbrica con criterios
pedagógicos. La rúbrica tiene seis dimensiones:

| Dimensión | Descripción |
|---|---|
| Adecuación al estado | La técnica elegida es apropiada para el estado del hilo detectado |
| Fidelidad a la técnica | El texto realiza lo que la técnica prescribe |
| No evaluativo | El texto no juzga ni califica contribuciones de los estudiantes |
| Fundamentación | El texto referencia contribuciones concretas del hilo, no es genérico |
| Alineación con la acción | El texto produce la acción anunciada en `action_category` |
| Tono | El registro es apropiado al contexto académico asíncrono |

El judge recibe: el hilo, el estado clasificado, la técnica seleccionada, y
el texto generado. Emite una puntuación por dimensión (1-5) y una justificación.

**Por qué LLM-as-judge**: escala a todos los pares modelo × hilo sin coste
de anotación humana. Zheng et al. (2023) muestran que GPT-4 como judge alcanza
alta concordancia con jueces humanos en evaluaciones de calidad de texto.
La limitación conocida (sesgo hacia respuestas largas y hacia el propio
estilo del modelo judge) se mitiga usando un modelo judge distinto del modelo
evaluado y controlando la longitud en la rúbrica.

### Capa 3: Anotación humana (pendiente, muestra reducida)

Anotación de 20-30 pares (hilo, respuesta) por expertos con criterios de
facilitación académica. Proporciona el estándar de referencia (*gold standard*)
contra el que calibrar el judge automático.

Protocolo:
- Dos anotadores independientes por caso.
- Rúbrica idéntica a la de la Capa 2.
- Kappa de Cohen para medir acuerdo inter-anotador.
- Los casos con kappa < 0.6 se revisan conjuntamente y se resuelven por
  consenso antes de incluirlos como referencia.

La muestra de 20-30 casos es suficiente para validar el judge automático,
no para conclusiones estadísticas sobre el sistema. Las conclusiones
estadísticas provienen de la Capa 2 a escala completa.

### Comparación con línea base

Los resultados del sistema se comparan con una línea base mínima: una
respuesta generada sin pipeline multi-agente, usando directamente el modelo
con un prompt simple de facilitación. Esto permite distinguir la contribución
del pipeline de la capacidad base del modelo.

## Relación con la evaluación actual

Los experimentos en `docs/experiments/results/` evalúan la **compatibilidad
del modelo con el pipeline** (¿completa el modelo los 6 hilos sin error?) y
la **coherencia de la clasificación** (¿asigna el modelo el estado esperado
al hilo?). No evalúan la calidad pedagógica de las respuestas generadas.

La evaluación pedagógica (este ADR) es una fase posterior, después de
confirmar la compatibilidad del modelo.

## Consecuencias

### Positivas

- La separación en tres capas permite ejecutarlas de forma incremental:
  la Capa 1 ya existe; la Capa 2 puede implementarse cuando los modelos
  estén validados; la Capa 3 requiere coordinación externa con anotadores.
- El LLM-as-judge escala sin coste adicional a todos los modelos y escenarios
  ya evaluados.
- La comparación con línea base proporciona una métrica relativa que no
  depende de un estándar absoluto de calidad pedagógica.

### Negativas

- El LLM-as-judge introduce un sesgo del modelo judge. Un modelo judge que
  favorezca respuestas largas o un estilo particular puede puntuar de forma
  sistemáticamente sesgada.
- La anotación humana es costosa y requiere anotadores con conocimiento de
  facilitación académica. Encontrar dos anotadores con ese perfil es una
  restricción práctica del PoC.
- La rúbrica de seis dimensiones es una propuesta, no un instrumento validado.
  Su fiabilidad como medida de calidad pedagógica no está demostrada para
  este sistema.

### Cuestiones abiertas

- ¿Qué modelo se usa como judge? Debe ser distinto del modelo evaluado y
  suficientemente capaz para evaluar texto en inglés con criterios pedagógicos.
- ¿Qué muestra de pares (hilo, respuesta) se selecciona para la anotación
  humana? ¿Solo los casos exitosos o también los que el judge automático
  puntúa bajo?
- ¿Cómo se reportan los resultados en la tesis: puntuación media por
  dimensión, puntuación agregada, o comparación cualitativa por escenario?
- ¿Debe la evaluación incluir comparación entre modos (PromptedOutput vs.
  tool-calling) además de comparación entre modelos?

## Referencias

- Kim, J., et al. (2024). Prometheus: Inducing fine-grained evaluation
  capability in language models. *ICLR 2024*.
- Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval:
  NLG evaluation using GPT-4 with better human alignment. *EMNLP 2023*.
- Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023). Judging LLM-as-a-judge
  with MT-bench and chatbot arena. *NeurIPS 2023*.
- Rovai, A. P. (2007). Facilitating online discussions effectively. *The
  Internet and Higher Education*, 10(1), 77-88.
