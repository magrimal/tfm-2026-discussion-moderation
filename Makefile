-include .env
-include .env.local

DISCUSSION_MODERATION_API_PORT ?= 8765
ifneq ($(origin API_PORT), undefined)
DISCUSSION_MODERATION_API_PORT := $(API_PORT)
endif
export DISCUSSION_MODERATION_API_PORT

# Tooling boundary:
#   uv     — Python deps and entry points (uv run <script>)
#   npm    — frontend deps and Vite build
#   honcho — runs uv + npm together in dev (two ports: API on 8765, Vite on 5173)
#   make   — cross-toolchain orchestration only (dev, deploy)
#
# Deployments:
#   server-deploy — builds dashboard for idril.fdi.ucm.es and rsyncs to public_html
#   service-up    — builds a local container for testing (API + dashboard, port 8080)

IDRIL_USER ?= magrimal
IDRIL_HOST = idril.fdi.ucm.es
IDRIL_PORT = 2203
IDRIL_PUBLIC_HTML = /home/2526-moderacion/public_html/

.PHONY: dev-setup dev-up dashboard-build server-deploy service-build service-up service-down

dev-setup:
	npm --prefix dashboard install

dev-up:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

dashboard-build:
	VITE_API_BASE_URL="/api" npm --prefix dashboard run build

server-deploy:
	VITE_API_BASE_URL="/2526-moderacion/api" \
	VITE_BASE_PATH="/2526-moderacion/" \
	npm --prefix dashboard run build
	rsync -av --delete -e "ssh -p $(IDRIL_PORT)" \
		dashboard/dist/ \
		$(IDRIL_USER)@$(IDRIL_HOST):$(IDRIL_PUBLIC_HTML)

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
