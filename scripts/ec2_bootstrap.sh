#!/usr/bin/env bash
# Bootstrap script for EC2 (Ubuntu 22.04).
# Installs Docker, clones the repo, and starts the facilitation service.
# Run via: make ec2-setup (which SSHes and pipes this script to bash)
set -euo pipefail

APP=/home/ubuntu/app
REPO=https://github.com/magrimal/tfm-2026-discussion-moderation.git

if ! command -v docker &>/dev/null; then
    echo "==> Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker ubuntu
fi

if [ -d "$APP/.git" ]; then
    echo "==> Repo exists, pulling latest..."
    git -C "$APP" pull
else
    echo "==> Cloning repo..."
    ENV_TMP=""
    if [ -f "$APP/.env.local" ]; then
        ENV_TMP=$(mktemp)
        cp "$APP/.env.local" "$ENV_TMP"
    fi
    rm -rf "$APP"
    git clone "$REPO" "$APP"
    if [ -n "$ENV_TMP" ]; then
        mv "$ENV_TMP" "$APP/.env.local"
    fi
fi

cd "$APP"

echo "==> Pulling image and starting service..."
docker compose pull
docker compose up -d

echo "==> Done. Check with:"
echo "    docker compose ps"
echo "    curl http://localhost:8080/api/health"
