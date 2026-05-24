#!/usr/bin/env bash

# Sync current directory to HPC cluster via SSH config entry "fau_fritz"

set -euo pipefail

# Remote target directory on the cluster
REMOTE_DIR="~/bachelor-thesis"

# Rsync options
RSYNC_OPTS=(
  -avz
  --progress
  --delete
  --exclude ".git"
  --exclude "__pycache__"
  --exclude "*.pyc",
  --exclude ".venv"
)

echo "Syncing current directory to fau_fritz:${REMOTE_DIR}"

rsync "${RSYNC_OPTS[@]}" fau_fritz:"${REMOTE_DIR}" ./

echo "Sync complete."