# TODO — State of the work and open items

**Last updated**: 2026-04-08

This document lists what is built, what is broken, and what is missing.
Organized by area, roughly in priority order within each section.

---

## What is built

### Pipeline
- Classification, Intervention, Orchestrator, and 5 Role agents
- pydantic-graph pipeline with ClassificationEvalNode, InterventionEvalNode,
  ResponseEvalNode, and retry via OrchestratorNode
- `PipelineResult` with full state, classification, intervention, role
  selection, and facilitation response

### Agents
- Four-component prompt structure (PERSONA, CONSTRAINTS, CONTEXT, TASK)
- Shared role constraints (EMT, cooldown, `instructor_escalation` guard)
- 30-technique repertoire accessible to all role agents via `retrieve_techniques`
- `flag_content` tool on ModeratorAgent

### Tools and backends
- `LMSBackend` protocol
- `OpenEdXBackend`: real `get_thread()` → `/api/v2/threads/{id}?recursive=true`,
  real `flag_content()` → `/api/v2/comments/{id}/abuse_flag`
- `ThreadHistoryStore` protocol with `InMemoryThreadStore` and `SQLiteThreadStore`

### Testing (5 layers)
- Layer 0: unit tests (models, utils, knowledge base, prompt builder, mapper)
- Layer 1: pydantic-ai `TestModel` wiring (all agents, output types, tool calls)
- Layer 2: structural eval assertions (`assert_facilitation_response`)
- Layer 3: `pydantic_evals` eval suites (classifier, pipeline)
- Layer 4: playground CLI (`uv run --env-file .env facilitate <thread>.json`)

### Integration
- FastAPI REST endpoint `POST /facilitate` accepting `DiscussionThread`
- `_build_backend()` in `api/facilitation.py` wires backend from settings
- JWT auth via `JWT_AUTHENTICATION_TOKEN` env var
- `FACILITATION_LMS_URL` and `FACILITATION_LMS_BACKEND` in `.env`

### Docs and ADRs
- ADRs 0001–0010
- `docs/pipeline.md`: decision map, execution flow, node responsibilities
- `docs/experiments.md`: 12 design tensions, 6 run results, observations
- `docs/threads/`: 6 scenario JSON files

---

## Bugs

### 1. `overt_attack` playground crash (high priority)

The playground uses `OpenEdXBackend` by default (from settings). When the
ModeratorAgent calls `flag_content` with a synthetic post ID, the real
`/api/v2/comments/{id}/abuse_flag` endpoint returns 404 and the pipeline
crashes.

**Fix**: Pass `lms_backend=None` to `facilitate()` in the playground when
loading from a JSON file (no real backend needed). Only use the real backend
when `--thread-id` is given.

### 2. History is never written by the pipeline

`PipelineDeps` accepts a `history_store`, and role agents call
`get_thread_history` as a tool. But no pipeline node ever calls
`history_store.record_intervention()`. The history feature is structurally
present but operationally inert.

**Consequence**: EMT escalation logic and cooldown checks in role prompts
always operate on empty history. The constraints exist in the prompt but have
no data to reason about.

**Fix**: Add a history write step after `RoleNode` completes successfully,
before the pipeline ends.

### 3. No closed thread guard (tension #9)

`DiscussionThread.closed` is part of the domain model but no node checks it
before running the pipeline. A closed thread will be classified, intervened
upon, and have a response generated — with nowhere to post it.

**Fix**: Add a guard at the pipeline entry (before `ClassificationNode`) or
at the API layer. Decision pending (ADR needed or extend ADR 0010).

---

## Missing features

### Integration entry points (ADR 0010)

- [ ] Playground `--thread-id` flag: call `backend.get_thread(id)` instead
  of loading from JSON. This is the primary path for testing against real
  forum data.
- [ ] REST endpoint `POST /api/v1/facilitate` accepting `{"thread_id": "..."}`
  as an alternative to a full DiscussionThread body. The current endpoint
  accepts the full body; the `thread_id` path requires calling `get_thread`.

### Backend stubs

These exist but return hardcoded or empty data:

- [ ] `get_course_context()`: returns a fake CourseContext. Should call the
  Open edX course blocks endpoint.
- [ ] `get_participant_history()`: returns `[]`. Should call
  `/api/v2/users/{username}/active_threads`.
- [ ] `get_course_materials()`: returns `[]`. No clear API target yet.

### Unused data in prompts

These fields are collected but never injected into any agent prompt:

- [ ] `CourseContext` (display name, module topic, audience level, language):
  modeled, fetched stub exists, never passed to agents. Would change technique
  selection for different course levels (undergraduate vs. graduate).
- [ ] `DiscussionThread.last_activity_at`: collected from the LMS but not
  included in `format_thread()`. The classification agent infers staleness
  from comment timestamps instead.

### Pipeline structural gaps

- [ ] Classification sub-dimensions (`participation_balance`,
  `discourse_quality`, `inquiry_phase`, `trajectory`) reach the orchestrator
  only through free-text reasoning, not as structured fields. The orchestrator
  cannot reliably distinguish a `dominated` thread from a `distributed` one
  with the same state.
- [ ] Dynamic tool registration: `tools/__init__.py` has a TODO for
  registering tools per backend. Currently the ModeratorAgent always has
  `flag_content` regardless of whether a real backend is available.

### Experiment scenarios not yet runnable

- [ ] `repeat_intervention`: requires history pre-populated before the run.
  Needs a small harness (inject records into `SQLiteThreadStore` then run).
- [ ] `closed_thread`: add `"closed": true` to a thread file and confirm the
  pipeline runs fully — this is the expected failure case for tension #9.

---

## Evaluation framework

The system has structural assertions (Layer 2) and deterministic wiring tests
(Layer 1), but no framework for evaluating whether the *content* of generated
responses is pedagogically appropriate.

### State of the art

Two dominant approaches in the literature:

**LLM-as-judge** (Zheng et al., MT-Bench 2023; Liu et al., G-Eval 2023):
A second LLM evaluates the generated response against a rubric. Scalable and
handles nuanced criteria. Known biases: verbosity (longer = better),
positional (first option favored in pairwise), self-enhancement (same model
favors its own outputs). Mitigated by: using a different model family as
judge, averaging over multiple prompts, using structured scoring rather than
free-form.

**Prometheus** (Kim et al., 2024): An open-source model fine-tuned
specifically for evaluation using reference answers and explicit rubrics.
More calibrated than vanilla GPT-4-as-judge for rubric-based scoring. Useful
when you want reproducible, non-proprietary evaluation.

**Human annotation**: Still the gold standard. Common protocol: Likert scales
(1–5) on multiple dimensions, two or three expert annotators, inter-annotator
agreement via Cohen's kappa. For a thesis, 2 annotators on ~30–50 cases is a
reasonable scope.

**pydantic-evals scorers**: The eval infrastructure already uses
`pydantic_evals`. Custom scorers can be added that call an LLM judge, check
groundedness, or compare against reference responses.

### What this system needs

A rubric with at least these dimensions:

| Dimension | Question |
|---|---|
| State appropriateness | Does the response address the actual detected state? |
| Technique fidelity | Is the response recognizable as the named technique? |
| Non-evaluative | Does it avoid grading, ranking, or judging contributions? |
| Groundedness | Does it reference specific thread content, not hallucinated facts? |
| Action alignment | Is `post_to_thread` consistent with the technique chosen? |
| Tone | Is the register appropriate for an academic asynchronous context? |

### Recommended evaluation design for the thesis

1. **Automated (LLM-as-judge)**: Add a `ResponseQualityScorer` to the
   `pydantic_evals` pipeline eval suite. Use a separate model (e.g. GPT-4o
   if the pipeline uses Claude, or vice versa) to score each dimension 1–5
   against the rubric above. This gives scalable coverage over all 6+
   scenarios and their variants.

2. **Structural (existing)**: Keep the `assert_facilitation_response`
   invariant checks as a fast gate. These are not quality measures, but they
   catch clear violations before the LLM judge runs.

3. **Human annotation (small-scale)**: Select ~20–30 representative outputs
   spanning the 6 scenarios and the main role types. Have 2 annotators
   (ideally educators familiar with online facilitation) score each on the
   rubric. Report Cohen's kappa and mean scores per dimension. This is the
   thesis's empirical contribution.

4. **Comparison baseline**: Run each scenario through a simpler version of the
   system (e.g. classification only + a generic "you should participate more"
   message) and compare quality scores. This shows what the full pipeline adds.

### Open question

Does evaluating the response independently of student reaction capture what
matters? The facilitation literature (Garrison et al., Community of Inquiry)
argues that teaching presence is only meaningful if it produces cognitive or
social presence in subsequent posts. A stronger evaluation would track whether
a response prompted continued engagement — but that requires real thread data
over time, not synthetic scenarios.

---

## Thesis documentation gaps

- [ ] `agent-memory/architecture-notes.md` does not exist — was planned but
  not created. Relevant design decisions live in ADRs and `docs/pipeline.md`
  but are not summarized in agent memory.
- [ ] `docs/literature/papers.csv` — unclear if it reflects the current
  literature scope (evaluation methods, facilitation literature, pydantic-ai).
- [ ] No empirical evaluation section in the thesis draft yet.
- [ ] Terminology file (`agent-memory/terminology.md`) should be checked for
  consistency with the evaluation rubric terms.
