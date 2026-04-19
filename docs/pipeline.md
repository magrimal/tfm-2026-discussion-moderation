# Facilitation Pipeline

**Last updated**: 2026-04-07

This document describes the full execution flow of the facilitation
pipeline: what each node decides, which nodes make LLM calls, and
how the retry path works.

---

## Decision map (quick reference)

| Node | LLM call | Decides |
|---|---|---|
| ClassificationNode | yes | state + 4 sub-dimensions |
| ClassificationEvalNode | no | flags missing reasoning (if eval enabled) |
| InterventionNode | yes | should_intervene? (binary) |
| InterventionEvalNode | no | route to orchestrator or end |
| OrchestratorNode | yes | which facilitation role? |
| RoleNode | yes | which technique + response text |
| ResponseEvalNode | no | retry or end; checks for empty text and evaluative language |

---

## Execution flow

```
DiscussionThread
      |
      v
ClassificationNode         [LLM call]
      |
      v
ClassificationEvalNode     [rule check: reasoning non-empty if eval enabled]
      |
      v
InterventionNode           [LLM call]
      |
      v
InterventionEvalNode       [routing only]
      |
      +-- should_intervene=False --> End (classification + intervention only)
      |
      +-- should_intervene=True  --> OrchestratorNode
                                          |
                                          v
                                    OrchestratorNode   [LLM call]
                                          |
                                          v
                                      RoleNode         [LLM call]
                                          |
                                          v
                                    ResponseEvalNode   [rule checks]
                                          |
                                          +-- checks pass --> End (full result)
                                          |
                                          +-- checks fail, retries left
                                                 --> OrchestratorNode (retry)
```

Four LLM calls in the happy path: classification, intervention,
orchestrator, role.

---

## Node responsibilities

### ClassificationNode

Calls the classification agent. Produces a `ClassificationResult`
with five dimensions:

| Field | Values |
|---|---|
| `state` | new, active, stalled, conflictive, convergent, off_topic |
| `trajectory` | growing, stable, declining, never_started |
| `participation_balance` | distributed, dominated, instructor_centered |
| `discourse_quality` | substantive, mixed, formulaic |
| `inquiry_phase` | triggering, exploration, integration, resolution |

### ClassificationEvalNode

Rule check only (no LLM). If `classification_eval_enabled=True`,
flags missing reasoning. Otherwise passes through.

### InterventionNode

Calls the intervention agent. Receives `state` and `reasoning` from
classification. Decides `should_intervene: bool`.

Note: the intervention agent sees `state` and `reasoning` but not the
four sub-dimensions explicitly. They are present in the reasoning text
only if the classification agent included them.

### InterventionEvalNode

Routes based on `should_intervene`. If False, the pipeline ends here
with no response generated. If True, continues to orchestrator.

### OrchestratorNode

Calls the orchestrator agent. Selects one of the five facilitation
roles. Receives the full classification, intervention reasoning, and
a description of each role. On retry, receives the previous feedback
from `ResponseEvalNode`.

### RoleNode

Calls the selected role agent. The role agent:
1. Calls `retrieve_techniques` (tool) to see the full repertoire.
2. Calls `get_thread_history` (tool) to check prior interventions.
3. Selects one technique and generates a response.

### ResponseEvalNode

Rule checks (no LLM):
- Response text non-empty
- Technique name non-empty
- No evaluative/grading language in the response text

If checks fail and retries remain: sends feedback to the orchestrator
and reruns from `OrchestratorNode`. The retry picks a *different role*,
not a different technique within the same role.

---

## Retry behavior

The retry path is: `ResponseEvalNode` → `OrchestratorNode` → `RoleNode`
→ `ResponseEvalNode`.

`max_orchestrator_retries` controls how many times this loop can run
(default: 1, meaning one original attempt + one retry). The feedback
string from the failed check is injected into the orchestrator prompt
on retry.

---

## PipelineResult fields

| Field | Set when |
|---|---|
| `classification` | always |
| `intervention` | always |
| `role_selection` | only if `should_intervene=True` |
| `response` | only if `should_intervene=True` and checks pass |
| `final_text` | same as `response`, convenience copy |
