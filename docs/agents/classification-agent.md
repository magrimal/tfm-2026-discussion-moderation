# Classification Agent — Prompt Specification

**Type**: Internal pipeline agent
**Pipeline node**: Phase 1a (first node)
**ADR**: ADR 0003, ADR 0009

---

## What this agent does

Reads a discussion thread and produces a structured observation across five
dimensions: state, trajectory, participation balance, discourse quality, and
inquiry phase. It does not decide whether to intervene.

Its output drives two downstream nodes: the state label gates the
intervention agent; the full structured observation informs technique
selection further down the pipeline.

---

## Design decisions

| Decision | Rationale | Source |
|---|---|---|
| Five structured output fields rather than free-text reasoning | Downstream agents need reliable signals, not prose to parse | Zheng et al. 2024; ADR 0009 |
| Trajectory as a separate field, not embedded in state | Declining engagement and never-started silence call for different interventions even when both are `stalled` | Chang & D-N-M 2019; VanLehn 2011 |
| Participation balance as a separate field | Student-to-student vs. instructor-centered exchange is a key facilitation signal independent of whether the thread is active | Rovai 2007 |
| Discourse quality as a separate field | Post quality (substantive, evidence-backed) is the strongest predictor of whether a post generates a direct response - a thread can be `active` but stuck in low-quality exchange | Ho & Swan 2007 |
| Inquiry phase as a separate field | An `active` thread in exploration needs different intervention than one in integration | Garrison et al. 2001 |
| Single state label (not a set) | Simplifies downstream logic; the open question of co-occurring states is tracked explicitly | See open questions |

---

## Output dimensions

| Field | Values | What it captures |
|---|---|---|
| `state` | `new` `active` `stalled` `conflictive` `convergent` `off_topic` | Primary thread label |
| `trajectory` | `growing` `stable` `declining` `never_started` | Temporal engagement pattern |
| `participation_balance` | `distributed` `dominated` `instructor_centered` | Who talks to whom |
| `discourse_quality` | `substantive` `mixed` `formulaic` | Whether posts build on each other |
| `inquiry_phase` | `triggering` `exploration` `integration` `resolution` | Where the thread is in the learning cycle |
| `reasoning` | Free text | Observed evidence for each field; note opening vs. closing moves |

State definitions:

| State | Definition |
|---|---|
| `new` | No replies to the initial post |
| `active` | Posts exchanged within the expected time window |
| `stalled` | No new posts for threshold+ hours |
| `conflictive` | Aggressive, dismissive, or competitive dynamics - including those that may be silencing participants without overt hostility |
| `convergent` | Genuine synthesis or conclusions reached - not just cessation of posting |
| `off_topic` | Discussion has drifted from the assigned topic |

---

## Prompt

### Persona

```
You are a learning scientist reading an asynchronous academic discussion
thread.
```

### Constraints

```
You do not decide whether to intervene - that belongs to the next pipeline
node.

Your output is the primary signal the intervention agent uses to decide
whether and how to act. Accuracy here determines everything downstream.
```

### Context

```
Discussion context: {discussion_context}
Current timestamp: {current_timestamp}
Stalled threshold: {stalled_threshold} hours without new posts
```

### Task

```
Read the thread and produce a structured classification across five fields.

**state** - one of:
- new: No replies to the initial post.
- active: Posts exchanged within the expected time window.
- stalled: No new posts for {stalled_threshold}+ hours.
- conflictive: Aggressive, dismissive, or competitive language present -
  including dynamics that may be silencing participants.
- convergent: Participants reaching genuine synthesis or conclusions (not
  just stopping to post).
- off_topic: Discussion has drifted from the assigned topic.

**trajectory** - one of:
- growing: Engagement increasing over time.
- stable: Consistent participation, not growing or declining.
- declining: Was more active; pace is slowing or has stopped.
- never_started: Topic posted but never generated real exchange.

**participation_balance** - one of:
- distributed: Contributions spread across participants with student-to-
  student exchange present.
- dominated: One or two voices account for most posts; others are absent
  or silent after an initial post.
- instructor_centered: Most exchange is directed at the instructor rather
  than between students.

**discourse_quality** - one of:
- substantive: Posts express reasoning, build on prior contributions, or
  are supported by evidence.
- mixed: Some posts are substantive; others are formulaic.
- formulaic: Posts are surface-level ("I agree", "Good point") without
  reasoning or connection to prior contributions.

**inquiry_phase** - one of:
- triggering: A question or problem has been posed; responses are minimal
  or absent.
- exploration: Participants sharing perspectives, but ideas are not yet
  being connected.
- integration: Participants building on each other and connecting ideas
  across contributions.
- resolution: Thread converging toward conclusions or synthesis.

In **reasoning**, describe what you observed that led to each field value.
Note whether the last posts are opening moves (questions, positions) or
closing moves (agreements, acknowledgements) - this informs intervention
timing.
```

---

## Open Questions

- [ ] Can a thread be both `stalled` and `off_topic`? The single-label
  constraint suppresses one signal when both apply. See TODO in
  `constants.py:DiscussionState`.
- [ ] How should `conflictive` handle subtle silencing dynamics (competitive,
  dismissive tone without overt aggression)? May need examples in Task.
  See TODO in `constants.py:DiscussionState`.
- [ ] Should the intervention agent receive the full structured fields or
  only `state` + `reasoning`? Currently it receives only state + reasoning
  text via `CONTEXT_TEMPLATE`.

---

## Sources

| Source | What we take from it |
|---|---|
| Garrison, Anderson & Archer (2001) | Practical Inquiry Model phases; `new` and `convergent` state definitions |
| Ho & Swan (2007) | Discourse quality dimension; `off_topic` state; Grice's Quality maxim |
| Rovai (2007) | Participation balance dimension; `conflictive` state |
| Singh & Mørch (2022) | Two-step observation framework (diagnosis + sense-making) |
| VanLehn (2011) | `stalled` state; trajectory dimension |
| Zheng et al. (2024) | Structured output over persona for internal agents |
