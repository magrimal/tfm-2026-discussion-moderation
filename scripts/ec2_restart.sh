#!/usr/bin/env bash
# Redeploy script — runs on the EC2 instance to update the facilitation stack.
# Pulls compose config, pulls the latest image, and recreates containers.
#
# Run via: make ec2-restart (which SSHes and invokes this script)

set -euo pipefail

APP=/home/ubuntu/app
cd "$APP"

echo "==> Pulling latest compose config..."
git pull

echo "==> Pulling latest image..."
docker compose pull

echo "==> Stopping containers..."
docker compose down

echo "==> Clearing stale dashboard build..."
docker volume rm app_dashboard_dist 2>/dev/null || true

echo "==> Starting containers..."
docker compose up -d

echo "==> Done."
docker compose ps
