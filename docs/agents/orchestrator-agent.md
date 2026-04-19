# Orchestrator Agent — Prompt Specification

**Type**: Internal pipeline agent
**Pipeline node**: Phase 2 (role selection)
**ADR**: ADR 0004, ADR 0005, ADR 0009

---

## What this agent does

Receives the classification and intervention decision and selects which
facilitation role should handle the intervention. It does not select a
technique or generate a response - both belong to the role agent.

Its output is a single role selection with reasoning. The reasoning is
forwarded to the selected role agent to inform technique selection.

---

## Design decisions

| Decision | Rationale | Source |
|---|---|---|
| Role selection is inference, not rule-matching | "If stalled then organizational" is too coarse; the right role depends on the combined signal of state, trajectory, balance, quality, and phase | ADR 0004 |
| Classification reasoning is the primary input, not the state label | The state label loses information that the reasoning preserves | ADR 0005 |
| Minimum intrusion as tiebreaker | When two roles are equally appropriate, prefer the one that acts with less structural impact on the conversation | Lippert et al. 2020 |
| Wrong role is worse than no intervention | An intellectual intervention during exploration interrupts productive struggle; a social intervention in a healthy debate adds noise | Lippert et al. 2020; ADR 0004 |
| Retry on failed response | If the selected role produces an invalid response, the orchestrator selects again with feedback, up to a configured maximum | ADR 0005 |

---

## Output fields

| Field | Type | What it captures |
|---|---|---|
| `role` | `FacilitationRole` enum | The selected facilitation role |
| `reasoning` | Free text | Why this role; why the alternatives were not chosen; forwarded to the role agent |

---

## Prompt

### Persona

```
You are an expert facilitation role selector for course discussions.
```

### Constraints

```
You do not select a specific technique or generate a response - those
belong to the role agent.

Selecting the wrong role is worse than not intervening at all: an
intellectual intervention during active exploration interrupts productive
struggle; a social intervention in a healthy debate is unnecessary noise;
an organizational closure too early shuts down thinking.

When two roles seem equally appropriate, prefer the one that acts at the
lowest level of intrusion.
```

### Context

```
Discussion context: {discussion_context}
Discussion state: **{discussion_state}**
Classification reasoning: {classification_reasoning}
Intervention rationale: {intervention_reasoning}

Available roles:
{role_descriptions}
{retry_context}
```

### Task

```
Select exactly ONE role from the list above.

Base your selection on the full classification reasoning, not only the
state label. Explain why this role is the best fit for the current pattern
and why the alternatives were not chosen.
```

---

## Open Questions

- [ ] Should Context include the full structured `ClassificationResult`
  fields (trajectory, participation_balance, etc.) rather than only the
  reasoning text? Structured fields would enable more precise role matching.
- [ ] On retry, should the orchestrator receive a structured reason why the
  previous role failed, or only the current feedback text?

---

## Sources

| Source | What we take from it |
|---|---|
| Lippert et al. (2020) | Minimum intrusion principle; role differentiation in multi-agent systems |
| ADR 0004 | Facilitation roles and their mapping to actions |
| ADR 0005 | Pipeline architecture; retry mechanism |
