FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY discussion_moderation/ ./discussion_moderation/
RUN uv sync --frozen --no-dev

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "discussion_moderation.rest_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
