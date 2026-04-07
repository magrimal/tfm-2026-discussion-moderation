# System Behavior Experiments

**Last updated**: 2026-04-07

This document maps design tensions in the pipeline to concrete
thread scenarios that reveal how the system behaves. Use these
with the playground CLI or the eval suites.

```
uv run facilitate docs/threads/<scenario>.json
uv run facilitate docs/threads/<scenario>.json --pretty
```

---

## Design tensions to probe

These are properties of the current design that are not guaranteed
by the code. They depend on LLM behavior, prompt wording, and the
interaction between pipeline nodes.

### 1. Role selection does not constrain technique selection

The orchestrator selects a role. The role agent has access to all 30
techniques regardless of role. The Connector (Social) can select
`socratic_clarification`; the Sage-Facilitator (Intellectual) can
select `encourage_participation`. Persona is the only constraint on
technique choice, and it is soft.

**Question**: Do role agents actually select techniques that match
their archetype, or do they drift toward adjacent techniques?

### 2. Intervention agent does not receive sub-dimensions explicitly

The intervention prompt shows `state` and `classification_reasoning`
but not the four sub-dimensions as structured fields. A stalled thread
with `trajectory=declining` is meaningfully different from one with
`trajectory=stable`, but the intervention agent sees this distinction
only if the classification agent included it in the reasoning text.

**Question**: Does the intervention agent make different decisions for
the same state with different trajectories?

### 3. Retry selects a different role, not a different technique

If `ResponseEvalNode` flags an issue, the pipeline retries via
`OrchestratorNode`, not `RoleNode`. The orchestrator may pick the
same role again (it receives "previous feedback" but no instruction
to avoid the prior role). If it does, the role agent runs again with
no memory of the previous attempt.

**Question**: When a response fails rule checks, does the retry
actually produce a different role, or does the same role recur?

### 4. `instructor_escalation` is available to all roles

Any role agent can select `instructor_escalation` and set
`post_to_thread=False`. Only `ModeratorAgent` has the `flag_content`
tool. There is no prompt-level guard preventing the Social agent from
escalating to the instructor.

**Question**: Does the Social or Affective agent ever select
`instructor_escalation`? Under what circumstances?

---

## Experiment scenarios

Each row is a thread designed to probe one or more tensions above.
The "expected behavior" is a hypothesis, not a guarantee.

| Scenario | What it tests | Expected behavior |
|---|---|---|
| **dominated** | Classifier sub-dimensions; Social role activation | `participation_balance=dominated`; Social selected; `redistribute_attention` or `encourage_participation` |
| **formulaic** | Discourse quality detection; Intellectual role activation | `discourse_quality=formulaic`; Intellectual selected; EMT L1 pump |
| **hostile_then_silent** | State label at the boundary of conflictive/stalled; intervention timing | `state=stalled` or `conflictive`; trajectory matters; Social or Moderator |
| **integration_phase** | System staying silent during productive exchange | `should_intervene=False`; `inquiry_phase=integration`; no response generated |
| **explicit_distress** | Affective role activation vs Intellectual; EMT vs validation | Affective selected; `validate_effort` or `normalize_difficulty` |
| **overt_attack** | Moderator activation; `instructor_escalation` + `flag_content` | Moderator selected; `instructor_escalation`; `post_to_thread=False` |

---

## How to read the playground output

```
State:       stalled           <- ClassificationNode output
Trajectory:  declining         <- sub-dimension
Inquiry:     triggering        <- sub-dimension
Intervention: YES              <- InterventionNode output
Role:        social            <- OrchestratorNode output
Technique:   redistribute_attention   <- RoleNode output
Post:        True              <- whether response goes to thread
Confidence:  0.82

--- Response ---
Hey Carlos, you raised a sharp point about proxy variables
earlier...
```

Key things to check in the output:
- Does `State` match what you expected given the thread?
- Does the selected `Role` make sense for the state and reasoning?
- Does the `Technique` match the role's archetype (not just any technique)?
- Is `Post: False` only when technique is `instructor_escalation`?
- Does the response text reference specific student names and contributions?

---

## Threads to write

The following scenarios are planned but not yet implemented as JSON
playground files. See `docs/playground-example.json` for the
DiscussionThread schema.

- `docs/threads/dominated.json`
- `docs/threads/formulaic.json`
- `docs/threads/hostile_then_silent.json`
- `docs/threads/integration_phase.json`
- `docs/threads/explicit_distress.json`
- `docs/threads/overt_attack.json`
