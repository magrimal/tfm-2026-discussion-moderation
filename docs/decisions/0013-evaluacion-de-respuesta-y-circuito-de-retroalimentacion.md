# ADR 0013: Evaluación de respuesta y circuito de retroalimentación al orquestador

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0003 (Modelo de intervención), ADR 0005 (Arquitectura
multi-agente), ADR 0007 (Historial de intervenciones), ADR 0009 (Estructura
de prompts)

## Descripción

El pipeline genera una respuesta en el nodo `RoleNode`, pero nada garantiza
que esa respuesta cumpla los invariantes del sistema antes de ser entregada.
El más crítico: el sistema facilita, no evalúa. Una respuesta que contenga
lenguaje evaluativo ("correcto", "incorrecto", "aprobado") violaría la
premisa central de la tesis y podría dañar la dinámica del hilo.

Además, el `OrchestratorNode` selecciona el rol y la técnica sin ver la
respuesta resultante. Si la respuesta no es viable — vacía, sin técnica
especificada, o con lenguaje evaluativo — el error silencioso llega al
usuario final sin oportunidad de corrección interna.

Esta decisión introduce un mecanismo de validación post-generación y un
circuito de retroalimentación que permite al sistema corregirse sin
intervención externa.

## Decisión

Añadir una fase de evaluación por reglas en `RoleNode`, con retroalimentación
al `OrchestratorNode` en caso de fallo, y condicionar el registro en
`ThreadHistoryStore` al resultado de esa evaluación.

### Comprobaciones por reglas

La función `_run_response_rule_checks()` verifica tres condiciones sobre
la respuesta generada:

1. **Respuesta no vacía**: el texto de la respuesta no puede estar en blanco.
2. **Técnica especificada**: el campo `technique_used` debe ser no vacío.
3. **Ausencia de lenguaje evaluativo**: el texto no puede contener frases
   como `"correcto"`, `"incorrecto"`, `"mark"`, `"pass or fail"`, etc. Este
   invariante refleja directamente el principio del sistema: facilitar, no
   evaluar ni calificar (ADR 0002, ADR 0003).

Las comprobaciones son deterministas y no requieren llamada adicional al
modelo. Se ejecutan solo si `response_eval_enabled` está activo en
`Settings`; si está desactivado, el sistema se comporta como si todas las
comprobaciones pasaran.

### Circuito de retroalimentación

Si alguna comprobación falla y no se ha alcanzado el límite de reintentos
(`orchestrator_attempts < 1 + max_orchestrator_retries`), el nodo:

1. Añade los problemas detectados a `ctx.state.eval_feedback`.
2. Devuelve `OrchestratorNode()` en lugar de `End(...)`.

El `OrchestratorNode` recibe el feedback en su contexto y puede seleccionar
un rol o técnica diferente en el siguiente intento. El número máximo de
reintentos es configurable mediante `max_orchestrator_retries` en `Settings`.

Si se agotan los reintentos, la respuesta se entrega tal cual: el sistema
no bloquea indefinidamente ni devuelve vacío al usuario.

```
RoleNode
  ↓ genera respuesta
  ↓ _run_response_rule_checks()
  ├── pasa → registra en historial → End(PipelineResult)
  └── falla y hay reintentos → OrchestratorNode (con feedback)
        ↓
      RoleNode (siguiente intento)
```

### Temporización del registro en el historial

El registro en `ThreadHistoryStore` ocurre **después** de que las
comprobaciones pasen (o después del último reintento si `response_eval_enabled`
está desactivado). En consecuencia:

- Los intentos fallidos **no se registran**. El historial solo contiene
  intervenciones que superaron la validación.
- Si `history_store` es `None`, no se registra nada y el pipeline continúa
  sin error. El store es opcional.

Esta semántica es deliberada: registrar intentos fallidos contaminaría el
historial que usa el clasificador para comprobar el cooldown y que el rol
intelectual usa para la escalada EMT (ADR 0007). Un intento fallido no
constituye una intervención real.

## Consecuencias

### Positivas

- El invariante "facilitar, no evaluar" se comprueba de forma determinista
  antes de cada entrega, sin depender de que el modelo lo respete siempre.
- El circuito de retroalimentación permite corregir fallos de rol o técnica
  sin intervención externa y sin entregar una respuesta inválida.
- El historial refleja solo intervenciones reales, lo que mantiene la
  fiabilidad de la guardia de cooldown y la escalada EMT.
- El coste computacional es bajo: las comprobaciones son locales y el número
  de reintentos está acotado.

### Negativas

- Las comprobaciones por reglas son necesarias pero no suficientes. No
  detectan respuestas que sean válidas sintácticamente pero inadecuadas
  pedagógicamente (tono incorrecto, técnica mal aplicada, respuesta
  irrelevante para el hilo).
- Si se agotan los reintentos, la respuesta inválida se entrega igualmente.
  El sistema no tiene mecanismo de fallback más allá del límite de reintentos.
- La lista de frases evaluativas es estática y en inglés. Un modelo que use
  equivalentes en otro idioma o paráfrasis no activará la comprobación.

### Cuestiones abiertas

- ¿Conviene añadir una comprobación semántica mediante LLM-as-judge para los
  casos que las reglas no detectan? ADR 0005 menciona `ClassifierEval` y
  `ResponseEval` como nodos opcionales; este ADR implementa el segundo con
  reglas, pero la versión LLM queda pendiente.
- ¿Debe el feedback al orquestador incluir la respuesta fallida además de los
  problemas detectados, para que el orquestador pueda razonar sobre por qué
  falló y no solo sobre qué falló?
- ¿Cuál es el valor correcto de `max_orchestrator_retries` por defecto? El
  valor actual (configurable, sin valor por defecto documentado en el código)
  no está calibrado empíricamente.

## Alternativas consideradas

- **LLM-as-judge en lugar de reglas**: un segundo modelo evalúa la respuesta
  contra una rúbrica. Más expresivo, pero añade latencia, coste y un punto
  de fallo adicional. Descartado como primera capa; puede complementar las
  reglas en una capa posterior.
- **Fallo sin reintento**: si la respuesta no supera las comprobaciones, el
  pipeline termina sin entregar nada. Descartado porque aumenta la tasa de
  fallos visibles al usuario y no aprovecha que el modelo puede producir una
  respuesta válida en un segundo intento.
- **Sin validación post-generación**: entregar la respuesta directamente.
  Descartado porque el invariante "no evaluar" es crítico para la validez de
  la tesis y no puede depender solo del prompt.
- **Validación en el prompt del rol**: añadir al prompt una instrucción
  explícita para no usar lenguaje evaluativo. Esta instrucción ya existe
  (ADR 0009), pero no es suficiente por sí sola: los modelos pueden ignorarla
  o no reconocer las frases concretas como evaluativas.

## Referencias

- Coppola, N. W., Hiltz, S. R., & Rotter, N. G. (2002). Becoming a virtual
  professor: Pedagogical roles and asynchronous learning networks. *Journal
  of Management Information Systems*, 18(4), 169-189.
- Garrison, D. R., Anderson, T., & Archer, W. (2000). Critical inquiry in a
  text-based environment: Computer conferencing in higher education.
  *The Internet and Higher Education*, 2(2-3), 87-105.
- Koedinger, K. R., & Aleven, V. (2007). Exploring the assistance dilemma
  in experiments with cognitive tutors. *Educational Psychology Review*,
  19(3), 239-264.
