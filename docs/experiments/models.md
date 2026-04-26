# Tested Models

All models evaluated against the six thread scenarios. Scores reflect the best
result across all runs for each model. Mode column indicates the extraction mode
under which the best score was achieved.

## Compatibility tiers

- **full**: completes all 6 threads including the role agent node (requires tool calling)
- **partial-schema**: tool support present but intermittent schema-echo failures on some threads; score depends on thread content
- **partial-tool**: no tool support; passes only threads where the pipeline exits before the role node (should_intervene=False)
- **none**: fails at classification; too small or too poorly instruction-tuned to follow the output schema

## Results

| Model | Family | Size | Tool support | Tier | Best score | Mode | Notes |
|---|---|---|---|---|---|---|---|
| `ollama:qwen2.5:14b` | Qwen 2.5 (Alibaba) | 14B | yes | full | 6/6 | ToolOutput | Reference model for local runs; stable across modes |
| `ollama:llama3.1:8b` | Llama 3.1 (Meta) | 8B | yes | full | 6/6 | ToolOutput | Stable across modes |
| `ollama:mistral-nemo:12b` | Mistral Nemo (Mistral AI) | 12B | yes | partial-schema | 6/6 | PromptedOutput | 4/6 with ToolOutput; schema-echo on 2 threads (conflictive, new) |
| `ollama:deepseek-r1:14b` | DeepSeek R1 (DeepSeek) | 14B | yes | partial-schema | 5/6 | ToolOutput | 0/6 with PromptedOutput (misdiagnosed as no-tool); 5/6 with ToolOutput; 1 schema-echo on stalled |
| `ollama:gemma2:9b` | Gemma 2 (Google) | 9B | no | partial-tool | 4/6 | both | Passes 4 threads where intervention not triggered; fails at role node otherwise |
| `ollama:phi4` | Phi-4 (Microsoft) | 14B | no | partial-tool | 5/6 | PromptedOutput | 4/6 with ToolOutput; no tool support confirmed |
| `ollama:llama3.2` | Llama 3.2 (Meta) | 3B | no | none | 2/6 | ToolOutput | Inconsistent; passes 2 threads by chance; schema-echo on the rest |
| `ollama:gemma3:4b` | Gemma 3 (Google) | 4B | no | none | 1/6 | PromptedOutput | 0/6 with ToolOutput; occasional pass is not reliable |
| `ollama:mistral` | Mistral v0.3 (Mistral AI) | 7B | no | none | 0/6 | both | Returns schema instead of instance consistently |
| `ollama:gemma3:12b` | Gemma 3 (Google) | 12B | no | none | 0/6 | both | Schema-echo on all threads in both modes |
| `openrouter:openai/gpt-oss-120b:free` | GPT OSS 120B (OpenAI) | 120B | yes | partial-infra | 2/6 | PromptedOutput | 4 threads failed with null response from OpenRouter free tier rate limiting; 2 completed show high quality |

## Key findings

**Schema-echo is a model behavior, not a framework behavior.** Both PromptedOutput
and ToolOutput can trigger it. The extraction mode changes the delivery channel
(text vs. tool argument) but not whether a model interprets "fill this schema"
as "return the schema definition". ToolOutput reduces frequency for some models
but does not eliminate it.

**Tool support is necessary but not sufficient.** `deepseek-r1:14b` has tool
support but produces schema-echo intermittently. `llama3.1:8b` (8B) is more
reliable than `mistral-nemo:12b` (12B) despite being smaller. Fine-tuning
quality for instruction following matters more than parameter count.

**Mode comparison for the five models tested in both modes:**

| Model | PromptedOutput | ToolOutput | Direction |
|---|:---:|:---:|---|
| `qwen2.5:14b` | 6/6 | 6/6 | stable |
| `mistral-nemo:12b` | 6/6 | 4/6 | regressed |
| `llama3.1:8b` | 6/6 | 6/6 | stable |
| `gemma2:9b` | 4/6 | 4/6 | stable |
| `phi4` | 5/6 | 4/6 | regressed |

## Runs

| Directory | Models | Mode | Notes |
|---|---|---|---|
| `2026-04-24T15-51-baseline-5models` | qwen2.5:14b, phi4, mistral:7b, llama3.2, gemma3:4b | PromptedOutput | First run after PromptedOutput migration |
| `2026-04-25T17-10-5models-tool-calling` | same 5 | ToolOutput (pre-migration) | All models fail or degrade |
| `2026-04-25T18-49-mistral-nemo-12b` | mistral-nemo:12b | PromptedOutput | Isolated run after fixing provider format |
| `2026-04-25T20-49-llama31-8b-gemma2-9b` | llama3.1:8b, gemma2:9b | PromptedOutput | deepseek-r1:14b was in EVAL_MODELS but not pulled |
| `2026-04-25T21-27-openrouter-test` | gpt-oss-120b:free | PromptedOutput | Free tier rate limit caused 4/6 null responses |
| `2026-04-25T22-54-deepseek-r1-14b-gemma3-12b` | deepseek-r1:14b, gemma3:12b | PromptedOutput | deepseek-r1:14b: misdiagnosed as no-tool; gemma3:12b: schema-echo all threads |
| `2026-04-26T11-25-all-10-local-tool-output` | all 10 local models | ToolOutput | First full run after ToolOutput migration; confirms schema-echo persists in ToolOutput for some models |
