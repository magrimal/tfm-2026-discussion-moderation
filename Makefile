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
#   server-setup   — one-time setup on idril.fdi.ucm.es (clone, deps, systemd)
#   server-restart — redeploy API + dashboard on the server (git pull + rebuild)
#   service-up     — local container for testing (API + dashboard, port 8080)

IDRIL_USER ?= magrimal
IDRIL_HOST ?= idril.fdi.ucm.es

.PHONY: dev-setup dev-up dashboard-build server-setup server-restart server-restart-api service-build service-up service-down

dev-setup:
	npm --prefix dashboard install

dev-up:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

dashboard-build:
	VITE_API_BASE_URL="/api" npm --prefix dashboard run build

server-setup:
	scp .env.idril $(IDRIL_USER)@$(IDRIL_HOST):/home/2526-moderacion/app/.env.local
	ssh $(IDRIL_USER)@$(IDRIL_HOST) '\
		APP=/home/2526-moderacion/app; \
		if [ -d "$$APP/.git" ]; then git -C "$$APP" pull; \
		else git clone https://github.com/magrimal/tfm-2026-discussion-moderation.git "$$APP"; fi; \
		bash "$$APP/scripts/server_setup.sh"'

server-restart:
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash /home/2526-moderacion/app/scripts/server_restart.sh

server-restart-api:
	ssh $(IDRIL_USER)@$(IDRIL_HOST) '\
		cd /home/2526-moderacion/app && git pull && uv sync --no-dev && \
		su - 2526-moderacion -c "systemctl --user restart facilitation-api"'

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
