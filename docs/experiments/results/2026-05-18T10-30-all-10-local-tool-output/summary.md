# Model Comparison — Experiment Summary

**Date**: 2026-05-19 08:05 UTC
**Models**: 10
**Threads**: 8
**Total runs**: 12

## Results by model

### `ollama:qwen2.5:14b`

- Runs: 8 (8 ok, 0 errors)
- Avg duration: 70.7s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | stalled | never_started | dominated | False | - | - | 1.00 | 1.00 | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | 1.00 | 1.00 | - |
| stalled — *Open source licensing in AI research* | active | never_started | dominated | False | - | - | 1.00 | 1.00 | - |
| conflictive — *Regulation of AI systems in the EU* | conflictive | never_started | dominated | True | social | Acknowledge and Redirect | 1.00 | 1.00 | 1.00 |
| convergent — *Explainability vs. accuracy tradeoff* | active | stable | distributed | False | - | - | 0.96 | 1.00 | - |
| off_topic — *Environmental impact of training large models* | stalled | never_started | dominated | True | organizational | redirect | 1.00 | 1.00 | 0.95 |
| shallow_discourse — *Transparency requirements for AI decision systems* | convergent | stable | dominated | False | - | - | 1.00 | 1.00 | - |
| dominated — *Federated learning as a privacy-preserving approach* | active | stable | dominated | False | - | - | 1.00 | 1.00 | - |

<details><summary>new: full pipeline output</summary>

**Classification reasoning**

The post by Prof. García has been unanswered since it was posted over two months ago, indicating no follow-up activity (stalled). Given that there are no replies to the initial question, the thread hasn't generated any exchange at all - never_started. As there are only posts from one participant, participation is dominated by a single voice (dominated). The discourse quality defaults to formulaic since no additional posts have given it qualities of substantive discussion; however, this situation could change if engagement begins.

**Intervention reasoning**

There is no evidence of blockage or impasse since there have been no replies indicating students are stuck or confused. The silence could be due to various factors such as time required for reflection or other commitments. Given the lack of follow-up activity over two months and dominated participation from Prof. García alone, intervention would interrupt the natural rhythm of discussion rather than address a genuine blockage.

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The thread has seen several posts that build on each other, with contributions from multiple participants. It explores different aspects of algorithmic bias without synthesizing them into conclusions yet. The engagement has remained consistent since the initial post.

**Intervention reasoning**

The thread shows consistent engagement across multiple posts that engage with each other's points and build upon them. Students are actively debating different aspects of algorithmic bias in hiring systems without signs of impasse or confusion.

</details>

<details><summary>stalled: full pipeline output</summary>

**Classification reasoning**

The current discourse is still at the triggering phase with only two posts. The discussion hasn't truly started yet, as per Chang & D-N-M (2019) criteria of engagement. It's formulaic due to a short exchange without in-depth reasoning; it's dominated by the initial post and one reply from Elena.

**Intervention reasoning**

The discussion thread has started with only two posts and shows no signs of impasse or confusion as per the criteria described by Chang & D-N-M (2019). There's a clear starting point but no deep engagement yet. It is too early to determine if there are genuine barriers to further development, so intervention at this stage could disrupt nascent discussion dynamics.

</details>

<details><summary>conflictive: full pipeline output</summary>

**Classification reasoning**

The thread has not yet entered a productive phase of discussion due to hostility between the participants. The interactions are superficial and adversarial rather than substantive. Posts are largely dismissive without reasoned argument, indicating formulaic discourse. Participation is dominated by two voices (Frank and Grace) with no indication of a positive direction towards exploration or integration.

**Intervention reasoning**

The discussion between Frank and Grace has turned adversarial without substantive argumentation or progress towards understanding different viewpoints on the EU AI Act’s regulatory approach. This hostile interaction pattern indicates a genuine need for intervention to prevent further deterioration of constructive dialogue.

**Role reasoning**

The discussion has turned hostile and dismissive between Frank and Grace without substantive contribution or exploration of differing viewpoints on the EU AI Act. A social intervention can encourage a more constructive conversation, acknowledge contributions positively, and model respectful interaction. Organizational and intellectual interventions might prematurely structure the debate or deepen thought processes respectively when the participants need to engage better first.

**Response reasoning**

The discussion is becoming antagonistic with each participant dismissing the other's viewpoint without substantiating their own opinion critically. By asking them to provide specific examples, it encourages a more respectful and focused dialogue on the EU AI Act’s merits and demerits.

**Response text**

Hi Frank and Grace, it sounds like there's some disagreement about how effective or necessary the EU AI Act is for regulating AI systems in Europe. Could you each point out one aspect of the act that you think showcases its strengths or weaknesses, so we can have a clearer picture? This would also help others understand your perspectives better.

</details>

<details><summary>convergent: full pipeline output</summary>

**Classification reasoning**

The thread is active with posts exchanged within expected timeframe and no stalls. Posts are well-spaced over two days, indicating stable engagement without growth or decline. Contributions come from multiple participants suggesting distributed participation, which is evident through diverse opinions on the application of explainability in various contexts. High-quality reasoning in posts suggests substantive discourse where contributions build upon each other—highlighting domain-specific applications and recent work balancing accuracy with explainability. The discussion reflects integration as ideas are connected across participant perspectives.

**Intervention reasoning**

The discussion thread is currently active with high-quality contributions from multiple participants. Posts are well-spaced over two days indicating stable and productive engagement. The latest post introduces a new perspective on balancing explainability and accuracy via recent advancements in interpretative techniques (SHAP, LIME). There are no signs of blockage or unproductive loops.

</details>

<details><summary>off_topic: full pipeline output</summary>

**Classification reasoning**

The discussion started but failed to address the original question about environmental costs of training large models. Participants deviated from the topic, focusing instead on new features unrelated to environmental concerns. There are no contributions that contribute substantively to the discussion or respond thoughtfully to Prof. García's initial prompt.

**Intervention reasoning**

The discussion has deviated from addressing environmental concerns of training large models and instead shifted towards discussing new features unrelated to the original prompt. There are no contributions contributing substantively to the environmental impact topic, indicating participants have not responded thoughtfully to Prof. García's initial question.

**Role reasoning**

The discussion has deviated from addressing environmental concerns of training large models and instead shifted towards discussing new features unrelated to the original prompt. An organizational role is appropriate here to redirect participants back to the topic and structure the conversation around the initial question posed by Prof. García.

**Response reasoning**

The discussion has diverged from addressing the prompt which asks for insights on balancing model capability with environmental cost, focusing instead on new features of GPT-4. The redirect technique is suitable to steer the conversation back towards the original topic.

**Response text**

Hi everyone! It looks like we've been focusing on some of GPT-4's new features, but let's circle back to Prof. García’s original question: How can we balance the model's capability with its environmental impact? Could you share any insights related to this topic?

</details>

<details><summary>shallow_discourse: full pipeline output</summary>

**Classification reasoning**

The thread has few active contributors (Mia, Noah, Olivia) who agree on the importance of transparency in AI decision-making, especially within a regulatory context. While engagement is consistent and there are clear agreements between participants, it does not involve deeper reasoning or questioning, indicating mixed discourse quality. The conclusion that regulation is necessary to enforce transparency seems widely accepted.

**Intervention reasoning**

The discussion shows agreement on the necessity of transparency in AI decision-making, particularly for high-risk systems like those in healthcare. There has been no explicit blockage or confusion indicated by participants. Engagement remains consistent among active contributors (Mia, Noah, Olivia) but lacks deeper questioning or elaboration. This suggests a natural ebb, rather than a genuine need for intervention.

</details>

<details><summary>dominated: full pipeline output</summary>

**Classification reasoning**

The thread has active contributions focused on the exploration of federated learning privacy guarantees and critiques, including discussions of gradient inversion attacks and differential privacy tradeoffs. The last posts engage with a deeper dive into fairness issues but have maintained engagement without additional new insights or conclusions over recent days post latest update. Marco's voice predominates, making participation rather dominated. Discourse is substantive.

**Intervention reasoning**

The thread remains active but the most recent contributions explore the same area of federated learning fairness without new insights or broader engagement beyond Marco and Nora. While Marco's insight is valuable, repeated focused exchange in a small subset isn't indicative of an impasse but suggests deeper consideration around fairness and privacy might be ongoing within these two students.

</details>

### `ollama:mistral-nemo:12b`

- Runs: 4 (4 ok, 0 errors)
- Avg duration: 86.1s

| Thread | State | Trajectory | Balance | Intervene | Role | Technique | c_conf | i_conf | r_conf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new — *Privacy implications of large language models* | stalled | declining | dominated | False | - | - | 0.95 | 1.00 | - |
| active — *Algorithmic bias in hiring systems* | active | stable | distributed | False | - | - | 0.95 | 1.00 | - |
| stalled — *Open source licensing in AI research* | stalled | never_started | instructor_centered | True | social | Redistribute_attention | 1.00 | 1.00 | 0.95 |
| conflictive — *Regulation of AI systems in the EU* | active | stable | distributed | False | - | - | 1.00 | 1.00 | - |

<details><summary>new: full pipeline output</summary>

**Classification reasoning**

The last post was over 48 hours ago with no new posts since, indicating a stalled state. Engagement has been declining as the most recent response is just a ' thanks' acknowledging another student's point but not building on it ('I agree'). The participation balance is dominated by Prof. García and Student B, while others have remained silent after their initial posts. Posts lack substantive discussion with no evidence of reasoning or connection to prior contributions.

**Intervention reasoning**

The discussion stalled over 48 hours ago due to lack of substantiveness ('I agree') rather than explicit confusion or repeated unproductive loops. While engagement has declined, it's not clear if students are genuinely blocked or simply require more time to consider their points. Given the silence might be a normal rhythm of asynchronous discussions, intervening now could disrupt potential productive activity.

</details>

<details><summary>active: full pipeline output</summary>

**Classification reasoning**

The thread is considered active as there has been at least one reply to the initial post, although the last post was over 6 hours ago. The trajectory is deemed stable because while engagement is consistent, it's not growing or declining rapidly. Participation balance is distributed with multiple students actively involved in discussion. Discourse quality is rated substantive as each post builds on prior contributions and shows evidence-based understanding of the topic. The inquiry phase is integration, where participants are building on each other's ideas to develop a shared understanding.

**Intervention reasoning**

The thread is active with continuous discussion over multiple posts from different students, indicating no genuine blockage or confusion. The participants are showing in-depth understanding and even proposing practical solutions. Intervention at this point could disrupt the productive flow of ideas.

</details>

<details><summary>stalled: full pipeline output</summary>

**Classification reasoning**

The only other reply after the initial post by Prof. García is from Elena, solely stating her opinion without addressing or building on the professor's post or any further participation. The last posts did not engage deeper into the topic and therefore there was no exploration of ideas yet nor integration.

**Intervention reasoning**

The discussion has been stalled since Elena's post with no further engagement. Although there was initial participation, the thread has not explored or integrated ideas beyond initial statements due to lack of follow-up posts addressing each other's viewpoints.

**Role reasoning**

The discussion has stalled due to lack of engagement and exploration of ideas beyond initial statements. The social role, which encourages participation and redistributes attention, is the best fit as it can reignite interaction among all participants without intruding too deeply into their thought processes or closing the discussion prematurely.

**Response reasoning**

The discussion has stalled after Elena's post. Using 'Redistribute_attention' encourages others to join the conversation, promoting inclusivity and balancing participation.

**Response text**

Hi everyone, we've not heard from you since Elena shared her thoughts! Let's continue discussing the tensions between openness and potential misuse. What are your views on this?

</details>

<details><summary>conflictive: full pipeline output</summary>

**Classification reasoning**

The thread is classified as active based on recent posts from Frank and Grace. The trajectory is stable, with ongoing direct exchange between the students. Participation balance is distributed across contributors after initial responses to Prof. García's post. Discourse quality is mixed: while Frank's posting was formulaic, Grace engaged substantively with Frank's viewpoint.

**Intervention reasoning**

The thread is Active as per recent posts from Frank and Grace, indicating normal discussion rhythm rather than evidence of blockage or genuine need. Intervening now may disrupt productive argumentation.

</details>

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
| `ollama:qwen2.5:14b` | stalled | False | - | - |
| `ollama:mistral-nemo:12b` | stalled | False | - | - |

### active — Algorithmic bias in hiring systems

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |
| `ollama:mistral-nemo:12b` | active | False | - | - |

### stalled — Open source licensing in AI research

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |
| `ollama:mistral-nemo:12b` | stalled | True | social | Redistribute_attention |

<details><summary>ollama:mistral-nemo:12b: response</summary>

**Response text**

Hi everyone, we've not heard from you since Elena shared her thoughts! Let's continue discussing the tensions between openness and potential misuse. What are your views on this?

</details>

### conflictive — Regulation of AI systems in the EU

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | conflictive | True | social | Acknowledge and Redirect |
| `ollama:mistral-nemo:12b` | active | False | - | - |

<details><summary>ollama:qwen2.5:14b: response</summary>

**Response text**

Hi Frank and Grace, it sounds like there's some disagreement about how effective or necessary the EU AI Act is for regulating AI systems in Europe. Could you each point out one aspect of the act that you think showcases its strengths or weaknesses, so we can have a clearer picture? This would also help others understand your perspectives better.

</details>

### convergent — Explainability vs. accuracy tradeoff

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |

### off_topic — Environmental impact of training large models

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | stalled | True | organizational | redirect |

<details><summary>ollama:qwen2.5:14b: response</summary>

**Response text**

Hi everyone! It looks like we've been focusing on some of GPT-4's new features, but let's circle back to Prof. García’s original question: How can we balance the model's capability with its environmental impact? Could you share any insights related to this topic?

</details>

### shallow_discourse — Transparency requirements for AI decision systems

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | convergent | False | - | - |

### dominated — Federated learning as a privacy-preserving approach

| Model | State | Intervene | Role | Technique |
| --- | --- | --- | --- | --- |
| `ollama:qwen2.5:14b` | active | False | - | - |

## Observations

*(Fill in after reviewing results.)*

## Conclusions

*(Fill in after reviewing results.)*