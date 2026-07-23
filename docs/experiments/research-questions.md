# Research Questions for the Evaluation Chapter

**Last updated**: 2026-07-20

What the experiments should try to answer, grounded in this project's
own ADRs, code, and disclosed gaps — not literature about other
systems. Each question names the source that motivates it and whether
it's answerable with what exists today or needs new work first.

This is the informatics/CS-engineering framing: architecture validity,
LLM reliability, evaluation methodology, integration design. Where a
question touches the pedagogical literature (Rovai, VanLehn, Kapur,
etc.), it's because the system's *design* encodes a claim from that
literature as a testable behavior — the question is about whether the
implementation matches the design intent, not about pedagogical
outcomes.

---

## Group 1: Does the implementation match the design intent?

The system's design translates literature-grounded claims into
specific, testable behaviors. These questions ask whether the
implementation actually produces that behavior, not whether the
underlying pedagogical claim is true.

**RQ1 — Does trajectory information reach the role agent, or only the state label?**
ADR 0003 requires the classifier to describe trajectory in its
reasoning "not as an additional field, but as part of the
classification's justification" specifically so role agents have that
context. `docs/pipeline.md` confirms the orchestrator receives
`classification_reasoning` as free text, not `trajectory` as a
structured field. *Answerable now*: run the same `state=stalled` fixture
with `trajectory=declining` vs. a hypothetical `trajectory=stable`
variant and check whether the orchestrator's role selection or the
role agent's response actually differs, or whether trajectory is
present in the reasoning text but never acted on.

**RQ2 — Does `participation_balance` ever reach the orchestrator as a signal, or does role selection happen on `state` alone?**
Confirmed as an open gap twice already: the `dominated` ADR-0023
fixture and the independent `docs/threads/dominated.json`
design-tension probe (`all-tests.csv` rows 08, 15) both
found the orchestrator selecting Social based on state, with no
evidence `participation_balance` reached its context as a structured
signal. *Answerable now* — this is confirmatory work on an already
observed pattern, not a new experiment: instrument the orchestrator's
actual prompt input across a larger set of runs and check whether
`participation_balance`/`discourse_quality`/`inquiry_phase` ever appear
outside the free-text reasoning field.

**RQ3 — Does the "one action per intervention" constraint actually hold, or do responses drift toward combining actions?**
ADR 0003, Phase 3, constraint 1: never combine multiple actions in one
message. No current test checks this — `assertions.py`'s structural
checks cover non-empty text, known technique, confidence range, and
`post_to_thread` coherence, not this constraint specifically. *Needs
new work*: a rule check (or LLM-judge rubric dimension) for
single-action responses, run against existing generated responses.

**RQ4 — Does the moderator role actually behave as "last resort," or does the orchestrator reach for it on the first attempt?**
ADR 0003's facilitation/moderation split, and tension #12
(`docs/experiments.md`) both name this as an open question. One
design-tension probe (`hostile_then_silent`) found Social selected over
Moderator on a conflictive thread — a single data point, not a
pattern. *Needs more runs*: repeat across more conflictive-state
fixtures and models to see if this holds generally or was
model/scenario-specific.

---

## Group 2: Architecture and reliability

**RQ5 — How much does the technique-repertoire ordering bias actually move role-agent selection?**
ADR 0016 names LLM primacy bias as a known, reasoned-about,
**unmitigated** risk: 30 techniques in one fixed order
(organizational→intellectual→social→affective→moderator), so social/
affective agents read 13 other roles' techniques before their own.
The `state` filter parameter on `get_techniques()` exists but is
unused. *Needs new work, but cheap*: re-run the existing 8 fixtures
with the technique list order shuffled (or reversed) and compare
technique-selection distribution against the current fixed order,
per role, per model.

**RQ6 — Does the schema-echo failure mode correlate with extraction mode, model family, or model size?**
`docs/experiments/models.md` documents "schema-echo" (model returns the
JSON *schema* instead of an *instance*) across both ToolOutput and
PromptedOutput modes, and found tool support necessary but not
sufficient (`deepseek-r1:14b` has tool support but still echoes
intermittently) and parameter count not predictive (`llama3.1:8b`, 8B,
outperformed `mistral-nemo:12b`, 12B). *Partially answerable now*: this
data already exists across ~16 models in `docs/experiments/results/` —
a proper cross-tabulation (extraction mode × model family × schema-echo
rate) hasn't been written up, only individual observations in
`models.md`.

**RQ7 — Do weaker/smaller models show more ordering-bias-driven role skew than stronger ones?**
Synthesizes RQ5 and RQ6: if smaller models are both more prone to
schema-echo and more susceptible to primacy bias in long option lists,
does the technique selection of weak models skew toward
organizational/intellectual (the first two categories in the fixed
list) more than strong models do, independent of the actual state?
*Needs new work*: requires the RQ5 shuffle experiment run across the
full model roster, not just current-order data.

**RQ8 — Does graceful degradation actually produce a usable partial result under real failure conditions, or only under the exceptions it was designed for?**
ADR 0032: Intervention/Orchestrator/Role nodes catch exceptions and
return a partial `PipelineResult`; Classification does not (by design —
no useful data exists if it fails). *Needs new work*: fault-injection
tests (mock a timeout, a malformed-schema exception, and a network
error at each node) confirming the partial result is actually returned
and is coherent, not just that no crash occurs.

**RQ9 — Does the pipeline's retry loop ever hit `max_orchestrator_retries` without producing a valid response, and what happens then?**
`docs/pipeline.md`: retry path is ResponseEval→Orchestrator→Role→
ResponseEval, bounded by `max_orchestrator_retries` (default 1). What
the system does when retries are exhausted and rule checks still fail
is not documented or tested. *Needs new work*: a scenario engineered to
fail rule checks repeatably (e.g. forcing evaluative language) to
observe the exhausted-retry path directly.

---

## Group 3: Evaluation methodology itself

**RQ10 — Does classification accuracy hold across academic domains, or is it an artifact of the single domain tested?**
ADR 0023 explicitly chose one domain (AI ethics) for all 8 fixtures,
disclosed as a limitation: "los temas elegidos pueden estar
representados de forma desigual en los datos de entrenamiento de
distintos modelos." *Needs new fixtures*: parallel fixtures in at least
one different domain (e.g. a humanities or a purely technical/STEM
topic) to check whether compatibility tiers and classification accuracy
hold or shift.

**RQ11 — Does a model that "passes" a fixture do so by reasoning, or by a shortcut correlated with message count?**
Also an explicitly disclosed negative in ADR 0023: a model could
classify `stalled` correctly because "it has few messages" and `active`
correctly because "it has many," while failing a thread that's busy
but stalled on substance. None of the 8 fixtures currently test this
directly. *Needs a new fixture*: a thread with high message count but
low discourse quality (already partially covered by
`shallow_discourse`, but that one has distributed participation and
formulaic content — not high volume; a dedicated
high-volume-low-substance fixture would isolate the message-count
confound specifically).

**RQ12 — What is the actual agreement rate between the structural-assertion layer and self-reported confidence?**
ADR 0028: self-reported confidence as an evaluation parameter. Layer 1
(`assert_facilitation_response`) is implemented but has no direct unit
test (`all-tests.csv` row 27) and there's no existing
analysis of whether high self-reported confidence correlates with
passing structural checks. *Answerable now, no new infrastructure
needed*: correlate confidence values against assertion pass/fail across
existing run data.

**RQ13 — Confirmed decision: who judges, and what does that mean for the eval roster?**
ADR 0020 requires the judge to differ from every evaluated model.
The judge is GPT-5.6 Sol, used through a Codex session and identified in
the artifacts as `codex:gpt-5.6-sol`. It is not part of the current
evaluation roster, so GPT-4o, Claude, DeepSeek, Ministral and Qwen can
remain in the comparison. Each judge run must preserve the rubric,
prompt, model identifier, date and structured scores because this is an
assisted evaluation, not an automatic call made by the application.

---

## Group 4: What the real bugs found this session imply

Not "did we find bugs" (that's `TODO.md`'s job) — what they reveal
about testing an LLM-agent system specifically, which is itself a
legitimate methodology question for the thesis.

**RQ14 — What fraction of this system's failure surface is in tool-call plumbing rather than model output quality?**
The `flag_content` bug (Moderator's escalation tool calling a method
that existed on no backend) crashed with an `AttributeError` — the
model did everything right (correct role, correct tool call); the
failure was entirely in the code the tool called into. This is a
different failure class from "the LLM produced a bad response," and
standard LLM-output evaluation (Layers 1-3 of ADR 0020) wouldn't catch
it — only integration-level testing would. *Answerable now*: audit how
many of this project's other tool-registered functions (across all 5
role agents) have direct test coverage at the tool-call level, not just
prompt-wiring level.

**RQ15 — How much of the model-comparison data is quietly wrong because of the empty-string error bug?**
Before the fix, a thread that failed with an empty-message exception
(e.g. a bare `asyncio.TimeoutError`) was silently counted as a success
in every historical run. *Needs an audit*: re-derive `error_count` /
`completion_count` for every run in `docs/experiments/results/`
using the now-fixed `normalize_error`/`thread_view` logic (already
correct on read, since `thread_view` recomputes from raw records — so
this is really: has anyone re-generated the summary tables and model
comparison writeups that were produced from the old, silently-wrong
numbers?).

---

## Not included here

Design questions that are genuinely open but need infrastructure that
doesn't exist yet (LLM-as-judge rubric, human annotation) are tracked
in `docs/TODO.md`'s "Evaluation framework" section, not duplicated
here — those are prerequisites, not experiments to run against the
current system.
