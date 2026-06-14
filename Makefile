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
# Diagrams:
#   diagrams-export   — render docs/diagrams/*.mmd to docs/thesis/figures/*.png (requires Node)
#
# Deployments:
#   server-setup      — first-time setup on idril.fdi.ucm.es (clone, deps, systemd)
#   server-restart    — redeploy API + dashboard on the server (git pull + rebuild)
#   server-restart-api — redeploy API only (no dashboard rebuild)
#   service-up        — local container for testing (API + dashboard, port 8080)
#   ec2-build         — build image and push to ECR public
#   ec2-setup         — first-time setup on EC2 (docker, clone, compose up)
#   ec2-restart       — pull latest image and restart on EC2

IDRIL_USER ?= magrimal
IDRIL_HOST ?= idril.fdi.ucm.es

EC2_USER ?= ubuntu
EC2_HOST ?= tfm-ec2
ECR_IMAGE ?= public.ecr.aws/h1n7c6s4/tfm/facilitation

.PHONY: dev-setup dev-up dashboard-build diagrams-export server-setup server-restart server-restart-api service-build service-up service-down ec2-build ec2-setup ec2-restart

dev-setup:
	npm --prefix dashboard install

dev-up:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

dashboard-build:
	VITE_API_BASE_URL="/api" npm --prefix dashboard run build

diagrams-export:
	for f in docs/diagrams/*.mmd; do \
	    name=$$(basename "$$f" .mmd); \
	    mmdc \
	        -i "$$f" \
	        -o "docs/thesis/figures/$$name.png" \
	        --scale 2 \
	        -p docs/diagrams/puppeteer-config.json; \
	done

server-setup:
	scp .env.idril $(IDRIL_USER)@$(IDRIL_HOST):/home/2526-moderacion/app/.env.local
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash -s < scripts/server_bootstrap.sh

server-restart:
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash /home/2526-moderacion/app/scripts/server_restart.sh

server-restart-api:
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash -s < scripts/server_restart_api.sh

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

ec2-build:
	aws ecr-public get-login-password --region us-east-1 \
	    | podman login --username AWS --password-stdin public.ecr.aws
	podman build -f Containerfile -t $(ECR_IMAGE):latest .
	podman push $(ECR_IMAGE):latest

ec2-setup:
	scp .env.ec2 $(EC2_USER)@$(EC2_HOST):/home/ubuntu/app/.env.local
	scp docker-compose.yml $(EC2_USER)@$(EC2_HOST):/home/ubuntu/app/docker-compose.yml
	ssh $(EC2_USER)@$(EC2_HOST) bash -s < scripts/ec2_bootstrap.sh

ec2-restart:
	ssh $(EC2_USER)@$(EC2_HOST) \
	    "cd /home/ubuntu/app && docker compose pull && docker compose up -d"
