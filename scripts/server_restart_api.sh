#!/usr/bin/env bash
# Restart only the API service — no dashboard rebuild.
# Run via: make server-restart-api
set -euo pipefail

APP=/home/2526-moderacion/app

cd "$APP"
git pull
uv sync --no-dev
systemctl --user restart facilitation-api
