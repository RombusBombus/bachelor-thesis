#!/usr/bin/env bash

# Sync bandgap.log, DOSCAR, and POSCAR files from the fritz cluster into ./cluster_results
# Wipes cluster_results/ first, then re-fetches a fresh copy via SSH config entry "fau_fritz".

set -euo pipefail

REMOTE_BASE="/home/atuin/b299bb/b299bb25"
REMOTE_DIRS=(flow-otter-test flow-otter-CuTaN2-5T)
LOCAL_DIR="cluster_results"
SECRET_FILE="secret.txt"

RSYNC_OPTS=(
  -avz
  --prune-empty-dirs
  --include "*/"
  --include "DOSCAR"
  --include "POSCAR"
  --include "EIGENVAL"
  --include "bandgap.log"
  --exclude "*"
)

# echo "Removing existing ${LOCAL_DIR}/ ..."
# rm -rf "${LOCAL_DIR}"

echo "Unlocking SSH key ..."
eval "$(ssh-agent -s)" > /dev/null
ASKPASS_SCRIPT="$(mktemp)"
trap 'ssh-agent -k > /dev/null; rm -f "${ASKPASS_SCRIPT}"' EXIT
cat > "${ASKPASS_SCRIPT}" << EOF
#!/bin/sh
cat "${SECRET_FILE}"
EOF
chmod +x "${ASKPASS_SCRIPT}"

SSH_ASKPASS="${ASKPASS_SCRIPT}" SSH_ASKPASS_REQUIRE=force \
  setsid -w ssh-add ~/.ssh/id_rsa < /dev/null > /dev/null 2>&1
rm -f "${ASKPASS_SCRIPT}"

for dir in "${REMOTE_DIRS[@]}"; do
  echo "Syncing ${dir} ..."
  mkdir -p "${LOCAL_DIR}/${dir}"
  rsync "${RSYNC_OPTS[@]}" \
    "fau_fritz:${REMOTE_BASE}/${dir}/" "${LOCAL_DIR}/${dir}/"
  sleep 1
done

echo "Sync complete."
