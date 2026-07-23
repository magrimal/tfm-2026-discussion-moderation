FROM node:20-slim AS dashboard
WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci
COPY dashboard/ ./
RUN VITE_API_BASE_URL="/api" npm run build

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY discussion_moderation/ ./discussion_moderation/
COPY docs/threads/ ./docs/threads/
RUN uv sync --frozen --no-dev
COPY --from=dashboard /app/dashboard/dist ./dashboard/dist
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "discussion_moderation.rest_api.main:app", "--host", "0.0.0.0", "--port", "8080"]
