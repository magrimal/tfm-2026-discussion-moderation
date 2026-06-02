-include .env
-include .env.local

DISCUSSION_MODERATION_API_PORT ?= 8765
ifneq ($(origin API_PORT), undefined)
DISCUSSION_MODERATION_API_PORT := $(API_PORT)
endif
export DISCUSSION_MODERATION_API_PORT

# Tooling boundary:
#   uv    — Python deps and entry points (uv run <script>)
#   npm   — frontend deps and Vite build
#   honcho — runs uv + npm together in dev (two ports: API on 8765, Vite on 5173)
#   make  — cross-toolchain orchestration only (dev, deploy)
#
# In production: one container, one port (8080).
#   FastAPI serves API routes and the pre-built dashboard as static files.
#   No honcho, no Vite, no separate frontend process.

.PHONY: dev-setup dev-up dashboard-build service-build service-up service-down

dev-setup:
	npm --prefix dashboard install

dev-up:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

dashboard-build:
	VITE_API_BASE_URL="" npm --prefix dashboard run build

service-build:
	podman build -t discussion-moderation:dev .

service-up: service-build
	podman rm -f facilitation-service 2>/dev/null || true
	podman run -d --name facilitation-service \
		--network host \
		--env-file .env.local \
		-v $(CURDIR)/docs/experiments/results:/app/docs/experiments/results:Z \
		discussion-moderation:dev

service-down:
	podman rm -f facilitation-service 2>/dev/null || true
