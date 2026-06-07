#!/usr/bin/env bash
# Server setup script — runs on idril.fdi.ucm.es after the repo is cloned.
# Installs Python deps, builds the dashboard, copies it to public_html,
# and configures the systemd user service.
#
# Run via: make server-setup (which SSHes and invokes this script)
# Do not run locally.

set -euo pipefail

APP=/home/2526-moderacion/app
PUBLIC_HTML=/home/2526-moderacion/public_html

cd "$APP"

echo "==> Installing Python dependencies..."
uv sync --no-dev

echo "==> Installing dashboard dependencies..."
npm --prefix dashboard ci

echo "==> Building dashboard..."
VITE_API_BASE_URL="/2526-moderacion/api" \
VITE_BASE_PATH="/2526-moderacion/" \
npm --prefix dashboard run build

echo "==> Copying dashboard to public_html..."
mkdir -p "$PUBLIC_HTML"
cp -r dashboard/dist/. "$PUBLIC_HTML/"

echo "==> Writing systemd service..."
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/facilitation-api.service << 'SERVICE'
[Unit]
Description=Discussion Facilitation API
After=network.target

[Service]
WorkingDirectory=/home/2526-moderacion/app
EnvironmentFile=/home/2526-moderacion/app/.env.local
ExecStart=/home/2526-moderacion/app/.venv/bin/uvicorn \
    discussion_moderation.rest_api.main:app \
    --host 0.0.0.0 --port 8080
Restart=on-failure

[Install]
WantedBy=default.target
SERVICE

echo "==> Enabling and starting service..."
systemctl --user daemon-reload
systemctl --user enable facilitation-api
systemctl --user restart facilitation-api

echo "==> Done. Check status with:"
echo "    systemctl --user status facilitation-api"
