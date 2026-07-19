# Open edX LMS (Tutor, EC2) — inline plugin deployment.
# See ../../docs/decisions/0040-despliegue-openedx-en-aws-ec2.md
#
# The LMS instance never gets these files any other way: inline Tutor
# plugins (tutor/inline_plugins/*.py) are loose .py files Tutor loads
# from TUTOR_PLUGINS_ROOT, not something `git clone` on its own wires
# up. This copies them over and re-applies Tutor's config.
#
# The running containers were originally created under root's Tutor
# config root (/root/.local/share/tutor), not ubuntu's - `docker
# compose restart` doesn't recreate mounts, so config saved under
# ubuntu's own tutor root never reaches the running LMS. Every tutor
# command here therefore runs via sudo, targeting root's config root
# (sudo resets $HOME to /root, which is where tutor resolves its
# default root from). Confirmed 2026-07-19 by checking the running
# container's actual bind mounts with `docker inspect`.
#
#   make lms-setup   first-time or after editing an inline plugin
#   make lms-deploy  alias for lms-setup (no separate "build" step)

LMS_USER ?= ubuntu
LMS_HOST ?= tfm-lms
LMS_PLUGINS_REMOTE_DIR ?= /home/ubuntu/tfm-tutor-plugins
LMS_TUTOR_BIN ?= /home/ubuntu/venv/bin/tutor

.PHONY: lms-setup lms-deploy

lms-setup:
	@echo "==> [lms] copying inline Tutor plugins..."
	rsync -a --delete tutor/inline_plugins/ $(LMS_USER)@$(LMS_HOST):$(LMS_PLUGINS_REMOTE_DIR)/
	@echo "==> [lms] enabling plugins, applying config, restarting LMS..."
	ssh $(LMS_USER)@$(LMS_HOST) "sudo TUTOR_PLUGINS_ROOT=$(LMS_PLUGINS_REMOTE_DIR) $(LMS_TUTOR_BIN) plugins enable dev_jwt_long_expiry facilitation_override && sudo TUTOR_PLUGINS_ROOT=$(LMS_PLUGINS_REMOTE_DIR) $(LMS_TUTOR_BIN) config save && sudo TUTOR_PLUGINS_ROOT=$(LMS_PLUGINS_REMOTE_DIR) $(LMS_TUTOR_BIN) local restart lms"

lms-deploy: lms-setup
