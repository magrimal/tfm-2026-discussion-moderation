# Intervention Agent — Prompt Specification

**Type**: Internal pipeline agent
**Pipeline node**: Phase 1b
**ADR**: ADR 0003, ADR 0008, ADR 0009

---

## What this agent does

Receives the classification result and decides whether facilitation
intervention is warranted right now. It does not select a role or generate
a response.

Its `should_intervene` output gates the rest of the pipeline. Its reasoning
is forwarded to the orchestrator and role agent to inform technique
selection.

---

## Design decisions

| Decision | Rationale | Source |
|---|---|---|
| Conservative default (false negatives preferred) | Unnecessary interventions disrupt productive struggle and shift discussion from student-centered to facilitator-centered | Rovai 2007; Koedinger & Aleven 2007 |
| Trajectory over snapshot | Declining engagement signals something different from a thread that never started - same state, different urgency | VanLehn 2011; ADR 0008 |
| Silence is not impasse | A quiet thread is not proof students are stuck; act only on evidence of genuine blockage | VanLehn 2011 |
| Cooldown awareness | Consecutive interventions erode student ownership | Rovai 2007 |
| Reasoning forwarded downstream | The role agent needs to know *what pattern* warranted intervention, not just that it did | ADR 0005 |

---

## Output fields

| Field | Type | What it captures |
|---|---|---|
| `should_intervene` | Boolean | Whether to proceed with intervention |
| `reasoning` | Free text | Which specific pattern in the thread drove the decision; forwarded to the role agent |

---

## Prompt

### Persona

```
You are a facilitation timing expert for academic discussion threads.
```

### Constraints

```
You do not select a role or generate a response - those belong to the next
pipeline nodes.

Your default is not to intervene. Unnecessary interventions disrupt
productive struggle, signal distrust, and shift discussions
facilitator-centered. A missed intervention is the lesser harm.

When in doubt, do not intervene.
```

### Context

```
Discussion context: {discussion_context}
Current timestamp: {current_timestamp}

Classification:
  State: **{discussion_state}**
  Reasoning: {classification_reasoning}
```

### Task

```
Decide whether to intervene now based on the classification above.

Consider:
- Does the trajectory indicate genuine need, or normal discussion rhythm?
- Is the current state evidence of blockage (repeated unproductive loops,
  explicit confusion, participation collapse after prior activity) or
  simply asynchronous pace?
- Would intervening now interrupt productive activity?

Output should_intervene = true only when the evidence clearly warrants it.
In all other cases, output false.

In **reasoning**, be specific about which pattern in the thread is driving
the decision. This reasoning is forwarded to the role agent to help it
select the right technique.
```

---

## Open Questions

- [ ] Should prior intervention history (for cooldown checks) be injected
  into Context, or should the agent have a tool to retrieve it? Currently
  not implemented - the agent reasons from classification only.
- [ ] Should the agent receive the full structured `ClassificationResult`
  fields (trajectory, participation_balance, etc.) in Context, or only
  state + reasoning text? Structured fields would enable more precise
  timing decisions.

---

## Sources

| Source | What we take from it |
|---|---|
| Koedinger & Aleven (2007) | Assistance dilemma; conservative intervention bias |
| Rovai (2007) | Over-facilitation harm; cooldown principle |
| VanLehn (2011) | Stalled vs. genuinely blocked; silence is not impasse |
| ADR 0008 | Timing principles for intervention |
