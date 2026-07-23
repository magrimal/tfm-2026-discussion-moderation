# ADR 0020: Marco de evaluación pedagógica de las respuestas

**Estado**: Aceptado (ejecución asistida pendiente)
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

### Capa 2: LLM-as-judge

GPT-5.6 Sol, ejecutado mediante Codex, evalúa cada respuesta contra una rúbrica
derivada de la literatura sobre facilitación de discusiones. La evaluación es
individual: el juez recibe una intervención cada vez y no conoce qué modelo la
generó. La rúbrica tiene ocho dimensiones:

| Dimensión | Descripción |
|---|---|
| Relevancia y fundamentación | Responde al hilo, usa correctamente sus aportes y no inventa participantes, hechos o fuentes |
| Necesidad y momento | La intervención es necesaria, oportuna y proporcional a la dinámica observable |
| Activación cognitiva | Promueve elaboración, evidencia, conexión, síntesis o avance en la indagación |
| Apertura dialógica | Devuelve la conversación a los participantes sin sustituirla por una explicación cerrada |
| Seguridad social e inclusión | Mantiene un clima respetuoso, despersonaliza el desacuerdo y abre espacio a distintas voces |
| Andamiaje y siguiente paso | Ofrece una pregunta, pista o acción concreta que permite continuar sin resolver la tarea |
| Fidelidad a la función | Aplica la técnica y el rol declarados de forma apropiada y coherente con la acción |
| Claridad y carga de respuesta | Es comprensible, proporcionada y fácil de contestar sin acumular instrucciones innecesarias |

El judge recibe el hilo, el estado clasificado, el rol, la técnica, la
categoría de acción, `post_to_thread` y el texto generado. Emite una puntuación
por dimensión (1-5), una justificación breve y tres comprobaciones críticas:

- alucinación sobre el contenido o los participantes del hilo;
- calificación, juicio de corrección o atribución de capacidad al alumnado,
  invariante propio de este artefacto;
- moderación insegura o publicación contraria a la ruta de escalado.

Estas comprobaciones no se compensan mediante la media. Un caso que active
cualquiera de ellas queda marcado para revisión aunque obtenga puntuaciones
altas en otras dimensiones. El lenguaje no evaluativo se presenta como una
restricción de diseño del sistema, no como una regla universal de la
facilitación docente: la taxonomía de Blignaut y Trollip (2003), por ejemplo,
incluye intervenciones correctivas. El reconocimiento específico y respetuoso
de una contribución no activa esta comprobación, porque forma parte de las
funciones afectiva y social del propio repertorio.

Las notas internas de escalado (`post_to_thread=false`) no reciben puntuación
en activación cognitiva ni apertura dialógica. Esas dimensiones describen
efectos buscados en mensajes dirigidos al alumnado y no corresponden a una
nota cuyo destinatario es el instructor. La media se calcula solo sobre las
dimensiones aplicables, evitando penalizar sistemáticamente al rol moderador.

El modelo judge se identifica en los artefactos como
`codex:gpt-5.6-sol`. No forma parte del conjunto de modelos evaluados, por
lo que no juzga respuestas propias. La ejecución se realiza de forma asistida
en una sesión de Codex, no mediante el proveedor configurado en la aplicación.
Para conservar la trazabilidad se guardan junto a los resultados la versión
del modelo, la fecha, la rúbrica, el prompt completo y la salida estructurada
de cada caso. Esta decisión permite usar el modelo disponible en el entorno de
trabajo, pero no convierte la evaluación en una prueba determinista: una nueva
ejecución puede producir puntuaciones distintas.

**Por qué LLM-as-judge**: permite aplicar una rúbrica común a todos los pares
modelo × hilo con menos anotación humana. G-Eval muestra que las instrucciones
de evaluación y la salida estructurada mejoran la correspondencia con juicios
humanos (Liu et al., 2023); Prometheus muestra la utilidad de descriptores
explícitos por nivel y material de referencia (Kim et al., 2024). El método
no elimina el coste ni garantiza
validez. Los jueces pueden favorecer respuestas largas, estilos determinados
o salidas de su misma familia (Zheng et al., 2023). Para reducir estos
sesgos se oculta el modelo evaluado, no se premia la extensión y se conserva
la salida por dimensión.

### Alcance: evaluación ex ante y efecto ex post

La Capa 2 estima la adecuación de una intervención antes de observar sus
efectos. No permite afirmar que aumentó la participación, equilibró las voces,
redujo el conflicto o hizo avanzar la presencia cognitiva. Esos efectos
requieren mensajes posteriores a la intervención y un diseño longitudinal o
comparativo. Por tanto, la evaluación ex post queda fuera de la evidencia
obtenida con los artefactos actuales.

### Capa 3: Anotación humana (pendiente, muestra reducida)

Anotación de 20-30 pares (hilo, respuesta) por expertos con criterios de
facilitación académica. Proporciona el estándar de referencia (*gold standard*)
contra el que calibrar el judge automático.

Protocolo:
- Dos anotadores independientes por caso.
- Rúbrica idéntica a la de la Capa 2.
- Kappa ponderada de Cohen por dimensión ordinal e ICC para la puntuación
  agregada.
- Los casos con kappa < 0.6 se revisan conjuntamente y se resuelven por
  consenso antes de incluirlos como referencia.

La muestra de 20-30 casos permite una calibración exploratoria del judge, no
una validación general del instrumento ni conclusiones estadísticas sobre
efectividad pedagógica.

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
  la Capa 1 ya existe; la Capa 2 puede aplicarse a los artefactos guardados
  una vez validados los modelos; la Capa 3 requiere coordinación externa con
  anotadores.
- El LLM-as-judge reduce el trabajo de anotación necesario para cubrir todos
  los modelos y escenarios ya evaluados, aunque conserva costes de ejecución,
  calibración y revisión.
- La comparación con línea base proporciona una métrica relativa que no
  depende de un estándar absoluto de calidad pedagógica.

### Negativas

- El LLM-as-judge introduce un sesgo del modelo judge. Un modelo judge que
  favorezca respuestas largas o un estilo particular puede puntuar de forma
  sistemáticamente sesgada.
- La anotación humana es costosa y requiere anotadores con conocimiento de
  facilitación académica. Encontrar dos anotadores con ese perfil es una
  restricción práctica del PoC.
- La rúbrica de ocho dimensiones es una propuesta, no un instrumento validado.
  Su fiabilidad como medida de calidad pedagógica no está demostrada para
  este sistema.

### Cuestiones abiertas

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
- Anderson, T., Rourke, L., Garrison, D. R., & Archer, W. (2001). Assessing
  teaching presence in a computer conferencing context. *Journal of
  Asynchronous Learning Networks*, 5(2).
- Hattie, J., & Timperley, H. (2007). The power of feedback. *Review of
  Educational Research*, 77(1), 81-112.
- Blignaut, S., & Trollip, S. R. (2003). Developing a taxonomy of faculty
  participation in asynchronous learning environments. *Computers &
  Education*, 41(2), 149-172.
