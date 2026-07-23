# LLM-as-judge summary

- Judge: `codex:gpt-5.6-sol`
- Evaluated interventions: 46
- Overall mean: 3.911/5
- Cases requiring review: 29
- Hallucinations detected: 27
- Evaluative/grading language: 1
- Unsafe moderation/publication: 6

## By model

| Model | n | Mean | Review | Hallucination | Evaluative | Unsafe |
|---|---:|---:|---:|---:|---:|---:|
| `ollama:ministral-3:14b` | 5 | 4.142 | 3 | 3 | 0 | 1 |
| `ollama:ministral-3:8b` | 13 | 3.337 | 9 | 7 | 0 | 1 |
| `ollama:qwen3.5:27b` | 2 | 4.771 | 1 | 1 | 0 | 0 |
| `ollama:qwen3.5:9b` | 2 | 2.500 | 2 | 2 | 0 | 1 |
| `openrouter:anthropic/claude-haiku-4.5` | 9 | 4.301 | 7 | 7 | 1 | 2 |
| `openrouter:openai/gpt-4o` | 9 | 4.315 | 2 | 2 | 0 | 0 |
| `openrouter:openai/gpt-4o-mini` | 6 | 3.958 | 5 | 5 | 0 | 1 |

The scores estimate ex-ante adequacy under the documented rubric. They do not measure effects on subsequent discussion or learning.

Only runs that generated an intervention were scored. Sample sizes therefore differ by model, and these means must not be interpreted as a controlled model ranking. DeepSeek produced no scoreable intervention before its EC2 run was cancelled.
