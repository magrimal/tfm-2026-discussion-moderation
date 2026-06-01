-include .env
-include .env.local

DISCUSSION_MODERATION_API_PORT ?= 8765
ifneq ($(origin API_PORT), undefined)
DISCUSSION_MODERATION_API_PORT := $(API_PORT)
endif
export DISCUSSION_MODERATION_API_PORT

.PHONY: lint format test eval-classifier eval-pipeline eval-models eval-models-isolated render-prompt facilitate eval-all serve graph-diagram dev-setup dev-up dashboard-build

lint:
	uv run ruff check discussion_moderation/

format:
	uv run ruff format discussion_moderation/

test:
	uv run pytest

eval-classifier:
	uv run python -m discussion_moderation.evals.eval_classifier

eval-pipeline:
	uv run python -m discussion_moderation.evals.eval_pipeline

eval-models:
	uv run python -m discussion_moderation.evals.eval_models

eval-models-isolated:
	uv run python -m discussion_moderation.evals.eval_isolated

render-prompt:
	uv run python -m discussion_moderation.evals.render_prompt

facilitate:
	uv run python -m discussion_moderation.playground

eval-all: eval-classifier eval-pipeline

serve:
	uv run uvicorn discussion_moderation.rest_api.main:app --reload --port $(DISCUSSION_MODERATION_API_PORT)

dev-setup:
	npm --prefix dashboard install

dev-up:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

dashboard-build:
	npm --prefix dashboard run build

graph-diagram:
	uv run python -m discussion_moderation.graph.pipeline --diagram
