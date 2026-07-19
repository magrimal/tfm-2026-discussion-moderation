#!/usr/bin/env bash
# Redeploy script — runs on idril.fdi.ucm.es to update API and dashboard.
# Pulls latest code, reinstalls deps, rebuilds dashboard, restarts service.
#
# Run via: make idril-deploy (which SSHes and invokes this script)

set -euo pipefail

APP=/home/2526-moderacion/app
PUBLIC_HTML=/home/2526-moderacion/public_html

echo "==> Pulling latest code..."
git -C "$APP" pull

cd "$APP"

echo "==> Updating Python dependencies..."
uv sync --no-dev

echo "==> Rebuilding dashboard..."
npm --prefix dashboard ci
VITE_API_BASE_URL="/2526-moderacion/api" \
VITE_BASE_PATH="/2526-moderacion/" \
npm --prefix dashboard run build

echo "==> Copying dashboard to public_html..."
cp -r dashboard/dist/. "$PUBLIC_HTML/"

echo "==> Restarting API service..."
systemctl --user restart facilitation-api

echo "==> Done."
