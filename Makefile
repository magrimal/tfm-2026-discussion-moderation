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
# Every environment below follows the same shape: setup (first-time),
# deploy (the one routine command), down (stop it).
#
# local        — dev process (uv + npm via honcho)
#   make local-setup   first-time: install dashboard deps
#   make local-deploy  run API + dashboard dev servers
#   make local-down    stop the dev servers
#
# local-image  — podman container smoke test (same image as prod)
#   make local-image-build   build the image only
#   make local-image-deploy  build + run the container locally (routine)
#   make local-image-down    stop it
#   make local-image-logs    tail the container's logs
#
# idril        — UCM server (idril.fdi.ucm.es), bare-metal + systemd
#   make idril-setup   first-time: clone, deps, systemd unit
#   make idril-deploy  redeploy API + dashboard (routine)
#   make idril-down    stop the systemd service
#   make idril-logs    tail the systemd service's logs
#
# ec2          — AWS EC2, docker compose
#   make ec2-setup   first-time: docker, clone, compose up
#   make ec2-build   build image and push to ECR only
#   make ec2-deploy  build image, push to ECR, restart on EC2 (routine)
#   make ec2-down    stop the compose stack
#   make ec2-logs    tail the facilitation container's logs

IDRIL_USER ?= magrimal
IDRIL_HOST ?= idril.fdi.ucm.es

EC2_USER ?= ubuntu
EC2_HOST ?= tfm-ec2
ECR_IMAGE ?= public.ecr.aws/h1n7c6s4/tfm/facilitation

.PHONY: local-setup local-deploy local-down dashboard-build diagrams-export idril-setup idril-deploy idril-down idril-logs local-image-build local-image-deploy local-image-down local-image-logs ec2-build ec2-setup ec2-restart ec2-deploy ec2-down ec2-logs

local-setup:
	npm --prefix dashboard install

local-deploy:
	uv run --extra dev honcho start -e .env,.env.local -f Procfile.dev

local-down:
	@echo "==> [local] stopping dev servers..."
	pkill -f "honcho start -e .env,.env.local -f Procfile.dev" || true

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

idril-setup:
	scp .env.idril $(IDRIL_USER)@$(IDRIL_HOST):/home/2526-moderacion/app/.env.local
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash -s < scripts/server_bootstrap.sh

idril-deploy:
	scp .env.idril $(IDRIL_USER)@$(IDRIL_HOST):/home/2526-moderacion/app/.env.local
	ssh $(IDRIL_USER)@$(IDRIL_HOST) bash -s < scripts/server_restart.sh

idril-down:
	@echo "==> [idril] stopping service..."
	ssh $(IDRIL_USER)@$(IDRIL_HOST) "systemctl --user stop facilitation-api"

idril-logs:
	ssh $(IDRIL_USER)@$(IDRIL_HOST) "journalctl --user -u facilitation-api -f"

local-image-build:
	@echo "==> [local-image] building container..."
	podman build -t discussion-moderation:dev .

local-image-deploy: local-image-build
	@echo "==> [local-image] starting container..."
	podman rm -f facilitation-service 2>/dev/null || true
	podman run -d --name facilitation-service \
		--network host \
		--env-file .env.local \
		-v $(CURDIR)/docs/experiments/results:/app/docs/experiments/results:Z \
		discussion-moderation:dev

local-image-down:
	@echo "==> [local-image] stopping container..."
	podman rm -f facilitation-service 2>/dev/null || true

local-image-logs:
	podman logs -f facilitation-service

ec2-build:
	@echo "==> [ec2] building and pushing image..."
	aws ecr-public get-login-password --region us-east-1 \
	    | podman login --username AWS --password-stdin public.ecr.aws
	podman build --no-cache --ulimit nofile=65536:65536 -f Containerfile -t $(ECR_IMAGE):latest .
	podman push $(ECR_IMAGE):latest

ec2-setup:
	ssh $(EC2_USER)@$(EC2_HOST) "mkdir -p /home/ubuntu/app"
	scp .env.ec2 $(EC2_USER)@$(EC2_HOST):/home/ubuntu/app/.env.local
	scp docker-compose.yml $(EC2_USER)@$(EC2_HOST):/home/ubuntu/app/docker-compose.yml
	ssh $(EC2_USER)@$(EC2_HOST) bash -s < scripts/ec2_bootstrap.sh

ec2-restart:
	@echo "==> [ec2] restarting service..."
	scp .env.ec2 $(EC2_USER)@$(EC2_HOST):/home/ubuntu/app/.env.local
	ssh $(EC2_USER)@$(EC2_HOST) bash -s < scripts/ec2_restart.sh

ec2-deploy: ec2-build ec2-restart
	@echo "==> [ec2] deploy complete"

ec2-down:
	@echo "==> [ec2] stopping compose stack..."
	ssh $(EC2_USER)@$(EC2_HOST) "cd /home/ubuntu/app && docker compose down"

ec2-logs:
	ssh $(EC2_USER)@$(EC2_HOST) "cd /home/ubuntu/app && docker compose logs -f facilitation"
