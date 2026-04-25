# Model Comparison — Experiment Summary

**Date**: 2026-04-25 21:04 UTC
**Models**: 3
**Threads**: 6
**Total runs**: 18

## Results by model

### `ollama:llama3.1:8b`

- Runs: 6 (6 ok, 0 errors)
- Avg duration: 53.7s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | new | never_started | distributed | False | - | - | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | - |
| stalled — *Open source licensing in AI research* | stalled | stable | dominated | False | - | - | - |
| conflictive — *Regulation of AI systems in the EU* | stalled | declining | dominated | False | - | - | - |
| convergent — *Explainability vs. accuracy tradeoff* | active | stable | distributed | False | - | - | - |
| off_topic — *Environmental impact of training large models* | stalled | declining | dominated | False | - | - | - |

<details><summary>new: full pipeline output</summary>

**Classification reasoning**

The thread has just been created by Prof. García, introducing the topic of privacy implications of large language models. No posts have been made yet, so engagement pattern and discourse quality are not applicable at this point. The inquiry phase is triggering, as a question or problem has been posed.

**Intervention reasoning**

No posts have been made yet, it's still within the expectation of an introduction and setup for discussion; initial inquiry phase as a trigger indicates potential but no concrete evidence of need or blockage.

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The discussion started with a question by Prof. García, which was responded to by Alice with a specific real-world example of algorithmic bias in Amazon's recruiting tool. Bob added another relevant case study from ProPublica's analysis of COMPAS and its findings on proxy variables. Carlos then proposed an alternative approach using counterfactual fairness, but countered by Diana who pointed out the practical challenges of implementing it.

**Intervention reasoning**

The discussion trajectory shows a genuine engagement on the topic, with students exploring different aspects of algorithmic bias in ML hiring systems. Responses are thoughtful and build upon each other's ideas, indicating a productive discussion rhythm. Intervening now would disrupt this activity without clear evidence of blockage or genuine need.

</details>

<details><summary>stalled: full pipeline output</summary>

**Classification reasoning**

The thread has been stalled since March 8, with no new posts for over a month. Initially, the topic seemed to stimulate some interest, as Prof. García posed an open-ended question that Elena responded to shortly after. However, their exchange appears to have plateaued without further development or engagement from other participants. While there is potentially valuable discussion to be had on the trade-offs between openness and safety in AI research, the current state of the thread suggests it may require some intervention to revive it.

**Intervention reasoning**

The thread has been stalled for over a month with only two initial posts, suggesting that the topic may not be of interest to the participants or they might have reached an impasse. However, given the initial enthusiasm and thoughtful responses from Elena and Prof. García, caution suggests that some additional time should pass to see if there's a quiet storm brewing.

</details>

<details><summary>conflictive: full pipeline output</summary>

**Classification reasoning**

The thread started with a potentially thought-provoking question from Prof. García on the effectiveness of the EU AI Act's risk classification approach. However, Frank's initial aggressive response deviated the conversation into a simplistic 'regulation vs innovation' dichotomy. Grace attempted to steer the discussion back on track with her nuanced explanation, but Frank continued to use dismissive and competitive language, causing the thread to diverge further. The last posts from both Frank and Grace have an almost confrontational tone, closing moves that undermine constructive exchange. Now, there has been no new post in over 48 hours, signaling a stalled state.

**Intervention reasoning**

The thread has deviated into a personal attack between Frank and Grace, but there hasn't been a clear indication of genuine blockage or unproductive loops lasting for an extended period. Furthermore, while there has been aggression in the tone, it is not sufficient to warrant intervention at this stage without signs of participation collapse or explicit confusion. Intervening now may disrupt productive activity.

</details>

<details><summary>convergent: full pipeline output</summary>

**Classification reasoning**

The discussion remains active with new posts, and the pace of participation has stabilized after the initial flurry. Participation is distributed among four different contributors, with no single voice dominating the conversation. Posts are substantive and evidence-backed, showing understanding of the topic. In terms of practical inquiry, this thread has moved beyond triggering or exploration phases and is now in a state of integration, where participants (here, Prof. García, Hana, Ivan, Julia) use each other's perspectives to build on ideas. The real question posed by Julia has sparked thoughtful responses from Hana, which indicates the thread remains convergent rather than diverging.

**Intervention reasoning**

The discussion remains active with new posts, participants are engaging in a convergent manner, building on each other's ideas and refining their understanding of the tradeoff between explainability and accuracy. Given that there is no evidence of genuine blockage or impasse, and the conversation appears to be progressing as expected towards integrating different perspectives, interventions would disrupt this productive activity.

</details>

<details><summary>off_topic: full pipeline output</summary>

**Classification reasoning**

The discussion appears to have stalled due to the lack of engagement in meaningful conversation. The last few posts focus on showcasing personal uses and experiences with GPT-4, rather than addressing the topics proposed (energy consumption and sustainable AI practices). Kevin and Laura's responses have become mostly formulaic and lacking in reasoning or substance. The initial question posed by Prof. García is still unanswered.

**Intervention reasoning**

The discussion has stalled but not shown clear evidence of blockage or impasse. The lack of engagement with the topic and instead focus on showcasing personal uses of GPT-4 may indicate a normal discussion rhythm rather than a genuine need for intervention. Furthermore, intervening now could disrupt productive activity in progress.

</details>

### `ollama:gemma2:9b`

- Runs: 6 (4 ok, 2 errors)
- Avg duration: 81.2s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | new | never_started | instructor_centered | - | - | - | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | - |
| stalled — *Open source licensing in AI research* | new | never_started | instructor_centered | False | - | - | - |
| conflictive — *Regulation of AI systems in the EU* | conflictive | declining | dominated | True | intellectual | - | - |
| convergent — *Explainability vs. accuracy tradeoff* | active | growing | distributed | False | - | - | - |
| off_topic — *Environmental impact of training large models* | active | stable | distributed | False | - | - | - |

<details><summary>new: error</summary>

**Error**

```
Exceeded maximum retries (3) for output validation
```

**Raw model output**

```
2 validation errors for InterventionDecision
should_intervene
  Field required [type=missing, input_value={'properties': {'should_i...m technique selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
reasoning
  Field required [type=missing, input_value={'properties': {'should_i...m technique selection.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
```

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The discussion is actively engaging with the prompt. Participants are building upon each other's ideas and introducing relevant case studies. Several students have directly addressed Professor Garcia's questions, and the conversation flows logically from one contribution to the next.  The last post poses a thoughtful question about appropriate fairness metrics, indicating the exploration phase of inquiry.

**Intervention reasoning**

The discussion is actively engaging with the prompt, participants are building upon each other's ideas, and there's a logical flow of conversation.  No evidence of blockage or unproductive loops.

</details>

<details><summary>stalled: full pipeline output</summary>

**Classification reasoning**

The discussion has only two posts - an initial question from the professor and a brief response. There's no student-to-student interaction, suggesting the thread hasn't taken off. However, both the opening post and Elena's reply demonstrate engagement with the topic conceptually, indicating potential for substantive contributions.

**Intervention reasoning**

The thread is new with only two posts, one from the professor initiating the discussion and another thoughtful response from Elena. While there isn't student-to-student interaction yet, both posts show engagement with the topic. This warrants observation rather than immediate intervention as the potential for a productive discussion is present.

</details>

<details><summary>conflictive: error</summary>

**Error**

```
status_code: 400, model_name: gemma2:9b, body: {'message': 'registry.ollama.ai/library/gemma2:9b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': 'registry.ollama.ai/library/gemma2:9b does not support tools', 'type': 'invalid_request_error', 'param': None, 'code': None}
```

</details>

<details><summary>convergent: full pipeline output</summary>

**Classification reasoning**

The discussion is actively progressing with participants building on each other's points and exploring the complexities of the explainability-accuracy tradeoff. Each post contributes meaningfully to the conversation, avoiding simplistic or formulaic statements. While not yet converged on a definitive answer, the thread demonstrates a healthy exchange of ideas in an exploratory phase.

**Intervention reasoning**

The discussion is actively progressing with students building upon each other's ideas and exploring the complexities of the topic. There's no evidence of blockage or unproductive loops.

</details>

<details><summary>off_topic: full pipeline output</summary>

**Classification reasoning**

The thread is actively progressing with posts exchanged within the expected time window. Participants are sharing perspectives on the potential benefits (image generation, coding assistance) of GPT-4, but the initial question regarding environmental impact hasn't been directly addressed yet. Discourse quality is mixed as some contributions are focused on features and less on the core topic. The thread is currently exploring user experiences with GPT-4 before potentially reaching a synthesis or resolution.

**Intervention reasoning**

The thread is actively progressing with students discussing GPT-4's features. While the initial question about environmental impact hasn't been directly addressed, this is normal early discourse development.  It's too early to intervene as the discussion may naturally gravitate towards the core topic.

</details>

### `ollama:deepseek-r1:14b`

- Runs: 6 (0 ok, 6 errors)
- Avg duration: 0.0s

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
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

<details><summary>active: error</summary>

**Error**

```
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

<details><summary>stalled: error</summary>

**Error**

```
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

<details><summary>conflictive: error</summary>

**Error**

```
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

<details><summary>convergent: error</summary>

**Error**

```
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

<details><summary>off_topic: error</summary>

**Error**

```
status_code: 404, model_name: deepseek-r1:14b, body: {'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

**Raw model output**

```
{'message': "model 'deepseek-r1:14b' not found", 'type': 'not_found_error', 'param': None, 'code': None}
```

</details>

## Cross-model comparison by thread

### new — Privacy implications of large language models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | new | False | - | - |
| `ollama:gemma2:9b` | new | - | - | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

### active — Algorithmic bias in hiring systems

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | active | False | - | - |
| `ollama:gemma2:9b` | active | False | - | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

### stalled — Open source licensing in AI research

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | stalled | False | - | - |
| `ollama:gemma2:9b` | new | False | - | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

### conflictive — Regulation of AI systems in the EU

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | stalled | False | - | - |
| `ollama:gemma2:9b` | conflictive | True | intellectual | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

### convergent — Explainability vs. accuracy tradeoff

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | active | False | - | - |
| `ollama:gemma2:9b` | active | False | - | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

### off_topic — Environmental impact of training large models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:llama3.1:8b` | stalled | False | - | - |
| `ollama:gemma2:9b` | active | False | - | - |
| `ollama:deepseek-r1:14b` | ERROR | - | - | - |

## Observations

*(Fill in after reviewing results.)*

## Conclusions

*(Fill in after reviewing results.)*