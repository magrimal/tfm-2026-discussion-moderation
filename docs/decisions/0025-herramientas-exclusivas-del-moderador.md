# ADR 0025: Herramientas exclusivas del ModeratorAgent

**Estado**: Aceptado
**Fecha**: 2026-04-26
**Depende de**: ADR 0004 (Roles de facilitación), ADR 0005 (Arquitectura
multi-agente), ADR 0010 (Puntos de integración), ADR 0017 (Técnicas como
herramienta dinámica)

## Descripción

Los cinco agentes de rol (organizacional, intelectual, social, afectivo, moderador)
comparten las herramientas `retrieve_techniques` y `get_thread_history`. Sin
embargo, el repertorio incluye la técnica `instructor_escalation`, cuya ejecución
requiere comunicación externa con el LMS: marcar una contribución para revisión
humana. No todos los agentes de rol deben tener acceso a esta capacidad.

## Decisión

`ModeratorAgent` registra una herramienta adicional (`flag_content`) que no
está disponible en los demás agentes de rol:

```python
class ModeratorAgent(RoleAgent):
    def register_tools(self) -> None:
        super().register_tools()  # retrieve_techniques, get_thread_history

        @self.agent.tool
        async def flag_content(ctx, post_id: str, reason: str) -> str:
            """Flag a post for instructor review via the LMS backend."""
            if ctx.deps.lms_backend is None:
                return "No LMS backend configured; cannot flag content."
            await ctx.deps.lms_backend.flag_content(post_id, reason)
            return f"Post {post_id} flagged for review: {reason}"
```

Los demás agentes de rol heredan `register_tools()` de `RoleAgent` sin añadir
`flag_content`.

### Tensión con la técnica `instructor_escalation`

El repertorio de técnicas incluye `instructor_escalation` en `MODERATOR_TECHNIQUES`.
Esta técnica prescribe notificar al instructor cuando la situación supera lo que
el sistema puede manejar de forma automatizada. Un modelo que selecciona
`instructor_escalation` en cualquier agente de rol puede generar una respuesta
válida estructuralmente (el nombre de la técnica es conocido, `post_to_thread=False`
se requiere por la aserción correspondiente), pero sin llamar a `flag_content`
porque la herramienta no existe en ese agente.

El resultado: un agente no moderador que selecciona `instructor_escalation`
produce una respuesta que supera las aserciones estructurales pero no ejecuta
la acción externa que la técnica implica. El sistema no reporta el error.

Este gap es conocido y está documentado como limitación.

### Por qué la restricción a ModeratorAgent es correcta

El principio de diseño del sistema es que la moderación activa (gestión de
conflictos, escalación) es responsabilidad del rol de moderación, no de los
roles de facilitación organizacional, intelectual, social o afectivo. Los demás
roles tienen acceso al repertorio completo (incluyendo las técnicas de moderador,
por el motivo documentado en ADR 0016), pero su persona y restricciones de
prompt no los inclinan a seleccionar `instructor_escalation`. La herramienta
`flag_content` solo es necesaria cuando esa técnica se selecciona de forma
deliberada.

Añadir `flag_content` a todos los agentes de rol acoplaría la capacidad de
escalación a todos los roles y ampliaría el potencial de escalaciones incorrectas.
La restricción es un control de seguridad por diseño.

## Consecuencias

### Positivas

- La capacidad de escalación al instructor está restringida al rol que la
  literatura asigna a esa función (Rovai, 2007: el moderador gestiona los
  conflictos que superan la facilitación normal).
- Los demás agentes de rol no pueden invocar `flag_content` accidentalmente,
  independientemente de qué técnica seleccionen.
- El código es explícito: `register_tools()` en `ModeratorAgent` añade la
  herramienta; los demás agentes no la mencionan.

### Negativas

- Si un agente no moderador selecciona `instructor_escalation`, el sistema
  no detecta la inconsistencia entre la técnica declarada y la acción ejecutada.
  Las aserciones estructurales (`assertions.py`) verifican que
  `instructor_escalation` implica `post_to_thread=False`, pero no verifican
  que `flag_content` fue llamado.
- El repertorio completo está disponible para todos los agentes (ADR 0016):
  un agente social puede ver la técnica `instructor_escalation` en la lista y
  seleccionarla si el modelo lo considera apropiado. La restricción está en las
  herramientas, no en el repertorio visible.

### Cuestiones abiertas

- ¿Debe `assertions.py` añadir una verificación que detecte si la técnica
  seleccionada es `instructor_escalation` en un agente que no es moderador,
  y marcarlo como error?
- ¿Debe el filtrado del repertorio por rol (ADR 0016) excluir explícitamente
  `instructor_escalation` de los repertorios no moderadores cuando se
  implemente el filtrado?
- ¿Debe el `StubLMSBackend` implementar `flag_content` como operación no
  operativa para permitir evaluar el flujo completo de ModeratorAgent sin
  un LMS real?

## Referencias

- ADR 0004: roles de facilitación; define el papel del moderador.
- ADR 0016: sesgo de ordenación; explica por qué todos los agentes ven el
  repertorio completo incluyendo técnicas de otros roles.
- Rovai, A. P. (2007). Facilitating online discussions effectively. *The
  Internet and Higher Education*, 10(1), 77-88.
