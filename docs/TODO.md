# TODO — Open items

**Last updated**: 2026-07-20

What's not covered yet. Fixed items are removed, not archived here —
check `git log` for what changed and when. Per-test-case detail (setup,
priority, how something was verified): `docs/experiments/test-sheets/`.

---

## Bugs

- [ ] Closed-thread guard only covers the `/runs/live/trigger` path
      (`router.py:733`). `POST /facilitate` and the eval runner
      (`eval_models.py`) can still run a closed thread through the full
      pipeline with nowhere for the response to go. Decide whether the
      guard belongs in `run_pipeline()` itself (covers every entry
      point) or needs duplicating per call site.
- [ ] Classification sub-dimensions (`participation_balance`,
      `discourse_quality`, `inquiry_phase`) reach the orchestrator only
      as free text inside `classification_reasoning`, not as structured
      fields — a `dominated` thread and a `distributed` one can look
      identical to it (`docs/experiments.md` tension #6).
- [ ] Playground defaults to the real `OpenEdXBackend` regardless of
      whether `--thread-id` was given, so any backend-calling tool
      (`post_comment`, `get_course_context`, `flag_content`) fires a
      real HTTP call against synthetic post IDs when running a thread
      from a JSON file. Pass `lms_backend=None` when no `--thread-id`
      is supplied (`docs/experiments.md`, `overt_attack`).

## Testing gaps

- [ ] Graph control flow (node routing, the rule-check retry loop in
      `RoleNode`, the `max_orchestrator_retries` cutoff) has no fast,
      deterministic test — only real-LLM eval runs exercise it.
- [ ] `assert_facilitation_response` (ADR 0020 Layer 1) has no direct
      unit test.
- [ ] 10 of 14 REST endpoints have no request-level (`TestClient`)
      coverage.
- [ ] No automated frontend test suite exists at all — no test script
      in `dashboard/package.json`, no `*.test.*`/`*.spec.*` files.
- [ ] S3 vs. filesystem run-result backend parity untested (both are
      tested individually, not against each other).
- [ ] HTTP Basic Auth untested against the real deployed idril/EC2
      servers — only via `TestClient`.
- [ ] JWT expiry mid-run untested (a live LMS run that outlives its
      1-day token).
- [ ] Concurrent runs (two triggered at once) untested on the
      dashboard.
- [ ] `repeat_intervention` scenario has no harness to pre-populate
      history before the run — more tractable now than it used to be,
      since history recording itself works.

## Model × fixture coverage gaps

Tracked in `test-sheets/all-tests.csv`, `Section = Pipeline
Correctness`, filter `Environment` to `idril` / `EC2` / `OpenRouter
free tier` — every row there is `Pass/Fail = Not started` since idril
and EC2's live run history was cleared 2026-07-20. This is a full
fresh 8-fixture campaign on every currently-configured model, needed
before writing the thesis results section — not just closing a
historical gap. Don't duplicate the row list here.

## Missing features

- [ ] Playground `--thread-id` flag to call `backend.get_thread(id)`
      instead of loading from JSON
- [ ] `get_course_materials()` returns `[]`, no API target defined yet
- [ ] `DiscussionThread.last_activity_at` collected from the LMS but
      not included in `format_thread()`

## Evaluation framework

- [x] ~~Decide the judge model~~ — resolved 2026-07-20: Claude judges,
      Claude models get excluded from the evaluated roster instead
      (rather than excluding individual responses after the fact).
- [x] ~~Remove `claude-sonnet-4.5` from EC2's `EVAL_MODELS`~~ — done
      2026-07-20 (`.env.ec2`). Also fixed `ec2-restart` to scp
      `.env.ec2` on every deploy, not just `ec2-setup` (same class of
      bug already fixed for idril) — otherwise this change wouldn't
      reach the real server. Not yet deployed to the live EC2 host.
- [ ] LLM-as-judge rubric scoring — blocked on the six-dimension
      rubric (ADR 0020). Judge model decision is no longer blocking
      (see above).
- [ ] Human annotation calibration sample — blocked on recruiting two
      annotators with academic facilitation background

## Thesis documentation

- [ ] Audit `agent-memory/architecture-notes.md` for completeness
- [ ] Check `docs/literature/papers.csv` reflects current literature
      scope
- [ ] No empirical evaluation section in the thesis draft yet
- [ ] Check `agent-memory/terminology.md` against the evaluation
      rubric terms
- [ ] `docs/experiments/models.md` predates the 8-fixture set (still
      says "six thread scenarios")
