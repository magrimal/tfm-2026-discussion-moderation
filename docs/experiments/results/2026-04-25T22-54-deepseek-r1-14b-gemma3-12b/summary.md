# Model Comparison — Experiment Summary

**Date**: 2026-04-26 00:00 UTC
**Models**: 2
**Threads**: 6
**Total runs**: 12

## Results by model

### `ollama:deepseek-r1:14b`

- Runs: 6 (4 ok, 2 errors)
- Avg duration: 244.6s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | stalled | never_started | instructor_centered | False | - | - | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | - |
| stalled — *Open source licensing in AI research* | new | never_started | distributed | False | - | - | - |
| conflictive — *Regulation of AI systems in the EU* | stalled | declining | dominated | True | intellectual | - | - |
| convergent — *Explainability vs. accuracy tradeoff* | active | stable | distributed | False | - | - | - |
| off_topic — *Environmental impact of training large models* | stalled | declining | instructor_centered | True | organizational | - | - |

<details><summary>new: full pipeline output</summary>

**Classification reasoning**

The thread has only one post from the instructor and no subsequent responses. This makes it stalled as there's no engagement beyond the initial prompt. The trajectory is 'never_started' since real exchange hasn't occurred. Participation is dominated by the instructor, hence 'instructor_centered.' Discourse quality is formulaic since the single post lacks depth or student contributions. It remains in the triggering phase as questions have been posed but not addressed.

**Intervention reasoning**

The thread has only one post from the instructor and no subsequent responses, indicating it is in the 'never_started' trajectory. There is no evidence of a genuine blockage such as repeated unproductive loops or explicit confusion. Intervening now could disrupt productive struggle and might be premature given the early stage of the discussion.

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The discussion thread is active with posts exchanged within the expected time window, showing consistent engagement. The trajectory is stable as all contributions are timely without signs of decline. Participation is distributed among multiple students and the instructor, with balanced exchanges. Discourse quality is substantive as each post provides reasoning or examples building on prior points. The inquiry phase is exploration, with participants sharing perspectives on bias sources but not yet integrating ideas into conclusions.

**Intervention reasoning**

The discussion thread is actively engaged with timely contributions from multiple participants, including substantive posts that build on each other. The stable trajectory indicates consistent engagement without signs of decline or blockage. Since there's no evidence of unproductive loops or explicit confusion, and the thread remains active with meaningful exchanges, intervention is unnecessary.

</details>

<details><summary>stalled: full pipeline output</summary>

**Classification reasoning**

The discussion thread has two initial posts: an opening question from Prof. García and a responding comment from Elena. The state is 'new' because there are no further replies beyond the initial exchange. The trajectory is 'never_started' as only two posts exist with no subsequent activity indicating ongoing engagement. Participation balance is 'distributed' since both instructor and student have contributed, without dominance by one participant or excessive focus on the instructor alone. Discourse quality is 'substantive' because both posts offer reasoned perspectives: Prof. García presents a nuanced question about AI model release under open-source licenses, considering reproducibility versus potential misuse. Elena's response thoughtfully weighs the importance of open-source for science against the need for limitations. The inquiry phase is 'triggering' as the thread has just begun with an exploratory question and minimal response, suggesting the discussion is still in its early stages of posing questions rather than developing or integrating ideas further.

**Intervention reasoning**

The thread is in its initial stage with two posts showing engagement, but no evidence of blockage or decline yet. The trajectory indicates it's just beginning and silence isn't an issue since participation is minimal but balanced. Intervention could disrupt the natural development process.

</details>

<details><summary>conflictive: error</summary>

**Error**

```
status_code: 400, model_name: deepseek-r1:14b, body: {'message': 'registry.ollama.ai/library/deepseek-r1:14b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/deepseek-r1:14b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>convergent: full pipeline output</summary>

**Classification reasoning**

The thread is active with posts exchanged within the expected time frame. Engagement has been stable, with consistent participation among students and the instructor. The participation is distributed as multiple individuals contribute meaningfully, sharing perspectives and building on each other's ideas. The discourse quality is substantive as participants provide reasoning and evidence to support their points, such as Hana citing GDPR requirements and Julia referencing recent research on SHAP and LIME. The thread is in the integration phase as participants synthesize different viewpoints, connecting the importance of explainability in high-stakes domains with the practical implications for model selection noted by Ivan.

**Intervention reasoning**

The thread is classified as active with stable and consistent participation among students and the instructor. The discussion has reached a mature phase where participants are integrating different viewpoints, showing deep understanding without signs of confusion or blockage. There isn't evidence of genuine blockage or decline in engagement that would warrant an intervention. Instead, allowing the thread to progress naturally maintains student ownership and prevents unnecessary disruption.

</details>

<details><summary>off_topic: error</summary>

**Error**

```
status_code: 400, model_name: deepseek-r1:14b, body: {'message': 'registry.ollama.ai/library/deepseek-r1:14b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/deepseek-r1:14b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

### `ollama:gemma3:12b`

- Runs: 6 (0 ok, 6 errors)
- Avg duration: 407.8s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | ERROR | - | - | - | - | - | - |
| active — *Algorithmic bias in hiring systems* | ERROR | - | - | - | - | - | - |
| stalled — *Open source licensing in AI research* | ERROR | - | - | - | - | - | - |
| conflictive — *Regulation of AI systems in the EU* | ERROR | - | - | - | - | - | - |
| convergent — *Explainability vs. accuracy tradeoff* | ERROR | - | - | - | - | - | - |
| off_topic — *Environmental impact of training large models* | ERROR | - | - | - | - | - | - |

<details><summary>new: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ...re the topic further.'}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>active: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>stalled: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ... further interaction."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>conflictive: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ... escalating conflict."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>convergent: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ...the initial question."}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>off_topic: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
6 validation errors for ClassificationResult
state
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
trajectory
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
participation_balance
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
discourse_quality
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
inquiry_phase
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'state': ...ue\n        selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

## Cross-model comparison by thread

### new — Privacy implications of large language models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | stalled | False | - | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

### active — Algorithmic bias in hiring systems

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | active | False | - | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

### stalled — Open source licensing in AI research

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | new | False | - | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

### conflictive — Regulation of AI systems in the EU

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | stalled | True | intellectual | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

### convergent — Explainability vs. accuracy tradeoff

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | active | False | - | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

### off_topic — Environmental impact of training large models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:deepseek-r1:14b` | stalled | True | organizational | - |
| `ollama:gemma3:12b` | ERROR | - | - | - |

## Observations

*(Fill in after reviewing results.)*

## Conclusions

*(Fill in after reviewing results.)*