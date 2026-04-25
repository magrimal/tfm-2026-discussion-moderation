# Tested Models

All models evaluated against the six thread scenarios with PromptedOutput mode unless noted.

## Compatibility tiers

- **full**: completes all 6 threads including the role agent node (which requires tool calling)
- **partial**: passes classification and intervention nodes but fails at the role node when intervention is required (no tool support)
- **none**: too small to follow the output schema; returns the schema itself or malformed JSON

## Results

| Model | Family | Size | Tool support | Tier | Best score | Notes |
|---|---|---|---|---|---|---|
| `ollama:qwen2.5:14b` | Qwen 2.5 (Alibaba) | 14B | yes | full | 6/6 | Reference model for local runs |
| `ollama:mistral-nemo:12b` | Mistral Nemo (Mistral AI) | 12B | yes | full | 6/6 | |
| `ollama:llama3.1:8b` | Llama 3.1 (Meta) | 8B | yes | full | 6/6 | Tool support added in Llama 3.1 |
| `ollama:gemma2:9b` | Gemma 2 (Google) | 9B | no | partial | 4/6 | Fails when intervention triggers role node; Ollama confirms no tool support |
| `ollama:phi4` | Phi-4 (Microsoft) | 14B | no | partial | 5/6 | 5/6 because only 1 thread required role node; tool-calling mode gives 0/6 |
| `ollama:mistral:7b` | Mistral v0.3 (Mistral AI) | 7B | no | none | 0/6 | Returns schema instead of instance |
| `ollama:llama3.2` | Llama 3.2 (Meta) | 3B | no | none | 0/6 | Same pattern as mistral:7b |
| `ollama:gemma3:4b` | Gemma 3 (Google) | 4B | no | none | 0/6 | Same pattern as mistral:7b |
| `ollama:deepseek-r1:14b` | DeepSeek R1 (DeepSeek) | 14B | yes | pending | — | Reasoning model; produces `<think>` blocks before JSON — parse behavior with PromptedOutput TBD |
| `ollama:gemma3:12b` | Gemma 3 (Google) | 12B | yes | pending | — | Tool support confirmed in Gemma 3 release |
| `openrouter:openai/gpt-oss-120b:free` | GPT OSS 120B (OpenAI) | 120B | yes | partial-infra | 2/6 | 4 threads failed with null response from OpenRouter free tier rate limiting, not model failure; 2 completed threads show high quality output |

## Runs

| Directory | Models | Mode | Notes |
|---|---|---|---|
| `2026-04-24T15-51-baseline-5models` | qwen2.5:14b, phi4, mistral:7b, llama3.2, gemma3:4b | PromptedOutput | First run after PromptedOutput migration |
| `2026-04-25T17-10-5models-tool-calling` | same 5 | tool-calling | Pre-migration run; all models fail or degrade |
| `2026-04-25T18-49-mistral-nemo-12b` | mistral-nemo:12b | PromptedOutput | Isolated run after fixing provider format |
| `2026-04-25T20-49-llama31-8b-gemma2-9b` | llama3.1:8b, gemma2:9b | PromptedOutput | deepseek-r1:14b was in EVAL_MODELS but not pulled |
| `2026-04-25T21-27-openrouter-test` | gpt-oss-120b:free | PromptedOutput | Free tier rate limit caused 4/6 null responses; 2 complete runs show high quality |
