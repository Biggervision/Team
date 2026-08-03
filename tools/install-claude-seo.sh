#!/usr/bin/env bash
set -euo pipefail

# Installs the Claude SEO skill (https://github.com/AgriciDaniel/claude-seo)
# into ~/.claude so /seo commands are available in Claude Code sessions.
# Cloud sessions are ephemeral, so re-run this in a fresh environment
# (or add it to the environment's setup script).

TMP_DIR=$(mktemp -d)
trap 'rm -rf -- "${TMP_DIR}"' EXIT

git clone --depth 1 https://github.com/AgriciDaniel/claude-seo.git "${TMP_DIR}/claude-seo"
bash "${TMP_DIR}/claude-seo/install.sh"
