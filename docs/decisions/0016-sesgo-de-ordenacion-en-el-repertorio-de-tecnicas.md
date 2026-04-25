# ADR 0016: Sesgo de ordenación en el repertorio de técnicas

**Estado**: Propuesto (pendiente de mitigación)
**Fecha**: 2026-04-26
**Depende de**: ADR 0002 (Repertorio de técnicas), ADR 0004 (Roles de
facilitación), ADR 0005 (Arquitectura multi-agente)

## Descripción

Los agentes de rol recuperan el repertorio de técnicas mediante la herramienta
`retrieve_techniques`, que devuelve la lista completa de técnicas disponibles
(`TECHNIQUES`) en un orden fijo:

```
TECHNIQUES = (
    ORGANIZATIONAL_TECHNIQUES    # 5 técnicas
    + INTELLECTUAL_TECHNIQUES    # 8 técnicas
    + SOCIAL_TECHNIQUES          # 5 técnicas
    + AFFECTIVE_TECHNIQUES       # 5 técnicas
    + MODERATOR_TECHNIQUES       # 7 técnicas
)
```

Los LLMs exhiben sesgo de posición primaria (*primacy bias*) en listas largas:
tienden a seleccionar opciones que aparecen antes, especialmente cuando el
contexto de elección es largo. Con 30 técnicas en orden fijo, los agentes
de rol social y afectivo deben leer 13 técnicas de otros roles antes de
llegar a las propias. Esto puede sesgar sistemáticamente la selección hacia
técnicas organizacionales e intelectuales, independientemente del rol activo.

Esta decisión documenta el sesgo conocido, su origen, y el estado actual de
la mitigación.

## Estado actual

`get_techniques()` devuelve `list(TECHNIQUES)` sin filtrar por rol ni por
estado. El parámetro `state` de la función está reservado para filtrado futuro
y actualmente no se usa:

```python
def get_techniques(state: DiscussionState | None = None) -> list[Technique]:
    # state: Reserved for future state-based filtering. Currently unused.
    return list(TECHNIQUES)
```

Existe `STATE_ROLE_RELEVANCE`, un diccionario que mapea cada estado a los
roles más relevantes para ese estado:

```python
STATE_ROLE_RELEVANCE: dict[DiscussionState, list[FacilitationRole]] = {
    DiscussionState.STALLED: [SOCIAL, INTELLECTUAL, ORGANIZATIONAL],
    DiscussionState.CONFLICTIVE: [MODERATOR, SOCIAL, AFFECTIVE],
    ...
}
```

Este diccionario existe en el módulo pero no se usa para filtrar las técnicas
devueltas al agente. La guía de selección la aportan la persona y las
restricciones del prompt del agente de rol, no el orden ni el contenido de la
lista.

## Implicación para la evaluación

Si el sesgo existe y es sistemático, los experimentos de evaluación observarán
una distribución sesgada de técnicas seleccionadas: sobrerepresentación de
técnicas organizacionales e intelectuales y subrepresentación de técnicas
sociales, afectivas y de moderación. Esto no es atribuible a la calidad del
razonamiento del modelo sino al artefacto de ordenación.

El sesgo es especialmente relevante para comparar modelos: un modelo pequeño
puede seleccionar técnicas organizacionales no porque sean las más adecuadas
sino porque aparecen primero. Interpretar esta diferencia como una diferencia
de capacidad sería incorrecto.

## Decisión provisional

No se implementa mitigación en esta fase por las razones siguientes:

1. El sesgo no está confirmado empíricamente en este sistema. La evidencia
   de primacy bias en LLMs proviene de contextos de evaluación y ranking
   (Zheng et al. 2023, Ko et al. 2020), no de selección de técnicas de
   facilitación.
2. Añadir filtrado por rol antes de confirmar el sesgo introduce una variable
   de confusión: si los resultados cambian, no se puede distinguir si el
   cambio se debe al filtrado o a otros factores.
3. El diseño actual tiene una propiedad útil: todos los agentes de rol ven
   todas las técnicas, lo que permite selecciones cross-rol cuando el contexto
   lo justifica (por ejemplo, un agente social que selecciona una técnica
   organizacional porque el hilo lo requiere).

La mitigación correcta es filtrar por rol usando `STATE_ROLE_RELEVANCE` o
un mapeo rol → técnicas, pero solo después de confirmar el sesgo
experimentalmente.

## Mitigaciones pendientes de evaluación

Las siguientes opciones están disponibles y no requieren cambios de
arquitectura:

1. **Filtrado por rol**: `get_techniques(role)` devuelve solo las técnicas
   del rol activo. Elimina el sesgo por posición pero también elimina la
   posibilidad de selección cross-rol. Puede introducir rigidez.

2. **Ordenación por relevancia al estado**: usar `STATE_ROLE_RELEVANCE` para
   poner primero las técnicas del rol más relevante para el estado actual.
   Preserva el acceso a todas las técnicas pero reduce el sesgo de primacía.

3. **Aleatorización del orden**: reordenar la lista aleatoriamente en cada
   llamada. Elimina el sesgo sistemático pero introduce varianza en los
   resultados, lo que dificulta la reproducibilidad de experimentos.

4. **Posición invertida según el rol**: el agente social recibe la lista con
   técnicas sociales primero. Simple, determinista, preserva el acceso
   completo.

## Consecuencias de no mitigar

- Los experimentos actuales pueden subestimar la capacidad de los modelos para
  seleccionar técnicas sociales y afectivas.
- La comparación entre modelos puede reflejar diferencias en sensibilidad al
  sesgo de posición más que diferencias en razonamiento de facilitación.
- Esta limitación debe declararse explícitamente en la evaluación de la tesis.

## Cuestiones abiertas

- ¿Es el sesgo de primacía observable en los experimentos actuales?
  Un análisis de la distribución de técnicas por rol en los resultados de
  `docs/experiments/results/` podría confirmarlo o descartarlo.
- Si se filtra por rol, ¿debe el agente tener acceso a un subconjunto de
  técnicas de otros roles para casos mixtos? ¿Cuáles y bajo qué criterio?
- ¿Debe `STATE_ROLE_RELEVANCE` usarse para ordenar o para filtrar?

## Referencias

- Ko, W., et al. (2020). Positional bias in pairwise comparisons of large
  language model responses. Evidencia de primacy bias en evaluaciones LLM.
- Zheng, L., Chiang, W. L., Sheng, Y., et al. (2023). Judging LLM-as-a-judge
  with MT-bench and chatbot arena. *NeurIPS 2023*.
- Burgess, A., & Taylor, L. (2013). The long list problem in recommendation
  systems: position effects and mitigation strategies.
