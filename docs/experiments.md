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

### 5. History is never written by the pipeline

`PipelineDeps` accepts a `history_store`, and the role agent calls
`get_thread_history` as a tool. But no node in the pipeline calls
`history_store.record_intervention()`. The store is read-only from the
pipeline's perspective. Unless the API caller manually writes records
before invoking the pipeline, `get_thread_history` always returns
"No prior interventions recorded."

This means the cooldown constraint ("do not repeat interventions that
produced no progress") and the EMT escalation logic ("escalate only
when lower levels have been tried") are both aspirational: the data
they require is never present.

**Question**: Does the role agent behave differently when history is
populated vs empty? Does the absence of history cause it to always
start from L1, or does it skip the cooldown reasoning entirely?

### 6. Classification sub-dimensions do not reach the orchestrator

The classification produces five fields: `state`, `trajectory`,
`participation_balance`, `discourse_quality`, `inquiry_phase`. The
orchestrator's CONTEXT_TEMPLATE forwards only `state` and
`classification_reasoning`. The sub-dimensions are available in
`reasoning` only if the classification agent wrote them out in prose.

A `dominated` thread and a `distributed` thread with the same `state`
and similar reasoning text look identical to the orchestrator. The
orchestrator cannot reason about participation balance when selecting
a role.

**Question**: Does the classification agent reliably describe
sub-dimension values in its reasoning text? Does the orchestrator
use that information when selecting a role?

### 7. Technique list ordering may bias selection

`retrieve_techniques` returns all 30 techniques in a fixed order:
organizational (5) → intellectual (8) → social (5) → affective (5) →
moderator (7). LLMs tend to anchor on early-appearing options in long
lists. A Social or Affective role agent has to read through 13
techniques before reaching its most relevant ones.

**Question**: Do Social and Affective agents systematically select
techniques that appear early in the list (organizational/intellectual)
more often than expected?

### 8. Single forced-choice state suppresses multi-condition signals

The classifier assigns exactly one `state` value. A thread can satisfy
multiple conditions simultaneously: stalled AND off_topic, or stalled
AND conflictive. The forced choice means one signal is silently
dropped. The downstream pipeline has no way to know both conditions
apply.

**Question**: When a thread is genuinely dual-state (stalled after
conflict, or off-topic and declining), which label does the
classifier assign? Is the intervention still appropriate for both
conditions?

### 9. `closed` threads are not checked before the pipeline runs

`DiscussionThread.closed: bool` is part of the domain model but no
node checks it before running. The pipeline will classify, decide to
intervene, and generate a response for a closed thread. The response
has nowhere to go.

**Question**: Does this need a guard at the API layer, or at the
pipeline entry node?

### 10. `CourseContext` and `last_activity_at` are defined but unused

`CourseContext` (course display name, module topic, audience level,
language) is modeled in `models.py` but never injected into any agent
prompt. `DiscussionThread.last_activity_at` is collected from the LMS
but `format_thread` does not include it. Agents have no knowledge of
the broader course context or the authoritative LMS staleness signal.

A thread that belongs to a first-year introductory module needs
different facilitation than one in a graduate seminar. A thread where
`last_activity_at` is 72 hours ago but the last comment is 2 hours old
(comments could include edits or likes) would be misread.

**Question**: Would injecting `CourseContext` into classification or
role prompts change technique selection? Is `last_activity_at` more
reliable than inferring staleness from comment timestamps?

### 11. `action_category` is self-reported with no consistency check

`FacilitationResponse.action_category` is set by the role agent itself.
There is no check that a `SocialAgent` returns `ActionCategory.SOCIAL`,
or that `ModeratorAgent` returns `ActionCategory.MODERATION`. A
cross-category response passes all rule checks in `ResponseEvalNode`.

**Question**: Do role agents reliably report the correct category for
their role, or does the category drift when the selected technique
belongs to an adjacent role?

### 12. Moderator "last resort" is a persona constraint, not a routing rule

`ModeratorAgent` CONSTRAINTS say "You are the last resort. Activate
only when other roles cannot address the situation." But the
orchestrator can select Moderator on the first attempt for a
conflictive thread, with no prior Social or Affective intervention.
The "last resort" instruction applies only within the role agent's
own reasoning, not to the orchestrator's selection logic.

**Question**: Does the orchestrator select Moderator immediately for
conflictive threads, or does it prefer Social/Affective first? Does
the Moderator agent's "last resort" framing cause it to produce softer
responses than expected when selected first?

---

## Experiment scenarios

Each row is a thread designed to probe one or more tensions above.
The "expected behavior" is a hypothesis, not a guarantee.

| Scenario | Tensions probed | Expected behavior |
|---|---|---|
| **dominated** | #6, #1 | `participation_balance=dominated`; Social selected; `redistribute_attention` or `encourage_participation` |
| **formulaic** | #6, #1, #7 | `discourse_quality=formulaic`; Intellectual selected; EMT L1 pump |
| **hostile_then_silent** | #8, #2, #12 | Ambiguous state (stalled vs conflictive); trajectory drives intervention; Social or Moderator |
| **integration_phase** | #2 | `should_intervene=False`; `inquiry_phase=integration`; no response generated |
| **explicit_distress** | #1, #7 | Affective selected; `validate_effort` or `normalize_difficulty` |
| **overt_attack** | #4, #12 | Moderator selected; `instructor_escalation`; `post_to_thread=False` |
| **repeat_intervention** | #5 | With history populated: does the role agent avoid repeating prior technique? |
| **closed_thread** | #9 | Should terminate before classification; currently does not |

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

## Run results

Run with `uv run --env-file .env facilitate docs/threads/<scenario>.json`.
Results below are from the first run of each scenario (2026-04-08).

### dominated

```
State:       stalled
Trajectory:  declining
Inquiry:     exploration
Intervention: YES
Role:        social
Technique:   redistribute_attention
Post:        True
Confidence:  0.90
```

**Observation**: Classification correctly identified a stalled thread (one
participant posted 5 of 7 messages) but labeled it `stalled`, not
`dominated`. `participation_balance` is not surfaced in the output —
tension #6 confirmed: the orchestrator selected Social based on state
alone, not on balance data. Technique matched the Social archetype.

---

### formulaic

```
State:       stalled
Trajectory:  declining
Inquiry:     triggering
Intervention: YES
Role:        intellectual
Technique:   challenge_counterargument
Post:        True
Confidence:  0.90
```

**Observation**: Six students all posted surface agreement ("I also agree",
"same here"). Intellectual selected — correct archetype for a discourse
quality problem. Technique was `challenge_counterargument`, not an EMT L1
pump as expected. This probes tension #1: the Intellectual agent had all 30
techniques available and chose one from its own archetype, but not the
expected one. Tension #7 not confirmed: the agent skipped early-list
organizational techniques.

---

### hostile_then_silent

```
State:       conflictive
Trajectory:  declining
Inquiry:     exploration
Intervention: YES
Role:        social
Technique:   de_escalate
Post:        True
Confidence:  0.85
```

**Observation**: Thread had a sharp exchange followed by a defensive close.
State classified as `conflictive` (not `stalled`), so the dual-state
ambiguity in tension #8 did not manifest here — the conflict signal was
dominant. Social selected over Moderator, consistent with tension #12: the
"last resort" framing kept Moderator out. `de_escalate` is appropriate and
within the Social archetype.

---

### integration_phase

```
State:       convergent
Trajectory:  stable
Inquiry:     resolution
Intervention: NO - thread does not need intervention
```

**Observation**: Thread where students actively synthesized cross-unit
connections and the instructor confirmed the pattern. System correctly
decided not to intervene. `inquiry_phase=resolution` is the most advanced
phase. This is the clearest result: the pipeline stayed silent when it
should. Tension #2 is not confirmed here — the sub-dimensions did reach
the intervention agent through the classification reasoning.

---

### explicit_distress

```
State:       stalled
Trajectory:  declining
Inquiry:     exploration
Intervention: YES
Role:        affective
Technique:   emotional_support
Post:        True
Confidence:  0.95
```

**Observation**: One student explicitly wrote "I don't know if I'm missing
something fundamental... Everyone else seems to get it." Affective selected
with the highest confidence of any run (0.95). Technique `emotional_support`
is appropriate. Tension #7 not confirmed: the Affective agent correctly
reached its own techniques despite them appearing late in the list.

---

### overt_attack

**Result**: Pipeline crashed at the `flag_content` tool call.

The Moderator agent was selected, called `flag_content` with the flagged
post ID, and the tool made a real HTTP call to
`http://local.openedx.io:8000/api/v2/comments/<id>/abuse_flag` which
returned 404. The post does not exist in the real forum because the thread
is synthetic.

**What this confirms**: Tension #4 is real — the Moderator agent did select
`instructor_escalation` and called `flag_content` before the crash. The
role selection and technique were correct. The failure is an integration
issue: the playground uses the real `OpenEdXBackend` (configured via
`.env`) when running synthetic threads that have no real post IDs.

**Fix needed**: The playground should pass `lms_backend=None` when no
`--thread-id` is supplied, so `flag_content` is a no-op for synthetic data.

---

## Pending scenarios

- `repeat_intervention`: requires manually populating history before the
  run. Needs a test harness, not just a JSON file.
- `closed_thread`: requires a thread with `"closed": true`. Pipeline will
  run it fully — tension #9 confirms there is no guard.

---

## Threads

All scenario files are in `docs/threads/`. See `docs/playground-example.json`
for the DiscussionThread schema (field names are domain model names:
`username`, `body` — not the LMS API names `author`, `raw_body`).
`learning_objectives` is not present in the OpenEdX API and is omitted from
all thread files.
