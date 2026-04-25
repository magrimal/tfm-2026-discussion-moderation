# Model Comparison — Experiment Summary

**Date**: 2026-04-25 17:36 UTC
**Models**: 2
**Threads**: 6
**Total runs**: 12

## Results by model

### `ollama:qwen2.5:14b`

- Runs: 6 (2 ok, 4 errors)
- Avg duration: 274.4s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new | new | never_started | instructor_centered | - | - | - | - |
| active | active | stable | distributed | False | - | - | - |
| stalled | new | never_started | instructor_centered | - | - | - | - |
| conflictive | stalled | declining | dominated | - | - | - | - |
| convergent | active | declining | distributed | False | - | - | - |
| off_topic | off_topic | never_started | dominated | True | - | - | - |

<details><summary>new: error</summary>

**Error**

```
status_code: 400, model_name: qwen2.5:14b, body: {'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The thread remains active and stable with participants engaging in substantive discussion about algorithmic bias. Posts include real-world examples (e.g., Amazon's recruiting tool) and analysis of methodological challenges like proxy variables, causal modeling, and fairness metrics. Participation is distributed across students, and the conversation moves towards deeper exploration rather than synthesis or resolution.

**Intervention reasoning**

The thread remains active with participants engaging deeply on the topic of algorithmic bias in hiring systems and discussing methods to address such biases. There is no indication of blockage or repeated unproductive loops. The conversation continues to evolve with new insights being shared by each participant.

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

<details><summary>conflictive: error</summary>

**Error**

```
status_code: 400, model_name: qwen2.5:14b, body: {'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'invalid message content type: <nil>', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>convergent: full pipeline output</summary>

**Classification reasoning**

The thread is currently active with recent posts, but engagement has slowed since the last post about a week ago, indicating a declining trend in activity. The participants are distributed among Hana, Ivan, Julia, and Prof. García, contributing substantively to the discussion on explainability vs accuracy tradeoffs within domain-specific contexts. They reference technical tools like SHAP and LIME, moving towards integration as ideas are interconnected regarding thresholds for balancing stakes with model requirements.

**Intervention reasoning**

The discussion remains active but with a slowing rate of engagement, particularly over the past week. The participants have not explicitly signaled confusion or blockage in their posts. There is ongoing substantive dialogue without repetitive loops or clear signs of hesitation. Therefore, no intervention appears necessary at this juncture to prevent potential disruption.

</details>

<details><summary>off_topic: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
1 validation error for RoleSelection
  Invalid JSON: expected value at line 1 column 1 [type=json_invalid, input_value='คณะกรรมก...มที่สุด.', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/json_invalid
```

</details>

### `ollama:phi4`

- Runs: 6 (0 ok, 6 errors)
- Avg duration: 0.1s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new | ERROR | - | - | - | - | - | - |
| active | ERROR | - | - | - | - | - | - |
| stalled | ERROR | - | - | - | - | - | - |
| conflictive | ERROR | - | - | - | - | - | - |
| convergent | ERROR | - | - | - | - | - | - |
| off_topic | ERROR | - | - | - | - | - | - |

<details><summary>new: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>active: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>stalled: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>conflictive: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>convergent: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>off_topic: error</summary>

**Error**

```
status_code: 400, model_name: phi4, body: {'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/phi4:latest does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

## Cross-model comparison by thread

### new

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | new | - | - | - |
| `ollama:phi4` | ERROR | - | - | - |

### active

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |
| `ollama:phi4` | ERROR | - | - | - |

### stalled

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | new | - | - | - |
| `ollama:phi4` | ERROR | - | - | - |

### conflictive

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | stalled | - | - | - |
| `ollama:phi4` | ERROR | - | - | - |

### convergent

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |
| `ollama:phi4` | ERROR | - | - | - |

### off_topic

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | off_topic | True | - | - |
| `ollama:phi4` | ERROR | - | - | - |

## Observations

*(Fill in after reviewing results.)*

## Conclusions

*(Fill in after reviewing results.)*