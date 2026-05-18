.PHONY: lint format test eval-classifier eval-pipeline eval-all serve graph-diagram dev-setup dev-up

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

eval-all: eval-classifier eval-pipeline

serve:
	uv run uvicorn discussion_moderation.rest_api.main:app --reload

dev-setup:
	uv run dev setup

dev-up:
	uv run dev up

graph-diagram:
	uv run python -m discussion_moderation.graph.pipeline --diagram
