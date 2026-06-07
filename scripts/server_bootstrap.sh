#!/usr/bin/env bash
# Bootstrap script — piped to the server via stdin to bypass the fish shell.
# Clones the repo if it doesn't exist, then runs server_setup.sh.
# Run via: make server-setup
set -euo pipefail

APP=/home/2526-moderacion/app
REPO=https://github.com/magrimal/tfm-2026-discussion-moderation.git

if [ -d "$APP/.git" ]; then
    echo "==> Repo exists, pulling latest..."
    git -C "$APP" pull
else
    echo "==> Cloning repo..."
    # Preserve .env.local if it was already copied
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

bash "$APP/scripts/server_setup.sh"
