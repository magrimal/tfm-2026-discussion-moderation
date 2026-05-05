# Model Comparison — Experiment Summary

**Date**: 2026-05-03 18:22 UTC
**Models**: 10
**Threads**: 6
**Total runs**: 3

## Results by model

### `ollama:qwen2.5:14b`

- Runs: 3 (2 ok, 1 errors)
- Avg duration: 89.5s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | new | never_started | instructor_centered | False | - | - | 1.00 | 1.00 | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | 1.00 | 0.95 | - |
| stalled — *Open source licensing in AI research* | new | never_started | dominated | - | - | - | 0.90 | - | - |

<details><summary>new: full pipeline output</summary>

**Classification reasoning**

The thread has one initial post by the instructor posing a prompt for discussion. No student posts have been made in reply, so it is classified as 'new'. Because there are no replies generating engagement patterns, the trajectory category defaults to never_started. The participation balance reflects that only an opening prompt has come from the instructor without any dialogue back yet; hence, 'instructor_centered' status. Discourse quality is assessed as formulaic since students have not contributed substantive remarks. Lastly, it's in a 'triggering' phase as questions and problems are outlined by the professor but response actions aren't seen.

**Intervention reasoning**

The thread has only an initial instructor prompt with no student responses yet, classified as 'new' and never_started trajectory. Current silence does not indicate blockage but is expected at this stage before students have time to think through the question and respond.

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The thread has seen four posts in just over a day, indicating active engagement focused on the topic of algorithmic bias in hiring systems. Contributions are substantive with reasoning and real-world case studies cited by participants who build connections within their postings (e.g., Carlos references both Alice's Amazon example and Bob's proxy variable concern). The trajectory is stable but has started well – more activity could signal growth if it continues, or a plateau if it stabilizes here. Participation balance is distributed with four distinct voices contributing evenly without an instructor response driving engagement.

**Intervention reasoning**

The discussion is currently active with four posts made over a short period of time (around 8 hours), showing engaged and constructive dialogue among students. The contributions are substantial and show evidence of depth and connection-building between points raised. Students appear to be addressing the topic thoroughly without explicit roadblocks or confusion. Since there's stable engagement, it would likely disrupt their process if I intervened now.

</details>

<details><summary>stalled: error</summary>

**Error**

```
status_code: 400, model_name: qwen2.5:14b, body: {'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

### `ollama:mistral-nemo:12b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:llama3.1:8b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:gemma2:9b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:phi4`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:gemma3:12b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:deepseek-r1:14b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:mistral`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:llama3.2`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### `ollama:gemma3:4b`

- Runs: 0 (0 ok, 0 errors)
- Avg duration: 0.0s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Cross-model comparison by thread

### new — Privacy implications of large language models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | new | False | - | - |

### active — Algorithmic bias in hiring systems

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |

### stalled — Open source licensing in AI research

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | new | - | - | - |

### conflictive — Regulation of AI systems in the EU

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |

### convergent — Explainability vs. accuracy tradeoff

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |

### off_topic — Environmental impact of training large models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |

## Observations

*(Fill in after reviewing results.)*

## Conclusions

*(Fill in after reviewing results.)*